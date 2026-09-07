"""Generate the final trio encounter -- the end of the eastward walk.

Chuck has met these three twice before and both times he walked into
the middle of something already happening. This is the third and worst
of those, and the phase document asks for it to be the most chaotic
version: they are trying to close the collision, they are being pressed
while they do it, and Chuck is in the room.

The arena is built to one rule that is easy to state and easy to break:
*chaotic in material, clear in shape*. The floor is a patchwork of
nine worlds jammed together with no desert between them -- which is
what the map is about -- but almost none of it is solid. The document
is explicit that readability must not be spent on spectacle, and in a
room full of stray arrows the thing a player needs is open ground and
hazards they can see the edges of. So the worlds are underfoot and the
danger is above it.

What is authored rather than scattered: the rift the wizard is working
on, in the east; the three of them standing between Chuck and it; the
few lava veins and Astral cracks that give the floor teeth; and the
enemies pressing in, each standing on its own world's ground the way
they do everywhere else in the region.

Nothing here can be helped with. Chuck cannot fight for them, cannot
reach the rift, and cannot leave east -- the only way out of this map
is the way in, until the heroes finish.
"""

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_collided_common import astral_fringe  # noqa: F401


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 76
HEIGHT = 52

GAP = 5
RIM = 1
APPROACH = 6
MID_Y = HEIGHT // 2

# The floor: nine worlds, and only their floors. No dense growth, no
# walls, no drifts -- every one of those is somewhere an arrow stops
# and Chuck cannot, and this room is about the arrows.
#
# Laid on a rough grid so the patches stay small. Scattered by hand at
# half this count they came out fifteen tiles across, and a cell that
# size is a region rather than a fragment: the middle of the room was
# one broad sweep of desert, which is the one thing this map is not
# supposed to look like.
PATCHES = (
    (6, 8, "."), (17, 6, "⩊" if False else "ᛗ"), (28, 7, "⌽"),
    (39, 6, "·"), (50, 8, "⌖"), (58, 6, "⌼"),
    (7, 18, "❄"), (18, 17, "ᛟ"), (29, 18, "="),
    (40, 16, "⌖"), (50, 18, "ᛗ"), (58, 17, "."),
    (6, 27, "."), (17, 27, "⌽"), (28, 26, "ᛟ"),
    (39, 27, "❄"), (49, 26, "·"), (58, 28, "⌼"),
    (7, 37, "⌼"), (18, 36, "ᛗ"), (29, 37, "·"),
    (40, 36, "ᛟ"), (50, 37, "="), (58, 38, "."),
    (11, 46, "⌖"), (23, 46, "❄"), (35, 46, "⌽"),
    (47, 46, "ᛗ"), (58, 46, "·"),
)

# The rift, in the east: the thing the wizard is opening. It is the
# Astral Sea, because that is what the collision has been made of all
# the way here, and it is lethal for the same reason it has always
# been. Chuck cannot reach the heroes' work, only stand near it.
RIFT_X = 61
RIFT_BULGE = 4.5        # how far west it bows at its middle
BOLT_BAND = 7           # rows either side of the wizard's own

# The three of them, between Chuck and the rift, in the order the
# document names: fighter holding the north, wizard at the rift itself,
# ranger holding the south.
# The wizard stands on the last tile of ground before the rift, with
# it bowing toward him: authored a tile east of that he came out on a
# spit inside the thing, unreachable and looking like a mistake rather
# than like the man doing the work.
# Six tiles apart, not eighteen. The camera cuts to the three of them
# for their lines and frames the whole group, and the frame it uses
# lifts to keep their feet off the dialogue panel -- so the span that
# fits is well under a screen's height. Spread across a third of the
# map, as they were first, the fighter was simply not in the shot.
FIGHTER = (54, 23)
WIZARD = (55, 26)
RANGER = (54, 29)

# What is pressing them. Each stands on its own world's floor, the way
# every enemy east of the hub does; between them they are most of the
# adventure, which is the point of the room.
GARRISON = (
    ("ᛗ", "⌴", 2),      # snakes, out of Chult
    ("ᛟ", "⌺", 2),      # redcaps, out of the Feywild
    ("·", "Ԓ", 2),      # spined devils, out of Hell
    ("⌽", "⍂", 1),      # a knight, off the courtyard
    (".", "ᛊ", 3),      # skeletons, the region's own
    (".", "❂", 2),      # and orcs
)

# Teeth in the floor. Authored rather than scattered: a player being
# shot at needs the holes in the ground to be somewhere they can learn,
# and noise puts them where the fight already is.
LAVA_VEINS = (((28, 12), (33, 18)), ((40, 38), (46, 44)),
              ((18, 28), (21, 33)))
CRACKS = (((12, 8), (18, 6)), ((30, 30), (36, 28)),
          ((24, 38), (28, 45)), ((48, 14), (52, 20)),
          ((42, 47), (49, 49)))

ANCHOR = (7, MID_Y + 3)
ARRIVAL = (4, MID_Y)


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def patch_at(x: int, y: int) -> str:
    """Which world's floor this tile is. Nearest patch centre wins."""
    best, best_d = ".", None
    for px, py, char in PATCHES:
        wobble = 2.6 * math.sin(x * 0.23 + y * 0.19 + px * 0.7)
        distance = math.hypot(x - px, y - py) + wobble
        if best_d is None or distance < best_d:
            best, best_d = char, distance
    return best


