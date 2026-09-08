"""Shared shaping for the Phase 13 collided maps.

Two things every map east of the hub needs and none of them should each
invent: the seam between a fragment and the desert it landed in, and
the dressing that stands on the fragment once it has arrived.

Left as a plain boundary, a piece of another world reads as having been
*placed* -- laid down on the sand like a decal, with the two grounds
meeting cleanly. That is the wrong impression entirely. These worlds
did not arrive, they collided, and the game already has a language for
where reality has come apart: the Astral Sea. So the seams get frayed
with it. Not a ring round each fragment, which would read as an outline
somebody drew, but a scatter along it -- some of the boundary torn open
and the rest simply touching.

The scatter is deterministic, so the maps are reproducible, and it
never eats a tile the map depends on: doorways, arrivals, anchors and
anything the caller names are left alone.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

# Ground the fringe is allowed to eat. Anything else -- a marker, a
# prop, a door -- is load-bearing and left where it is.
_EDIBLE = {".", ",", "⟁", "⍟"}


def _tearing(x: int, y: int, seed: float) -> float:
    """How badly the world has come apart around here.

    Low-frequency, so it varies over whole stretches of a boundary
    rather than tile by tile. That is the whole trick: the first
    version of this took roughly one seam tile in three, evenly, and a
    seam sampled evenly is a dashed line. A fragment came out neatly
    outlined in Astral Sea, which reads as somebody having drawn round
    it -- the opposite of the impression the fringe exists to give.
    """
    return (math.sin(x * 0.21 + y * 0.13 + seed)
            + math.sin(x * 0.09 - y * 0.24 + seed * 1.7)
            + 0.5 * math.sin((x + y) * 0.4 + seed * 0.6))


def astral_fringe(
    grid: list[list[str]],
    fragment_chars: set[str],
    *,
    threshold: float = 0.75,
    reach: int = 1,
    seed: float = 0.0,
    protect: set[tuple[int, int]] | None = None,
) -> int:
    """Tear open part of the seam between a fragment and the desert.

    `fragment_chars` is everything belonging to the intruding world.
    Desert ground within `reach` tiles of any of it is torn open where
    the tearing function runs high -- so some stretches of the boundary
    are ripped through and others simply touch, which is what a seam
    looks like and what an outline does not.

    Returns how many tiles were torn, which is what the callers assert
    on: a fringe that silently does nothing looks exactly like a fringe
    that was never called.
    """
    height = len(grid)
    width = len(grid[0])
    protect = protect or set()

    seam: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            if grid[y][x] not in _EDIBLE or (x, y) in protect:
                continue
            near = any(
                0 <= y + dy < height and 0 <= x + dx < width
                and grid[y + dy][x + dx] in fragment_chars
                for dy in range(-reach, reach + 1)
                for dx in range(-reach, reach + 1)
                if (dx, dy) != (0, 0)
            )
            if near:
                seam.append((x, y))

    torn = 0
    for x, y in seam:
        # Smooth and deterministic, so the same map is the same map
        # every time it is generated and the tears come in stretches.
        if _tearing(x, y, seed) < threshold:
            continue
        grid[y][x] = "V"
        torn += 1
    return torn


def protected_cells(*cells: tuple[int, int]) -> set[tuple[int, int]]:
    """Convenience for callers naming a handful of tiles to leave alone."""
    return set(cells)


# ------------------------------------------------------------------
# Dressing


# What stands on each world's ground, and whether that ground was
# already solid before anything stood on it.
#
# Every prop here belongs to the world it dresses -- Chult's own trees,
# the Feywild's own mushrooms, Phlegethos's own basalt debris. That is
# the point rather than a convenience: a fragment is recognised by what
# grows on it, and a desert-styled lookalike would cost the fragment
# the only thing it is for.
#
# The second field decides where a prop may stand. On ground that is
# already a wall, anywhere -- a tree on dense jungle changes no route
# and breaks up a blocky mass that badly needs it. On ground a player
# can walk, only well inside it, because every one of these props is
# solid and the basalt slab on the fourth map is the only crossing
# there is.
FRAGMENT_DRESSING: dict[str, tuple[tuple[str, ...], bool, float, int]] = {
    # ground: (props, the ground is already solid, extra density, spacing)
    #
    # Growth on ground that is already a wall gets the extra density,
    # because it is free: a tree standing on dense jungle changes no
    # route at all, and a thicket that reads as a thicket needs to be
    # thick. Props on ground a player walks are kept thinner, and are
    # spaced further apart, because each one of them is an obstacle.
    "ᚷ": (("⍮",), True, 0.35, 2),      # Chult's dense jungle: trees
    "ᛗ": (("⍯",), False, 0.0, 3),      # ...and bushes on its open ground
    "ᛇ": (("⍰",), True, 0.35, 2),      # the Feywild's dense growth: trees
    "ᛟ": (("⍱", "⍲"), False, 0.0, 3),  # ...shrubs and mushrooms on its floor
    "·": (("þ",), False, 0.1, 3),      # Phlegethos's own basalt rubble
    "⌼": (("⍶", "⍷"), False, 0.0, 4),  # the ship's barrels and crates
}


# Ground a player can stand on, across every world the traversal
# passes through. Written positively rather than as "not solid":
# a negative list has to be kept in step with every tile the region
# ever gains, and the failure when it drifts is silent -- a prop
# planted in a doorway, on a map nobody re-walked.
_STANDABLE = {
    ".", ",", "⟁", "⌖",             # the desert and its buried floors
    "=", "≡",                        # the modern city's road
    "ᛗ",                             # Chult's jungle floor
    "ᛟ", "☼",                        # the Feywild's floor and its pollen
    "·",                             # Phlegethos's basalt
    "⌽", "⌼",                        # the courtyard, and the ship's deck
    "❄", "❆",                        # snow, and ice
}


# Every dressing character, and the ground it belongs to. Exported so
# that the maps' own vocabulary tests can attribute a prop to a world
# the same way they attribute a tile: a piece of Chult is a piece of
# Chult whether it is the jungle floor or a tree standing on it.
PROP_GROUND: dict[str, str] = {
    prop: ground
    for ground, (props, _, _, _) in FRAGMENT_DRESSING.items()
    for prop in props
}
# ...and the one that is placed by hand rather than scattered, because
# there is a single lava fall in the region and it belongs where the
# cliff is rather than wherever the noise says.
PROP_GROUND["ƒ"] = "≋"

# Below this many tiles a fragment is a scrap rather than a mass,
# and is dressed at whatever density it can afford instead of at
# the one its map's main fragment wants.
SCRAP_TILES = 60
SCRAP_THRESHOLD = -0.6


def _well_inside(grid, x: int, y: int) -> bool:
    """Is there a way past this tile on all four sides of it?

    The test that keeps a solid prop from ever closing a route, and the
    reason it can be applied blindly across six maps. A tile with
    standable ground north, south, east and west of it is by definition
    not a chokepoint: whatever else the map does, a prop standing there
    can be walked around.

    It was written as "the whole three-by-three is the same ground" at
    first, which is safe and much too strict -- the small scraps are
    three or four tiles across and never have a uniform middle, so the
    maps whose fragments are only scraps came back with nothing on them
    at all. What matters is the four ways past, not the sameness.
    """
    height, width = len(grid), len(grid[0])
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if not (0 <= ny < height and 0 <= nx < width):
            return False
        if grid[ny][nx] not in _STANDABLE:
            return False
    return True


def dress_fragments(
    grid: list[list[str]],
    *,
    seed: float = 0.0,
    threshold: float = 0.45,
    protect: set[tuple[int, int]] | None = None,
) -> int:
    """Stand each world's own growth and debris on its own ground.

    Clumped rather than sprinkled, using the same low-frequency
    function the seam frayer uses and for the same reason: an evenly
    sampled scatter reads as wallpaper. Trees come in stands and
    rubble comes in falls, so what decides placement has to vary over
    whole stretches of a fragment rather than tile by tile.

    How dense and how spread out is per ground rather than per map,
    because the answer depends on what the ground already is: growth on
    a wall is decoration and growth on a floor is an obstacle.

    Returns how many pieces were placed, which is what the callers
    assert on -- a dressing pass that silently does nothing looks
    exactly like one that was never called.
    """
    height, width = len(grid), len(grid[0])
    protect = protect or set()

    # How much of each world is actually here. A map's main fragment is
    # hundreds of tiles and wants thinning; the scraps of the worlds it
    # met further back are a dozen or two, and at the density the big
    # one wants, a scrap that size draws nothing at all -- which is how
    # three of these maps ended up with an undressed piece of Chult on
    # them. So a scrap is dressed at whatever density it can afford.
    present: dict[str, int] = {}
    for row in grid:
        for char in row:
            if char in FRAGMENT_DRESSING:
                present[char] = present.get(char, 0) + 1

    placed: list[tuple[int, int, int]] = []
    for y in range(height):
        for x in range(width):
            char = grid[y][x]
            entry = FRAGMENT_DRESSING.get(char)
            if entry is None or (x, y) in protect:
                continue
            props, ground_is_solid, bias, apart = entry
            bar = SCRAP_THRESHOLD if present[char] < SCRAP_TILES else threshold
            # Clumping decides *where* stands of growth are; this decides
            # which tiles inside a stand actually get one. Without it,
            # everywhere the clumping runs high the spacing rule is the
            # only thing left deciding, and minimum-spacing packing is a
            # lattice -- a bank of bushes came back as a pegboard.
            grain = 0.4 * math.sin(x * 1.7 + y * 2.3 + seed * 3.1)
            if _tearing(x, y, seed) + grain < bar - bias:
                continue
            if not ground_is_solid and not _well_inside(grid, x, y):
                continue
            if any(abs(px - x) + abs(py - y) < max(apart, gap)
                   for px, py, gap in placed):
                continue
            # Which of the world's props, hashed rather than taken
            # from a linear form: any of those, taken modulo two,
            # is the parity of x + y -- so a ground with two props
            # on it lays them out as a checkerboard, and a spacing
            # rule on top of that picks all of one and none of the
            # other.
            pick = int(abs(math.sin(x * 12.9898 + y * 78.233))
                       * 43758.5) % len(props)
            grid[y][x] = props[pick]
            placed.append((x, y, apart))
    return len(placed)


# ---------------------------------------------------------------------
# The castle, finished
# ---------------------------------------------------------------------
# The medieval fragment shipped as flat coursed ashlar: correct stone,
# and unmistakably a boundary rather than a building. A wall is a castle
# wall the moment it is notched and has a tower on the corner, and it
# belongs to somebody the moment there is a banner on it -- and out here
# that matters more than usual, because this is the one world in the
# collision Chuck has never visited and the walls are all anybody will
# ever learn about it.
#
# Everything below either swaps stone for different stone or adds
# stone and then proves, by flooding the map, that it cut nothing off.
# That is what lets it run over the trio's arena and the two island
# maps whose geometry other tests measure to the tile.

COURTYARD_STONE = "⌽"
COURTYARD_WALL = "⌾"
COURTYARD_MERLON = "ᛦ"
COURTYARD_TOWER = "ᛧ"
# A corner turret: three tiles of stone with a roof on it, tall enough
# that the curtain runs into its base. The prop stands on the middle of
# the block's bottom row and draws upward over the whole of it.
CASTLE_TURRET = "ᛪ"
# A banner, hanging on wall rather than in front of it. It used to hang
# on the ground tile below the curtain, where two thirds of the cloth
# came down past the bottom of the wall and lay on the courtyard floor
# like a rug. It goes on stone now, and the wall is widened under every
# one of them so there is stone for it to hang on.
BANNER_ON_WALL = "ᛮ"

CASTLE_WALLS = (
    COURTYARD_WALL, COURTYARD_MERLON, COURTYARD_TOWER,
    CASTLE_TURRET, BANNER_ON_WALL,
)
# Ground the castle is allowed to build out over: its own swept floor
# inside and open sand outside, and nothing else. Everything on these
# maps that matters -- knights, arrivals, Ashtrays, lava, the Astral --
# is some other character, so this one test keeps all of them safe.
BUILDABLE = (".", COURTYARD_STONE)
# How far apart the banners hang. Close together they stop being an
# announcement and become bunting.
BANNER_SPACING = 7
# Turrets are three tiles across, so their middles have to be four
# apart or the blocks grow into each other.
TURRET_SPACING = 4


def _wall_neighbours(grid, col: int, row: int) -> set[tuple[int, int]]:
    height, width = len(grid), len(grid[0])
    return {
        (dcol, drow)
        for dcol, drow in ((1, 0), (-1, 0), (0, 1), (0, -1))
        if 0 <= col + dcol < width and 0 <= row + drow < height
        and grid[row + drow][col + dcol] in CASTLE_WALLS
    }


def _is_mass(grid, col: int, row: int) -> bool:
    """Is this wall tile part of a solid two-by-two block of wall?

    A curtain wall is one tile thick and wants crenellation; anything
    thicker is a tower or a keep and wants to be drawn as one. Told
    apart here rather than authored per map, because the maps that have
    this stone scatter it differently on every one of them.
    """
    for top in (row - 1, row):
        for left in (col - 1, col):
            block = [(left, top), (left + 1, top),
                     (left, top + 1), (left + 1, top + 1)]
            if all(
                0 <= c < len(grid[0]) and 0 <= r < len(grid)
                and grid[r][c] in CASTLE_WALLS
                for c, r in block
            ):
                return True
    return False


def _open_cells(grid) -> set[tuple[int, int]]:
    """Every tile nothing solid is standing on.

    Solidity is read off the game's own table rather than guessed at,
    so a pass that runs over eight maps of nine worlds' worth of ground
    cannot be wrong about what a route is.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.world.tilemap import MARKER_DEFS, TILE_DEFS

    open_cells = set()
    for row, line in enumerate(grid):
        for col, char in enumerate(line):
            marker = MARKER_DEFS.get(char)
            tile = TILE_DEFS[marker.under if marker else char]
            if not tile.solid:
                open_cells.add((col, row))
    return open_cells


