"""Phase 11 City Night 4, the final ordinary block before the highway."""

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


MAP_NAME = "modern_city_night_4"
# The roof volume: field, parapets on three edges, and the vents and
# skylights standing on it. All of it is one solid office mass.
OFFICE = frozenset("#▘▖▗▙▟▱▤▥w")


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


def _game_and_world(checkpoint="modern_city_4"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_city_night_4_is_an_offset_full_scale_city_block() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert (tilemap.width_tiles, tilemap.height_tiles) == (84, 60)
    assert MAP_TILESET[MAP_NAME] == "city"
    assert kinds["arrival:from_city_night_3"] == 1
    assert kinds["boundary:modern_city_night_3"] == 1
    assert kinds["npc:businessman"] == 2
    assert kinds["patrol_npc:businessman:h"] == 1
    assert kinds["npc:homeless_man"] == 0
    assert kinds["raccoon"] == 2
    assert kinds["cigarette"] == 4
    assert kinds["traffic_lane:right:0"] == 1
    assert kinds["traffic_lane:left:1"] == 1
    assert kinds["boundary:modern_city_night_5"] == 1
    assert kinds["arrival:from_city_night_5"] == 1

    components = _office_components(tilemap)
    assert len(components) == 4
    for component in components:
        cols = [point[0] for point in component]
        rows = [point[1] for point in component]
        assert max(cols) - min(cols) + 1 >= 29
        assert max(rows) - min(rows) + 1 >= 21


def test_map_4_content_and_both_authored_routes_are_reachable() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    reached = _reachable(tilemap, markers["arrival:from_city_night_3"][0])
    required = {
        markers["boundary:modern_city_night_3"][0],
        markers["boundary:modern_city_night_5"][0],
        *markers["npc:businessman"],
        *markers["patrol_npc:businessman:h"],
        *markers["raccoon"],
        *markers["cigarette"],
    }
    assert required <= reached
    assert {
        terrain for source, terrain in AREA_WALK_EXITS if source == MAP_NAME
    } == {"⮟", "⮜"}
    assert AREA_WALK_EXITS[(MAP_NAME, "⮟")].destination == (
        "modern_city_night_3"
    )
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].destination == (
        "modern_city_night_5"
    )


def test_city_3_and_4_openings_align_with_named_arrivals() -> None:
    map_3 = TileMap(config.MAPS_DIR / "modern_city_night_3.txt")
    map_4 = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers_3 = _markers(map_3)
    markers_4 = _markers(map_4)
    assert markers_3["boundary:modern_city_night_4"] == [(45, 0)]
    assert markers_3["arrival:from_city_night_4"] == [(45, 4)]
    assert markers_4["boundary:modern_city_night_3"] == [(36, 59)]
    assert markers_4["arrival:from_city_night_3"] == [(36, 55)]
    assert markers_4["boundary:modern_city_night_5"] == [(0, 36)]
    assert markers_4["arrival:from_city_night_5"] == [(4, 36)]
    assert AREA_WALK_EXITS[("modern_city_night_3", "⮝")].arrival == (
        "from_city_night_3"
    )
    assert AREA_WALK_EXITS[(MAP_NAME, "⮟")].arrival == "from_city_night_4"
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].arrival == "from_city_night_4"


def test_city_night_4_checkpoint_world_and_respawn_are_shared() -> None:
    entry = CHECKPOINT_BY_ID["modern_city_4"]
    assert (entry.display_name, entry.map_name, entry.arrival) == (
        "City Night 4", MAP_NAME, "from_city_night_3"
    )

    directory, game, world = _game_and_world("modern_city_4")
    try:
        assert world.city_rain is not None
        assert len(world.npcs) == 3
        assert all(npc.npc_id == "businessman" for npc in world.npcs)
        assert sum(isinstance(npc, PedestrianNPC)
                   for npc in world.npcs) == 1
        assert len(world.raccoons) == 2
        assert {lane.direction for lane in world.traffic_lanes} == {
            "left", "right"
        }
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        world._arrival_fade_t = None
        world.raccoons[0].on_scratched()
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert world._respawn_phase == "in"
        assert len(world.raccoons) == 2
        assert all(
            enemy.scratches_remaining == config.RACCOON_SCRATCHES
            for enemy in world.raccoons
        )
    finally:
        game._shutdown()
        directory.cleanup()
