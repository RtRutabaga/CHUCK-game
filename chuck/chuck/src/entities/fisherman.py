"""The man fishing from Waterdeep's south pier in the Phase 14 return."""

from __future__ import annotations

import math

from src.entities.npc import NPC


class FishermanNPC(NPC):
    """A dock worker silhouette with a small, readable fishing idle."""

    def __init__(self, center_x: float, center_y: float) -> None:
        super().__init__(
            center_x, center_y,
            npc_id="fisherman", dialogue_id="fisherman",
        )
        self.facing = "right"
        self._idle_t = 0.0
        self._return_to_water = 0.0

    def load_sprites(self, assets) -> None:
        """Use the established dock-worker scale and clothes."""
        import pygame

        row = assets.sheet("npcs/dock_worker.png", 16, 30)[0]
        down, up, left = row
        self._frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": pygame.transform.flip(left, True, False),
        }

    def interact(self, by) -> str:
        dialogue = super().interact(by)
        self._return_to_water = 0.8
        return dialogue

    def update(self, dt: float) -> None:
        self._idle_t += dt
        if self._return_to_water > 0.0:
            self._return_to_water = max(0.0, self._return_to_water - dt)
            if self._return_to_water == 0.0:
                self.facing = "right"

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        super().draw(surface, camera_offset)
        if self.facing != "right":
            return

        import pygame

        ox, oy = camera_offset
        hand_x = round(self.x + self.width / 2 + 4) - ox
        hand_y = round(self.y + self.height - 15) - oy
        lift = round(math.sin(self._idle_t * 1.7))
        tip = (hand_x + 19, hand_y - 8 + lift)
        bobber = (tip[0] + 10, hand_y + 6 + lift)
        pygame.draw.line(surface, (104, 72, 42), (hand_x, hand_y), tip)
        pygame.draw.line(surface, (176, 184, 176), tip, bobber)
        pygame.draw.rect(surface, (188, 54, 44), (*bobber, 2, 2))
