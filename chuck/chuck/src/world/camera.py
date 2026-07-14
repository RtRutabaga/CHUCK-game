"""Camera.

Responsibilities:
    * Follow a target (Chuck) smoothly around the map.
    * Clamp the view to the map bounds so the void is never visible.
    * Provide the pixel offset every draw call subtracts from world
      coordinates.

Design notes (Game Bible: smooth follow, no fancy effects):
    * Smoothing is frame-rate independent (exponential approach), so
      the feel doesn't change if FPS ever varies.
    * The public offset is rounded to whole pixels to avoid shimmer on
      the low-res native surface; internal position stays float.
    * No pygame import — fully unit-testable anywhere.
"""

from __future__ import annotations

from src.core import config
from src.core.mathutil import approach


class Camera:
    """A viewport into the world, in world-pixel coordinates."""

    def __init__(self, view_width: int, view_height: int) -> None:
        self.view_width = view_width
        self.view_height = view_height
        self.x = 0.0
        self.y = 0.0
        self._target = None  # anything with x, y, width, height (an Entity)
        self._bounds: tuple[int, int] | None = None  # map size in pixels
        self._snap_next = False

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def set_bounds(self, map_width_px: int, map_height_px: int) -> None:
        """Restrict the view to the map so the void is never shown."""
        self._bounds = (map_width_px, map_height_px)

    def follow(self, target) -> None:
        """Track an entity. The first update snaps (no opening pan)."""
        self._target = target
        self._snap_next = True

    # ------------------------------------------------------------------
    # Per-frame
    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Move toward the target's center, then clamp to the map."""
        if self._target is None:
            return

        desired_x = (self._target.x + self._target.width / 2) - self.view_width / 2
        desired_y = (self._target.y + self._target.height / 2) - self.view_height / 2

        if self._snap_next:
            self.x, self.y = desired_x, desired_y
            self._snap_next = False
        else:
            self.x = approach(self.x, desired_x, config.CAMERA_LERP_RATE, dt)
            self.y = approach(self.y, desired_y, config.CAMERA_LERP_RATE, dt)
            # End the settle crisply: exponential approach never quite
            # arrives, and hovering sub-pixel at a rounding boundary is
            # exactly where frame-time jitter reads as shake. Within
            # half a pixel (invisible), just arrive.
            if abs(desired_x - self.x) < 0.5:
                self.x = desired_x
            if abs(desired_y - self.y) < 0.5:
                self.y = desired_y

        self._clamp()

    def _clamp(self) -> None:
        """Keep the view inside the map (maps smaller than the view
        pin to the top-left)."""
        if self._bounds is None:
            return
        map_w, map_h = self._bounds
        self.x = min(max(self.x, 0.0), max(0.0, map_w - self.view_width))
        self.y = min(max(self.y, 0.0), max(0.0, map_h - self.view_height))

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    @property
    def offset(self) -> tuple[int, int]:
        """Pixel offset to subtract from world coordinates when drawing."""
        return (round(self.x), round(self.y))
