"""The four stationary, seated light-formed entities in the Cabin."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.entities.npc import NPC

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.systems.checkpoints import ProgressState


FRAME_W = 28
FRAME_H = 30
FRAME_TIME = 0.34


class CabinLightEntity(NPC):
    """A non-hostile seated silhouette whose conversation is durable."""

    def __init__(
        self,
        center_x: float,
        center_y: float,
        *,
        dialogue_id: str,
        progress: "ProgressState",
        progress_flag: str,
        phase_index: int,
        seat_sort_y: float,
        facing: str = "south",
    ) -> None:
        super().__init__(
            center_x,
            center_y,
            npc_id="cabin_light_entity",
            dialogue_id=dialogue_id,
            sort_y_override=seat_sort_y,
        )
        self.progress = progress
        self.progress_flag = progress_flag
        self.facing = facing
        self._frames: tuple[object, ...] = ()
        self._animation_t = phase_index * FRAME_TIME

    def load_sprites(self, assets: "AssetManager") -> None:
        rows = assets.sheet(
            "npcs/cabin_light_entity.png", FRAME_W, FRAME_H
        )
        row = 1 if self.facing == "west" else 0
        self._frames = tuple(rows[row])

    def update(self, dt: float) -> None:
        self._animation_t += dt

    def interact(self, by) -> str:
        # They remain seated and still; talking changes state, not posture.
        self.progress.enable(self.progress_flag)
        return self.dialogue_id

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        if not self._frames:
            return
        ox, oy = camera_offset
        frame = self._frames[
            int(self._animation_t / FRAME_TIME) % len(self._frames)
        ]
        fw, fh = frame.get_size()
        surface.blit(
            frame,
            (
                int(self.x + self.width / 2 - fw / 2) - ox,
                int(self.y + self.height - fh) - oy,
            ),
        )