def _flood(open_cells: set, start) -> set:
    from collections import deque

    seen = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for spot in ((col + 1, row), (col - 1, row),
                     (col, row + 1), (col, row - 1)):
            if spot in open_cells and spot not in seen:
                seen.add(spot)
                frontier.append(spot)
    return seen


def _walkable_map(grid) -> set:
    """The biggest connected piece of open ground: the playable map.

    Flooding from whichever open tile happens to come first sounded
    fine and was not. These maps are nine worlds in pieces, and several
    of them have a sealed pocket somewhere -- the first open tile on
    east 7 is in one. Every block then measured itself against a flood
    that never reached it and was refused, and the map came back with
    no turrets and no banners at all.
    """
    open_cells = _open_cells(grid)
    best: set = set()
    unseen = set(open_cells)
    while unseen:
        region = _flood(open_cells, next(iter(unseen)))
        unseen -= region
        if len(region) > len(best):
            best = region
    return best


def dress_castle(grid: list[list[str]], *, seed: int = 0) -> dict[str, int]:
    """Crenellate the curtain, turret the corners, hang the banners.

    Everything here is built out of, or onto, stone that was already
    standing, and every block that adds stone is flooded before it is
    kept: a turret or a buttress that shuts a gate or strands a knight
    is taken back off rather than shipped. That is what lets a
    furnishing pass run over maps whose geometry other suites measure to
    the tile.
    """
    height, width = len(grid), len(grid[0])
    walls = [
        (col, row)
        for row in range(height) for col in range(width)
        if grid[row][col] == COURTYARD_WALL
    ]
    if not walls:
        return {COURTYARD_MERLON: 0, COURTYARD_TOWER: 0,
                CASTLE_TURRET: 0, "banner": 0}

    towers, merlons, corners = [], [], []
    for col, row in walls:
        sides = _wall_neighbours(grid, col, row)
        # A stump -- one tile of wall left standing, or the end of a
        # run -- is a tower. Out here that is most of what a broken
        # castle is, and a single drum reads as one where a single
        # crenellated tile reads as a mistake.
        if len(sides) <= 1:
            towers.append((col, row))
        elif _is_mass(grid, col, row):
            # Anything two tiles thick is a section of building rather
            # than a curtain: crenellate the ring of it that shows and
            # leave the inside as plain stone. Making the whole mass a
            # tower instead gave the island maps forty drum towers in a
            # heap, each with its own arrow slit -- which reads as a
            # wall covered in holes rather than as one building.
            if len(sides) < 4:
                merlons.append((col, row))
        else:
            # A run that turns is a corner, and a corner is where a
            # castle puts its tower. These are the ones that get a real
            # turret built on them further down; a stump only gets the
            # drum tile.
            turns = (
                {(1, 0), (0, 1)} <= sides or {(1, 0), (0, -1)} <= sides
                or {(-1, 0), (0, 1)} <= sides or {(-1, 0), (0, -1)} <= sides
            )
            if turns:
                towers.append((col, row))
                corners.append((col, row))
            else:
                merlons.append((col, row))

    for col, row in towers:
        grid[row][col] = COURTYARD_TOWER
    for col, row in merlons:
        grid[row][col] = COURTYARD_MERLON

    # Nothing below this point is a like-for-like swap, so from here on
    # the walkable map is watched.
    reach_before = _walkable_map(grid)
    start = min(reach_before, key=lambda spot: spot[::-1])

    def _buildable(col: int, row: int) -> bool:
        return grid[row][col] in BUILDABLE or grid[row][col] in CASTLE_WALLS

    def _try(cells: dict[tuple[int, int], str]) -> bool:
        """Write a block, keep it only if the map still holds together."""
        if any(not _buildable(col, row) for col, row in cells):
            return False
        was = {spot: grid[spot[1]][spot[0]] for spot in cells}
        for (col, row), char in cells.items():
            grid[row][col] = char
        after = _open_cells(grid)
        if start in after and _flood(after, start) == reach_before & after:
            return True
        for (col, row), char in was.items():
            grid[row][col] = char
        return False

    # ------------------------------------------------------------------
    # The turrets. A corner is the one part of a castle that is taller
    # than the rest -- that is what a corner tower is for -- and at one
    # tile each these read as a slightly different piece of wall.
    # ------------------------------------------------------------------
    turrets: list[tuple[int, int]] = []
    for col, row in sorted(corners, key=lambda spot: spot[::-1]):
        if not (1 <= col < width - 1 and 1 <= row < height - 2):
            continue
        if any(max(abs(col - c), abs(row - r)) < TURRET_SPACING
               for c, r in turrets):
            continue
        # Three by three where there is room for three by three. Where
        # there is not -- the south-west corner of east 5 stands on the
        # lip of a chasm -- the block is clipped to what it can stand
        # on and the sprite overhangs the drop, which is what a tower
        # built on a cliff edge does anyway. Refusing those outright
        # left one corner of a four-cornered courtyard bare.
        block = {
            (col + dcol, row + drow): COURTYARD_TOWER
            for dcol in (-1, 0, 1) for drow in (-1, 0, 1)
            if _buildable(col + dcol, row + drow)
        }
        # The prop stands on the middle of the bottom row and draws
        # upward across the whole block and a tile and a half beyond it,
        # which is the height. Without that tile there is no turret.
        if (col, row + 1) not in block or (col, row) not in block:
            continue
        block[(col, row + 1)] = CASTLE_TURRET
        if _try(block):
            turrets.append((col, row))

    # ------------------------------------------------------------------
    # The banners, and the wall widened to carry them.
    #
    # Cloth is two tiles of sprite drawn upward from the bottom of the
    # tile it stands on. Hung on the ground in front of a one-tile
    # curtain, two thirds of it came down past the bottom of the wall
    # and lay on the floor -- a banner the same height as the building
    # it is on. So the wall grows a buttress three tiles wide and one
    # deep on the face that shows, and the banner hangs on that: the
    # cloth now covers the buttress and the curtain behind it and stops
    # at the wall's own base.
    # ------------------------------------------------------------------
    hung: list[tuple[int, int]] = []
    faces = [
        (col, row + 1)
        for col, row in sorted(merlons + towers, key=lambda spot: spot[::-1])
        if row + 1 < height and grid[row + 1][col] in BUILDABLE
    ]
    for col, row in faces:
        if any(max(abs(col - c), abs(row - r)) < BANNER_SPACING
               for c, r in hung):
            continue
        if (col * 7 + row * 13 + seed) % 3 == 2:
            continue        # not on every eligible face, or it is bunting
        if not 1 <= col < width - 1:
            continue
        buttress = {
            (col - 1, row): COURTYARD_WALL,
            (col, row): BANNER_ON_WALL,
            (col + 1, row): COURTYARD_WALL,
        }
        if _try(buttress):
            hung.append((col, row))

    return {
        COURTYARD_MERLON: len(merlons),
        COURTYARD_TOWER: len(towers),
        CASTLE_TURRET: len(turrets),
        "banner": len(hung),
    }
