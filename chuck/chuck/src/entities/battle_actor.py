"""The final chamber's battle actors (sessions 131-132).

Chuck has wandered into someone else's climactic battle. The three
adventurers and the beholder hold their ground — placed, y-sorted,
deliberately NON-interactive (they never respond to E; their entrance
lines play automatically, and Chuck cannot help them). Session 132 set
them in motion in place: the beholder's hover breathes, and each actor
lunges toward its target for a beat when the BattleChoreographer fires
its attack. Do not explain who they are: the phase contract forbids it.
"""

from __future__ import annotations

import math

from src.core import config
from src.entities.entity import Entity

_SPRITES = {
    "fighter": "npcs/fighter.png",
    "wizard": "npcs/wizard.png",
    "ranger": "npcs/ranger.png",
    "beholder": "npcs/beholder.png",
}

# The beholder floats: its sprite draws lifted above its ground shadow.
_BEHOLDER_HOVER = 10


class BattleActor(Entity):
    """One scripted combatant, standing its ground in the tableau."""

    def __init__(self, center_x: float, center_y: float, kind: str) -> None:
        if kind not in _SPRITES:
            raise ValueError(f"Unknown battle actor {kind!r}")
        self.kind = kind
        width, height = (24, 12) if kind == "beholder" else (12, 8)
        super().__init__(center_x - width / 2, center_y - height / 2,
                         width, height)
        self._image = None
        # Deterministic per-actor phase so the tableau never moves in
        # lockstep; attack_flash is set by the BattleChoreographer.
        self._time = (sum(map(ord, kind)) % 100) / 100.0 * math.tau
        self.attack_flash = 0.0
        self.spin = 0.0  # radians; the ranger whirls as she looses arrows

    def load_sprite(self, assets) -> None:
        self._image = assets.image(_SPRITES[self.kind])

    def update(self, dt: float) -> None:
        self._time += dt
        self.attack_flash = max(0.0, self.attack_flash - dt)

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    @property
    def sort_y(self) -> float:
        return self.y + self.height

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        foot_y = self.y + self.height
        if self.kind == "beholder":
            # A soft ground shadow beneath the floating tyrant.
            shadow = pygame.Rect(int(self.x) - ox,
                                 int(foot_y - 3) - oy,
                                 self.width, 3)
            pygame.draw.ellipse(surface, (20, 24, 22), shadow)
        if self._image is None:
            pygame.draw.rect(
                surface, (128, 84, 118),
                pygame.Rect(int(self.x) - ox, int(self.y) - oy,
                            self.width, self.height))
            return
        fw, fh = self._image.get_size()
        if self.kind == "beholder":
            # The hover breathes; a firing beat pushes the orb east.
            lift = _BEHOLDER_HOVER + round(2 * math.sin(self._time * 2.2))
            lunge = 2 if self.attack_flash > 0.0 else 0
        else:
            # A subtle in-place sway; attacks lunge west at the beholder.
            lift = round(0.5 + 0.5 * math.sin(self._time * 3.1))
            lunge = -2 if self.attack_flash > 0.0 else 0
        image = self._image
        if self.spin:
            # The whirling archer: spin the sprite about its own center,
            # keeping the body over the same spot on the floor.
            image = pygame.transform.rotate(image, math.degrees(self.spin))
        iw, ih = image.get_size()
        # Center the (possibly rotated) image where the upright sprite's
        # center would sit, so rotation pivots in place.
        center_x = self.x + self.width / 2 + lunge
        center_y = foot_y - fh / 2 - lift
        surface.blit(
            image,
            (int(center_x - iw / 2) - ox, int(center_y - ih / 2) - oy),
        )
