"""Author Phase 10's peaceful Feywild Cloud Staircase approach."""

from collections import deque
from pathlib import Path


W, H = 64, 44
OUT = Path(__file__).resolve().parents[1] / "assets/maps/feywild_cloud_staircase.txt"

ARRIVAL = (62, 30)
RETURN_EXIT = (63, 30)
ANCHOR = (52, 33)
STAIR_ANCHOR = (28, 21)
STAIR_TRIGGER = (28, 22)

HEADER = [
    "; PHASE 10 - CLOUD STAIRCASE (64x44 tiles).",
    "; A peaceful Feywild approach. The enormous cloud stair dominates the",
    "; central clearing; approaching its base asks whether Chuck will climb.",
    "; There are no enemies. The east opening returns to Twilight Crossroads.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _path(grid, points, radius=1):
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        assert x1 == x2 or y1 == y2
        if x1 == x2:
            for row in range(min(y1, y2), max(y1, y2) + 1):
                for col in range(x1 - radius, x1 + radius + 1):
                    grid[row][col] = "'"
        else:
            for col in range(min(x1, x2), max(x1, x2) + 1):
                for row in range(y1 - radius, y1 + radius + 1):
                    grid[row][col] = "'"


def build():
    grid = [["#"] * W for _ in range(H)]

    # Broad, quiet clearing with two small scenic lobes and one obvious route.
    for row in range(19, 39):
        inset = max(0, abs(row - 29) - 6)
        _room(grid, 15 + inset, row, 56 - inset, row)
    _room(grid, 8, 27, 18, 37)
    _room(grid, 43, 18, 58, 28)
    _path(grid, [(63, 30), (48, 30), (48, 27), (28, 27), (28, 23)])
    _path(grid, [(28, 32), (12, 32)])
    _path(grid, [(47, 27), (51, 27), (51, 22)])

    # Solid growth forms a pedestal behind the immense stair prop.
    _room(grid, 24, 17, 32, 21, "#")
    _dress_edge(grid)
    grid[STAIR_ANCHOR[1]][STAIR_ANCHOR[0]] = "☁"

    # Map-local markers.
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ሀ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ሁ"
    grid[STAIR_TRIGGER[1]][STAIR_TRIGGER[0]] = "ሂ"
    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][W - 1] = "→"
    return grid


def _dress_edge(grid):
    for row in range(1, H - 1):
        for col in range(1, W - 1):
            if grid[row][col] != "#":
                continue
            neighbours = sum(
                grid[row + dr][col + dc] == "#"
                for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            if neighbours < 3:
                continue
            key = (col * 31 + row * 17) % 23
            if key == 0:
                grid[row][col] = "ŧ"
            elif key == 7:
                grid[row][col] = "Ŧ"
            elif key == 14:
                grid[row][col] = "Ɓ"


def _base(char):
    return {"ሀ": "'", "ሁ": "'", "ሂ": "'", "☁": "#"}.get(char, char)


def _reachable(grid):
    solid = {"#", "ŧ", "Ŧ", "Ɓ", "☁"}
    reached = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < W and 0 <= y < H) or point in reached:
                continue
            if _base(grid[y][x]) in solid:
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def validate(grid):
    assert len(grid) == H and all(len(row) == W for row in grid)
    reached = _reachable(grid)
    assert ANCHOR in reached and STAIR_TRIGGER in reached and RETURN_EXIT in reached
    text = "".join("".join(row) for row in grid)
    assert text.count("☁") == 1
    assert text.count("ሁ") == 1 and text.count("ሂ") == 1
    assert all(grid[row][W - 1] == "→"
               for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2))


def main():
    grid = build()
    validate(grid)
    OUT.write_text("\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
                   encoding="utf-8")
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
