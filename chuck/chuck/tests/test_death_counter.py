"""The death count: how many times Chuck died this playthrough.

Two kinds of death go into it and the second is the one worth policing.
The ordinary kind is easy -- Sanity runs out, or Chuck drops into the
Astral, and the world quietly takes him away and gives him back. The
other kind happens on screen: three of the game's cutscenes play that
exact vanish and return, and those count. Every other cutscene, where
he lands on something and gets up, counts nothing -- so this file runs
every cutscene in the game from its first frame to its handoff and
checks which ones moved the number, rather than trusting a list.

The count only goes up. Death rewinds the cigarettes, because what
Chuck picked up past the checkpoint is lost with him; a death is not a
thing that can be lost that way.
"""

import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.deaths import DeathCounter
from src.systems.save import SAVE_VERSION, SaveRecord, SaveSystem
from src.ui.hud import death_icon


def _game() -> tuple[tempfile.TemporaryDirectory, Game]:
    directory = tempfile.TemporaryDirectory()
    return directory, Game(save_path=Path(directory.name) / "save.json")


def _die_and_return(scene) -> None:
    scene.sanity.deplete()
    scene.update(config.RESPAWN_FADE_OUT + 0.01)
    scene.update(config.RESPAWN_HOLD + 0.01)
    scene.update(config.RESPAWN_FADE_IN + 0.01)


