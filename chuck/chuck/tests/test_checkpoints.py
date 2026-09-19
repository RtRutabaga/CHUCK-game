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
from src.systems.checkpoints import (
    CHECKPOINTS, OPENING_CHECKPOINT_ID, CheckpointLoader)
from src.systems import save_code
from src.systems.save import SaveRecord
from src.ui.bitmap_font import GLYPH_ORDER


def _temp_save() -> tuple[tempfile.TemporaryDirectory, Path]:
    directory = tempfile.TemporaryDirectory()
    return directory, Path(directory.name) / "save.json"


def _boot_to_title(game: Game) -> TitleScene:
    assert isinstance(game.scenes.current, BootScene)
    game.scenes.current.update(0.01)
    assert isinstance(game.scenes.current, TitleScene)
    return game.scenes.current


def _play_through_opening(game) -> None:
    """New Game opens on the wake-up cutscene; run it to its hand-off."""
    from src.scenes.opening_cutscene_scene import OpeningCutsceneScene

    scene = game.scenes.current
    assert isinstance(scene, OpeningCutsceneScene)
    while game.scenes.current is scene:
        scene.update(0.25)


def test_the_title_offers_no_continue_and_new_game_uses_the_loader() -> None:
    """There is no CONTINUE: a code is the only way back into a game."""
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        title = _boot_to_title(game)
        assert "CONTINUE" not in title.options
        assert title.options == ("NEW GAME", "LOAD CODE", "CONTROLS")
        # Every option is reachable; none is greyed out any more.
        for step in range(len(title.options)):
            title._move(1)
            assert title._selected == (step + 1) % len(title.options)
        title._selected = 0

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


def test_a_saved_code_relaunches_into_the_same_game_and_respawn() -> None:
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        game.progress.enable("sewer_completed")
        game.scenes.replace(WorldScene(game, "waterdeep_docks"))
        scene = game.scenes.current
        scene.sanity.current = 47
        came_in = scene.respawn.position_for_chuck()
        scene.update(0.01)
        # The save the menu banks, at the door he came in by. It is
        # handed back as a record, and the code is made of it.
        record = game.checkpoints.save_here("waterdeep_start", 47)
        assert record == SaveRecord(
            "waterdeep_start", 47, ("sewer_completed",)
        )
        code = save_code.for_display(record)
        assert game.active_checkpoint_id == "waterdeep_start"

        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT)
        scene.update(config.RESPAWN_HOLD)
        # The door he came in by.
        assert (scene.player.x, scene.player.y) == came_in
        assert scene.sanity.current == config.SANITY_MAX
    finally:
        game._shutdown()

    # A fresh launch that has never seen this game, resuming from the
    # twelve characters alone.
    game = Game(save_path=path)
    try:
        _boot_to_title(game)
        calls = []
        real_load = game.checkpoints.load_checkpoint
        game.checkpoints.load_checkpoint = lambda checkpoint_id, **kwargs: (
            calls.append((checkpoint_id, kwargs))
            or real_load(checkpoint_id, **kwargs)
        )
        scene = game.checkpoints.resume_from(save_code.decode(code))
        assert calls == [(
            "waterdeep_start",
            {"progress_flags": ("sewer_completed",),
             "sanity": config.SANITY_START,
             "cigarettes": 0, "deaths": 0},
        )]
        assert scene.map_name == "waterdeep_docks"
        # Sanity is what a code trades away for being twelve characters.
        assert scene.sanity.current == config.SANITY_START
        assert scene.tilemap.terrain_at(44, 17) == "v"
    finally:
        game._shutdown()
        directory.cleanup()


def test_continue_rejects_ids_that_are_not_save_points() -> None:
    """A save names a door Chuck walked in by, or it is not a save.

    `pantry_entry` used to be listed here as something to refuse, back
    when only an door could be saved at. It is a door, so it is a
    save point now. What stays refused is a checkpoint that is neither
    -- `waterdeep_finale` is reached by a cutscene, not walked into --
    and an id that is not a checkpoint at all.
    """
    for checkpoint_id in ("waterdeep_finale", "not_a_checkpoint"):
        record = SaveRecord(checkpoint_id, 60, ())
        assert not CheckpointLoader.can_resume(record), checkpoint_id


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
            "Waterdeep 1", "Sewer 1",             "Waterdeep 2", "Waterdeep Finale", "Fountain Plaza",
            "Fountain Plaza Finale", "Tavern 1", "Pantry 1",
            "Chult 2", "Chult 3", "Chult 4", "Chult Falls",
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
            "Feywild 4", "Feywild 6", "Feywild 7",
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
            game.checkpoints.save_here("waterdeep_finale", 60)
        except ValueError as exc:
            assert "not a save point" in str(exc)
        else:
            raise AssertionError("a cutscene handoff is not a save point")
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
        code = save_code.for_display(
            game.checkpoints.save_here("chult_2", 77))
    finally:
        game._shutdown()
    try:
        # The round trip is the code's, because the code is the save.
        record = save_code.decode(code)
        assert record.checkpoint_id == "chult_2"
        # Sanity is the one thing a code does not carry.
        assert record.sanity == config.SANITY_START
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
            x, y = scene.respawn.position_for_chuck()
            col = int((x + scene.player.width / 2) // size)
            row = int((y + scene.player.height / 2) // size)
            assert not scene.tilemap.is_solid(col, row), (
                entry, scene.map_name, col, row)
    finally:
        game._shutdown()
        directory.cleanup()
