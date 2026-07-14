"""Phase 2 sewer outflow and restrained return-to-docks tests."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.world_scene import WorldScene


def test_walking_through_outflow_climbs_from_water_onto_south_pier() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "sewer"))
        scene = game.scenes.current
        ts = config.TILE_SIZE
        scene.player.x = 16 * ts + (ts - scene.player.width) / 2
        scene.player.y = 70 * ts + (ts - scene.player.height) / 2

        scene.update(0.01)
        assert scene.map_name == "waterdeep_docks"
        assert scene._climb_t == 0.0
        assert scene.player.facing == "up"
        start_y, target_y = scene._climb_from_y, scene._climb_target_y
        assert start_y == target_y + ts

        scene.update(config.CLIMB_OUT_DURATION / 2)
        assert target_y < scene.player.y < start_y
        assert scene.player.climb_progress is not None
        game.scenes.draw(game.native_surface)

        scene.update(config.CLIMB_OUT_DURATION)
        assert scene._climb_t is None
        assert scene.player.climb_progress is None
        assert scene.player.y == target_y
        assert not scene.player.moving
        assert scene.tilemap.terrain_at(*scene._player_tile()) == "="
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
    print("All outflow tests passed.")


if __name__ == "__main__":
    _run_all()
