"""Author Phase 10's vast open Aerie at the top of Zephyros' tower."""

from collections import deque
import math
from pathlib import Path


W, H = 60, 46
OUT = Path(__file__).resolve().parents[1] / "assets/maps/zephyros_aerie.txt"
ARRIVAL = (30, 41)
ANCHOR = (23, 38)
ROPE_CHOICE = (29, 28)
ROPE_PROP = (29, 27)
GRIFFON = (13, 15)
NESTS = ((13, 13), (46, 13), (13, 32), (46, 32))

HEADER = [
    "; PHASE 10 - ZEPHYROS' AERIE (60x46 tiles).",
    "; A vast open-sided cloud-giant chamber: four enormous nests surround",
    "; a central floor opening and rope. One slow griffon begins at the",
    "; northwest nest; the southern threshold returns to the exterior.",
]


def build():
    grid = [["~"] * W for _ in range(H)]
    center = 30

    # A broad elliptical platform.  The previous clipped octagon had long
    # straight sides that read as a square at gameplay scale; this stepped
    # ellipse keeps the same useful floor area while making the tower's round
    # plan unmistakable.
    center_x, center_y = 29.5, 23.0
    radius_x, radius_y = 27.0, 19.0
    for row in range(3, 43):
        for col in range(2, 58):
            dx = (col - center_x) / radius_x
            dy = (row - center_y) / radius_y
            if dx * dx + dy * dy <= 1.0:
                grid[row][col] = "."
    stone = {(col, row) for row in range(H) for col in range(W)
             if grid[row][col] == "."}
    for col, row in stone:
        if any((col + dc, row + dr) not in stone
               for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            grid[row][col] = "#"

    # Southern arch landing and three-cell return threshold.
    for row in range(40, 46):
        for col in range(27, 34):
            grid[row][col] = "."
    for col in range(29, 32):
        grid[45][col] = "⇓"

    # Four giant nests use authored solid footprints matching their sprites.
    footprints = ((10, 10), (43, 10), (10, 29), (43, 29))
    for left, top in footprints:
        for row in range(top, top + 4):
            for col in range(left, left + 7):
                grid[row][col] = "#"
    for col, row in NESTS:
        grid[row][col] = "♘"

    # The central opening is the black interior of the tower, not exposed sky.
    # A two-tile break in the south rim is the only safe approach.  The rope's
    # prop tile is itself part of that stone lip so its giant cleat has a
    # visible physical attachment rather than levitating over the shaft.
    for row in range(18, 28):
        for col in range(25, 35):
            rim = row in (18, 27) or col in (25, 34)
            grid[row][col] = "#" if rim else "●"
    grid[27][30] = "."
    grid[ROPE_PROP[1]][ROPE_PROP[0]] = "℞"

    grid[ARRIVAL[1]][ARRIVAL[0]] = "ሇ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ለ"
    grid[GRIFFON[1]][GRIFFON[0]] = "ሉ"
    grid[ROPE_CHOICE[1]][ROPE_CHOICE[0]] = "ሊ"
    return grid


def _base(char):
    return {
        "ሇ": ".", "ለ": ".", "ሉ": ".", "ሊ": ".",
        "♘": "#", "℞": "#",
    }.get(char, char)


def _reachable(grid):
    reached = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < W and 0 <= y < H) or point in reached:
                continue
            if _base(grid[y][x]) in {"#", "~", "♘", "℞"}:
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def validate(grid):
    assert len(grid) == H and all(len(row) == W for row in grid)
    reached = _reachable(grid)
    assert {ANCHOR, ROPE_CHOICE, (30, 45)} <= reached
    assert all(nest not in reached for nest in NESTS)
    assert math.dist(ARRIVAL, GRIFFON) > 8
    text = "".join("".join(row) for row in grid)
    assert text.count("♘") == 4
    assert text.count("℞") == 1
    assert text.count("ሉ") == 1 and text.count("ሊ") == 1
    assert sum(row.count("⇓") for row in grid) == 3


def main():
    grid = build()
    validate(grid)
    OUT.write_text("\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
                   encoding="utf-8")
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
