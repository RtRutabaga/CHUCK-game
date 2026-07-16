"""Reusable breakable grass and its first Waterdeep reward."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.breakable_grass import BreakableGrass
from src.scenes.world_scene import WorldScene
from src.world.tilemap import TileMap


def test_waterdeep_grass_replaces_exposed_cigarette_at_ruin_corner() -> None:
    tilemap = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    grass = [
        (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
        for kind, (x, y) in tilemap.object_spawns
        if kind == "breakable_grass"
    ]
    cigarettes = {
        (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
        for kind, (x, y) in tilemap.object_spawns
        if kind == "cigarette"
    }
    assert grass == [(32, 25)]
    assert (30, 25) not in cigarettes
    assert tilemap.terrain_at(31, 24) == "R"
    assert not tilemap.is_solid(32, 25)


def test_grass_breaks_once_and_finishes_its_debris_animation() -> None:
    grass = BreakableGrass(40, 40)
    assert grass.intact and grass.alive
    grass.on_scratched()
    assert not grass.intact
    assert grass.take_drop_position() == (40, 40)
    assert grass.take_drop_position() is None
    grass.update(config.BREAKABLE_GRASS_DURATION + 0.01)
    assert not grass.alive


def test_world_scratch_reveals_loaded_cigarette() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_docks"))
        scene = game.scenes.current
        assert len(scene.breakables) == 1
        initial_pickups = len(scene.pickups)
        grass = scene.breakables[0]
        scene.player.x = grass.x - scene.player.width
        scene.player.y = grass.y + 3
        scene.player.facing = "right"
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.01)
        assert not grass.intact
        assert len(scene.pickups) == initial_pickups + 1
        revealed = scene.pickups[-1]
        assert (revealed.x + revealed.width / 2,
                revealed.y + revealed.height / 2) == grass._center
        scene.update(config.BREAKABLE_GRASS_DURATION + 0.01)
        assert not scene.breakables
        assert revealed in scene.pickups
    finally:
        game._shutdown()


def test_grass_sprite_is_one_native_tile() -> None:
    image = pygame.image.load(
        config.SPRITES_DIR / "objects" / "breakable_grass.png"
    )
    assert image.get_size() == (config.TILE_SIZE, config.TILE_SIZE)


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All breakable-grass tests passed.")


if __name__ == "__main__":
    _run_all()
