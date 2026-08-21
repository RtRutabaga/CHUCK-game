"""Generate the authored Cabin grounds and compact exterior landmark."""

from pathlib import Path
import random


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 80
HEIGHT = 64


def _path(grid, start, end, radius=1):
    x0, y0 = start
    x1, y1 = end
    steps = max(abs(x1 - x0), abs(y1 - y0))
    for step in range(steps + 1):
        t = step / max(1, steps)
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        for oy in range(-radius, radius + 1):
            for ox in range(-radius, radius + 1):
                if 0 <= y + oy < HEIGHT and 0 <= x + ox < WIDTH:
                    grid[y + oy][x + ox] = "⌇"


# The fire circle, and where the world stops being a clearing.
#
# The trail and the lit mushrooms used to run on south past the fire and
# off the bottom of the map, which read as a way out that goes nowhere.
# They end at the fire now, and everything south of it is the forest the
# cabin stands in: a few rows of thickening stand, then trees closed
# over entirely.
FIRE = (57, 43)
FOREST_EDGE = FIRE[1] + 3      # firs crowd in from here south...
FOREST_SOLID = FIRE[1] + 8     # ...and close over completely here

CABIN_TILE = (62, 34)          # the tile the cabin prop hangs from
CABIN_COVERAGE = 0.38          # how much of a tile the building must fill


# The porch, its steps, and the deck boards, as drawn. Any tile the
# cabin sprite fills mostly with these is board Chuck stands on rather
# than building he walks around.
CABIN_BOARDS = ((104, 74, 48), (138, 100, 64), (70, 48, 32), (88, 62, 40))
CABIN_BOARD_SHARE = 0.20
# Where the deck meets the wall, as a fraction of the sprite height. The
# porch posts and the railing are the same timber as the deck, so
# without this the posts standing beside the cabin were read as floor.
CABIN_DECK_TOP = 132 / 188


