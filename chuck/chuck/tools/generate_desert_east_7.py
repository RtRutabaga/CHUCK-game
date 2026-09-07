"""Generate the seventh map east -- where the collision stops being tidy.

Every map so far has been the desert with something in it. One world
per map, mostly, laid into sand that still reads as the ground the
fragment landed on. The phase document says the later maps should be
heavily fragmented and geographically impossible, and the honest
reading of that is that the desert stops being the ground: there are
nine pieces of world on this map and none of them is a majority.

They are laid out as cells around scattered points rather than as
shapes drawn by hand, which is the only way I know to get a patchwork
that does not read as a diagram. Two of the cells are Chult and they
are at opposite corners; two are desert and they do not touch. That is
the impossible part, and it is impossible in the specific way the
document asks for -- not "strange terrain" but *this place cannot be a
place*: you walk out of a snowfield straight onto a ship's deck.

Every border between two worlds is torn. On the earlier maps the Astral
Sea frayed the seam between a fragment and the sand; here there is no
sand to fray against, so it frays between the worlds themselves, and
the result is that most of the map is islands.

Which means the one thing this map has to guarantee is a way through.
It is guaranteed by construction rather than by luck: a corridor is
walked from the west gap to the east gap before anything is torn, and
every tile of it is protected from tearing afterwards. The corridor is
invisible -- it is made of whatever world it happens to be crossing,
and all that marks it is that the ground there was not taken away.

The enemies are the phase document's "final mechanical remix": six
kinds on one map, each one standing in the world it belongs to. Snakes
in the jungle, redcaps in the Feywild, spined devils on the basalt,
knights on the courtyard, skeletons in the ruins and orcs on the sand.
None of them is new. All of them being here at once is.
"""

import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_collided_common import astral_fringe, dress_fragments
from generate_desert_ruin_dressing import dress_ruin


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 88
HEIGHT = 64

GAP = 5
RIM = 1
APPROACH = 5

# The nine cells, and which world each one is. Written as points rather
# than rectangles because the borders between them then come out of the
# arithmetic: whichever point a tile is nearest to, that is the world it
# belongs to. Rectangles would have given straight seams, and a straight
# seam between two worlds reads as a wall somebody built.
#
# The repeats are deliberate. Two pieces of Chult in opposite corners
# and two of desert that never touch is the clearest possible statement
# that this is not a map of anywhere.
SITES = (
    (11, 13, "desert"),
    (32, 9, "city"),
    (56, 12, "chult"),
    (78, 17, "snow"),
    (17, 37, "feywild"),
    (41, 33, "hell"),
    (66, 35, "courtyard"),
    (27, 57, "ship"),
    (58, 55, "desert"),
    (81, 50, "chult"),
)

# Each world's ground, the thing it grows or heaps on that ground, and
# the rarer third material that gives it its accent. All of them come
# from the tilesets the worlds already use.
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
# What a player can stand on in each, which is what the corridor is
# carved out of and what the enemies are stood on.
FLOOR = {name: chars[0] for name, chars in WORLDS.items()}

# The way through, as waypoints. It wanders on purpose: a corridor that
# runs straight across the middle is a road, and this map is not
# allowed to have one.
MID_Y = HEIGHT // 2
# The row the city fragment's centre line runs along.
LANE_Y = SITES[1][1]
PATH = (
    (RIM, MID_Y), (12, 26), (22, 15), (34, 22), (44, 40),
    (57, 46), (68, 30), (79, 22), (WIDTH - RIM - 1, MID_Y),
)
CORRIDOR_HALF = 1       # the way through is three tiles wide

# Desert masonry, in the two desert cells, so the region's own ruins
# are still turning up this far east.
RUINS = ((8, 8, 7, 5), (54, 52, 7, 5))

