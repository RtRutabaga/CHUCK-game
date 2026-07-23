"""Ordinary rats: small sewer patrols and aggressive ship-hold pursuers."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from src.core import config
from src.core.animation import Animation
from src.entities.entity import Entity
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.entities.player import Player
    from src.world.tilemap import TileMap


class SewerRat(Entity):
    """A mundane rat, visibly smaller than Chuck and defeated in one hit."""

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            center_x - config.RAT_HITBOX_W / 2,
            center_y - config.RAT_HITBOX_H / 2,
            config.RAT_HITBOX_W,
            config.RAT_HITBOX_H,
        )
        self.damage = config.RAT_SANITY_DAMAGE
        self._idle: Animation | None = None
        self._spawn_x = self.x
        self._patrol_direction = 1.0
        self.patrolling = False
        self.attack_chase_enabled = False
        self.tilemap: "TileMap | None" = None

    def configure_patrol(self, tilemap, blocked_spawn_tiles=()) -> None:
        """Enable a short horizontal patrol only when both sides are safe."""
        self.attack_chase_enabled = False
        self.tilemap = None
        ts = config.TILE_SIZE
        col = int((self.x + self.width / 2) // ts)
        row = int((self.y + self.height / 2) // ts)
        blocked = set(blocked_spawn_tiles)

        def safe(neighbor_col: int) -> bool:
            tile = (neighbor_col, row)
            return (
                tile not in blocked
                and not tilemap.is_solid(*tile)
                and tilemap.terrain_at(*tile) != "V"
            )

        self.patrolling = safe(col - 1) and safe(col + 1)

    def configure_attack_chase(self, tilemap: "TileMap") -> None:
        """Use the temple snakes' notice-and-pursue behavior in combat rooms."""
        self.tilemap = tilemap
        self.patrolling = False
        self.attack_chase_enabled = True

    def load_sprites(self, assets: "AssetManager") -> None:
        frames = assets.sheet(
            config.RAT_SHEET, config.RAT_FRAME_W, config.RAT_FRAME_H
        )[0]
        self._idle = Animation(frames, 0.28)

    def update(self, dt: float, target: "Player | None" = None) -> None:
        if self._idle is not None:
            self._idle.update(dt)
        if self.attack_chase_enabled:
            self._update_attack_chase(dt, target)
            return
        if not self.patrolling:
            return
        self.x += self._patrol_direction * config.RAT_PATROL_SPEED * dt
        left = self._spawn_x - config.RAT_PATROL_RANGE
        right = self._spawn_x + config.RAT_PATROL_RANGE
        if self.x <= left:
            self.x = left
            self._patrol_direction = 1.0
        elif self.x >= right:
            self.x = right
            self._patrol_direction = -1.0

    def _update_attack_chase(
        self,
        dt: float,
        target: "Player | None",
    ) -> None:
        if target is None or self.tilemap is None:
            return
        dx = (target.x + target.width / 2) - (self.x + self.width / 2)
        dy = (target.y + target.height / 2) - (self.y + self.height / 2)
        distance = math.hypot(dx, dy)
        if distance <= 0.0 or distance > config.HOLD_RAT_NOTICE_RANGE:
            return
        step = config.HOLD_RAT_CHASE_SPEED * dt / distance
        self.x, self.y = collision.move_and_collide(
            self.x,
            self.y,
            self.width,
            self.height,
            dx * step,
            dy * step,
            self.tilemap,
            extra_solid_terrain=collision.FALL_HAZARD_TERRAIN,
        )

    def on_scratched(self) -> None:
        """One scratch, one rat. Later enemies may be stronger."""
        self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        if self._idle is not None:
            frame = self._idle.current_frame
            fw, fh = frame.get_size()
            surface.blit(
                frame,
                (int(self.x + self.width / 2 - fw / 2) - ox,
                 int(self.y + self.height - fh) - oy),
            )
        else:
            pygame.draw.rect(
                surface, (118, 112, 106),
                pygame.Rect(int(self.x) - ox, int(self.y) - oy,
                            self.width, self.height),
            )
