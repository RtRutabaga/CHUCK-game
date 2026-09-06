"""Generate the second map east -- the collision gets its second world.

East 1 was four fifths desert with a slab of road in it. This map is
the next step of the same escalation and nothing more: still mostly
desert, but the intrusion is a good deal bigger, there are two worlds
in it rather than one, and one of them brought its wildlife.

The jungle is the point. It is a wedge of Chult -- the real jungle, the
same art as the map Chuck crawled through in Phase 4 -- pushed into the
sand along the northern half, with a stream in it that still runs. It
is dense enough that walking into it means threading between the trees
rather than crossing open ground, and the snakes that came with it are
in there where the cover is.

The road comes back too, smaller: one broken length of it running out
of the western edge and stopping in the sand. A fragment that appeared
once as a bridge and again as debris is the collision saying the same
thing twice in different tones, which is more use than a new material
would be this early.

Nothing here is a wall. The wedge stops halfway down the map, so the
southern sand runs clear from one door to the other and a player in a
hurry can walk past the whole thing -- the escalation on this map is in
what is on it, not yet in what it makes you do. East 1 gave Chuck a
crossing he had to take; this one gives him somewhere he may go.

Going in is worth it and survivable: the growth is thick but the open
ground inside it is one connected mass, so the jungle is threaded
rather than solved.
"""

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_collided_common import astral_fringe


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 72
HEIGHT = 52

GAP = 5
RIM = 1
APPROACH = 5

# The jungle wedge: an irregular mass in the north, thinning southward
# so it reads as something that came to rest here rather than a shape
# somebody drew. `_jungle_depth` is how far south it reaches per column.
JUNGLE_LEFT = 14
JUNGLE_RIGHT = 58
JUNGLE_DEEP = 26        # deepest it reaches at its middle
STREAM_X = 36           # the stream runs south out of the jungle's heart

# The road fragment: shorter than east 1's and going nowhere.
ROAD_Y = 40
ROAD_HALF_H = 2
ROAD_LEFT = 2
ROAD_RIGHT = 22

# Astral scars, smaller than east 1's single tear and scattered rather
# than spanning: the ground is coming apart in more places at once.
SCARS = ((30, 44, 7, 3), (52, 34, 4, 6), (62, 12, 3, 5), (8, 20, 4, 4))

RUINS = ((46, 42, 8, 6), (6, 30, 7, 5))
OUTCROPS = ((24, 40, 4, 3), (64, 42, 3, 4), (2, 12, 3, 3))
SCRUB = ((20, 36, ), (30, 38,), (44, 36,), (58, 45,), (12, 44,),
         (68, 30,), (26, 47,), (52, 48,))
SNAKES = ((24, 12), (33, 8), (42, 15), (50, 10), (30, 20), (46, 6),
          (20, 7), (54, 18))
ANCHOR = (6, 26)        # by the west gap, before any of it
ARRIVAL = (4, 26)


# Everything on this map that came from somewhere else. The seam
# between it and the desert gets frayed with Astral Sea, so the
# fragment reads as having torn its way in rather than as having
# been laid down on the sand.
FRAGMENT_CHARS = {"=", "≡", "ᛗ", "ᚷ", "ᚺ"}


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _jungle_depth(x: int) -> int:
    """How far south the jungle reaches in this column, or 0.

    A raised cosine across the wedge's width, roughened by two sines so
    the southern edge is ragged. A clean arc of jungle would read as a
    hedge somebody planted, and the whole point of a fragment is that
    nothing arranged it.
    """
    if not JUNGLE_LEFT <= x <= JUNGLE_RIGHT:
        return 0
    span = JUNGLE_RIGHT - JUNGLE_LEFT
    across = (x - JUNGLE_LEFT) / span
    bow = 0.5 - 0.5 * math.cos(across * 2.0 * math.pi)
    ragged = 0.10 * math.sin(x / 3.0) + 0.07 * math.sin(x / 1.7 + 2.0)
    depth = (bow + ragged) * JUNGLE_DEEP
    return max(0, round(depth))


