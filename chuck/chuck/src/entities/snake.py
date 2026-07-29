"""Small one-hit temple snakes for the dedicated snake chamber."""

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


class TempleSnake(Entity):
    """A low, readable pursuer that disappears after one scratch.

    `variant` selects the sprite sheet only: Phlegethos fire snakes
    (Phase 8) are this exact gameplay in molten colours.
    """

    def __init__(self, center_x: float, center_y: float,
                 variant: str = "snake") -> None:
        super().__init__(
            center_x - config.SNAKE_HITBOX_W / 2,
            center_y - config.SNAKE_HITBOX_H / 2,
            config.SNAKE_HITBOX_W,
            config.SNAKE_HITBOX_H,
        )
        self.variant = variant
        self.speed = config.SNAKE_SPEED
        self.damage = config.SNAKE_SANITY_DAMAGE
        self.max_scratches = 1
        self.scratches_remaining = 1
        self.facing = "down"
        self.tilemap: "TileMap | None" = None
        self._frames: dict[str, object] = {}

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        down, up, left = assets.sheet(
            f"hazards/{self.variant}.png",
            config.SNAKE_FRAME_W,
            config.SNAKE_FRAME_H,
        )[0]
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": pygame.transform.flip(left, True, False),
        }

    def update(self, dt: float, target: "Player | None" = None) -> None:
        if target is None or self.tilemap is None:
            return
        dx = (target.x + target.width / 2) - (self.x + self.width / 2)
        dy = (target.y + target.height / 2) - (self.y + self.height / 2)
        distance = math.hypot(dx, dy)
        if distance <= 0.0 or distance > config.SNAKE_NOTICE_RANGE:
            return
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"
        step = self.speed * dt / distance
        self.x, self.y = collision.move_and_collide(
            self.x, self.y, self.width, self.height,
            dx * step, dy * step, self.tilemap,
            extra_solid_terrain=collision.FALL_HAZARD_TERRAIN,
        )

    def on_scratched(self) -> None:
        self.scratches_remaining = 0
        self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frame = self._frames.get(self.facing)
        if frame is not None:
            fw, fh = frame.get_size()
            surface.blit(
                frame,
                (int(self.x + self.width / 2 - fw / 2) - ox,
                 int(self.y + self.height - fh) - oy),
            )
        else:
            pygame.draw.rect(
                surface, (84, 126, 54),
                (int(self.x) - ox, int(self.y) - oy,
                 self.width, self.height),
            )
