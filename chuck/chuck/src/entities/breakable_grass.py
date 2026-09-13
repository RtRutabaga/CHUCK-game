"""Scratchable grass that briefly scatters into leaf fragments."""

from __future__ import annotations

import math

from src.core import config
from src.entities.entity import Entity


_FRAGMENTS = (
    (-12, -5, 2, 1, (139, 174, 57)),
    (-9, 8, 1, 3, (85, 127, 43)),
    (-5, -12, 2, 2, (169, 193, 68)),
    (4, -13, 1, 3, (104, 150, 48)),
    (9, -8, 2, 1, (153, 184, 61)),
    (13, 4, 1, 3, (79, 116, 40)),
    (7, 11, 2, 2, (124, 164, 51)),
    (-7, 12, 2, 1, (146, 178, 57)),
)


class BreakableGrass(Entity):
    """One walkable tuft; a scratch reveals its authored cigarette drop."""

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(center_x - 7, center_y - 7, 14, 14)
        self._center = (center_x, center_y)
        self._image = None
        self.intact = True
        self._break_time = 0.0
        self._drop_pending = False

    def load_sprite(self, assets) -> None:
        self._image = assets.image("objects/breakable_grass.png")

    @property
    def dialogue_id(self) -> str | None:
        """A hint while there is something to find; silence once scratched."""
        return "examine_breakable_grass" if self.intact else None

    def interaction_bounds(self) -> tuple[int, int, int, int]:
        """The footprint, padded a little, for the interact probe."""
        pad = 3
        return (int(self.x) - pad, int(self.y) - pad,
                int(self.width) + pad * 2, int(self.height) + pad * 2)


    @property
    def hitbox(self):
        """Broken grass stops consuming later scratches during its debris pass."""
        if self.intact:
            return super().hitbox
        import pygame
        return pygame.Rect(0, 0, 0, 0)

    def on_scratched(self) -> None:
        if not self.intact:
            return
        self.intact = False
        self._break_time = 0.0
        self._drop_pending = True

    def take_drop_position(self) -> tuple[float, float] | None:
        """Return the concealed cigarette position exactly once."""
        if not self._drop_pending:
            return None
        self._drop_pending = False
        return self._center

    def create_pickup(self, drop: tuple[float, float], assets):
        """The reward this breakable conceals: one cigarette."""
        from src.entities.pickup import Cigarette

        pickup = Cigarette(*drop)
        pickup.load_sprite(assets)
        return pickup

    def update(self, dt: float) -> None:
        if self.intact:
            return
        self._break_time += dt
        if self._break_time >= config.BREAKABLE_GRASS_DURATION:
            self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        cx, cy = self._center
        if self.intact:
            if self._image is not None:
                w, h = self._image.get_size()
                surface.blit(self._image, (int(cx - w / 2) - ox,
                                           int(cy + 8 - h) - oy))
            else:
                pygame.draw.rect(surface, (104, 150, 48),
                                 pygame.Rect(int(cx - 7) - ox,
                                             int(cy - 5) - oy, 14, 12))
            return

        progress = min(1.0, self._break_time / config.BREAKABLE_GRASS_DURATION)
        if progress < 0.16 and self._image is not None:
            w, h = self._image.get_size()
            jitter = -1 if int(progress * 100) % 2 else 1
            surface.blit(self._image, (int(cx - w / 2) + jitter - ox,
                                       int(cy + 8 - h) - oy))
        arc = math.sin(progress * math.pi) * 5.0
        for dx, dy, w, h, color in _FRAGMENTS:
            x = int(cx + dx * progress - w / 2) - ox
            y = int(cy + dy * progress - arc - h / 2) - oy
            pygame.draw.rect(surface, color, pygame.Rect(x, y, w, h))
