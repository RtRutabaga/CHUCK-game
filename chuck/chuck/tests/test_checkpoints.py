"""Persistent saves, title flow, shared checkpoint loader, and dev menu."""

import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.boot_scene import BootScene
from src.scenes.checkpoint_select_scene import CheckpointSelectScene
from src.scenes.title_scene import TitleScene
from src.scenes.world_scene import WorldScene
from src.systems.checkpoints import CHECKPOINTS, OPENING_CHECKPOINT_ID
from src.systems.save import SAVE_VERSION, SaveRecord, SaveSystem
from src.ui.bitmap_font import GLYPH_ORDER


def _temp_save() -> tuple[tempfile.TemporaryDirectory, Path]:
    directory = tempfile.TemporaryDirectory()
    return directory, Path(directory.name) / "save.json"


def _boot_to_title(game: Game) -> TitleScene:
    assert isinstance(game.scenes.current, BootScene)
    game.scenes.current.update(0.01)
    assert isinstance(game.scenes.current, TitleScene)
    return game.scenes.current


def test_save_format_is_readable_versioned_and_atomic() -> None:
    directory, path = _temp_save()
    try:
        saves = SaveSystem(path)
        assert saves.load() is None
        record = SaveRecord("sewer_anchor", 47, ("sewer_completed",))
        assert saves.write(record)
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw == {
            "version": SAVE_VERSION,
            "checkpoint_id": "sewer_anchor",
            "sanity": 47,
            "progress_flags": ["sewer_completed"],
            "cigarettes": 0,
            "deaths": 0,
            "spoken": [],
        }
        assert saves.load() == record
        assert not path.with_suffix(".json.tmp").exists()
    finally:
        directory.cleanup()


def test_missing_invalid_and_outdated_saves_are_graceful() -> None:
    directory, path = _temp_save()
    try:
        saves = SaveSystem(path)
        for raw in (
            "not json",
            json.dumps({"version": SAVE_VERSION + 1}),
            json.dumps({
                "version": SAVE_VERSION,
                "checkpoint_id": "sewer_anchor",
                "sanity": 0,
                "progress_flags": [],
            }),
            json.dumps({
                "version": SAVE_VERSION,
                "checkpoint_id": "sewer_anchor",
                "sanity": "lots",
                "progress_flags": [],
            }),
        ):
            path.write_text(raw, encoding="utf-8")
            assert saves.load() is None
    finally:
        directory.cleanup()


def _play_through_opening(game) -> None:
    """New Game opens on the wake-up cutscene; run it to its hand-off."""
    from src.scenes.opening_cutscene_scene import OpeningCutsceneScene

    scene = game.scenes.current
    assert isinstance(scene, OpeningCutsceneScene)
    while game.scenes.current is scene:
        scene.update(0.25)


def test_title_without_save_disables_continue_and_new_game_uses_loader() -> None:
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        title = _boot_to_title(game)
        assert not title.continue_available
        assert title.options[:2] == ("NEW GAME", "CONTINUE")
        title._move(1)
        assert title._selected != 1

        calls = []
        real_load = game.checkpoints.load_checkpoint
        game.checkpoints.load_checkpoint = lambda checkpoint_id, **kwargs: (
            calls.append((checkpoint_id, kwargs))
            or real_load(checkpoint_id, **kwargs)
        )
        title._selected = 0
        title._choose()
        assert calls == [], "the opening cutscene plays before the loader"
        _play_through_opening(game)
        scene = game.scenes.current
        assert calls == [(OPENING_CHECKPOINT_ID,
                          {"cigarettes": 0, "deaths": 0})]
        assert isinstance(scene, WorldScene)
        assert scene.map_name == "waterdeep_docks"
        assert game.active_checkpoint_id == OPENING_CHECKPOINT_ID
        assert not path.exists(), "NEW GAME must not fabricate progress"
    finally:
        game._shutdown()
        directory.cleanup()


def test_new_game_clears_an_existing_save_slot() -> None:
    directory, path = _temp_save()
    SaveSystem(path).write(SaveRecord("sewer_anchor", 32, ()))
    game = Game(save_path=path)
    try:
        title = _boot_to_title(game)
        assert title.continue_available
        title._selected = 0
        title._choose()
        _play_through_opening(game)
        assert not path.exists()
        assert game.active_checkpoint_id == OPENING_CHECKPOINT_ID
        assert game.progress.flags == set()
    finally:
        game._shutdown()
        directory.cleanup()


