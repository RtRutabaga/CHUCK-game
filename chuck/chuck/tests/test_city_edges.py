"""Only a city map's ways out reach its edge.

Every walkable tile on the outer row or column of a day or night city map
is part of a wired exit strip (its arrows, or the arrival marker inside
them). Everything else that ran to the edge -- a highway's far end, a
pavement sliver past a corner -- is closed with the Astral Sea, so no
street looks like a way on and turns out to be an invisible wall.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from src.core import config  # noqa: E402
from src.world.collision import FALL_HAZARD_TERRAIN  # noqa: E402
from src.world.tilemap import MARKER_DEFS, TILE_DEFS  # noqa: E402
from src.world.transitions import AREA_WALK_EXITS  # noqa: E402

CITY_MAPS = ("modern_city_arrival",) + tuple(
    f"modern_city_day_{i}" for i in range(1, 7)) + tuple(
    f"modern_city_night_{i}" for i in range(2, 7))


def _walkable(char: str) -> bool:
    if char in MARKER_DEFS:
        under = MARKER_DEFS[char].under
        return not TILE_DEFS[under].solid and under not in FALL_HAZARD_TERRAIN
    return not TILE_DEFS[char].solid and char not in FALL_HAZARD_TERRAIN


def test_every_walkable_edge_tile_is_part_of_a_way_out() -> None:
    for name in CITY_MAPS:
        rows = [line for line in (config.MAPS_DIR / f"{name}.txt")
                .read_text(encoding="utf-8").splitlines()
                if not line.startswith(";")]
        height, width = len(rows), len(rows[0])
        exits = {char for (map_name, char) in AREA_WALK_EXITS
                 if map_name == name}
        assert exits, name
        for row in range(height):
            for col in range(width):
                if row not in (0, height - 1) and col not in (0, width - 1):
                    continue
                char = rows[row][col]
                if not _walkable(char) or char in exits:
                    continue
                marker = MARKER_DEFS.get(char)
                assert marker is not None and marker.kind.startswith(
                    ("boundary:", "arrival:")), (name, col, row, char)
                # ...and such a marker really is inside an exit strip.
                around = {rows[y][x]
                          for y in range(max(0, row - 1),
                                         min(height, row + 2))
                          for x in range(max(0, col - 1),
                                         min(width, col + 2))}
                assert around & exits, (name, col, row)


def test_the_seal_pass_is_what_the_generators_run() -> None:
    import generate_city_map_common as common

    for name in CITY_MAPS:
        stem = ("generate_modern_city_night_1" if name == "modern_city_arrival"
                else f"generate_{name}")
        source = (Path(common.__file__).parent / f"{stem}.py").read_text(
            encoding="utf-8")
        assert f'seal_open_edges(grid, "{name}")' in source, name
