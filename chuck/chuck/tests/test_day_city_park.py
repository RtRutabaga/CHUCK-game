"""The new plaza stays walkable and every added object answers Examine."""
import os
from collections import deque
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.dialogue_scene import DialogueScene


def test_day_shops_and_park_answer_examine_in_the_world():
    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            shops = 0
            park = []
            for i in range(1, 7):
                world = game.checkpoints.load_checkpoint(f"modern_city_day_{i}")
                for kind, col, row in world.tilemap.prop_tiles:
                    if not (kind.startswith(("city_shop_", "city_park_"))
                            or kind == "city_newspaper_box"):
                        continue
                    shop = kind.startswith("city_shop_")
                    if shop:
                        shops += 1
                        for y in range(row - 2, row + 1):
                            for x in range(col - 1, col + 2):
                                assert world.tilemap.is_solid(x, y)
                    else:
                        assert i == 1
                        park.append(kind)
                    world.player.x = (col + (1 if shop else 0)) * config.TILE_SIZE
                    world.player.y = (row + 1) * config.TILE_SIZE
                    world.player.facing = "up"
                    game.input._actions_just_pressed.add("interact")
                    world.update(0.0)
                    game.input._actions_just_pressed.clear()
                    overlay = game.scenes.current
                    assert isinstance(overlay, DialogueScene), kind
                    if shop:
                        assert overlay._lines == ["it's closed"]
                    else:
                        assert overlay._lines == world.dialogue.get(f"examine_{kind}")
                    game.scenes.pop()
            assert shops == 12
            assert park.count("city_park_fountain") == 1
            assert park.count("city_park_bench") == 4
            assert park.count("city_park_planter") == 4
            assert park.count("city_newspaper_box") == 1
        finally:
            game._shutdown()


def test_park_has_a_walkable_ring_and_preserves_the_plaza_routes():
    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            world = game.checkpoints.load_checkpoint("modern_city_day_1")
            tilemap = world.tilemap
            start = (30, 28)
            found = {start}
            queue = deque([start])
            while queue:
                x, y = queue.popleft()
                for point in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                    c, r = point
                    if not (30 <= c <= 54 and 14 <= r <= 30):
                        continue
                    if point in found or tilemap.is_solid(c,r):
                        continue
                    found.add(point)
                    queue.append(point)
            for row in (21, 24):
                assert all((col, row) in found for col in range(39,46))
            assert {(39,22),(45,22),(53,20),(42,28),(36,17)} <= found
            for row in (22,23):
                assert all(tilemap.is_solid(col,row) for col in range(40,45))
        finally:
            game._shutdown()


if __name__ == "__main__":
    test_day_shops_and_park_answer_examine_in_the_world()
    test_park_has_a_walkable_ring_and_preserves_the_plaza_routes()
    print("Day-city park checks passed.")
