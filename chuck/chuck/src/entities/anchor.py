"""Astral Anchor — Chuck's checkpoint, standing in the world.

Responsibilities:
    * Sit on its tile. When Chuck touches it, the WorldScene marks it
      as the active respawn point (via AstralAnchorSystem) and it
      lights up. Touching it again does nothing dramatic. Nothing here
      is dramatic. That is the point.

Visual (placeholder rects until real art): a small dark post holding a
pale star-shard that glows brighter once attuned.
"""

from __future__ import annotations

from src.core import config
from src.entities.entity import Entity

_W, _H = 8, 6  # footprint: generous, so touching it is easy


class AstralAnchor(Entity):
    """A quiet piece of the Astral Sea, moored to a dock."""

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            center_x - _W / 2, center_y - _H / 2, width=_W, height=_H
        )
        self.lit = False  # True while this is the active anchor
        self._frames = None  # (dim, lit) set by load_sprites()

    def load_sprites(self, assets) -> None:
        """Slice the 2-frame sheet: cold ashtray | live ember."""
        row = assets.sheet("objects/astral_anchor.png", 12, 10)[0]
        self._frames = (row[0], row[1])

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        if self._frames is not None:
            frame = self._frames[1] if self.lit else self._frames[0]
            fw, fh = frame.get_size()
            surface.blit(
                frame,
                (int(self.x + self.width / 2 - fw / 2) - ox,
                 int(self.y + self.height - fh) - oy),
            )
            return
        x, y = int(self.x) - ox, int(self.y) - oy
        color = config.COLOR_ANCHOR_LIT if self.lit else config.COLOR_ANCHOR_DIM
        # Post (2x4) rising from the footprint's center...
        pygame.draw.rect(
            surface, (60, 58, 70), pygame.Rect(x + 3, y - 2, 2, _H + 2)
        )
        # ...holding the star-shard (4x4) above it.
        pygame.draw.rect(surface, color, pygame.Rect(x + 2, y - 6, 4, 4))
        if self.lit:  # a single bright core pixel. That's all.
            pygame.draw.rect(
                surface, config.COLOR_STAR, pygame.Rect(x + 3, y - 5, 2, 2)
            )
