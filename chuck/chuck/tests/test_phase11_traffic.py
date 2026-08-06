"""Phase 11 deterministic traffic lanes and City Night 1 crossing."""

from collections import Counter
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.traffic import ROAD_TERRAIN, TrafficLane
from src.world.collision import overlaps
from src.world.tilemap import TileMap


MAP_NAME = "modern_city_arrival"


def _game_and_world(checkpoint_id: str = "modern_city_1"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(checkpoint_id)
    return directory, game, world


def test_lane_has_fixed_deterministic_population_and_wraps_cleanly() -> None:
    lane = TrafficLane(0.0, 408.0, "right", 0, 1152.0, 864.0)
    expected_count = math.ceil(
        (1152.0 + config.TRAFFIC_MARGIN * 2) / config.TRAFFIC_SPACING
    )
    assert len(lane.vehicles) == expected_count
    initial = [vehicle.center for vehicle in lane.vehicles]

    for _ in range(600):
        lane.update(1 / 60)
    assert len(lane.vehicles) == expected_count
    assert all(
        -config.TRAFFIC_MARGIN <= vehicle.center[0]
        <= 1152.0 + config.TRAFFIC_MARGIN
        for vehicle in lane.vehicles
    )

    lane.reset()
    assert [vehicle.center for vehicle in lane.vehicles] == initial


def test_city_night_1_authors_two_observable_opposed_lanes() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _position in tilemap.object_spawns)
    assert kinds["traffic_lane:right:0"] == 1
    assert kinds["traffic_lane:left:1"] == 1
    assert ROAD_TERRAIN == frozenset({"=", "▦"})
    assert "".join(tilemap._grid).count("▦") == 12

    for kind, (x, y) in tilemap.object_spawns:
        if not kind.startswith("traffic_lane:"):
            continue
        assert tilemap.terrain_at(
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)
        ) == "="


def test_world_builds_fixed_traffic_and_draws_the_teaching_crossing() -> None:
    directory, game, world = _game_and_world()
    try:
        assert {lane.direction for lane in world.traffic_lanes} == {
            "left", "right"
        }
        assert len(world.traffic_vehicles) == 10
        initial_count = len(world.traffic_vehicles)
        for _ in range(300):
            world.update(1 / 60)
        assert len(world.traffic_vehicles) == initial_count

        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.draw(surface)
    finally:
        game._shutdown()
        directory.cleanup()


def test_traffic_hit_is_severe_and_never_leaves_chuck_embedded() -> None:
    directory, game, world = _game_and_world()
    try:
        safe_position = (world.player.x, world.player.y)
        world.sanity.current = config.SANITY_MAX
        vehicle = world.traffic_vehicles[0]
        world.player.x = vehicle.x
        world.player.y = vehicle.y
        world._traffic_safe_position = safe_position
        assert overlaps(world.player.hitbox, vehicle.hitbox)

        world.update(0.0)
        assert world.sanity.current == (
            config.SANITY_MAX - config.TRAFFIC_SANITY_DAMAGE
        )
        assert (world.player.x, world.player.y) == safe_position
        assert not overlaps(world.player.hitbox, vehicle.hitbox)
    finally:
        game._shutdown()
        directory.cleanup()


def test_lethal_traffic_uses_normal_checkpoint_return_and_resets_lanes() -> None:
    directory, game, world = _game_and_world("modern_city_anchor")
    try:
        world._arrival_fade_t = None
        world.sanity.current = config.TRAFFIC_SANITY_DAMAGE
        vehicle = world.traffic_vehicles[0]
        world.player.x = vehicle.x
        world.player.y = vehicle.y
        world.update(0.0)
        assert world._respawn_phase == "out"

        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert world._respawn_phase == "in"
        assert world.sanity.current == config.SANITY_MAX
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
        assert len(world.traffic_vehicles) == 10
    finally:
        game._shutdown()
        directory.cleanup()


def test_generated_vehicle_sheet_has_four_distinct_opaque_cars() -> None:
    image = pygame.image.load(
        str(config.SPRITES_DIR / "hazards" / "city_traffic.png")
    )
    assert image.get_size() == (160, 20)
    opaque_counts = []
    for index in range(4):
        frame = image.subsurface((index * 40, 0, 40, 20))
        opaque_counts.append(sum(
            frame.get_at((x, y)).a > 0
            for y in range(20) for x in range(40)
        ))
    assert all(count > 300 for count in opaque_counts)
