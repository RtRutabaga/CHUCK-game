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


def _grass_tiles(tilemap) -> list[tuple[int, int]]:
    return [
        (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
        for kind, (x, y) in tilemap.object_spawns
        if kind == "breakable_grass"
    ]


def test_waterdeep_grass_frames_ruin_and_replaces_exposed_cigarette() -> None:
    tilemap = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    cigarettes = {
        (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
        for kind, (x, y) in tilemap.object_spawns
        if kind == "cigarette"
    }
    assert _grass_tiles(tilemap) == [(32, 20), (25, 25), (32, 25)]
    assert (30, 25) not in cigarettes
    assert tilemap.terrain_at(31, 24) == "R"
    assert not tilemap.is_solid(32, 25)


def test_sewer_grass_is_scattered_only_on_safe_dirt() -> None:
    tilemap = TileMap(config.MAPS_DIR / "sewer.txt")
    expected = [(34, 6), (29, 23), (9, 44), (29, 63)]
    assert _grass_tiles(tilemap) == expected
    for tile in expected:
        assert tilemap.terrain_at(*tile) == "d"
        assert not tilemap.is_solid(*tile)


def test_chult_grass_is_scattered_only_on_jungle_ground() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_jungle.txt")
    expected = [
        (14, 14), (43, 15), (9, 20), (55, 24),
        (47, 34), (22, 40), (55, 45), (14, 51),
    ]
    assert _grass_tiles(tilemap) == expected
    for tile in expected:
        assert tilemap.terrain_at(*tile) == "."
        assert not tilemap.is_solid(*tile)


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
        assert len(scene.breakables) == 3
        initial_pickups = len(scene.pickups)
        grass = next(
            item for item in scene.breakables
            if (int(item._center[0] // config.TILE_SIZE),
                int(item._center[1] // config.TILE_SIZE)) == (32, 25)
        )
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
        assert grass not in scene.breakables
        assert len(scene.breakables) == 2
        assert revealed in scene.pickups
    finally:
        game._shutdown()


def test_scratch_hint_tracks_nearby_intact_grass_only_in_opening_maps() -> None:
    assert config.GRASS_SCRATCH_HINT_MAPS == {"waterdeep_docks", "sewer"}
    game = Game()
    try:
        for map_name in ("waterdeep_docks", "sewer"):
            game.scenes.replace(WorldScene(game, map_name))
            scene = game.scenes.current
            grass = scene.breakables[0]
            scene.player.x = grass.x
            scene.player.y = grass.y
            assert scene._scratch_hint_visible()
            grass.on_scratched()
            assert not scene._scratch_hint_visible()

        game.scenes.replace(WorldScene(game, "waterdeep_tavern"))
        scene = game.scenes.current
        assert scene.map_name not in config.GRASS_SCRATCH_HINT_MAPS
        assert not scene._scratch_hint_visible()

        game.scenes.replace(WorldScene(game, "chult_jungle"))
        scene = game.scenes.current
        grass = scene.breakables[0]
        scene.player.x = grass.x
        scene.player.y = grass.y
        assert not scene._scratch_hint_visible()
        assert config.HINT_SCRATCH == "Press F to scratch"
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
