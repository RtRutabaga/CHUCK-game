"""Generate the Phase 13 undead ruins -- south of the hub.

The hub has ruins scattered across it, six small broken rectangles a
player walks past. This is what those were fragments of: one building
big enough to have rooms, with a courtyard in the middle of it and a
chest standing in the courtyard.

That is the whole design argument for the map. The phase document says
the ruins should feel worth exploring even though they do not contain
the route forward, and the way to earn that is for the place to be
legibly a *building* rather than more scenery -- walls that meet at
corners, doorways that line up, an inside and an outside. Skeletons
patrol it, and the chest is far enough in that reaching it means going
through them.

West and south are the Astral Sea, as the document specifies, which
also means the walls do not have to do the work of sealing the map.
"""

import math
from pathlib import Path

from generate_desert_ruin_dressing import dress_ruin


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 60
HEIGHT = 52

GAP = 5
RIM = 1
APPROACH = 5
ASTRAL = 4          # depth of the Astral bands on the west and south

# The building. An outer wall with four gaps in it, an inner courtyard,
# and a few cross-walls making rooms out of the space between them.
OUTER = (16, 12, 32, 28)    # left, top, width, height
COURT = (28, 22, 10, 9)
# Where the outer wall is broken through. Four ways in, so the building
# is a place to move around inside rather than a box with a lid.
DOORS = (("north", 24), ("north", 40), ("south", 30), ("west", 20),
         ("east", 32))
# Cross-walls: (x, y, length, horizontal?) inside the outer wall.
PARTITIONS = (
    (16, 20, 9, True), (39, 20, 9, True),
    (22, 30, 6, True), (40, 32, 8, True),
    (22, 20, 6, False), (43, 24, 8, False),
)
# The gate. It stands in the north wall, on the door the player
# arrives at, and the door is widened to three tiles so there is an
# opening under it rather than a doorway with a monument next to it.
# The arch's own piers are the wall either side.
GATE = 24                   # the middle of it, on the outer wall's top row

# The great pillars. Every column in the ruin was a fragment, so the
# building they were fragments of was never on screen -- these are it.
#
# Four flank the way in and the courtyard door, which is where a
# building this size puts its order; two more stand outside the north
# wall where the portico came down, and two in the south-west room,
# which is the deepest part of the building and had nothing in it.
GREAT_PILLARS = (
    (21, 14), (28, 14), (36, 14), (43, 14),
    (27, 21), (39, 21),
    (20, 10), (44, 10),
    (20, 33), (20, 36),
)

CHEST = (32, 26)            # in the courtyard, dead centre
ANCHOR = (32, 44)           # outside the building, on the way in
ARRIVAL = (30, 4)           # just inside the way in from the hub

