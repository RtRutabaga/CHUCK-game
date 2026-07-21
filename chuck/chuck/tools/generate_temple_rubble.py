"""Author temple_rubble.txt — the collapsed map after the Fireball
(sessions 135, 138, 139).

Where the scripted Fireball throws Chuck: the temple's ceiling has caved
in. The chamber is choked with fallen stone ('█' masonry rubble and '¬'
toppled columns) and split open by numerous blocks of Astral Sea ('V',
the walkable-but-lethal fall hazard) — it is almost impossible to pick a
way across. But one route stays clear: a torch-lit lane winds from the
`from_fireball` arrival, past the rubble ashtray, to the one way out —
the crawlspace mouth ('∇') in the south wall that leads to the ship deck.
The open lane amid the debris makes the escape route obvious.

Assertion-checked: the clear lane connects the arrival, the anchor, and
the crawlspace on foot (treating rubble and Astral as impassable) before
the map is written.
"""

from collections import deque
from pathlib import Path

W, H = 48, 30
OUT = Path(__file__).resolve().parents[1] / "assets" / "maps" / "temple_rubble.txt"

ARRIVAL = (23, 5)      # where the blast throws Chuck in
ANCHOR = (23, 24)      # the rubble ashtray, passed on the way out
CRAWL = (34, 28)       # the crawlspace mouth, carved into the south wall

# The clear escape lane, as a polyline of axis-aligned segments. It is
# widened to three tiles so it reads as an open route through the debris.
PATH_POINTS = [
    (23, 5), (23, 11), (30, 11), (30, 18),
    (20, 18), (20, 24), (34, 24), (34, 27),
]

HEADER = [
    "; PHASE 6 - RUBBLE MAP (48x30 tiles).",
    "; The temple's ceiling has caved in: the chamber is choked with big",
    "; broken masonry blocks and split by blocks of Astral Sea. One clear",
    "; paved lane stays open - from the arrival, past the ashtray, to the",
    "; crawlspace mouth in the south wall (the one way out, to the ship).",
]


def _diamond(cx, cy, r):
    return {(cx + dx, cy + dy)
            for dx in range(-r, r + 1)
            for dy in range(-r, r + 1)
            if abs(dx) + abs(dy) <= r}


def _clear_lane() -> set:
    """The three-wide open lane along PATH_POINTS, plus room at the ends."""
    lane = set()
    for (x0, y0), (x1, y1) in zip(PATH_POINTS, PATH_POINTS[1:]):
        if x0 == x1:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                lane |= {(x0 - 1, y), (x0, y), (x0 + 1, y)}
        else:
            for x in range(min(x0, x1), max(x0, x1) + 1):
                lane |= {(x, y0 - 1), (x, y0), (x, y0 + 1)}
    for cx, cy in (ARRIVAL, ANCHOR, (CRAWL[0], CRAWL[1] - 1)):
        lane |= {(cx + dx, cy + dy)
                 for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
    return {(c, r) for (c, r) in lane if 2 <= c < W - 2 and 2 <= r < H - 2}


def build():
    grid = [["·" for _ in range(W)] for _ in range(H)]
    # Two-tile solid border, the chamber's broken outer wall.
    for c in range(W):
        for r in (0, 1, H - 2, H - 1):
            grid[r][c] = "█"
    for r in range(H):
        for c in (0, 1, W - 2, W - 1):
            grid[r][c] = "█"

    lane = _clear_lane()

    # Astral Sea: significant, distinct blocks torn through the floor,
    # set well off the clear lane so the route stays obvious.
    astral_blocks = [
        (7, 5, 2), (6, 11, 2), (7, 17, 3), (6, 24, 2), (13, 21, 2),
        (12, 8, 2), (41, 6, 2), (43, 13, 2), (41, 19, 3), (42, 25, 2),
        (37, 10, 2), (38, 16, 2), (27, 7, 2), (26, 15, 2), (27, 22, 2),
    ]
    astral = set()
    for cx, cy, r in astral_blocks:
        for c, rr in _diamond(cx, cy, r):
            if 2 <= c < W - 2 and 2 <= rr < H - 2 and (c, rr) not in lane:
                astral.add((c, rr))

    for c, r in astral:
        grid[r][c] = "V"

    # Pave the escape lane with the temple's processional path ('≡'): the
    # one intact strip of floor through the collapse. Against the debris
    # it reads, unmistakably, as the way out.
    for c, r in lane:
        if grid[r][c] == "·":
            grid[r][c] = "≡"

    # Fallen ceiling: a dense field of big broken masonry blocks ('ß'),
    # with a scattering of smaller toppled column drums ('¬') for scale.
    # Thick enough to make the chamber almost impassable off the paved
    # lane. Deterministic hash, so the render is reproducible.
    rubble = 0
    for cy in range(2, H - 2):
        for cx in range(2, W - 2):
            if grid[cy][cx] != "·":       # skip the lane, Astral, border
                continue
            h = (cx * 37 + cy * 101 + cx * cy * 3) % 100
            if h < 50:
                grid[cy][cx] = "¬" if h % 6 == 0 else "ß"
                rubble += 1

    # Carve the crawlspace mouth into the south wall at the lane's foot,
    # with the "Enter crevice?" prompt on the lane just before it.
    cx, cy = CRAWL
    assert grid[cy][cx] == "█", grid[cy][cx]
    grid[cy][cx] = "∇"
    assert grid[cy - 1][cx] == "≡", grid[cy - 1][cx]
    grid[cy - 1][cx] = "Ҏ"

    # Place the markers last so they sit on the paved lane.
    for (mx, my), glyph in ((ARRIVAL, "Ѣ"), (ANCHOR, "Ѥ")):
        assert grid[my][mx] == "≡", (glyph, grid[my][mx])
        grid[my][mx] = glyph

    return grid, rubble, astral


def solid(ch):
    # Border and fallen masonry (blocks/columns) block; Astral is a
    # walkable fall hazard; markers and the crawl mouth sit on floor.
    return ch in "█¬ß"


def validate(grid):
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
    grid, rubble, astral = build()
    validate(grid)
    lines = HEADER + ["".join(row) for row in grid]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({W}x{H}); {rubble} rubble, {len(astral)} astral")


if __name__ == "__main__":
    main()
