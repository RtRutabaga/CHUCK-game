"""Phase 13's second eastern map: the collision's second step.

The phase document asks for escalation rather than arrival -- small
intrusions early, heavily fragmented later -- which is a property of a
*sequence* and cannot be checked one map at a time. That comparison
runs over the whole run of eastern maps in test_phase13_east_3_4; what
is left here is what this map is on its own.

The other two things worth pinning are that the jungle does not block
the way through, and that it can be walked into anyway. Those sound
like the same claim and are not: an intrusion nobody has to enter still
has to be enterable, and "thick growth with gaps in it" and "a wall
with a hole somewhere" look identical in a screenshot. The first two
attempts at the growth pattern were neither. A modular hash of x and y
is constant along parallel lines, so the jungle came out striped; the
diagonal version left its open tiles touching only at their corners,
and a rat walks on edges, so there was no way through it at all.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.snake import TempleSnake
from src.systems.checkpoints import CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import CHULT, COLLIDED, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_desert_east_2 import (  # noqa: E402
    GAP, HEIGHT, RIM, WIDTH,
)


MAP_NAME = "desert_east_2"
BEHIND = "desert_east_1"

DESERT_GROUND = (".", ",", "⟁", "#", "⌗", "⌖", "⍟")
# Which intruding world each foreign character belongs to.
FRAGMENTS = {
    "=": "modern_city", "≡": "modern_city",
    "ᛗ": "chult", "ᚷ": "chult", "ᚺ": "chult",
}


def _tilemap(name: str = MAP_NAME) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _world(checkpoint: str = "desert_east_2"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _flood(tilemap, origin, extra_solid=()) -> set[tuple[int, int]]:
    seen = {origin}
    frontier = [origin]
    while frontier:
        x, y = frontier.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in seen or tilemap.is_solid(*cell):
                continue
            terrain = tilemap.terrain_at(*cell)
            if terrain in collision.FALL_HAZARD_TERRAIN:
                continue
            if terrain in extra_solid:
                continue
            seen.add(cell)
            frontier.append(cell)
    return seen


def _survey(name: str) -> tuple[float, set[str]]:
    """(how much of the map is not desert, which worlds it came from)."""
    tilemap = _tilemap(name)
    width, height = tilemap.width_tiles, tilemap.height_tiles
    foreign = 0
    worlds: set[str] = set()
    for y in range(height):
        for x in range(width):
            char = tilemap.terrain_at(x, y)
            if char in FRAGMENTS:
                foreign += 1
                worlds.add(FRAGMENTS[char])
    return foreign / (width * height), worlds


def test_this_map_is_two_worlds_and_still_mostly_desert() -> None:
    """What this map is, on its own.

    The comparison against the map behind it -- and against every map
    ahead of it -- moved to test_phase13_east_3_4 once there was a run
    of maps to compare. Escalation is a property of the sequence, and
    checking it pairwise in each map's own file means every new map
    east edits the file before it.
    """
    here_share, here_worlds = _survey(MAP_NAME)
    assert here_worlds == {"modern_city", "chult"}
    assert here_share > 0.10, here_share

    # Still mostly desert, because this is early.
    tilemap = _tilemap()
    desert = sum(1 for y in range(HEIGHT) for x in range(WIDTH)
                 if tilemap.terrain_at(x, y) in DESERT_GROUND)
    assert desert / (WIDTH * HEIGHT) > 0.65, desert / (WIDTH * HEIGHT)

    # Nothing on the map is unaccounted for: every character is desert,
    # a named fragment, the Sea, or a door.
    seen = {tilemap.terrain_at(x, y)
            for y in range(HEIGHT) for x in range(WIDTH)}
    assert seen <= set(DESERT_GROUND) | set(FRAGMENTS) | {"V", "⮜", "⮞"},         seen


def test_the_jungle_is_the_jungle_chuck_crossed() -> None:
    """The same rows, pixel for pixel, under different characters.

    Chult spells its ground "." and its growth "#", and the desert had
    both first -- so the fragment could not keep its spelling. It has to
    keep its art, or the fragment stops being a memory of anywhere.
    """
    assert tileset_for(MAP_NAME) is COLLIDED
    # The pixels are checked in test_phase13_collided_tileset, which
    # owns the sheet. What belongs here is that this map's characters
    # behave the way Chult's do underfoot -- the art being right is no
    # use if the ground it names walks differently.
    assert COLLIDED.char_to_terrain["ᛗ"] == CHULT.char_to_terrain["."]
    assert COLLIDED.char_to_terrain["ᚷ"] == CHULT.char_to_terrain["#"]
    assert not TILE_DEFS["ᛗ"].solid and TILE_DEFS["ᚷ"].solid
    assert TILE_DEFS["ᚺ"].solid, "a stream is water, and water stops him"


def test_the_snakes_came_with_it_and_they_are_in_it() -> None:
    directory, game, world = _world()
    try:
        assert len(world.snakes) >= 6, len(world.snakes)
        # The temple's snake, unchanged: the phase document asks for
        # familiar systems in new combinations, not new systems.
        assert all(isinstance(s, TempleSnake) for s in world.snakes)
    finally:
        game._shutdown()
        directory.cleanup()

    tilemap = _tilemap()
    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k == "arrival:from_east_1")
    seen = _flood(tilemap, (int(arrival[0]) // ts, int(arrival[1]) // ts))
    spots = [(int(p[0]) // ts, int(p[1]) // ts)
             for k, p in tilemap.object_spawns if k == "snake"]
    assert len(set(spots)) == len(spots), "two snakes in one tile"
    for cell in spots:
        # Every one on open jungle floor, and every one reachable: a
        # snake walled into dense growth is a snake that never happens.
        assert tilemap.terrain_at(*cell) == "ᛗ", cell
        assert cell in seen, cell


def test_the_jungle_can_be_walked_past_and_walked_into() -> None:
    """Two claims, and they are not the same claim.

    Past: with every foreign tile treated as solid the far door is
    still reachable, so nothing that fell into this map stands between
    the two doors. Into: the open ground inside the growth is one
    connected mass rather than scattered pockets, so a player who does
    go in can get about -- which is the property both earlier versions
    of the growth pattern silently failed.
    """
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k == "arrival:from_east_1")
    origin = (int(arrival[0]) // ts, int(arrival[1]) // ts)

    east_gap = [(WIDTH - 1, y) for y in range(HEIGHT)
                if not tilemap.is_solid(WIDTH - 1, y)]
    assert len(east_gap) == GAP

    without = _flood(tilemap, origin, extra_solid=set(FRAGMENTS))
    assert all(cell in without for cell in east_gap),         "the fragments block the way through"

    reachable = _flood(tilemap, origin)
    floor = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
             if tilemap.terrain_at(x, y) == "ᛗ"]
    dense = sum(1 for y in range(HEIGHT) for x in range(WIDTH)
                if tilemap.terrain_at(x, y) == "ᚷ")
    assert len(floor) > 150 and dense > 100
    # Thick, but not a maze: a good third of the jungle is open.
    assert 0.25 < dense / (len(floor) + dense) < 0.6

    # Nearly all of that open ground is one connected piece. A handful
    # of sealed pockets is what a real thicket looks like; a jungle in
    # scattered islands is one nobody can walk about in.
    joined = [cell for cell in floor if cell in reachable]
    assert len(joined) > len(floor) * 0.95, (len(joined), len(floor))
    # ...and it runs the width of the wedge rather than one end of it.
    assert min(x for x, _ in joined) < WIDTH * 0.3
    assert max(x for x, _ in joined) > WIDTH * 0.7

    # The wedge really does stop short of the southern half, which is
    # what leaves the clear way past it.
    southern = {tilemap.terrain_at(x, y)
                for y in range(int(HEIGHT * 0.7), HEIGHT - RIM)
                for x in range(RIM, WIDTH - RIM)}
    assert not southern & {"ᛗ", "ᚷ", "ᚺ"}, southern


def test_the_road_east_continues_in_both_directions() -> None:
    assert AREA_WALK_EXITS[(BEHIND, "⮞")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].destination == BEHIND
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[BEHIND]

    ts = config.TILE_SIZE
    directory, game, world = _world("desert_east_1")
    try:
        world.player.x = (world.tilemap.width_tiles - 1) * ts + 2
        world.player.y = (world.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            world.update(1 / 60)
        here = game.scenes.current
        assert here.map_name == MAP_NAME
        here._arrival_fade_t = None

        here.player.x = 2.0
        here.player.y = (here.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            here.update(1 / 60)
        back = game.scenes.current
        assert back.map_name == BEHIND
        assert int(back.player.x) // ts >= back.tilemap.width_tiles - RIM - 4
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_has_its_own_entries() -> None:
    for entry in ("desert_east_2", "desert_east_2_anchor",
                  "desert_east_1_from_east_2"):
        assert CHECKPOINT_BY_ID[entry].required_flags == DESERT_ENTRY_FLAGS
    assert CHECKPOINT_BY_ID["desert_east_2_anchor"].saveable
    assert CHECKPOINT_BY_ID["desert_east_2"].development_visible

    tilemap = _tilemap()
    ts = config.TILE_SIZE
    anchor = CHECKPOINT_BY_ID["desert_east_2_anchor"].position
    spawn = next(p for k, p in tilemap.object_spawns
                 if k == "anchor:desert_east_2_anchor")
    assert anchor is not None
    assert (int(anchor[0]) // ts, int(anchor[1]) // ts) == \
        (int(spawn[0]) // ts, int(spawn[1]) // ts)


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
    print("All east-2 tests passed.")


if __name__ == "__main__":
    _run_all()
