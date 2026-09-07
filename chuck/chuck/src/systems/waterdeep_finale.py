"""Authored population for Phase 14's two Waterdeep states.

The physical maps are shared with the opening. These placements are therefore
state dressing rather than duplicate geometry: the plaza always has its staff
and guards, while the return flag adds the larger midday crowd.
"""

from __future__ import annotations

from typing import NamedTuple


# The Chult cog art already speaks the game's ship language. Anchored low in
# the southwest harbor, it meets only the end of the fishing pier; its hull and
# sail remain over water, so the non-explorable scenery needs no new collision.
DOCKED_SHIP_TILE = (3, 34)


class TownspersonSpawn(NamedTuple):
    sprite_id: str
    dialogue_id: str
    tile: tuple[int, int]
    facing: str


FISHERMAN_TILE = (16, 29)

# Two more hands on the working dock and three browsers in front of the market
# make the return visibly busier without putting a human hitbox in Chuck's way.
RETURN_TOWNSFOLK = (
    TownspersonSpawn("dock_worker", "return_dock_worker", (23, 18), "left"),
    TownspersonSpawn("dock_worker", "return_dock_worker", (31, 25), "right"),
    TownspersonSpawn("market_woman", "market_browser", (41, 32), "up"),
    TownspersonSpawn("dock_worker", "market_browser", (46, 33), "up"),
    TownspersonSpawn("market_woman", "market_browser", (52, 32), "up"),
)


# Permanent plaza staff establish its function even during the quiet opening.
# The gate itself is solid; its guards remain non-colliding like every human,
# because Chuck can walk between boots but not through iron.
PLAZA_TOWNSFOLK = (
    TownspersonSpawn("guard", "plaza_guard", (21, 4), "down"),
    TownspersonSpawn("guard", "plaza_guard", (27, 4), "down"),
    TownspersonSpawn("dock_worker", "blacksmith", (9, 13), "down"),
    TownspersonSpawn("market_woman", "alchemist", (37, 13), "down"),
    TownspersonSpawn("market_woman", "plaza_townsperson", (15, 30), "right"),
)


# Midday brings six more people out around the fountain and south market.
RETURN_PLAZA_TOWNSFOLK = (
    TownspersonSpawn("dock_worker", "return_plaza_townsperson", (6, 20), "right"),
    TownspersonSpawn("market_woman", "return_plaza_townsperson", (13, 22), "right"),
    TownspersonSpawn("dock_worker", "return_plaza_townsperson", (19, 23), "up"),
    TownspersonSpawn("market_woman", "return_plaza_townsperson", (30, 22), "left"),
    TownspersonSpawn("dock_worker", "return_plaza_townsperson", (36, 20), "left"),
    TownspersonSpawn("market_woman", "return_plaza_townsperson", (42, 24), "left"),
)
