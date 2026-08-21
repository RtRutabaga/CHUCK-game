"""Phase 12 table-map awakening, persistence, and visual state."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.cabin_progress import (
    CABIN_ENTITY_FLAGS,
    COUNTER_MAP_AWAKENED_FLAG,
    apply_cabin_door_crossing,
)
from src.systems.checkpoints import ProgressState


INTERIOR = "tahuya_cabin_interior"
EXTERIOR = "tahuya_cabin_exterior"


def _game():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game


def _tile_with(world, terrain):
    return next(
        (col, row)
        for row in range(world.tilemap.height_tiles)
        for col in range(world.tilemap.width_tiles)
        if world.tilemap.terrain_at(col, row) == terrain
    )


def _stand_on(world, terrain):
    col, row = _tile_with(world, terrain)
    world.player.x = col * config.TILE_SIZE
    world.player.y = row * config.TILE_SIZE + 4
    world.update(0.0)


def _table(world):
    return next(prop for prop in world.props
                if prop.kind.startswith("cabin_table"))


def test_rule_requires_all_four_and_a_later_cabin_door_crossing() -> None:
    progress = ProgressState()
    for flag in sorted(CABIN_ENTITY_FLAGS)[:-1]:
        progress.enable(flag)
    assert not apply_cabin_door_crossing(
        progress, INTERIOR, EXTERIOR, "from_cabin_front"
    )
    assert not progress.has(COUNTER_MAP_AWAKENED_FLAG)

    progress.enable(sorted(CABIN_ENTITY_FLAGS)[-1])
    # Finishing the fourth conversation alone does not awaken the table.
    assert not progress.has(COUNTER_MAP_AWAKENED_FLAG)
    assert not apply_cabin_door_crossing(
        progress, INTERIOR, EXTERIOR, "wrong_arrival"
    )
    assert not progress.has(COUNTER_MAP_AWAKENED_FLAG)

    assert apply_cabin_door_crossing(
        progress, INTERIOR, EXTERIOR, "from_cabin_front"
    )
    assert progress.has(COUNTER_MAP_AWAKENED_FLAG)
    assert not apply_cabin_door_crossing(
        progress, EXTERIOR, INTERIOR, "from_front_door"
    )


def test_real_south_threshold_awakens_and_rebuilds_the_rectangular_map() -> None:
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint(
            "tahuya_interior", progress_flags=CABIN_ENTITY_FLAGS
        )
        assert _table(world).kind == "cabin_table"
        assert not game.progress.has(COUNTER_MAP_AWAKENED_FLAG)

        # Crossing out through the sole authored south threshold is the event.
        _stand_on(world, "Ɯ")
        assert world.map_name == EXTERIOR
        assert game.progress.has(COUNTER_MAP_AWAKENED_FLAG)

        # The same physical doorway returns to an already-awakened interior.
        _stand_on(world, "Ɛ")
        assert world.map_name == INTERIOR
        table = _table(world)
        assert table.kind == "cabin_table_awakened"
        assert len(table._frames) == 8
        assert len({pygame.image.tobytes(frame, "RGBA")
                    for frame in table._frames}) == 8
        assert all(frame.get_size() == (144, 57)
                   for frame in table._frames)
        assert table.choice_id is None and table.dialogue_id is None
        assert next(prop for prop in world.props
                    if prop.kind == "cabin_kitchen")._frames == ()
    finally:
        game._shutdown()
        directory.cleanup()


def test_awakened_state_survives_save_continue_and_shared_dev_loading() -> None:
    flags = CABIN_ENTITY_FLAGS | {COUNTER_MAP_AWAKENED_FLAG}
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint(
            "tahuya_interior", progress_flags=flags
        )
        assert _table(world).kind == "cabin_table_awakened"
        assert game.checkpoints.activate_checkpoint(
            "tahuya_interior_anchor", world.sanity.current
        )
        continued = game.checkpoints.continue_game()
        assert game.progress.has(COUNTER_MAP_AWAKENED_FLAG)
        assert _table(continued).kind == "cabin_table_awakened"

        # Development and production both use the same checkpoint loader.
        direct = game.checkpoints.load_checkpoint(
            "tahuya_interior", progress_flags=flags
        )
        assert _table(direct).kind == "cabin_table_awakened"
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
                print(f"  FAIL  {name}: {exc!r}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All Cabin table-awakening tests passed.")


if __name__ == "__main__":
    _run_all()
