"""Animation timing.

Responsibilities:
    * Advance through a list of frames at a fixed per-frame duration.
    * Loop (walk cycles) or hold the last frame (one-shots, later:
      Chuck's quiet vanish).

Frames are opaque objects (pygame Surfaces in the game, anything in
tests) — this module contains timing math only and never imports
pygame, so it is unit-testable anywhere.
"""

from __future__ import annotations

from typing import Sequence


class Animation:
    """A sequence of frames played at a fixed rate."""

    def __init__(
        self, frames: Sequence, frame_duration: float, loop: bool = True
    ) -> None:
        if not frames:
            raise ValueError("Animation needs at least one frame")
        if frame_duration <= 0:
            raise ValueError("frame_duration must be positive")
        self.frames = list(frames)
        self.frame_duration = frame_duration
        self.loop = loop
        self._elapsed = 0.0

    def reset(self) -> None:
        """Restart from the first frame (called on state changes)."""
        self._elapsed = 0.0

    def update(self, dt: float) -> None:
        """Advance the clock by dt seconds."""
        self._elapsed += dt

    @property
    def frame_index(self) -> int:
        """Index of the frame that should be showing right now."""
        raw = int(self._elapsed / self.frame_duration)
        if self.loop:
            return raw % len(self.frames)
        return min(raw, len(self.frames) - 1)

    @property
    def current_frame(self):
        """The frame object that should be showing right now."""
        return self.frames[self.frame_index]

    @property
    def finished(self) -> bool:
        """True once a non-looping animation has reached its last frame."""
        if self.loop:
            return False
        return self._elapsed >= self.frame_duration * len(self.frames)
