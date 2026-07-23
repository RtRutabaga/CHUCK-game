"""The captain's scratchable, one-time golden-carton chest."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config
from src.entities.entity import Entity

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.systems.checkpoints import ProgressState


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
    ) -> None:
        self.kind = "ship_captain_chest"
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

    def interact(self, _by) -> None:
        self._begin_opening()

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

        pickup = GoldenCigaretteCarton(*drop, self._progress)
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
