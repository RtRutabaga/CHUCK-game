"""Boot scene: one-frame handoff into the title menu.

Responsibilities (for now):
    * Fill the screen with black while core systems finish initializing.
    * Hand off to the title menu on the first update.

This scene exists so the project runs on day one. It will eventually be
replaced (or repurposed) as the scene that loads assets and hands off to
the Waterdeep Docks world scene.
"""

from __future__ import annotations

import pygame

from src.core import config
from src.scenes.scene import Scene


class BootScene(Scene):
    """A one-frame black screen before the title menu."""

    def handle_event(self, event: pygame.event.Event) -> None:
        """Allow quitting with ESC while there is no pause menu."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: float) -> None:
        """Hand off to the title menu immediately."""
        from src.scenes.title_scene import TitleScene

        self.game.scenes.replace(TitleScene(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        """Paint it black."""
        surface.fill(config.COLOR_BLACK)
