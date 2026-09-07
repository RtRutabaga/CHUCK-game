"""Generate the eighth map east -- where the ground has mostly gone.

The seventh map is nine worlds touching each other. This one is the
same worlds not touching: the Astral Sea is the map, and what is left
of the ground is islands in it, joined by causeways two tiles wide.

That is the escalation, and it is a structural one rather than another
count of fragments. Up to here, "further gone" has meant more of
somewhere else and less desert. Here it means there is less of
*anything* -- two thirds of the map is a hole, a fifth of it can be
reached, and every walk across it is a walk along a ledge with the Sea
on both sides. The phase document
lists narrow routes and Astral Sea fall hazards among the things to
reuse; this is both of them at once and nothing else.

Two of the islands have no causeway at all. They are drawn, they are
lit, they have their own weather, and there is no way to stand on
them -- which is the document's "castle walls or towers visible
through Astral Sea sections" taken at its word. A collision this big
should have places in it that Chuck can only look at.

The causeways change material halfway. A bridge from the jungle to the
courtyard is jungle at one end and flagstone at the other, because
neither world built it: it is what happens to be left of the ground
between two things that were never near each other.
"""

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_collided_common import (
    astral_fringe, dress_castle, dress_fragments,
)
from generate_desert_ruin_dressing import dress_ruin


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 92
HEIGHT = 68

GAP = 5
RIM = 1
APPROACH = 5
MID_Y = HEIGHT // 2

# The islands: centre, radii, and which world each one is what is left
# of. The first and the last are desert and they touch their own rim,
# because a map made entirely of ledges has to begin and end on
# something a player can stand on and think about.
ISLANDS = (
    (9, MID_Y, 7.5, 9.5, "desert"),         # 0: the shore you arrive on
    (25, 25, 8.0, 7.0, "chult"),            # 1
    (39, 43, 9.0, 8.5, "hell"),             # 2
    (55, 29, 10.0, 9.0, "courtyard"),       # 3
    (71, 45, 8.0, 7.0, "snow"),             # 4
    (83, MID_Y, 7.5, 9.5, "desert"),        # 5: the far shore
    (31, 10, 6.0, 5.0, "feywild"),          # 6: off the route
    (63, 60, 6.5, 5.0, "ship"),             # 7: off the route
    (15, 58, 5.5, 4.5, "city"),             # 8: marooned
    (78, 9, 6.0, 5.0, "chult"),             # 9: marooned
)

# Which islands are joined. Everything not named here is reachable only
# by looking at it.
CAUSEWAYS = ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (1, 6), (3, 7))
CAUSEWAY_HALF = 0       # two tiles wide: the middle line and one beside it

WORLDS = {
    #            floor  mass   accent
    "desert":   (".",   "⟁",   "⍟"),
    "city":     ("=",   "=",   "≡"),
    "chult":    ("ᛗ",   "ᚷ",   "ᚺ"),
    "feywild":  ("ᛟ",   "ᛇ",   "☼"),
    "hell":     ("·",   "█",   "≋"),
    "courtyard": ("⌽",  "⌾",   "⌽"),
    "ship":     ("⌼",   "⌼",   "⌼"),
    "snow":     ("❄",   "❅",   "❆"),
}
FLOOR = {name: chars[0] for name, chars in WORLDS.items()}

# One ruin, on the far shore. The region's own masonry is still turning
# up at the far end of it, which is most of what says this is still the
# Chult desert and not somewhere new.
RUINS = ((80, 30, 6, 5),)

# Each island's own enemy. Fewer than the seventh map's, on purpose:
# there the danger was how many of them there were, and here it is that
# there is nowhere to back away to.
GARRISON = (
    (1, "⌴", 3),        # snakes, in the jungle
    (2, "Ԓ", 3),        # spined devils, on the basalt
    (3, "⍂", 2),        # knights, on the courtyard
    (6, "⌺", 2),        # redcaps, in the Feywild
    (5, "ᛊ", 2),        # skeletons, in the far ruin
)
CLEARANCE = 3           # how far an enemy stands off a causeway landing

