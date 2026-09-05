"""Generate the Phase 13 desert orc camp -- north of the hub.

The phase document asks for a canyon: brown rock closing the north and
west edges, so that walking up here feels like walking into the back of
something rather than out into more desert. So the rock is not a rim
here, it is a mass. It comes down the west side and across the north in
an uneven front several tiles deep, and the only ways out of the map
are the way in from the south and nothing else.

The camp itself is deliberately plain. A ring of beaten ground where
the orcs have worn the ripple off the sand, stores stacked against the
cliff where the shade is, and a scatter of orcs between the player and
them. There is no treasure here and nothing to solve: the point of the
place is that a player who explores north finds a fight, learns what an
orc is, and can leave again.

The stores are the pantry's own scratchable sacks. They are worth
walking into the camp for, and walking into the camp is the risk.
"""

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 64
HEIGHT = 48

# The way back to the hub, in the middle of the south edge, matching the
# gap it comes out of.
GAP = 5
RIM = 1
# How far back from the way in the ground is kept clear of everything --
# an orc standing in the doorway is an ambush, not an encounter.
APPROACH = 5

# The cliff front. North and west are rock; the mass is uneven so it
# reads as a canyon wall rather than as a border drawn round the map.
NORTH_ROCK = 9      # deepest the northern front comes down
WEST_ROCK = 8       # ...and how far in the western one reaches

# The beaten ground the camp stands on, and where its stores are stacked
# against the western cliff in the shade.
CAMP = (22, 14, 26, 18)     # left, top, width, height
SACKS = ((25, 18), (26, 21), (25, 24), (28, 16), (29, 27),
         (33, 15), (41, 17), (43, 22), (39, 28), (44, 27))
# Fires: burnt-out rings of rock, the only built thing in the camp.
FIRES = ((31, 21), (40, 24), (36, 27), (27, 17))
ORCS = ((30, 26), (37, 19), (44, 19), (35, 30), (27, 15),
        (46, 25), (33, 24))
ANCHOR = (32, 39)   # south of the camp, in the open, before the fight
START = (32, 44)    # ...and the way in, below it


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _cliffs(grid) -> None:
    """The canyon: rock down the west side and across the north.

    Both fronts wander. Ruled straight they read as a border someone
    drew round the map; a cliff is a thing with a shape, and the shape
    is most of what makes this feel like the back of somewhere.
    """
    for x in range(WIDTH):
        depth = NORTH_ROCK - round(3.0 * math.sin(x / 7.0 + 1.2)) \
            - round(1.5 * math.sin(x / 3.0))
        # The west corner is the deepest part of it: the two fronts meet
        # there rather than crossing at a right angle.
        if x < WEST_ROCK + 4:
            depth += (WEST_ROCK + 4 - x)
        _rect(grid, x, 0, x, max(0, depth), "#")
    for y in range(HEIGHT):
        reach = WEST_ROCK - round(2.5 * math.sin(y / 6.0)) \
            - round(1.0 * math.sin(y / 2.5))
        _rect(grid, 0, y, max(0, reach), y, "#")
    # East and south are ordinary rim, except where the way back is cut.
    _rect(grid, WIDTH - RIM, 0, WIDTH - 1, HEIGHT - 1, "#")
    _rect(grid, 0, HEIGHT - RIM, WIDTH - 1, HEIGHT - 1, "#")


def _weather(grid) -> None:
    """Ripple and shadowed sand, away from the camp."""
    patches = (
        (14, 34, 14, 5, ","), (46, 32, 13, 6, ","), (12, 20, 8, 7, ","),
        (50, 12, 11, 5, ","), (20, 41, 12, 3, "⟁"), (48, 41, 12, 4, "⟁"),
        (14, 28, 7, 4, "⟁"), (52, 20, 8, 6, "⟁"),
    )
    for left, top, width, height, char in patches:
        for y in range(top, top + height):
            for x in range(left, left + width):
                if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                    continue
                nx = (x - (left + width / 2)) / (width / 2)
                ny = (y - (top + height / 2)) / (height / 2)
                if math.hypot(nx, ny) > 0.85 + ((x * 7 + y * 13) % 5) / 12:
                    continue
                if grid[y][x] == ".":
                    grid[y][x] = char


def _camp(grid) -> None:
    """Beaten ground, fire rings, and the stores against the cliff.

    The camp floor is ripple-free sand with a soft edge: orcs walking
    over the same ground for long enough is the only thing that would
    flatten a desert, and a hard rectangle of it would read as a rug.
    """
    left, top, width, height = CAMP
    for y in range(top, top + height):
        for x in range(left, left + width):
            if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                continue
            nx = (x - (left + width / 2)) / (width / 2)
            ny = (y - (top + height / 2)) / (height / 2)
            if math.hypot(nx, ny) > 0.95 + ((x * 5 + y * 11) % 4) / 10:
                continue
            if grid[y][x] in (".", ",", "⟁"):
                grid[y][x] = "."
    for cx, cy in FIRES:
        # One tile each. Built as a ring of four solid tiles round an
        # empty middle they read as four crates standing in a diamond.
        if 0 <= cy < HEIGHT and 0 <= cx < WIDTH:
            grid[cy][cx] = "⚱"
    for x, y in SACKS:
        if 0 <= y < HEIGHT and 0 <= x < WIDTH and not _is_solid(grid[y][x]):
            grid[y][x] = "⛰"


def _is_solid(char: str) -> bool:
    return char in ("#", "⌗", "⍟", "⛰", "⚱")


def _scrub(grid) -> None:
    for x, y in ((13, 33), (17, 44), (52, 35), (58, 28), (11, 15),
                 (55, 15), (49, 44), (20, 12), (15, 39), (60, 38)):
        if grid[y][x] in (".", ",", "⟁"):
            grid[y][x] = "⍟"


def build():
    grid = _blank()
    _weather(grid)
    _camp(grid)
    _scrub(grid)
    _cliffs(grid)

    mid_x = WIDTH // 2
    half = GAP // 2
    _rect(grid, mid_x - half, HEIGHT - RIM, mid_x + half, HEIGHT - 1, "⮟")
    for x in range(mid_x - half, mid_x + half + 1):
        for y in range(HEIGHT - RIM - APPROACH, HEIGHT - RIM):
            if grid[y][x] not in (",", "⟁"):
                grid[y][x] = "."

    grid[START[1]][START[0]] = "⌬"
    grid[ANCHOR[1]][ANCHOR[0]] = "⨁"
    for x, y in ORCS:
        grid[y][x] = "❂" if grid[y][x] != "," else "⟠"
    return grid


HEADER = (
    "; DESERT ORC CAMP - Phase 13, north of the hub (64x48).\n"
    "; Brown rock closes the north and west in an uneven canyon front;\n"
    "; the only way out is the way in, south to the central desert.\n"
    "; '⛰' scratchable sacks (the Waterdeep pantry's own), '❂'/'⟠' orcs,\n"
    "; '⚱' burnt-out fire rings, '⨁' the ashtray south of the fight.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_orc_camp.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