# Enemies, per world. Each is placed on its own world's floor, well
# clear of the corridor: an enemy standing in the only way through is a
# toll rather than an encounter, and this map has too many of them for
# that to be survivable.
GARRISON = (
    ("chult", "⌴", 3),
    ("feywild", "⌺", 3),
    ("hell", "Ԓ", 3),
    ("courtyard", "⍂", 2),
    ("desert", "ᛊ", 3),
    ("desert", "❂", 2),
)
CLEARANCE = 4           # how far an enemy must stand off the corridor

ANCHOR = (6, MID_Y + 2)
ARRIVAL = (4, MID_Y)

FRAGMENT_CHARS = {
    "=", "≡", "ᛗ", "ᚷ", "ᚺ", "ᛟ", "ᛇ", "☼", "·", "█", "≋",
    "⌼", "⌽", "⌾", "❄", "❅", "❆",
}


def _blank():
    return [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]


def _rect(grid, left, top, right, bottom, char) -> None:
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                grid[y][x] = char


def site_at(x: int, y: int) -> int:
    """Which cell this tile belongs to.

    Nearest point wins, but the distance is measured with a wobble on
    it, so the borders bulge and bite instead of being the straight
    bisectors the arithmetic would otherwise give. A patchwork with
    ruled edges reads as stained glass.
    """
    best, best_d = 0, None
    for index, (sx, sy, _) in enumerate(SITES):
        wobble = 3.2 * math.sin(x * 0.19 + y * 0.23 + index * 1.7)
        distance = math.hypot(x - sx, y - sy) + wobble
        if best_d is None or distance < best_d:
            best, best_d = index, distance
    return best


def _paint(grid) -> None:
    """Nine worlds, wall to wall, with no desert holding them apart."""
    for y in range(HEIGHT):
        for x in range(WIDTH):
            world = SITES[site_at(x, y)][2]
            floor, mass, accent = WORLDS[world]
            if world == "city":
                # A road is not a texture. Its accent is the centre
                # line, so it goes along one row and nowhere else --
                # scattered by the same grain as everything else, the
                # lane markings came out as a field of white dashes.
                grid[y][x] = accent if y == LANE_Y else floor
                continue
            # The world's own texture inside its cell. Two summed sines
            # again: anything modular here comes out as stripes, which
            # this project has now learned twice.
            grain = (math.sin(x * 0.31 + y * 0.17)
                     + math.sin(x * 0.13 - y * 0.29 + 1.1))
            if grain > 1.15:
                grid[y][x] = accent
            elif grain > 0.45:
                grid[y][x] = mass
            else:
                grid[y][x] = floor


def _corridor(grid) -> set[tuple[int, int]]:
    """Walk the way through, and hand back every tile of it.

    Carved before anything is torn and protected from tearing
    afterwards, which is what makes the route a guarantee rather than a
    hope. On a map where every border is a hole, a corridor found by
    checking afterwards is a corridor that fails on the next edit.
    """
    protected: set[tuple[int, int]] = set()
    for index in range(len(PATH) - 1):
        (x0, y0), (x1, y1) = PATH[index], PATH[index + 1]
        steps = max(abs(x1 - x0), abs(y1 - y0))
        for step in range(steps + 1):
            along = step / max(1, steps)
            cx = round(x0 + (x1 - x0) * along)
            cy = round(y0 + (y1 - y0) * along)
            for oy in range(-CORRIDOR_HALF, CORRIDOR_HALF + 1):
                for ox in range(-CORRIDOR_HALF, CORRIDOR_HALF + 1):
                    tx, ty = cx + ox, cy + oy
                    if not (0 <= ty < HEIGHT and 0 <= tx < WIDTH):
                        continue
                    # Whatever world it is crossing, at its walkable
                    # value. The corridor is never a material of its
                    # own: a path made of one thing all the way across
                    # nine worlds is a road, and a road here would be
                    # the map answering the question it exists to ask.
                    grid[ty][tx] = FLOOR[SITES[site_at(tx, ty)][2]]
                    protected.add((tx, ty))
    return protected


