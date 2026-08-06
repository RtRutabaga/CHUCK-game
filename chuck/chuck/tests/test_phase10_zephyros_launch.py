"""Phase 10's tower throw and horizontal flight between worlds."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.zephyros_launch_cutscene_scene import (
    ASTRAL_START,
    CITY_START,
    COLLISION_TIME,
    CUTSCENE_END,
    DESCENT_START,
    MUSIC_START,
    TOWER_SHOT_END,
    ZephyrosLaunchCutsceneScene,
)


def _scene(game, sanity=60):
    scene = ZephyrosLaunchCutsceneScene(game, sanity=sanity)
    game.scenes.replace(scene)
    return scene


def test_throw_uses_distant_whole_tower_scale_and_tiny_chuck() -> None:
    game = Game()
    try:
        scene = _scene(game)
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        scene.elapsed = 1.5
        assert scene.phase == "tower_throw"
        scene.draw(surface)
        # The tower is complete in frame; Chuck is represented by exactly the
        # tiny purple dot appropriate to this distant scale.
        purple = (101, 62, 145)
        assert sum(
            surface.get_at((x, y))[:3] == purple
            for y in range(config.NATIVE_HEIGHT)
            for x in range(config.NATIVE_WIDTH)
        ) == 4
    finally:
        game._shutdown()


def test_flight_begins_horizontal_then_gradually_descends() -> None:
    game = Game()
    try:
        scene = _scene(game)
        scene.elapsed = TOWER_SHOT_END
        first = scene.chuck_position()
        scene.elapsed = TOWER_SHOT_END + 2.2
        settled = scene.chuck_position()
        assert settled[0] > first[0] + 100
        assert abs(settled[1] - first[1]) <= 3

        scene.elapsed = DESCENT_START
        descent_start = scene.chuck_position()
        scene.elapsed = COLLISION_TIME
        collision = scene.chuck_position()
        assert collision[0] == descent_start[0]
        assert collision[1] >= descent_start[1] + 45
    finally:
        game._shutdown()


def test_astral_then_city_fragments_accumulate_in_the_same_sky() -> None:
    game = Game()
    try:
        scene = _scene(game)
        assert scene.visible_fragment_kinds == set()
        scene.elapsed = ASTRAL_START
        assert scene.visible_fragment_kinds == {"astral"}
        scene.elapsed = CITY_START + 5.1
        assert scene.visible_fragment_kinds == {
            "astral", "office", "concrete"
        }
        # Exact shared fall-hazard art: two variants by three frames.
        assert len(scene._astral_frames) == 6
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        scene.draw(surface)
    finally:
        game._shutdown()


def test_launch_reuses_falling_music_after_a_soft_gap() -> None:
    game = Game()
    try:
        stopped = []
        played = []
        game.audio.stop_music = lambda fade_ms=0: stopped.append(fade_ms)
        game.audio.play_music = lambda filename, loop=True: played.append(
            (filename, loop)
        )
        scene = ZephyrosLaunchCutsceneScene(game, sanity=51)
        scene.on_enter()
        assert stopped == [650]
        scene.update(MUSIC_START - 0.1)
        assert played == []
        scene.update(0.2)
        assert played == [("fall_to_chult.wav", False)]
        scene.update(10.0)
        assert played == [("fall_to_chult.wav", False)]
    finally:
        game._shutdown()


def test_collision_is_a_stable_input_free_boundary_before_rainy_descent() -> None:
    game = Game()
    try:
        scene = _scene(game, sanity=44)
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        scene.elapsed = COLLISION_TIME
        assert scene.phase == "city_fragment_collision"
        scene.draw(surface)
        scene.update(CUTSCENE_END)
        assert scene.complete
        assert game.scenes.current is scene
        scene.update(30.0)
        assert game.scenes.current is scene

        before = scene.elapsed
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f))
        assert scene.elapsed == before
        assert game.scenes.current is scene
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
    print("All Phase 10 Zephyros launch tests passed.")


if __name__ == "__main__":
    _run_all()
