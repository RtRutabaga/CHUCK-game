"""Generate the Phase 13 central desert -- the hub of the opening region.

The phase document is specific about what this map must not do. There
is no quest arrow, no road painted through the sand, and nothing that
announces east as the way forward. So the four ways out are cut into
the canyon rim at the same width, at the same distance from the
corners, and nothing on the ground leads to any of them: the player
finds the layout by walking it.

What the map does have is scattered ruins to give the open ground
landmarks, because an unmarked desert with no features in it is not
exploration, it is a maze made of one colour. Each ruin is a broken
rectangle of cut stone standing on its own buried floor, and they are
placed by hand rather than scattered randomly so that no two of them
line up into an accidental path.
"""

import math
from pathlib import Path

from generate_desert_ruin_dressing import dress_ruin


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 72
HEIGHT = 56

# The canyon rim. One tile of brown rock all the way round, which is
# what makes the region read as a floor between walls rather than as an
# arbitrarily cropped rectangle of sand.
RIM = 1
# Four ways out, all the same width and all the same distance in from
# the corner, so that none of them is the obvious one. The gaps are cut
# now even though only some of them lead anywhere yet: the shape of the
# map should not change as its neighbours are built, only its markers.
GAP = 5

# Each ruin: (left, top, width, height). Broken rectangles of standing
# stone on a buried floor. Deliberately unaligned -- three of them in a
# row would read as a road even without a road being drawn.
RUINS = (
    (12, 9, 9, 6),
    (46, 13, 7, 8),
    (26, 24, 11, 5),
    (55, 33, 8, 6),
    (14, 38, 7, 7),
    (45, 44, 6, 5),
)
# Where the ashtray stands: near the middle, on the biggest ruin's
# floor, so the one place a player is certain to come back to is a
# place they can see from a distance.
ANCHOR = (31, 26)
# Chuck arrives a little south and west of it, in the open.
START = (28, 31)


# How far back from each gap the ground is kept clear of everything.
APPROACH = 6


def _clear(grid, x: int, y: int) -> None:
    """Put a tile back to open ground, keeping whatever weather it had."""
    if 0 <= y < HEIGHT and 0 <= x < WIDTH and grid[y][x] not in (",", "⟁"):
        grid[y][x] = "."


def _blank() -> list[list[str]]:
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _weather(grid) -> None:
    """Ripple and dune fields across the open sand.

    Wind-blown ground in broad soft patches rather than per-tile noise:
    scattered a tile at a time it reads as static, and the point of the
    texture is to give the eye something to navigate by.
    """
    patches = (
        (8, 17, 13, 5, ","), (33, 6, 15, 4, ","), (56, 22, 11, 6, ","),
        (20, 47, 16, 4, ","), (44, 27, 9, 5, ","), (6, 28, 8, 6, ","),
        (24, 14, 7, 4, "⟁"), (52, 44, 12, 4, "⟁"), (10, 49, 9, 3, "⟁"),
        (62, 8, 6, 7, "⟁"), (38, 34, 10, 3, "⟁"),
    )
    for left, top, width, height, char in patches:
        for y in range(top, top + height):
            for x in range(left, left + width):
                if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                    continue
                # A soft edge: the further from the middle of the patch,
                # the less likely the tile belongs to it. Hard-edged
                # rectangles of ripple look like rugs laid on the sand.
                nx = (x - (left + width / 2)) / (width / 2)
                ny = (y - (top + height / 2)) / (height / 2)
                if math.hypot(nx, ny) > 0.85 + ((x * 7 + y * 13) % 5) / 12:
                    continue
                grid[y][x] = char


def _ruin(grid, left, top, width, height) -> None:
    """One broken structure: buried floor, walls with pieces missing."""
    _rect(grid, left - 1, top - 1, left + width, top + height, "⌖")
    for y in range(top, top + height):
        for x in range(left, left + width):
            edge = (y in (top, top + height - 1)
                    or x in (left, left + width - 1))
            if not edge:
                grid[y][x] = "⌖"
                continue
            # Gaps in the walls, so each ruin can be walked into rather
            # than only walked around. A sealed box is scenery; a broken
            # one is somewhere to look.
            if (x * 5 + y * 3 + left + top) % 7 < 2:
                grid[y][x] = "⌖"
            else:
                grid[y][x] = "⌗"


def _outcrops(grid) -> None:
    """Loose rock standing out of the sand, away from the rim.

    These are the landmarks that are not ruins. Without them every
    feature on the map is somebody's architecture, which makes the
    desert read as a built place rather than as a place with things
    buried in it.
    """
    for left, top, width, height in ((60, 15, 3, 3), (8, 22, 4, 2),
                                     (43, 8, 2, 4), (30, 40, 4, 3),
                                     (65, 37, 3, 5), (20, 5, 3, 2)):
        _rect(grid, left, top, left + width - 1, top + height - 1, "#")


