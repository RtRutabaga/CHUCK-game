"""Generate the third map east -- the Feywild lands on the desert.

The escalation so far has been quantity: one fragment, then two and
bigger. This map is a third again as much -- a third of the ground is
somebody else's -- but the change that matters is in kind. East 1 gave
Chuck a crossing and east 2 gave him somewhere optional to go; this is
not a patch lying in the sand any more. It is a piece of another place
with its own coast, its own light, and its own things living in it,
sitting in the middle of the map with the desert going round it.

The Feywild is the right world for that step because it is the only
one Chuck has visited that is not a shade of brown. A wedge of it in a
desert cannot be mistaken for weather.

The desert does still get you past: sand survives round the mass to the
north and to the south, so a player who wants nothing to do with the
Feywild can walk round it. Redcaps are in the growth, which is the
reason to want nothing to do with it.
"""

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_collided_common import astral_fringe, dress_fragments
from generate_desert_ruin_dressing import dress_ruin


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 76
HEIGHT = 56

GAP = 5
RIM = 1
APPROACH = 5

# The fey mass. An irregular blob filling the middle of the map, with
# its own ragged coast rather than a drawn outline.
FEY = (38, 28, 26.0, 17.0)      # centre x, centre y, x radius, y radius
POOLS = ((30, 22), (44, 32), (36, 36), (48, 20))
POLLEN = ((26, 30), (40, 24), (50, 28), (33, 17), (44, 40), (28, 38))
REDCAPS = ((30, 26), (42, 22), (36, 32), (48, 34), (26, 20), (44, 38))

SCARS = ((10, 10, 6, 5), (66, 44, 6, 6), (62, 12, 5, 4), (12, 46, 7, 4))
RUINS = ((6, 24, 7, 6), (64, 26, 6, 6))
SCRUB = ((16, 16), (20, 44), (58, 18), (56, 48), (8, 36), (70, 34))
ANCHOR = (6, 30)
ARRIVAL = (4, 30)


# Scraps of the worlds already met, still coming down.
SCRAPS = (
    (14, 8, 7, 3, "="), (60, 6, 5, 4, "ᛗ"), (18, 40, 6, 3, "ᛗ"),
)


# Everything on this map that came from somewhere else. The seam
# between it and the desert gets frayed with Astral Sea, so the
# fragment reads as having torn its way in rather than as having
# been laid down on the sand.
FRAGMENT_CHARS = {"ᛟ", "ᛇ", "ᛞ", "☼", "=", "ᛗ"}


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def _weather(grid) -> None:
    patches = (
        (8, 6, 12, 5, ","), (58, 6, 12, 5, ","), (10, 38, 10, 6, ","),
        (60, 36, 12, 6, "⟁"), (20, 48, 14, 4, "⟁"), (44, 48, 12, 4, "⟁"),
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


def _fey_reach(x: int, y: int) -> float:
    """How far inside the fey mass this tile is; <= 1 means inside.

    An ellipse with three harmonics on its rim, so the coast is ragged
    at more than one scale. A single wobble gives a shape that reads as
    a decorated oval; three give one that reads as a piece torn off.
    """
    cx, cy, rx, ry = FEY
    nx, ny = (x - cx) / rx, (y - cy) / ry
    angle = math.atan2(ny, nx)
    wobble = (0.13 * math.sin(angle * 3.0 + 0.7)
              + 0.08 * math.sin(angle * 5.0 - 1.1)
              + 0.05 * math.sin(angle * 9.0 + 2.3))
    return math.hypot(nx, ny) / (1.0 + wobble)


def _fey(grid) -> None:
    """The mass itself: growth, with open fey ground threaded through."""
    for y in range(RIM, HEIGHT - RIM):
        for x in range(RIM, WIDTH - RIM):
            reach = _fey_reach(x, y)
            if reach > 1.0:
                continue
            # Open at the coast, thickening inward -- but the thickness
            # is summed sines, not a modular hash, so the open ground
            # inside stays connected rather than becoming a lattice.
            growth = (math.sin(x * 0.48 + y * 0.29)
                      + math.sin(x * 0.21 - y * 0.44)
                      + math.sin((x + y) * 0.15 + 0.9))
            dense = reach < 0.85 and growth > 0.1
            grid[y][x] = "ᛇ" if dense else "ᛟ"

    for x, y in POOLS:
        # Glow pools are solid: bright, and to be walked round.
        for oy in range(-1, 2):
            for ox in range(-1, 2):
                if abs(ox) + abs(oy) > 1:
                    continue
                cx, cy = x + ox, y + oy
                if 0 <= cy < HEIGHT and 0 <= cx < WIDTH \
                        and grid[cy][cx] in ("ᛟ", "ᛇ"):
                    grid[cy][cx] = "ᛞ"
    for x, y in POLLEN:
        if 0 <= y < HEIGHT and 0 <= x < WIDTH and grid[y][x] == "ᛟ":
            grid[y][x] = "☼"


def _scar(grid, left, top, width, height) -> None:
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


def _nearest(grid, x: int, y: int, wanted: str) -> tuple[int, int]:
    for radius in range(0, 10):
        for oy in range(-radius, radius + 1):
            for ox in range(-radius, radius + 1):
                cx, cy = x + ox, y + oy
                if not (0 <= cy < HEIGHT and 0 <= cx < WIDTH):
                    continue
                if grid[cy][cx] == wanted:
                    return cx, cy
    raise ValueError(f"no {wanted!r} near {(x, y)}")


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
    _fey(grid)
    astral_fringe(grid, FRAGMENT_CHARS, seed=2.6)
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

    for x, y in REDCAPS:
        cx, cy = _nearest(grid, x, y, "ᛟ")
        grid[cy][cx] = "⌺"
    # Each world's own growth and debris, standing on its own
    # ground: a fragment is recognised by what is on it, and a
    # rectangle of somebody else's ground colour is not.
    #
    # Last, once every piece of ground on the map is final. Run
    # earlier it planted trees against a rim that had not been
    # drawn yet, and skipped the scraps of other worlds entirely
    # because they had not landed yet either.
    dress_fragments(grid, seed=3.1)
    grid[ARRIVAL[1]][ARRIVAL[0]] = "⌲"
    grid[mid_y][WIDTH - RIM - 2] = "⌷"
    grid[ANCHOR[1]][ANCHOR[0]] = "⌶"
    return grid


HEADER = (
    "; DESERT EAST 3 - Phase 13, the third world (76x56).\n"
    "; A mass of Feywild ('ᛟ' ground, 'ᛇ' growth, 'ᛞ' glow pools,\n"
    "; '☼' pollen) filling the middle, with redcaps ('⌺') in it. The\n"
    "; desert survives as a thin strip north and a wider way south.\n"
    "; '⍰' the Feywild's own grove trees stand on its growth, with\n"
    "; '⍱' shrubs and '⍲' mushrooms on the floor.\n"
    "; The ruins carry the hub's own fallen pieces: '⍏'/'⍐'\n"
    "; columns, '⍖'/'⍗' fallen ones, '⍓'/'⍔' blocks.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_east_3.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
