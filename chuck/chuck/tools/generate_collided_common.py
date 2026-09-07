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
