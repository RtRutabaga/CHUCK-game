"""Phase 14's shared Waterdeep fountain plaza."""

import os
from collections import deque
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import WATERDEEP_RETURN_FLAG
from src.systems.waterdeep_finale import (
    PLAZA_TOWNSFOLK, RETURN_PLAZA_TOWNSFOLK,
)
from src.world.tilemap import TileMap
from src.world.tileset_layout import DOCKS, DOCKS_MIDDAY, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


def _game() -> tuple[tempfile.TemporaryDirectory, Game]:
    directory = tempfile.TemporaryDirectory()
    return directory, Game(save_path=Path(directory.name) / "save.json")


def test_plaza_uses_one_map_and_waterdeep_art_in_both_eras() -> None:
    tilemap = TileMap(config.MAPS_DIR / "waterdeep_plaza.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (48, 34)
    assert tileset_for("waterdeep_plaza") is DOCKS
    assert tileset_for(
        "waterdeep_plaza", waterdeep_returned=True
    ) is DOCKS_MIDDAY
    assert AREA_MUSIC["waterdeep_plaza"] == "waterdeep_docks.wav"

    kinds = [kind for kind, _col, _row in tilemap.prop_tiles]
    for expected in (
        "waterdeep_fountain", "waterdeep_closed_gate", "waterdeep_forge",
        "waterdeep_anvil", "waterdeep_alchemist_display",
    ):
        assert kinds.count(expected) == 1


def test_eastern_docks_street_is_a_two_way_shared_route() -> None:
    docks_exit = AREA_WALK_EXITS[("waterdeep_docks", "⮞")]
    plaza_exit = AREA_WALK_EXITS[("waterdeep_plaza", "⮜")]
    assert (docks_exit.destination, docks_exit.arrival, docks_exit.facing) == (
        "waterdeep_plaza", "from_docks", "right"
    )
    assert (plaza_exit.destination, plaza_exit.arrival, plaza_exit.facing) == (
        "waterdeep_docks", "from_plaza", "left"
    )

    docks = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    plaza = TileMap(config.MAPS_DIR / "waterdeep_plaza.txt")
    assert sum(row.count("⮞") for row in docks._grid) == 6
    assert sum(row.count("⮜") for row in plaza._grid) == 6
    assert any(kind == "arrival:from_plaza"
               for kind, _position in docks.object_spawns)
    assert any(kind == "arrival:from_docks"
               for kind, _position in plaza.object_spawns)


def test_opening_and_finale_share_geometry_but_not_population_or_light() -> None:
    directory, game = _game()
    try:
        opening = game.checkpoints.load_checkpoint("waterdeep_plaza_from_docks")
        opening_grid = tuple(opening.tilemap._grid)
        assert opening.tilemap._tileset.sheet == "docks.png"
        assert len(opening.npcs) == len(PLAZA_TOWNSFOLK)
        assert not game.progress.has(WATERDEEP_RETURN_FLAG)

        finale = game.checkpoints.load_checkpoint("waterdeep_plaza_finale")
        assert tuple(finale.tilemap._grid) == opening_grid
        assert finale.tilemap._tileset.sheet == "docks_midday.png"
        assert len(finale.npcs) == (
            len(PLAZA_TOWNSFOLK) + len(RETURN_PLAZA_TOWNSFOLK)
        )
        assert game.progress.has(WATERDEEP_RETURN_FLAG)
    finally:
        game._shutdown()
        directory.cleanup()


def test_plaza_state_survives_both_directions_of_normal_travel() -> None:
    directory, game = _game()
    try:
        opening = game.checkpoints.load_checkpoint("waterdeep_start")
        opening.load_map("waterdeep_plaza", arrival="from_docks", facing="right")
        assert not game.progress.has(WATERDEEP_RETURN_FLAG)
        assert opening.tilemap._tileset.sheet == "docks.png"
        opening.load_map("waterdeep_docks", arrival="from_plaza", facing="left")
        assert not game.progress.has(WATERDEEP_RETURN_FLAG)

        finale = game.checkpoints.load_checkpoint("waterdeep_finale")
        finale.load_map("waterdeep_plaza", arrival="from_docks", facing="right")
        assert game.progress.has(WATERDEEP_RETURN_FLAG)
        assert finale.tilemap._tileset.sheet == "docks_midday.png"
        assert len(finale.npcs) == (
            len(PLAZA_TOWNSFOLK) + len(RETURN_PLAZA_TOWNSFOLK)
        )
        finale.load_map("waterdeep_docks", arrival="from_plaza", facing="left")
        assert game.progress.has(WATERDEEP_RETURN_FLAG)
        assert finale.tilemap._tileset.sheet == "docks_midday.png"
    finally:
        game._shutdown()
        directory.cleanup()


def test_return_state_survives_the_existing_waterdeep_save_point() -> None:
    directory, game = _game()
    save_path = Path(directory.name) / "save.json"
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_finale")
        scene._arrival_fade_t = None
        anchor = scene.anchors[0]
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.update(0.01)
        record = game.saves.load()
        assert record is not None
        assert WATERDEEP_RETURN_FLAG in record.progress_flags
    finally:
        game._shutdown()

    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.continue_game()
        assert scene is not None
        assert scene.tilemap._tileset.sheet == "docks_midday.png"
        scene.load_map("waterdeep_plaza", arrival="from_docks", facing="right")
        assert scene.tilemap._tileset.sheet == "docks_midday.png"
        assert len(scene.npcs) == (
            len(PLAZA_TOWNSFOLK) + len(RETURN_PLAZA_TOWNSFOLK)
        )
    finally:
        game._shutdown()
        directory.cleanup()


def test_fountain_animates_and_the_northern_gate_is_closed() -> None:
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_plaza_from_docks")
        fountain = next(
            prop for prop in scene.props if prop.kind == "waterdeep_fountain"
        )
        assert fountain._size == (72, 56)
        assert len(fountain._frames) == 4
        first = fountain._image
        fountain.update(0.25)
        assert fountain._image is not first
        assert all(scene.tilemap.is_solid(col, row)
                   for row in range(16, 19) for col in range(22, 27))

        assert scene.tilemap.is_solid(24, 3)
        assert all(scene.tilemap.is_solid(col, row)
                   for row in (0, 1) for col in range(48))
        gate = next(
            prop for prop in scene.props
            if prop.kind == "waterdeep_closed_gate"
        )
        assert gate.dialogue_id == "plaza_gate"
        assert gate.choice_id is None
    finally:
        game._shutdown()
        directory.cleanup()


def test_shopkeepers_only_speak_and_every_person_stands_off_the_route() -> None:
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_plaza_finale")
        by_dialogue = {npc.dialogue_id: npc for npc in scene.npcs}
        assert scene.dialogue.get("blacksmith") == ["I don't shoe rats."]
        assert scene.dialogue.get("alchemist") == ["No samples."]
        assert scene.dialogue.get("plaza_guard") == ["Gate's closed."]
        assert "blacksmith" in by_dialogue and "alchemist" in by_dialogue

        for spawn in (*PLAZA_TOWNSFOLK, *RETURN_PLAZA_TOWNSFOLK):
            assert not scene.tilemap.is_solid(*spawn.tile), spawn
    finally:
        game._shutdown()
        directory.cleanup()


def test_plaza_remains_navigable_around_the_fountain_and_shops() -> None:
    tilemap = TileMap(config.MAPS_DIR / "waterdeep_plaza.txt")
    start = (2, 20)
    queue = deque([start])
    seen = {start}
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (col + dc, row + dr)
            if nxt in seen or tilemap.is_solid(*nxt):
                continue
            seen.add(nxt)
            queue.append(nxt)
    assert {(21, 4), (27, 4), (9, 13), (37, 13),
            (21, 20), (28, 20), (15, 30)} <= seen


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
    print("All Phase 14 fountain-plaza tests passed.")


if __name__ == "__main__":
    _run_all()
