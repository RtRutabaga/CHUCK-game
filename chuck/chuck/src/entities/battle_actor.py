"""Non-interactive actors in the game's larger battles.

Chuck has wandered into someone else's climactic battle. The three
adventurers and their opponent hold their ground — placed, y-sorted,
and deliberately NON-interactive. Their entrance lines play automatically,
and Chuck cannot help them. Each actor moves in place when its selected
choreographer fires an attack.
"""

from __future__ import annotations

import math

from src.core import config
from src.entities import sword
from src.entities.entity import Entity

_SPRITES = {
    "fighter": "npcs/fighter.png",
    "wizard": "npcs/wizard.png",
    "ranger": "npcs/ranger.png",
    "beholder": "npcs/beholder.png",
    "pit_fiend": "npcs/pit_fiend.png",
}

# The beholder floats: its sprite draws lifted above its ground shadow.
_BEHOLDER_HOVER = 10

# Where the fighter's sword hand is on his 16x30 sprite, facing west.
_FIGHTER_HAND = (12, 15)


class BattleActor(Entity):
    """One scripted combatant, standing its ground in the tableau."""

    def __init__(self, center_x: float, center_y: float, kind: str) -> None:
        if kind not in _SPRITES:
            raise ValueError(f"Unknown battle actor {kind!r}")
        self.kind = kind
        if kind == "beholder":
            width, height = 24, 12
        elif kind == "pit_fiend":
            # A broad planted footprint supports the fortress tableau's
            # enormous 128px silhouette without changing its authored marker
            # or turning the non-interactive battle into collision geometry.
            width, height = 64, 32
        else:
            width, height = 12, 8
        super().__init__(center_x - width / 2, center_y - height / 2,
                         width, height)
        self._image = None
        # Deterministic per-actor phase so the tableau never moves in
        # lockstep; attack_flash is set by the BattleChoreographer.
        self._time = (sum(map(ord, kind)) % 100) / 100.0 * math.tau
        self.attack_flash = 0.0
        self.spin = 0.0  # radians; the ranger whirls as she looses arrows
        # The fighter's sword. Every stroke a choreographer calls starts a
        # swing, and the swing lasts longer than the attack flash does,
        # because a cut over in a fifth of a second is never seen.
        # swing_dir is -1 for a cut to the west, +1 east; he faces it.
        self.swing_dir = -1
        self.swing_t = 0.0
        self._flash_seen = 0.0

    def load_sprite(self, assets) -> None:
        self._image = assets.image(_SPRITES[self.kind])

    def update(self, dt: float) -> None:
        self._time += dt
        if self.kind == "fighter":
            self.swing_t = max(0.0, self.swing_t - dt)
            if self.attack_flash > self._flash_seen:
                self.swing_t = sword.SWING_DURATION
        self.attack_flash = max(0.0, self.attack_flash - dt)
        self._flash_seen = self.attack_flash

    def swing_toward(self, target_x: float) -> None:
        """Face the thing about to be cut."""
        self.swing_dir = 1 if target_x > self.center_x else -1

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
        if self.kind in {"beholder", "pit_fiend"}:
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
        elif self.kind == "pit_fiend":
            # The Pit Fiend is planted and immense; attacks only tense the
            # silhouette rather than making it skitter like a small actor.
            lift = round(0.5 + 0.5 * math.sin(self._time * 1.7))
            lunge = 1 if self.attack_flash > 0.0 else 0
        else:
            # A subtle in-place sway; attacks lunge west at the beholder.
            lift = round(0.5 + 0.5 * math.sin(self._time * 3.1))
            lunge = -2 if self.attack_flash > 0.0 else 0
        image = self._image
        if self.kind == "fighter":
            lunge = 2 * self.swing_dir if self.attack_flash > 0.0 else 0
            if self.swing_dir > 0:
                image = pygame.transform.flip(image, True, False)
        if self.spin:
            # The whirling archer: spin the sprite about its own center,
            # keeping the body over the same spot on the floor.
            image = pygame.transform.rotate(image, math.degrees(self.spin))
        iw, ih = image.get_size()
        # Center the (possibly rotated) image where the upright sprite's
        # center would sit, so rotation pivots in place.
        center_x = self.x + self.width / 2 + lunge
        center_y = foot_y - fh / 2 - lift
        left = int(center_x - iw / 2) - ox
        top = int(center_y - ih / 2) - oy
        surface.blit(image, (left, top))
        if self.kind == "fighter":
            self._draw_sword(surface, left, top, iw)

    def _draw_sword(self, surface, left: int, top: int, width: int) -> None:
        hand_x, hand_y = _FIGHTER_HAND
        if self.swing_dir > 0:
            hand_x = width - 1 - hand_x
        hilt = (left + hand_x, top + hand_y)
        toward = "right" if self.swing_dir > 0 else "left"
        _rest, start, end = sword.cut_angles(toward)
        # His shield is toward the enemy and his sword hand is behind it,
        # so at rest the blade stands up on the far side of him rather
        # than across his face.
        rest = sword.cut_angles("left" if toward == "right" else "right")[0]
        if self.swing_t > 0.0:
            progress = 1.0 - self.swing_t / sword.SWING_DURATION
            angle = sword.swing_angle(progress, start, end)
            sword.draw_trail(surface, hilt, start, angle)
        else:
            angle = rest
        sword.draw_sword(surface, hilt, angle)
