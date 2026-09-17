"""Generate Chult Falls: the hidden map off Chult 4's western pocket.

A plunge pool under a cliff, the way the reference has it: a dark rock
face across the north with the fall coming out of a notch in its lip, a
small pool at its foot ringed with boulders, and a river running out of
the pool's south end and off the bottom of the map through the jungle.

The river is Chult 4's own stream tile and one tile wide, so it takes the
jump to cross, and it runs from the pool to the map's south edge: it cuts
the map in two. The way in from Chult 4 lands on the east bank. The chest
-- the ruin chest's twin, with its own flags and its own carton of
premium Buhetian halfling leaf -- is on the west bank, tucked into a nook
of ferns a little way down from the pool. Nothing on the east bank says
so; the pool's west shore is in plain sight across the water.

The way back is the east edge, under the jungle arch Chult's other exits
use -- the hidden one is hidden from Chult 4's side only.
"""

from __future__ import annotations

import math
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "maps" / "chult_falls.txt"
W, H = 48, 40

GROUND = "."
JUNGLE = "#"
STREAM = "≈"
CLIFF = "Ꝙ"
BOULDER = "Ꝛ"
BOULDER_WATER = "Ꝝ"
CHEST = "Ꝟ"
ARRIVAL = "Ꝗ"
TORTLE = "Ꝡ"
EXIT = "ð"
TRAIL = "'"
FERN = "ꝭ"
LITTER = "ꝯ"
GRASS = "<"

CLIFF_ANCHOR = (24, 9)
CLIFF_COLS = range(14, 35)
POOL_ROWS = range(10, 15)
ARRIVAL_TILE = (42, 24)
EXIT_ROWS = range(23, 26)
CHEST_TILE = (13, 22)
# He stands just past the chest, between it and the river.
TORTLE_TILE = (15, 22)
EAST_GRASS = ((34, 21), (37, 30), (31, 35))
WEST_GRASS = ((10, 27), (17, 33))
SHORE_BOULDERS = ((15, 17), (33, 16), (31, 18), (18, 18), (13, 15))
POOL_BOULDERS = ((19, 12), (28, 13), (21, 11))


