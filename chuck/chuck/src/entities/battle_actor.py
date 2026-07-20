"""The final chamber's battle actors (session 131, tableau slice).

Chuck has wandered into someone else's climactic battle. The three
adventurers and the beholder stand as static presences for now — placed,
y-sorted, deliberately NON-interactive (they never respond to E; their
entrance lines play automatically, and Chuck cannot help them). Combat
behavior, attacks, and animation are the next slice. Do not explain who
they are: the phase contract forbids it.
"""

from __future__ import annotations

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

    def load_sprite(self, assets) -> None:
        self._image = assets.image(_SPRITES[self.kind])

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
        lift = _BEHOLDER_HOVER if self.kind == "beholder" else 0
        surface.blit(
            self._image,
            (int(self.x + self.width / 2 - fw / 2) - ox,
             int(foot_y - fh - lift) - oy),
        )
