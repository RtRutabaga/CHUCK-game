"""Phlegethos flameskulls: fast, weaving, unkillable dodge hazards.

A flameskull hangs around a fixed haunt and darts back and forth across
it in a quick sine weave -- bee-like, never a pursuer. It cannot be
cleared with a scratch; it is a moving obstacle to be timed. Being a
floating skull it drifts over lava as happily as over stone, so it is at
its most dangerous along the molten edges.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity

if TYPE_CHECKING:
    from src.core.assets import AssetManager


class Flameskull(Entity):
    """A hovering hazard that weaves along one axis around its haunt."""

    damage = config.FLAMESKULL_SANITY_DAMAGE

    def __init__(self, center_x: float, center_y: float,
                 axis: str = "h", variant: str = "flameskull") -> None:
        if axis not in {"h", "v"}:
            raise ValueError(f"Unknown flameskull axis {axis!r}")
        # `variant` selects the sprite only: the Feywild's lantern moths
        # (Phase 9) are this exact hazard as living wildlife.
        self.variant = variant
        super().__init__(
            center_x - config.FLAMESKULL_HITBOX_W / 2,
            center_y - config.FLAMESKULL_HITBOX_H / 2,
            config.FLAMESKULL_HITBOX_W,
            config.FLAMESKULL_HITBOX_H,
        )
        self.axis = axis
        self.home = (center_x, center_y)
        # A deterministic phase so a group never moves in lockstep.
        self._t = ((int(center_x) * 7 + int(center_y) * 13) % 100) / 100.0
        self._image = None

    def load_sprites(self, assets: "AssetManager") -> None:
        self._image = assets.image(f"hazards/{self.variant}.png")

    def update(self, dt: float, _target=None) -> None:
        """Weave along the haunt axis, bobbing across it.

        Deliberately ignores terrain: a flameskull floats, so lava and
        the map's hazards are no obstacle to it (they are Chuck's
        problem, not the skull's).
        """
        self._t += dt
        travel = config.FLAMESKULL_SPEED / max(1.0, config.FLAMESKULL_RANGE)
        along = math.sin(self._t * travel) * config.FLAMESKULL_RANGE
        across = math.sin(self._t * travel * 3.1) * config.FLAMESKULL_WEAVE
        hx, hy = self.home
        if self.axis == "h":
            cx, cy = hx + along, hy + across
        else:
            cx, cy = hx + across, hy + along
        self.x = cx - self.width / 2
        self.y = cy - self.height / 2

    @property
    def sort_y(self) -> float:
        return self.y + self.height

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        # A guttering flame trail behind the skull sells the speed.
        cx = self.x + self.width / 2 - ox
        cy = self.y + self.height / 2 - oy
        for i in range(3):
            flicker = math.sin(self._t * 9.0 + i * 1.7)
            fx = round(cx + flicker * 2)
            fy = round(cy + 5 + i * 2)
            size = 3 - i
            colour = (
                ((198, 236, 255), (140, 196, 246), (96, 138, 208))
                if self.variant != "flameskull"
                else ((255, 196, 84), (240, 128, 34), (176, 58, 20))
            )[i]
            pygame.draw.rect(surface, colour, (fx - size // 2, fy, size, size))
        if self._image is None:
            pygame.draw.rect(surface, (226, 220, 198),
                             (int(self.x) - ox, int(self.y) - oy,
                              self.width, self.height))
            return
        fw, fh = self._image.get_size()
        surface.blit(self._image,
                     (int(cx - fw / 2), int(cy - fh / 2)))
