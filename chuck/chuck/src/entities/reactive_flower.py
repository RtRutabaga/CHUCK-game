"""Scratch-activated Feywild flowers that request authored route changes."""

from __future__ import annotations

import math
from collections.abc import Callable

from src.core import config
from src.entities.entity import Entity


class ReactiveFlower(Entity):
    """One map-local switch flower; the controller owns its tile mutations."""

    def __init__(
        self,
        center_x: float,
        center_y: float,
        group_id: str,
        trigger: Callable[[], bool],
    ) -> None:
        super().__init__(center_x - 7, center_y - 6, 14, 12)
        self.group_id = group_id
        self._center = (center_x, center_y)
        self._trigger = trigger
        self._images: tuple[object, object] = ()
        self._active = False
        self._pulse_t = 0.0

    def load_sprites(self, assets) -> None:
        self._images = (
            assets.image("objects/feywild_reactive_flower_closed.png"),
            assets.image("objects/feywild_reactive_flower_open.png"),
        )

    def on_scratched(self) -> None:
        if self._trigger():
            self._pulse_t = config.REACTIVE_FLOWER_CHANGE_DELAY

    def set_active(self, active: bool) -> None:
        self._active = active

    def reset(self) -> None:
        self._active = False
        self._pulse_t = 0.0

    def update(self, dt: float) -> None:
        self._pulse_t = max(0.0, self._pulse_t - dt)

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        cx, cy = self._center
        image = self._images[1 if self._active else 0] if self._images else None
        shake = 0
        if self._pulse_t > 0.0:
            progress = 1.0 - self._pulse_t / config.REACTIVE_FLOWER_CHANGE_DELAY
            shake = round(math.sin(progress * math.pi * 8.0))
        if image is not None:
            width, height = image.get_size()
            surface.blit(
                image,
                (
                    round(cx - width / 2) + shake - ox,
                    round(cy + 7 - height) - oy,
                ),
            )
            return
        color = (240, 104, 195) if not self._active else (83, 229, 206)
        pygame.draw.circle(
            surface,
            color,
            (round(cx) + shake - ox, round(cy) - 5 - oy),
            6,
        )
        pygame.draw.line(
            surface,
            (46, 145, 78),
            (round(cx) - ox, round(cy) - oy),
            (round(cx) - ox, round(cy) + 7 - oy),
            2,
        )
