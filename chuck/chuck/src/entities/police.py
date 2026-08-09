"""Police officers: the spined devil's lane, with a warning first.

An officer holds a fixed position and fires down one authored direction.
The projectile is the devil's own -- same travel, same "stops dead
against solid geometry" rule -- retuned to a faster, smaller bullet.

What is new is the tell. The devil fires on a bare cadence; an officer
raises his weapon for most of a second first, with a muzzle flash on the
shot itself, so a lane can always be read before it is live. That is the
difference between a hazard to route around and an ambush.

One officer on the final map has stopped aiming at anything: he spins
and fires wide, which is the Beholder fight's whirling archer standing
in a street. His rounds fall short by design, so he is a disc to walk
around rather than a lane to time.

Chuck never gains a ranged attack of his own. These are scenery with
consequences.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity
from src.entities.spined_devil import _VECTORS, FlamingSpine
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager


class Bullet(FlamingSpine):
    """One round: the devil's spine, faster and smaller."""

    damage = config.BULLET_SANITY_DAMAGE
    speed = config.BULLET_SPEED

    def __init__(self, center_x: float, center_y: float,
                 direction: str) -> None:
        super().__init__(center_x, center_y, direction)
        horizontal = direction in {"left", "right"}
        width = (config.BULLET_HITBOX_LONG if horizontal
                 else config.BULLET_HITBOX_SHORT)
        height = (config.BULLET_HITBOX_SHORT if horizontal
                  else config.BULLET_HITBOX_LONG)
        self.x += (self.width - width) / 2
        self.y += (self.height - height) / 2
        self.width, self.height = width, height

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        pygame.draw.rect(surface, (246, 226, 148),
                         (round(self.x) - ox, round(self.y) - oy,
                          self.width, self.height))


class SpinBullet(Bullet):
    """A round fired at a free angle, and it falls short.

    The lane officers get their readability from the aim tell. This one
    has no lane to tell, so it is bounded instead: the rounds die at
    `SPIN_BULLET_RANGE`, which turns the spinning officer into a disc on
    the floor to walk around rather than a map-wide denial.
    """

    def __init__(self, center_x: float, center_y: float,
                 angle: float) -> None:
        super().__init__(center_x, center_y, "right")
        size = config.BULLET_HITBOX_SHORT + 1
        self.x = center_x - size / 2
        self.y = center_y - size / 2
        self.width = self.height = size
        self.angle = angle
        self._ux, self._uy = math.cos(angle), math.sin(angle)
        self._travel_left = config.SPIN_BULLET_RANGE

    def update(self, dt: float, tilemap) -> None:
        dx = self._ux * self.speed * dt
        dy = self._uy * self.speed * dt
        target_x, target_y = self.x + dx, self.y + dy
        self.x, self.y = collision.move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, tilemap
        )
        if (abs(self.x - target_x) > 1e-4 or abs(self.y - target_y) > 1e-4):
            self.alive = False
        self._travel_left -= math.hypot(dx, dy)
        if self._travel_left <= 0.0:
            self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        pygame.draw.circle(
            surface, (246, 226, 148),
            (round(self.x + self.width / 2) - ox,
             round(self.y + self.height / 2) - oy), 2)


