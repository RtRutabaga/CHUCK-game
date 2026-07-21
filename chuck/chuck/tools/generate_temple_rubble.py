"""Author temple_rubble.txt — the collapsed map after the Fireball (session 135).

Where the scripted Fireball throws Chuck: a broken chamber strewn with
Astral Sea hazard blocks ('V', the established walkable fall hazard).
Chuck lands at the top on the `from_fireball` arrival; an Astral Anchor
(the rubble ashtray) sits at the bottom. A clear central spine keeps
the arrival connected to the anchor on foot, and a single narrow lane
runs down the right side to the one way out: a crawlspace mouth ('∇')
in the south wall that leads to the ship deck (session 138). Assertion-
checked: connectivity to both the anchor and the crawlspace is proven
before writing.
"""

from collections import deque
from pathlib import Path

W, H = 48, 30
OUT = Path(__file__).resolve().parents[1] / "assets" / "maps" / "temple_rubble.txt"

ARRIVAL = (23, 5)      # where the blast throws Chuck in
ANCHOR = (23, 24)      # the rubble ashtray
CRAWL_COL = 34         # the escape lane runs down this column
CRAWL = (CRAWL_COL, 28)  # the crawlspace mouth, carved into the south wall

HEADER = [
    "; PHASE 6 - RUBBLE MAP (48x30 tiles).",
    "; Where the scripted Fireball throws Chuck: a collapsed chamber",
    "; strewn with Astral Sea hazard blocks. He lands at the top with",
    "; half his Sanity; the rubble ashtray waits below. The one way out",
    "; is the crawlspace mouth in the south wall, down the right lane.",
]


def _diamond(cx, cy, r):
    return {(cx + dx, cy + dy)
            for dx in range(-r, r + 1)
            for dy in range(-r, r + 1)
            if abs(dx) + abs(dy) <= r}


def build():
    grid = [["·" for _ in range(W)] for _ in range(H)]
    # Two-tile solid border, the chamber's broken outer wall.
    for c in range(W):
        for r in (0, 1, H - 2, H - 1):
            grid[r][c] = "█"
    for r in range(H):
        for c in (0, 1, W - 2, W - 1):
            grid[r][c] = "█"

    # Protected cells that must stay walkable floor: 3x3 around the
    # arrival and anchor, and a central spine linking them.
    protected = set()
    for cx, cy in (ARRIVAL, ANCHOR):
        protected |= {(cx + dx, cy + dy)
                      for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    for row in range(ARRIVAL[1], ANCHOR[1] + 1):
        protected |= {(22, row), (23, row), (24, row)}
    # Two clear cross-bands so the spine isn't a lone corridor.
    for col in range(3, W - 3):
        protected |= {(col, 9), (col, 20)}
    # The escape lane: a clear column from the lower cross-band down to
    # the crawlspace mouth, so the one way out is always reachable.
    for row in range(20, 28):
        protected.add((CRAWL_COL, row))

    # Astral Sea fields — irregular diamond blobs of broken reality on
    # either side of the spine, avoiding the protected floor.
    blobs = [
        (7, 5, 2), (12, 6, 1), (6, 13, 2), (11, 15, 1), (8, 24, 2),
        (14, 25, 1), (17, 13, 1), (16, 17, 2), (13, 11, 1),
        (40, 5, 2), (35, 6, 1), (41, 13, 2), (36, 15, 1), (39, 24, 2),
        (33, 25, 1), (30, 13, 1), (31, 17, 2), (34, 11, 1),
        (23, 14, 1),  # a lone island of danger straddling the spine's edge
    ]
    astral = set()
    for cx, cy, r in blobs:
        for c, r2 in _diamond(cx, cy, r):
            if 2 <= c < W - 2 and 2 <= r2 < H - 2 and (c, r2) not in protected:
                astral.add((c, r2))
    for c, r in astral:
        grid[r][c] = "V"

    # Wall-mounted torches for light, on the interior faces of the border.
    for c, r in ((10, 1), (23, 1), (37, 1), (10, H - 2), (37, H - 2),
                 (1, 9), (1, 20), (W - 2, 9), (W - 2, 20)):
        grid[r][c] = "i"

    # A little fallen-temple dressing among the rubble.
    for c, r in ((19, 6), (28, 6), (20, 23), (27, 23)):
        if (c, r) not in astral and (c, r) not in protected:
            grid[r][c] = "¬"  # toppled columns
    for c, r in ((23, 3), (23, 26)):
        grid[r][c] = "‡"  # a standing stela at each end

    # Carve the crawlspace mouth into the south wall at the lane's foot.
    cx, cy = CRAWL
    assert grid[cy][cx] == "█", grid[cy][cx]
    grid[cy][cx] = "∇"

    # Place the markers last so they sit on known floor.
    ax, ay = ARRIVAL
    assert grid[ay][ax] == "·", grid[ay][ax]
    grid[ay][ax] = "Ѣ"
    nx, ny = ANCHOR
    assert grid[ny][nx] == "·", grid[ny][nx]
    grid[ny][nx] = "Ѥ"

    return grid, astral


def solid(ch):
    # Border, dressing columns/stelae, and torches are solid; astral is
    # a walkable fall hazard; markers and the crawl mouth sit on floor.
    return ch in "█¬‡i"


def validate(grid):
    # The arrival reaches the anchor AND the crawlspace on foot, treating
    # Astral as a wall (walkable fall hazard, but lethal to cross).
    def blocked(c, r):
        ch = grid[r][c]
        return solid(ch) or ch == "V"

    start = ARRIVAL
    seen = {start}
    q = deque([start])
    while q:
        c, r = q.popleft()
        for nc, nr in ((c - 1, r), (c + 1, r), (c, r - 1), (c, r + 1)):
            if (0 <= nc < W and 0 <= nr < H and (nc, nr) not in seen
                    and not blocked(nc, nr)):
                seen.add((nc, nr))
                q.append((nc, nr))
    assert ANCHOR in seen, "arrival cannot reach the anchor on foot!"
    assert CRAWL in seen, "arrival cannot reach the crawlspace on foot!"


def main():
    grid, astral = build()
    validate(grid)
    lines = HEADER + ["".join(row) for row in grid]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({W}x{H}), {len(astral)} astral tiles")


if __name__ == "__main__":
    main()
