"""Author the collided-world traversal immediately before the Pit Fiend fight.

The route winds through rubble and around three small lava ponds, pauses at a
modern bus shelter whose commuter has noticed nothing unusual, then narrows
into four mandatory one-tile Astral jumps before the fortress. The roaming Pit
Fiend is enormous but far enough off the route to be avoided; flameskulls stay
with the ponds as distant setting motion rather than route gates.
"""

from __future__ import annotations

from collections import deque
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "maps" / "phlegethos_fractured_way.txt"

W, H = 76, 48
WEST_PASS = (1, 38)
ARRIVAL = (3, 38)
WAYPOINT = (15, 37)
NORTH_PASS = (60, 1)
RETURN_ARRIVAL = (60, 3)
PIT_FIEND = (25, 16)
BUS_STOP = (29, 30)
BUSINESSMAN = (32, 31)

PONDS = (
    (8, 8, 17, 14),
    (8, 20, 16, 26),
    (42, 35, 50, 42),
)
FLAMESKULLS = ((12, 11, "Ԛ"), (12, 23, "Ԛ"), (46, 38, "Ԛ"))
BUS_STOP_ASTRAL = (
    (22, 27), (22, 34), (23, 29), (24, 28), (25, 28), (27, 26),
    (33, 24), (34, 26), (37, 34), (26, 35), (24, 34),
)
COURSE_ROWS = (15, 12, 9, 6)

PATH_POINTS = (
    ARRIVAL,
    (18, 38),
    (18, 32),
    (36, 32),
    (36, 24),
    (48, 24),
    (48, 20),
    (60, 20),
    RETURN_ARRIVAL,
)

HEADER = [
    "; PHASE 8 - PHLEGETHOS 5, THE FRACTURED WAY (76x48 tiles).",
    "; Rubble and small lava ponds frame a safe winding route. Flameskulls",
    "; remain over the ponds as scenery; one distant Pit Fiend is avoidable.",
    "; A modern bus stop and oblivious commuter sit before four mandatory",
    "; one-tile Astral jumps.",
]


def _wide_path() -> set[tuple[int, int]]:
    lane: set[tuple[int, int]] = set()
    for (x0, y0), (x1, y1) in zip(PATH_POINTS, PATH_POINTS[1:]):
        if x0 == x1:
            for row in range(min(y0, y1), max(y0, y1) + 1):
                lane.update((x0 + dx, row) for dx in (-1, 0, 1))
        else:
            for col in range(min(x0, x1), max(x0, x1) + 1):
                lane.update((col, y0 + dy) for dy in (-1, 0, 1))
    return {
        (col, row) for col, row in lane
        if 2 <= col < W - 2 and 2 <= row < H - 2
    }


