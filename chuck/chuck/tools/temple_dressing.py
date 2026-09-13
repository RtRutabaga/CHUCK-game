"""The jungle temple's added dressing, applied to the shipped maps.

Four big rooms get it -- the entrance hall, the skeleton hall, the shrine
and the sanctum. The temple maps are hand-authored, so like the Chult
floor pass this edits the shipped files and only ever writes on plain
floor ('·') or on plain wall ('█').

* Floor: cracks across several slabs, beds where slabs have gone, bones,
  and moss -- the moss only on floor touching a wall, because that is
  where it comes in from. All flat, all walked over.
* Walls: carved relief panels on wall faces that look into the room,
  never beside a torch, a skull, a monument or anything else already
  set into the wall.
* The skeleton hall: two toppled pillars and two broken stumps, solid,
  each kept only if every reachable tile stays reachable.
* The sanctum: a grand arch at each end of its east wall, north and
  south, flanking the door the room is left by.

Nothing lands on the processional paving or within a tile of a marker,
a prop or a transition.
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
WALL = "█"
CRACK = "ꞗ"
MISSING = "ꞙ"
MOSS = "ꞛ"
BONES = "ꞝ"
CARVING = "ꞟ"
TOPPLED = "ꞡ"        # the middle of a toppled pillar, carrying the sprite
TOPPLED_END = "ꞣ"
STUMP = "ꞥ"
ARCH = "ꞧ"           # walkable, under the arch's opening
ARCH_PIER = "ꞩ"
DRESSING = {CRACK, MISSING, MOSS, BONES, CARVING, TOPPLED, TOPPLED_END,
            STUMP, ARCH, ARCH_PIER}
PLAIN = {FLOOR, WALL} | DRESSING

MAPS = ("temple_entrance", "temple_skeletons", "temple_shrine",
        "temple_sanctum")

# Per thousand floor tiles: cracks, missing slabs, bones, moss (of the
# floor tiles touching a wall).
DENSITY = (22, 8, 10, 120)
CARVINGS_PER_MAP = 8
SKELETON_HALL_RUIN = {"toppled": 2, "stumps": 2}

# Each arch's anchor, the walkable tile in the middle of its opening; the
# piers stand two tiles either side.
ARCHES_BY_MAP: dict[str, tuple[tuple[int, int], ...]] = {
    "temple_sanctum": ((54, 6), (54, 43)),
}

# Columns left bare on purpose, (first, last) inclusive. The sanctum's
# breach turns plain floor in columns 32 and 33 into the Astral Sea, and
# it only takes plain floor: a crack drawn there would leave a gap in
# the seal and a picture of a crack floating on the sea.
KEEP_CLEAR_COLS: dict[str, tuple[int, int]] = {
    "temple_sanctum": (31, 34),
}


def _near_something(grid, col, row, radius=1) -> bool:
    height, width = len(grid), len(grid[0])
    for y in range(row - radius, row + radius + 1):
        for x in range(col - radius, col + radius + 1):
            if 0 <= y < height and 0 <= x < len(grid[y]) \
                    and grid[y][x] not in PLAIN:
                return True
    return False


def _open(grid, col, row, left, top, right, bottom) -> bool:
    height, width = len(grid), len(grid[0])
    return all(
        0 <= y < height and 0 <= x < len(grid[y]) and grid[y][x] == FLOOR
        for y in range(row + top, row + bottom + 1)
        for x in range(col + left, col + right + 1))


def _touches_wall(grid, col, row) -> bool:
    return any(grid[row + dy][col + dx] == WALL
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


def _carving_spot(grid, col, row) -> bool:
    """A wall face looking into the room, with nothing set in it nearby."""
    height, width = len(grid), len(grid[0])
    if grid[row][col] != WALL or row + 1 >= height \
            or grid[row + 1][col] != FLOOR:
        return False
    # Plain wall either side along the face and above.
    for x in range(col - 2, col + 3):
        for y in range(row - 1, row + 1):
            if not (0 <= y < height and 0 <= x < len(grid[y])):
                return False
            if grid[y][x] not in (WALL, CARVING):
                return False
            if grid[y][x] == CARVING:
                return False
    # And nothing standing on the floor right in front of it.
    return not _near_something(grid, col, row + 1, 1)


def dress_grid(map_name: str, grid: list[list[str]]) -> None:
    seed = _name_seed(map_name)
    height, width = len(grid), len(grid[0])

    for col, row in ARCHES_BY_MAP.get(map_name, ()):
        if not _open(grid, col, row, -2, -1, 2, 0):
            raise ValueError(f"Arch at {(col, row)} in {map_name} needs "
                             "open floor under it")
        grid[row][col] = ARCH
        grid[row][col - 2] = grid[row][col + 2] = ARCH_PIER

    if map_name == "temple_skeletons":
        baseline = len(reachable(grid))
        toppled = stumps = 0
        for row in range(2, height - 2):
            for col in range(2, width - 2):
                roll = _hash(seed, col, row, 5) % 1000
                if grid[row][col] != FLOOR or _near_something(grid, col, row, 2):
                    continue
                if toppled < SKELETON_HALL_RUIN["toppled"] and roll < 14 \
                        and _open(grid, col, row, -2, -1, 2, 1):
                    trial = [list(r) for r in grid]
                    trial[row][col] = TOPPLED
                    trial[row][col - 1] = trial[row][col + 1] = TOPPLED_END
                    if len(reachable(trial)) == baseline - 3:
                        grid[:] = trial
                        baseline -= 3
                        toppled += 1
                        continue
                if stumps < SKELETON_HALL_RUIN["stumps"] and 14 <= roll < 26 \
                        and _open(grid, col, row, -1, -1, 1, 1):
                    trial = [list(r) for r in grid]
                    trial[row][col] = STUMP
                    if len(reachable(trial)) == baseline - 1:
                        grid[:] = trial
                        baseline -= 1
                        stumps += 1

    carvings = 0
    candidates = [(col, row) for row in range(height) for col in range(width)
                  if _carving_spot(grid, col, row)]
    candidates.sort(key=lambda cell: _hash(seed, cell[0], cell[1], 17))
    for col, row in candidates:
        if carvings >= CARVINGS_PER_MAP:
            break
        if _carving_spot(grid, col, row):
            grid[row][col] = CARVING
            carvings += 1

    cracks, missing, bones, moss = DENSITY
    clear = KEEP_CLEAR_COLS.get(map_name)
    for row in range(1, height - 1):
        for col in range(1, width - 1):
            if grid[row][col] != FLOOR or _near_something(grid, col, row, 1):
                continue
            if clear and clear[0] <= col <= clear[1]:
                continue
            roll = _hash(seed, col, row) % 1000
            if _touches_wall(grid, col, row):
                if roll < moss:
                    grid[row][col] = MOSS
                continue
            if roll < cracks:
                grid[row][col] = CRACK
            elif roll < cracks + missing:
                grid[row][col] = MISSING
            elif roll < cracks + missing + bones:
                grid[row][col] = BONES


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
        # A few authored rows are a tile short; pad them with wall while
        # dressing and trim them back after, so no row changes length.
        lengths = [len(row) for row in grid]
        width = max(lengths)
        for row in grid:
            row.extend(WALL * (width - len(row)))
        dress_grid(map_name, grid)
        rows = ["".join(row[:length]) for row, length in zip(grid, lengths)]
        path.write_text("\n".join(header + rows) + "\n", encoding="utf-8")
        print(f"Dressed {map_name}")


if __name__ == "__main__":
    update_authored_maps()
