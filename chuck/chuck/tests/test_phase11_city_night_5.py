"""Phase 11 City Night 5 and its staged multi-lane highway crossing."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.pedestrian import PedestrianNPC
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_night_5"
OFFICE = frozenset("#▱▤▥w")


def _markers(tilemap):
    result = {}
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)
        ))
    return result


def _reachable(tilemap, start):
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in found or tilemap.is_solid(*point):
                continue
            if tilemap.terrain_at(*point) == "V":
                continue
            found.add(point)
            queue.append(point)
    return found


def _office_components(tilemap):
    remaining = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) in OFFICE
    }
    components = []
    while remaining:
        component = {remaining.pop()}
        queue = list(component)
        while queue:
            col, row = queue.pop()
            for point in ((col - 1, row), (col + 1, row),
                          (col, row - 1), (col, row + 1)):
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    queue.append(point)
        components.append(component)
    return components


def _game_and_world(checkpoint="modern_city_5"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_city_night_5_is_a_large_staged_highway_map() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert (tilemap.width_tiles, tilemap.height_tiles) == (112, 48)
    assert MAP_TILESET[MAP_NAME] == "city"
    assert kinds["arrival:from_city_night_4"] == 1
    assert kinds["anchor:modern_city_5_anchor"] == 1
    assert kinds["boundary:modern_city_night_4"] == 1
    assert kinds["npc:businessman"] == 2
    assert kinds["patrol_npc:businessman:h"] == 1
    assert kinds["npc:homeless_man"] == 0
    assert kinds["raccoon"] == 1
    assert kinds["cigarette"] == 5
    assert sum(
        count for kind, count in kinds.items()
        if kind.startswith("traffic_lane:")
    ) == 8
    assert not any(kind == "boundary:modern_city_night_6" for kind in kinds)

    components = _office_components(tilemap)
    assert len(components) == 4
    for component in components:
        cols = [point[0] for point in component]
        rows = [point[1] for point in component]
        assert max(cols) - min(cols) + 1 >= 24
        assert max(rows) - min(rows) + 1 >= 18


def test_highway_has_two_carriageways_crosswalks_and_safe_median() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    road_columns = (
        set(range(35, 51)) | set(range(61, 77))
    )
    for row in (22, 24, 26):
        assert all(tilemap.terrain_at(col, row) == "▦"
                   for col in road_columns)
    for row in range(tilemap.height_tiles):
        assert all(tilemap.terrain_at(col, row) not in {"=", "▦"}
                   for col in range(52, 60))

    markers = _markers(tilemap)
    lane_columns = sorted(
        point[0]
        for kind, points in markers.items()
        if kind.startswith("traffic_lane:")
        for point in points
    )
    assert lane_columns == [37, 41, 45, 49, 63, 67, 71, 75]


def test_every_authored_discovery_is_reachable_without_astral_fall() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    reached = _reachable(tilemap, markers["arrival:from_city_night_4"][0])
    required = {
        markers["anchor:modern_city_5_anchor"][0],
        markers["boundary:modern_city_night_4"][0],
        *markers["npc:businessman"],
        *markers["patrol_npc:businessman:h"],
        *markers["raccoon"],
        *markers["cigarette"],
    }
    assert required <= reached
    exits = {
        terrain: exit_def
        for (source, terrain), exit_def in AREA_WALK_EXITS.items()
        if source == MAP_NAME
    }
    assert len(exits) == 1
    only_exit = next(iter(exits.values()))
    assert (only_exit.destination, only_exit.arrival) == (
        "modern_city_night_4", "from_city_night_5"
    )


def test_city_4_and_5_visual_openings_match_named_arrivals() -> None:
    map_4 = TileMap(config.MAPS_DIR / "modern_city_night_4.txt")
    map_5 = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers_4 = _markers(map_4)
    markers_5 = _markers(map_5)
    assert markers_4["boundary:modern_city_night_5"] == [(0, 36)]
    assert markers_4["arrival:from_city_night_5"] == [(4, 36)]
    assert markers_5["boundary:modern_city_night_4"] == [(111, 24)]
    assert markers_5["arrival:from_city_night_4"] == [(107, 24)]
    outbound = next(
        exit_def for (source, _), exit_def in AREA_WALK_EXITS.items()
        if source == "modern_city_night_4"
        and exit_def.destination == MAP_NAME
    )
    assert outbound.arrival == "from_city_night_4"


def test_city_night_5_checkpoint_world_and_respawn_use_shared_systems() -> None:
    entry = CHECKPOINT_BY_ID["modern_city_5"]
    anchor = CHECKPOINT_BY_ID["modern_city_5_anchor"]
    assert (entry.display_name, entry.map_name, entry.arrival) == (
        "City Night 5", MAP_NAME, "from_city_night_4"
    )
    assert anchor.position == (1668.0, 389.0)
    assert anchor.saveable

    directory, game, world = _game_and_world("modern_city_5_anchor")
    try:
        assert world.city_rain is not None
        assert len(world.npcs) == 3
        assert all(npc.npc_id == "businessman" for npc in world.npcs)
        assert sum(isinstance(npc, PedestrianNPC)
                   for npc in world.npcs) == 1
        assert len(world.raccoons) == 1
        assert len(world.traffic_lanes) == 8
        assert {lane.direction for lane in world.traffic_lanes} == {
            "up", "down"
        }
        assert sum(len(lane.vehicles) for lane in world.traffic_lanes) == 32
        initial_centers = [
            [vehicle.center for vehicle in lane.vehicles]
            for lane in world.traffic_lanes
        ]
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        world._arrival_fade_t = None
        world.traffic_lanes[0].update(0.25)
        world.raccoons[0].on_scratched()
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert world._respawn_phase == "in"
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
        assert [
            [vehicle.center for vehicle in lane.vehicles]
            for lane in world.traffic_lanes
        ] == initial_centers
        assert len(world.raccoons) == 1
        assert world.raccoons[0].scratches_remaining == (
            config.RACCOON_SCRATCHES
        )
    finally:
        game._shutdown()
        directory.cleanup()
