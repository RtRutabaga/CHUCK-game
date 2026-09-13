"""Chult's jungle-floor dressing, checked against the shipped maps.

The same rules tools/chult_floor_dressing.py places by: nothing but plain
ground changes, nothing solid cuts anything off, the great trees keep
their crowns clear of everything that matters, and the run's gaps and
the temple's avenue stay bare.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import chult_floor_dressing as dressing  # noqa: E402
from src.core import config  # noqa: E402
from src.entities.prop import MUTE_PROPS, SEE_THROUGH_PROPS  # noqa: E402
from src.world.tilemap import TILE_DEFS, TileMap  # noqa: E402


def _grid(name):
    return dressing._read(name)[2]


def _undressed(grid):
    return [[dressing.GROUND if char in dressing.DRESSING else char
             for char in row] for row in grid]


def test_every_chult_map_is_dressed_and_loads() -> None:
    for name in dressing.MAPS:
        grid = _grid(name)
        placed = sum(char in dressing.DRESSING for row in grid for char in row)
        assert placed >= 12, name
        TileMap(config.MAPS_DIR / f"{name}.txt")


def test_nothing_solid_cuts_anything_off() -> None:
    for name in dressing.MAPS:
        grid = _grid(name)
        solid = sum(TILE_DEFS[char].solid for row in grid for char in row
                    if char in dressing.DRESSING)
        before = dressing.reachable(_undressed(grid))
        after = dressing.reachable(grid)
        assert len(after) == len(before) - solid, name
        assert after <= before, name


def test_great_trees_stand_where_the_rules_allow() -> None:
    for name, (col, row) in dressing.GREAT_TREES_BY_MAP.items():
        grid = _undressed(_grid(name))
        assert dressing.check_great_tree(grid, col, row) is None, name
        shipped = _grid(name)
        assert shipped[row][col] == dressing.GREAT_TREE
    assert "chult_run" not in dressing.GREAT_TREES_BY_MAP


def test_the_run_gaps_and_the_temple_avenue_stay_bare() -> None:
    for name, rects in dressing.KEEP_CLEAR.items():
        grid = _grid(name)
        for left, top, right, bottom in rects:
            for y in range(top, bottom + 1):
                for x in range(left, right + 1):
                    if grid[y][x] in dressing.DRESSING:
                        assert grid[y][x] == dressing.STELA, (name, x, y)


def test_the_floor_is_mute_and_the_giants_fade() -> None:
    kinds = {"chult_fern", "chult_leaf_litter", "chult_fallen_log",
             "chult_ruin_fragment", "chult_great_tree"}
    assert kinds <= MUTE_PROPS
    assert "chult_great_tree" in SEE_THROUGH_PROPS
    assert not TILE_DEFS[dressing.FERN].solid
    assert not TILE_DEFS[dressing.LITTER].solid
