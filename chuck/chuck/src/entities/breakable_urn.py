"""Scratchable temple urns that shatter into terracotta shards.

The temple's version of breakable grass: the dressed urns (map chars
'¦' against wall bases, '¢' on open floor) are living entities rather
than static props, and one scratch breaks them. Each conceals a full
cigarette carton — the temple's authored reward economy.

Breaking also clears the urn's map tile to its under-terrain via the
scene-supplied callback: a floor urn's tile opens up for walking, while
a wall-base urn's tile simply stays the solid wall it always was. The
carton drops on walkable ground either way (a wall urn spills onto the
floor tile beneath it). Map reload rebuilds every urn, matching the
established return-to-checkpoint lifecycle.
"""

from __future__ import annotations

import math
from typing import Callable

from src.core import config
from src.entities.entity import Entity


# Terracotta shards, matching the urn sprites' clay palette.
_FRAGMENTS = (
    (-11, -4, 2, 2, (139, 90, 58)),
    (-8, 7, 2, 1, (104, 66, 44)),
    (-4, -10, 1, 3, (166, 116, 76)),
    (3, -12, 2, 2, (139, 90, 58)),
    (8, -7, 1, 2, (104, 66, 44)),
    (12, 3, 2, 2, (166, 116, 76)),
    (6, 10, 2, 1, (139, 90, 58)),
    (-6, 11, 1, 2, (104, 66, 44)),
)

_SPRITES = (
    "objects/temple_urn_1.png",
    "objects/temple_urn_2.png",
    "objects/temple_urn_3.png",
)


class BreakableUrn(Entity):
    """One dressed temple urn; a scratch shatters it and spills a carton.

    Subclasses may restyle the vessel (FRAGMENTS shard palette and the
    sprite path) — the pantry's floor jars reuse this whole lifecycle.
    """

    FRAGMENTS = _FRAGMENTS

    def __init__(self, col: int, row: int, wall_mounted: bool,
                 on_break: Callable[[], None] | None = None) -> None:
        ts = config.TILE_SIZE
        center_x = col * ts + ts / 2
        bottom = (row + 1) * ts
        # Footprint: the urn's base, hugging its tile's bottom edge so a
        # scratch from the adjacent floor reaches it.
        super().__init__(center_x - 7, bottom - 14, 14, 14)
        self._center_x = center_x
        self._bottom = bottom
        # Same stable positional-variant formula as Prop, so the living
        # urn looks identical to the one the dressing pass placed.
        self._sprite_path = _SPRITES[(col * 31 + row * 17) % len(_SPRITES)]
        # A wall urn spills onto the floor tile beneath it; a floor urn
        # spills where it stood.
        drop_y = bottom + ts / 2 if wall_mounted else bottom - ts / 2
        self._drop = (center_x, drop_y)
        self._on_break = on_break
        self._image = None
        self.intact = True
        self._break_time = 0.0
        self._drop_pending = False

    EXAMINE_LINE = "examine_breakable_urn"

    @property
    def dialogue_id(self) -> str | None:
        return self.EXAMINE_LINE if self.intact else None

    def interaction_bounds(self) -> tuple[int, int, int, int]:
        """The footprint, padded a little, for the interact probe."""
        pad = 3
        return (int(self.x) - pad, int(self.y) - pad,
                int(self.width) + pad * 2, int(self.height) + pad * 2)

    def load_sprite(self, assets) -> None:
        self._image = assets.image(self._sprite_path)

    @property
    def hitbox(self):
        """Broken urns stop consuming later scratches during the debris."""
        if self.intact:
            return super().hitbox
        import pygame
        return pygame.Rect(0, 0, 0, 0)

    @property
    def sort_y(self) -> float:
        """Depth key: the tile's bottom edge, same rule as the old prop."""
        return float(self._bottom)

    def on_scratched(self) -> None:
        if not self.intact:
            return
        self.intact = False
        self._break_time = 0.0
        self._drop_pending = True
        if self._on_break is not None:
            self._on_break()

    def take_drop_position(self) -> tuple[float, float] | None:
        """Return the concealed carton position exactly once."""
        if not self._drop_pending:
            return None
        self._drop_pending = False
        return self._drop

    def create_pickup(self, drop: tuple[float, float], assets):
        """The reward this breakable conceals: a full carton."""
        from src.entities.pickup import CigaretteCarton

        pickup = CigaretteCarton(*drop)
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
        cx, bottom = self._center_x, self._bottom
        if self.intact:
            if self._image is not None:
                w, h = self._image.get_size()
                surface.blit(self._image,
                             (int(cx - w / 2) - ox, int(bottom - h) - oy))
            else:
                pygame.draw.rect(surface, (139, 90, 58),
                                 pygame.Rect(int(cx - 6) - ox,
                                             int(bottom - 14) - oy, 12, 14))
            return

        progress = min(1.0, self._break_time / config.BREAKABLE_GRASS_DURATION)
        cy = bottom - 8
        arc = math.sin(progress * math.pi) * 5.0
        for dx, dy, w, h, color in self.FRAGMENTS:
            x = int(cx + dx * progress - w / 2) - ox
            y = int(cy + dy * progress - arc - h / 2) - oy
            pygame.draw.rect(surface, color, pygame.Rect(x, y, w, h))