def _scrub(grid) -> None:
    """Dry bushes, thin and unevenly spread.

    Placed against the rock and the ruins more often than in the open,
    because the only shade in the region is beside something.
    """
    spots = (
        (11, 12), (22, 11), (19, 20), (7, 33), (13, 45), (23, 43),
        (34, 19), (29, 33), (41, 30), (38, 16), (45, 39), (50, 25),
        (54, 18), (59, 30), (64, 45), (57, 49), (67, 24), (49, 48),
        (16, 27), (26, 6), (44, 6), (61, 6), (9, 8), (67, 51),
        (35, 51), (18, 34), (52, 9), (40, 47),
    )
    for x, y in spots:
        if grid[y][x] in (".", ",", "⟁"):
            grid[y][x] = "⍟"


def build() -> list[list[str]]:
    grid = _blank()
    _weather(grid)
    _outcrops(grid)
    for left, top, width, height in RUINS:
        _ruin(grid, left, top, width, height)
    # ...and then what fell off it. The walls alone were flat: at this
    # scale a ruin is a rectangle of paler ground until something
    # taller than a tile is standing in it, and the pieces are what
    # tell the player the rectangle used to have a roof.
    for left, top, width, height in RUINS:
        dress_ruin(grid, left, top, width, height, seed=left + top)
    _scrub(grid)

    # The rim goes on last so nothing can be authored through it.
    _rect(grid, 0, 0, WIDTH - 1, RIM - 1, "#")
    _rect(grid, 0, HEIGHT - RIM, WIDTH - 1, HEIGHT - 1, "#")
    _rect(grid, 0, 0, RIM - 1, HEIGHT - 1, "#")
    _rect(grid, WIDTH - RIM, 0, WIDTH - 1, HEIGHT - 1, "#")

    # ...and then the four ways out are cut back through it. They are
    # identical: same width, same offset from the middle of each side.
    mid_x, mid_y = WIDTH // 2, HEIGHT // 2
    half = GAP // 2
    _rect(grid, mid_x - half, 0, mid_x + half, RIM - 1, ".")
    _rect(grid, mid_x - half, HEIGHT - RIM, mid_x + half, HEIGHT - 1, ".")
    _rect(grid, 0, mid_y - half, RIM - 1, mid_y + half, ".")
    _rect(grid, WIDTH - RIM, mid_y - half, WIDTH - 1, mid_y + half, ".")

    # Nothing built, grown or drifted is allowed to stand in front of a
    # way out. This is enforced here rather than checked afterwards
    # because it is exactly the kind of rule that a later edit breaks by
    # accident: one ruin nudged south, and the map is quietly telling
    # the player which exit is special.
    for x in range(mid_x - half, mid_x + half + 1):
        for y in range(RIM, RIM + APPROACH):
            _clear(grid, x, y)
        for y in range(HEIGHT - RIM - APPROACH, HEIGHT - RIM):
            _clear(grid, x, y)
    for y in range(mid_y - half, mid_y + half + 1):
        for x in range(RIM, RIM + APPROACH):
            _clear(grid, x, y)
        for x in range(WIDTH - RIM - APPROACH, WIDTH - RIM):
            _clear(grid, x, y)

    # All four gaps lead somewhere now: north to the orc camp, west to
    # the oasis, south to the undead ruins, east to the route forward.
    # They were cut identically before any of them had a map behind it,
    # which is what stops the one that matters from looking different.
    _rect(grid, mid_x - half, 0, mid_x + half, RIM - 1, "⮝")
    grid[RIM + 1][mid_x] = "⛲"
    # West leads to the oasis, south to the undead ruins.
    _rect(grid, 0, mid_y - half, RIM - 1, mid_y + half, "⮜")
    grid[mid_y][RIM + 1] = "♆"
    _rect(grid, mid_x - half, HEIGHT - RIM, mid_x + half, HEIGHT - 1, "⮟")
    grid[HEIGHT - RIM - 2][mid_x] = "♁"
    # ...and east, which is the way forward. It is wired like the other
    # three and looks like the other three: the map still does not say
    # which of the four is the one that matters.
    _rect(grid, WIDTH - RIM, mid_y - half, WIDTH - 1, mid_y + half, "⮞")
    grid[mid_y][WIDTH - RIM - 2] = "⌱"

    grid[ANCHOR[1]][ANCHOR[0]] = "⨀"
    return grid


HEADER = (
    "; DESERT CENTRAL - Phase 13 hub (72x56).\n"
    "; '.' open sand, ',' wind ripple, '⟁' dune, '#' canyon rock.\n"
    "; '⌗' standing ruin (solid), '⌖' its buried floor,"
    " '⍟' dry scrub.\n"
    "; '⍏'/'⍐' standing columns, '⍖'/'⍗' fallen ones,"
    " '⍓'/'⍔' spilled blocks.\n"
    "; Four identical gaps in the rim, one per side. Nothing on the\n"
    "; ground points at any of them -- that is the whole design.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_central.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
