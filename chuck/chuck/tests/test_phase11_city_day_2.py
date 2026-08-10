"""Phase 11 City Day 2: the crossroads, and the damage spreading.

City Day 1 was one broad avenue with a plaza off it. This map is the
other thing a city is: a junction, with traffic running on both streets,
so a crossing has to be timed twice rather than once.

The phase document asks for Astral blocks to grow more common through
the daytime progression, so one of these tests compares this map's
damage against City Day 1's rather than just counting it.
"""

from collections import Counter, deque
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
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_day_2"
DAY_1 = "modern_city_day_1"


def _markers(tilemap):
    result = {}
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)
        ))
    return result


def _flood(tilemap, start):
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
            if point in found or tilemap.is_solid(x, y):
                continue
            if tilemap.terrain_at(x, y) == "V":
                continue
            found.add(point)
            queue.append(point)
    return found


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_the_crossroads_carries_traffic_on_both_streets() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (76, 58)
    assert MAP_TILESET[MAP_NAME] == "city_day"
    assert tileset_for(MAP_NAME).sheet == "city_day.png"

    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    horizontal = sum(count for kind, count in kinds.items()
                     if kind.startswith(("traffic_lane:left",
                                         "traffic_lane:right")))
    vertical = sum(count for kind, count in kinds.items()
                   if kind.startswith(("traffic_lane:up",
                                       "traffic_lane:down")))
    assert horizontal >= 4 and vertical >= 4, (horizontal, vertical)

    # City Day 1 has no traffic at all, so this really is a new kind of
    # space rather than the same street drawn again.
    day_one = TileMap(config.MAPS_DIR / f"{DAY_1}.txt")
    assert not any(kind.startswith("traffic_lane:")
                   for kind, _ in day_one.object_spawns)

    directory, game, world = _game_and_world()
    try:
        assert len(world.traffic_lanes) == horizontal + vertical
        assert world.traffic_vehicles
        # Cars actually move, on both axes.
        before = [(car.x, car.y) for car in world.traffic_vehicles]
        for _ in range(10):
            world.update(0.05)
        after = [(car.x, car.y) for car in world.traffic_vehicles]
        assert any(a[0] != b[0] for a, b in zip(before, after))
        assert any(a[1] != b[1] for a, b in zip(before, after))
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_damage_is_spreading_through_the_daytime_city() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    day_one = TileMap(config.MAPS_DIR / f"{DAY_1}.txt")

    here = sum(row.count("V") for row in tilemap._grid)
    before = sum(row.count("V") for row in day_one._grid)
    assert here > before, (here, before)

    # A whole quarter of the junction is gone, and the streets that
    # served it end in it rather than at an invisible wall.
    assert all(tilemap.terrain_at(col, row) == "V"
               for row in range(0, 26) for col in range(0, 30))

    markers = _markers(tilemap)
    reachable = _flood(tilemap, markers["arrival:from_city_day_1"][0])
    assert markers["anchor:modern_city_day_2_anchor"][0] in reachable
    assert markers["boundary:modern_city_day_3"][0] in reachable
    assert markers["boundary:modern_city_day_1"][0] in reachable

    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["cigarette"] == 4
    # The daytime cast: businesspeople only, and the red dress stays on
    # City Day 1 so she reads as that street's landmark.
    assert not any(kind.endswith("homeless_man") for kind in kinds)
    assert not any("red_dress" in kind for kind in kinds)


def test_city_day_1_and_2_connect_both_ways() -> None:
    onward = AREA_WALK_EXITS[(DAY_1, "⮞")]
    assert (onward.destination, onward.arrival) == (
        MAP_NAME, "from_city_day_1")
    back = AREA_WALK_EXITS[(MAP_NAME, "⮜")]
    assert (back.destination, back.arrival) == (DAY_1, "from_city_day_2")

    entry = CHECKPOINT_BY_ID[MAP_NAME]
    assert (entry.display_name, entry.map_name) == ("City Day 2", MAP_NAME)
    assert entry.runtime_entry
    assert CHECKPOINT_BY_ID["modern_city_day_2_anchor"].saveable

    directory, game, world = _game_and_world(DAY_1)
    try:
        world._arrival_fade_t = None
        east = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮞"
        )
        world.player.x = east[0] * config.TILE_SIZE
        world.player.y = east[1] * config.TILE_SIZE + 4
        world.update(0.0)
        assert world.map_name == MAP_NAME
        assert game.active_checkpoint_id == MAP_NAME
        world.update(0.0)
        assert world.map_name == MAP_NAME  # no bounce

        west = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮜"
        )
        world.player.x = west[0] * config.TILE_SIZE
        world.player.y = west[1] * config.TILE_SIZE + 4
        world.update(0.0)
        assert world.map_name == DAY_1
        assert game.active_checkpoint_id == "modern_city_day_1_return"
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_crossroads_rains_and_respawns_at_its_own_ashtray() -> None:
    directory, game, world = _game_and_world("modern_city_day_2_anchor")
    try:
        assert world.city_rain is not None
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        world._arrival_fade_t = None
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
        # Respawning never lands Chuck in a lane.
        tile = (int(world.player.x // config.TILE_SIZE),
                int(world.player.y // config.TILE_SIZE))
        assert world.tilemap.terrain_at(*tile) not in {"=", "≡", "‖"}
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
    print("All City Day 2 tests passed.")


if __name__ == "__main__":
    _run_all()
