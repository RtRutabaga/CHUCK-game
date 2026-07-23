"""Animated pirate NPCs with durable first/repeat conversations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.entities.npc import NPC

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.systems.checkpoints import ProgressState


class PirateNPC(NPC):
    """A rhythmically animated pirate who remembers meeting Chuck.

    The progress flag is intentionally supplied by authored content. Future
    important pirates can reuse this entity without putting dialogue or story
    switches into WorldScene.
    """

    def __init__(
        self,
        center_x: float,
        center_y: float,
        npc_id: str,
        progress: "ProgressState",
        progress_flag: str,
    ) -> None:
        super().__init__(
            center_x, center_y, npc_id=npc_id,
            dialogue_id=f"{npc_id}_first",
        )
        self.progress = progress
        self.progress_flag = progress_flag
        self.first_dialogue_id = f"{npc_id}_first"
        self.repeat_dialogue_id = f"{npc_id}_repeat"
        self._animated_frames: dict[str, tuple[object, object]] = {}
        self._anim_t = 0.0

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        frames = assets.sheet(
            f"npcs/{self.npc_id}.png",
            config.NPC_FRAME_W,
            config.NPC_FRAME_H,
        )[0]
        down = (frames[0], frames[1])
        up = (frames[2], frames[3])
        left = (frames[4], frames[5])
        self._animated_frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": tuple(pygame.transform.flip(frame, True, False)
                           for frame in left),
        }

    def update(self, dt: float) -> None:
        self._anim_t += dt

    def interact(self, by) -> str:
        self.face_toward(by)
        if self.progress.has(self.progress_flag):
            return self.repeat_dialogue_id
        self.progress.enable(self.progress_flag)
        return self.first_dialogue_id

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset
        frames = self._animated_frames.get(self.facing)
        if frames is None:
            return super().draw(surface, camera_offset)
        # A relaxed half-beat sway: readable motion, not tavern-cartoon bustle.
        frame = frames[int(self._anim_t / 0.38) % 2]
        fw, fh = frame.get_size()
        surface.blit(
            frame,
            (int(self.x + self.width / 2 - fw / 2) - ox,
             int(self.y + self.height - fh) - oy),
        )