def _seams(grid, protected: set[tuple[int, int]]) -> int:
    """Tear the borders between worlds.

    The earlier maps fray the seam between a fragment and the sand.
    There is no sand here to fray against, so what gets torn is the
    join between one world and the next -- and since every tile is in
    some world, that is most of the map's structure. Low-frequency
    again, so stretches of a border are ripped through and other
    stretches simply touch.
    """
    torn = 0
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if (x, y) in protected:
                continue
            here = site_at(x, y)
            on_seam = any(
                0 <= y + dy < HEIGHT and 0 <= x + dx < WIDTH
                and site_at(x + dx, y + dy) != here
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            if not on_seam:
                continue
            tearing = (math.sin(x * 0.21 + y * 0.13 + 7.8)
                       + math.sin(x * 0.09 - y * 0.24 + 3.4)
                       + 0.5 * math.sin((x + y) * 0.4 + 1.9))
            if tearing < 0.15:
                continue
            grid[y][x] = "V"
            torn += 1
    return torn


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


def _garrison(grid, protected: set[tuple[int, int]]) -> None:
    """One world's own enemy in each world, and nowhere near the way in.

    Placed by scanning each cell rather than by hand, because the cells
    are decided by arithmetic and would have to be re-eyeballed every
    time a point moved. What is authored is how many and how far off
    the corridor they stand.
    """
    for world, marker, wanted in GARRISON:
        placed: list[tuple[int, int]] = []
        for y in range(RIM + 2, HEIGHT - RIM - 2):
            for x in range(RIM + APPROACH, WIDTH - RIM - APPROACH):
                if len(placed) >= wanted:
                    break
                if SITES[site_at(x, y)][2] != world:
                    continue
                if grid[y][x] != FLOOR[world]:
                    continue
                if any(abs(px - x) + abs(py - y) < 9 for px, py in placed):
                    continue
                if any(abs(px - x) + abs(py - y) < CLEARANCE
                       for px, py in protected):
                    continue
                # It has to be able to get off the tile it is standing
                # on, or it is scenery with a hitbox.
                room = sum(
                    1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if grid[y + dy][x + dx] == FLOOR[world]
                )
                if room < 3:
                    continue
                grid[y][x] = marker
                placed.append((x, y))
    return None


def build():
    grid = _blank()
    _paint(grid)
    for ruin in RUINS:
        _ruin(grid, *ruin)
    for left, top, width, height in RUINS:
        dress_ruin(grid, left, top, width, height, seed=left + top)
    protected = _corridor(grid)
    _seams(grid, protected)
    # The desert's own seam frayer still has work to do where the two
    # desert cells meet a fragment: this one eats sand, the other eats
    # borders, and between them nothing on the map joins cleanly.
    astral_fringe(grid, FRAGMENT_CHARS, seed=7.8, protect=protected)

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

    _garrison(grid, protected)
    dress_fragments(grid, seed=8.3, protect=protected)

    grid[ARRIVAL[1]][ARRIVAL[0]] = "⍳"
    grid[ANCHOR[1]][ANCHOR[0]] = "⍴"
    grid[MID_Y][WIDTH - RIM - 2] = "⍺"
    return grid


HEADER = (
    "; DESERT EAST 7 - Phase 13, where the collision stops being tidy\n"
    "; (88x64). Nine pieces of world and no majority: two of Chult in\n"
    "; opposite corners, two of desert that never touch, and a ship's\n"
    "; deck against a snowfield. Every border between them is torn.\n"
    "; The way through is guaranteed rather than found: a corridor is\n"
    "; walked west to east before anything is torn and protected after,\n"
    "; and it is made of whatever world it happens to be crossing.\n"
    "; Six kinds of enemy, each standing in the world it belongs to.\n"
    "; East leads on to the eighth, where the ground has mostly gone.\n"
)


def main() -> None:
    grid = build()
    out = ROOT / "assets" / "maps" / "desert_east_7.txt"
    body = "\n".join("".join(row) for row in grid)
    out.write_text(HEADER + body + "\n", encoding="utf-8")
    print(f"Wrote {out} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
