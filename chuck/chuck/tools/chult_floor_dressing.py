"""Chult's jungle-floor dressing, applied to the shipped maps.

Chult's maps are hand-authored (no generator reproduces them), so this
works like the Feywild's great trees and mushrooms: it edits the shipped
files in place and changes nothing but plain jungle ground.

What goes down:

* one great tree on each map with room for one -- the Feywild's giants
  in Chult's palette, fading like theirs when anyone walks behind;
* ferns (walked through) and leaf litter (flat) scattered over open
  ground;
* a few fallen logs and ruin fragments, which are solid, so each one is
  checked against the map's walkable area before it is kept: if putting
  it down would cut off a single tile anybody could reach before, it is
  not put down;
* on the temple approach, carved stelae either side of the skull-stake
  avenue.

Nothing lands within reach of anything that matters -- arrivals, exits,
Waypoints, grass, enemies, hazards, the stream -- because the tiles
around those are where the player's attention needs to be, not on a fern.
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GROUND = "."
FERN = "ꝭ"
LITTER = "ꝯ"
LOG = "ꞁ"            # the middle of a log, carrying the sprite
LOG_END = "ꞃ"        # the two solid tiles either side of it
FRAGMENT = "ꞅ"
GREAT_TREE = "ꞇ"
GREAT_TREE_ROOTS = "ꞑ"
STELA = "ꞓ"
DRESSING = {FERN, LITTER, LOG, LOG_END, FRAGMENT, GREAT_TREE,
            GREAT_TREE_ROOTS, STELA}
# Chult's own vegetation and ground: everything else on a map is something
# a player needs to see.
SCENERY = {GROUND, "#", "/", "\\"} | DRESSING

MAPS = ("chult_jungle", "chult_cog", "chult_run", "chult_respite",
        "chult_temple")

# The great trees, one per map with room, found by ``find_great_tree``
# and held to ``check_great_tree``. The run is a chase through corridors
# and gets none; the temple approach has the pyramid, and a tree that
# size beside it would be arguing with it.
GREAT_TREES_BY_MAP: dict[str, tuple[int, int]] = {
    "chult_jungle": (22, 54),
    "chult_cog": (57, 64),
    "chult_respite": (46, 18),
}

# Carved stelae flanking the temple's skull-stake avenue.
STELAE_BY_MAP: dict[str, tuple[tuple[int, int], ...]] = {
    "chult_temple": ((24, 27), (39, 27), (24, 33), (39, 33)),
}

# Per map: how much of the open ground gets a fern and litter (per
# thousand tiles), and whether solid pieces go down at all.
DENSITY = {
    "chult_jungle": (26, 34, True),
    "chult_cog": (22, 30, True),
    "chult_run": (14, 24, False),
    "chult_respite": (26, 34, True),
    "chult_temple": (18, 30, True),
}
LOGS_PER_MAP = 3
FRAGMENTS_PER_MAP = 4

# Areas left bare on purpose.
KEEP_CLEAR: dict[str, tuple[tuple[int, int, int, int], ...]] = {
    # The avenue between the skull stakes, up to the pyramid's stair.
    "chult_temple": ((25, 23, 38, 36),),
    # The three gaps the run's route squeezes north through.
    "chult_run": ((22, 9, 26, 11), (22, 16, 26, 18), (22, 23, 26, 25)),
}


def _hash(*values: int) -> int:
    h = 2166136261
    for value in values:
        h = ((h ^ (value & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def _name_seed(map_name: str) -> int:
    return sum(ord(ch) * (index + 1) for index, ch in enumerate(map_name))


def _solid(char: str) -> bool:
    from src.world.tilemap import MARKER_DEFS, TILE_DEFS

    if char in TILE_DEFS:
        return TILE_DEFS[char].solid
    marker = MARKER_DEFS[char]
    return TILE_DEFS[marker.under].solid


def reachable(grid: list[list[str]]) -> set[tuple[int, int]]:
    """Every walkable tile connected to the largest walkable region."""
    height = len(grid)
    seen: set[tuple[int, int]] = set()
    best: set[tuple[int, int]] = set()
    for row in range(height):
        for col in range(len(grid[row])):
            if (col, row) in seen or _solid(grid[row][col]):
                continue
            region = {(col, row)}
            queue = deque([(col, row)])
            seen.add((col, row))
            while queue:
                x, y = queue.popleft()
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= ny < height and 0 <= nx < len(grid[ny]) \
                            and (nx, ny) not in seen \
                            and not _solid(grid[ny][nx]):
                        seen.add((nx, ny))
                        region.add((nx, ny))
                        queue.append((nx, ny))
            if len(region) > len(best):
                best = region
    return best


def _near_something(grid, col, row, radius) -> bool:
    height, width = len(grid), len(grid[0])
    for y in range(row - radius, row + radius + 1):
        for x in range(col - radius, col + radius + 1):
            if 0 <= x < width and 0 <= y < height \
                    and grid[y][x] not in SCENERY:
                return True
    return False


def _kept_clear(map_name, col, row) -> bool:
    return any(left <= col <= right and top <= row <= bottom
               for left, top, right, bottom in KEEP_CLEAR.get(map_name, ()))


def _open(grid, col, row, left, top, right, bottom) -> bool:
    height, width = len(grid), len(grid[0])
    for y in range(row + top, row + bottom + 1):
        for x in range(col + left, col + right + 1):
            if not (0 <= x < width and 0 <= y < height):
                return False
            if grid[y][x] != GROUND:
                return False
    return True


def tree_footprint(col: int, row: int) -> list[tuple[int, int]]:
    cells = [(col + dcol, row + drow) for drow in (-1, 0)
             for dcol in (-1, 0, 1)]
    cells.remove((col, row))
    return cells + [(col, row)]


def check_great_tree(grid, col, row) -> str | None:
    """Why a great tree cannot stand here, or None if it can."""
    height, width = len(grid), len(grid[0])
    if not _open(grid, col, row, -2, -2, 2, 1):
        return "the trunk needs open ground all round it"
    for y in range(row - 13, row + 2):
        for x in range(col - 5, col + 6):
            if 0 <= x < width and 0 <= y < height \
                    and grid[y][x] not in SCENERY:
                return f"{grid[y][x]!r} at {(x, y)} would be under the crown"
    before = reachable(grid)
    trial = [list(r) for r in grid]
    for x, y in tree_footprint(col, row):
        trial[y][x] = GREAT_TREE_ROOTS
    after = reachable(trial)
    if len(after) != len(before) - 6:
        return "the footprint would cut part of the map off"
    return None


def find_great_tree(grid) -> tuple[int, int] | None:
    """The most open legal spot: the crown over the most ground."""
    height, width = len(grid), len(grid[0])
    best, best_score = None, 0
    for row in range(14, height - 3):
        for col in range(6, width - 6):
            if not _open(grid, col, row, -2, -2, 2, 1):
                continue
            score = sum(1 for y in range(row - 13, row + 2)
                        for x in range(col - 5, col + 6)
                        if grid[y][x] == GROUND)
            if score > best_score and check_great_tree(grid, col, row) is None:
                best, best_score = (col, row), score
    return best if best_score >= 120 else None


def dress_grid(map_name: str, grid: list[list[str]]) -> None:
    seed = _name_seed(map_name)
    height, width = len(grid), len(grid[0])
    baseline = len(reachable(grid))

    tree = GREAT_TREES_BY_MAP.get(map_name)
    if tree is not None:
        problem = check_great_tree(grid, *tree)
        if problem:
            raise ValueError(f"Great tree at {tree} in {map_name}: {problem}")
        for x, y in tree_footprint(*tree):
            grid[y][x] = GREAT_TREE_ROOTS
        grid[tree[1]][tree[0]] = GREAT_TREE
        baseline -= 6

    def under_tree(col, row):
        return tree is not None and abs(col - tree[0]) <= 3 \
            and tree[1] - 3 <= row <= tree[1] + 2

    for col, row in STELAE_BY_MAP.get(map_name, ()):
        if grid[row][col] != GROUND:
            raise ValueError(f"Stela at {(col, row)} in {map_name} "
                             f"overlaps {grid[row][col]!r}")
        grid[row][col] = STELA
        baseline -= 1

    ferns, litter, solids = DENSITY[map_name]
    logs = fragments = 0
    for row in range(1, height - 1):
        for col in range(1, width - 1):
            if grid[row][col] != GROUND or under_tree(col, row) \
                    or _kept_clear(map_name, col, row) \
                    or _near_something(grid, col, row, 2):
                continue
            roll = _hash(seed, col, row) % 1000
            if solids and logs < LOGS_PER_MAP and roll < 6 \
                    and _open(grid, col, row, -2, -1, 2, 1):
                trial = [list(r) for r in grid]
                trial[row][col - 1] = trial[row][col + 1] = LOG_END
                trial[row][col] = LOG
                if len(reachable(trial)) == baseline - 3:
                    grid[:] = trial
                    baseline -= 3
                    logs += 1
                    continue
            if solids and fragments < FRAGMENTS_PER_MAP and 6 <= roll < 14 \
                    and _open(grid, col, row, -1, -1, 1, 1):
                trial = [list(r) for r in grid]
                trial[row][col] = FRAGMENT
                if len(reachable(trial)) == baseline - 1:
                    grid[:] = trial
                    baseline -= 1
                    fragments += 1
                    continue
            if 14 <= roll < 14 + ferns:
                grid[row][col] = FERN
            elif 14 + ferns <= roll < 14 + ferns + litter:
                grid[row][col] = LITTER


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
    if sys.argv[1:] == ["--find-trees"]:
        for name in MAPS:
            if name == "chult_run":
                continue
            print(name, find_great_tree(_read(name)[2]))
    else:
        update_authored_maps()
