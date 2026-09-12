"""Author Feywild 10: the meadow a displacer beast has claimed.

The phase's massive-creature encounter. The main route is a meandering
walk across open ground with nowhere to hide on it, and the beast holds
its middle. Chuck's answer is never to fight: it is the root arches and
toadstool caps threaded through the meadow, which he strolls under and
the beast stops dead at.

Two things the phase document insists on are proved here rather than
eyeballed: the Ashtray sits in a pocket the beast physically cannot
enter, and respawning at it never puts Chuck inside its notice range.
"""

from collections import deque
import math
from pathlib import Path

try:
    from tools.feywild_mushroom_dressing import dress_grid
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_mushroom_dressing import dress_grid
try:
    from tools.feywild_great_tree_dressing import (
        dress_grid as plant_great_tree,
    )
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_great_tree_dressing import dress_grid as plant_great_tree
try:
    from tools.feywild_root_dressing import dress_grid as dress_root_walls
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_root_dressing import dress_grid as dress_root_walls

W, H = 74, 48
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_displacer_meadow.txt"
)

# config.DINOSAUR_NOTICE_RANGE is 128px; at 16px tiles that is eight.
NOTICE_TILES = 8.0

RETURN_EXIT = (0, 24)
ARRIVAL = (1, 24)
ANCHOR = (22, 34)
FUTURE_RETURN = (72, 22)
FUTURE_EXIT = (73, 22)

BEAST = (46, 28)
MITES = ((18, 22), (34, 12), (58, 20))

# Three pockets, each behind an opening built to Chuck's scale.
ROOT_DOOR_WEST = (22, 29)
MUSHROOM_DOOR = (35, 5)
ROOT_DOOR_EAST = (60, 13)
CACHES = ((34, 3), (60, 8))

# Loose arches out in the open: walkable ground for Chuck, a wall for
# anything larger, so the meadow itself offers places to break pursuit.
OPEN_ARCHES = ((31, 20), (44, 21), (52, 25), (39, 26))

HEADER = [
    "; PHASE 9 - FEYWILD 10, THE DISPLACER MEADOW (74x48 tiles).",
    "; One massive displacer beast holds the middle of a meandering open",
    "; route thick with slowing pollen. Root arches and toadstool caps run",
    "; through the meadow: Chuck walks under them, the beast stops dead.",
    "; The Ashtray sits in a pocket the beast can never enter.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _walled_box(grid, left, top, right, bottom, door, wall, door_char):
    for col in range(left, right + 1):
        grid[top][col] = wall
        grid[bottom][col] = wall
    for row in range(top, bottom + 1):
        grid[row][left] = wall
        grid[row][right] = wall
    _room(grid, left + 1, top + 1, right - 1, bottom - 1, "'")
    grid[door[1]][door[0]] = door_char


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    # A route that swings north, then south, then north again: open the
    # whole way, so the beast always has a line on it somewhere.
    _room(grid, 1, 20, 15, 30)
    _room(grid, 14, 16, 32, 30)
    _room(grid, 26, 6, 44, 22)
    _room(grid, 38, 18, 56, 34)
    _room(grid, 50, 12, 68, 28)
    _room(grid, 66, 18, 72, 26)

    # Pollen thickens exactly where the crossing is most exposed. The beds
    # are eaten away at their edges so they read as drifts of flowers
    # rather than as rectangles someone painted on the meadow.
    for left, top, right, bottom in (
        (29, 9, 40, 14), (33, 17, 42, 21),
        (41, 23, 52, 29), (44, 30, 53, 33),
        (54, 15, 63, 19), (18, 24, 27, 28),
    ):
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if grid[row][col] != ".":
                    continue
                edge = min(col - left, right - col, row - top, bottom - row)
                if edge == 0 and (col * 7 + row * 13) % 3:
                    continue
                if edge == 1 and (col * 5 + row * 11) % 5 == 0:
                    continue
                grid[row][col] = "☼"

    _dress_with_vegetation(grid)

    # The three protected pockets. The Ashtray lives in the first.
    _walled_box(grid, 18, 29, 27, 38, ROOT_DOOR_WEST, "※", "≀")
    _walled_box(grid, 31, 1, 39, 5, MUSHROOM_DOOR, "ᛘ", "ᚿ")
    _walled_box(grid, 56, 4, 64, 13, ROOT_DOOR_EAST, "※", "≀")

    # Each loose arch is a short run of root with one low gap in it, so it
    # reads as something to duck under rather than as furniture standing
    # in a field -- and so the beast must actually go around.
    for index, (col, row) in enumerate(OPEN_ARCHES):
        assert grid[row][col] in {".", "☼"}, (col, row)
        vertical = index % 2 == 1
        for step in range(-2, 3):
            x = col + (0 if vertical else step)
            y = row + (step if vertical else 0)
            if grid[y][x] in {".", "☼"}:
                grid[y][x] = "※"
        grid[row][col] = "≀"
    for col, row in CACHES:
        grid[row][col] = "<"

    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][RETURN_EXIT[0]] = "←"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][FUTURE_EXIT[0]] = "→"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ს"
    grid[ANCHOR[1]][ANCHOR[0]] = "ტ"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "ფ"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "უ"
    grid[BEAST[1]][BEAST[0]] = "ქ"
    for col, row in MITES:
        grid[row][col] = "ღ"
    dress_grid("feywild_displacer_meadow", grid)
    dress_root_walls("feywild_displacer_meadow", grid)
    plant_great_tree("feywild_displacer_meadow", grid)
    return grid


