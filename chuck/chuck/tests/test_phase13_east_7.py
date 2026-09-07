"""Phase 13's seventh map east: nine worlds, and no ground of its own.

Every map before this one is the desert with something in it. The phase
document asks for the later maps to be heavily fragmented and
geographically impossible, and the properties that phrase actually
means are testable ones, so they are tested rather than eyeballed.

*Heavily fragmented* is measured as the absence of a majority. A map
that is two-thirds desert with a big piece of Chult on it satisfies
"has fragments" and fails the document, so what is asserted is that no
world owns a third of the map and that most of the worlds are here.

*Geographically impossible* is measured as adjacency. It is not enough
for the worlds to be present; they have to be touching each other in
combinations that could not exist -- snow against a ship's deck, a
courtyard against Hell -- and the same world has to turn up in two
places that are nowhere near one another.

And the one thing a map like this can quietly lose is the way through.
Every border on it is torn open, so the route is guaranteed by
construction: a corridor is walked before anything is torn and
protected from tearing afterwards. The test walks it.
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
from generate_desert_east_7 import (  # noqa: E402
    CLEARANCE, GAP, GARRISON, HEIGHT, MID_Y, PATH, RIM, SITES, WIDTH,
    WORLDS, site_at,
)


MAP_NAME = "desert_east_7"
BEHIND = "desert_east_6"

# Pairs that cannot share a border anywhere in the real world, or in
# this game's fiction either. Some of them have to be touching here.
IMPOSSIBLE = (
    ("snow", "ship"), ("snow", "hell"), ("ship", "hell"),
    ("courtyard", "hell"), ("courtyard", "chult"), ("city", "snow"),
    ("ship", "chult"), ("feywild", "hell"), ("city", "hell"),
    ("courtyard", "snow"), ("ship", "feywild"), ("city", "chult"),
)


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


def _corridor_cells() -> list[tuple[int, int]]:
    """The middle line of the authored way through, in order."""
    cells: list[tuple[int, int]] = []
    for index in range(len(PATH) - 1):
        (x0, y0), (x1, y1) = PATH[index], PATH[index + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for step in range(steps + 1):
            along = step / max(1, steps)
            cells.append((round(x0 + (x1 - x0) * along),
                          round(y0 + (y1 - y0) * along)))
    return cells


def test_no_world_owns_this_map() -> None:
    """Heavily fragmented, measured as the absence of a majority.

    A map that is two-thirds desert with one big piece of Chult on it
    has fragments and is not what the phase document is asking for. So
    the assertion is about the largest share rather than about the
    number of worlds: nobody gets a third of it, and almost everywhere
    Chuck has been is here.
    """
    tilemap = _tilemap()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (WIDTH, HEIGHT)
    assert tileset_for(MAP_NAME) is COLLIDED

    share: dict[str, int] = {}
    for y in range(RIM, HEIGHT - RIM):
        for x in range(RIM, WIDTH - RIM):
            world = SITES[site_at(x, y)][2]
            share[world] = share.get(world, 0) + 1
    total = sum(share.values())
    assert len(share) >= 7, sorted(share)
    assert max(share.values()) / total < 0.30, {
        k: round(v / total, 3) for k, v in share.items()
    }
    # ...and none of them is a token presence either. A world with
    # twenty tiles is a scrap, and this map is supposed to be made of
    # pieces rather than of one place with souvenirs on it.
    assert min(share.values()) / total > 0.04, {
        k: round(v / total, 3) for k, v in share.items()
    }
    assert set(share) <= set(WORLDS), set(share) - set(WORLDS)


def test_it_could_not_be_anywhere() -> None:
    """Impossible, measured as adjacency rather than as presence.

    Nine worlds laid out in a line, each meeting only its neighbours,
    would be a strange journey through somewhere. What makes this a
    place that cannot exist is which things are touching: the same
    world in two corners that never meet, and borders between worlds
    that have no business sharing one.
    """
    # The same world, twice, and nowhere near itself.
    repeats = {}
    for x, y, world in SITES:
        repeats.setdefault(world, []).append((x, y))
    split = {
        world: points for world, points in repeats.items() if len(points) > 1
    }
    assert split, "every world is in exactly one piece"
    for world, points in split.items():
        spread = max(
            abs(a[0] - b[0]) + abs(a[1] - b[1])
            for a in points for b in points
        )
        assert spread > WIDTH // 2, (world, spread)

    # ...and the borders themselves.
    touching = set()
    for y in range(RIM, HEIGHT - RIM):
        for x in range(RIM, WIDTH - RIM):
            here = SITES[site_at(x, y)][2]
            for dx, dy in ((1, 0), (0, 1)):
                nx, ny = x + dx, y + dy
                if not (nx < WIDTH - RIM and ny < HEIGHT - RIM):
                    continue
                there = SITES[site_at(nx, ny)][2]
                if there != here:
                    touching.add(frozenset((here, there)))
    assert len(touching) >= 8, sorted(tuple(sorted(p)) for p in touching)
    impossible = [
        pair for pair in IMPOSSIBLE if frozenset(pair) in touching
    ]
    assert len(impossible) >= 3, impossible


def test_the_borders_are_torn_and_torn_in_stretches() -> None:
    """The Astral Sea, doing here what it does on every map east.

    On the earlier maps it frays the seam between a fragment and the
    sand. There is no sand here to fray against, so it frays between
    the worlds -- and in stretches, for the same reason as before: a
    border sampled evenly comes out as a dashed line, which reads as
    somebody having drawn round each piece.
    """
    tilemap = _tilemap()
    astral = {
        (x, y) for y in range(HEIGHT) for x in range(WIDTH)
        if tilemap.terrain_at(x, y) == "V"
    }
    assert len(astral) > 150, len(astral)
    assert "V" in collision.FALL_HAZARD_TERRAIN

    joined = sum(
        1 for x, y in astral
        if any((x + dx, y + dy) in astral
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    )
    assert joined > len(astral) * 0.7, (joined, len(astral))

    # It really is the borders that are torn, not the middles: nearly
    # every torn tile has two different worlds within a step of it.
    on_seam = 0
    for x, y in astral:
        worlds = {
            SITES[site_at(x + dx, y + dy)][2]
            for dx in (-1, 0, 1) for dy in (-1, 0, 1)
            if 0 <= x + dx < WIDTH and 0 <= y + dy < HEIGHT
        }
        on_seam += 1 if len(worlds) > 1 else 0
    assert on_seam > len(astral) * 0.6, (on_seam, len(astral))


def test_the_way_through_is_guaranteed_rather_than_found() -> None:
    """Walked, on a map where every border is a hole.

    The corridor is carved before the tearing and protected from it
    afterwards, which is the only way a route survives an edit to any
    of the nine cells. This walks the whole of it and then floods from
    the arrival to prove the two agree.
    """
    tilemap = _tilemap()
    for x, y in _corridor_cells():
        assert not tilemap.is_solid(x, y), (x, y)
        assert tilemap.terrain_at(x, y) not in collision.FALL_HAZARD_TERRAIN, \
            (x, y)

    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k == "arrival:from_east_6")
    seen = _safe_flood(tilemap, (int(arrival[0]) // ts, int(arrival[1]) // ts))
    for cell in _corridor_cells():
        assert cell in seen, cell
    assert (WIDTH - RIM - 1, MID_Y) in seen, "the east end is cut off"

    # The Ashtray is on it, because this is the map you will die on.
    anchor = CHECKPOINT_BY_ID["desert_east_7_anchor"]
    assert anchor.position is not None
    assert (int(anchor.position[0]) // ts,
            int(anchor.position[1]) // ts) in seen

    # ...and the map is still mostly closed: a corridor through a map
    # that is open everywhere is not a corridor.
    assert len(seen) < WIDTH * HEIGHT * 0.85, len(seen)


def test_six_kinds_of_enemy_each_standing_where_it_belongs() -> None:
    """The document's final remix: familiar systems, new combination.

    Nothing here is new. Every one of these is an enemy the player has
    met in the region it came from, and the only thing this map does is
    put all of them on one screen's walk -- which is exactly what the
    document asks for and exactly what no earlier map does.

    Each is checked against the ground it is standing on, so a snake in
    the snow fails here rather than looking merely odd.
    """
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    corridor = set(_corridor_cells())

    kinds: dict[str, int] = {}
    for kind, position in tilemap.object_spawns:
        if kind.startswith(("arrival:", "anchor:")):
            continue
        cell = (int(position[0]) // ts, int(position[1]) // ts)
        kinds[kind] = kinds.get(kind, 0) + 1
        # In its own world.
        world = SITES[site_at(*cell)][2]
        expected = {
            marker_world for marker_world, marker, _ in GARRISON
            if MARKER_DEFS[marker].kind == kind
        }
        assert world in expected, (kind, cell, world, expected)
        # ...and never in the doorway. An enemy standing in the only
        # way through is a toll, and this map has too many of them for
        # that to be survivable.
        assert all(abs(cx - cell[0]) + abs(cy - cell[1]) >= CLEARANCE
                   for cx, cy in corridor), (kind, cell)

    assert len(kinds) >= 5, sorted(kinds)
    for world, marker, wanted in GARRISON:
        kind = MARKER_DEFS[marker].kind
        assert kinds.get(kind, 0) >= wanted, (kind, kinds.get(kind, 0))
        # The marker paints its own world's floor beneath it.
        assert MARKER_DEFS[marker].under == WORLDS[world][0], marker

    directory, game, world = _world()
    try:
        alive = (len(world.snakes) + len(world.redcaps)
                 + len(world.spined_devils) + len(world.undead))
        assert alive >= sum(count for _, _, count in GARRISON), alive
        assert {u.kind for u in world.undead} == {"knight", "skeleton", "orc"}
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_road_east_reaches_it_and_comes_back() -> None:
    """Both directions, walked for real.

    The sixth map's east gap was cut as open sand while there was
    nothing behind it. This is where it becomes a door, so the half
    that matters is that the gap became one without the map being
    reshaped around it.
    """
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

    for entry in (MAP_NAME, f"{MAP_NAME}_anchor", "desert_east_6_from_east_7"):
        assert CHECKPOINT_BY_ID[entry].required_flags == DESERT_ENTRY_FLAGS
    assert CHECKPOINT_BY_ID[f"{MAP_NAME}_anchor"].saveable
    assert CHECKPOINT_BY_ID[MAP_NAME].development_visible


def test_the_gap_east_became_a_door_without_the_map_moving() -> None:
    """The rule the hub set, held to seven maps later.

    This map's east edge was cut as rim while there was nothing behind
    it, and the corridor was walked to it anyway. Adding the eighth map
    should therefore have added a marker and a gap and changed nothing
    else -- so what is checked is that the two doors match each other
    exactly, and that the way through still arrives at the new one
    rather than having been bent toward it.
    """
    tilemap = _tilemap()

    def gap(cells) -> list[int]:
        return [index for index, cell in enumerate(cells)
                if not tilemap.is_solid(*cell)]

    west = gap([(0, y) for y in range(HEIGHT)])
    east = gap([(WIDTH - 1, y) for y in range(HEIGHT)])
    assert west == east, (west, east)
    assert len(east) == GAP, east
    # Same distance from the middle of the side, both of them.
    assert abs((east[0] + east[-1]) / 2 - (HEIGHT - 1) / 2) <= 0.5, east

    # The corridor was already running to it: its last tile is inside
    # the gap it now leads through.
    assert (WIDTH - RIM - 1, MID_Y) in _corridor_cells()
    assert MID_Y in east


def test_the_map_renders_as_a_patchwork() -> None:
    """Drawn, and checked for the thing that would be wrong.

    Nine worlds on one screen means nine palettes, and the failure this
    is guarding against is a fragment whose tileset row was never
    added: it would draw as flat placeholder colour and look, at a
    glance, like terrain.
    """
    directory, game, world = _world()
    try:
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        ts = config.TILE_SIZE
        seen_colours = set()
        for cx, cy in ((20, 12), (44, 32), (70, 20), (30, 52)):
            world.camera.x = cx * ts - config.NATIVE_WIDTH // 2
            world.camera.y = cy * ts - config.NATIVE_HEIGHT // 2
            for _ in range(2):
                world.update(0.05)
            world.draw(surface)
            seen_colours |= {
                surface.get_at((x, y))[:3]
                for x in range(0, config.NATIVE_WIDTH, 11)
                for y in range(0, config.NATIVE_HEIGHT, 9)
            }
        # Four screens of nine worlds is a lot of different colour.
        assert len(seen_colours) > 60, len(seen_colours)
        assert world.snow is not None, "the frozen cell brought no weather"
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
    print("All east-7 tests passed.")


if __name__ == "__main__":
    _run_all()