def _cabin_footprint():
    """Every tile the drawn cabin actually stands on.

    Taken from the sprite's own alpha rather than from a rectangle
    written out by hand. A gable-roofed building is not a rectangle --
    the roof reaches further than the walls at the ridge and less at the
    eaves -- and the two drifted apart every time the art moved. Reading
    the coverage back off the finished sprite means collision follows
    the visible mass by construction.
    """
    import pygame

    pygame.init()
    image = pygame.image.load(
        str(ROOT / "assets" / "sprites" / "objects" / "tahuya_cabin.png")
    )
    width, height = image.get_size()
    left = CABIN_TILE[0] * 16 + 8 - width // 2
    top = (CABIN_TILE[1] + 1) * 16 - height
    boards = set(CABIN_BOARDS)
    solid, deck = [], []
    for row in range((top // 16), (top + height) // 16 + 1):
        for col in range((left // 16), (left + width) // 16 + 1):
            covered = board = 0
            for y in range(row * 16, row * 16 + 16):
                for x in range(col * 16, col * 16 + 16):
                    px, py = x - left, y - top
                    if not (0 <= px < width and 0 <= py < height):
                        continue
                    pixel = image.get_at((px, py))
                    if pixel[3] <= 128:
                        continue
                    covered += 1
                    if tuple(pixel)[:3] in boards:
                        board += 1
            floor = (top + height * CABIN_DECK_TOP) // 16
            if row >= floor and board / 256.0 >= CABIN_BOARD_SHARE:
                deck.append((row, col))
            elif covered / 256.0 >= CABIN_COVERAGE:
                solid.append((row, col))
    # Close any single tile the treads happen to miss: a hole in the
    # middle of a staircase is not a design, it is a rounding error.
    filled = set(deck)
    for row, col in list(filled):
        for dr, dc in ((0, 1), (1, 0)):
            gap = (row + dr, col + dc)
            beyond = (row + dr * 2, col + dc * 2)
            if gap not in filled and beyond in filled:
                deck.append(gap)
    return solid, deck


def build_map():
    grid = [["♟" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # The hand-drawn reference places a broad irregular clearing west of a
    # long north/south cabin.  Keep that silhouette rather than centring the
    # building as a generic game landmark.
    for y in range(4, FOREST_SOLID):
        left = 4 + abs(y - 31) // 13
        right = 75 - abs(y - 31) // 20
        for x in range(left, right + 1):
            grid[y][x] = "ᶠ"

    # The western arrival begins as a narrow, slightly wandering foot trail,
    # then opens toward the compact cabin's sole south door and fire circle.
    west_approach = (
        ((5, 33), (10, 31)),
        ((10, 31), (16, 32)),
        ((16, 32), (23, 30)),
        ((23, 30), (30, 32)),
        ((30, 32), (37, 30)),
        ((37, 30), (44, 31)),
    )
    for start, end in west_approach:
        _path(grid, start, end, 0)
    _path(grid, (44, 31), (52, 34), 2)
    _path(grid, (52, 34), (59, 37), 2)
    # ...and stops at the fire. There is nothing south of it to walk to.
    _path(grid, (59, 37), (58, FIRE[1]), 2)

    # The exterior cabin is still smaller than its interior map, but it is
# a proper gable-roofed landmark now rather than a compact block, so
# its footprint follows the drawn mass: roof to the eaves, the deck
# walkable under the porch, and the steps where they are drawn.
    # One procedural three-quarter-view landmark carries its roof, walls,
    # windows, porch, and stairs. Collision follows the visible building mass,
    # while a narrow porch corridor reaches the sole south-facing door.
    mass, boards = _cabin_footprint()
    for y, x in mass:
        grid[y][x] = "♟"
    # Only what the cabin actually draws is walkable board. The porch used
    # to be a rectangle wider than the deck on it, which left bare planks
    # lying around the building's feet like spilled flooring, so the deck
    # and the steps are read off the sprite the same way the mass is: a
    # tile is boards if the cabin fills it with the porch's own timber.
    for y, x in boards:
        grid[y][x] = "↟" if y >= 34 else "▣"
    # Three tiles of doorway rather than one. A single-tile door on a
    # building this size has to be lined up on before it will open.
    for x in range(58, 61):
        grid[31][x] = "Ɛ"
    grid[33][59] = "ኂ"
    grid[34][62] = "ℂ"

    # Real-place landmarks from the authored drawing.
    grid[13][18] = "◌"       # circular UFO object at upper-left
    grid[43][57] = "⚉"       # fire circle just south of the front steps
    grid[42][70] = "⌘"       # firewood shed close in on the south-east

    # The mushroom-light trail hugs the cabin clearing's west side, rather than
    # wandering through the middle of the clearing.
    # ...and the last two turn in toward the fire and stop there with it,
    # so the lit path leads somewhere instead of trailing off into trees.
    for x, y in ((44, 13), (45, 20), (44, 27), (45, 34),
                 (48, 39), (53, 42)):
        grid[y][x] = "✦"

    # A dense but irregular Douglas-fir stand fills the west side. A fixed
    # authored seed gives natural spacing without a tree-farm grid and keeps
    # the same forest on every load.
    rng = random.Random(1204)
    candidates = [
        (x, y)
        for y in range(5, 60)
        for x in range(6, 44)
        if grid[y][x] == "ᶠ"
    ]
    rng.shuffle(candidates)
    firs = []
    for x, y in candidates:
        if any(abs(x - px) <= 1 and abs(y - py) <= 1 for px, py in firs):
            continue
        grid[y][x] = "♣"
        firs.append((x, y))
        if len(firs) == 118:
            break
    for x, y in ((73, 12), (75, 45)):
        if grid[y][x] == "ᶠ":
            grid[y][x] = "♣"
    # South of the fire the spacing rule is dropped: the last rows before
    # the solid stand are planted thick, so the tree line closes in
    # rather than ending at a straight edge.
    # Thicker the further south, and off the same authored seed as the
    # stand above: a modulo pattern here planted the tree farm the west
    # side was carefully built to avoid.
    for y in range(FOREST_EDGE, FOREST_SOLID):
        crowding = 0.42 + 0.44 * (y - FOREST_EDGE) / (
            FOREST_SOLID - FOREST_EDGE - 1
        )
        for x in range(5, 76):
            if grid[y][x] == "ᶠ" and rng.random() < crowding:
                grid[y][x] = "♣"

    # A handful of the established scratchable cigarette-grass tufts soften
    # the clearing and reward inspecting the tighter west approach.
    for x, y in ((12, 29), (18, 34), (26, 28), (33, 34),
                 (40, 28), (47, 18), (47, 43), (52, 45)):
        if grid[y][x] in {"ᶠ", "♣"}:
            grid[y][x] = "ʛ"

    # The cutscene emerges onto the western trail; the one Ashtray is close
    # enough to discover naturally but does not interrupt the reveal.
    grid[31][10] = "ኀ"
    grid[36][24] = "ኁ"
    return ["".join(row) for row in grid]


def main():
    output = ROOT / "assets" / "maps" / "tahuya_cabin_exterior.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