class PoliceOfficer(Entity):
    """A stationary shooter with a readable aim before every shot."""

    damage = config.POLICE_CONTACT_DAMAGE

    def __init__(self, center_x: float, center_y: float,
                 direction: str) -> None:
        if direction not in _VECTORS:
            raise ValueError(f"Unknown police direction {direction!r}")
        super().__init__(
            center_x - config.POLICE_HITBOX_W / 2,
            center_y - config.POLICE_HITBOX_H / 2,
            config.POLICE_HITBOX_W,
            config.POLICE_HITBOX_H,
        )
        self.direction = direction
        self.facing = direction
        # The same deterministic stagger the devils use, so a line of
        # officers never fires in unison.
        col = int(center_x // config.TILE_SIZE)
        row = int(center_y // config.TILE_SIZE)
        stagger = ((col * 23 + row * 11) % 100) / 100.0
        self._until_shot = 0.6 + stagger * config.POLICE_INTERVAL
        self._flash_t = 0.0
        self._frames: dict[str, object] = {}

    @property
    def aiming(self) -> bool:
        """True while the weapon is up and the lane is about to go live."""
        return 0.0 < self._until_shot <= config.POLICE_AIM_SECONDS

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        down, up, left = assets.sheet(
            "hazards/police.png",
            config.POLICE_FRAME_W,
            config.POLICE_FRAME_H,
        )[0]
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": pygame.transform.flip(left, True, False),
        }

    def update(self, dt: float) -> "Bullet | None":
        """Tick the aim-and-fire cadence; returns a bullet on the shot."""
        self._flash_t = max(0.0, self._flash_t - dt)
        self._until_shot -= dt
        if self._until_shot > 0.0:
            return None
        while self._until_shot <= 0.0:
            self._until_shot += config.POLICE_INTERVAL
        self._flash_t = 0.08
        vx, vy = _VECTORS[self.direction]
        offset = config.TILE_SIZE / 2 + config.BULLET_HITBOX_LONG
        return Bullet(
            self.x + self.width / 2 + vx * offset,
            self.y + self.height / 2 + vy * offset,
            self.direction,
        )

    @property
    def sort_y(self) -> float:
        return self.y + self.height

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frame = self._frames.get(self.facing)
        if frame is not None:
            width, height = frame.get_size()
            surface.blit(frame, (
                round(self.x + self.width / 2 - width / 2) - ox,
                round(self.y + self.height - height) - oy,
            ))
        else:
            pygame.draw.rect(surface, (38, 48, 84),
                             (round(self.x) - ox, round(self.y) - oy,
                              self.width, self.height))

        vx, vy = _VECTORS[self.direction]
        muzzle_x = round(self.x + self.width / 2 + vx * 10) - ox
        muzzle_y = round(self.y + self.height / 2 + vy * 10) - oy - 8
        if self._flash_t > 0.0:
            pygame.draw.circle(surface, (255, 236, 158),
                               (muzzle_x, muzzle_y), 3)
        elif self.aiming:
            # The tell: a short bright bead along the lane about to fire.
            pygame.draw.line(
                surface, (236, 96, 84),
                (muzzle_x, muzzle_y),
                (muzzle_x + round(vx * 7), muzzle_y + round(vy * 7)), 2,
            )


class SpinningPoliceOfficer(PoliceOfficer):
    """The officer who lost the plot: whirls on the spot, firing wide.

    This is the Beholder fight's whirling archer brought into the world
    -- the body spins about its own centre and the aim advances a fixed
    step between rounds, so the spray sweeps rather than tracks. He is
    shooting at a dinosaur and hitting everything else, which is the
    whole joke, and Chuck is not exempt.
    """

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(center_x, center_y, "down")
        self.spin = 0.0
        self._aim = 0.0
        self._until_shot = config.POLICE_SPIN_INTERVAL

    @property
    def aiming(self) -> bool:
        """Never: the spin itself is the tell, and it never stops."""
        return False

    def update(self, dt: float) -> "SpinBullet | None":
        self.spin = (self.spin + config.POLICE_SPIN_SPEED * dt) % math.tau
        self._flash_t = max(0.0, self._flash_t - dt)
        self._until_shot -= dt
        if self._until_shot > 0.0:
            return None
        while self._until_shot <= 0.0:
            self._until_shot += config.POLICE_SPIN_INTERVAL
        self._aim = (self._aim + config.POLICE_SPIN_STEP) % math.tau
        self._flash_t = 0.06
        offset = config.TILE_SIZE / 2
        return SpinBullet(
            self.x + self.width / 2 + math.cos(self._aim) * offset,
            self.y + self.height / 2 + math.sin(self._aim) * offset,
            self._aim,
        )

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frame = self._frames.get("down")
        if frame is None:
            super().draw(surface, camera_offset)
            return
        # Spin about the sprite's own centre so the boots stay put.
        _fw, fh = frame.get_size()
        image = pygame.transform.rotate(frame, math.degrees(self.spin))
        iw, ih = image.get_size()
        center_x = self.x + self.width / 2
        center_y = self.y + self.height - fh / 2
        surface.blit(image, (round(center_x - iw / 2) - ox,
                             round(center_y - ih / 2) - oy))
        if self._flash_t > 0.0:
            pygame.draw.circle(
                surface, (255, 236, 158),
                (round(center_x + math.cos(self._aim) * 10) - ox,
                 round(center_y + math.sin(self._aim) * 10) - oy), 3)
