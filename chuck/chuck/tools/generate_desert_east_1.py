"""Generate the first map east of the hub -- where the collision starts.

The phase document is careful about this one. The first eastern
transition must not be dramatically different from the rest of the
desert, and the mash-up has to escalate as Chuck goes rather than
arriving all at once. So this map is desert. It has the same sand, the
same rock, the same broken ruins as everything behind it, and a player
who walks in here has not obviously left the region they were in.

There is exactly one wrong thing in it: a slab of rained-on city road,
lane line and all, lying in a tear of Astral Sea about a third of the
way across. It is small enough to walk past and strange enough to walk
toward, and it is the first evidence in the game that the desert is not
going to stay a desert.

It is also a real crossing rather than scenery. The tear cuts the map
in half from rim to rim and the road is the only way over -- so the
first fragment of another world Chuck meets is one he has to stand on.
"""

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_collided_common import astral_fringe, dress_fragments
from generate_desert_ruin_dressing import dress_ruin


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 68
HEIGHT = 48

GAP = 5
RIM = 1
APPROACH = 5

# The tear: a band of Astral Sea running north-south, rim to rim, with
# the road slab laid across the middle of it.
#
# Rim to rim matters. Tapered to nothing a few rows short of each end it
# left walkable sand round both, and the road stopped being a crossing
# and became an ornament beside one -- the map claimed a beat it did not
# actually have.
TEAR_X = 34
TEAR_HALF = 3           # how wide the tear is at its widest
TEAR_TOP = RIM
TEAR_BOTTOM = HEIGHT - RIM - 1

# The road: an east-west slab bridging the tear, with the lane line
# running down the middle of it exactly as it does in the city.
ROAD_Y = 23
ROAD_HALF_H = 2         # the carriageway is five tiles deep
ROAD_LEFT = TEAR_X - 9
ROAD_RIGHT = TEAR_X + 9

RUINS = ((10, 10, 8, 6), (52, 14, 7, 7), (14, 33, 9, 5), (55, 34, 6, 6))
OUTCROPS = ((22, 20, 3, 3), (60, 24, 3, 4), (8, 24, 2, 3), (46, 38, 4, 2))
SCRUB = ((12, 18), (26, 12), (44, 11), (62, 17), (18, 27), (29, 39),
         (49, 30), (57, 43), (7, 38), (41, 43), (24, 44), (64, 9))
ANCHOR = (12, 24)       # west of the tear, before the crossing
ARRIVAL = (4, 24)       # just inside the way in from the hub


