"""Simple city pedestrians that patrol one authored sidewalk segment.

The same walk covers somebody running for their life. A fleeing
pedestrian is a patrol at sprint speed on an authored segment, which
is what keeps the City Day 6 chase honest: the path was drawn safe, so
no amount of panic can run a businessperson into the Astral Sea.
"""

from __future__ import annotations

from src.core import config
from src.entities.npc import NPC
from src.world import collision


class PedestrianNPC(NPC):
    """An interactable NPC with a short, deterministic street patrol."""

    def __init__(self, center_x: float, center_y: float, npc_id: str,
                 dialogue_id: str, axis: str = "h",
                 patrol_range: float | None = None,
                 fleeing: bool = False) -> None:
        if axis not in {"h", "v"}:
            raise ValueError(f"Unknown pedestrian axis {axis!r}")
        super().__init__(center_x, center_y, npc_id, dialogue_id)
        self.axis = axis
        # Most pedestrians share one short beat. The woman in the red
        # dress is given a longer one, which is the whole of what makes
        # her a landmark rather than another commuter.
        self.patrol_range = (
            config.CITY_PEDESTRIAN_RANGE if patrol_range is None
            else patrol_range
        )
        self.fleeing = fleeing
        self.speed = (config.CITY_FLEEING_SPEED if fleeing
                      else config.CITY_PEDESTRIAN_SPEED)
        self.tilemap = None
        self._origin = self.x if axis == "h" else self.y
        self._direction = 1.0
        self.facing = "right" if axis == "h" else "down"

    def update(self, dt: float) -> None:
        if self.tilemap is None:
            return
        amount = self._direction * self.speed * dt
        dx, dy = (amount, 0.0) if self.axis == "h" else (0.0, amount)
        old = (self.x, self.y)
        self.x, self.y = collision.move_and_collide(
            self.x, self.y, self.width, self.height, dx, dy, self.tilemap,
            extra_solid_terrain=collision.FALL_HAZARD_TERRAIN,
        )
        coordinate = self.x if self.axis == "h" else self.y
        if (
            abs(coordinate - self._origin) >= self.patrol_range
            or (self.x, self.y) == old
        ):
            self._direction *= -1.0
        if self.axis == "h":
            self.facing = "right" if self._direction > 0 else "left"
        else:
            self.facing = "down" if self._direction > 0 else "up"