def test_anchor_save_relaunch_continue_restores_state_and_respawn() -> None:
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        game.progress.enable("sewer_completed")
        game.scenes.replace(WorldScene(game, "waterdeep_docks"))
        scene = game.scenes.current
        anchor = scene.anchors[0]
        scene.sanity.current = 47
        came_in = scene.anchors_system.respawn_position_for_chuck()
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.update(0.01)

        record = game.saves.load()
        assert record == SaveRecord(
            "waterdeep_anchor", 47, ("sewer_completed",)
        )
        assert game.active_checkpoint_id == "waterdeep_anchor"
        assert anchor.lit

        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT)
        scene.update(config.RESPAWN_HOLD)
        # The door he came in by, not the Ashtray he touched.
        assert (scene.player.x, scene.player.y) == came_in
        assert scene.sanity.current == config.SANITY_MAX
    finally:
        game._shutdown()

    game = Game(save_path=path)
    try:
        title = _boot_to_title(game)
        assert title.continue_available
        calls = []
        real_load = game.checkpoints.load_checkpoint
        game.checkpoints.load_checkpoint = lambda checkpoint_id, **kwargs: (
            calls.append((checkpoint_id, kwargs))
            or real_load(checkpoint_id, **kwargs)
        )
        title._selected = 1
        title._choose()
        scene = game.scenes.current
        assert calls == [(
            "waterdeep_anchor",
            {"progress_flags": ("sewer_completed",), "sanity": 47,
             "cigarettes": 0, "deaths": 0},
        )]
        assert scene.map_name == "waterdeep_docks"
        assert scene.sanity.current == 47
        assert scene.tilemap.terrain_at(44, 17) == "v"
        assert scene.anchors[0].lit
    finally:
        game._shutdown()
        directory.cleanup()


def test_continue_rejects_ids_that_are_not_save_points() -> None:
    """A save names a door Chuck walked in by, or it is not a save.

    `pantry_entry` used to be listed here as something to refuse, back
    when only an Ashtray could be saved at. It is a door, so it is a
    save point now. What stays refused is a checkpoint that is neither
    -- `waterdeep_finale` is reached by a cutscene, not walked into --
    and an id that is not a checkpoint at all.
    """
    directory, path = _temp_save()
    try:
        for checkpoint_id in ("waterdeep_finale", "not_a_checkpoint"):
            SaveSystem(path).write(SaveRecord(checkpoint_id, 60, ()))
            game = Game(save_path=path)
            try:
                title = _boot_to_title(game)
                assert not title.continue_available
            finally:
                game._shutdown()
    finally:
        directory.cleanup()


def test_normal_map_entries_preserve_sanity_and_use_registry_checkpoints() -> None:
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        scene.sanity.current = 41
        scene.load_map("sewer")
        assert scene.sanity.current == 41
        assert game.active_checkpoint_id == "sewer_entrance"

        scene.load_map(
            "waterdeep_docks",
            arrival="sewer_outflow",
            climb_from_water=True,
        )
        assert scene.sanity.current == 41
        assert game.active_checkpoint_id == "waterdeep_return"
        assert game.progress.has("sewer_completed")
        assert scene.tilemap.terrain_at(44, 17) == "v"
    finally:
        game._shutdown()
        directory.cleanup()


def test_development_selector_pages_follow_and_leap_the_selection() -> None:
    """Session 125: the registry outgrew one screen, so the selector
    pages in twelve-slot screenfuls — the page follows the up/down
    caret, and left/right leap a whole page with wraparound."""
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        selector = CheckpointSelectScene(game)

        def press(action):
            game.input.begin_frame()
            game.input._actions_just_pressed.add(action)
            selector.update(0.0)

        count = len(selector.checkpoints)
        assert count > selector.PAGE_SIZE  # it genuinely overflows now
        assert selector.pages == (count + selector.PAGE_SIZE - 1) // (
            selector.PAGE_SIZE
        )
        assert selector.page == 0

        # The page follows the caret as it walks past the fold...
        selector._selected = selector.PAGE_SIZE - 1
        press("move_down")
        assert selector._selected == selector.PAGE_SIZE
        assert selector.page == 1

        # ...and wraps from the last entry back to the first page.
        selector._selected = count - 1
        press("move_down")
        assert selector._selected == 0 and selector.page == 0

        # Left/right leap a full page, clamped to real entries.
        press("move_right")
        assert selector.page == 1
        assert selector._selected == min(selector.PAGE_SIZE, count - 1)
        for _ in range(selector.pages - 1):
            press("move_right")
        assert selector.page == 0  # wrapped around from any page count
        press("move_left")
        assert selector.page == selector.pages - 1
        assert selector._selected <= count - 1

        # Every entry still loads through the real loader from any page.
        selector._selected = count - 1
        press("interact")
        assert game.active_checkpoint_id == (
            selector.checkpoints[-1].checkpoint_id
        )
    finally:
        game._shutdown()
        directory.cleanup()


