"""Phase 8's fortress escape and handoff to the first Feywild map."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.feywild_river_cutscene_scene import (
    ASHORE_TIME,
    CUTSCENE_END,
    FADE_IN_END,
    FADE_OUT_START,
    FEYWILD_GROW_START,
    MUSIC_START,
    PRONE_END,
    RISE_END,
    SHORE_START,
    WATERFALL_END,
    WATERFALL_START,
    FeywildRiverCutsceneScene,
    _FOAM,
)


APPROACH = "phlegethos_fortress_approach"


def test_fortress_escape_hands_off_to_the_shared_cutscene_scene() -> None:
    game = Game()
    try:
        world = game.checkpoints.load_checkpoint(APPROACH, sanity=47)
        world._pending_entrance_dialogue = None
        world._begin_river_escape()
        world.update(config.FEYWILD_RIVER_ESCAPE_FADE)
        cutscene = game.scenes.current
        assert isinstance(cutscene, FeywildRiverCutsceneScene)
        assert cutscene.sanity == 47
    finally:
        game._shutdown()


def test_cutscene_uses_the_fall_cue_and_reaches_each_authored_phase() -> None:
    game = Game()
    try:
        scene = FeywildRiverCutsceneScene(game, sanity=61)
        game.scenes.replace(scene)
        music = []
        sounds = []
        game.audio.play_music = lambda filename, loop=True: music.append(
            (filename, loop)
        )
        game.audio.play_sfx = sounds.append

        scene.update(MUSIC_START - 0.01)
        assert music == []
        scene.update(0.02)
        assert music == [("fall_to_chult.wav", False)]
        scene.update(FEYWILD_GROW_START - scene.elapsed + 0.1)
        assert scene.phase == "rush"
        scene.update(WATERFALL_START - scene.elapsed + 0.01)
        assert scene.phase == "waterfall" and sounds == ["jump"]
        scene.update(WATERFALL_END - scene.elapsed + 0.01)
        assert scene.phase == "calm"
        scene.update(SHORE_START - scene.elapsed + 0.01)
        assert scene.phase == "washing_ashore"
        scene.update(ASHORE_TIME - scene.elapsed + 0.01)
        assert scene.phase == "prone" and sounds == ["jump", "chime"]
        scene.update(PRONE_END - scene.elapsed + 0.01)
        assert scene.phase == "rising"
        scene.update(RISE_END - scene.elapsed + 0.01)
        assert scene.phase == "standing"
        assert scene.sanity == 61
    finally:
        game._shutdown()


def test_every_phase_draws_then_hands_off_to_the_feywild_riverbank() -> None:
    game = Game()
    try:
        scene = FeywildRiverCutsceneScene(game, sanity=75)
        game.scenes.replace(scene)
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        for target in (
            0.3,
            4.5,
            WATERFALL_START + 0.8,
            WATERFALL_END + 1.0,
            SHORE_START + 0.5,
            ASHORE_TIME + 0.5,
            PRONE_END + 0.5,
            RISE_END + 0.5,
            FADE_OUT_START + 0.5,
            CUTSCENE_END - 0.01,
        ):
            scene.update(target - scene.elapsed)
            scene.draw(surface)
            assert game.scenes.current is scene

        assert surface.get_at((160, 90))[:3] == (0, 0, 0)
        scene.update(0.02)
        world = game.scenes.current
        assert scene.complete
        assert world is not scene
        assert world.map_name == "feywild_riverbank"
        assert world.sanity.current == 75
        assert game.active_checkpoint_id == "feywild_riverbank"
        assert game.progress.has("feywild_reached")
    finally:
        game._shutdown()


def test_cutscene_opens_on_black_and_fades_in_slowly() -> None:
    game = Game()
    try:
        scene = FeywildRiverCutsceneScene(game, sanity=75)
        game.scenes.replace(scene)
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))

        scene.draw(surface)
        assert surface.get_at((160, 90))[:3] == (0, 0, 0)
        scene.update(FADE_IN_END / 2)
        scene.draw(surface)
        midpoint = surface.get_at((160, 90))[:3]
        assert midpoint != (0, 0, 0)
        scene.update(FADE_IN_END / 2 + 0.01)
        scene.draw(surface)
        assert surface.get_at((160, 90))[:3] != midpoint
    finally:
        game._shutdown()


def test_washing_ashore_has_no_detached_horizontal_foam_line() -> None:
    game = Game()
    try:
        scene = FeywildRiverCutsceneScene(game, sanity=75)
        game.scenes.replace(scene)
        scene.update((SHORE_START + ASHORE_TIME) / 2)
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        scene.draw(surface)

        # The prior artifact was an explicit 19px horizontal _FOAM stroke
        # beside Chuck. Natural river foam elsewhere remains untouched.
        longest = 0
        for y in range(90, 130):
            run = 0
            for x in range(155, 215):
                if surface.get_at((x, y))[:3] == _FOAM:
                    run += 1
                    longest = max(longest, run)
                else:
                    run = 0
        assert longest < 8
    finally:
        game._shutdown()


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All Phase 8 Feywild river-cutscene tests passed.")


if __name__ == "__main__":
    _run_all()
