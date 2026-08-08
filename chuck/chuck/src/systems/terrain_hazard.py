"""Reusable contact effects for hazardous walkable terrain."""

from __future__ import annotations

from typing import NamedTuple

from src.core import config


class TerrainHazard(NamedTuple):
    kind: str
    sanity_damage: int


TERRAIN_HAZARDS = {
    "|": TerrainHazard("thorns", config.THORN_SANITY_DAMAGE),
    "ʓ": TerrainHazard("sludge", config.SLUDGE_SANITY_DAMAGE),
}


def touching_terrain_hazard(tilemap, hitbox, airborne: bool) -> TerrainHazard | None:
    """Return the first hazardous terrain touched by Chuck's footprint."""
    if airborne:
        return None
    ts = config.TILE_SIZE
    left = int(hitbox.left // ts)
    right = int((hitbox.right - 1) // ts)
    top = int(hitbox.top // ts)
    bottom = int((hitbox.bottom - 1) // ts)
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            hazard = TERRAIN_HAZARDS.get(tilemap.terrain_at(col, row))
            if hazard is not None:
                return hazard
    return None
