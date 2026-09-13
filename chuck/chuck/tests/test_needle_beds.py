"""The Needle Garden's beds are needles: walked through, at a cost.

Chuck can push into them like Chult's thorns and takes the thorns'
damage for it; the orchids' seeds still stop at them, so the lanes the
beds cut are unchanged.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.entities.spitting_orchid import OrchidSeed
from src.systems.terrain_hazard import TERRAIN_HAZARDS, touching_terrain_hazard
from src.world.tilemap import TILE_DEFS, TileMap


def _garden():
    return TileMap(config.MAPS_DIR / "feywild_needle_garden.txt")


def test_the_beds_are_walkable_and_bite_like_thorns() -> None:
    assert not TILE_DEFS["✿"].solid
    assert TERRAIN_HAZARDS["✿"].sanity_damage == TERRAIN_HAZARDS["|"].sanity_damage
    tilemap = _garden()
    col, row = next((c, r) for r, line in enumerate(tilemap._grid)
                    for c, char in enumerate(line) if char == "✿")
    ts = config.TILE_SIZE
    hitbox = pygame.Rect(col * ts + 4, row * ts + 4, 8, 8)
    assert touching_terrain_hazard(tilemap, hitbox, airborne=False).kind \
        == "needles"
    assert touching_terrain_hazard(tilemap, hitbox, airborne=True) is None


def test_seeds_still_stop_at_the_beds() -> None:
    tilemap = _garden()
    ts = config.TILE_SIZE
    # Find a bed with open ground directly west of it and fire at it.
    for row, line in enumerate(tilemap._grid):
        for col, char in enumerate(line):
            if char == "✿" and col > 2 and not tilemap.is_solid(col - 2, row) \
                    and tilemap._grid[row][col - 1] not in "✿#" \
                    and tilemap._grid[row][col - 2] not in "✿#":
                seed = OrchidSeed((col - 2) * ts + 8, row * ts + 8, "right")
                for _ in range(40):
                    seed.update(0.05, tilemap)
                    if not seed.alive:
                        break
                assert not seed.alive
                assert seed.x < col * ts
                return
    raise AssertionError("no bed with open ground west of it")
