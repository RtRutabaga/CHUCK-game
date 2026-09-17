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
# Palms, standing in a ring round the pool.
#
# There were only ever canopy tiles here: an overhead layer, shade
# drawn above Chuck so he walks under it. It was authored as four
# clumps of four, and three of the four clumps fell on sand rather than
# turf and were quietly dropped -- so what the oasis actually had was
# two lonely tiles of shade with nothing casting them.
#
# Now each palm is a tree: a solid trunk standing on the ground, and
# its own crown drawn overhead in the tiles the crown reaches. They are
# placed on a ring rather than by hand so that they stand *round* the
# water at an even distance from it, which is the thing that makes an
# oasis read as an oasis rather than as a pond with bushes near it.
PALM_COUNT = 9
PALM_RING = 1.62        # in pool radii: just outside the turf's edge
# How far the crown of a palm reaches above the tile its trunk stands
# on: one narrow row and one wide one, immediately above it. Written
# two tiles higher than this the shade came out as a separate green
# blob floating above each tree -- an overhead tile is only shade if
# it lands where the thing casting it actually is.
CROWN_ROWS = (2, 1)
# Cigarette grass: most of it on the turf, a few tufts out on the sand
# so the walk in has something in it too.
TURF_GRASS = ((26, 16), (34, 16), (25, 26), (35, 26), (30, 15),
              (30, 27), (22, 21), (38, 21))
SAND_GRASS = ((13, 31), (47, 33), (15, 13), (46, 14), (11, 25), (44, 9),
              (18, 34), (41, 34))
# On the turf, not below it. The anchor marker paints its own
# under-terrain, so stood out on the sand it drew one green square
# in the middle of a desert with nothing else green near it.
WAYPOINT = (28, 25)
ARRIVAL = (51, 21)  # just inside the way in from the hub


TURF_CHAR = "⩊"


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


def _palms(grid) -> None:
    """A ring of palms round the pool, each with the shade it casts.

    Trees rather than tiles. The trunk is a solid prop standing on the
    ground -- Chuck walks around it, and it is taller than he is by
    three times -- and the crown is written into the overhead layer
    above it, so he can still walk into the shade and be under it.

    Anything already spoken for is left alone. A palm is the least
    important thing on this map and it must never be the reason the
    waypoint moved, or a tuft of cigarette grass went missing, or the
    way in stopped being clear.
    """
    cx, cy, rx, ry = POOL
    ground = (".", ",", "⟁")
    for index in range(PALM_COUNT):
        angle = index * (2.0 * math.pi / PALM_COUNT) + 0.4
        # The ring is squashed the same way the pool is, so the palms
        # keep the same distance from the water all the way round
        # rather than bunching at the ends of it.
        x = round(cx + math.cos(angle) * rx * PALM_RING)
        y = round(cy + math.sin(angle) * ry * PALM_RING)
        if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
            continue
        if grid[y][x] == TURF_CHAR:
            grid[y][x] = "⍑"
        elif grid[y][x] in ground:
            grid[y][x] = "⍒"
        else:
            continue
        # The crown, in the tiles it actually reaches. Drawn as a
        # square block above the trunk it covered ground the tree does
        # not, and a canopy that does not line up with the tree under
        # it reads as two separate things.
        for depth in CROWN_ROWS:
            for offset in (-1, 0, 1):
                sx, sy = x + offset, y - depth
                if not (0 <= sy < HEIGHT and 0 <= sx < WIDTH):
                    continue
                if abs(offset) and depth == CROWN_ROWS[0]:
                    continue        # the crown is narrower at the top
                if grid[sy][sx] == TURF_CHAR:
                    grid[sy][sx] = "⏦"
                elif grid[sy][sx] in ground:
                    grid[sy][sx] = "⍚"


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

    for x, y in TURF_GRASS:
        if grid[y][x] == "⩊":
            grid[y][x] = "⩏"
    for x, y in SAND_GRASS:
        if grid[y][x] in (".", ",", "⟁"):
            grid[y][x] = "<"
    # Last, so that a palm can only ever take a tile nothing else
    # wanted. Planted before the cigarette grass, a trunk landing on a
    # tuft's square silently deleted the tuft -- the tufts are placed
    # by hand and only go down on ground of the right kind, so they
    # lose the argument without saying anything.
    _palms(grid)

    grid[ARRIVAL[1]][ARRIVAL[0]] = "⌬"
    return grid


HEADER = (
    "; DESERT OASIS - Phase 13, west of the hub (56x44). No enemies.\n"
    "; '~' water, '⩊' turf, '⏦'/'⍚' palm shade (drawn over Chuck),\n"
    "; '⍑'/'⍒' the palms casting it, standing on turf and on sand,\n"
    "; '⩏'/'<' scratchable cigarette grass.\n"
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
