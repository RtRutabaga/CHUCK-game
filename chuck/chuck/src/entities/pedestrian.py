"""Simple city pedestrians that patrol one authored sidewalk segment."""

from __future__ import annotations

from src.core import config
from src.entities.npc import NPC
from src.world import collision


class PedestrianNPC(NPC):
    """An interactable NPC with a short, deterministic street patrol."""

    def __init__(self, center_x: float, center_y: float, npc_id: str,
                 dialogue_id: str, axis: str = "h") -> None:
        if axis not in {"h", "v"}:
            raise ValueError(f"Unknown pedestrian axis {axis!r}")
        super().__init__(center_x, center_y, npc_id, dialogue_id)
        self.axis = axis
        self.tilemap = None
        self._origin = self.x if axis == "h" else self.y
        self._direction = 1.0
        self.facing = "right" if axis == "h" else "down"

    def update(self, dt: float) -> None:
        if self.tilemap is None:
            return
        amount = self._direction * config.CITY_PEDESTRIAN_SPEED * dt
        dx, dy = (amount, 0.0) if self.axis == "h" else (0.0, amount)
        old = (self.x, self.y)
        self.x, self.y = collision.move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, self.tilemap,
            extra_solid_terrain=collision.FALL_HAZARD_TERRAIN,
        )
        coordinate = self.x if self.axis == "h" else self.y
        if (
            abs(coordinate - self._origin) >= config.CITY_PEDESTRIAN_RANGE
            or (self.x, self.y) == old
        ):
            self._direction *= -1.0
        if self.axis == "h":
            self.facing = "right" if self._direction > 0 else "left"
        else:
            self.facing = "down" if self._direction > 0 else "up"
