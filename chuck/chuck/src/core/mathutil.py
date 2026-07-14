"""Small pure math helpers shared across systems. No pygame, ever."""

from __future__ import annotations

import math


def approach(current: float, target: float, rate: float, dt: float) -> float:
    """Frame-rate independent exponential approach.

    Moves current toward target such that the feel is identical at any
    FPS: one 0.1s step lands where ten 0.01s steps do. Used by the
    camera follow and the home-music crossfade.
    """
    return current + (target - current) * (1.0 - math.exp(-rate * dt))