def _dress_with_vegetation(grid) -> None:
    """The region's trees and shrubs, only well inside the dense growth."""
    for row in range(1, H - 1):
        for col in range(1, W - 1):
            if grid[row][col] != "#":
                continue
            if sum(grid[row + dr][col + dc] == "#"
                   for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))) < 3:
                continue
            key = (col * 31 + row * 17) % 21
            if key == 0:
                grid[row][col] = "ŧ"
            elif key == 8:
                grid[row][col] = "Ŧ"
            elif key == 16:
                grid[row][col] = "Ɓ"


SOLID = {"#", "※", "ፒ", "ፓ", "ፔ", "ᛘ", "ŧ", "Ŧ", "Ɓ", "ŋ"}
PASSAGES = {"≀", "ᚿ"}


def _under(char: str) -> str:
    return {"ს": "'", "ტ": "'", "უ": "→", "ფ": "'", "ქ": ".", "ღ": ".",
            "<": "."}.get(char, char)


def _reachable(grid, start, *, large_actor=False):
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < W and 0 <= y < H) or point in reached:
                continue
            char = _under(grid[y][x])
            if char in SOLID or (large_actor and char in PASSAGES):
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def validate(grid) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)

    walk = _reachable(grid, ARRIVAL)
    assert {FUTURE_EXIT, FUTURE_RETURN, RETURN_EXIT, ANCHOR, BEAST,
            ROOT_DOOR_WEST, MUSHROOM_DOOR, ROOT_DOOR_EAST,
            *CACHES, *MITES, *OPEN_ARCHES} <= walk

    # The beast is a stalker, not a doorman: it starts well away from
    # where Chuck arrives, and it cannot reach the Ashtray or the caches.
    assert math.dist(ARRIVAL, BEAST) > NOTICE_TILES * 2, math.dist(ARRIVAL,
                                                                  BEAST)
    prowl = _reachable(grid, BEAST, large_actor=True)
    assert ANCHOR not in prowl, "the beast can reach the Ashtray"
    for cache in CACHES:
        assert cache not in prowl, cache
    # Respawning must never drop Chuck inside its notice range.
    assert math.dist(ANCHOR, BEAST) > NOTICE_TILES, math.dist(ANCHOR, BEAST)

    # At least three openings it must stop at, each guarding real ground.
    doors = [ROOT_DOOR_WEST, MUSHROOM_DOOR, ROOT_DOOR_EAST]
    assert len(doors) >= 3
    for door in doors:
        assert door not in prowl, door
    # ...plus loose arches in the open, so pursuit can always be broken.
    assert len(OPEN_ARCHES) >= 3
    for arch in OPEN_ARCHES:
        assert arch not in prowl, arch

    # The exposed route really is exposed: pollen, and no cover on it.
    pollen = sum(row.count("☼") for row in grid)
    assert pollen >= 150, pollen

    text = "".join("".join(row) for row in grid)
    assert text.count("ქ") == 1
    assert text.count("ტ") == 1
    assert text.count("<") == len(CACHES)
    assert "զ" not in text and "Շ" not in text, "no redcaps in the meadow"
    assert all(grid[row][0] == "←"
               for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2))
    assert all(grid[row][W - 1] in {"→", "უ"}
               for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2))


def main() -> None:
    grid = build()
    validate(grid)
    OUT.write_text(
        "\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
