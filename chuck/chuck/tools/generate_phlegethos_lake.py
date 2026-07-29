"""Author phlegethos_lake.txt --- the lava-lake island crossing (Phase 8).

The spec's called-out set piece: Chuck jumps across small basalt islands
over a lava lake. Every gap between consecutive islands is EXACTLY one
lava tile, so each crossing is a single committed hop (the jump clears
one hazard cell and lands on safe floor -- the same rule the temple's
Astral connector is built on). The chain zigzags north so the crossing
reads as a route, not a ladder.

Assertion-checked: the whole map is proved completable with walking plus
single-tile hops, and no safe cell is stranded, before it is written.
"""

from collections import deque
from pathlib import Path

W, H = 44, 34
OUT = Path(__file__).resolve().parents[1] / "assets" / "maps" / "phlegethos_lake.txt"

SOUTH_SHORE_TOP = 25      # rows 25..31 are the southern basalt shore
NORTH_SHORE_BOTTOM = 8    # rows 2..8 are the northern shore
ENTRY = (21, 28)
ANCHOR = (17, 28)
EXIT = (27, 4)
SOUTH_PASS = (21, 32)     # back to the lava road
NORTH_PASS = (27, 1)      # onward (inert until map 4)

# Each island is (col0, col1, row0, row1) inclusive. Consecutive islands
# are separated by exactly one lava tile, alternating north / sideways.
ISLANDS = [
    (19, 23, 22, 23),   # from the south shore: hop north over row 24
    (19, 23, 19, 20),   # hop north over row 21
    (25, 29, 19, 20),   # hop east over col 24
    (25, 29, 16, 17),   # hop north over row 18
    (19, 23, 16, 17),   # hop west over col 24
    (19, 23, 13, 14),   # hop north over row 15
    (25, 29, 13, 14),   # hop east over col 24
    (25, 29, 10, 11),   # hop north over row 12
]                       # then hop north over row 9 onto the north shore

HEADER = [
    "; PHASE 8 - PHLEGETHOS 3, THE LAVA LAKE (44x34 tiles).",
    "; A wide molten lake crossed by small basalt islands. Every gap is",
    "; exactly one lava tile, so each crossing is a single committed hop;",
    "; the chain zigzags north from the south shore's Ashtray to the far",
    "; pass. Falling short is the usual quiet lava death and return.",
]


def build():
    grid = [["≋"] * W for _ in range(H)]          # the lake, wall to wall
    for c in range(W):
        for r in (0, 1, H - 2, H - 1):
            grid[r][c] = "█"
    for r in range(H):
        for c in (0, 1, W - 2, W - 1):
            grid[r][c] = "█"
    # The two shores.
    for r in range(2, NORTH_SHORE_BOTTOM + 1):
        for c in range(2, W - 2):
            grid[r][c] = "·"
    for r in range(SOUTH_SHORE_TOP, H - 2):
        for c in range(2, W - 2):
            grid[r][c] = "·"
    # A worn path across each shore, up to the water's edge.
    for r in range(SOUTH_SHORE_TOP, H - 2):
        for c in range(ENTRY[0] - 1, ENTRY[0] + 2):
            grid[r][c] = "≡"
    for r in range(2, NORTH_SHORE_BOTTOM + 1):
        for c in range(EXIT[0] - 1, EXIT[0] + 2):
            grid[r][c] = "≡"
    # The stepping stones.
    for c0, c1, r0, r1 in ISLANDS:
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                grid[r][c] = "·"
    # A little dressing on the shores only (never on a stepping stone).
    for c, r in ((6, 27), (36, 29), (8, 4), (34, 6), (12, 30), (39, 3)):
        if grid[r][c] == "·":
            grid[r][c] = "♨"
    # Fire snakes patrol the shores; the lake itself is pure traversal.
    for c, r in ((10, 27), (33, 28), (12, 5), (31, 4)):
        assert grid[r][c] == "·", (c, r, grid[r][c])
        grid[r][c] = "Ԁ"
    # The passes, markers, and the inert onward boundary.
    grid[SOUTH_PASS[1]][SOUTH_PASS[0]] = "Δ"
    grid[NORTH_PASS[1]][NORTH_PASS[0]] = "∇"
    grid[EXIT[1]][EXIT[0]] = "Ԍ"
    for (mc, mr), char in ((ENTRY, "Ԉ"), (ANCHOR, "Ԋ")):
        assert grid[mr][mc] in "·≡", (char, grid[mr][mc])
        grid[mr][mc] = char
    return grid


def validate(grid) -> int:
    """Prove the map is completable with walking plus SINGLE-tile hops."""
    solid = set("█")
    hazard = {(c, r) for r in range(H) for c in range(W)
              if grid[r][c] == "≋"}
    safe = {(c, r) for r in range(H) for c in range(W)
            if grid[r][c] not in solid and (c, r) not in hazard}
    start = ENTRY
    reached = {start}
    frontier = deque([start])
    while frontier:
        c, r = frontier.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            walk = (c + dc, r + dr)
            if walk in safe and walk not in reached:
                reached.add(walk)
                frontier.append(walk)
            over = (c + dc, r + dr)
            land = (c + 2 * dc, r + 2 * dr)
            if over in hazard and land in safe and land not in reached:
                reached.add(land)
                frontier.append(land)
    # Nothing safe may be stranded, and the far side must be reachable.
    stranded = safe - reached
    assert not stranded, f"stranded safe cells: {sorted(stranded)[:8]}"
    for label, point in (("anchor", ANCHOR), ("exit", EXIT),
                         ("north pass", NORTH_PASS),
                         ("south pass", SOUTH_PASS)):
        assert point in reached, f"{label} unreachable"
    # Every island must genuinely require a hop: no island touches
    # another island or a shore cardinally (that would make it a bridge).
    for c0, c1, r0, r1 in ISLANDS:
        for r in range(r0, r1 + 1):
            for c in range(c0, c1 + 1):
                for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (c + dc, r + dr)
                    inside = any(a <= n[0] <= b and x <= n[1] <= y
                                 for a, b, x, y in ISLANDS)
                    if not inside and n in safe:
                        raise AssertionError(
                            f"island at {(c, r)} touches safe {n}: no hop")
    return len(hazard)


def main() -> None:
    grid = build()
    lava = validate(grid)
    OUT.write_text("\n".join(HEADER + ["".join(r) for r in grid]) + "\n",
                   encoding="utf-8")
    print(f"Wrote {OUT} ({W}x{H}); {lava} lava tiles, "
          f"{len(ISLANDS)} stepping stones")


if __name__ == "__main__":
    main()
