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


# --------------------------------------------------------------------------
# Whole-map passes, run after a map's streets and masses are laid down.
# --------------------------------------------------------------------------

_MASS = ("#", "▥", "▘", "▖", "▗", "▙", "▟", "▱", "▤", "w")


def terrace_mass(grid: list[list[str]], *, fill=("#", "▥")) -> None:
    """Turn every block of undifferentiated building mass into buildings.

    The day maps were laid out by filling everything that is not street
    with one solid char and cutting a three-row front into it where a
    building was wanted. That leaves most of the map as a single flat
    colour. This walks whatever mass is left and gives it the same
    treatment the night blocks get: parapets, a stepped roofline,
    fronts with windows, and side walls turning away from the camera.

    It works a column at a time rather than on rectangles, so it can
    dress an L-shaped or ragged mass without being told its shape. Only
    solid chars are ever written, so nothing about where Chuck can walk
    changes.
    """
    height = len(grid)
    width = len(grid[0])

    # Every vertical run of mass, per column: these are the wall faces.
    runs: list[tuple[int, int, int]] = []
    for col in range(width):
        row = 0
        while row < height:
            if grid[row][col] in fill:
                start = row
                while row < height and grid[row][col] in fill:
                    row += 1
                runs.append((col, start, row - 1))
            else:
                row += 1

    # Group adjacent columns whose runs line up into one building, and cut
    # every so many columns so a long mass becomes a terrace rather than
    # one impossibly wide office.
    by_column: dict[int, list[tuple[int, int]]] = {}
    for col, top, bottom in runs:
        by_column.setdefault(col, []).append((top, bottom))

    used: set[tuple[int, int, int]] = set()
    buildings: list[list[tuple[int, int, int]]] = []
    for col, top, bottom in runs:
        if (col, top, bottom) in used:
            continue
        group = [(col, top, bottom)]
        used.add((col, top, bottom))
        seed = col * 31 + top * 17
        limit = _WIDTHS[seed % len(_WIDTHS)]
        cursor, last = col + 1, (top, bottom)
        while cursor < width and len(group) < limit:
            match = None
            for candidate in by_column.get(cursor, ()):
                if (cursor, *candidate) in used:
                    continue
                # The runs have to overlap for most of their length, or
                # this is a different building that happens to be next door.
                overlap = (min(last[1], candidate[1])
                           - max(last[0], candidate[0]) + 1)
                shorter = min(last[1] - last[0], candidate[1] - candidate[0]) + 1
                if overlap >= shorter * 0.7:
                    match = candidate
                    break
            if match is None:
                break
            group.append((cursor, *match))
            used.add((cursor, *match))
            last = match
            cursor += 1
        buildings.append(group)

    for index, group in enumerate(buildings):
        first, last = group[0][0], group[-1][0]
        seed = first * 31 + group[0][1] * 17 + index
        front = _FRONTS[seed % len(_FRONTS)]
        for col, top, bottom in group:
            # Always leave two rows of roof above the cornice: a building
            # whose front eats its own roof stops reading from above.
            depth = min(front, bottom - top - 2)
            if depth < 1:
                # Too shallow to be a building: leave it as a plain wall.
                for row in range(top, bottom + 1):
                    grid[row][col] = "▤"
                continue
            facade_top = bottom - depth
            for row in range(top, bottom + 1):
                if row < facade_top:
                    if row == top:
                        char = "▘"
                    elif col == first:
                        char = "▖"
                    elif col == last:
                        char = "▗"
                    else:
                        char = "#"
                elif row == facade_top:
                    char = "▱"
                elif col in (first, last):
                    char = "▥"
                elif row == bottom:
                    char = "▤"
                else:
                    char = "w" if (col - first + row) % 3 else "▤"
                grid[row][col] = char
            if facade_top - top >= 4 and first < col < last:
                slot = (col * 7 + seed) % 5
                spot = top + 2 + (col + seed) % max(1, facade_top - top - 3)
                if slot == 0:
                    grid[spot][col] = "▙"
                elif slot == 2:
                    grid[spot][col] = "▟"


def mark_roads(grid: list[list[str]], *, road: str = "=") -> None:
    """Paint a centre line down every carriageway.

    A road's direction is not recorded anywhere, so it is measured: the
    run of road through a tile is longer along the way the traffic goes.
    The line is laid on the middle row (or column) of that run, and
    junctions -- where the road is long in both directions -- are left
    unpainted, because a line through an intersection is wrong and reads
    as one.
    """
    height = len(grid)
    width = len(grid[0])

    # A crosswalk is still carriageway. Measuring the road without it
    # shortens the run wherever a crossing is painted, which moves the
    # computed centre and leaves dashes scattered at three heights.
    carriageway = {road, "▦"}

    def span(col: int, row: int, dc: int, dr: int) -> tuple[int, int]:
        low = high = 0
        while True:
            c, r = col + dc * (low - 1), row + dr * (low - 1)
            if not (0 <= c < width and 0 <= r < height):
                break
            if grid[r][c] not in carriageway:
                break
            low -= 1
        while True:
            c, r = col + dc * (high + 1), row + dr * (high + 1)
            if not (0 <= c < width and 0 <= r < height):
                break
            if grid[r][c] not in carriageway:
                break
            high += 1
        return low, high

    marks: list[tuple[int, int, str]] = []
    for row in range(height):
        for col in range(width):
            if grid[row][col] != road:
                continue
            left, right = span(col, row, 1, 0)
            top, bottom = span(col, row, 0, 1)
            across = right - left + 1
            down = bottom - top + 1
            if across >= down * 3 and across >= 8:
                if row == (row + top + row + bottom) // 2:
                    marks.append((col, row, "≡"))
            elif down >= across * 3 and down >= 8:
                if col == (col + left + col + right) // 2:
                    marks.append((col, row, "‖"))

    for col, row, char in marks:
        grid[row][col] = char
