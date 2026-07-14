"""Boot scene: the foundation's placeholder.

Responsibilities (for now):
    * Fill the screen with black.
    * Quit cleanly on ESC.

This scene exists so the project runs on day one. It will eventually be
replaced (or repurposed) as the scene that loads assets and hands off to
the Waterdeep Docks world scene.
"""

from __future__ import annotations

import pygame

from src.core import config
from src.scenes.scene import Scene


class BootScene(Scene):
    """A black screen with a working game loop behind it."""

    def handle_event(self, event: pygame.event.Event) -> None:
        """Allow quitting with ESC while there is no pause menu."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: float) -> None:
        """Hand off to the world immediately.

        TODO: When real assets exist, load them here (possibly with a
              brief title card) before the handoff.
        """
        from src.scenes.world_scene import WorldScene

        self.game.scenes.replace(WorldScene(self.game))

    def draw(self, surface: pygame.Surface) -> None:
        """Paint it black."""
        surface.fill(config.COLOR_BLACK)
