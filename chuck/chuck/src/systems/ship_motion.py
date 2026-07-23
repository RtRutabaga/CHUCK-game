"""Presentation-only motion for the exterior pirate-ship deck."""

from __future__ import annotations

import math


SHIP_SHANTY_BPM = 126.0
ROCK_BEATS = 8.0


def deck_rock_offset(time_s: float) -> tuple[int, int]:
    """A subtle two-axis bob over two bars of the established shanty.

    Collision remains in stable world coordinates. Only the ship, Chuck, and
    deck props move by this pixel offset; the animated ocean stays fixed.
    """
    period = (60.0 / SHIP_SHANTY_BPM) * ROCK_BEATS
    phase = (time_s % period) / period * math.tau
    return round(math.sin(phase) * 1.0), round(math.sin(phase * 2.0) * 1.0)
