"""The jungle temple's added dressing, checked against the shipped maps.

Cracks, missing slabs, moss and bones on the floors of the four big
rooms, carvings in their walls, ruin in the skeleton hall and two grand
arches in the sanctum -- none of it cutting a route, none of it in the
sanctum's breach band.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import temple_dressing as dressing  # noqa: E402
from src.core import config  # noqa: E402
from src.entities.prop import MUTE_PROPS, SEE_THROUGH_PROPS  # noqa: E402
from src.world.tilemap import TILE_DEFS, TileMap  # noqa: E402


def _grid(name):
    grid = dressing._read(name)[2]
    width = max(len(row) for row in grid)
    return [row + [dressing.WALL] * (width - len(row)) for row in grid]


def _undressed(grid):
    return [[dressing.WALL if char == dressing.CARVING
             else dressing.FLOOR if char in dressing.DRESSING else char
             for char in row] for row in grid]


def _kinds(name):
    return [kind for kind, _, _ in
            TileMap(config.MAPS_DIR / f"{name}.txt").prop_tiles]


def test_every_big_room_is_dressed() -> None:
    for name in dressing.MAPS:
        kinds = _kinds(name)
        assert kinds.count("temple_wall_carving") >= 4, name
        assert "temple_floor_crack" in kinds and "temple_moss" in kinds, name
    skeletons = _kinds("temple_skeletons")
    assert skeletons.count("temple_toppled_pillar") == 2
    assert skeletons.count("temple_pillar_stump") == 2
    assert _kinds("temple_sanctum").count("temple_grand_arch") == 2


def test_nothing_solid_cuts_anything_off() -> None:
    for name in dressing.MAPS:
        grid = _grid(name)
        floor_solids = sum(TILE_DEFS[char].solid for row in grid
                           for char in row
                           if char in dressing.DRESSING
                           and char != dressing.CARVING)
        before = dressing.reachable(_undressed(grid))
        after = dressing.reachable(grid)
        assert len(after) == len(before) - floor_solids, name


def test_the_sanctum_breach_band_is_plain_floor() -> None:
    grid = _grid("temple_sanctum")
    first, last = dressing.KEEP_CLEAR_COLS["temple_sanctum"]
    assert first <= config.BREACH_COLS[0] and config.BREACH_COLS[1] <= last
    for row in grid:
        for col in range(first, last + 1):
            assert row[col] not in dressing.DRESSING - {dressing.CARVING}


def test_the_new_pieces_are_mute_and_the_arch_fades() -> None:
    kinds = {"temple_floor_crack", "temple_missing_slabs", "temple_moss",
             "temple_bones", "temple_wall_carving", "temple_toppled_pillar",
             "temple_pillar_stump", "temple_grand_arch"}
    assert kinds <= MUTE_PROPS
    assert "temple_grand_arch" in SEE_THROUGH_PROPS
    for char in (dressing.CRACK, dressing.MISSING, dressing.MOSS,
                 dressing.BONES, dressing.ARCH):
        assert not TILE_DEFS[char].solid
