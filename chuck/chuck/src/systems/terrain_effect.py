"""Small, immediate movement effects supplied by authored terrain."""

from __future__ import annotations

from src.core import config


# Terrain that drags on Chuck's feet, and how hard. Pollen was the first;
# sewer sludge is the second and slower. Anything added here is slowed by
# the same footprint rule, so no map needs its own movement code.
SLOWING_TERRAIN = {
    "\u263c": config.FEYWILD_POLLEN_SPEED_MULTIPLIER,
    "\u0293": config.SLUDGE_SPEED_MULTIPLIER,
}


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
    # The slowest terrain under the footprint wins, so straddling sludge
    # and clean floor is still slow.
    return min(
        (
            SLOWING_TERRAIN[terrain]
            for row in range(top, bottom + 1)
            for col in range(left, right + 1)
            if (terrain := tilemap.terrain_at(col, row)) in SLOWING_TERRAIN
        ),
        default=1.0,
    )
