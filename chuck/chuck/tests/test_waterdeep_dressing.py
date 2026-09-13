"""Waterdeep's added dressing.

Gate towers and the watch's banners on the plaza's north wall, a keg
rack, notice board and rug in the tavern, and sacks and baskets in the
pantry -- and still only the one cheese.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.entities.prop import FLOOR_PROPS, MUTE_PROPS
from src.world.tilemap import TileMap


def _props(name):
    return TileMap(config.MAPS_DIR / f"{name}.txt").prop_tiles


def test_the_gate_stands_between_two_towers_under_the_watchs_banners() -> None:
    props = _props("waterdeep_plaza")
    towers = sorted((col, row) for kind, col, row in props
                    if kind == "waterdeep_gate_tower")
    gate = next((col, row) for kind, col, row in props
                if kind == "waterdeep_closed_gate")
    assert len(towers) == 2
    (west, west_row), (east, east_row) = towers
    # Symmetric about the gate, standing on the first row of paving.
    assert gate[0] - west == east - gate[0]
    assert west_row == east_row == gate[1] + 1
    banners = sorted(col for kind, col, row in props
                     if kind == "waterdeep_banner")
    assert len(banners) == 4
    assert all(row == west_row for kind, col, row in props
               if kind == "waterdeep_banner")


def test_the_tavern_and_pantry_are_furnished_without_a_second_cheese() -> None:
    tavern = {kind for kind, _, _ in _props("waterdeep_tavern")}
    assert {"tavern_keg_rack", "tavern_notice_board", "tavern_rug"} <= tavern
    pantry = [kind for kind, _, _ in _props("waterdeep_pantry")]
    assert pantry.count("pantry_sack_pile") == 2
    assert pantry.count("pantry_produce_basket") == 2
    assert [kind for kind in pantry if "cheese" in kind] == ["cheese"]


def test_the_new_pieces_are_mute_and_the_rug_is_underfoot() -> None:
    kinds = {"waterdeep_gate_tower", "waterdeep_banner", "tavern_keg_rack",
             "tavern_notice_board", "tavern_rug", "pantry_sack_pile",
             "pantry_produce_basket"}
    assert kinds <= MUTE_PROPS
    assert "tavern_rug" in FLOOR_PROPS
    tavern = TileMap(config.MAPS_DIR / "waterdeep_tavern.txt")
    rug = next((col, row) for kind, col, row in tavern.prop_tiles
               if kind == "tavern_rug")
    assert not tavern.is_solid(*rug)
