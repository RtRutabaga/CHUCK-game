"""The captain's one-time Premium Buhetian Halfling Leaf chest."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.systems.checkpoints import ProgressState
    from src.systems.cigarettes import CigaretteLedger


class CaptainChest:
    """A solid, y-sorted chest with a durable open/reward state."""

    progress_flag = "captain_chest_opened"

    def __init__(
        self,
        col: int,
        row: int,
        assets: "AssetManager",
        progress: "ProgressState",
        cigarettes: "CigaretteLedger",
    ) -> None:
        self.kind = "ship_captain_chest"
        self._progress = progress
        self._cigarettes = cigarettes
        self._frames = assets.sheet(
            "objects/ship_captain_chest.png", 32, 24
        )[0]
        ts = config.TILE_SIZE
        self._draw_x = col * ts + (ts - 32) // 2
        self._draw_y = (row + 1) * ts - 24
        self._bottom = (row + 1) * ts
        self._size = (32, 24)
        self.opened = self._progress.has(self.progress_flag)
        self.dialogue_id = (
            "captain_chest_empty" if self.opened else "captain_chest_reward"
        )
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
        if self.opened:
            return "captain_chest_empty"
        self.opened = True
        self.dialogue_id = "captain_chest_empty"
        self._progress.enable(self.progress_flag)
        self._cigarettes.add(config.HALFLING_LEAF_CIGARETTES)
        # Opening the one-time chest and losing its reward on death would leave
        # an open, empty chest with no way to recover the forty. Bank both sides
        # of that state transition together; the next Ashtray persists them.
        self._cigarettes.commit()
        return "captain_chest_reward"

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset
        frame = self._frames[1 if self.opened else 0]
        surface.blit(frame, (self._draw_x - ox, self._draw_y - oy))
