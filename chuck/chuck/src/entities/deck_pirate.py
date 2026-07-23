"""Rhythmic non-combat pirates for the exterior ship deck."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.entities.pirate_npc import PirateNPC

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.systems.checkpoints import ProgressState


SHANTY_BPM = 126.0
FRAMES_PER_BEAT = 2
ANIMATION_FRAMES = 4
_PHASE_OFFSETS = {
    "concertina": 0,
    "cheer": 2,
    "dance": 1,
    "struggle": 0,
    "captain": 0,
}
_DRAW_LIFTS = {
    # Jeffries' authored marker remains on the safe interaction tile below
    # the solid mast base, while his whole struggling figure is tied visibly
    # against the exposed pole rather than standing at its foot.
    "struggle": 24,
}


class DeckPirateNPC(PirateNPC):
    """One four-frame deck performance locked to the shanty's beat."""

    def __init__(
        self,
        center_x: float,
        center_y: float,
        npc_id: str,
        progress: "ProgressState",
        progress_flag: str,
        performance: str,
    ) -> None:
        if performance not in _PHASE_OFFSETS:
            raise ValueError(f"Unknown deck-pirate performance {performance!r}")
        super().__init__(
            center_x, center_y, npc_id,
            progress=progress, progress_flag=progress_flag,
        )
        self.performance = performance
        self._deck_frames: dict[str, tuple[object, ...]] = {}

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        frames = assets.sheet(
            f"npcs/{self.npc_id}.png",
            config.NPC_FRAME_W,
            config.NPC_FRAME_H,
        )[0]
        if len(frames) != ANIMATION_FRAMES * 3:
            raise ValueError(
                f"{self.npc_id} needs 12 deck-animation frames, got "
                f"{len(frames)}"
            )
        down = tuple(frames[0:4])
        up = tuple(frames[4:8])
        left = tuple(frames[8:12])
        self._deck_frames = {
            "down": down,
            "up": up,
            "left": left,
            "right": tuple(
                pygame.transform.flip(frame, True, False) for frame in left
            ),
        }

    @property
    def animation_frame(self) -> int:
        seconds_per_frame = 60.0 / SHANTY_BPM / FRAMES_PER_BEAT
        phase = int(self._anim_t / seconds_per_frame)
        return (phase + _PHASE_OFFSETS[self.performance]) % ANIMATION_FRAMES

    @property
    def draw_lift(self) -> int:
        return _DRAW_LIFTS.get(self.performance, 0)

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset
        frames = self._deck_frames.get(self.facing)
        if frames is None:
            return super().draw(surface, camera_offset)
        frame = frames[self.animation_frame]
        fw, fh = frame.get_size()
        surface.blit(
            frame,
            (int(self.x + self.width / 2 - fw / 2) - ox,
             int(self.y + self.height - fh) - oy - self.draw_lift),
        )
