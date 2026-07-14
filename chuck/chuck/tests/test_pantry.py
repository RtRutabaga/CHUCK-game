"""Phase 3 pantry layout, materials, transition, and Astral retry tests."""

import os
from collections import Counter, deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.world_scene import WorldScene
from src.world.tilemap import TileMap


def _place_on_tile(scene: WorldScene, col: int, row: int) -> None:
    ts = config.TILE_SIZE
    scene.player.x = col * ts + (ts - scene.player.width) / 2
    scene.player.y = row * ts + (ts - scene.player.height) / 2


def test_pantry_is_compact_readable_and_safely_navigable() -> None:
    pantry = TileMap(config.MAPS_DIR / "waterdeep_pantry.txt")
    assert (pantry.width_tiles, pantry.height_tiles) == (26, 18)
    terrain = Counter(ch for row in pantry._grid for ch in row)
    assert terrain["p"] > 250
    assert terrain["V"] == 18
    assert terrain["s"] == 14
    assert not pantry.is_solid(9, 7)  # Astral retains the fall-zone contract.
    assert pantry.is_solid(11, 4)     # Sky waits for its distinct fall branch.

    props = Counter(kind for kind, _, _ in pantry.prop_tiles)
    assert props == Counter({
        "grain_sack": 4,
        "barrel": 2,
        "pantry_shelf": 2,
        "crate": 2,
        "pantry_open": 1,
    })

    sx, sy = pantry.spawn_points["player"]
    start = (int(sx // config.TILE_SIZE), int(sy // config.TILE_SIZE))
    seen = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for neighbor in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            if (
                neighbor not in seen
                and pantry.terrain_at(*neighbor) == "p"
                and not pantry.is_solid(*neighbor)
            ):
                seen.add(neighbor)
                frontier.append(neighbor)
    safe_floor = {
        (col, row)
        for row in range(pantry.height_tiles)
        for col in range(pantry.width_tiles)
        if pantry.terrain_at(col, row) == "p" and not pantry.is_solid(col, row)
    }
    assert seen == safe_floor


def test_pantry_doorway_is_bidirectional_without_bounce() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_tavern"))
        scene = game.scenes.current
        _place_on_tile(scene, 14, 1)
        scene.update(0.01)
        assert scene.map_name == "waterdeep_pantry"
        assert scene._player_tile() == (13, 15)
        assert scene.player.facing == "up"
        scene.update(0.01)
        assert scene.map_name == "waterdeep_pantry"

        _place_on_tile(scene, 13, 16)
        scene.update(0.01)
        assert scene.map_name == "waterdeep_tavern"
        assert scene._player_tile() == (14, 2)
        assert scene.player.facing == "down"
        scene.update(0.01)
        assert scene.map_name == "waterdeep_tavern"
    finally:
        game._shutdown()


def test_pantry_astral_floor_reuses_fall_and_local_retry() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_pantry"))
        scene = game.scenes.current
        spawn = (scene.player.x, scene.player.y)
        _place_on_tile(scene, 9, 7)
        scene.update(0.01)
        assert scene._fall_t == 0.0
        assert scene.player.fall_progress == 0.0
        scene.update(config.FALL_DURATION)
        assert scene._respawn_phase == "out"
        scene.update(config.RESPAWN_FADE_OUT)
        scene.update(config.RESPAWN_HOLD)
        assert scene.map_name == "waterdeep_pantry"
        assert (scene.player.x, scene.player.y) == spawn
        assert scene.player.visible
        game.scenes.draw(game.native_surface)
    finally:
        game._shutdown()


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
    print("All pantry tests passed.")


if __name__ == "__main__":
    _run_all()
