"""The Feywild's path lanterns and edging, and the Moonmoth Fen's water
plants, applied to the shipped maps.

Edits the shipped files in place, like the great trees and mushrooms.
The generators for these maps are not touched: their validators prove
the hedge and flower puzzles from the generated grid, and none of this
dressing changes what can be walked, so the proofs stand as they are.

Paths (the Shifting Hedge, the Twilight Crossroads, the Pollen Orchard
and the Blooming Path):

* lanterns stand in the hedge along the north edge of a path, looking
  down onto it, never closer than seven tiles to another;
* mossy stones lie along path edges, flat, never two side by side.

The Moonmoth Fen:

* lily pads on open water, at least three tiles from any island, bank,
  channel or moth -- the fen is a chain of committed hops, and nothing
  near a hop may look like a place to land;
* reeds in the water just off the west and east banks, the same
  distance from the channels.

Nothing is placed within two tiles of a marker -- flower switches, the
tiles they open and close, exits, arrivals, grass, enemies -- because a
flower toggles its target's terrain and a prop drawn there would stay
drawn over whatever it became.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from chult_floor_dressing import _hash, _name_seed  # noqa: E402

HEDGE = "#"
PATH = "'"
WATER = "~"
LANTERN_TEAL = "Ꞵ"
LANTERN_VIOLET = "Ꞷ"
PATH_STONES = "Ꞹ"
LILY_PADS = "Ꞻ"
REEDS = "Ꞽ"
DRESSING = {LANTERN_TEAL, LANTERN_VIOLET, PATH_STONES, LILY_PADS, REEDS}
VEGETATION = {"ŧ", "Ŧ", "Ɓ"}
PLAIN = {HEDGE, PATH, ".", WATER} | VEGETATION | DRESSING

PATH_MAPS = ("feywild_shifting_hedge", "feywild_twilight_crossroads",
             "feywild_pollen_orchard", "feywild_blooming_path")
FEN = "feywild_moonmoth_fen"
MAPS = PATH_MAPS + (FEN,)

LANTERN_SPACING = 7
STONES_PER_THOUSAND = 140
LILY_PADS_PER_THOUSAND = 22
REEDS_PER_THOUSAND = 260
FEN_CLEARANCE = 3


def _near(grid, col, row, radius, allowed) -> bool:
    for y in range(row - radius, row + radius + 1):
        for x in range(col - radius, col + radius + 1):
            if 0 <= y < len(grid) and 0 <= x < len(grid[y]) \
                    and grid[y][x] not in allowed:
                return True
    return False


def _dress_paths(map_name, grid) -> None:
    seed = _name_seed(map_name)
    lanterns: list[tuple[int, int]] = []
    height = len(grid)
    for row in range(1, height - 1):
        for col in range(1, len(grid[row]) - 1):
            if grid[row][col] != HEDGE or grid[row + 1][col] != PATH:
                continue
            if _near(grid, col, row, 2, PLAIN):
                continue
            if any(max(abs(col - c), abs(row - r)) < LANTERN_SPACING
                   for c, r in lanterns):
                continue
            if _hash(seed, col, row, 1) % 3:
                continue
            grid[row][col] = (LANTERN_TEAL if _hash(seed, col, row, 2) % 2
                              else LANTERN_VIOLET)
            lanterns.append((col, row))

    for row in range(1, height - 1):
        for col in range(1, len(grid[row]) - 1):
            if grid[row][col] != PATH:
                continue
            edge = any(grid[row + dy][col + dx] in {HEDGE} | VEGETATION
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if not edge or _near(grid, col, row, 2, PLAIN):
                continue
            if any(grid[y][x] == PATH_STONES
                   for y in range(row - 1, row + 2)
                   for x in range(col - 1, col + 2)):
                continue
            if _hash(seed, col, row, 3) % 1000 < STONES_PER_THOUSAND:
                grid[row][col] = PATH_STONES


def _dress_fen(grid) -> None:
    seed = _name_seed(FEN)
    open_water = {WATER, LILY_PADS, REEDS, HEDGE}
    for row in range(1, len(grid) - 1):
        for col in range(1, len(grid[row]) - 1):
            if grid[row][col] != WATER:
                continue
            roll = _hash(seed, col, row) % 1000
            clear = not _near(grid, col, row, FEN_CLEARANCE, open_water)
            if clear and roll < LILY_PADS_PER_THOUSAND:
                grid[row][col] = LILY_PADS
                continue
            # Reeds: water touching a bank, and clear of everything that
            # is not bank, water or wall.
            beside_bank = any(grid[row + dy][col + dx] == ","
                              for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if beside_bank and roll < REEDS_PER_THOUSAND and not _near(
                    grid, col, row, FEN_CLEARANCE, open_water | {","}):
                grid[row][col] = REEDS


def dress_grid(map_name: str, grid: list[list[str]]) -> None:
    if map_name == FEN:
        _dress_fen(grid)
    else:
        _dress_paths(map_name, grid)


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
