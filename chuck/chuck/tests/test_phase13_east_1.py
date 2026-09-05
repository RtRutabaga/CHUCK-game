"""Phase 13's eastern route: the first map, and the collided sheet.

Two things are being established here that the rest of the traversal
will be built on, and both are worth pinning now while there is one
fragment rather than ten.

The first is that a fragment of another world is *that world*. The
collided sheet's rows are rendered by the same functions that render
the sheets they came from, and the test compares the finished pixels --
because the failure mode is not a crash, it is a lookalike drifting a
shade at a time until a piece of the modern city is just a grey road
and the player no longer recognises what they are standing on.

The second is escalation. This map has to be almost entirely desert,
because the phase document says the first eastern transition must not
be dramatically different and the mash-up must build as Chuck goes. So
the intrusion is measured as a fraction of the map, which gives every
later map in the sequence something to be measured against.
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
from src.world.tilemap import TileMap
from src.world.tileset_layout import (
    CITY, COLLIDED, DESERT, TILE_PX, tileset_for,
)
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_desert_east_1 import (  # noqa: E402
    GAP, HEIGHT, RIM, ROAD_Y, TEAR_X, WIDTH,
)


MAP_NAME = "desert_east_1"
HUB = "desert_central"
ROAD = ("=", "≡")
DESERT_GROUND = (".", ",", "⟁", "#", "⌗", "⌖", "⍟")


def _tilemap(name: str = MAP_NAME) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _world(checkpoint: str = "desert_east_1"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _flood(tilemap: TileMap, origin, extra_solid=()) -> set[tuple[int, int]]:
    """Everywhere Chuck can walk to without falling out of the world."""
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


def _row_pixels(sheet, tileset, name) -> list:
    index = [n for n, _, _ in tileset.order].index(name)
    variants, frames = tileset.info()[name]
    return [
        sheet.get_at((x, index * TILE_PX + y))[:3]
        for y in range(TILE_PX)
        for x in range(variants * frames * TILE_PX)
    ]


def test_a_fragment_of_a_world_is_drawn_as_that_world() -> None:
    """Pixel for pixel, not merely in spirit.

    Both the count of variants and the art itself: a row rendered with
    fewer variants would be the same drawing shown differently, which
    fools the eye in exactly the way this is meant to prevent.
    """
    pygame.init()
    sheets = {
        "city": pygame.image.load(
            str(config.ASSETS_DIR / "tilesets" / CITY.sheet)),
        "desert": pygame.image.load(
            str(config.ASSETS_DIR / "tilesets" / DESERT.sheet)),
        "collided": pygame.image.load(
            str(config.ASSETS_DIR / "tilesets" / COLLIDED.sheet)),
    }
    sources = {
        "sand": DESERT, "sand_ripple": DESERT, "dune": DESERT,
        "desert_rock": DESERT, "ruin_stone": DESERT, "ruin_floor": DESERT,
        "desert_scrub": DESERT, "astral_void": DESERT,
        "city_road": CITY, "city_road_line_h": CITY,
    }
    assert {name for name, _, _ in COLLIDED.order} == set(sources)

    for name, source in sources.items():
        assert COLLIDED.info()[name] == source.info()[name], name
        sheet = sheets["city"] if source is CITY else sheets["desert"]
        assert _row_pixels(sheets["collided"], COLLIDED, name) == \
            _row_pixels(sheet, source, name), name

    # The road is reached by the same characters that draw a road in the
    # city, so a map author cannot accidentally author a different one.
    assert COLLIDED.char_to_terrain["="] == CITY.char_to_terrain["="]
    assert COLLIDED.char_to_terrain["≡"] == CITY.char_to_terrain["≡"]


def test_the_first_map_east_is_still_a_desert() -> None:
    """Escalation starts from almost nothing.

    The phase document forbids making the first eastern transition
    dramatically different. Held as a proportion so that later maps in
    the sequence have a number to exceed.
    """
    tilemap = _tilemap()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (WIDTH, HEIGHT)
    assert tileset_for(MAP_NAME) is COLLIDED

    counts: dict[str, int] = {}
    for y in range(HEIGHT):
        for x in range(WIDTH):
            char = tilemap.terrain_at(x, y)
            counts[char] = counts.get(char, 0) + 1
    total = WIDTH * HEIGHT
    desert = sum(counts.get(c, 0) for c in DESERT_GROUND)
    intrusion = sum(counts.get(c, 0) for c in ROAD)

    assert desert / total > 0.80, desert / total
    assert 0.01 < intrusion / total < 0.05, intrusion / total
    # Exactly one intruding world so far, and it is the modern city.
    foreign = set(counts) - set(DESERT_GROUND) - {"V", "⮜"}
    assert foreign == set(ROAD), foreign


def test_the_road_is_the_only_way_over_the_tear() -> None:
    """The fragment is a crossing, not an ornament beside one.

    Proved by taking it away: with the asphalt walkable the far half of
    the map is reachable, and with it solid nothing over there is.
    """
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k == "arrival:from_desert_central")
    origin = (int(arrival[0]) // ts, int(arrival[1]) // ts)
    assert origin[0] < TEAR_X, "Chuck should arrive west of the tear"

    with_road = _flood(tilemap, origin)
    without_road = _flood(tilemap, origin, extra_solid=ROAD)
    far_side = [cell for cell in with_road if cell[0] > TEAR_X + 4]
    assert len(far_side) > 500, len(far_side)
    assert not [cell for cell in without_road if cell[0] > TEAR_X + 4]

    # The tear really does run the whole height, rather than being
    # walkable round one end.
    for y in range(RIM, HEIGHT - RIM):
        column = [tilemap.terrain_at(x, y)
                  for x in range(TEAR_X - 5, TEAR_X + 6)]
        assert "V" in column or any(c in ROAD for c in column), y

    # Every tile of road can be stood on, and the lane line runs down
    # the middle of the carriageway the way it does in the city.
    road = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
            if tilemap.terrain_at(x, y) in ROAD]
    assert len(road) > 40
    assert all(cell in with_road for cell in road)
    assert {y for x, y in road if tilemap.terrain_at(x, y) == "≡"} == {ROAD_Y}


def test_the_road_east_is_walked_in_both_directions() -> None:
    assert AREA_WALK_EXITS[(HUB, "⮞")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].destination == HUB
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[HUB], \
        "the region's theme carries past its edge"

    ts = config.TILE_SIZE
    directory, game, world = _world("desert_central_start")
    try:
        world.player.x = (world.tilemap.width_tiles - 1) * ts + 2
        world.player.y = (world.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            world.update(1 / 60)
        east = game.scenes.current
        assert east.map_name == MAP_NAME
        east._arrival_fade_t = None

        east.player.x = 2.0
        east.player.y = (east.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            east.update(1 / 60)
        back = game.scenes.current
        assert back.map_name == HUB
        assert int(back.player.x) // ts >= back.tilemap.width_tiles - RIM - 4
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_hub_still_does_not_say_which_way_is_forward() -> None:
    """All four gaps lead somewhere now, and still look alike.

    This is the point at which the hub could quietly start hinting: the
    east door is the one that matters, and it would be easy for it to
    end up wider, or approached differently, or dressed.
    """
    doors = {char for (name, char) in AREA_WALK_EXITS if name == HUB}
    assert doors == {"⮝", "⮜", "⮟", "⮞"}, doors

    hub = _tilemap(HUB)
    width, height = hub.width_tiles, hub.height_tiles
    runs = {
        "north": [x for x in range(width) if not hub.is_solid(x, 0)],
        "south": [x for x in range(width) if not hub.is_solid(x, height - 1)],
        "west": [y for y in range(height) if not hub.is_solid(0, y)],
        "east": [y for y in range(height) if not hub.is_solid(width - 1, y)],
    }
    for side, cells in runs.items():
        assert len(cells) == GAP, (side, len(cells))
        assert cells == list(range(cells[0], cells[0] + GAP)), side
    # ...and the ground in front of each is the same handful of terrains.
    approach = {
        "north": [(x, y) for x in runs["north"] for y in range(RIM, RIM + 5)],
        "south": [(x, y) for x in runs["south"]
                  for y in range(height - RIM - 5, height - RIM)],
        "west": [(x, y) for y in runs["west"] for x in range(RIM, RIM + 5)],
        "east": [(x, y) for y in runs["east"]
                 for x in range(width - RIM - 5, width - RIM)],
    }
    for side, cells in approach.items():
        kinds = {hub.terrain_at(x, y) for x, y in cells}
        assert kinds <= {".", ",", "⟁"}, (side, sorted(kinds))


def test_the_traversal_has_its_own_entries() -> None:
    for entry in ("desert_east_1", "desert_east_1_anchor",
                  "desert_central_from_east_1"):
        assert CHECKPOINT_BY_ID[entry].required_flags == DESERT_ENTRY_FLAGS
    assert CHECKPOINT_BY_ID["desert_east_1_anchor"].saveable
    # The phase document asks for development access to the collided
    # traversal by name, not only to the initial desert.
    assert CHECKPOINT_BY_ID["desert_east_1"].development_visible

    tilemap = _tilemap()
    ts = config.TILE_SIZE
    anchor = CHECKPOINT_BY_ID["desert_east_1_anchor"].position
    spawn = next(p for k, p in tilemap.object_spawns
                 if k == "anchor:desert_east_1_anchor")
    assert anchor is not None
    assert (int(anchor[0]) // ts, int(anchor[1]) // ts) == \
        (int(spawn[0]) // ts, int(spawn[1]) // ts)
    # It stands before the crossing, so the last save is on the near
    # side of the one hazard on the map.
    assert int(anchor[0]) // ts < TEAR_X


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
    print("All east-1 tests passed.")


if __name__ == "__main__":
    _run_all()
