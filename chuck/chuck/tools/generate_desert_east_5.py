"""Generate the fifth map east -- a castle Chuck has never been to.

Every fragment so far has been somewhere he remembers. This one is not,
and that is the whole point of it: the phase document wants the player
to understand that the collision is much larger than the route Chuck
happened to walk. A courtyard of swept flagstones with ashlar walls
round it, standing in the sand, is a place that exists and that he has
no memory of at all.

It is deliberately *kept* rather than ruined. The desert already has
three kinds of fallen-down stone on it, and a broken castle would read
as a fourth. This one is coursed, swept, and mossed only in the joints,
so it reads as somewhere that was still in use when it was taken.

The knights came with it, and they are the heaviest thing in the game's
pursuer role -- slow, and very hard to see off. Fighting through the
courtyard is a bad idea. Going round the outside of the walls is not.

This is also the first map to hold two hazards at once, which is the
document's "familiar systems in new combinations": an Astral tear and a
run of lava off the Hell fragment behind, in the same place.
"""

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_collided_common import (
    astral_fringe, dress_castle, dress_fragments,
)


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 76
HEIGHT = 56

GAP = 5
RIM = 1
APPROACH = 5

# The courtyard: an outer wall with gates, flagstone within.
COURT = (24, 14, 30, 28)        # left, top, width, height
GATES = (("west", 24), ("east", 26), ("north", 36), ("south", 34))
# Inner structures: a well head and two lengths of cloister wall.
INNER = ((32, 22, 3, 3), (44, 30, 3, 3), (30, 34, 12, 1), (40, 18, 1, 8))
KNIGHTS = ((30, 20), (46, 24), (34, 30), (44, 36), (28, 38), (48, 16))

# Two hazards in one place, north-east of the courtyard: the Sea has
# torn the ground and Hell's lava is running into the tear.
TEAR = (58, 8, 10, 16)
LAVA_RUN = ((60, 23), (60, 25), (61, 27), (61, 29),
            (62, 31), (62, 33), (63, 35), (63, 37))

# A length of ship's deck, out on the sand to the south-west.
DECK = (8, 40, 12, 6)
SCRAPS = ((10, 10, 6, 3, "ᛗ"), (66, 44, 5, 3, "ᛟ"), (16, 24, 5, 3, "="))
SCRUB = ((20, 8), (68, 20), (14, 34), (70, 50), (22, 50))
WAYPOINT = (8, 28)
ARRIVAL = (4, 28)


