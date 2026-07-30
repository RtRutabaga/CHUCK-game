"""Small, immediate movement effects supplied by authored terrain."""

from __future__ import annotations

from src.core import config


POLLEN_TERRAIN = frozenset({"\u263c"})


def ground_speed_multiplier(tilemap, hitbox, airborne: bool) -> float:
    """Return the current grounded movement multiplier beneath an actor.

    This is deliberately not a status-effect system. The result is derived
    from the current footprint every frame and disappears as soon as Chuck
    leaves the terrain. Airborne movement is never slowed.
    """
    if airborne:
        return 1.0
    size = config.TILE_SIZE
    left = int(hitbox.left // size)
    right = int((hitbox.right - 1) // size)
    top = int(hitbox.top // size)
    bottom = int((hitbox.bottom - 1) // size)
    if any(
        tilemap.terrain_at(col, row) in POLLEN_TERRAIN
        for row in range(top, bottom + 1)
        for col in range(left, right + 1)
    ):
        return config.FEYWILD_POLLEN_SPEED_MULTIPLIER
    return 1.0
