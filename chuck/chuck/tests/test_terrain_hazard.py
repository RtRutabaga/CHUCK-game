"""Phase 4 thorn terrain behavior and safe-route placement."""

import os
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.world_scene import WorldScene
from src.systems.terrain_hazard import touching_terrain_hazard
from src.world.tilemap import TileMap


def test_thorns_damage_on_foot_but_are_safe_while_airborne() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_jungle.txt")
    box = pygame.Rect(31 * config.TILE_SIZE + 3,
                      37 * config.TILE_SIZE + 4, 10, 8)
    hazard = touching_terrain_hazard(tilemap, box, airborne=False)
    assert hazard is not None
    assert hazard.kind == "thorns"
    assert hazard.sanity_damage == config.THORN_SANITY_DAMAGE
    assert touching_terrain_hazard(tilemap, box, airborne=True) is None
    safe = pygame.Rect(20 * config.TILE_SIZE, 37 * config.TILE_SIZE, 10, 8)
    assert touching_terrain_hazard(tilemap, safe, airborne=False) is None


def test_scattered_thorn_patches_are_optional_and_main_route_stays_safe() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_jungle.txt")
    thorns = {
        (col, row)
        for row, line in enumerate(tilemap._grid)
        for col, char in enumerate(line)
        if char == "|"
    }
    assert len(thorns) == 25
    # Thorn growth is scattered through distinct clearings rather than reading
    # as one isolated tutorial patch.
    remaining = set(thorns)
    clusters = 0
    while remaining:
        clusters += 1
        frontier = [remaining.pop()]
        while frontier:
            col, row = frontier.pop()
            for neighbor in ((col - 1, row), (col + 1, row),
                             (col, row - 1), (col, row + 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    frontier.append(neighbor)
    assert clusters == 6

    sx, sy = tilemap.spawn_points["player"]
    start = (int(sx // config.TILE_SIZE), int(sy // config.TILE_SIZE))
    goal = (30, 3)
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for neighbor in ((col - 1, row), (col + 1, row),
                         (col, row - 1), (col, row + 1)):
            if (
                neighbor not in reached
                and neighbor not in thorns
                and not tilemap.is_solid(*neighbor)
            ):
                reached.add(neighbor)
                frontier.append(neighbor)
    assert goal in reached


def test_world_scene_applies_thorn_damage_with_existing_iframes() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "chult_jungle"))
        scene = game.scenes.current
        ts = config.TILE_SIZE
        scene.player.x = 31 * ts + (ts - scene.player.width) / 2
        scene.player.y = 37 * ts + (ts - scene.player.height) / 2
        start = scene.sanity.current
        scene.update(0.01)
        assert scene.sanity.current == start - config.THORN_SANITY_DAMAGE
        scene.update(0.01)
        assert scene.sanity.current == start - config.THORN_SANITY_DAMAGE
    finally:
        game._shutdown()


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Chult terrain-hazard tests passed.")


if __name__ == "__main__":
    _run_all()
