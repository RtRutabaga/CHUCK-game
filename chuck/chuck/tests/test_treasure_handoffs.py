"""Premium cartons survive story crossings, not just ordinary map exits."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pytest

from src.core.game import Game
from src.entities.captain_chest import premium_cartons_collected
from src.scenes.escape_cutscene_scene import EscapeCutsceneScene
from src.scenes.hell_falling_cutscene_scene import HellFallingCutsceneScene
from src.scenes.feywild_river_cutscene_scene import FeywildRiverCutsceneScene
from src.scenes.tower_arrival_cutscene_scene import TowerArrivalCutsceneScene
from src.scenes.modern_city_arrival_cutscene_scene import ModernCityArrivalCutsceneScene


@pytest.mark.parametrize("scene_type", [
    EscapeCutsceneScene, HellFallingCutsceneScene, FeywildRiverCutsceneScene,
    TowerArrivalCutsceneScene, ModernCityArrivalCutsceneScene,
])
def test_collected_cartons_survive_cutscene(scene_type, tmp_path):
    game = Game(save_path=tmp_path / "save.json")
    try:
        game.progress.enable("chult_falls_chest_opened")
        game.progress.enable("chult_falls_chest_carton_collected")
        scene = scene_type(game, sanity=75)
        game.scenes.replace(scene)
        scene.update(1000.0)
        assert game.scenes.current is not scene
        assert game.progress.has("chult_falls_chest_opened")
        assert premium_cartons_collected(game.progress) == 1
        game.progress.enable("captain_chest_carton_collected")
        assert premium_cartons_collected(game.progress) == 2
    finally:
        game._shutdown()
