"""Ordinary sewer rats: small, stubborn tutorial enemies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.core.animation import Animation
from src.entities.entity import Entity

if TYPE_CHECKING:
    from src.core.assets import AssetManager


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

    def configure_patrol(self, tilemap, blocked_spawn_tiles=()) -> None:
        """Enable a short horizontal patrol only when both sides are safe."""
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

    def load_sprites(self, assets: "AssetManager") -> None:
        frames = assets.sheet(
            config.RAT_SHEET, config.RAT_FRAME_W, config.RAT_FRAME_H
        )[0]
        self._idle = Animation(frames, 0.28)

    def update(self, dt: float) -> None:
        if self._idle is not None:
            self._idle.update(dt)
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
