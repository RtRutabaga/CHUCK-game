"""The ship's cook: a human-scale, cleaver-carrying pursuit hazard."""

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


class PirateChef(Entity):
    """Notice Chuck once, then chase him through the galley.

    The chef is deliberately not a scratch target. This room is an escape
    encounter, not another enemy-clearing exercise.
    """

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            center_x - config.NPC_HITBOX_W / 2,
            center_y - config.NPC_HITBOX_H / 2,
            config.NPC_HITBOX_W,
            config.NPC_HITBOX_H,
        )
        self.speed = config.PIRATE_CHEF_SPEED
        self.damage = config.PIRATE_CHEF_SANITY_DAMAGE
        self.notice_range = config.PIRATE_CHEF_NOTICE_RANGE
        self.pursuing = False
        self.facing = "down"
        self.tilemap: "TileMap | None" = None
        self._frames: dict[str, tuple[object, object]] = {}
        self._anim_t = 0.0

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        frames = assets.sheet(
            "hazards/pirate_chef.png",
            config.NPC_FRAME_W,
            config.NPC_FRAME_H,
        )[0]
        down = (frames[0], frames[1])
        up = (frames[2], frames[3])
        left = (frames[4], frames[5])
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": tuple(pygame.transform.flip(frame, True, False)
                           for frame in left),
        }

    def can_notice(self, target: "Player") -> bool:
        dx = (target.x + target.width / 2) - (self.x + self.width / 2)
        dy = (target.y + target.height / 2) - (self.y + self.height / 2)
        return math.hypot(dx, dy) <= self.notice_range

    def face_toward(self, target: "Player") -> None:
        dx = (target.x + target.width / 2) - (self.x + self.width / 2)
        dy = (target.y + target.height / 2) - (self.y + self.height / 2)
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"

    def begin_pursuit(self) -> None:
        self.pursuing = True

    def update(self, dt: float, target: "Player | None" = None) -> None:
        if not self.pursuing or target is None or self.tilemap is None:
            return
        dx = (target.x + target.width / 2) - (self.x + self.width / 2)
        dy = (target.y + target.height / 2) - (self.y + self.height / 2)
        distance = math.hypot(dx, dy)
        if distance <= 0.0:
            return
        self.face_toward(target)
        step = self.speed * dt / distance
        old = (self.x, self.y)
        self.x, self.y = collision.move_and_collide(
            self.x, self.y, self.width, self.height,
            dx * step, dy * step, self.tilemap,
            extra_solid_terrain=collision.FALL_HAZARD_TERRAIN,
        )
        if (self.x, self.y) != old:
            self._anim_t += dt

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frames = self._frames.get(self.facing)
        if frames:
            frame = frames[int(self._anim_t / 0.16) % 2]
            fw, fh = frame.get_size()
            surface.blit(
                frame,
                (int(self.x + self.width / 2 - fw / 2) - ox,
                 int(self.y + self.height - fh) - oy),
            )
        else:
            pygame.draw.rect(
                surface, (184, 176, 142),
                (int(self.x) - ox, int(self.y) - 22 - oy, 12, 30),
            )
