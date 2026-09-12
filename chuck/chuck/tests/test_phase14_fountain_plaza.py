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

import sys
sys.path.insert(0, "tools")
from generate_waterdeep_plaza import (  # noqa: E402
    PLAZA_BARRELS, PLAZA_CIGARETTES, PLAZA_CRATES, PLAZA_WEEDS,
    largest_bare_patch,
)


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
    assert docks_exit.keep_row and plaza_exit.keep_row

    docks = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    plaza = TileMap(config.MAPS_DIR / "waterdeep_plaza.txt")
    # The whole open east side of the docks is the way to the plaza: every
    # tile on its last column that is not a building is an exit.
    east = docks.width_tiles - 1
    open_east = [row for row in range(docks.height_tiles)
                 if not docks.is_solid(east, row)]
    assert len(open_east) > 20
    assert all(docks.terrain_at(east, row) == "⮞" for row in open_east)
    # ...and the plaza has no west wall at all: below the north wall and
    # above the south one, its whole west side is the way back.
    for row in range(4, plaza.height_tiles - 1):
        assert plaza.terrain_at(0, row) == "⮜", row
        assert plaza.terrain_at(1, row) == "⮜", row
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

        # The gate is set into the wall, not stood in front of it: the
        # wall is at least as tall as the gate, the gate's tile is the
        # wall's bottom course, and the paving starts right under it.
        assert all(scene.tilemap.is_solid(col, row)
                   for row in range(4) for col in range(48))
        assert scene.tilemap.terrain_at(24, 3) == "ϟ"
        assert not scene.tilemap.is_solid(24, 4)
        gate_prop = next(prop for prop in scene.props
                         if prop.kind == "waterdeep_closed_gate")
        assert gate_prop._draw_y >= 0          # its top is inside the wall
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


def _rows(name: str) -> list[str]:
    text = (config.MAPS_DIR / f"{name}.txt").read_text(encoding="utf-8")
    return [line for line in text.splitlines() if not line.startswith(";")]


def test_nowhere_in_the_square_is_a_screenful_of_nothing() -> None:
    """The complaint the dressing pass answers, as a number.

    The plaza's first version had 42x7 tiles of unbroken paving in it --
    over two screens wide and most of one tall. The docks, which is the
    map this square is meant to feel like, never manages worse than 49
    tiles and its worst case is a single row deep.

    A plaza is allowed to be open; that is what a plaza is for. What it
    is not allowed to be is a room a player can cross without noticing
    anything, and that is a measurable difference rather than a taste.
    """
    plaza = largest_bare_patch(_rows("waterdeep_plaza"))
    docks = largest_bare_patch(_rows("waterdeep_docks"))
    assert plaza[0] < 110, plaza
    # In the same country as the docks rather than an order out.
    assert plaza[0] < docks[0] * 3, (plaza, docks)


def test_the_dressing_only_ever_lands_on_paving() -> None:
    """Nothing furnishes over a shop front, a stall post or a doorway.

    Dressing that can silently land on authored geometry is dressing
    that will one day delete a route, and the failure mode is a plaza
    that looks finished and cannot be walked across. The generator
    asserts this as it writes; this asserts it about what was written.
    """
    rows = _rows("waterdeep_plaza")
    for group, char in ((PLAZA_BARRELS, "O"), (PLAZA_CRATES, "X"),
                        (PLAZA_WEEDS, "{"), (PLAZA_CIGARETTES, "c")):
        assert group, char
        for col, row in group:
            assert rows[row][col] == char, (col, row, rows[row][col])

    # Stacks stay small: nothing here is a wall by accident.
    solid = set(PLAZA_BARRELS) | set(PLAZA_CRATES)
    for col, row in solid:
        run = 1
        while (col + run, row) in solid:
            run += 1
        assert run <= 3, (col, row, run)


def test_the_square_has_something_to_scratch_at() -> None:
    """Every other map in the city does, and this one did not.

    The weeds between the paving stones are the cheap half of the
    dressing and the useful half: non-solid, so they can never narrow a
    route, and each one has a cigarette under it.
    """
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("waterdeep_plaza_from_docks")
        assert len(world.breakables) == len(PLAZA_WEEDS)
        assert len(world.pickups) == len(PLAZA_CIGARETTES)
        # ...and none of it is in anybody's way.
        for weed in world.breakables:
            ts = config.TILE_SIZE
            tile = (int(weed.x) // ts, int(weed.y) // ts)
            assert not world.tilemap.is_solid(*tile), tile
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
            (21, 20), (28, 20), (15, 30),
            # The corners and the flanks, because a furnishing pass is
            # exactly the kind of change that walls one off.
            (2, 4), (45, 4), (2, 32), (45, 32),
            (3, 20), (45, 20), (6, 25), (24, 13)} <= seen


def test_crossing_the_edge_keeps_chuck_on_his_row() -> None:
    """Walk off the long edge anywhere and arrive level with where he left.

    Both eras, both directions. Where the row he left on is a building on
    the other side, he comes out on the nearest open row instead.
    """
    for checkpoint in ("waterdeep_start", "waterdeep_finale"):
        directory, game = _game()
        try:
            scene = game.checkpoints.load_checkpoint(checkpoint)
            ts = config.TILE_SIZE
            east = scene.tilemap.width_tiles - 1
            for row in (3, 30):
                scene.load_map("waterdeep_docks", arrival="from_plaza",
                               facing="left")
                scene.player.x = east * ts + 3
                scene.player.y = row * ts + 4
                scene.update(1 / 60)
                assert scene.map_name == "waterdeep_plaza", (checkpoint, row)
                arrived = int((scene.player.y + scene.player.height / 2)
                              // ts)
                expected = max(row, 4)          # rows 0-3 are the wall
                assert arrived == expected, (checkpoint, row, arrived)

            # Back the other way from a row that is a building in the docks.
            scene.load_map("waterdeep_plaza", arrival="from_docks",
                           facing="right")
            scene.player.x = 0 * ts + 3
            scene.player.y = 12 * ts + 4
            scene.update(1 / 60)
            assert scene.map_name == "waterdeep_docks"
            col = int((scene.player.x + scene.player.width / 2) // ts)
            row = int((scene.player.y + scene.player.height / 2) // ts)
            assert not scene.tilemap.is_solid(col, row)
            assert abs(row - 12) <= 6, row
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
    print("All Phase 14 fountain-plaza tests passed.")


if __name__ == "__main__":
    _run_all()
