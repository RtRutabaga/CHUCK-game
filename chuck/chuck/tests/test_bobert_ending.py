"""The end: premium carton counter, Bobert awake, and the fade to black."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.captain_chest import (
    PREMIUM_CARTON_FLAGS, premium_cartons_collected)
from src.scenes.dialogue_scene import DialogueScene
from src.scenes.ending_scene import FADE, HOLD, EndingScene
from src.scenes.credits_scene import CreditsScene
from src.systems.checkpoints import (
    DESERT_ENTRY_FLAGS, KNOWN_PROGRESS_FLAGS, WATERDEEP_RETURN_FLAG)
from src.systems.dialogue import DialogueSystem
from src.ui.hud import chest_icon


FINALE_FLAGS = set(DESERT_ENTRY_FLAGS) | {WATERDEEP_RETURN_FLAG}


def _finale(cartons: int):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        "waterdeep_finale", progress_flags=set(FINALE_FLAGS))
    for flag in PREMIUM_CARTON_FLAGS[:cartons]:
        game.progress.enable(flag)
    world._arrival_fade_t = None
    return directory, game, world


def _press(game) -> None:
    game.input._actions_just_pressed.add("interact")
    game.scenes.update(1 / 60)
    game.input._actions_just_pressed.clear()


def _talk_to_bobert(game, world) -> list[str]:
    """Stand south of Bobert, face him, and read everything he says."""
    (bobert,) = [p for p in world.props if p.kind == "bobert_barrel_awake"]
    bx, by, bw, bh = bobert.interaction_bounds()
    world.player.x = bx + bw / 2 - world.player.width / 2
    world.player.y = by + bh + 1
    world.player.facing = "up"
    assert world._interactable_in_range() is bobert
    _press(game)
    lines = []
    for _ in range(40):
        scene = game.scenes.current
        if not isinstance(scene, DialogueScene):
            break
        line = scene._lines[scene._index]
        if not lines or lines[-1] != line:
            lines.append(line)
        _press(game)  # finish typing
        _press(game)  # next line
    return lines


QUESTION = ["Chuck! Where have you been?", "...",
            "... did you bring back any smokes?"]
THANKS = ["What's this?...",
          "Three cartons of premium Buhetian halfling leaf?!",
          "You're the best, Chuck"]


def test_the_three_premium_cartons_are_the_three_chests() -> None:
    assert PREMIUM_CARTON_FLAGS == (
        "captain_chest_carton_collected",
        "desert_ruin_chest_carton_collected",
        "chult_falls_chest_carton_collected",
    )
    for flag in PREMIUM_CARTON_FLAGS:
        assert flag in KNOWN_PROGRESS_FLAGS
    dialogue = DialogueSystem()
    assert dialogue.get("bobert_awake") == QUESTION
    assert dialogue.get("bobert_awake_cartons") == THANKS


def test_hud_counts_premium_cartons_beside_the_death_count() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        world = game.checkpoints.load_checkpoint("waterdeep_start")
        assert world.hud.progress is game.progress
        assert premium_cartons_collected(game.progress) == 0
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.hud.draw(surface)
        game.progress.enable("desert_ruin_chest_carton_collected")
        assert premium_cartons_collected(game.progress) == 1
        # The chest icon is drawn left of the skull, in the top bar.
        before = pygame.Surface(surface.get_size())
        world.hud.draw(before)
        assert chest_icon().get_size() == (11, 8)
        gold = (232, 184, 72, 255)
        top = [before.get_at((x, y)) for y in range(0, 16)
               for x in range(config.NATIVE_WIDTH // 2, config.NATIVE_WIDTH)]
        assert gold in top
    finally:
        game._shutdown()
        directory.cleanup()


def test_bobert_sleeps_at_the_start_and_is_up_at_the_end() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        world = game.checkpoints.load_checkpoint("waterdeep_start")
        kinds = [p.kind for p in world.props if p.kind.startswith("bobert")]
        assert kinds == ["bobert_barrel"]
    finally:
        game._shutdown()
        directory.cleanup()
    directory, game, world = _finale(0)
    try:
        (bobert,) = [p for p in world.props if p.kind.startswith("bobert")]
        assert bobert.kind == "bobert_barrel_awake"
        assert bobert.dialogue_id == "bobert_awake"
    finally:
        game._shutdown()
        directory.cleanup()


def _ends_in_fade_then_credits(game, good: bool) -> None:
    ending = game.scenes.current
    assert isinstance(ending, EndingScene)
    assert ending.darkness == 0.0
    for _ in range(int(FADE / 2 * 30)):
        game.scenes.update(1 / 30)
    assert 0.2 < ending.darkness < 0.8  # slow
    for _ in range(int((FADE / 2 + HOLD) * 30) + 5):
        game.scenes.update(1 / 30)
    credits = game.scenes.current
    assert isinstance(credits, CreditsScene)
    assert credits.good is good
    assert len(game.scenes._stack) == 1  # the world is gone


def test_without_all_three_cartons_the_game_ends_on_the_question() -> None:
    directory, game, world = _finale(2)
    try:
        assert _talk_to_bobert(game, world) == QUESTION
        _ends_in_fade_then_credits(game, good=False)
    finally:
        game._shutdown()
        directory.cleanup()


def test_with_all_three_cartons_bobert_is_thrilled_then_the_fade() -> None:
    directory, game, world = _finale(3)
    try:
        assert _talk_to_bobert(game, world) == QUESTION + THANKS
        _ends_in_fade_then_credits(game, good=True)
    finally:
        game._shutdown()
        directory.cleanup()
