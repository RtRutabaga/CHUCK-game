"""Phase 11 city raccoon: a short, mid-strength pursuit encounter."""

from __future__ import annotations

import math

from src.core import config
from src.entities.entity import Entity
from src.world import collision


class Raccoon(Entity):
    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            center_x - config.RACCOON_HITBOX_W / 2,
            center_y - config.RACCOON_HITBOX_H / 2,
            config.RACCOON_HITBOX_W,
            config.RACCOON_HITBOX_H,
        )
        self.damage = config.RACCOON_SANITY_DAMAGE
        self.max_scratches = config.RACCOON_SCRATCHES
        self.scratches_remaining = self.max_scratches
        self.tilemap = None
        self.facing = "down"
        self._frames: dict[str, object] = {}

    def load_sprites(self, assets) -> None:
        import pygame

        down, up, left = assets.sheet(
            "hazards/raccoon.png",
            config.RACCOON_FRAME_W,
            config.RACCOON_FRAME_H,
        )[0]
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": pygame.transform.flip(left, True, False),
        }

    def update(self, dt: float, target=None) -> None:
        if target is None or self.tilemap is None:
            return
        dx = (target.x + target.width / 2) - (self.x + self.width / 2)
        dy = (target.y + target.height / 2) - (self.y + self.height / 2)
        distance = math.hypot(dx, dy)
        if distance <= 0.0 or distance > config.RACCOON_NOTICE_RANGE:
            return
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"
        step = config.RACCOON_SPEED * dt / distance
        self.x, self.y = collision.move_and_collide(
            self.x, self.y, self.width, self.height,
            dx * step, dy * step, self.tilemap,
            extra_solid_terrain=collision.FALL_HAZARD_TERRAIN,
        )

    def on_scratched(self) -> None:
        self.scratches_remaining -= 1
        if self.scratches_remaining <= 0:
            self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frame = self._frames.get(self.facing)
        if frame is not None:
            fw, fh = frame.get_size()
            surface.blit(frame, (
                int(self.x + self.width / 2 - fw / 2) - ox,
                int(self.y + self.height - fh) - oy,
            ))
        else:
            pygame.draw.rect(surface, (77, 82, 88), (
                int(self.x) - ox, int(self.y) - oy, self.width, self.height,
            ))
