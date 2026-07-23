"""The escape cutscene — the Phase 6 -> 7 boundary (session 140).

A contained, input-free scene: Chuck crawls the tight stone passage
toward a growing daylight, a whiteout, then he emerges into the wooden
hold whose hull is set with portholes onto the sunlit sea. It plays out
wordlessly before handing off to the playable ship deck, carrying his
Sanity across.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes import escape_cutscene_scene
from src.scenes.escape_cutscene_scene import EscapeCutsceneScene, FADE_END


def test_the_escape_is_wordless() -> None:
    # The narration captions were removed: the escape shows, never tells.
    assert not hasattr(escape_cutscene_scene, "_CAPTIONS")


def test_porthole_waves_use_lines_without_white_glitter_dots() -> None:
    game = Game()
    try:
        scene = EscapeCutsceneScene(game)
        surface = pygame.Surface((64, 64))
        surface.fill((0, 0, 0))
        for elapsed in (0.0, 1.0, 2.5):
            scene.elapsed = elapsed
            scene._draw_porthole(surface, 32, 32, 22)
            assert not any(
                surface.get_at((x, y))[:3] == (255, 255, 255)
                for y in range(10, 54)
                for x in range(10, 54)
            )
    finally:
        game._shutdown()


def test_the_cutscene_is_input_free_and_draws_every_phase() -> None:
    game = Game()
    try:
        scene = EscapeCutsceneScene(game, sanity=50)
        game.scenes.replace(scene)
        scene.on_enter()
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        # Draw across the crawl, the whiteout, the reveal, and the hold
        # (all before the fade hands off) without error.
        for target in (2.0, 5.3, 7.0, 10.0):
            while scene.elapsed < target:
                scene.update(0.05)
            scene.draw(surface)  # must not raise
        # It never spontaneously left before the fade completed.
        assert game.scenes.current is scene
    finally:
        game._shutdown()


def test_it_hands_off_to_the_ship_deck_preserving_sanity() -> None:
    game = Game()
    try:
        scene = EscapeCutsceneScene(game, sanity=37)
        game.scenes.replace(scene)
        scene.on_enter()
        handed_off = False
        for _ in range(int((FADE_END + 1.0) / 0.05)):
            scene.update(0.05)
            if game.scenes.current is not scene:
                handed_off = True
                break
        assert handed_off
        deck = game.scenes.current
        assert deck.map_name == "ship_deck"
        assert game.active_checkpoint_id == "ship_deck"
        assert deck.sanity.current == 37
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
    print("All escape cutscene tests passed.")


if __name__ == "__main__":
    _run_all()
