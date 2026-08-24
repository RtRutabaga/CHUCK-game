"""Generate the authored Cabin grounds and compact exterior landmark."""

import math
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
# ...except directly below the fire, where the stand bows away from it.
# A straight tree line across the bottom of a clearing reads as a fence;
# the wood should open out around a fire rather than stop at one.
FIRE_BAY_WIDTH = 15            # how far either side the opening reaches
FIRE_BAY_DEPTH = 7             # ...and how much further south at the fire


# The north side answers the south. The stand bows away from a second
# opening above the cabin, and a driveway's width of dirt runs out of
# the top of it through the trees -- which is how anyone ever got a
# cabin onto this ground in the first place.
NORTH_TREE = 10                # the tree line away from the opening
NORTH_BAY = 60                 # ...which bows north around this column
NORTH_BAY_WIDTH = 17
NORTH_BAY_DEPTH = 7
DRIVEWAY_HALF = 1              # a driveway is three tiles of dirt wide


def _north_edge(x: int) -> int:
    """The first clearing row in this column, coming down from the top.

    The same raised cosine the fire bay uses, mirrored. Both openings
    are bays in one wood rather than two differently-shaped holes.
    """
    reach = abs(x - NORTH_BAY) / NORTH_BAY_WIDTH
    if reach >= 1.0:
        return NORTH_TREE
    bow = 0.5 + 0.5 * math.cos(math.pi * reach)
    return NORTH_TREE - round(NORTH_BAY_DEPTH * bow)


def _south_edge(x: int) -> int:
    """The first fully wooded row in this column.

    A raised cosine rather than a straight line or a wedge: a wedge
    gives the clearing a pointed bottom, which reads as a path heading
    off south, and that is exactly what the trail stopping at the fire
    was meant to stop suggesting.
    """
    reach = abs(x - FIRE[0]) / FIRE_BAY_WIDTH
    if reach >= 1.0:
        return FOREST_SOLID
    bow = 0.5 + 0.5 * math.cos(math.pi * reach)
    return FOREST_SOLID + round(FIRE_BAY_DEPTH * bow)

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
    for y in range(NORTH_TREE - NORTH_BAY_DEPTH,
                   FOREST_SOLID + FIRE_BAY_DEPTH):
        left = 4 + abs(y - 31) // 13
        right = 75 - abs(y - 31) // 20
        for x in range(left, right + 1):
            if _north_edge(x) <= y < _south_edge(x):
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

    # The strip of astroturf, laid over the dirt from the foot of the
    # cabin steps. It is the walkway in the reference photographs: a
    # rectangle of fake grass on bare ground, straight-edged, going
    # nowhere in particular. Authored after the trail so it lies on top
    # of it rather than being cut by it.
    for y in range(35, 42):
        for x in range(57, 60):
            grid[y][x] = "ᵿ"

    # Real-place landmarks from the authored drawing.
    grid[10][53] = "◌"       # the circular object, west of the driveway
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
    # The same treatment along the northern line, thinning toward the
    # opening above the cabin so the bay stays a bay.
    north_band = FOREST_SOLID - FOREST_EDGE
    for y in range(NORTH_TREE - NORTH_BAY_DEPTH, NORTH_TREE + north_band):
        for x in range(5, 76):
            if grid[y][x] != "ᶠ":
                continue
            start = _north_edge(x)
            if not start <= y < start + north_band:
                continue
            reach = min(1.0, abs(x - NORTH_BAY) / NORTH_BAY_WIDTH)
            crowding = (0.42 + 0.44
                        * (start + north_band - 1 - y) / (north_band - 1)) * (
                0.74 + 0.26 * reach
            )
            if rng.random() < crowding:
                grid[y][x] = "♣"

    band = FOREST_SOLID - FOREST_EDGE
    for y in range(FOREST_EDGE, FOREST_SOLID + FIRE_BAY_DEPTH):
        for x in range(5, 76):
            if grid[y][x] != "ᶠ":
                continue
            # The thickening is the same few rows deep everywhere; it is
            # the tree line it hangs from that moves. Stretching the ramp
            # to fill the bay instead just planted the opening, which is
            # the opposite of what a clearing round a fire looks like.
            start = _south_edge(x) - band
            if y < start:
                continue
            reach = min(1.0, abs(x - FIRE[0]) / FIRE_BAY_WIDTH)
            crowding = (0.42 + 0.44 * (y - start) / (band - 1)) * (
                0.74 + 0.26 * reach
            )
            if rng.random() < crowding:
                grid[y][x] = "♣"

    # The driveway: a road's width of dirt out of the top of the north
    # opening and away through the trees. Cut after the planting so no
    # fir can grow in the middle of it.
    # It stops two rows short of the top edge, so the track goes out of
    # sight behind the trees rather than running to the border and
    # ending against nothing.
    for y in range(2, _north_edge(NORTH_BAY) + 4):
        for x in range(NORTH_BAY - DRIVEWAY_HALF - 1,
                       NORTH_BAY + DRIVEWAY_HALF + 2):
            if abs(x - NORTH_BAY) <= DRIVEWAY_HALF:
                grid[y][x] = "⌇"
            elif grid[y][x] == "♣":
                # A fir is three tiles of canopy wide. One standing
                # right against the track hangs over the whole of it,
                # so the columns either side are kept clear of trunks.
                grid[y][x] = "ᶠ"

    # A handful of the established scratchable cigarette-grass tufts soften
    # the clearing and reward inspecting the tighter west approach.
    for x, y in ((12, 29), (18, 34), (26, 28), (33, 34),
                 (40, 28), (47, 18), (47, 43), (52, 45)):
        if grid[y][x] in {"ᶠ", "♣"}:
            grid[y][x] = "ʛ"

    # Evergreen huckleberry and salal fill in under the stand. A
    # Douglas-fir wood in this part of Washington does not have a bare
    # floor under it, and the trees on their own read as posts standing
    # in a lawn. Both are scenery Chuck walks through, so they can be
    # thick without fencing anything off.
    #
    # Placement follows the trees rather than covering the map: a tile
    # gets brush only if there is a fir within a couple of tiles of it,
    # which keeps the clearing, the trail and the fire circle open
    # without any of those having to be named here.
    # Read the trees back off the grid rather than off the list the west
    # stand was built from: the thickened tree lines north and south are
    # planted straight into the grid, and taking the list left both of
    # them standing on bare ground while the west side had an
    # understory.
    firs_by_row = {}
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if grid[y][x] == "♣":
                firs_by_row.setdefault(y, []).append(x)
    for y in range(4, HEIGHT):
        for x in range(1, WIDTH - 1):
            if grid[y][x] != "ᶠ":
                continue
            near = any(
                abs(x - fx) <= 2
                for row in range(y - 2, y + 3)
                for fx in firs_by_row.get(row, ())
            )
            if not near or rng.random() > 0.34:
                continue
            grid[y][x] = "ᶲ" if rng.random() < 0.45 else "ᶳ"

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
