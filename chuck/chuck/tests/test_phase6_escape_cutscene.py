"""The escape cutscene — the Phase 6 -> 7 boundary (session 140).

A contained, input-free scene: Chuck crawls the tight stone passage
toward a growing daylight, a whiteout, then he emerges into the wooden
hold with the open sea beyond the hull breach. Three quiet narration
lines land the moment before it hands off to the playable ship deck,
carrying his Sanity across.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.escape_cutscene_scene import (
    EscapeCutsceneScene, FADE_END, _CAPTIONS,
)


def test_the_captions_land_the_moment_and_all_render() -> None:
    from src.ui.bitmap_font import GLYPH_ORDER

    lines = [line for _t, line in _CAPTIONS]
    assert len(lines) == 3
    assert "ship" in lines[-1].lower()  # the phase-ending beat
    for line in lines:
        assert set(line) <= set(GLYPH_ORDER), line


def test_the_cutscene_is_input_free_and_draws_every_phase() -> None:
    game = Game()
    try:
        scene = EscapeCutsceneScene(game, sanity=50)
        game.scenes.replace(scene)
        scene.on_enter()
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        # Draw across the crawl, the whiteout, and the reveal without error.
        for target in (2.0, 5.3, 7.0, 9.5, 13.9):
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
