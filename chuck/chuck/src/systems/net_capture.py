"""The Animal Control net: a timed hold that ends in ordinary depletion.

Being caught is deliberately *not* a second way to die. The net holds
Chuck still and drains Sanity to zero over a fixed few seconds, and then
the existing depletion hook runs -- the same quiet disappearance and
Astral Anchor return as walking into anything else. Nothing here knows
about respawning.

The drain is computed from total elapsed time rather than subtracted
frame by frame, so a slow frame, a fast frame, or a hundred tiny ones
all leave Sanity in exactly the same place.
"""

from __future__ import annotations

from src.core import config


class NetCapture:
    """One map's net state. Cleared by map reset, exactly like enemies."""

    def __init__(self) -> None:
        self._elapsed: float | None = None
        self._start_sanity = 0

    @property
    def active(self) -> bool:
        return self._elapsed is not None

    @property
    def elapsed(self) -> float:
        return self._elapsed or 0.0

    @property
    def progress(self) -> float:
        """0.0 at the moment of the catch, 1.0 when the drain completes."""
        if self._elapsed is None:
            return 0.0
        return min(1.0, self._elapsed / config.NET_CAPTURE_SECONDS)

    def begin(self, sanity_now: int) -> None:
        """Snare Chuck. Re-catching mid-net changes nothing."""
        if self._elapsed is not None:
            return
        self._elapsed = 0.0
        self._start_sanity = sanity_now

    def clear(self) -> None:
        self._elapsed = None
        self._start_sanity = 0

    def advance(self, dt: float) -> int | None:
        """Tick the hold.

        Returns the Sanity value Chuck should now be at, or None once the
        drain has run out -- at which point the caller depletes him
        through the ordinary route.
        """
        if self._elapsed is None:
            return None
        self._elapsed += dt
        if self._elapsed >= config.NET_CAPTURE_SECONDS:
            return None
        remaining = 1.0 - self._elapsed / config.NET_CAPTURE_SECONDS
        return max(0, int(self._start_sanity * remaining))
