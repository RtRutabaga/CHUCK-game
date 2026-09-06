"""Generate the fourth map east -- Phlegethos, and the first real cost.

Three maps of escalation have all been escalation of *presence*: more
of the map belonging to somewhere else, and more somewheres. Every one
of them could be walked past. This is where that stops.

A slab of the Nine Hells lies across the map from north rim to south
rim -- basalt, cliff, and lava running through it in channels. There is
no sand round it. Chuck goes over the basalt or he does not go on, and
the lava is a fall hazard, which means the phase document's "lava
hazards where Hell fragments appear" needed no new system at all: `≋`
has been lethal since Phlegethos, and it stays lethal here.

The basalt between the channels is wide enough to walk and narrow
enough to be worth looking at first. Spined devils came through with
it, and they are on the far side, so the crossing is the dangerous part
rather than the arrival.

The ashtray stands on the sand before the slab, which is the whole
reason it is there: this is the first map east where dying is likely.
"""

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_collided_common import astral_fringe, dress_fragments
from generate_desert_ruin_dressing import dress_ruin


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 72
HEIGHT = 56

GAP = 5
RIM = 1
APPROACH = 5

# The slab: basalt from rim to rim, its coasts ragged.
SLAB_LEFT = 22
SLAB_RIGHT = 52


def _slab_edges(y: int) -> tuple[int, int]:
    """(west edge, east edge) of the basalt in this row."""
    west = SLAB_LEFT + round(2.5 * math.sin(y / 7.0 + 0.4)
                             + 1.2 * math.sin(y / 3.0))
    east = SLAB_RIGHT + round(2.5 * math.sin(y / 6.0 + 2.1)
                              + 1.2 * math.sin(y / 2.6))
    return west, east


# Lava channels, running down the slab. Each is (x at the top, drift),
# and each wanders as it descends so the crossings are not in a line.
CHANNELS = ((30, 0.9), (41, -0.7), (48, 0.5))
CHANNEL_HALF = 1        # channels are three tiles wide
# Where each channel is bridged by unbroken basalt. Without these the
# slab would be three walls rather than one crossing.
FORDS = ((30, 14), (30, 38), (41, 22), (41, 46), (48, 12), (48, 34))
FORD_HALF = 2

CLIFFS = ((24, 6, 3, 5), (48, 44, 4, 6), (34, 2, 4, 3), (26, 48, 3, 4))

# The lava fall: Phlegethos's own, off the shoulder of the first cliff.
#
# It ends in the Astral Sea rather than in a river. That distinction is
# the whole reason it is here: a fall feeding a channel would just be a
# fourth channel with a nicer top, where a fall pouring into a hole in
# reality says what this whole region is about -- the lava is running
# out of the world rather than through it.
#
# Well north of the crossing corridor, because everything in it is
# lethal and the slab is the only way across the map.
LAVA_FALL = (25, 12)        # the tile the fall's sprite stands on
FALL_RUN = 4                # tiles of lava below it before the drop
FALL_VOID = (23, 17, 5, 3)  # left, top, width, height of the hole
# Phlegethos's own markers, one per facing. Hell needed no new marker
# for its devils: the Nine Hells already authored one per direction,
# each standing on basalt, which is exactly what this fragment is.
# Three watch back toward the crossing and one is looking away, so they
# read as posted rather than as a firing line awaiting the player.
DEVILS = ((58, 20, "Ԓ"), (60, 34, "Ԓ"),
          (56, 44, "Ԑ"), (62, 12, "Ԓ"))
SCARS = ((8, 8, 6, 5), (64, 48, 6, 5), (10, 44, 5, 6))
RUINS = ((8, 22, 7, 6), (60, 26, 6, 6))
SCRUB = ((16, 14), (14, 36), (66, 18), (58, 52), (18, 50))
ANCHOR = (16, 28)       # on the sand, before the crossing
ARRIVAL = (4, 28)


# Scraps of the worlds already met, still coming down.
SCRAPS = (
    (8, 12, 6, 3, "="), (62, 6, 5, 4, "ᛗ"), (10, 48, 6, 3, "ᛟ"),
    (64, 40, 5, 3, "ᛗ"),
)