# Everything on this map that came from somewhere else. The seam
# between it and the desert gets frayed with Astral Sea, so the
# fragment reads as having torn its way in rather than as having
# been laid down on the sand.
FRAGMENT_CHARS = {"=", "≡"}


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _weather(grid) -> None:
    patches = (
        (8, 14, 12, 5, ","), (44, 20, 12, 6, ","), (20, 36, 13, 5, ","),
        (56, 6, 10, 6, ","), (24, 8, 9, 4, "⟁"), (48, 40, 12, 4, "⟁"),
        (6, 30, 8, 5, "⟁"), (60, 28, 7, 6, "⟁"),
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


def _ruin(grid, left, top, width, height) -> None:
    _rect(grid, left - 1, top - 1, left + width, top + height, "⌖")
    for y in range(top, top + height):
        for x in range(left, left + width):
            edge = (y in (top, top + height - 1)
                    or x in (left, left + width - 1))
            if not edge:
                grid[y][x] = "⌖"
            elif (x * 5 + y * 3 + left + top) % 7 < 2:
                grid[y][x] = "⌖"
            else:
                grid[y][x] = "⌗"


def _tear(grid) -> None:
    """The Astral Sea, torn through the desert from north to south.

    The edges wander so it reads as ground come apart rather than as a
    trench somebody dug, but it runs the full height of the map: what
    makes the road worth anything is that there is no way round it.
    """
    for y in range(TEAR_TOP, TEAR_BOTTOM + 1):
        span = max(1, TEAR_HALF + round(1.4 * math.sin(y / 5.0 + 0.8)))
        _rect(grid, TEAR_X - span, y, TEAR_X + span, y, "V")


def _road(grid) -> None:
    """A slab of the modern city, lying across the tear.

    Laid over the Sea rather than beside it: the first fragment Chuck
    meets is the thing he crosses on, which is a better introduction to
    the collision than a piece of scenery he can only look at.
    """
    for y in range(ROAD_Y - ROAD_HALF_H, ROAD_Y + ROAD_HALF_H + 1):
        for x in range(ROAD_LEFT, ROAD_RIGHT + 1):
            if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                continue
            # The slab has broken ends: the further from the tear, the
            # more likely the asphalt has given way to sand again.
            reach = abs(x - TEAR_X) / (ROAD_RIGHT - TEAR_X)
            if reach > 0.55 + ((x * 3 + y * 5) % 5) / 9:
                continue
            grid[y][x] = "≡" if y == ROAD_Y else "="


def build():
    grid = _blank()
    _weather(grid)
    for left, top, width, height in OUTCROPS:
        _rect(grid, left, top, left + width - 1, top + height - 1, "#")
    for ruin in RUINS:
        _ruin(grid, *ruin)
    # ...and what fell off them, out of the same box the
    # hub's ruins are dressed from. These are the same
    # building, still coming apart, further east.
    for left, top, width, height in RUINS:
        dress_ruin(grid, left, top, width, height,
                   seed=left + top)
    for x, y in SCRUB:
        if grid[y][x] in (".", ",", "⟁"):
            grid[y][x] = "⍟"

    _tear(grid)
    _road(grid)
    astral_fringe(grid, FRAGMENT_CHARS, seed=0.0)

    _rect(grid, 0, 0, WIDTH - 1, RIM - 1, "#")
    _rect(grid, 0, HEIGHT - RIM, WIDTH - 1, HEIGHT - 1, "#")
    _rect(grid, 0, 0, RIM - 1, HEIGHT - 1, "#")
    _rect(grid, WIDTH - RIM, 0, WIDTH - 1, HEIGHT - 1, "#")

    mid_y = HEIGHT // 2
    half = GAP // 2
    # West back to the hub, east onward to the next map.
    _rect(grid, 0, mid_y - half, RIM - 1, mid_y + half, "⮜")
    _rect(grid, WIDTH - RIM, mid_y - half, WIDTH - 1, mid_y + half, "⮞")
    for y in range(mid_y - half, mid_y + half + 1):
        for x in range(RIM, RIM + APPROACH):
            if grid[y][x] not in (",", "⟁"):
                grid[y][x] = "."
        for x in range(WIDTH - RIM - APPROACH, WIDTH - RIM):
            if grid[y][x] not in (",", "⟁"):
                grid[y][x] = "."

    # Each world's own growth and debris, standing on its own
    # ground: a fragment is recognised by what is on it, and a
    # rectangle of somebody else's ground colour is not.
    #
    # Last, once every piece of ground on the map is final. Run
    # earlier it planted trees against a rim that had not been
    # drawn yet, and skipped the scraps of other worlds entirely
    # because they had not landed yet either.
    dress_fragments(grid, seed=0.5)
    grid[ARRIVAL[1]][ARRIVAL[0]] = "⌦"
    grid[mid_y][WIDTH - RIM - 2] = "⌲"
    grid[ANCHOR[1]][ANCHOR[0]] = "⌸"
    return grid


HEADER = (
    "; DESERT EAST 1 - Phase 13, the first map of the traversal (68x48).\n"
    "; Still desert. One wrong thing in it: a tear of Astral Sea from\n"
    "; north to south, with a slab of rained-on city road ('='/'≡')\n"
    "; lying across the middle of it as the only way over.\n"
    "; The ruins carry the hub's own fallen pieces: '⍏'/'⍐'\n"
    "; columns, '⍖'/'⍗' fallen ones, '⍓'/'⍔' blocks.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_east_1.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