def _hash(*values: int) -> int:
    h = 2166136261
    for value in values:
        h = ((h ^ (value & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def river_col(row: int) -> int:
    return 24 + round(2.5 * math.sin((row - 17) / 4.5))


def build() -> list[list[str]]:
    grid = [[JUNGLE] * W for _ in range(H)]

    # The clearing under the cliff: ground in a broad oval round the pool.
    for row in range(8, 30):
        for col in range(2, W - 2):
            if ((col - 24) / 17.5) ** 2 + ((row - 16) / 11.5) ** 2 <= 1:
                grid[row][col] = GROUND
    # The river's banks, ragged, both sides all the way south.
    for row in range(17, H - 1):
        centre = river_col(row)
        for side in (-1, 1):
            reach = 4 + _hash(row, side, 3) % 4
            for step in range(1, reach + 1):
                col = centre + side * step
                if 1 <= col < W - 1:
                    grid[row][col] = GROUND
    # The cliff: solid rock across the north, whatever the oval said.
    for row in range(0, 10):
        for col in range(12, 37):
            grid[row][col] = JUNGLE
    # The pool: flat along the cliff's foot, rounded to the south. Small
    # -- a plunge pool, not a lake. A wide one pushed the only shore you
    # could stand on so far south that the fall itself was off the top of
    # the screen from everywhere you could get to.
    for row in POOL_ROWS:
        for col in range(14, 36):
            if ((col - 24.5) / 7) ** 2 + ((row - 10) / 4) ** 2 <= 1:
                grid[row][col] = STREAM
    # The river, one tile wide and unbroken from the pool to the south edge.
    previous = None
    for row in range(13, H):
        col = river_col(row)
        grid[row][col] = STREAM
        if previous is not None and previous != col:
            step = 1 if col > previous else -1
            for between in range(previous, col, step):
                grid[row][between] = STREAM
        previous = col
    # The way in and out: a corridor from the east bank to the east edge.
    for row in EXIT_ROWS:
        for col in range(30, W):
            if grid[row][col] != STREAM:
                grid[row][col] = GROUND
        for col in range(W - 3, W):
            grid[row][col] = EXIT
    grid[ARRIVAL_TILE[1]][ARRIVAL_TILE[0]] = ARRIVAL
    grid[ARRIVAL_TILE[1]][ARRIVAL_TILE[0] + 1] = TRAIL

    # The chest's nook on the west bank.
    col, row = CHEST_TILE
    for y in range(row - 2, row + 3):
        for x in range(col - 3, col + 3):
            if grid[y][x] == JUNGLE and _hash(x, y, 7) % 3:
                grid[y][x] = GROUND
    grid[row][col] = CHEST
    grid[TORTLE_TILE[1]][TORTLE_TILE[0]] = TORTLE

    grid[CLIFF_ANCHOR[1]][CLIFF_ANCHOR[0]] = CLIFF
    for col, row in SHORE_BOULDERS:
        assert grid[row][col] == GROUND, (col, row, grid[row][col])
        grid[row][col] = BOULDER
    for col, row in POOL_BOULDERS:
        assert grid[row][col] == STREAM, (col, row, grid[row][col])
        grid[row][col] = BOULDER_WATER
    for col, row in EAST_GRASS + WEST_GRASS:
        if grid[row][col] == GROUND:
            grid[row][col] = GRASS

    # Ferns and litter over open ground, away from everything placed.
    for row in range(1, H - 1):
        for col in range(1, W - 1):
            if grid[row][col] != GROUND:
                continue
            if any(grid[y][x] not in (GROUND, JUNGLE, FERN, LITTER)
                   for y in range(row - 1, row + 2)
                   for x in range(col - 1, col + 2)):
                continue
            roll = _hash(col, row, 13) % 100
            if roll < 5:
                grid[row][col] = FERN
            elif roll < 9:
                grid[row][col] = LITTER

    # Trees on the jungle mass, but none against the cliff.
    for row in range(1, H - 1):
        for col in range(1, W - 1):
            if grid[row][col] != JUNGLE:
                continue
            if row < 10 and 11 <= col <= 37:
                continue
            roll = _hash(col, row, 29) % 100
            if roll < 14:
                grid[row][col] = "/"
            elif roll < 26:
                grid[row][col] = "\\"
    return grid


def _walkable(char: str) -> bool:
    return char in (GROUND, TRAIL, ARRIVAL, TORTLE, FERN, LITTER, EXIT)


def reachable(grid, start, jump_stream: bool = False) -> set[tuple[int, int]]:
    seen = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            x, y = col + dx, row + dy
            if not (0 <= x < W and 0 <= y < H) or (x, y) in seen:
                continue
            if _walkable(grid[y][x]):
                seen.add((x, y))
                frontier.append((x, y))
            elif jump_stream and grid[y][x] == STREAM:
                # One committed jump clears a single stream tile.
                lx, ly = x + dx, y + dy
                if 0 <= lx < W and 0 <= ly < H and _walkable(grid[ly][lx]) \
                        and (lx, ly) not in seen:
                    seen.add((lx, ly))
                    frontier.append((lx, ly))
    return seen


def validate(grid) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)
    start = ARRIVAL_TILE
    east = reachable(grid, start)
    chest_col, chest_row = CHEST_TILE
    chest_side = {(chest_col + 1, chest_row), (chest_col - 1, chest_row),
                  (chest_col, chest_row + 1), (chest_col, chest_row - 1)}
    # The chest cannot be walked to from the way in...
    assert not chest_side & east
    # ...and can be reached with the jump over the river.
    assert chest_side & reachable(grid, start, jump_stream=True)
    # The river runs unbroken from the pool to the south edge.
    stream = {(c, r) for r in range(H) for c in range(W)
              if grid[r][c] in (STREAM, BOULDER_WATER)}
    assert any(r == H - 1 for _c, r in stream)


def main() -> None:
    grid = build()
    validate(grid)
    header = (
        "; CHULT FALLS - the hidden map off Chult 4's western pocket (48x40).\n"
        "; A plunge pool under a cliff and its fall; a one-tile river runs out\n"
        "; of the pool and off the south edge, splitting the map. The way in\n"
        "; lands on the east bank; the chest is across the river, on the west.\n"
    )
    OUT.write_text(header + "\n".join("".join(row) for row in grid) + "\n",
                   encoding="utf-8")
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