# Everything on this map that came from somewhere else. The seam
# between it and the desert gets frayed with Astral Sea, so the
# fragment reads as having torn its way in rather than as having
# been laid down on the sand.
FRAGMENT_CHARS = {"·", "█", "≋", "=", "ᛗ", "ᛟ"}


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _weather(grid) -> None:
    patches = (
        (6, 12, 10, 5, ","), (58, 6, 12, 5, ","), (8, 34, 10, 5, "⟁"),
        (58, 38, 12, 6, "⟁"),
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


def _channel_x(top_x: float, drift: float, y: int) -> int:
    """Where a lava channel runs in this row."""
    return round(top_x + drift * y * 0.25
                 + 1.8 * math.sin(y / 5.0 + top_x))


def _slab(grid) -> None:
    """Basalt rim to rim, with lava down it and fords across the lava."""
    for y in range(RIM, HEIGHT - RIM):
        west, east = _slab_edges(y)
        for x in range(west, east + 1):
            if 0 <= x < WIDTH:
                grid[y][x] = "·"

    for top_x, drift in CHANNELS:
        for y in range(RIM, HEIGHT - RIM):
            cx = _channel_x(top_x, drift, y)
            forded = any(
                abs(fx - top_x) < 0.5 and abs(y - fy) <= FORD_HALF
                for fx, fy in FORDS
            )
            if forded:
                continue
            for x in range(cx - CHANNEL_HALF, cx + CHANNEL_HALF + 1):
                if 0 <= x < WIDTH and grid[y][x] == "·":
                    grid[y][x] = "≋"

    for left, top, width, height in CLIFFS:
        for y in range(top, top + height):
            for x in range(left, left + width):
                if 0 <= y < HEIGHT and 0 <= x < WIDTH and grid[y][x] == "·":
                    grid[y][x] = "█"


def _lava_fall(grid) -> None:
    """Lava off the cliff, a short run, and then nothing at all.

    Three pieces and they have to be in this order: the fall's own
    anchor tile, the run it pours into, and the hole the run ends in.
    Built the other way round the hole eats the run before the run
    exists, and the fall comes out pouring onto solid basalt.
    """
    x, y = LAVA_FALL
    grid[y][x] = "ƒ"
    # The run. Three tiles wide, matching the sprite's own width, so
    # the lava leaving the fall is the same lava that was in it.
    for step in range(1, FALL_RUN + 1):
        for offset in (-1, 0, 1):
            cx, cy = x + offset, y + step
            if not (0 <= cy < HEIGHT and 0 <= cx < WIDTH):
                continue
            if grid[cy][cx] in ("·", "█"):
                grid[cy][cx] = "≋"
    # ...and the hole. Ragged, because a rectangle of Astral Sea reads
    # as a trapdoor rather than as somewhere the ground has gone.
    left, top, width, height = FALL_VOID
    cx, cy = left + width / 2, top + height / 2
    rx, ry = width / 2, height / 2
    for cy_i in range(top - 1, top + height + 1):
        for cx_i in range(left - 1, left + width + 1):
            if not (0 <= cy_i < HEIGHT and 0 <= cx_i < WIDTH):
                continue
            nx, ny = (cx_i - cx) / rx, (cy_i - cy) / ry
            wobble = 0.25 * math.sin(math.atan2(ny, nx) * 3.0 + 0.7)
            if math.hypot(nx, ny) <= 1.0 + wobble:
                grid[cy_i][cx_i] = "V"


def _scar(grid, left, top, width, height) -> None:
    cx, cy = left + width / 2, top + height / 2
    rx, ry = max(1.0, width / 2), max(1.0, height / 2)
    for y in range(top - 1, top + height + 1):
        for x in range(left - 1, left + width + 1):
            if not (0 <= y < HEIGHT and 0 <= x < WIDTH):
                continue
            nx, ny = (x - cx) / rx, (y - cy) / ry
            wobble = 0.22 * math.sin(math.atan2(ny, nx) * 3.0 + left)
            if math.hypot(nx, ny) <= 1.0 + wobble and grid[y][x] not in (
                    "·", "≋", "█"):
                grid[y][x] = "V"


def _scrap(grid, left, top, width, height, char) -> None:
    """A small piece of somewhere else, dropped on the sand.

    The map each of these belongs to has one big fragment that gives it
    its character. These are the others still arriving: a few tiles of a
    world Chuck met further back, too small to change the route and
    large enough to notice. Without them each map reads as a clean
    single-world overlay, and the collision is supposed to be getting
    messier rather than tidier.
    """
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


def build():
    grid = _blank()
    _weather(grid)
    for ruin in RUINS:
        _ruin(grid, *ruin)
    # ...and what fell off them, out of the same box the
    # hub's ruins are dressed from. These are the same
    # building, still coming apart, further east.
    for left, top, width, height in RUINS:
        dress_ruin(grid, left, top, width, height,
                   seed=left + top)
    _slab(grid)
    _lava_fall(grid)
    astral_fringe(grid, FRAGMENT_CHARS, seed=3.9)
    for scrap in SCRAPS:
        _scrap(grid, *scrap)
    for scar in SCARS:
        _scar(grid, *scar)
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

    # The devils stand on their own basalt, which came through with
    # them: a scrap of Hell under each, out on the sand past the slab.
    for x, y, marker in DEVILS:
        for oy in range(-1, 2):
            for ox in range(-1, 2):
                cx, cy = x + ox, y + oy
                if 0 <= cy < HEIGHT and 0 <= cx < WIDTH \
                        and grid[cy][cx] in (".", ",", "⟁"):
                    grid[cy][cx] = "·"
        grid[y][x] = marker
    # Each world's own growth and debris, standing on its own
    # ground: a fragment is recognised by what is on it, and a
    # rectangle of somebody else's ground colour is not.
    #
    # Last, once every piece of ground on the map is final. Run
    # earlier it planted trees against a rim that had not been
    # drawn yet, and skipped the scraps of other worlds entirely
    # because they had not landed yet either.
    dress_fragments(grid, seed=4.4)
    grid[ARRIVAL[1]][ARRIVAL[0]] = "⌵"
    grid[mid_y][WIDTH - RIM - 2] = "⍀"
    grid[ANCHOR[1]][ANCHOR[0]] = "⌹"
    return grid


HEADER = (
    "; DESERT EAST 4 - Phase 13, the first crossing that costs (72x56).\n"
    "; A slab of Phlegethos rim to rim: '·' basalt, '█' cliff, and '≋'\n"
    "; lava in three wandering channels with fords across them. Lava is\n"
    "; already a fall hazard everywhere in the game and stays one here.\n"
    "; Spined devils wait on the far side. There is no way round.\n"
    "; A lava fall ('ƒ') pours off the northern cliff into a short\n"
    "; run that ends in the Astral Sea rather than in a river, and\n"
    "; 'þ' basalt rubble lies over the slab.\n"
    "; '⍯'/'⍲' the scraps' own growth, where there is room for it.\n"
    "; The ruins carry the hub's own fallen pieces: '⍏'/'⍐'\n"
    "; columns, '⍖'/'⍗' fallen ones, '⍓'/'⍔' blocks.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_east_4.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
