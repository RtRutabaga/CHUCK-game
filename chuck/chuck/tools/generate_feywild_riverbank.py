"""Author the first playable Feywild map at the riverbank.

This deliberately bounded Phase 9 opening continues the completed cutscene:
Chuck stands on the eastern bank of the same blue-green river, finds an
Ashtray almost immediately, and can explore a quiet enchanted clearing before
reaching an inert route deeper into the Feywild. No enemies or future-region
mechanics are invented here.
"""

from collections import deque
import math
from pathlib import Path


W, H = 52, 36
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_riverbank.txt"
)

ARRIVAL = (15, 27)
ANCHOR = (20, 27)
DEEPER = (51, 6)
RETURN = (48, 6)

PATH_POINTS = (
    ARRIVAL,
    (26, 27),
    (26, 21),
    (36, 21),
    (36, 14),
    (48, 14),
    (48, 6),
    DEEPER,
)

HEADER = [
    "; PHASE 9 - FEYWILD 1, THE RIVERBANK (52x36 tiles).",
    "; Chuck regains control beside the river from the ending cutscene.",
    "; A quiet luminous clearing leads from the shore past one Ashtray",
    "; to the Blooming Path deeper in the Feywild. No enemies are authored.",
]


def _path() -> set[tuple[int, int]]:
    cells: set[tuple[int, int]] = set()
    for (x0, y0), (x1, y1) in zip(PATH_POINTS, PATH_POINTS[1:]):
        if x0 == x1:
            for row in range(min(y0, y1), max(y0, y1) + 1):
                cells.update((x0 + dx, row) for dx in (-1, 0, 1))
        else:
            for col in range(min(x0, x1), max(x0, x1) + 1):
                cells.update((col, y0 + dy) for dy in (-1, 0, 1))
    return cells


def _river_edge(row: int) -> int:
    offsets = (0, 0, 1, 2, 2, 1, 0, -1, -1, 0, 1, 1)
    return 10 + offsets[row % len(offsets)]


def build() -> list[list[str]]:
    grid = [["."] * W for _ in range(H)]
    for col in range(W):
        grid[0][col] = "#"
        grid[H - 1][col] = "#"
    for row in range(H):
        grid[row][0] = "#"
        grid[row][W - 1] = "#"

    # The cutscene river runs down the west side. A two-tile irregular bank
    # keeps its edge organic while remaining solid water to tiny Chuck.
    for row in range(1, H - 1):
        edge = _river_edge(row)
        for col in range(1, edge + 1):
            grid[row][col] = "~"
        for col in (edge + 1, edge + 2):
            grid[row][col] = ","

    lane = _path()
    for col, row in lane:
        if grid[row][col] == ".":
            grid[row][col] = "'"

    # Dense growth forms broad rooms and bends around the authored route.
    # Deterministic clustered noise gives the clearing a handmade silhouette
    # without procedural runtime generation.
    groves = (
        (18, 7), (28, 8), (39, 8), (48, 11),
        (17, 17), (29, 16), (47, 20),
        (17, 32), (31, 31), (44, 30),
    )
    protected = {
        (col + dx, row + dy)
        for col, row in lane
        for dx in range(-2, 3)
        for dy in range(-2, 3)
    }
    protected |= {
        (cx + dx, cy + dy)
        for cx, cy in (ARRIVAL, ANCHOR, DEEPER, RETURN)
        for dx in range(-2, 3)
        for dy in range(-2, 3)
    }
    for row in range(1, H - 1):
        for col in range(1, W - 1):
            if grid[row][col] != "." or (col, row) in protected:
                continue
            distance = min(
                math.hypot(col - cx, row - cy) for cx, cy in groves
            )
            chance = 0.08 + 0.72 * max(0.0, 1.0 - distance / 6.2)
            roll = ((col * 47 + row * 83 + col * row * 13) % 100) / 100
            if roll < chance:
                grid[row][col] = "#"

    # Tall enchanted props rise out of the solid canopy; freestanding spiral
    # plants and mushrooms punctuate optional floor without blocking the route.
    for col, row in (
        (16, 5), (24, 6), (33, 7), (47, 9),
        (16, 18), (46, 19), (18, 33), (35, 31), (47, 29),
    ):
        if grid[row][col] == "#":
            grid[row][col] = "ł"
    for col, row in ((17, 24), (31, 25), (40, 17), (45, 24), (23, 12)):
        if grid[row][col] == ".":
            grid[row][col] = "Ł"
    for col, row in ((15, 30), (29, 18), (39, 25), (46, 15), (22, 9)):
        if grid[row][col] == ".":
            grid[row][col] = "ŋ"

    grid[ARRIVAL[1]][ARRIVAL[0]] = "Գ"
    grid[ANCHOR[1]][ANCHOR[0]] = "Դ"
    grid[RETURN[1]][RETURN[0]] = "Խ"
    # Chult-style wilderness handoff: a three-tile trail mouth cuts through
    # the actual map edge, with the stable boundary marker in its center.
    for row in range(DEEPER[1] - 1, DEEPER[1] + 2):
        grid[row][DEEPER[0]] = "→"
    grid[DEEPER[1]][DEEPER[0]] = "Ե"
    return grid


def validate(grid: list[list[str]]) -> None:
    blocked = {"#", "~", "ł", "Ł", "ŋ"}
    reached = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            x, y = point
            if (
                0 <= x < W and 0 <= y < H
                and point not in reached
                and grid[y][x] not in blocked
            ):
                reached.add(point)
                frontier.append(point)
    assert ANCHOR in reached, "arrival cannot reach the Feywild Ashtray"
    assert RETURN in reached, "arrival cannot reach the Blooming Path return"
    assert DEEPER in reached, "arrival cannot reach the deeper boundary"
    assert all(
        grid[row][W - 1] in {"→", "Ե"}
        for row in range(DEEPER[1] - 1, DEEPER[1] + 2)
    )
    assert sum(row.count("~") for row in grid) >= 300
    enemy_markers = set("()ѮԀԞ¡¶")
    assert not any(char in enemy_markers for row in grid for char in row)


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