def _floor(grid) -> None:
    for y in range(HEIGHT):
        for x in range(WIDTH):
            grid[y][x] = patch_at(x, y)


def _rift_edge(y: int) -> int:
    """The western edge of the rift in this row.

    It bows toward the heroes in the middle, which is where the wizard
    is standing: the thing is opening, and it opens at him.

    In the band his work travels down it comes all the way to him. That
    is not decoration -- everything he throws goes east, and it is only
    safe to make that the loudest thing in the room if there is no
    ground east of him for Chuck to be standing on. Left to the bow
    alone there was a column of walkable floor in the lane, one tile
    wide, which is exactly the sort of gap a fight finds.
    """
    across = (y - HEIGHT / 2) / (HEIGHT / 2)
    edge = RIFT_X - round(RIFT_BULGE * (1.0 - across * across))
    if abs(y - WIZARD[1]) <= BOLT_BAND:
        edge = min(edge, WIZARD[0] + 1)
    return edge


def _rift(grid) -> None:
    for y in range(HEIGHT):
        for x in range(_rift_edge(y), WIDTH):
            if 0 <= x < WIDTH:
                grid[y][x] = "V"


def _line(grid, start, end, char) -> None:
    (x0, y0), (x1, y1) = start, end
    steps = max(abs(x1 - x0), abs(y1 - y0))
    for step in range(steps + 1):
        along = step / max(1, steps)
        cx = round(x0 + (x1 - x0) * along)
        cy = round(y0 + (y1 - y0) * along)
        for ox, oy in ((0, 0), (1, 0), (0, 1)):
            if 0 <= cy + oy < HEIGHT and 0 <= cx + ox < WIDTH:
                grid[cy + oy][cx + ox] = char


def _teeth(grid) -> None:
    for start, end in LAVA_VEINS:
        _line(grid, start, end, "≋")
    for start, end in CRACKS:
        _line(grid, start, end, "V")


def _garrison(grid) -> None:
    """Enemies on their own worlds, and none of them in the doorway."""
    for ground, marker, wanted in GARRISON:
        placed: list[tuple[int, int]] = []
        for y in range(RIM + 2, HEIGHT - RIM - 2):
            for x in range(RIM + APPROACH, RIFT_X - 8):
                if len(placed) >= wanted:
                    break
                if grid[y][x] != ground:
                    continue
                if any(abs(px - x) + abs(py - y) < 7 for px, py in placed):
                    continue
                room = sum(
                    1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if grid[y + dy][x + dx] == ground
                )
                if room < 3:
                    continue
                grid[y][x] = marker
                placed.append((x, y))


def build():
    grid = _blank()
    _floor(grid)
    _teeth(grid)
    _rift(grid)

    _rect(grid, 0, 0, WIDTH - 1, RIM - 1, "#")
    _rect(grid, 0, HEIGHT - RIM, WIDTH - 1, HEIGHT - 1, "#")
    _rect(grid, 0, 0, RIM - 1, HEIGHT - 1, "#")
    _rect(grid, WIDTH - RIM, 0, WIDTH - 1, HEIGHT - 1, "#")

    half = GAP // 2
    _rect(grid, 0, MID_Y - half, RIM - 1, MID_Y + half, "⮜")
    # The ground Chuck arrives on is kept clear of everything: he walks
    # into the middle of this, and he should get to see it before it
    # reaches him.
    for y in range(MID_Y - half - 1, MID_Y + half + 2):
        for x in range(RIM, RIM + APPROACH):
            if 0 <= y < HEIGHT:
                grid[y][x] = "."

    _garrison(grid)

    # The heroes last, so nothing can be authored on top of them, and
    # each on plain desert: they are standing on the one ground this
    # whole phase has been about.
    for (x, y), marker in ((FIGHTER, "⍻"), (WIZARD, "⍼"), (RANGER, "⍽")):
        for oy in range(-1, 2):
            for ox in range(-1, 2):
                if 0 <= y + oy < HEIGHT and 0 <= x + ox < WIDTH \
                        and grid[y + oy][x + ox] != "V":
                    grid[y + oy][x + ox] = "."
        grid[y][x] = marker

    grid[ARRIVAL[1]][ARRIVAL[0]] = "⍾"
    grid[ANCHOR[1]][ANCHOR[0]] = "⍿"
    return grid


HEADER = (
    "; DESERT TRIO - Phase 13, the final encounter (76x52).\n"
    "; The floor is nine worlds jammed together and almost none of it\n"
    "; is solid: chaotic in material, clear in shape. In a room full of\n"
    "; stray arrows what a player needs is open ground and hazards with\n"
    "; visible edges, so the worlds are underfoot and the danger is\n"
    "; above it.\n"
    "; '⍻' fighter, '⍼' wizard, '⍽' ranger, standing between Chuck and\n"
    "; the rift ('V') the wizard is opening in the east. '≋' lava veins\n"
    "; and Astral cracks give the floor teeth. Every enemy in it came\n"
    "; from one of the worlds the walk east passed through.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_trio.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
