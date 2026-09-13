"""The opening cutscene: a new game starts with Chuck waking beside Bobert.

It is played by New Game from the title, runs asleep -> waking ->
smoking -> fading, can be skipped to its fade with interact, and hands
off to the opening docks with a fresh game when it has faded. It is
drawn in the opening docks' evening, not the return's midday.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.game import Game
from src.scenes.opening_cutscene_scene import (
    FADE_END, HOLD_END, LIT, WAKE, OpeningCutsceneScene,
)
from src.scenes.world_scene import WorldScene


def _game():
    directory = tempfile.TemporaryDirectory()
    return directory, Game(save_path=Path(directory.name) / "save.json")


def test_new_game_from_the_title_plays_the_opening() -> None:
    from src.scenes.title_scene import TitleScene

    directory, game = _game()
    try:
        title = TitleScene(game)
        game.scenes.replace(title)
        title._selected = 0
        title._choose()
        assert isinstance(game.scenes.current, OpeningCutsceneScene)
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_wakes_lights_up_and_starts_a_fresh_game() -> None:
    directory, game = _game()
    try:
        game.cigarettes.replace(7)
        scene = OpeningCutsceneScene(game)
        game.scenes.replace(scene)
        phases = []
        while game.scenes.current is scene:
            scene.update(1 / 30)
            if not phases or phases[-1] != scene.phase:
                phases.append(scene.phase)
            if scene.elapsed > WAKE and scene.elapsed < LIT:
                assert not scene.cigarette_lit
        assert phases == ["asleep", "waking", "smoking", "fading"]
        world = game.scenes.current
        assert isinstance(world, WorldScene)
        assert world.map_name == "waterdeep_docks"
        assert game.cigarettes.total == 0
    finally:
        game._shutdown()
        directory.cleanup()


def test_interact_skips_to_the_fade_not_past_it() -> None:
    directory, game = _game()
    try:
        scene = OpeningCutsceneScene(game)
        game.scenes.replace(scene)
        scene.update(0.5)
        game.input._actions_just_pressed.add("interact")
        scene.update(1 / 30)
        game.input._actions_just_pressed.discard("interact")
        assert HOLD_END <= scene.elapsed < FADE_END
        assert game.scenes.current is scene
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_is_drawn_in_the_opening_evening_not_the_midday() -> None:
    directory, game = _game()
    try:
        scene = OpeningCutsceneScene(game)
        game.scenes.replace(scene)
        scene.elapsed = WAKE + 3.0
        surface = pygame.Surface((320, 180))
        scene.draw(surface)
        # The water band is the opening sheet's navy, not the return's teal.
        water = [tuple(surface.get_at((x, 70)))[:3] for x in range(0, 320, 7)]
        navy = sum(1 for r, g, b in water if b > g > r)
        assert navy > len(water) * 0.7
        # The quay is the opening sheet's planks.
        assert scene._planks
        assert tuple(surface.get_at((300, 170)))[:3] != (0, 0, 0)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_docks_fade_up_on_the_pose_the_cutscene_ended_on() -> None:
    directory, game = _game()
    try:
        scene = OpeningCutsceneScene(game)
        game.scenes.replace(scene)
        scene.elapsed = FADE_END - 0.01
        scene.update(0.05)
        world = game.scenes.current
        assert isinstance(world, WorldScene)
        assert world._arrival_fade_t is not None
        assert world._arrival_fade_from == (0, 0, 0)
        assert world.player.facing == "left"
    finally:
        game._shutdown()
        directory.cleanup()
