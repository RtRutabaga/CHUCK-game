"""Phlegethos's added dressing, checked against the shipped maps.

Ember cracks, vents, bone heaps and spikes on the basalt of five maps --
none solid on the lava lake, none cutting a route -- and the fortress
approach's floor left plain for its Astral waves, with towers and
banners on the row beneath its wall.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import phlegethos_dressing as dressing  # noqa: E402
from src.entities.prop import MUTE_PROPS  # noqa: E402
from src.world.tilemap import TILE_DEFS  # noqa: E402


def _answers_e(kinds) -> None:
    """Each kind has its examine line and is not in the mute scatter."""
    from src.entities.prop import examine_line_id
    from src.systems.dialogue import DialogueSystem

    dialogue = DialogueSystem()
    for kind in kinds:
        assert kind not in MUTE_PROPS, kind
        assert dialogue.get(examine_line_id(kind)), kind


def _grid(name):
    return dressing._read(name)[2]


def _undressed(grid):
    return [[dressing.FLOOR if char in dressing.DRESSING else char
             for char in row] for row in grid]


def test_hell_has_things_lying_about_in_it() -> None:
    total = {char: 0 for char in dressing.DRESSING}
    for name in dressing.FLOOR_MAPS:
        for row in _grid(name):
            for char in row:
                if char in total:
                    total[char] += 1
    assert total[dressing.CRACK] >= 30
    assert total[dressing.BONES] >= 6
    assert total[dressing.SPIKES] >= 4
    assert total[dressing.VENT] >= 2


def test_nothing_solid_cuts_anything_off_and_the_lake_has_none() -> None:
    for name in dressing.FLOOR_MAPS:
        grid = _grid(name)
        solid = sum(TILE_DEFS[char].solid for row in grid for char in row
                    if char in dressing.DRESSING)
        before = dressing.reachable(_undressed(grid))
        after = dressing.reachable(grid)
        assert len(after) == len(before) - solid, name
        if name in dressing.NO_SOLIDS:
            assert solid == 0, name


def test_the_fortress_floor_stays_plain_for_its_waves() -> None:
    grid = _grid(dressing.FORTRESS)
    placed = [(col, row) for row, line in enumerate(grid)
              for col, char in enumerate(line) if char in dressing.DRESSING]
    assert all(row == dressing.FORTRESS_ROW for _col, row in placed)
    towers = [col for col, row in placed
              if grid[row][col] == dressing.TOWER]
    banners = [col for col, row in placed
               if grid[row][col] == dressing.BANNER]
    assert sorted(towers) == list(dressing.TOWER_COLS)
    assert sorted(banners) == list(dressing.BANNER_COLS)
    # Symmetric about the gate.
    gate = [col for col, char in enumerate(grid[4]) if char == "╬"]
    middle = sum(gate) / len(gate)
    assert middle - towers[0] == towers[1] - middle


def test_the_cracks_are_mute_and_the_rest_answers_e() -> None:
    assert "phlegethos_ember_crack" in MUTE_PROPS
    _answers_e({"phlegethos_vent", "phlegethos_bone_heap",
                "phlegethos_iron_spikes", "phlegethos_fortress_tower",
                "phlegethos_banner"})
    assert not TILE_DEFS[dressing.CRACK].solid
    assert not TILE_DEFS[dressing.VENT].solid
