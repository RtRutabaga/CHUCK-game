"""A massive, deliberately slow Chultan dinosaur."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.entities.player import Player
    from src.world.tilemap import TileMap


class MassiveDinosaur(Entity):
    """A towering pursuer whose threat comes from scale, not speed."""

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            center_x - config.DINOSAUR_HITBOX_W / 2,
            center_y - config.DINOSAUR_HITBOX_H / 2,
            config.DINOSAUR_HITBOX_W,
            config.DINOSAUR_HITBOX_H,
        )
        self.speed = config.DINOSAUR_SPEED
        self.damage = config.DINOSAUR_SANITY_DAMAGE
        self.max_scratches = config.DINOSAUR_SCRATCHES
        self.scratches_remaining = self.max_scratches
        self.facing = "down"
        self.moving = False
        self.tilemap: "TileMap | None" = None
        self._frames: dict[str, tuple[object, object]] = {}
        self._step_time = 0.0

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        rows = assets.sheet(
            "hazards/massive_dinosaur.png",
            config.DINOSAUR_FRAME_W,
            config.DINOSAUR_FRAME_H,
        )
        down = (rows[0][0], rows[1][0])
        up = (rows[0][1], rows[1][1])
        left = (rows[0][2], rows[1][2])
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": tuple(pygame.transform.flip(frame, True, False)
                           for frame in left),
        }

    def update(self, dt: float, target: "Player | None" = None) -> None:
        self.moving = False
        if target is None or self.tilemap is None:
            return
        dx = (target.x + target.width / 2) - (self.x + self.width / 2)
        dy = (target.y + target.height / 2) - (self.y + self.height / 2)
        distance = math.hypot(dx, dy)
        if distance <= 0.0 or distance > config.DINOSAUR_NOTICE_RANGE:
            return
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"
        step = self.speed * dt / distance
        old_position = (self.x, self.y)
        self.x, self.y = collision.move_and_collide(
            self.x, self.y, self.width, self.height,
            dx * step, dy * step, self.tilemap,
            extra_solid_terrain=collision.FALL_HAZARD_TERRAIN,
        )
        self.moving = (self.x, self.y) != old_position
        if self.moving:
            self._step_time += dt

    def on_scratched(self) -> None:
        self.scratches_remaining -= 1
        if self.scratches_remaining <= 0:
            self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frames = self._frames.get(self.facing)
        if frames is not None:
            index = int(self._step_time / config.DINOSAUR_FRAME_DURATION) % 2
            frame = frames[index if self.moving else 0]
            fw, fh = frame.get_size()
            surface.blit(
                frame,
                (int(self.x + self.width / 2 - fw / 2) - ox,
                 int(self.y + self.height - fh) - oy),
            )
        else:
            pygame.draw.rect(
                surface, (45, 95, 52),
                (int(self.x) - ox, int(self.y) - 34 - oy,
                 self.width, self.height + 34),
            )
