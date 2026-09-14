"""The end: a slow fade to black over the docks, and back to the title.

Pushed over the frozen WorldScene once Bobert has had his say, so the
last thing on screen is the place the game started -- Chuck by the
barrel -- going dark. No card, no credits; the fade is the ending.
"""

from __future__ import annotations

import pygame

from src.scenes.scene import Scene

FADE = 6.0    # seconds from the docks to black: slow
HOLD = 3.0    # seconds of black before the title


class EndingScene(Scene):
    """Fade the world beneath to black, hold, then return to the title."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.elapsed = 0.0
        self.finished = False

    def on_enter(self) -> None:
        self.game.audio.stop_music(fade_ms=int(FADE * 1000))

    @property
    def darkness(self) -> float:
        t = max(0.0, min(1.0, self.elapsed / FADE))
        return t * t * (3 - 2 * t)

    def update(self, dt: float) -> None:
        if self.finished:
            return
        self.elapsed += dt
        if self.elapsed >= FADE + HOLD:
            self.finished = True
            from src.scenes.title_scene import TitleScene
            scenes = self.game.scenes
            while scenes.current is not None:
                scenes.pop()
            scenes.push(TitleScene(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        veil = pygame.Surface(surface.get_size())
        veil.fill((0, 0, 0))
        veil.set_alpha(round(255 * self.darkness))
        surface.blit(veil, (0, 0))
