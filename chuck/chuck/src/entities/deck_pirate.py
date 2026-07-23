"""Rhythmic non-combat pirates for the exterior ship deck."""

from __future__ import annotations

import math
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
        self._walk_frames: dict[str, tuple[object, ...]] = {}
        self.scripted_moving = False

    def load_sprites(self, assets: "AssetManager") -> None:
        import pygame

        frames = assets.sheet(
            f"npcs/{self.npc_id}.png",
            config.NPC_FRAME_W,
            config.NPC_FRAME_H,
        )[0]
        expected = ANIMATION_FRAMES * (6 if self.performance == "captain" else 3)
        if len(frames) != expected:
            raise ValueError(
                f"{self.npc_id} needs {expected} deck-animation frames, got "
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
        if self.performance == "captain":
            walk_down = tuple(frames[12:16])
            walk_up = tuple(frames[16:20])
            walk_left = tuple(frames[20:24])
            self._walk_frames = {
                "down": walk_down,
                "up": walk_up,
                "left": walk_left,
                "right": tuple(
                    pygame.transform.flip(frame, True, False)
                    for frame in walk_left
                ),
            }

    def scripted_walk_toward(
        self,
        target_x: float,
        target_y: float,
        speed: float,
        dt: float,
    ) -> bool:
        """Walk an authored deck route while player control is suspended."""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.hypot(dx, dy)
        if distance <= 1e-4:
            self.x, self.y = target_x, target_y
            self.scripted_moving = False
            self.update(dt)
            return True
        if abs(dx) > abs(dy):
            self.facing = "right" if dx > 0 else "left"
        else:
            self.facing = "down" if dy > 0 else "up"
        step = min(distance, speed * dt)
        self.x += dx / distance * step
        self.y += dy / distance * step
        reached = step >= distance
        if reached:
            self.x, self.y = target_x, target_y
        self.scripted_moving = step > 0.0 and not reached
        self.update(dt)
        return reached

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
        frames_by_facing = (
            self._walk_frames if self.scripted_moving else self._deck_frames
        )
        frames = frames_by_facing.get(self.facing)
        if frames is None:
            return super().draw(surface, camera_offset)
        frame_index = (
            int(self._anim_t / 0.14) % ANIMATION_FRAMES
            if self.scripted_moving
            else self.animation_frame
        )
        frame = frames[frame_index]
        fw, fh = frame.get_size()
        surface.blit(
            frame,
            (int(self.x + self.width / 2 - fw / 2) - ox,
             int(self.y + self.height - fh) - oy - self.draw_lift),
        )