def build() -> list[list[str]]:
    grid = [["·"] * W for _ in range(H)]
    for col in range(W):
        for row in (0, 1, H - 2, H - 1):
            grid[row][col] = "█"
    for row in range(H):
        for col in (0, 1, W - 2, W - 1):
            grid[row][col] = "█"

    lane = _wide_path()

    # Three contained ponds animate beside the route without becoming its
    # challenge. Their skulls have enough molten room for the full weave.
    for left, top, right, bottom in PONDS:
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                grid[row][col] = "≋"

    # The required route is broad and calm until the authored Astral course.
    for col, row in lane:
        if grid[row][col] == "·":
            grid[row][col] = "≡"

    protected = {
        (col + dx, row + dy)
        for col, row in lane
        for dx in range(-2, 3)
        for dy in range(-2, 3)
    }
    protected.update(
        (BUS_STOP[0] + dx, BUS_STOP[1] + dy)
        for dx in range(-5, 6)
        for dy in range(-4, 5)
    )
    protected.update(
        (PIT_FIEND[0] + dx, PIT_FIEND[1] + dy)
        for dx in range(-5, 6)
        for dy in range(-4, 5)
    )

    # Deterministic heaps form walls and pockets rather than uniform noise.
    piles = (
        (5, 5), (22, 7), (37, 9), (53, 8), (69, 11),
        (5, 31), (27, 23), (44, 29), (57, 37), (69, 41),
    )
    for row in range(2, H - 2):
        for col in range(2, W - 2):
            if grid[row][col] != "·" or (col, row) in protected:
                continue
            near = min(math.hypot(col - px, row - py) for px, py in piles)
            probability = 0.08 + 0.48 * max(0.0, 1.0 - near / 6.5)
            roll = ((col * 47 + row * 89 + col * row * 13) % 100) / 100
            if roll < probability:
                grid[row][col] = "þ"
            elif (col * 23 + row * 31) % 79 == 0:
                grid[row][col] = "♨"

    # A seven-tile channel is hemmed in by cliff-backed Astral walls. Four
    # single rows cut it crosswise: each is jumpable, none is walkable, and
    # the surrounding basalt cannot be used to walk around the course.
    for row in range(2, 20):
        for col in (*range(51, 54), *range(67, 70)):
            grid[row][col] = "█"
    for row in range(3, 18):
        for col in (*range(54, 57), *range(64, 67)):
            grid[row][col] = "V"
    for row in COURSE_ROWS:
        for col in range(57, 64):
            grid[row][col] = "V"

    # A few wrong-world fragments gather around the bus stop without closing
    # its broad paved approach or preventing Chuck from reaching the commuter.
    for col, row in BUS_STOP_ASTRAL:
        assert (col, row) not in lane
        grid[row][col] = "V"

    # The displaced city scene: shelter behind, commuter on clear pavement.
    grid[BUS_STOP[1]][BUS_STOP[0]] = "☂"
    grid[BUSINESSMAN[1]][BUSINESSMAN[0]] = "ዕ"

    # All motion besides the optional Pit Fiend belongs over the lava ponds.
    grid[PIT_FIEND[1]][PIT_FIEND[0]] = "ዓ"
    for col, row, marker in FLAMESKULLS:
        assert grid[row][col] == "≋"
        grid[row][col] = marker

    grid[WEST_PASS[1]][WEST_PASS[0]] = "«"
    for col in range(NORTH_PASS[0] - 1, NORTH_PASS[0] + 2):
        grid[NORTH_PASS[1]][col] = "∇"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ዐ"
    grid[RETURN_ARRIVAL[1]][RETURN_ARRIVAL[0]] = "ዒ"
    return grid


_UNDER = {
    "ዐ": "≡", "ዒ": "≡", "ዓ": "·", "ዕ": "≡",
    "Ԛ": "≋", "Ԝ": "≋",
}
_SOLID = {"█", "þ", "☂"}
_HAZARD = {"V", "≋"}


def _terrain(grid: list[list[str]], point: tuple[int, int]) -> str:
    col, row = point
    return _UNDER.get(grid[row][col], grid[row][col])


def _reachable(
    grid: list[list[str]], *, allow_hops: bool,
) -> set[tuple[int, int]]:
    reached = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for dc, dr in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            step = (col + dc, row + dr)
            if not (0 <= step[0] < W and 0 <= step[1] < H):
                continue
            terrain = _terrain(grid, step)
            destination = step
            if terrain in _HAZARD and allow_hops:
                destination = (col + dc * 2, row + dr * 2)
                if not (0 <= destination[0] < W and 0 <= destination[1] < H):
                    continue
                if _terrain(grid, destination) in (_SOLID | _HAZARD):
                    continue
            elif terrain in (_SOLID | _HAZARD):
                continue
            if destination not in reached:
                reached.add(destination)
                frontier.append(destination)
    return reached


def validate(grid: list[list[str]]) -> tuple[int, int]:
    assert len(grid) == H and all(len(row) == W for row in grid)
    walking = _reachable(grid, allow_hops=False)
    hopping = _reachable(grid, allow_hops=True)
    assert WAYPOINT in walking and BUSINESSMAN in walking
    assert RETURN_ARRIVAL not in walking, "Astral course can be walked"
    assert RETURN_ARRIVAL in hopping and NORTH_PASS in hopping
    assert math.dist(PIT_FIEND, min(PATH_POINTS, key=lambda p: math.dist(
        PIT_FIEND, p))) > 8.0
    assert all(_terrain(grid, (col, row)) == "≋"
               for col, row, _marker in FLAMESKULLS)
    assert sum(row.count("ዓ") for row in grid) == 1
    assert sum(row.count("ዕ") for row in grid) == 1
    assert sum(row.count("☂") for row in grid) == 1
    assert sum(row.count("V") for row in grid) >= 100
    return (
        sum(row.count("þ") for row in grid),
        sum(row.count("≋") for row in grid),
    )


def main() -> None:
    grid = build()
    rubble, lava = validate(grid)
    OUT.write_text(
        "\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} ({W}x{H}); {rubble} rubble, {lava} lava tiles")


if __name__ == "__main__":
    main()