def test_development_selector_lists_and_loads_all_authored_test_entries() -> None:
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        selector = CheckpointSelectScene(game)
        expected_names = (
            "Waterdeep 1", "Waterdeep Ashtray", "Sewer 1", "Sewer 2",
            "Waterdeep 2", "Waterdeep Finale", "Fountain Plaza",
            "Fountain Plaza Finale", "Tavern 1", "Pantry 1",
            "Chult 1", "Chult 2", "Chult 3", "Chult 4", "Chult Falls",
            "Chult 5",
            "Temple 1", "Temple 2", "Temple 3", "Temple 4", "Temple 5",
            "Temple 6", "Temple 7", "Temple 8", "Temple 9",
            "Rubble 1", "Ship 1", "Ship Hold", "Ship Galley",
            "Ship Crew Quarters",
            "Ship Captain Cabin",
            "Ship Exterior Deck",
            "Captain Arrival",
            "Phlegethos 1", "Phlegethos 2", "Phlegethos 3", "Phlegethos 4",
            "Phlegethos 5", "Phlegethos 6", "Feywild 1", "Feywild 2", "Feywild 3",
            "Feywild 4", "Feywild 5", "Feywild 6", "Feywild 7",
            "Feywild 8", "Feywild 9",
            "Feywild 10", "Feywild 11", "Feywild 12", "Feywild 13",
            "Zephyros 1", "Zephyros 2", "Zephyros 3", "City Night 1",
            "City Night 2",
            "City Night 3",
            "City Night 4",
            "City Night 5",
            "City Night 6",
            "City Sewer 1", "City Sewer 2", "City Sewer 3",
            "City Sewer 4", "City Day 1", "City Day 2", "City Day 3",
            "City Day 4", "City Day 5", "City Day 6",
            "Cabin Exterior", "Cabin Interior",
            # Phase 13's development entry to the initial desert, which
            # the phase document asks for by name.
            "Desert Central", "Orc Camp", "Oasis", "Undead Ruins",
            "Collided Desert 1", "Collided Desert 2",
            "Collided Desert 3", "Collided Desert 4",
            "Collided Desert 5", "Collided Desert 6",
            "Collided Desert 7", "Collided Desert 8",
            "Final Trio Encounter",
        )
        assert tuple(cp.display_name for cp in selector.checkpoints) == expected_names
        assert set("".join(expected_names)) <= set(GLYPH_ORDER)

        for checkpoint in selector.checkpoints:
            scene = game.checkpoints.load_checkpoint(checkpoint.checkpoint_id)
            assert scene.map_name == checkpoint.map_name
            assert game.active_checkpoint_id == checkpoint.checkpoint_id
            assert game.progress.flags >= set(checkpoint.required_flags)
            if checkpoint.saveable:
                active_anchor = next(
                    anchor for anchor in scene.anchors
                    if anchor.checkpoint_id == checkpoint.checkpoint_id
                )
                assert active_anchor.lit
                assert (scene.player.x, scene.player.y) == (
                    active_anchor.x, active_anchor.y
                )
            if checkpoint.map_name in {"waterdeep_tavern", "waterdeep_pantry"}:
                assert game.progress.has("sewer_completed")
            if checkpoint.map_name in {
                "chult_jungle", "chult_cog", "chult_run", "chult_respite",
                "chult_temple", "temple_entrance", "temple_spikes",
                "temple_skeletons",
                "temple_darts",
                "temple_snakes",
                "temple_astral_wind",
            }:
                assert game.progress.has("chult_reached")
        assert len(CHECKPOINTS) > len(selector.checkpoints)  # internal returns
    finally:
        game._shutdown()
        directory.cleanup()