def test_the_counter_only_goes_up() -> None:
    deaths = DeathCounter()
    assert deaths.total == 0
    deaths.record()
    deaths.record()
    assert deaths.total == 2
    deaths.replace(9)
    assert deaths.total == 9
    try:
        deaths.replace(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("a death count cannot be negative")


def test_an_ordinary_death_counts_once_and_is_not_rewound() -> None:
    """One vanish, one death -- and the respawn does not take it back.

    The cigarette count rolls back on the same respawn, which is the
    contrast worth asserting: both happen in one frame and only one of
    them is undone.
    """
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        game.cigarettes.add(4)
        _die_and_return(scene)
        assert game.deaths.total == 1
        assert game.cigarettes.total == 0      # rewound
        _die_and_return(scene)
        assert game.deaths.total == 2
    finally:
        game._shutdown()
        directory.cleanup()


def test_a_second_depletion_during_the_fade_is_the_same_death() -> None:
    """A hit that lands while Chuck is already gone does not count again."""
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        scene.sanity.deplete()
        scene.update(0.05)
        scene.sanity.deplete()
        assert game.deaths.total == 1
    finally:
        game._shutdown()
        directory.cleanup()


def test_a_fall_into_the_astral_is_a_death() -> None:
    """The fall hands off to the ordinary respawn, so it counts there."""
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        scene._begin_fall("astral")
        scene.update(config.FALL_DURATION + 0.01)
        assert game.deaths.total == 1
    finally:
        game._shutdown()
        directory.cleanup()


def _cutscenes():
    """Every cutscene in the game, built the way the game builds it."""
    from src.scenes.desert_arrival_cutscene_scene import (
        DesertArrivalCutsceneScene)
    from src.scenes.doug_fir_cutscene_scene import DougFirCutsceneScene
    from src.scenes.escape_cutscene_scene import EscapeCutsceneScene
    from src.scenes.falling_cutscene_scene import FallingCutsceneScene
    from src.scenes.feywild_river_cutscene_scene import (
        FeywildRiverCutsceneScene)
    from src.scenes.hell_falling_cutscene_scene import (
        HellFallingCutsceneScene)
    from src.scenes.modern_city_arrival_cutscene_scene import (
        ModernCityArrivalCutsceneScene)
    from src.scenes.return_to_waterdeep_cutscene_scene import (
        ReturnToWaterdeepCutsceneScene)
    from src.scenes.tower_arrival_cutscene_scene import (
        TowerArrivalCutsceneScene)
    from src.scenes.zephyros_intro_cutscene_scene import (
        ZephyrosIntroCutsceneScene)
    from src.scenes.zephyros_launch_cutscene_scene import (
        ZephyrosLaunchCutsceneScene)

    full = config.SANITY_MAX
    return {
        "fall_to_chult": lambda game: FallingCutsceneScene(game),
        "fall_into_hell": lambda game: HellFallingCutsceneScene(
            game, sanity=full),
        "modern_city_arrival": lambda game: ModernCityArrivalCutsceneScene(
            game, sanity=full),
        "escape": lambda game: EscapeCutsceneScene(game),
        "feywild_river": lambda game: FeywildRiverCutsceneScene(
            game, sanity=full),
        "tower_arrival": lambda game: TowerArrivalCutsceneScene(
            game, sanity=full),
        "zephyros_intro": lambda game: ZephyrosIntroCutsceneScene(
            game, sanity=full),
        "zephyros_launch": lambda game: ZephyrosLaunchCutsceneScene(
            game, sanity=full),
        "doug_fir": lambda game: DougFirCutsceneScene(game),
        "desert_arrival": lambda game: DesertArrivalCutsceneScene(game),
        "return_to_waterdeep": lambda game: ReturnToWaterdeepCutsceneScene(
            game),
    }


# The three where he dies on screen: impact, the quiet vanish, the
# return. Every other cutscene ends with him alive and on his feet.
DYING_CUTSCENES = {"fall_to_chult", "fall_into_hell", "modern_city_arrival"}


def test_only_the_cutscenes_where_chuck_dies_count_a_death() -> None:
    """Run each one start to handoff and see what it did to the number.

    Forty-five seconds covers the longest of them with room to spare;
    the dialogue scene never finishes without a key press, which is
    fine, because nothing in it can kill him either.
    """
    counted = {}
    for name, build in _cutscenes().items():
        directory, game = _game()
        try:
            game.checkpoints.load_checkpoint("waterdeep_start")
            scene = build(game)
            game.deaths.replace(0)
            for _ in range(45 * 20):
                scene.update(1 / 20)
            counted[name] = game.deaths.total
        finally:
            game._shutdown()
            directory.cleanup()

    assert {name for name, total in counted.items() if total} == \
        DYING_CUTSCENES, counted
    # ...and each of those is one death, not one per cue that mentions it.
    for name in DYING_CUTSCENES:
        assert counted[name] == 1, (name, counted[name])


def test_the_count_carries_through_handoffs_and_resets_only_on_new_game():
    directory, game = _game()
    try:
        game.checkpoints.load_checkpoint("waterdeep_start")
        game.deaths.replace(3)
        game.checkpoints.load_checkpoint("chult_landing")
        assert game.deaths.total == 3
        game.checkpoints.new_game()
        assert game.deaths.total == 0
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_ashtray_saves_it_and_continue_restores_it() -> None:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "save.json"
    game = Game(save_path=path)
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        _die_and_return(scene)
        _die_and_return(scene)
        anchor = scene.anchors[0]
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.update(0.01)
        assert json.loads(path.read_text(encoding="utf-8"))["deaths"] == 2
    finally:
        game._shutdown()

    resumed = Game(save_path=path)
    try:
        assert resumed.checkpoints.continue_game() is not None
        assert resumed.deaths.total == 2
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_saves_from_before_the_counter_still_load() -> None:
    directory = tempfile.TemporaryDirectory()
    path = Path(directory.name) / "save.json"
    try:
        base = {
            "version": SAVE_VERSION,
            "checkpoint_id": "waterdeep_anchor",
            "sanity": 50,
            "progress_flags": [],
            "cigarettes": 4,
        }
        path.write_text(json.dumps(base), encoding="utf-8")
        assert SaveSystem(path).load() == SaveRecord(
            "waterdeep_anchor", 50, (), 4, 0)
        for forged in (-1, True, "3"):
            path.write_text(json.dumps({**base, "deaths": forged}),
                            encoding="utf-8")
            assert SaveSystem(path).load() is None, forged
    finally:
        directory.cleanup()


def test_the_hud_shows_a_skull_beside_the_cigarettes() -> None:
    """Top right, left of the cigarette count, and it changes with the total."""
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        region = (config.NATIVE_WIDTH - 110, 0, 110, 16)

        def corner() -> bytes:
            scene.draw(surface)
            crop = pygame.Surface(region[2:])
            crop.blit(surface, (0, 0), region)
            return pygame.image.tobytes(crop, "RGB")

        game.deaths.replace(0)
        first = corner()
        game.deaths.replace(88)
        assert corner() != first

        # The skull itself is in the frame, pixel for pixel.
        icon = death_icon()
        scene.draw(surface)
        bone = (226, 218, 196)
        found = any(
            surface.get_at((x, y))[:3] == bone
            for x in range(region[0], config.NATIVE_WIDTH)
            for y in range(0, 16)
        )
        assert found, "no bone-coloured pixels in the HUD corner"
        assert icon.get_width() > icon.get_height() > 8
    finally:
        game._shutdown()
        directory.cleanup()


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
    print("All death counter tests passed.")


if __name__ == "__main__":
    _run_all()
