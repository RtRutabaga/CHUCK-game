"""Reusable temple wall launchers and their moving dart projectiles."""

from __future__ import annotations

from src.core import config
from src.entities.entity import Entity
from src.world import collision


_VECTORS = {
    "up": (0.0, -1.0),
    "down": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
}


class TempleDart(Entity):
    """A single fast projectile that disappears against solid masonry."""

    damage = config.DART_SANITY_DAMAGE

    def __init__(self, center_x: float, center_y: float, direction: str) -> None:
        if direction not in _VECTORS:
            raise ValueError(f"Unknown dart direction {direction!r}")
        horizontal = direction in {"left", "right"}
        width = config.DART_HITBOX_LONG if horizontal else config.DART_HITBOX_SHORT
        height = config.DART_HITBOX_SHORT if horizontal else config.DART_HITBOX_LONG
        super().__init__(center_x - width / 2, center_y - height / 2,
                         width, height)
        self.direction = direction

    def update(self, dt: float, tilemap) -> None:
        vx, vy = _VECTORS[self.direction]
        dx = vx * config.DART_SPEED * dt
        dy = vy * config.DART_SPEED * dt
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
        pygame.draw.rect(surface, (207, 194, 139), rect)
        vx, vy = _VECTORS[self.direction]
        tip_x = round(self.x + self.width / 2 + vx * self.width / 2) - ox
        tip_y = round(self.y + self.height / 2 + vy * self.height / 2) - oy
        pygame.draw.rect(surface, (246, 221, 150), (tip_x, tip_y, 1, 1))


class DartTrap:
    """An invisible controller anchored to a visible wall-aperture tile."""

    def __init__(self, center_x: float, center_y: float, direction: str) -> None:
        if direction not in _VECTORS:
            raise ValueError(f"Unknown dart direction {direction!r}")
        self.center_x = center_x
        self.center_y = center_y
        self.direction = direction
        col = int(center_x // config.TILE_SIZE)
        row = int(center_y // config.TILE_SIZE)
        stagger = ((col * 17 + row * 31) % 100) / 100.0
        self._time_until_fire = 0.35 + stagger * config.DART_INTERVAL

    def update(self, dt: float) -> TempleDart | None:
        self._time_until_fire -= dt
        if self._time_until_fire > 0.0:
            return None
        while self._time_until_fire <= 0.0:
            self._time_until_fire += config.DART_INTERVAL
        vx, vy = _VECTORS[self.direction]
        offset = config.TILE_SIZE / 2 + config.DART_HITBOX_LONG / 2
        return TempleDart(
            self.center_x + vx * offset,
            self.center_y + vy * offset,
            self.direction,
        )
