"""A scratchable, one-time golden-carton chest.

Built for the sea captain's quarters, and reused unchanged for the
desert ruins in Phase 13 -- the phase document asks for the same chest
language, and the honest way to give it the same language is to give it
the same chest. The only thing the two cannot share is which flags they
set: two chests keyed to one pair would open together and pay out once
between them, so the flags are per instance and the captain's remain
the defaults.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.systems.checkpoints import ProgressState


def examine_chest_line(kind: str, opened: bool) -> str:
    return f"examine_{kind}_open" if opened else f"examine_{kind}"


class CaptainChest(Entity):
    """A solid chest that physically opens and drops its reward."""

    progress_flag = "captain_chest_opened"
    collected_flag = "captain_chest_carton_collected"
    opening_duration = 0.45

    def __init__(
        self,
        col: int,
        row: int,
        assets: "AssetManager",
        progress: "ProgressState",
        kind: str = "ship_captain_chest",
        progress_flag: str | None = None,
        collected_flag: str | None = None,
    ) -> None:
        self.kind = kind
        if progress_flag is not None:
            self.progress_flag = progress_flag
        if collected_flag is not None:
            self.collected_flag = collected_flag
        self._progress = progress
        self._frames = assets.sheet(
            "objects/ship_captain_chest.png", 32, 24
        )[0]
        ts = config.TILE_SIZE
        self._draw_x = col * ts + (ts - 32) // 2
        self._draw_y = (row + 1) * ts - 24
        self._bottom = (row + 1) * ts
        self._size = (32, 24)
        super().__init__(self._draw_x, self._draw_y, *self._size)
        self.opened = self._progress.has(self.progress_flag)
        self._opening = False
        self._opening_time = (
            self.opening_duration if self.opened else 0.0
        )
        self._drop = (
            col * ts + ts / 2,
            (row + 2) * ts + ts / 2,
        )
        self._drop_pending = (
            self.opened and not self._progress.has(self.collected_flag)
        )
        self.dialogue_id = None
        self.choice_id = None

    def interaction_bounds(self) -> tuple[int, int, int, int]:
        pad = 3
        w, h = self._size
        return (
            self._draw_x - pad, self._draw_y - pad,
            w + pad * 2, h + pad * 2,
        )

    @property
    def sort_y(self) -> float:
        return float(self._bottom)

    def interact(self, _by) -> str:
        """Pressing E only looks at it. Opening it takes a scratch.

        E used to open it too, which made the chest the one thing in the
        game where the two buttons did the same job -- and taught nothing
        about which one breaks things.
        """
        return examine_chest_line(self.kind, self.opened)

    def on_scratched(self) -> None:
        self._begin_opening()

    def _begin_opening(self) -> None:
        if self.opened:
            return
        self.opened = True
        self._opening = True
        self._opening_time = 0.0
        self._progress.enable(self.progress_flag)

    def update(self, dt: float) -> None:
        if not self._opening:
            return
        self._opening_time = min(
            self.opening_duration, self._opening_time + dt
        )
        if self._opening_time >= self.opening_duration:
            self._opening = False
            if not self._progress.has(self.collected_flag):
                self._drop_pending = True

    def take_drop_position(self) -> tuple[float, float] | None:
        if not self._drop_pending:
            return None
        self._drop_pending = False
        return self._drop

    def create_pickup(self, drop: tuple[float, float], assets):
        from src.entities.pickup import GoldenCigaretteCarton

        pickup = GoldenCigaretteCarton(
            *drop, self._progress, progress_flag=self.collected_flag
        )
        pickup.load_sprite(assets)
        return pickup

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset
        if not self.opened:
            frame_index = 0
        elif not self._opening:
            frame_index = len(self._frames) - 1
        else:
            progress = self._opening_time / self.opening_duration
            frame_index = min(
                len(self._frames) - 1,
                1 + int(progress * (len(self._frames) - 1)),
            )
        frame = self._frames[frame_index]
        surface.blit(frame, (self._draw_x - ox, self._draw_y - oy))