# Everything on this map that came from somewhere else. The seam
# between it and the desert gets frayed with Astral Sea, so the
# fragment reads as having torn its way in rather than as having
# been laid down on the sand.
FRAGMENT_CHARS = {"⌽", "⌾", "⌼", "=", "ᛗ", "ᛟ", "·", "≋"}


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _weather(grid) -> None:
    patches = (
        (6, 12, 10, 5, ","), (60, 44, 12, 6, ","), (14, 46, 10, 5, "⟁"),
        (66, 30, 8, 6, "⟁"),
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


def _courtyard(grid) -> None:
    """Wall, gates, flagstone, and the cloister inside it.

    The wall is unbroken except where it is gated, which is the one
    thing that separates this from every ruin in the region: it is not
    falling down, it is simply somewhere else.
    """
    left, top, width, height = COURT
    right, bottom = left + width - 1, top + height - 1
    _rect(grid, left, top, right, bottom, "⌽")
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if y in (top, bottom) or x in (left, right):
                grid[y][x] = "⌾"

    for side, at in GATES:
        if side == "north":
            _rect(grid, at, top, at + 2, top, "⌽")
        elif side == "south":
            _rect(grid, at, bottom, at + 2, bottom, "⌽")
        elif side == "west":
            _rect(grid, left, at, left, at + 2, "⌽")
        else:
            _rect(grid, right, at, right, at + 2, "⌽")

    for x, y, w, h in INNER:
        _rect(grid, x, y, x + w - 1, y + h - 1, "⌾")


def _tear(grid) -> None:
    left, top, width, height = TEAR
    cx, cy = left + width / 2, top + height / 2
    rx, ry = width / 2, height / 2
    for y in range(top - 1, top + height + 1):
        for x in range(left - 1, left + width + 1):
            if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                continue
            nx, ny = (x - cx) / rx, (y - cy) / ry
            wobble = 0.2 * math.sin(math.atan2(ny, nx) * 3.0 + 1.4)
            if math.hypot(nx, ny) <= 1.0 + wobble and grid[y][x] != "⌾":
                grid[y][x] = "V"


def _lava(grid) -> None:
    """A run of Hell coming down out of the tear.

    Two hazards in one place: the phase document asks for mechanics that
    used to belong to separate regions turning up together, and the
    cheapest honest version of that is a fall you can walk into and a
    burn you can walk into, side by side.
    """
    for x, y in LAVA_RUN:
        # Banks two tiles wide rather than one. At one, every basalt
        # tile on this map touched lava, which is a stripe rather than a
        # place -- there was nowhere on it to put anything down, and the
        # rubble that came through with it had nowhere to lie.
        for oy in range(-1, 2):
            for ox in range(-2, 3):
                cx, cy = x + ox, y + oy
                if not (0 <= cy < HEIGHT and 0 <= cx < WIDTH):
                    continue
                if grid[cy][cx] in (".", ",", "⟁"):
                    grid[cy][cx] = "·"
        # Three tiles wide, not one. A single tile per point came out
        # as four orange dots on a basalt path -- something to notice
        # rather than something to get past, which is the opposite of
        # what a second hazard is for.
        for ox in (-1, 0, 1):
            if 0 <= y < HEIGHT and 0 <= x + ox < WIDTH:
                grid[y][x + ox] = "≋"


def _deck(grid) -> None:
    left, top, width, height = DECK
    for y in range(top, top + height):
        for x in range(left, left + width):
            if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                continue
            # Broken at both ends, like everything else that fell.
            along = abs(x - (left + width / 2)) / (width / 2)
            if along > 0.7 + ((x * 3 + y * 5) % 5) / 9:
                continue
            if grid[y][x] in (".", ",", "⟁"):
                grid[y][x] = "⌼"


def _scrap(grid, left, top, width, height, char) -> None:
    cx, cy = left + width / 2, top + height / 2
    rx, ry = max(1.0, width / 2), max(1.0, height / 2)
    for y in range(top - 1, top + height + 1):
        for x in range(left - 1, left + width + 1):
            if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                continue
            if grid[y][x] not in (".", ",", "⟁"):
                continue
            nx, ny = (x - cx) / rx, (y - cy) / ry
            wobble = 0.2 * math.sin(math.atan2(ny, nx) * 3.0 + left)
            if math.hypot(nx, ny) <= 1.0 + wobble:
                grid[y][x] = char


def build():
    grid = _blank()
    _weather(grid)
    _courtyard(grid)
    _deck(grid)
    for scrap in SCRAPS:
        _scrap(grid, *scrap)
    _tear(grid)
    _lava(grid)
    astral_fringe(grid, FRAGMENT_CHARS, seed=5.2)
    for x, y in SCRUB:
        if grid[y][x] in (".", ",", "⟁"):
            grid[y][x] = "⍟"

    _rect(grid, 0, 0, WIDTH - 1, RIM - 1, "#")
    _rect(grid, 0, HEIGHT - RIM, WIDTH - 1, HEIGHT - 1, "#")
    _rect(grid, 0, 0, RIM - 1, HEIGHT - 1, "#")
    _rect(grid, WIDTH - RIM, 0, WIDTH - 1, HEIGHT - 1, "#")

    mid_y = HEIGHT // 2
    half = GAP // 2
    _rect(grid, 0, mid_y - half, RIM - 1, mid_y + half, "⮜")
    _rect(grid, WIDTH - RIM, mid_y - half, WIDTH - 1, mid_y + half, "⮞")
    for y in range(mid_y - half, mid_y + half + 1):
        for x in range(RIM, RIM + APPROACH):
            if grid[y][x] not in (",", "⟁"):
                grid[y][x] = "."
        for x in range(WIDTH - RIM - APPROACH, WIDTH - RIM):
            if grid[y][x] not in (",", "⟁"):
                grid[y][x] = "."

    for x, y in KNIGHTS:
        if grid[y][x] == "⌽":
            grid[y][x] = "⍂"
    # Each world's own growth and debris, standing on its own
    # ground: a fragment is recognised by what is on it, and a
    # rectangle of somebody else's ground colour is not.
    #
    # Last, once every piece of ground on the map is final. Run
    # earlier it planted trees against a rim that had not been
    # drawn yet, and skipped the scraps of other worlds entirely
    # because they had not landed yet either.
    dress_fragments(grid, seed=5.7)
    # ...and the castle finished: crenellation on the curtain, drum
    # towers on the corners and the stumps, banners on the faces
    # that show. All of it converted from stone that was already
    # there, so nothing about the walk changes.
    dress_castle(grid, seed=5)
    grid[ARRIVAL[1]][ARRIVAL[0]] = "⌷"
    grid[mid_y][WIDTH - RIM - 2] = "⍃"
    return grid


HEADER = (
    "; DESERT EAST 5 - Phase 13, a world Chuck has never been to (76x56).\n"
    "; A kept courtyard: '⌽' swept flagstone, '⌾' ashlar wall, with\n"
    "; armoured knights ('⍂') in it. Gated on all four sides, and the\n"
    "; walls can be walked round rather than through.\n"
    "; North-east, two hazards in one place: an Astral tear with Hell's\n"
    "; lava running into it. '⌼' is a length of the ship's deck.\n"
    "; 'þ' Phlegethos's basalt rubble lies on the lava's banks, and\n"
    "; the scraps carry their own worlds' growth.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_east_5.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
