"""The Feywild's path lanterns and edging and the Moonmoth Fen's water
plants, checked against the shipped maps."""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import feywild_path_dressing as dressing  # noqa: E402
from src.core import config  # noqa: E402
from src.entities.prop import MUTE_PROPS  # noqa: E402
from src.world.tilemap import TILE_DEFS, TileMap  # noqa: E402


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


def _placed(grid, chars):
    return [(col, row) for row, line in enumerate(grid)
            for col, char in enumerate(line) if char in chars]


def test_every_path_map_has_lanterns_and_edging() -> None:
    for name in dressing.PATH_MAPS:
        grid = _grid(name)
        lanterns = _placed(grid, {dressing.LANTERN_TEAL,
                                  dressing.LANTERN_VIOLET})
        assert len(lanterns) >= 3, name
        assert _placed(grid, {dressing.PATH_STONES}), name
        for col, row in lanterns:
            # In the hedge, looking down onto a path.
            assert grid[row + 1][col] in {dressing.PATH, dressing.PATH_STONES}
            for other in lanterns:
                if other != (col, row):
                    assert max(abs(col - other[0]), abs(row - other[1])) \
                        >= dressing.LANTERN_SPACING
        TileMap(config.MAPS_DIR / f"{name}.txt")


def test_nothing_is_placed_near_a_marker() -> None:
    for name in dressing.MAPS:
        grid = _grid(name)
        for col, row in _placed(grid, dressing.DRESSING):
            radius = (dressing.FEN_CLEARANCE if name == dressing.FEN
                      and grid[row][col] == dressing.LILY_PADS else 2)
            allowed = dressing.PLAIN | ({","} if name == dressing.FEN else set())
            if grid[row][col] == dressing.LILY_PADS:
                allowed = {dressing.WATER, dressing.LILY_PADS, dressing.REEDS,
                           dressing.HEDGE}
            assert not dressing._near(grid, col, row, radius, allowed), \
                (name, col, row)


def test_the_fen_plants_stay_on_water_and_off_every_hop() -> None:
    grid = _grid(dressing.FEN)
    pads = _placed(grid, {dressing.LILY_PADS})
    reeds = _placed(grid, {dressing.REEDS})
    assert len(pads) >= 12 and reeds
    tilemap = TileMap(config.MAPS_DIR / f"{dressing.FEN}.txt")
    for col, row in pads + reeds:
        assert tilemap.is_solid(col, row)
        for y in range(row - dressing.FEN_CLEARANCE,
                       row + dressing.FEN_CLEARANCE + 1):
            for x in range(col - dressing.FEN_CLEARANCE,
                           col + dressing.FEN_CLEARANCE + 1):
                if 0 <= y < len(grid) and 0 <= x < len(grid[y]):
                    assert grid[y][x] not in {".", "≈"}, (col, row)


def test_lanterns_and_reeds_answer_e_and_walkability_is_unchanged() -> None:
    assert {"fey_path_stones", "fen_lily_pads"} <= MUTE_PROPS
    _answers_e({"fey_lantern_teal", "fey_lantern_violet", "fen_reeds"})
    assert TILE_DEFS[dressing.LANTERN_TEAL].solid == TILE_DEFS["#"].solid
    assert TILE_DEFS[dressing.PATH_STONES].solid == TILE_DEFS["'"].solid
    assert TILE_DEFS[dressing.LILY_PADS].solid == TILE_DEFS["~"].solid
    assert TILE_DEFS[dressing.REEDS].solid == TILE_DEFS["~"].solid
