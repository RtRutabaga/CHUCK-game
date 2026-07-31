"""Feywild spitting orchids and their hard seed projectiles.

Orchids are rooted, cardinal launchers. Their deterministic cadence and
visible petal swell turn each authored lane into a timing problem rather
than an aiming or pursuit problem.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity
from src.world import collision

if TYPE_CHECKING:
    from src.core.assets import AssetManager


_VECTORS = {
    "up": (0.0, -1.0),
    "down": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
}


class OrchidSeed(Entity):
    """One hard seed that breaks against solid terrain."""

    damage = config.ORCHID_SEED_SANITY_DAMAGE

    def __init__(
        self, center_x: float, center_y: float, direction: str,
    ) -> None:
        if direction not in _VECTORS:
            raise ValueError(f"Unknown orchid-seed direction {direction!r}")
        horizontal = direction in {"left", "right"}
        width = (
            config.ORCHID_SEED_HITBOX_LONG
            if horizontal else config.ORCHID_SEED_HITBOX_SHORT
        )
        height = (
            config.ORCHID_SEED_HITBOX_SHORT
            if horizontal else config.ORCHID_SEED_HITBOX_LONG
        )
        super().__init__(
            center_x - width / 2, center_y - height / 2, width, height
        )
        self.direction = direction

    def update(self, dt: float, tilemap) -> None:
        vx, vy = _VECTORS[self.direction]
        dx = vx * config.ORCHID_SEED_SPEED * dt
        dy = vy * config.ORCHID_SEED_SPEED * dt
        target_x, target_y = self.x + dx, self.y + dy
        new_x, new_y = collision.move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, tilemap
        )
        self.x, self.y = new_x, new_y
        if abs(new_x - target_x) > 1e-4 or abs(new_y - target_y) > 1e-4:
            self.alive = False

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        rect = pygame.Rect(
            round(self.x) - ox, round(self.y) - oy, self.width, self.height
        )
        pygame.draw.rect(surface, (118, 65, 139), rect)
        vx, vy = _VECTORS[self.direction]
        tip_x = round(self.hitbox.centerx + vx * self.width / 2) - ox
        tip_y = round(self.hitbox.centery + vy * self.height / 2) - oy
        pygame.draw.rect(
            surface, (226, 156, 232), (tip_x - 1, tip_y - 1, 2, 2)
        )


class SpittingOrchid(Entity):
    """A rooted launcher with a readable three-stage wind-up."""

    def __init__(
        self, center_x: float, center_y: float, direction: str,
    ) -> None:
        if direction not in _VECTORS:
            raise ValueError(f"Unknown spitting-orchid direction {direction!r}")
        super().__init__(
            center_x - config.ORCHID_HITBOX_W / 2,
            center_y - config.ORCHID_HITBOX_H / 2,
            config.ORCHID_HITBOX_W,
            config.ORCHID_HITBOX_H,
        )
        self.direction = direction
        self.facing = direction
        col = int(center_x // config.TILE_SIZE)
        row = int(center_y // config.TILE_SIZE)
        # Four evenly spaced cadence slots make small authored groups legible
        # and keep their shots from collapsing into near-simultaneous volleys.
        stagger = ((col + row * 3) % 4) / 4.0
        self._time_until_shot = (
            0.65 + stagger * config.ORCHID_SHOT_INTERVAL
        )
        self._frames: dict[str, tuple[object, object, object]] = {}

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        rows = assets.sheet(
            "hazards/spitting_orchid.png",
            config.ORCHID_FRAME_W,
            config.ORCHID_FRAME_H,
        )
        self._frames = {
            "down": tuple(row[0] for row in rows),
            "up": tuple(row[1] for row in rows),
            "left": tuple(row[2] for row in rows),
            "right": tuple(
                pygame.transform.flip(row[2], True, False) for row in rows
            ),
        }

    @property
    def windup_stage(self) -> int:
        if self._time_until_shot <= config.ORCHID_FLASH_TIME:
            return 2
        if self._time_until_shot <= config.ORCHID_WINDUP_TIME:
            return 1
        return 0

    def update(self, dt: float) -> "OrchidSeed | None":
        self._time_until_shot -= dt
        if self._time_until_shot > 0.0:
            return None
        while self._time_until_shot <= 0.0:
            self._time_until_shot += config.ORCHID_SHOT_INTERVAL
        vx, vy = _VECTORS[self.direction]
        offset = config.TILE_SIZE / 2 + config.ORCHID_SEED_HITBOX_LONG / 2
        return OrchidSeed(
            self.hitbox.centerx + vx * offset,
            self.hitbox.centery + vy * offset,
            self.direction,
        )

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        frames = self._frames.get(self.facing)
        if frames is None:
            color = (
                (218, 92, 201)
                if self.windup_stage else (135, 70, 150)
            )
            pygame.draw.rect(
                surface, color,
                (
                    int(self.x) - 4 - ox, int(self.y) - 14 - oy,
                    self.width + 8, self.height + 14,
                ),
            )
            return
        frame = frames[self.windup_stage]
        fw, fh = frame.get_size()
        surface.blit(
            frame,
            (
                int(self.x + self.width / 2 - fw / 2) - ox,
                int(self.y + self.height - fh) - oy,
            ),
        )
