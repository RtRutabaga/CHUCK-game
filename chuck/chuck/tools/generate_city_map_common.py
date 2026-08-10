"""Shared authored-map helpers for Phase 11 city blocks.

A city block used to be painted as one mass: a single unbroken field of
roof with a strip of windows along its bottom edge. At map scale that
read as a slab of plain stone taking up half the screen, because a roof
with no edge and no plant on it is just a colour.

What is painted now is a *terrace* -- several buildings of different
heights sharing one footprint. Each has its own parapet, its own
roofline, its own front, and its own side wall turning away from the
camera, and the steps between them are what make the block read as
three-quarter view rather than flat.

None of this changes where Chuck can walk. The footprint is solid
before and after, tile for tile, so every route, reachability check and
office-mass test on top of these blocks still measures the same thing.
"""

# How many rows of wall each building shows below its roofline. Kept
# shallow on purpose: a front deep enough to fill the screen stops
# reading as a building seen from above and starts reading as a
# side-scroller. Cycled across the buildings in a block.
_FRONTS = (6, 9, 4, 7, 5, 8)
# Building widths, cycled likewise. Nothing narrower than eight tiles:
# below that a front with windows in it stops reading as a building.
_WIDTHS = (17, 12, 21, 14, 9, 19)


def _plant(grid, left, top, right, bottom, seed: int) -> None:
    """Scatter vents and skylights over one roof, deterministically.

    Roof furniture is the difference between a roof and a rectangle. It
    is placed on a coarse lattice rather than at random so it never
    clumps into a line or leaves half a roof bare.
    """
    for row in range(top + 1, bottom, 3):
        for col in range(left + 1, right, 4):
            slot = (col * 7 + row * 13 + seed) % 5
            if slot in (0, 4):
                grid[row][col] = "▙"
            elif slot == 2:
                grid[row][col] = "▟"


def paint_building(
    grid: list[list[str]], left: int, top: int, right: int, bottom: int,
    *, front: int = 8, seed: int = 0, parapet_top: bool = True,
) -> None:
    """Paint one three-quarter-view building: roof, front, and side.

    `front` is how many rows of wall are visible below the roofline --
    in effect how tall the building is, since a taller one shows more of
    itself. The side walls are the faces turning away from the camera.
    """
    facade_top = bottom - front
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            if row < facade_top:
                if row == top and parapet_top:
                    char = "▘"          # the parapet wall along the back
                elif col == left:
                    char = "▖"          # ...and down both roof edges, each
                elif col == right:
                    char = "▗"          # lit on its own outward face
                else:
                    char = "#"
            elif row == facade_top:
                char = "▱"              # the cornice the front hangs from
            elif col in (left, right):
                char = "▥"              # the wall turning away
            elif row == bottom:
                char = "▤"
            else:
                char = "w" if (col - left + row) % 3 else "▤"
            grid[row][col] = char
    if facade_top - top >= 4:
        _plant(grid, left + 1, top + 1, right - 1, facade_top - 1, seed)


def paint_office(
    grid: list[list[str]], left: int, top: int, right: int, bottom: int,
) -> None:
    """Paint one city block as a terrace of buildings sharing a footprint.

    The block is divided into buildings across its width, each given a
    different front depth so the roofline steps between them. A block
    too narrow to divide is simply one building, which is why small
    infill masses still work through the same call.
    """
    width = right - left + 1
    seed = left * 31 + top * 17

    bounds = []
    cursor = left
    index = 0
    while cursor <= right:
        span = _WIDTHS[(index + seed) % len(_WIDTHS)]
        end = min(cursor + span - 1, right)
        # Never leave a sliver at the end: fold it into the last building.
        if right - end < 8:
            end = right
        bounds.append((cursor, end))
        cursor = end + 1
        index += 1

    if width < 16:
        bounds = [(left, right)]

    for index, (start, end) in enumerate(bounds):
        front = _FRONTS[(index + seed) % len(_FRONTS)]
        # Every front has to fit inside the footprint with roof left over.
        front = min(front, bottom - top - 3)
        paint_building(grid, start, top, end, bottom,
                       front=front, seed=seed + index * 5)
