"""Day-city connections follow clear footways and arrive away from traffic."""
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.transitions import AREA_WALK_EXITS

MAPS = tuple(f"modern_city_day_{i}" for i in range(1, 7))
INWARD = {"⮝": (0, 1), "⮟": (0, -1), "⮞": (-1, 0), "⮜": (1, 0)}


def _exits(tilemap, name):
    for row in range(tilemap.height_tiles):
        for col in range(tilemap.width_tiles):
            char = tilemap.terrain_at(col, row)
            if (name, char) in AREA_WALK_EXITS:
                yield col, row, char


def test_every_exit_has_a_clear_pavement_approach():
    for name in MAPS:
        tilemap = TileMap(config.MAPS_DIR / f"{name}.txt")
        for col, row, char in _exits(tilemap, name):
            dx, dy = INWARD[char]
            for depth in range(1, 5):
                x, y = col + dx * depth, row + dy * depth
                terrain = tilemap.terrain_at(x, y)
                under = TILE_DEFS[terrain].under or terrain
                assert not tilemap.is_solid(x, y), (name, x, y)
                assert under in {".", "ꞏ"}, (name, x, y, terrain)


def test_every_threshold_cell_travels_and_arrives_on_pavement_without_bounce():
    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            for name in MAPS:
                tilemap = TileMap(config.MAPS_DIR / f"{name}.txt")
                for col, row, char in _exits(tilemap, name):
                    world = game.checkpoints.load_checkpoint(name)
                    world.player.x = col * config.TILE_SIZE
                    world.player.y = row * config.TILE_SIZE
                    world.update(0.0)
                    route = AREA_WALK_EXITS[(name, char)]
                    assert world.map_name == route.destination
                    x = int(world.player.x // config.TILE_SIZE)
                    y = int(world.player.y // config.TILE_SIZE)
                    assert world.tilemap.terrain_at(x, y) == ".", (name, x, y)
                    assert world.player.facing == route.facing
                    world.update(0.0)
                    assert world.map_name == route.destination
        finally:
            game._shutdown()


def test_day_one_plaza_and_side_street_have_no_thin_building_between_them():
    tilemap = TileMap(config.MAPS_DIR / "modern_city_day_1.txt")
    for row in range(14, 29):
        for col in (52, 53, 54):
            terrain = tilemap.terrain_at(col, row)
            assert (TILE_DEFS[terrain].under or terrain) == ".", (col, row)
        assert not tilemap.is_solid(53, row), row


if __name__ == "__main__":
    test_every_exit_has_a_clear_pavement_approach()
    test_every_threshold_cell_travels_and_arrives_on_pavement_without_bounce()
    test_day_one_plaza_and_side_street_have_no_thin_building_between_them()
    print("Day-city sidewalk exit checks passed.")
