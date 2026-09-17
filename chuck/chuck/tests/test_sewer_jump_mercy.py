"""Missed sewer-course jumps retry locally, without changing portable saves."""
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.respawn import mercy_retry_tile


def _place(world, col, row):
    world.player.x = (col + 0.5) * config.TILE_SIZE - world.player.width / 2
    world.player.y = (row + 0.5) * config.TILE_SIZE - world.player.height / 2


def _finish_respawn(world):
    world.update(config.RESPAWN_FADE_OUT + 0.01)
    world.update(config.RESPAWN_HOLD + 0.01)
    world.update(config.RESPAWN_FADE_IN + 0.01)


def test_every_course_gap_retries_on_dry_ground_and_does_not_move_save_entry():
    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            world = game.checkpoints.load_checkpoint("modern_city_sewer_2")
            entrance = world.respawn.position_for_chuck()
            checkpoint = game.active_checkpoint_id
            assert world.tilemap.terrain_at(12, 42) == "d"
            assert not world.tilemap.is_solid(12, 42)
            count = 0
            for row in range(45, 55):
                for col in range(10, 25):
                    if world.tilemap.terrain_at(col, row) != "V":
                        continue
                    _place(world, col, row)
                    world.update(0.0)
                    assert world._fall_t is not None
                    world.update(config.FALL_DURATION + 0.01)
                    assert world._respawn_phase == "out"
                    _finish_respawn(world)
                    count += 1
                    assert game.deaths.total == count
                    assert int((world.player.x + world.player.width / 2) / 16) == 12
                    assert int((world.player.y + world.player.height / 2) / 16) == 42
                    assert world.respawn.position_for_chuck() == entrance
                    assert game.active_checkpoint_id == checkpoint
                    world.update(0.0)
                    assert world._fall_t is None
                    assert world._respawn_phase is None
            assert count > 20
            # A later death away from the jumps must not inherit the mercy
            # destination from the preceding retry.
            _place(world, 34, 34)
            world.sanity.deplete()
            _finish_respawn(world)
            assert (world.player.x, world.player.y) == entrance
            assert game.deaths.total == count + 1
        finally:
            game._shutdown()


def test_mercy_is_limited_to_this_course():
    assert mercy_retry_tile("modern_city_sewer_2", 12, 46) == (12, 42)
    for map_name in ("sewer", "modern_city_sewer_1", "modern_city_sewer_3",
                     "modern_city_sewer_4", "pantry"):
        assert mercy_retry_tile(map_name, 12, 46) is None
    for col, row in ((12, 44), (12, 55), (12, 59), (9, 49), (25, 49)):
        assert mercy_retry_tile("modern_city_sewer_2", col, row) is None


if __name__ == "__main__":
    test_every_course_gap_retries_on_dry_ground_and_does_not_move_save_entry()
    test_mercy_is_limited_to_this_course()
    print("Sewer jump mercy checks passed.")
