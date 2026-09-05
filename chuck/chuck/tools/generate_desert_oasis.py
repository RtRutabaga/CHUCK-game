"""Generate the Phase 13 desert oasis -- west of the hub.

The phase document calls this a small reward for exploration rather
than part of the critical route, and everything about the map is bent
toward being read that way from the doorway. There are no enemies in
it. There is nothing to solve in it. What there is, is the only water
and the only green in the region, and enough cigarette grass to make
the walk worth having made.

It is also a dead end on purpose, and closed three different ways so
that the dead end reads as geography rather than as a wall: rock down
the west, rock across the north, and the Astral Sea along the south --
the one edge in the region that is not made of rock, because a player
who has come this far knows exactly what that blue means.
"""

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 56
HEIGHT = 44

# The way back to the hub, in the middle of the east edge.
GAP = 5
RIM = 1
APPROACH = 5

NORTH_ROCK = 7      # how far down the northern cliff comes
WEST_ROCK = 7       # ...and how far in the western one reaches
ASTRAL = 4          # the depth of the southern Astral Sea band

# The pool, as a squashed ellipse: water, then a ring of turf around it,
# then palm shade over the turf.
#
# Deliberately small. Drawn at twice this it filled two screens and read
# as a lake, and the phase document is asking for a reward you find at
# the end of a walk -- something you can put your back to.
POOL = (30, 21, 6.0, 3.6)       # centre x, centre y, x radius, y radius
TURF = 2.6                      # how far the green reaches past the water
# Palm shade in clumps rather than single tiles. This is an overhead
# layer, the same kind of thing as the market awning: one tile of it on
# its own has no trunk under it and reads as a bush drawn on top of
# Chuck, where three or four together read as a tree he walks beneath.
PALM_CLUMPS = ((23, 17), (36, 17), (22, 25), (37, 24))
# Cigarette grass: most of it on the turf, a few tufts out on the sand
# so the walk in has something in it too.
TURF_GRASS = ((26, 16), (34, 16), (25, 26), (35, 26), (30, 15),
              (30, 27), (22, 21), (38, 21))
SAND_GRASS = ((13, 31), (47, 33), (15, 13), (46, 14), (11, 25), (44, 9),
              (18, 34), (41, 34))
# On the turf, not below it. The anchor marker paints its own
# under-terrain, so stood out on the sand it drew one green square
# in the middle of a desert with nothing else green near it.
ANCHOR = (28, 25)
ARRIVAL = (51, 21)  # just inside the way in from the hub


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _weather(grid) -> None:
    patches = (
        (12, 8, 12, 5, ","), (40, 30, 13, 6, ","), (10, 33, 9, 5, ","),
        (44, 12, 9, 6, "⟁"), (14, 27, 8, 4, "⟁"), (33, 34, 11, 4, "⟁"),
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


def _pool(grid) -> None:
    """Water with turf round it, both edges soft.

    Two ellipses with a wobble on the rim. Drawn true, a pool in a
    sixteen-pixel grid comes out as an obvious oval stamped on the sand;
    the wobble is what stops it reading as a swimming pool.
    """
    cx, cy, rx, ry = POOL
    for y in range(HEIGHT):
        for x in range(WIDTH):
            nx = (x - cx) / rx
            ny = (y - cy) / ry
            distance = math.hypot(nx, ny)
            wobble = 0.10 * math.sin(math.atan2(ny, nx) * 3.0 + 1.1)
            if distance <= 1.0 + wobble:
                grid[y][x] = "~"
            elif distance <= 1.0 + TURF / rx + wobble * 1.5:
                grid[y][x] = "⩊"


def _cliffs(grid) -> None:
    """Rock north and west, Astral Sea south, rim east.

    The two rock fronts wander for the same reason the orc camp's do:
    ruled straight they read as a border drawn round the map rather than
    as the sides of a canyon.
    """
    for x in range(WIDTH):
        depth = NORTH_ROCK - round(2.5 * math.sin(x / 8.0 + 0.6)) \
            - round(1.0 * math.sin(x / 3.5))
        if x < WEST_ROCK + 3:
            depth += (WEST_ROCK + 3 - x)
        _rect(grid, x, 0, x, max(0, depth), "#")
    for y in range(HEIGHT):
        reach = WEST_ROCK - round(2.0 * math.sin(y / 5.5)) \
            - round(1.0 * math.sin(y / 2.5))
        _rect(grid, 0, y, max(0, reach), y, "#")
    # The south is the Astral Sea rather than more rock: the one edge in
    # the region that is not stone, and the player already knows what
    # that colour means.
    for x in range(WIDTH):
        depth = ASTRAL + round(1.5 * math.sin(x / 6.0 + 2.0))
        _rect(grid, x, HEIGHT - depth, x, HEIGHT - 1, "V")
    _rect(grid, WIDTH - RIM, 0, WIDTH - 1, HEIGHT - 1, "#")


def build():
    grid = _blank()
    _weather(grid)
    _pool(grid)
    _cliffs(grid)

    mid_y = HEIGHT // 2
    half = GAP // 2
    _rect(grid, WIDTH - RIM, mid_y - half, WIDTH - 1, mid_y + half, "⮞")
    for y in range(mid_y - half, mid_y + half + 1):
        for x in range(WIDTH - RIM - APPROACH, WIDTH - RIM):
            if grid[y][x] not in (",", "⟁"):
                grid[y][x] = "."

    for left, top in PALM_CLUMPS:
        for y in range(top, top + 2):
            for x in range(left, left + 2):
                if 0 <= y < HEIGHT and 0 <= x < WIDTH and grid[y][x] == "⩊":
                    grid[y][x] = "⏦"
    for x, y in TURF_GRASS:
        if grid[y][x] == "⩊":
            grid[y][x] = "⩏"
    for x, y in SAND_GRASS:
        if grid[y][x] in (".", ",", "⟁"):
            grid[y][x] = "<"

    grid[ARRIVAL[1]][ARRIVAL[0]] = "⌬"
    grid[ANCHOR[1]][ANCHOR[0]] = "☉"
    return grid


HEADER = (
    "; DESERT OASIS - Phase 13, west of the hub (56x44). No enemies.\n"
    "; '~' water, '⩊' turf, '⏦' palm shade (drawn over Chuck),\n"
    "; '⩏'/'<' scratchable cigarette grass, '☉' the ashtray.\n"
    "; Rock closes the north and west; the south is the Astral Sea.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_oasis.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
