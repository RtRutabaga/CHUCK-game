"""Shared shaping for the Phase 13 collided maps.

One thing every map east of the hub needs and none of them should each
invent: the seam between a fragment and the desert it landed in.

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