def test_development_menu_dispatches_to_the_same_load_checkpoint_method() -> None:
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        game.scenes.replace(CheckpointSelectScene(game))
        selector = game.scenes.current
        selector._selected = next(
            index for index, checkpoint in enumerate(selector.checkpoints)
            if checkpoint.checkpoint_id == "pantry_entry"
        )
        calls = []
        real_load = game.checkpoints.load_checkpoint
        game.checkpoints.load_checkpoint = lambda checkpoint_id, **kwargs: (
            calls.append((checkpoint_id, kwargs))
            or real_load(checkpoint_id, **kwargs)
        )
        game.input._actions_just_pressed.add("interact")
        selector.update(0.01)
        assert calls == [("pantry_entry", {})]
        assert game.scenes.current.map_name == "waterdeep_pantry"
        assert game.progress.has("sewer_completed")
    finally:
        game._shutdown()
        directory.cleanup()


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All checkpoint/save/title tests passed.")


if __name__ == "__main__":
    _run_all()


def test_the_new_save_format_leaves_the_old_file_where_it_was() -> None:
    """Rolling the code back has to find the player's save intact.

    Git can revert a commit; it cannot un-overwrite a file on disk. The
    version moved to 2 *and* the file moved to a new name, so an older
    build reads its own save.json exactly as it left it, and a newer
    file it cannot understand is simply not its file.
    """
    import json
    from src.systems.save import SAVE_FILENAME, SAVE_VERSION, default_save_path

    assert SAVE_VERSION == 2
    assert SAVE_FILENAME == "save2.json"
    assert default_save_path().name == SAVE_FILENAME

    directory = tempfile.TemporaryDirectory()
    try:
        old = Path(directory.name) / "save.json"
        old.write_text(json.dumps({
            "version": 1, "checkpoint_id": "waterdeep_anchor", "sanity": 60,
            "progress_flags": [], "cigarettes": 3, "deaths": 1, "spoken": [],
        }), encoding="utf-8")
        before = old.read_text(encoding="utf-8")

        path = Path(directory.name) / "save2.json"
        game = Game(save_path=path)
        try:
            assert game.checkpoints.write_save("temple_1", 55)
        finally:
            game._shutdown()

        assert path.exists(), "the new save went somewhere else"
        assert old.read_text(encoding="utf-8") == before, "it ate the old save"
        # ...and a version-1 file is refused rather than misread.
        assert SaveSystem(old).load() is None
    finally:
        directory.cleanup()


def test_a_door_is_a_save_point_and_a_cutscene_handoff_is_not() -> None:
    from src.systems.checkpoints import is_save_point
    from src.systems import save_registry

    assert is_save_point("pantry_entry")          # walked in by
    assert is_save_point("temple_1")
    assert not is_save_point("waterdeep_finale")  # arrived at by cutscene
    assert not is_save_point("not_a_checkpoint")
    # Every door in the registry is one, which is what makes a record
    # writable as a code.
    for entry in save_registry.SAVE_ENTRIES:
        if entry:
            assert is_save_point(entry), entry

    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        try:
            game.checkpoints.write_save("waterdeep_finale", 60)
        except ValueError as exc:
            assert "not a save point" in str(exc)
        else:
            raise AssertionError("a cutscene handoff should not be saveable")
    finally:
        game._shutdown()
        directory.cleanup()


def test_a_save_written_at_a_door_survives_the_round_trip() -> None:
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        game.progress.enable("sewer_completed")
        game.cigarettes.replace(42)
        game.deaths.replace(3)
        assert game.checkpoints.write_save("chult_2", 77)
    finally:
        game._shutdown()
    try:
        record = SaveSystem(path).load()
        assert record is not None
        assert record.checkpoint_id == "chult_2"
        assert record.sanity == 77
        assert "sewer_completed" in record.progress_flags
        assert record.cigarettes == 42 and record.deaths == 3
    finally:
        directory.cleanup()


def test_every_door_is_somewhere_chuck_can_stand() -> None:
    """The door is the respawn point now, so every door has to be one.

    Loads all of them and checks the spot he would come back to is not
    inside a wall. One was: the climb out of the sewer outflow starts a
    tile lower than it finishes, with the animation running, so the
    arrival position is in the harbour. Dying on those docks would have
    dropped him in the water.
    """
    from src.systems import save_registry

    directory, path = _temp_save()
    game = Game(save_path=path)
    size = config.TILE_SIZE
    try:
        doors = [entry for entry in save_registry.SAVE_ENTRIES if entry]
        assert len(doors) >= 100
        for entry in doors:
            scene = game.checkpoints.load_checkpoint(entry)
            x, y = scene.anchors_system.respawn_position_for_chuck()
            col = int((x + scene.player.width / 2) // size)
            row = int((y + scene.player.height / 2) // size)
            assert not scene.tilemap.is_solid(col, row), (
                entry, scene.map_name, col, row)
    finally:
        game._shutdown()
        directory.cleanup()