SKELETONS = ((24, 17), (40, 17), (20, 26), (44, 28), (30, 34),
             (36, 19), (26, 31), (33, 15), (43, 36), (19, 35))


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _weather(grid) -> None:
    patches = (
        (6, 6, 10, 5, ","), (48, 8, 10, 6, ","), (8, 42, 12, 5, ","),
        (46, 42, 11, 5, "⟁"), (4, 24, 8, 7, "⟁"), (50, 26, 8, 6, "⟁"),
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


def _wall(grid, left, top, width, height) -> None:
    """One rectangle of standing stone on its own buried floor.

    The wall is broken in places by the same rule the hub's ruins use,
    so no stretch of it runs perfectly intact -- but the corners are
    always left standing, because a corner is what tells the eye this
    was built rather than piled.
    """
    right, bottom = left + width - 1, top + height - 1
    _rect(grid, left, top, right, bottom, "⌖")
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if not (y in (top, bottom) or x in (left, right)):
                continue
            corner = (x in (left, left + 1, right - 1, right)
                      and y in (top, top + 1, bottom - 1, bottom))
            if corner or (x * 5 + y * 3) % 9 >= 2:
                grid[y][x] = "⌗"


def _thicken(grid) -> None:
    """Give the outer wall a second leaf, inside the first.

    One tile of stone is a garden wall. A building with rooms, a
    courtyard and a gate in it was built thick, and at this scale the
    difference between one tile and two is the difference between a
    line drawn round the floor and something with a weight to it.

    The inner leaf is broken much harder than the outer one, because
    that is how these walls actually fail: the facing stays up and the
    rubble core behind it goes. So the thickness comes and goes along
    the run, which is what stops two tiles of wall reading as one tile
    of wall drawn twice.
    """
    left, top, width, height = OUTER
    right, bottom = left + width - 1, top + height - 1
    for y in range(top + 1, bottom):
        for x in range(left + 1, right):
            if not (y in (top + 1, bottom - 1) or x in (left + 1, right - 1)):
                continue
            corner = (x in (left + 1, left + 2, right - 2, right - 1)
                      and y in (top + 1, top + 2, bottom - 2, bottom - 1))
            if corner or (x * 7 + y * 11) % 10 >= 5:
                grid[y][x] = "⌗"


def _partitions(grid) -> None:
    for x, y, length, horizontal in PARTITIONS:
        for step in range(length):
            cx = x + step if horizontal else x
            cy = y if horizontal else y + step
            if not (0 <= cy < HEIGHT and 0 <= cx < WIDTH):
                continue
            # Gaps, so the rooms connect and the building can be walked
            # through rather than only looked into.
            grid[cy][cx] = "⌖" if (cx * 3 + cy * 7) % 8 < 2 else "⌗"


def _doors(grid) -> None:
    """Cut the ways in, through both leaves of the wall.

    A doorway that goes through the facing and stops at the core is a
    niche, so every door is cut twice: once in the outer ring and once
    in the inner one directly behind it.
    """
    left, top, width, height = OUTER
    right, bottom = left + width - 1, top + height - 1
    for side, at in DOORS:
        if side == "north":
            _rect(grid, at, top, at + 1, top + 1, "⌖")
        elif side == "south":
            _rect(grid, at, bottom - 1, at + 1, bottom, "⌖")
        elif side == "west":
            _rect(grid, left, at, left + 1, at + 1, "⌖")
        else:
            _rect(grid, right - 1, at, right, at + 1, "⌖")


def _gate(grid) -> None:
    """Widen the arrival door to three tiles and stand the arch on it.

    The arch is one sprite five tiles across, anchored on the middle of
    the opening. That is why the door has to be three wide: the sprite's
    two piers land on the tiles either side, and those stay standing
    wall, so what is solid about the gate is exactly the stone that
    looks solid.
    """
    left, top, width, height = OUTER
    for offset in (-1, 0, 1):
        grid[top][GATE + offset] = "⌖"
        grid[top + 1][GATE + offset] = "⌖"
    for offset in (-2, 2):
        grid[top][GATE + offset] = "⌗"
        grid[top + 1][GATE + offset] = "⌗"
    grid[top][GATE] = "⍛"
    # The gate is the way in, so the sand in front of it is swept clear
    # of anything the ruin dressing dropped there.
    for row in range(top - 3, top):
        for col in range(GATE - 2, GATE + 3):
            if grid[row][col] not in (",", "⟁"):
                grid[row][col] = "."


def _great_pillars(grid) -> None:
    """Stand the big order where a building this size would have it."""
    for col, row in GREAT_PILLARS:
        if not (0 <= row < HEIGHT and 0 <= col < WIDTH):
            continue
        if grid[row][col] == "⌖":
            grid[row][col] = "⍕"
        elif grid[row][col] in (".", ",", "⟁"):
            grid[row][col] = "⍙"


def _astral(grid) -> None:
    """The Sea along the west and south, and rim rock elsewhere."""
    for y in range(HEIGHT):
        depth = ASTRAL + round(1.5 * math.sin(y / 6.0 + 1.0))
        _rect(grid, 0, y, depth - 1, y, "V")
    for x in range(WIDTH):
        depth = ASTRAL + round(1.5 * math.sin(x / 7.0 + 2.4))
        _rect(grid, x, HEIGHT - depth, x, HEIGHT - 1, "V")
    _rect(grid, 0, 0, WIDTH - 1, RIM - 1, "#")
    _rect(grid, WIDTH - RIM, 0, WIDTH - 1, HEIGHT - 1, "#")


def build():
    grid = _blank()
    _weather(grid)
    _wall(grid, *OUTER)
    _thicken(grid)
    _partitions(grid)
    _wall(grid, *COURT)
    _doors(grid)
    # What came off it. The hub's ruins are fragments of this building,
    # so they are dressed by the same rule and out of the same pieces --
    # a player who has walked past six broken rectangles up north
    # should recognise this as the thing they were broken off.
    # The big order first, and the fragments round it afterwards: the
    # ruin dressing never writes on a tile that already has something
    # on it, so putting the pillars down first means a great one and a
    # broken one can never want the same tile.
    _great_pillars(grid)
    dress_ruin(grid, *OUTER, seed=OUTER[0] + OUTER[1])
    dress_ruin(grid, *COURT, seed=COURT[0] + COURT[1])
    _gate(grid)
    _astral(grid)

    mid_x = WIDTH // 2
    half = GAP // 2
    _rect(grid, mid_x - half, 0, mid_x + half, RIM - 1, "⮝")
    for x in range(mid_x - half, mid_x + half + 1):
        for y in range(RIM, RIM + APPROACH):
            if grid[y][x] not in (",", "⟁"):
                grid[y][x] = "."

    grid[CHEST[1]][CHEST[0]] = "⎈"
    # Arrivals are named for where you came *from*, so the marker in
    # this map is the hub's -- the same one the camp and the oasis
    # use. The ruins' own name belongs on the hub's south edge.
    grid[ARRIVAL[1]][ARRIVAL[0]] = "⌬"
    grid[ANCHOR[1]][ANCHOR[0]] = "☽"
    for x, y in SKELETONS:
        if grid[y][x] in (".", ",", "⟁"):
            grid[y][x] = "ᛊ"
        elif grid[y][x] == "⌖":
            grid[y][x] = "ᛏ"
    return grid


HEADER = (
    "; DESERT UNDEAD RUINS - Phase 13, south of the hub (60x52).\n"
    "; One building with rooms and a courtyard, not scattered rubble:\n"
    "; '⌗' standing wall, '⌖' its buried floor, '⎈' the chest in the\n"
    "; courtyard, 'ᛊ'/'ᛏ' patrolling skeletons, '☽' the ashtray.\n"
    "; The Astral Sea closes the west and the south.\n"
    "; '⍏'/'⍐' standing columns, '⍖'/'⍗' fallen ones,"
    " '⍓'/'⍔' spilled blocks.\n"
    "; '⍕'/'⍙' the great pillars and '⍛' the gate arch, which is the\n"
    "; one piece of the building still whole. Chuck walks under it.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_undead_ruins.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
