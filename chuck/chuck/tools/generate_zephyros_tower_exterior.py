"""Author the first playable top-down platform outside Zephyros' tower."""

from collections import deque
from pathlib import Path


W, H = 44, 34
OUT = Path(__file__).resolve().parents[1] / "assets/maps/zephyros_tower_exterior.txt"
ARRIVAL = (22, 27)
ANCHOR = (17, 25)
ARCH_PROP = (22, 6)
ARCH = (22, 9)
FUTURE_RETURN = (22, 10)

HEADER = [
    "; PHASE 10 - ZEPHYROS TOWER EXTERIOR (44x34 tiles).",
    "; A circular pale-stone platform suspended in animated open sky.",
    "; Chuck arrives on the south platform; the giant north arch is inert",
    "; until the Aerie slice is implemented.",
]


def build():
    grid = [["~"] * W for _ in range(H)]
    cx, cy = 22, 18
    for row in range(4, 31):
        for col in range(5, 39):
            dx = (col - cx) / 16.0
            dy = (row - cy) / 13.0
            if dx * dx + dy * dy <= 1.0:
                grid[row][col] = "."

    # Turn the outer ring into a solid, readable stone lip above the clouds.
    stone = {(col, row) for row in range(H) for col in range(W)
             if grid[row][col] == "."}
    for col, row in stone:
        if any((col + dc, row + dr) not in stone
               for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            grid[row][col] = "#"

    # Southern landing tongue and the broad approach to the immense arch.
    for row in range(24, 30):
        for col in range(19, 26):
            grid[row][col] = "."
    for row in range(7, 26):
        for col in range(19, 26):
            if grid[row][col] != "~":
                grid[row][col] = "."
    grid[ARCH_PROP[1]][ARCH_PROP[0]] = "Ƶ"
    grid[ARCH[1]][ARCH[0]] = "ህ"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "ሆ"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ሃ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ሄ"
    return grid


def _base(char):
    return {"ሃ": ".", "ሄ": ".", "ህ": "Ƶ", "ሆ": "."}.get(char, char)


def validate(grid):
    assert len(grid) == H and all(len(row) == W for row in grid)
    walkable = {(col, row) for row in range(H) for col in range(W)
                if _base(grid[row][col]) in {".", "'", "Ƶ"}}
    reached = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in walkable and point not in reached:
                reached.add(point)
                frontier.append(point)
    assert ANCHOR in reached and ARCH in reached and FUTURE_RETURN in reached
    text = "".join("".join(row) for row in grid)
    assert text.count("ሄ") == 1 and text.count("ህ") == 1
    assert text.count("Ƶ") == 1
    assert text.count("~") > text.count("."), "open sky no longer dominates"


def main():
    grid = build()
    validate(grid)
    OUT.write_text("\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
                   encoding="utf-8")
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
