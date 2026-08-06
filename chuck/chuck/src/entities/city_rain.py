"""Low-cost screen-space rain for the modern-city arrival."""

from __future__ import annotations

import pygame

from src.core import config


class CityRain:
    """Deterministic pixel rain shared by the arrival scene and city map."""

    def __init__(self) -> None:
        self.elapsed = 0.0
        self.drops = tuple(
            (
                (index * 47 + 19) % (config.NATIVE_WIDTH + 48) - 24,
                (index * 83 + 11) % (config.NATIVE_HEIGHT + 34) - 17,
                86 + (index * 13) % 45,
                4 + index % 4,
            )
            for index in range(46)
        )

    def update(self, dt: float) -> None:
        self.elapsed += max(0.0, dt)

    def draw(self, surface: pygame.Surface, *, alpha: int = 145) -> None:
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for x, y, speed, length in self.drops:
            travel = config.NATIVE_HEIGHT + 42
            draw_y = round((y + self.elapsed * speed) % travel) - 21
            draw_x = round((x - self.elapsed * speed * 0.16) % 368) - 24
            pygame.draw.line(
                layer, (154, 198, 225, alpha),
                (draw_x, draw_y), (draw_x - 1, draw_y + length), 1,
            )
        surface.blit(layer, (0, 0))
