"""Phase 13's eighth map east: the ground has mostly gone.

The seventh map is nine worlds touching each other; this is the same
worlds not touching. The escalation is structural rather than another
count of fragments -- up to here "further gone" has meant more of
somewhere else and less desert, and here it means there is less of
anything. Two thirds of the map is Astral Sea and what is left is
islands joined by ledges two tiles wide.

Three properties carry the map and all three are measured.

The Sea has to actually dominate, and by a distance: a map that is
merely torn is the map behind this one. So its share is checked
against every earlier map rather than against a number.

The ledges have to be ledges. A causeway four tiles wide is a road
with a view, and the whole difficulty of this map is that there is
nowhere to step aside to -- so the width is measured across every
stretch of every one of them that is out over the Sea.

And two islands have to be unreachable. That is the odd one, because
it is a thing the map must fail to do: a collision this big should
have places in it that Chuck can only look at, and the natural drift
of any later edit is to join them up.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS
from src.world import collision
from src.world.tilemap import MARKER_DEFS, TileMap
from src.world.tileset_layout import COLLIDED, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_desert_east_8 import (  # noqa: E402
    CAUSEWAYS, CLEARANCE, GAP, GARRISON, HEIGHT, ISLANDS, MID_Y, RIM,
    WIDTH, island_at,
)


MAP_NAME = "desert_east_8"
BEHIND = "desert_east_7"
EARLIER = tuple(f"desert_east_{index}" for index in range(1, 8))

# The islands nothing reaches. Named here rather than derived, because
# it is the one property a later edit removes by being helpful.
MAROONED = (8, 9)
FAR_SHORE = 5


def _tilemap(name: str = MAP_NAME) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _world(checkpoint: str = MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _safe_flood(tilemap: TileMap, origin) -> set[tuple[int, int]]:
    seen = {origin}
    frontier = [origin]
    while frontier:
        x, y = frontier.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in seen or tilemap.is_solid(*cell):
                continue
            if tilemap.terrain_at(*cell) in collision.FALL_HAZARD_TERRAIN:
                continue
            seen.add(cell)
            frontier.append(cell)
    return seen


def _reachable() -> set[tuple[int, int]]:
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k == "arrival:from_east_7")
    return _safe_flood(tilemap, (int(arrival[0]) // ts, int(arrival[1]) // ts))


def _sea_share(name: str) -> float:
    tilemap = _tilemap(name)
    sea = sum(
        1 for y in range(tilemap.height_tiles)
        for x in range(tilemap.width_tiles)
        if tilemap.terrain_at(x, y) == "V"
    )
    return sea / (tilemap.width_tiles * tilemap.height_tiles)


def test_the_sea_is_the_map_now() -> None:
    """Measured against every map behind it, not against a number.

    "Further gone" has meant more of somewhere else on every map so
    far. Here it means less of anything: what the player is walking
    over is mostly a hole. A threshold would have let a later edit tune
    this back down to merely torn without anything failing, so it is
    compared with the whole run instead.
    """
    tilemap = _tilemap()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (WIDTH, HEIGHT)
    assert tileset_for(MAP_NAME) is COLLIDED

    here = _sea_share(MAP_NAME)
    behind = [_sea_share(name) for name in EARLIER]
    assert here > 0.5, here
    assert here > max(behind) * 5, (here, max(behind))

    # ...and it is the same Sea the game has used since the pantry, so
    # walking into it does what walking into it has always done.
    assert "V" in collision.FALL_HAZARD_TERRAIN

    # Very little of the map can be stood on, and less of it can be
    # reached. That gap is the marooned islands.
    standable = sum(
        1 for y in range(HEIGHT) for x in range(WIDTH)
        if not tilemap.is_solid(x, y)
        and tilemap.terrain_at(x, y) not in collision.FALL_HAZARD_TERRAIN
    )
    reachable = _reachable()
    assert standable / (WIDTH * HEIGHT) < 0.35, standable
    assert len(reachable) < standable, "nothing was left off the route"


def test_the_ledges_are_ledges() -> None:
    """Two tiles wide out over the Sea, everywhere they are over it.

    The whole difficulty of this map is that there is nowhere to step
    aside to. A causeway that quietly widens to four is a road with a
    view, and it would take the map's only idea away without anything
    else changing -- so every stretch of every one of them that is not
    standing on an island is measured across.
    """
    tilemap = _tilemap()
    reachable = _reachable()
    # Out over the Sea, rather than merely off an island: a tile at a
    # landing has island on seven sides of it and is not a ledge in any
    # sense a player would recognise.
    ledges = [
        (x, y) for (x, y) in reachable
        if RIM < x < WIDTH - RIM
        and all(
            island_at(x + dx, y + dy) is None
            for dx in (-1, 0, 1) for dy in (-1, 0, 1)
        )
    ]
    assert len(ledges) > 40, len(ledges)

    # Measured as "how much Sea is beside it" rather than as a run
    # along an axis. The causeways are diagonal as often as not, and a
    # two-wide diagonal is a staircase whose horizontal run is three --
    # so counting along x and y calls a perfectly good ledge four wide
    # and would have had the map widened to satisfy the test.
    #
    # What being on a ledge actually means is that there is nowhere to
    # step aside to, and that is exactly this: every tile of one has
    # open Sea within a step of it.
    for x, y in ledges:
        sea = sum(
            1 for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            if (dx, dy) != (0, 0)
            and (0 <= x + dx < WIDTH and 0 <= y + dy < HEIGHT)
            and (x + dx, y + dy) not in reachable
        )
        assert sea >= 2, (x, y, sea)


def test_two_islands_are_only_ever_looked_at() -> None:
    """A property the map has to keep failing to provide.

    The phase document asks for walls and towers visible through
    Astral Sea sections. Taken at its word, that means somewhere Chuck
    can see and cannot reach -- and the natural drift of any later edit
    is to join it up, because an island with no bridge looks like an
    oversight rather than the point.
    """
    reachable = _reachable()
    for index in range(len(ISLANDS)):
        on_it = {
            (x, y) for y in range(HEIGHT) for x in range(WIDTH)
            if island_at(x, y) == index
        }
        assert on_it, index
        touched = on_it & reachable
        if index in MAROONED:
            assert not touched, (index, ISLANDS[index][4], len(touched))
        else:
            assert len(touched) > 8, (index, ISLANDS[index][4], len(touched))

    # ...and they are worth looking at: two different worlds, neither
    # of them the one the player is standing on when they see it.
    marooned_worlds = {ISLANDS[index][4] for index in MAROONED}
    assert len(marooned_worlds) == len(MAROONED), marooned_worlds

    # No causeway names them. This is the thing that actually keeps
    # them marooned, so it is asserted rather than inferred.
    joined = {index for pair in CAUSEWAYS for index in pair}
    assert not joined & set(MAROONED), joined & set(MAROONED)


def test_the_far_shore_can_be_walked_to() -> None:
    """The route, over every ledge in the chain.

    Guaranteed by construction rather than found: the causeways are
    authored and the islands they join are authored, so what this
    checks is that the two agree once the map has been drawn and
    frayed on top of them.
    """
    reachable = _reachable()
    far = {
        (x, y) for y in range(HEIGHT) for x in range(WIDTH)
        if island_at(x, y) == FAR_SHORE
    }
    assert far & reachable, "the far shore is cut off"

    # Every island on the chain, in order, so a broken link says which.
    chain = [0]
    for a, b in CAUSEWAYS:
        if a in chain and b not in chain:
            chain.append(b)
    for index in chain:
        on_it = {
            (x, y) for y in range(HEIGHT) for x in range(WIDTH)
            if island_at(x, y) == index
        }
        assert on_it & reachable, (index, ISLANDS[index][4])

    ts = config.TILE_SIZE
    anchor = CHECKPOINT_BY_ID[f"{MAP_NAME}_anchor"]
    assert anchor.position is not None
    assert (int(anchor.position[0]) // ts,
            int(anchor.position[1]) // ts) in reachable
    assert anchor.saveable


def test_each_island_keeps_its_own_enemy_and_none_at_a_landing() -> None:
    """The remix again, on ground with nothing behind it.

    Fewer of them than the map before, on purpose: there the danger
    was how many there were, here it is that there is nowhere to back
    away to. Which makes the placement rule the load-bearing part --
    an enemy standing where a ledge lands is not an encounter, it is a
    two-tile bridge with something on the end of it.
    """
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    reachable = _reachable()
    ledges = {(x, y) for (x, y) in reachable if island_at(x, y) is None}

    seen: dict[str, int] = {}
    for kind, position in tilemap.object_spawns:
        if kind.startswith(("arrival:", "anchor:")):
            continue
        cell = (int(position[0]) // ts, int(position[1]) // ts)
        seen[kind] = seen.get(kind, 0) + 1
        island = island_at(*cell)
        assert island is not None, (kind, cell, "standing on a ledge")
        expected = {
            index for index, marker, _ in GARRISON
            if MARKER_DEFS[marker].kind == kind
        }
        assert island in expected, (kind, cell, island, expected)
        assert all(abs(lx - cell[0]) + abs(ly - cell[1]) >= CLEARANCE
                   for lx, ly in ledges), (kind, cell)

    for index, marker, wanted in GARRISON:
        kind = MARKER_DEFS[marker].kind
        assert seen.get(kind, 0) >= wanted, (kind, seen.get(kind, 0))
    assert len(seen) >= 4, sorted(seen)


def test_the_road_east_reaches_it_and_comes_back() -> None:
    assert AREA_WALK_EXITS[(BEHIND, "⮞")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].destination == BEHIND
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[BEHIND], "one theme, still"

    ts = config.TILE_SIZE
    directory, game, world = _world(BEHIND)
    try:
        world.player.x = (world.tilemap.width_tiles - 1) * ts + 2
        world.player.y = (world.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            world.update(1 / 60)
        here = game.scenes.current
        assert here.map_name == MAP_NAME
        here._arrival_fade_t = None
        here.player.x = 2.0
        here.player.y = MID_Y * ts + 2
        for _ in range(4):
            here.update(1 / 60)
        assert game.scenes.current.map_name == BEHIND
    finally:
        game._shutdown()
        directory.cleanup()

    for entry in (MAP_NAME, f"{MAP_NAME}_anchor", "desert_east_7_from_east_8"):
        assert CHECKPOINT_BY_ID[entry].required_flags == DESERT_ENTRY_FLAGS

    # The east edge is rim: the trio is next and this map should not
    # have to change shape when it arrives.
    tilemap = _tilemap()
    for y in range(HEIGHT):
        assert tilemap.terrain_at(WIDTH - 1, y) == "#", y
    west = [y for y in range(HEIGHT) if not tilemap.is_solid(0, y)]
    assert len(west) == GAP, west


def test_it_renders_as_islands_in_the_sea() -> None:
    """Drawn at four places on it, and the four are all different.

    This began as a brightness test and then as a colour-variety one,
    and neither survives the map it is testing: half these islands are
    dark -- jungle, basalt, the Feywild at night -- so brightness
    cannot tell them from the Sea, and the Sea is drawn with a
    starfield in it, so it has more colours on screen than a courtyard
    does. What is left that is both true and worth asserting is that
    the map draws differently everywhere, which is what a missing
    tileset row would take away: an unpainted world comes out as one
    flat colour wherever you stand in it.
    """
    directory, game, world = _world()
    try:
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        ts = config.TILE_SIZE
        for _ in range(2):
            world.update(0.05)
        frames = []
        for cx, cy in ((25, 25), (55, 29), (71, 45), (46, 6)):
            # The camera is moved after the update, not before it: the
            # update follows the player, so a camera set first is a
            # camera put straight back where it was.
            world.camera.x = cx * ts - config.NATIVE_WIDTH // 2
            world.camera.y = cy * ts - config.NATIVE_HEIGHT // 2
            world.draw(surface)
            frames.append(tuple(
                surface.get_at((x, y))[:3]
                for x in range(0, config.NATIVE_WIDTH, 11)
                for y in range(0, config.NATIVE_HEIGHT, 9)
            ))
        assert len(set(frames)) == len(frames), "two places look identical"
        for frame in frames:
            assert len(set(frame)) > 5, len(set(frame))

        assert world.snow is not None, "the frozen island brought no weather"
        assert world.props, "nothing is standing on any of it"
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
    print("All east-8 tests passed.")


if __name__ == "__main__":
    _run_all()
