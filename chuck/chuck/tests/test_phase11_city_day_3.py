"""Phase 11 City Day 3: the street that runs along the open edge.

Day 1 was an avenue, Day 2 a crossroads; this one narrows to a single
street with alleys off it, and the whole east side of the block is gone
-- not its frontages, the buildings themselves.

Both officer types work this street, and the phase document requires
both to stay avoidable, so the test that matters proves a route down it
exists that never enters an Animal Control notice range nor stands in a
police firing lane.
"""

from collections import Counter, deque
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "modern_city_day_3"
DAY_2 = "modern_city_day_2"
LANES = {"police:right": (1, 0), "police:left": (-1, 0),
         "police:up": (0, -1), "police:down": (0, 1)}


def _markers(tilemap):
    result = {}
    ts = config.TILE_SIZE
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((int(x // ts), int(y // ts)))
    return result


def _lane_tiles(tilemap, markers):
    covered = set()
    for kind, step in LANES.items():
        for col, row in markers.get(kind, ()):
            for distance in range(1, 60):
                point = (col + step[0] * distance, row + step[1] * distance)
                if not (0 <= point[0] < tilemap.width_tiles
                        and 0 <= point[1] < tilemap.height_tiles):
                    break
                if tilemap.is_solid(*point):
                    break
                covered.add(point)
    return covered


def _flood(tilemap, start, *, avoid=frozenset()):
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < tilemap.width_tiles
                    and 0 <= y < tilemap.height_tiles):
                continue
            if point in found or tilemap.is_solid(x, y) or point in avoid:
                continue
            if tilemap.terrain_at(x, y) == "V":
                continue
            found.add(point)
            queue.append(point)
    return found


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(checkpoint)
    world._arrival_fade_t = None
    return directory, game, world


def test_the_street_narrows_and_the_damage_grows() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    day_two = TileMap(config.MAPS_DIR / f"{DAY_2}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (58, 64)
    assert MAP_TILESET[MAP_NAME] == "city_day"

    # It runs north-south where Day 2 was a junction, and it is narrower.
    assert tilemap.height_tiles > tilemap.width_tiles
    assert tilemap.width_tiles < day_two.width_tiles

    # The daytime progression: more Astral here than on the map before.
    here = sum(row.count("V") for row in tilemap._grid)
    before = sum(row.count("V") for row in day_two._grid)
    assert here > before, (here, before)
    # Whole buildings are gone, not just frontages: the east edge is open
    # top to bottom.
    assert all(tilemap.terrain_at(tilemap.width_tiles - 1, row) == "V"
               for row in range(tilemap.height_tiles))

    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["cigarette"] == 4
    assert kinds["animal_control"] == 2
    assert sum(count for kind, count in kinds.items()
               if kind.startswith("police:")) == 2
    assert not any(kind.endswith("homeless_man") for kind in kinds)


def test_both_officer_types_can_be_walked_past() -> None:
    """The phase document's requirement, for the net and the gun alike."""
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_city_day_2"][0]
    anchor = markers["anchor:modern_city_day_3_anchor"][0]
    onward = markers["boundary:modern_city_day_4"][0]

    hazard = set(_lane_tiles(tilemap, markers))
    notice = config.UNDEAD_NOTICE_RANGE / config.TILE_SIZE
    for col, row in markers["animal_control"]:
        hazard |= {
            (x, y)
            for y in range(tilemap.height_tiles)
            for x in range(tilemap.width_tiles)
            if math.dist((x, y), (col, row)) <= notice
        }

    reachable = _flood(tilemap, start)
    assert {anchor, onward} <= reachable

    clear = _flood(tilemap, start, avoid=hazard)
    assert onward in clear, "the street cannot be walked safely"
    assert anchor in clear, "the Ashtray sits inside a hazard"
    # ...and no lane fires along the Ashtray or either doorway.
    lanes = _lane_tiles(tilemap, markers)
    assert not ({anchor, start, onward,
                 markers["boundary:modern_city_day_2"][0]} & lanes)


def test_day_2_and_3_connect_both_ways() -> None:
    onward = AREA_WALK_EXITS[(DAY_2, "⮟")]
    assert (onward.destination, onward.arrival) == (
        MAP_NAME, "from_city_day_2")
    back = AREA_WALK_EXITS[(MAP_NAME, "⮝")]
    assert (back.destination, back.arrival) == (DAY_2, "from_city_day_3")
    # The day cue runs on unbroken: this is not a region boundary.
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[DAY_2] == "city_day.wav"

    entry = CHECKPOINT_BY_ID[MAP_NAME]
    assert (entry.display_name, entry.map_name) == ("City Day 3", MAP_NAME)
    assert entry.runtime_entry
    assert CHECKPOINT_BY_ID["modern_city_day_3_anchor"].saveable

    directory, game, world = _game_and_world(DAY_2)
    try:
        south = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮟"
        )
        world.player.x = south[0] * config.TILE_SIZE
        world.player.y = south[1] * config.TILE_SIZE
        world.update(0.0)
        assert world.map_name == MAP_NAME
        assert game.active_checkpoint_id == MAP_NAME
        world.update(0.0)
        assert world.map_name == MAP_NAME  # no bounce

        north = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮝"
        )
        world.player.x = north[0] * config.TILE_SIZE
        world.player.y = north[1] * config.TILE_SIZE
        world.update(0.0)
        assert world.map_name == DAY_2
        assert game.active_checkpoint_id == "modern_city_day_2_return"
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_open_edge_draws_and_respawns_safely() -> None:
    directory, game, world = _game_and_world("modern_city_day_3_anchor")
    try:
        assert world.city_rain is not None
        assert len(world.undead) == 2 and len(world.police) == 2
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
        # Respawning never lands on the road, in a net's reach, or in a lane.
        tile = (int(world.player.x // config.TILE_SIZE),
                int(world.player.y // config.TILE_SIZE))
        assert world.tilemap.terrain_at(*tile) not in {"=", "≡", "‖"}
        notice = config.UNDEAD_NOTICE_RANGE
        for officer in world.undead:
            assert math.dist((officer.x, officer.y),
                             (world.player.x, world.player.y)) > notice
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
    print("All City Day 3 tests passed.")


if __name__ == "__main__":
    _run_all()
