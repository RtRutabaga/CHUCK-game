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
        scene = game.scenes.current
        assert calls == [(OPENING_CHECKPOINT_ID, {"cigarettes": 0})]
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
        assert (scene.player.x, scene.player.y) == (anchor.x, anchor.y)
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
             "cigarettes": 0},
        )]
        assert scene.map_name == "waterdeep_docks"
        assert scene.sanity.current == 47
        assert scene.tilemap.terrain_at(44, 17) == "v"
        assert scene.anchors[0].lit
    finally:
        game._shutdown()
        directory.cleanup()


def test_continue_rejects_non_saveable_or_unknown_checkpoint_ids() -> None:
    directory, path = _temp_save()
    try:
        for checkpoint_id in ("pantry_entry", "not_a_checkpoint"):
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
        press("move_right")
        assert selector.page == 0  # wrapped around
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
            "Waterdeep 2", "Tavern 1", "Pantry 1",
            "Chult 1", "Chult 2", "Chult 3", "Chult 4", "Chult 5",
            "Temple 1", "Temple 2", "Temple 3", "Temple 4", "Temple 5",
            "Temple 6", "Temple 7", "Temple 8", "Temple 9",
            "Rubble 1", "Ship 1", "Ship Hold",
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