# Everything on this map that came from somewhere else, which
# here is everything except the two desert shores.
FRAGMENT_CHARS = {
    "=", "≡", "ᛗ", "ᚷ", "ᚺ", "ᛟ", "ᛇ", "☼",
    "·", "█", "≋", "⌼", "⌽", "⌾", "❄", "❅", "❆",
}

ANCHOR = (9, MID_Y + 4)
ARRIVAL = (4, MID_Y)


def _blank():
    """Nothing but the Sea. Everything else is put back on top of it."""
    return [["V" for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def island_at(x: int, y: int) -> int | None:
    """Which island this tile is part of, if any.

    An ellipse with a wobble on its rim, the same shape the oasis and
    the ruins' tears use. Drawn true, an island in a sixteen-pixel grid
    comes out as a stamped oval, and a sea full of ovals reads as a
    diagram of a sea.
    """
    for index, (cx, cy, rx, ry, _) in enumerate(ISLANDS):
        nx, ny = (x - cx) / rx, (y - cy) / ry
        distance = math.hypot(nx, ny)
        if distance == 0.0:
            return index
        wobble = (0.16 * math.sin(math.atan2(ny, nx) * 3.0 + index)
                  + 0.09 * math.sin(math.atan2(ny, nx) * 7.0 + index * 2.1))
        if distance <= 1.0 + wobble:
            return index
    return None


def _paint(grid) -> None:
    for y in range(HEIGHT):
        for x in range(WIDTH):
            index = island_at(x, y)
            if index is None:
                continue
            world = ISLANDS[index][4]
            floor, mass, accent = WORLDS[world]
            if world == "city":
                grid[y][x] = accent if y == ISLANDS[index][1] else floor
                continue
            grain = (math.sin(x * 0.31 + y * 0.17)
                     + math.sin(x * 0.13 - y * 0.29 + 1.1))
            if grain > 1.15:
                grid[y][x] = accent
            elif grain > 0.45:
                grid[y][x] = mass
            else:
                grid[y][x] = floor


def _causeways(grid) -> set[tuple[int, int]]:
    """Ledges between the islands, and the tiles they own.

    Two tiles wide, which is the narrowest a route can be and still be
    walked rather than threaded, and made of the ground at either end
    rather than of a material of its own -- half one world and half the
    other. Nobody built these. They are what happens to be left.
    """
    owned: set[tuple[int, int]] = set()
    for a, b in CAUSEWAYS:
        ax, ay = ISLANDS[a][0], ISLANDS[a][1]
        bx, by = ISLANDS[b][0], ISLANDS[b][1]
        steps = max(abs(bx - ax), abs(by - ay))
        for step in range(steps + 1):
            along = step / max(1, steps)
            cx = round(ax + (bx - ax) * along)
            cy = round(ay + (by - ay) * along)
            world = ISLANDS[a if along < 0.5 else b][4]
            for oy in range(-CAUSEWAY_HALF, CAUSEWAY_HALF + 2):
                for ox in range(-CAUSEWAY_HALF, CAUSEWAY_HALF + 2):
                    tx, ty = cx + ox, cy + oy
                    if not (RIM <= ty < HEIGHT - RIM
                            and RIM <= tx < WIDTH - RIM):
                        continue
                    # An island's own ground wins where the two meet:
                    # a causeway drawn straight over an island paints a
                    # stripe of somewhere else across the middle of it.
                    here = island_at(tx, ty)
                    grid[ty][tx] = FLOOR[
                        ISLANDS[here][4] if here is not None else world
                    ]
                    owned.add((tx, ty))
    return owned


def _ruin(grid, left, top, width, height) -> None:
    for y in range(top - 1, top + height + 1):
        for x in range(left - 1, left + width + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH \
                    and island_at(x, y) is not None:
                grid[y][x] = "⌖"
    for y in range(top, top + height):
        for x in range(left, left + width):
            if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                continue
            if island_at(x, y) is None:
                continue
            edge = (y in (top, top + height - 1)
                    or x in (left, left + width - 1))
            if not edge or (x * 5 + y * 3 + left + top) % 7 < 2:
                grid[y][x] = "⌖"
            else:
                grid[y][x] = "⌗"


def _garrison(grid, causeways: set[tuple[int, int]]) -> None:
    """One kind of enemy per island, and never at a landing.

    The islands are small and the causeways arrive at their edges, so
    an enemy standing where a ledge lands is not an encounter -- it is
    a two-tile bridge with something on the far end of it and the Sea
    on both sides.
    """
    for index, marker, wanted in GARRISON:
        world = ISLANDS[index][4]
        placed: list[tuple[int, int]] = []
        for y in range(RIM + 1, HEIGHT - RIM - 1):
            for x in range(RIM + APPROACH, WIDTH - RIM - 1):
                if len(placed) >= wanted:
                    break
                if island_at(x, y) != index:
                    continue
                if grid[y][x] != FLOOR[world]:
                    continue
                if any(abs(px - x) + abs(py - y) < 6 for px, py in placed):
                    continue
                if any(abs(cx - x) + abs(cy - y) < CLEARANCE
                       for cx, cy in causeways):
                    continue
                room = sum(
                    1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if grid[y + dy][x + dx] == FLOOR[world]
                )
                if room < 3:
                    continue
                grid[y][x] = marker
                placed.append((x, y))


def build():
    grid = _blank()
    _paint(grid)
    for ruin in RUINS:
        _ruin(grid, *ruin)
    for left, top, width, height in RUINS:
        dress_ruin(grid, left, top, width, height, seed=left + top)
    causeways = _causeways(grid)

    # The desert islands still fray at their own rims, the same way the
    # fragments do on every map behind this one. Everything else here
    # is already surrounded by Sea and has nothing left to fray into.
    astral_fringe(grid, FRAGMENT_CHARS, seed=9.1,
                  protect=causeways)

    _rect(grid, 0, 0, WIDTH - 1, RIM - 1, "#")
    _rect(grid, 0, HEIGHT - RIM, WIDTH - 1, HEIGHT - 1, "#")
    _rect(grid, 0, 0, RIM - 1, HEIGHT - 1, "#")
    _rect(grid, WIDTH - RIM, 0, WIDTH - 1, HEIGHT - 1, "#")

    half = GAP // 2
    _rect(grid, 0, MID_Y - half, RIM - 1, MID_Y + half, "⮜")
    _rect(grid, WIDTH - RIM, MID_Y - half, WIDTH - 1, MID_Y + half, "⮞")
    for y in range(MID_Y - half, MID_Y + half + 1):
        for x in range(RIM, RIM + APPROACH):
            grid[y][x] = "."
        for x in range(WIDTH - RIM - APPROACH, WIDTH - RIM):
            grid[y][x] = "."

    _garrison(grid, causeways)
    dress_fragments(grid, seed=9.6, protect=causeways)
    # ...and the castle finished: crenellation on the curtain, drum
    # towers on the corners and the stumps, banners on the faces
    # that show. All of it converted from stone that was already
    # there, so nothing about the walk changes.
    dress_castle(grid, seed=8)

    grid[ARRIVAL[1]][ARRIVAL[0]] = "⍵"
    grid[ANCHOR[1]][ANCHOR[0]] = "⍹"
    grid[MID_Y][WIDTH - RIM - 2] = "⎀"
    return grid


HEADER = (
    "; DESERT EAST 8 - Phase 13, where the ground has mostly gone\n"
    "; (92x68). The Astral Sea is the map; what is left of the worlds\n"
    "; is islands in it, joined by causeways two tiles wide. Every walk\n"
    "; across is a ledge with the Sea on both sides.\n"
    "; Two islands have no causeway at all: drawn, lit, weathered, and\n"
    "; impossible to stand on. A collision this big should have places\n"
    "; in it that Chuck can only look at.\n"
    "; The causeways change material halfway, because nobody built\n"
    "; them -- they are what happens to be left of the ground between\n"
    "; two things that were never near each other.\n"
    "; East is the trio, and the end of the walk.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_east_8.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
