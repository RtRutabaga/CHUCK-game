"""Premium cartons survive story crossings, not just ordinary map exits."""
import os
import tempfile
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core.game import Game
from src.entities.captain_chest import premium_cartons_collected
from src.scenes.escape_cutscene_scene import EscapeCutsceneScene
from src.scenes.hell_falling_cutscene_scene import HellFallingCutsceneScene
from src.scenes.feywild_river_cutscene_scene import FeywildRiverCutsceneScene
from src.scenes.tower_arrival_cutscene_scene import TowerArrivalCutsceneScene
from src.scenes.modern_city_arrival_cutscene_scene import ModernCityArrivalCutsceneScene
from src.systems.captain_confrontation import (
    CAPTAIN_CONFRONTED_FLAG, CAPTAIN_REQUIRED_FLAGS,
)


# Every cutscene that hands Chuck from one part of the story to the next.
CROSSINGS = (
    EscapeCutsceneScene,
    HellFallingCutsceneScene,
    FeywildRiverCutsceneScene,
    TowerArrivalCutsceneScene,
    ModernCityArrivalCutsceneScene,
)


def _carton_survives(scene_type) -> None:
    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            game.progress.enable("chult_falls_chest_opened")
            game.progress.enable("chult_falls_chest_carton_collected")
            if scene_type is not EscapeCutsceneScene:
                # A real run has finished the captain encounter before Hell.
                # Carrying only treasure flags missed the ship-state crash.
                for flag in CAPTAIN_REQUIRED_FLAGS | {CAPTAIN_CONFRONTED_FLAG}:
                    game.progress.enable(flag)
            scene = scene_type(game, sanity=75)
            game.scenes.replace(scene)
            scene.update(1000.0)
            assert game.scenes.current is not scene, scene_type.__name__
            world = game.scenes.current
            world.update(1 / 30)
            world.draw(game.native_surface)
            assert not any(getattr(npc, "npc_id", None) == "captain_pirate"
                           for npc in world.npcs), scene_type.__name__
            assert game.progress.has("chult_falls_chest_opened"), \
                scene_type.__name__
            assert premium_cartons_collected(game.progress) == 1, \
                scene_type.__name__
            game.progress.enable("captain_chest_carton_collected")
            assert premium_cartons_collected(game.progress) == 2, \
                scene_type.__name__
        finally:
            game._shutdown()


def test_collected_cartons_survive_every_cutscene() -> None:
    for scene_type in CROSSINGS:
        _carton_survives(scene_type)


def _run_all() -> None:
    test_collected_cartons_survive_every_cutscene()
    print("All treasure-handoff tests passed.")


if __name__ == "__main__":
    _run_all()