def _weather(grid) -> None:
    patches = (
        (6, 36, 12, 5, ","), (56, 24, 12, 6, ","), (28, 30, 12, 4, ","),
        (14, 46, 14, 4, "⟁"), (60, 46, 10, 4, "⟁"), (66, 20, 6, 8, "⟁"),
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


def _jungle(grid) -> None:
    """The wedge of Chult, and the stream still running through it."""
    for x in range(WIDTH):
        depth = _jungle_depth(x)
        for y in range(RIM, RIM + depth):
            if not (0 <= y < HEIGHT):
                continue
            # Dense at the heart, open toward the ragged southern edge:
            # a fragment with a uniform interior is a green rectangle.
            #
            # Summed sines rather than a modular hash. Two attempts at
            # this used `(ax + by) % n`, and both failed in the same way
            # for the same reason: a linear form modulo n is constant
            # along a family of parallel lines, so the growth came out
            # as stripes -- horizontal the first time, diagonal the
            # second. The diagonal one was much worse than it looked,
            # because it left the open tiles connected only corner to
            # corner, and a rat walks on edges. There was no way through
            # the jungle at all.
            from_edge = (RIM + depth) - y
            growth = (math.sin(x * 0.55 + y * 0.31)
                      + math.sin(x * 0.23 - y * 0.47)
                      + math.sin((x + y) * 0.17 + 1.3))
            solid = from_edge > 3 and growth > 0.15
            grid[y][x] = "ᚷ" if solid else "ᛗ"
    # The stream runs south out of the jungle and stops where the
    # jungle does, because that is where its riverbed ends too.
    for y in range(RIM, RIM + _jungle_depth(STREAM_X)):
        drift = round(1.6 * math.sin(y / 4.0))
        for x in range(STREAM_X + drift - 1, STREAM_X + drift + 2):
            if 0 <= x < WIDTH and grid[y][x] in ("ᛗ", "ᚷ"):
                grid[y][x] = "ᚺ"


def _road(grid) -> None:
    for y in range(ROAD_Y - ROAD_HALF_H, ROAD_Y + ROAD_HALF_H + 1):
        for x in range(ROAD_LEFT, ROAD_RIGHT + 1):
            if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                continue
            # It breaks up as it goes east: the further from the edge it
            # came in at, the less of it is left.
            along = (x - ROAD_LEFT) / (ROAD_RIGHT - ROAD_LEFT)
            if along > 0.45 + ((x * 3 + y * 5) % 6) / 9:
                continue
            grid[y][x] = "≡" if y == ROAD_Y else "="


def _scar(grid, left, top, width, height) -> None:
    """One torn-open patch of Astral Sea.

    An ellipse with a wobble on it rather than a rectangle. East 1's
    tear wanders down the map and reads as ground come apart; the same
    thing drawn square reads as somebody having set a tile down, and
    four of them read as a pattern.
    """
    cx, cy = left + width / 2, top + height / 2
    rx, ry = max(1.0, width / 2), max(1.0, height / 2)
    for y in range(top - 1, top + height + 1):
        for x in range(left - 1, left + width + 1):
            if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                continue
            nx, ny = (x - cx) / rx, (y - cy) / ry
            wobble = 0.22 * math.sin(math.atan2(ny, nx) * 3.0 + left)
            if math.hypot(nx, ny) <= 1.0 + wobble:
                grid[y][x] = "V"


def _ruin(grid, left, top, width, height) -> None:
    _rect(grid, left - 1, top - 1, left + width, top + height, "⌖")
    for y in range(top, top + height):
        for x in range(left, left + width):
            edge = (y in (top, top + height - 1)
                    or x in (left, left + width - 1))
            if not edge or (x * 5 + y * 3 + left + top) % 7 < 2:
                grid[y][x] = "⌖"
            else:
                grid[y][x] = "⌗"


def _nearest_floor(grid, x: int, y: int) -> tuple[int, int]:
    """The closest open jungle tile to (x, y), searching outward."""
    for radius in range(0, 8):
        for oy in range(-radius, radius + 1):
            for ox in range(-radius, radius + 1):
                cx, cy = x + ox, y + oy
                if not (0 <= cy < HEIGHT and 0 <= cx < WIDTH):
                    continue
                if grid[cy][cx] == "ᛗ":
                    return cx, cy
    raise ValueError(f"no jungle floor near {(x, y)}")


def build():
    grid = _blank()
    _weather(grid)
    for left, top, width, height in OUTCROPS:
        _rect(grid, left, top, left + width - 1, top + height - 1, "#")
    for ruin in RUINS:
        _ruin(grid, *ruin)
    _jungle(grid)
    _road(grid)
    astral_fringe(grid, FRAGMENT_CHARS, seed=1.3)
    for scar in SCARS:
        _scar(grid, *scar)
    for spot in SCRUB:
        x, y = spot[0], spot[1]
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

    # Snakes go on the nearest open jungle floor to each authored spot.
    # Dropped only where the exact tile happened to be floor, five of
    # the eight fell on dense growth and simply were not placed -- the
    # map looked deliberately sparse when it was actually just missing.
    for x, y in SNAKES:
        cx, cy = _nearest_floor(grid, x, y)
        grid[cy][cx] = "⌴"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "⌱"
    grid[mid_y][WIDTH - RIM - 2] = "⌵"
    grid[ANCHOR[1]][ANCHOR[0]] = "⌳"
    return grid


HEADER = (
    "; DESERT EAST 2 - Phase 13, the collision's second step (72x52).\n"
    "; A wedge of Chult jungle ('ᛗ' floor, 'ᚷ' dense, 'ᚺ' stream) pushed\n"
    "; into the northern half, with snakes ('⌴') in the cover. The city\n"
    "; road returns as debris ('='/'≡') running out of the west edge.\n"
    "; Scattered Astral scars rather than one tear -- the ground is\n"
    "; coming apart in more places at once, but none of it blocks.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_east_2.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
