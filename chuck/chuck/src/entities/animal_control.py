"""Animal Control officers: the zombie's role, plus a net.

Everything about how an officer takes damage, deals it on contact, and
walks toward Chuck is the undead pursuer's behaviour, inherited whole.
The one thing that is new is the reason to fear them at close range: a
net on a long stick that pins Chuck where he stands.
"""

from __future__ import annotations

import math

from src.core import config
from src.entities.undead import UndeadEnemy


class AnimalControlOfficer(UndeadEnemy):
    """A pursuer who ends the chase by throwing a net rather than biting."""

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(center_x, center_y, "animal_control")
        # A short wind-up before each throw, so a caught rat has always
        # had a moment to see the net coming.
        self._wind_up = 0.0
        # Set for exactly one frame, when the wind-up completes with Chuck
        # still in reach. The scene consumes it; nothing else re-arms.
        self.net_thrown = False

    @property
    def winding_up(self) -> bool:
        return self._wind_up > 0.0

    def update(self, dt: float, target=None) -> None:
        super().update(dt, target)
        self.net_thrown = False
        if target is None:
            self._wind_up = 0.0
            return
        if self._wind_up > 0.0:
            self._wind_up = max(0.0, self._wind_up - dt)
            if self._wind_up == 0.0:
                self.net_thrown = self.in_net_range(target)
        elif self.in_net_range(target):
            self._wind_up = config.NET_WIND_UP_SECONDS

    def in_net_range(self, target) -> bool:
        """The net is a close-range tool; it does not reach across a road."""
        dx = (target.x + target.width / 2) - (self.x + self.width / 2)
        dy = (target.y + target.height / 2) - (self.y + self.height / 2)
        return math.hypot(dx, dy) <= config.NET_RANGE

    def net_ready(self, target) -> bool:
        """True on the single frame the wind-up completed on Chuck."""
        return self.net_thrown and self.in_net_range(target)

    def reset_net(self) -> None:
        self._wind_up = 0.0
        self.net_thrown = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        super().draw(surface, camera_offset)
        if self._wind_up <= 0.0:
            return
        # The tell: the net rises over the officer's head before it comes
        # down. Drawn above the sprite so it reads even in a crowd.
        ox, oy = camera_offset
        cx = int(self.x + self.width / 2) - ox
        top = int(self.y) - oy - 12
        pygame.draw.line(surface, (86, 74, 58), (cx, top + 10), (cx, top), 2)
        pygame.draw.ellipse(surface, (206, 214, 220), (cx - 7, top - 5, 14, 9), 1)
        for offset in (-4, 0, 4):
            pygame.draw.line(surface, (176, 186, 196),
                             (cx + offset, top - 4), (cx + offset, top + 3))
