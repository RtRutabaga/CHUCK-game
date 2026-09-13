"""Phlegethos's added dressing, applied to the shipped maps.

Floor dressing on the arrival, the lava road, the lava lake, the rubble
pass and the fractured way: ember cracks and smoking vents (walked over
and past), bone heaps and iron spikes (solid, each kept only if every
reachable tile stays reachable). Only ever on plain basalt ('·'), and
never within a tile of lava, a fissure, a path, a marker or a prop -- so
nothing crowds a jump's take-off or landing.

The lava lake gets no solid pieces at all: its crossing is a chain of
single committed hops between small islands, and it is the one map
where a spike in the wrong place is a death.

The fortress approach gets no floor dressing. Its battle floods plain
basalt with the Astral Sea in waves, and those waves only take plain
basalt: dressing there would leave holes in the seal. It gets towers
and banners on the fortress wall instead, on the open row beneath it.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chult_floor_dressing import _hash, _name_seed, reachable  # noqa: E402

FLOOR = "·"
CRACK = "Ɜ"
VENT = "ꞵ"
BONES = "ꞷ"
SPIKES = "ꞹ"
TOWER = "ꞻ"
BANNER = "ꞽ"
DRESSING = {CRACK, VENT, BONES, SPIKES, TOWER, BANNER}
PLAIN = {FLOOR, "█"} | DRESSING

FLOOR_MAPS = ("phlegethos_arrival", "phlegethos_road", "phlegethos_lake",
              "phlegethos_rubble_pass", "phlegethos_fractured_way")
FORTRESS = "phlegethos_fortress_approach"
MAPS = FLOOR_MAPS + (FORTRESS,)

# Per thousand open tiles.
CRACKS = 30
VENTS_PER_MAP = 2
BONE_HEAPS_PER_MAP = 4
SPIKES_PER_MAP = 3
NO_SOLIDS = {"phlegethos_lake"}

# On the open row under the fortress wall: towers flanking the gate wide,
# banners either side of each tower.
FORTRESS_ROW = 7
TOWER_COLS = (13, 35)
BANNER_COLS = (8, 18, 30, 40)


def _near_something(grid, col, row, radius) -> bool:
    for y in range(row - radius, row + radius + 1):
        for x in range(col - radius, col + radius + 1):
            if 0 <= y < len(grid) and 0 <= x < len(grid[y]) \
                    and grid[y][x] not in PLAIN:
                return True
    return False


def dress_grid(map_name: str, grid: list[list[str]]) -> None:
    if map_name == FORTRESS:
        for col in TOWER_COLS:
            if grid[FORTRESS_ROW][col] != FLOOR:
                raise ValueError(f"Tower at {(col, FORTRESS_ROW)} overlaps "
                                 f"{grid[FORTRESS_ROW][col]!r}")
            grid[FORTRESS_ROW][col] = TOWER
        for col in BANNER_COLS:
            if grid[FORTRESS_ROW][col] != FLOOR:
                raise ValueError(f"Banner at {(col, FORTRESS_ROW)} overlaps "
                                 f"{grid[FORTRESS_ROW][col]!r}")
            grid[FORTRESS_ROW][col] = BANNER
        return

    seed = _name_seed(map_name)
    solids_allowed = map_name not in NO_SOLIDS
    baseline = len(reachable(grid))
    vents = heaps = spikes = 0
    for row in range(1, len(grid) - 1):
        for col in range(1, len(grid[row]) - 1):
            if grid[row][col] != FLOOR or _near_something(grid, col, row, 1):
                continue
            roll = _hash(seed, col, row) % 1000
            if solids_allowed and roll < 40 \
                    and not _near_something(grid, col, row, 2):
                want = BONES if roll < 24 else SPIKES
                if (want == BONES and heaps < BONE_HEAPS_PER_MAP) or \
                        (want == SPIKES and spikes < SPIKES_PER_MAP):
                    trial = [list(r) for r in grid]
                    trial[row][col] = want
                    if len(reachable(trial)) == baseline - 1:
                        grid[:] = trial
                        baseline -= 1
                        if want == BONES:
                            heaps += 1
                        else:
                            spikes += 1
                        continue
            if 40 <= roll < 46 and vents < VENTS_PER_MAP \
                    and not _near_something(grid, col, row, 2):
                grid[row][col] = VENT
                vents += 1
            elif 46 <= roll < 46 + CRACKS:
                grid[row][col] = CRACK


def _read(map_name):
    path = ROOT / "assets" / "maps" / f"{map_name}.txt"
    lines = path.read_text(encoding="utf-8").splitlines()
    header = [line for line in lines if line.startswith(";")]
    grid = [list(line) for line in lines if not line.startswith(";")]
    return path, header, grid


def update_authored_maps() -> None:
    for map_name in MAPS:
        path, header, grid = _read(map_name)
        if any(char in DRESSING for row in grid for char in row):
            raise ValueError(f"{map_name} is already dressed")
        dress_grid(map_name, grid)
        path.write_text("\n".join(header + ["".join(r) for r in grid]) + "\n",
                        encoding="utf-8")
        print(f"Dressed {map_name}")


if __name__ == "__main__":
    update_authored_maps()
