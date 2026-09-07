"""Authored population for Phase 14's returned Waterdeep docks.

The physical map is shared with the opening.  These placements are therefore
state dressing rather than map geometry: loading the same map without the
return flag produces the quiet morning exactly as before.
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
