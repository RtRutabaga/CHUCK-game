"""Generate the sixth map east -- a frozen world, and the thing in it.

The second place Chuck has never been, and the first hazard in the
phase that is neither terrain nor a pursuer. A shelf of snow lies
across the north-east with a frozen pool in it, and one blue dragon
stands at the far side of the pool breathing lightning across it.

One, and enormous. There were two smaller ones here first, facing each
other with their lanes crossing, and the arithmetic of that was fine --
but two of a thing is a species and one of a thing is *the* dragon.
Eight tiles by six, nine times Chuck's height, and the only creature in
the game that cannot be fought: it earns its place by being the biggest
thing a player has seen, not by there being a pair of them.

The phase document is firm that this is not a boss fight. It cannot be
hurt, it does not chase, and nothing about it ends -- it is weather
with a temper. What the map asks is timing: the lane is lethal for
three quarters of a second in every four and a bit, and the snow either
side of it is wide enough to wait on.

The lane runs the length of the pool, which is the part of the shelf
worth crossing. Going round the whole shelf is possible and slow, which
is the right shape for an optional hazard: a player who does not want
to time anything walks the long way south.

The snow really snows, and only over the snow. SnowFall masks itself to
the fragment's own tiles, so the weather stops exactly where the world
does -- which turns out to be the clearest way of showing the player
what they are looking at.
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
WIDTH = 76
HEIGHT = 56

GAP = 5
RIM = 1
APPROACH = 5

# The frozen shelf: a mass across the north, deeper on the east side.
SHELF_LEFT = 20
SHELF_RIGHT = 70
SHELF_DEEP = 30
POOL = (46, 16, 8.0, 5.0)       # the frozen pool, centre and radii

# The dragon: east of the frozen pool, facing west along it, so the
# lane it breathes covers the one stretch of the shelf worth crossing.
#
# Well inside the snow. Placed below it the first time, it stood on a
# three-tile island of snow the spawner had forced under it -- a dragon
# on a coaster, in a desert, with weather falling on nothing but its own
# feet. It is eight tiles wide now, so the clearing it needs is the size
# of its own body rather than a courtesy square.
DRAGONS = ((58, 18, "⍅"),)
DRAGON_FOOT = (4, 3)        # half-width and half-height, in tiles
DRIFTS = ((34, 10), (40, 26), (54, 12), (58, 34), (26, 14), (66, 20))

SCRAPS = ((10, 12, 6, 3, "ᛗ"), (12, 44, 6, 3, "⌽"), (66, 46, 5, 3, "·"))
RUINS = ((8, 26, 7, 6),)
SCRUB = ((16, 20), (14, 38), (24, 48), (70, 50), (18, 8))
WAYPOINT = (8, 30)
ARRIVAL = (4, 30)

# Everything on this map that came from somewhere else.
FRAGMENT_CHARS = {"❄", "❅", "❆", "ᛗ", "⌽", "·"}


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _weather(grid) -> None:
    patches = (
        (6, 14, 10, 5, ","), (14, 46, 12, 5, ","), (8, 36, 9, 6, "⟁"),
        (30, 46, 14, 5, "⟁"),
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


def _shelf_depth(x: int) -> int:
    """How far south the snow reaches in this column, or 0."""
    if not SHELF_LEFT <= x <= SHELF_RIGHT:
        return 0
    across = (x - SHELF_LEFT) / (SHELF_RIGHT - SHELF_LEFT)
    # Deeper toward the east, with a ragged southern edge.
    bow = 0.45 + 0.55 * across
    ragged = 0.09 * math.sin(x / 3.4) + 0.06 * math.sin(x / 1.9 + 1.2)
    return max(0, round((bow + ragged) * SHELF_DEEP))


def _shelf(grid) -> None:
    for x in range(WIDTH):
        depth = _shelf_depth(x)
        for y in range(RIM, RIM + depth):
            if 0 <= y < HEIGHT:
                grid[y][x] = "❄"

    cx, cy, rx, ry = POOL
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] != "❄":
                continue
            nx, ny = (x - cx) / rx, (y - cy) / ry
            wobble = 0.15 * math.sin(math.atan2(ny, nx) * 3.0 + 0.8)
            if math.hypot(nx, ny) <= 1.0 + wobble:
                grid[y][x] = "❆"

    for x, y in DRIFTS:
        # Drifts are heaped in threes, so they read as banked snow
        # rather than as boulders somebody set down.
        for ox, oy in ((0, 0), (1, 0), (0, 1)):
            if 0 <= y + oy < HEIGHT and 0 <= x + ox < WIDTH \
                    and grid[y + oy][x + ox] == "❄":
                grid[y + oy][x + ox] = "❅"


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
    _shelf(grid)
    for scrap in SCRAPS:
        _scrap(grid, *scrap)
    astral_fringe(grid, FRAGMENT_CHARS, seed=6.5)
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
    # East, onward. The gap was cut as open sand while there was
    # nothing behind it; it is a door now, and cutting it early is
    # what stops the map changing shape when its neighbour arrives.
    _rect(grid, WIDTH - RIM, mid_y - half, WIDTH - 1, mid_y + half, "⮞")
    for y in range(mid_y - half, mid_y + half + 1):
        for x in range(RIM, RIM + APPROACH):
            if grid[y][x] not in (",", "⟁"):
                grid[y][x] = "."
        for x in range(WIDTH - RIM - APPROACH, WIDTH - RIM):
            if grid[y][x] not in (",", "⟁"):
                grid[y][x] = "."

    for x, y, marker in DRAGONS:
        # A dragon has to stand on its own snow, and the ground in front
        # of it has to be clear enough for the lane to be worth timing.
        # The footprint is the sprite's, so nothing pokes out from under
        # a body eight tiles across.
        reach_x, reach_y = DRAGON_FOOT
        for oy in range(-reach_y, reach_y + 1):
            for ox in range(-reach_x, reach_x + 1):
                cx, cy = x + ox, y + oy
                if 0 <= cy < HEIGHT and 0 <= cx < WIDTH \
                        and grid[cy][cx] in (".", ",", "⟁", "❅"):
                    grid[cy][cx] = "❄"
        grid[y][x] = marker
    # Each world's own growth and debris, standing on its own
    # ground: a fragment is recognised by what is on it, and a
    # rectangle of somebody else's ground colour is not.
    #
    # Last, once every piece of ground on the map is final. Run
    # earlier it planted trees against a rim that had not been
    # drawn yet, and skipped the scraps of other worlds entirely
    # because they had not landed yet either.
    dress_fragments(grid, seed=7.0)
    # ...and the castle finished: crenellation on the curtain, drum
    # towers on the corners and the stumps, banners on the faces
    # that show. All of it converted from stone that was already
    # there, so nothing about the walk changes.
    dress_castle(grid, seed=6)
    grid[ARRIVAL[1]][ARRIVAL[0]] = "⍀"
    grid[mid_y][WIDTH - RIM - 2] = "⍵"
    return grid


HEADER = (
    "; DESERT EAST 6 - Phase 13, a frozen world (76x56).\n"
    "; '❄' snow, '❅' drift (solid), '❆' ice. It actually snows, and\n"
    "; only over these tiles: SnowFall masks itself to the fragment.\n"
    "; One blue dragon ('⍅'), eight tiles across, breathes lightning\n"
    "; west along the pool. It cannot be hurt and does not chase: the\n"
    "; map asks for timing, and the long way round the south asks for\n"
    "; nothing.\n"
    "; East leads on to the seventh map, where nine worlds meet.\n"
    "; 'þ' basalt rubble and '⍯' jungle bush on the scraps.\n"
    "; The ruins carry the hub's own fallen pieces: '⍏'/'⍐'\n"
    "; columns, '⍖'/'⍗' fallen ones, '⍓'/'⍔' blocks.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_east_6.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
