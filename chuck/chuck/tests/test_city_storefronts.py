"""Neon shops sit inside the wall and their closed doors answer Examine."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.prop import Prop
from src.scenes.dialogue_scene import DialogueScene
from src.systems.dialogue import DialogueSystem
from src.systems.interaction import find_target
from src.world.tilemap import TileMap


KINDS = {"city_neon_bar", "city_neon_open", "city_neon_24h"}
MAPS = ("modern_city_arrival",) + tuple(
    f"modern_city_night_{i}" for i in range(2, 7))


def test_every_shop_fits_the_building_and_has_a_reachable_closed_door():
    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            count = 0
            dialogue = DialogueSystem()
            for name in MAPS:
                tilemap = TileMap(config.MAPS_DIR / f"{name}.txt")
                for kind, col, row in tilemap.prop_tiles:
                    if kind not in KINDS:
                        continue
                    count += 1
                    prop = Prop(kind, col, row, game.assets)
                    # Every pixel of the enlarged frontage is over existing
                    # solid building, never sidewalk or a neighboring alley.
                    for y in range(row - 2, row + 1):
                        for x in range(col - 1, col + 2):
                            assert tilemap.is_solid(x, y), (name, x, y)
                    assert not tilemap.is_solid(col + 1, row + 1), name
                    assert prop.choice_id is None
                    assert dialogue.get(prop.dialogue_id) == ["it's closed"]
                    # Approach the visible door from the pavement, facing
                    # north: the same target search used by the Examine key.
                    feet = ((col + 1) * 16, (row + 1) * 16 + 2, 8, 8)
                    probe = (feet[0], feet[1] - 8, 8, 8)
                    assert find_target(probe, feet, [], [prop]) is prop
                    # Only the neon flickers. Nothing below the lintel moves
                    # or opens when the animation advances.
                    import pygame
                    bodies = [pygame.image.tobytes(
                        frame.subsurface((0, 13, 48, 35)), "RGBA")
                        for frame in prop._frames]
                    assert len(set(bodies)) == 1
            assert count == 12
        finally:
            game._shutdown()


def test_examine_at_each_door_opens_closed_dialogue_without_travel():
    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            for i, name in enumerate(MAPS, 1):
                scene = game.checkpoints.load_checkpoint(f"modern_city_{i}")
                for kind, col, row in scene.tilemap.prop_tiles:
                    if kind not in KINDS:
                        continue
                    scene.player.x = (col + 1) * config.TILE_SIZE
                    scene.player.y = (row + 1) * config.TILE_SIZE
                    scene.player.facing = "up"
                    game.input._actions_just_pressed.add("interact")
                    scene.update(0.0)
                    game.input._actions_just_pressed.discard("interact")
                    overlay = game.scenes.current
                    assert isinstance(overlay, DialogueScene), (name, kind)
                    assert overlay._lines == ["it's closed"], (name, kind)
                    assert scene.map_name == name
                    game.scenes.pop()
        finally:
            game._shutdown()


if __name__ == "__main__":
    test_every_shop_fits_the_building_and_has_a_reachable_closed_door()
    test_examine_at_each_door_opens_closed_dialogue_without_travel()
    print("All city storefront checks passed.")
