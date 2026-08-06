"""Deterministic modern-city traffic lanes and their vehicles."""

from __future__ import annotations

import math

from src.core import config
from src.entities.entity import Entity


_VECTORS = {
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
    "up": (0.0, -1.0),
    "down": (0.0, 1.0),
}
ROAD_TERRAIN = frozenset({"=", "▦"})


class TrafficVehicle(Entity):
    """One fast, non-combat road hazard owned by a fixed traffic lane."""

    damage = config.TRAFFIC_SANITY_DAMAGE

    def __init__(
        self, center_x: float, center_y: float, direction: str, variant: int,
    ) -> None:
        if direction not in _VECTORS:
            raise ValueError(f"Unknown traffic direction {direction!r}")
        horizontal = direction in {"left", "right"}
        width = (
            config.TRAFFIC_HITBOX_LONG
            if horizontal else config.TRAFFIC_HITBOX_SHORT
        )
        height = (
            config.TRAFFIC_HITBOX_SHORT
            if horizontal else config.TRAFFIC_HITBOX_LONG
        )
        super().__init__(center_x - width / 2, center_y - height / 2,
                         width, height)
        self.direction = direction
        self.variant = variant % 4
        self._image = None

    @property
    def center(self) -> tuple[float, float]:
        return self.x + self.width / 2, self.y + self.height / 2

    def set_center(self, center_x: float, center_y: float) -> None:
        self.x = center_x - self.width / 2
        self.y = center_y - self.height / 2

    def load_sprites(self, assets) -> None:
        base = assets.sheet("hazards/city_traffic.png", 40, 20)[0][self.variant]
        import pygame

        if self.direction == "left":
            self._image = pygame.transform.flip(base, True, False)
        elif self.direction == "right":
            self._image = base
        elif self.direction == "up":
            self._image = pygame.transform.rotate(base, 90)
        else:
            self._image = pygame.transform.rotate(base, -90)

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        import pygame

        ox, oy = camera_offset
        center_x, center_y = self.center
        if self._image is None:
            pygame.draw.rect(
                surface, (156, 53, 58),
                (round(self.x) - ox, round(self.y) - oy,
                 self.width, self.height),
            )
            return
        width, height = self._image.get_size()
        surface.blit(
            self._image,
            (round(center_x - width / 2) - ox,
             round(center_y - height / 2) - oy),
        )


class TrafficLane:
    """A fixed-size, wrapping traffic pattern that never accumulates cars."""

    def __init__(
        self,
        center_x: float,
        center_y: float,
        direction: str,
        phase: int,
        world_width: float,
        world_height: float,
    ) -> None:
        if direction not in _VECTORS:
            raise ValueError(f"Unknown traffic direction {direction!r}")
        self.center_x = center_x
        self.center_y = center_y
        self.direction = direction
        self.phase = phase
        self.world_width = world_width
        self.world_height = world_height
        self.horizontal = direction in {"left", "right"}
        axis_length = world_width if self.horizontal else world_height
        self._minimum = -config.TRAFFIC_MARGIN
        self._maximum = axis_length + config.TRAFFIC_MARGIN
        self._span = self._maximum - self._minimum
        count = max(1, math.ceil(self._span / config.TRAFFIC_SPACING))
        self.vehicles = [
            TrafficVehicle(center_x, center_y, direction, phase + index)
            for index in range(count)
        ]
        self.reset()

    def load_sprites(self, assets) -> None:
        for vehicle in self.vehicles:
            vehicle.load_sprites(assets)

    def reset(self) -> None:
        phase_offset = (self.phase * config.TRAFFIC_SPACING / 2) % self._span
        for index, vehicle in enumerate(self.vehicles):
            axis = self._minimum + (
                index * config.TRAFFIC_SPACING + phase_offset
            ) % self._span
            if self.horizontal:
                vehicle.set_center(axis, self.center_y)
            else:
                vehicle.set_center(self.center_x, axis)

    def update(self, dt: float) -> None:
        vector_x, vector_y = _VECTORS[self.direction]
        distance = config.TRAFFIC_SPEED * dt
        for vehicle in self.vehicles:
            center_x, center_y = vehicle.center
            center_x += vector_x * distance
            center_y += vector_y * distance
            axis = center_x if self.horizontal else center_y
            while axis > self._maximum:
                axis -= self._span
            while axis < self._minimum:
                axis += self._span
            if self.horizontal:
                vehicle.set_center(axis, self.center_y)
            else:
                vehicle.set_center(self.center_x, axis)
