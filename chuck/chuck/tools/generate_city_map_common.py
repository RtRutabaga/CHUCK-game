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

import sys
from pathlib import Path

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


# --------------------------------------------------------------------------
# Street furniture
# --------------------------------------------------------------------------
# The blocks were built and then never furnished. Every city map is a road, a
# kerb, a pavement and a wall of building, and between those four things there
# was nothing standing on the ground at all -- which is why a street here read
# as a diagram of a street rather than as one.
#
# What goes down is the boring stuff: a lamp post every so many paces along
# the kerb, a hydrant on a corner, a stop sign where a road ends. All three
# are solid, so all three are placed under one rule that makes them safe by
# construction rather than by inspection.
#
# The rule: nothing stands anywhere the pavement is less than three tiles
# deep, and it always stands on the tile against the kerb. Real pavements are
# furnished at their outer edge for exactly this reason -- whatever is behind
# the lamp post is the bit you walk down. `dress_street` then floods the map
# before and after and refuses to return one where the two differ by anything
# other than the tiles it just filled, so a placement can never quietly close
# a route.

STREETLIGHT = "Ⱡ"
FIRE_HYDRANT = "Ⱨ"
STOP_SIGN = "ⱦ"

PAVEMENT = "."
KERB = ","

# How far apart the lamps stand. Nine tiles is a hundred and forty-four
# pixels, which is most of a screen width: close enough that a night street
# always has one in view and far enough that a row of them never reads as
# fencing.
LIGHT_SPACING = 16
# ...and how much else there is. "A small amount", per the ask: these are
# punctuation, and a hydrant every corner is a hydrant nobody looks at.
HYDRANTS_PER_MAP = 3
SIGNS_PER_MAP = 2
# How much clear pavement a solid thing must leave behind it. One tile,
# because that is what the narrow blocks have: City Day 5 is a canyon
# with two tiles of pavement each side, and a rule that wanted three
# left it with no lamps at all. One tile is a lane -- the flood at the
# end of this pass is what proves it, rather than the number.
LANE_DEPTH = 1


def _open_chars(grid: list[list[str]]) -> set[str]:
    """Every char in this grid that Chuck could stand on.

    Derived from the runtime's own tile table rather than listed here, so
    a new marker or a new road surface cannot quietly become a wall to
    this pass while staying walkable to the game.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src.world.tilemap import MARKER_DEFS, TILE_DEFS

    chars = {char for row in grid for char in row}
    open_set = set()
    for char in chars:
        marker = MARKER_DEFS.get(char)
        if marker is not None:
            if not TILE_DEFS[marker.under].solid:
                open_set.add(char)
            continue
        tile = TILE_DEFS.get(char)
        if tile is not None and not tile.solid:
            open_set.add(char)
    return open_set


def _reachable(grid, open_set: set[str]) -> set[tuple[int, int]]:
    height, width = len(grid), len(grid[0])
    start = next(
        ((col, row) for row in range(height) for col in range(width)
         if grid[row][col] in open_set), None
    )
    if start is None:
        return set()
    seen = {start}
    frontier = [start]
    while frontier:
        col, row = frontier.pop()
        for dcol, drow in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (col + dcol, row + drow)
            if cell in seen:
                continue
            if not (0 <= cell[0] < width and 0 <= cell[1] < height):
                continue
            if grid[cell[1]][cell[0]] not in open_set:
                continue
            seen.add(cell)
            frontier.append(cell)
    return seen


def _kerbside(grid) -> list[tuple[int, int, int, int]]:
    """Pavement tiles against a kerb, with the direction away from it.

    Returns (col, row, inward_dcol, inward_drow) for every tile that has
    a kerb on one side and at least `LANE_DEPTH` tiles of plain pavement
    behind it -- which is the whole of the safety argument, since the
    lane behind is what stays walkable once the thing is standing there.
    """
    height, width = len(grid), len(grid[0])
    found = []
    for row in range(height):
        for col in range(width):
            if grid[row][col] != PAVEMENT:
                continue
            for dcol, drow in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                near = (col - dcol, row - drow)
                if not (0 <= near[0] < width and 0 <= near[1] < height):
                    continue
                if grid[near[1]][near[0]] != KERB:
                    continue
                lane = True
                for step in range(1, LANE_DEPTH + 1):
                    cell = (col + dcol * step, row + drow * step)
                    if not (0 <= cell[0] < width and 0 <= cell[1] < height):
                        lane = False
                        break
                    if grid[cell[1]][cell[0]] != PAVEMENT:
                        lane = False
                        break
                if lane:
                    found.append((col, row, dcol, drow))
                break
    return found


def _clear_of_everything(grid, col: int, row: int) -> bool:
    """Is this tile and its ring plain pavement?

    Authored things -- a crossing, an arrival, a person, a bottle -- get
    a tile of air around them. A lamp post growing out of a zebra
    crossing is not wrong so much as obviously unconsidered.
    """
    height, width = len(grid), len(grid[0])
    for drow in (-1, 0, 1):
        for dcol in (-1, 0, 1):
            cell = (col + dcol, row + drow)
            if not (0 <= cell[0] < width and 0 <= cell[1] < height):
                return False
            if grid[cell[1]][cell[0]] not in (PAVEMENT, KERB):
                return False
    return True


def _is_corner(grid, col: int, row: int) -> bool:
    """Does the kerb turn within a few tiles of here?

    Stop signs go where a road ends, and the only thing in these grids
    that says "junction" is the kerb changing direction. Measured rather
    than authored per map, because the roads themselves are.
    """
    height, width = len(grid), len(grid[0])
    horizontal = vertical = False
    # Five tiles rather than three. A junction's own corner is usually
    # busy -- a crossing, an arrival, somebody standing on it -- so the
    # tile a sign can actually take is a few paces back from the turn,
    # and at three the test could not see the turn from there.
    for step in range(-5, 6):
        near = (col + step, row)
        if 0 <= near[0] < width and grid[row][near[0]] == KERB:
            horizontal = True
        below = (col, row + step)
        if 0 <= below[1] < height and grid[below[1]][col] == KERB:
            vertical = True
    return horizontal and vertical


def dress_street(grid: list[list[str]], *, seed: int = 0) -> dict[str, int]:
    """Stand lamps, hydrants and signs along this map's kerbs.

    Deterministic: the same grid dresses the same way every time, which
    is the rule every scattered thing in this project follows. A street
    that furnishes itself differently per run is a street nobody can
    tell is working.

    Returns the count of each, and raises rather than returning a map
    whose routes it has changed.
    """
    open_set = _open_chars(grid)
    before = _reachable(grid, open_set)

    candidates = [
        spot for spot in _kerbside(grid)
        if _clear_of_everything(grid, spot[0], spot[1])
    ]
    candidates.sort(key=lambda spot: (spot[1], spot[0]))

    placed: dict[str, list[tuple[int, int]]] = {
        STREETLIGHT: [], FIRE_HYDRANT: [], STOP_SIGN: [],
    }

    def far_enough(col: int, row: int, others, reach: int) -> bool:
        return all(max(abs(col - c), abs(row - r)) >= reach
                   for c, r in others)

    def taken() -> list[tuple[int, int]]:
        return [cell for group in placed.values() for cell in group]

    # The sparse things choose first. There are two signs and three
    # hydrants on a map and a dozen lamps, so letting the lamps run
    # first meant every tile a hydrant could have wanted was already
    # a lamp post -- which is how the first version of this pass came
    # back with a hundred and eighty lamps and nothing else at all.
    plain = [(col, row) for col, row, _dc, _dr in candidates]
    corners = [spot for spot in plain if _is_corner(grid, *spot)]
    for source, char, wanted, apart in (
        (corners, STOP_SIGN, SIGNS_PER_MAP, 14),
        (plain, FIRE_HYDRANT, HYDRANTS_PER_MAP, 14),
    ):
        for col, row in sorted(
            source, key=lambda spot: (spot[0] * 7 + spot[1] * 13 + seed) % 101
        ):
            if len(placed[char]) >= wanted:
                break
            if far_enough(col, row, taken(), apart):
                placed[char].append((col, row))

    # Lamps space out along each kerb, and each side of a road is its
    # own kerb. Measured as a flat distance instead, a lamp on the north
    # pavement suppressed everything within sixteen tiles -- including
    # the whole of the south pavement nine rows below it -- and every
    # street came back lit down one side only.
    runs: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for col, row, dcol, drow in candidates:
        runs.setdefault((dcol, drow), []).append((col, row))
    for side in sorted(runs):
        for col, row in runs[side]:
            if not far_enough(col, row, runs.get(("placed", *side), []),
                              LIGHT_SPACING):
                continue
            if not far_enough(col, row, taken(), 3):
                continue
            runs.setdefault(("placed", *side), []).append((col, row))
            placed[STREETLIGHT].append((col, row))

    for char, cells in placed.items():
        for col, row in cells:
            grid[row][col] = char

    after = _reachable(grid, open_set)
    filled = {cell for group in placed.values() for cell in group}
    assert after == before - filled, sorted(before - filled - after)[:8]
    return {char: len(cells) for char, cells in placed.items()}


# ---------------------------------------------------------------------------
# A little more furniture, and only a little.
#
# One bench and one litter bin per street map, day or night, on the same
# kerbside tiles and under the same flood rule as the lamps. The night maps
# also get two neon signs on building fronts (on the facade's bottom course,
# above the pavement) and a grate breathing steam. The sewers get two outflow
# pipes and one tag on the brick above their walkways. The streets were
# already well furnished; this is punctuation, not a second pass.

BENCH = "ꟓ"
LITTER_BIN = "ꟕ"
NEON_SIGNS = ("ꟗ", "ꟙ", "ꜧ")
STEAM_GRATE = "ꜩ"
SEWER_PIPE = "ꜣ"
SEWER_GRAFFITI = "ꜥ"
FACADE = "▤"
SEWER_BRICK = "b"
SEWER_WALKWAY = "d"
NEON_SPACING = 12


def _spot_order(cells, seed: int):
    return sorted(cells, key=lambda c: ((c[0] * 7 + c[1] * 13 + seed * 3)
                                        % 97, c[1], c[0]))


def furnish_street(grid: list[list[str]], *, seed: int = 0,
                   night: bool = False) -> dict[str, int]:
    """A bench and a bin; at night, two neon signs and a steam grate."""
    open_set = _open_chars(grid)
    before = _reachable(grid, open_set)

    def apart(cell, others, reach):
        return all(max(abs(cell[0] - c), abs(cell[1] - r)) >= reach
                   for c, r in others)

    kerbside = [(col, row) for col, row, _dc, _dr in _kerbside(grid)
                if _clear_of_everything(grid, col, row)]
    placed: dict[str, list[tuple[int, int]]] = {}
    solid: list[tuple[int, int]] = []
    for char in (BENCH, LITTER_BIN):
        for cell in _spot_order(kerbside, seed + len(solid)):
            if apart(cell, solid, 12) and _clear_of_everything(grid, *cell):
                grid[cell[1]][cell[0]] = char
                placed[char] = [cell]
                solid.append(cell)
                break

    if night:
        height, width = len(grid), len(grid[0])
        fronts = [(col, row) for row in range(height - 1)
                  for col in range(1, width - 1)
                  if grid[row][col] == FACADE
                  and grid[row][col - 1] == FACADE
                  and grid[row][col + 1] == FACADE
                  and row + 2 < height
                  # Plain pavement in front of it, so a sign never hangs
                  # over a lamp, a door, a person or a crossing.
                  and all(grid[y][x] in (PAVEMENT, KERB)
                          for y in (row + 1, row + 2)
                          for x in (col - 1, col, col + 1))]
        signs: list[tuple[int, int]] = []
        for cell in _spot_order(fronts, seed):
            if len(signs) >= 2:
                break
            if apart(cell, signs, NEON_SPACING):
                # Never the same sign twice on one street.
                char = NEON_SIGNS[(seed + len(signs)) % len(NEON_SIGNS)]
                grid[cell[1]][cell[0]] = char
                signs.append(cell)
        placed["neon"] = signs
        kerb = set(kerbside)
        pavement = [(col, row) for row in range(1, height - 1)
                    for col in range(1, width - 1)
                    if grid[row][col] == PAVEMENT and (col, row) not in kerb
                    and _clear_of_everything(grid, col, row)]
        for cell in _spot_order(pavement, seed + 5):
            if apart(cell, solid + signs, 6):
                grid[cell[1]][cell[0]] = STEAM_GRATE
                placed[STEAM_GRATE] = [cell]
                break

    after = _reachable(grid, open_set | {STEAM_GRATE})
    assert after == before - set(solid), sorted(before - set(solid) - after)[:8]
    return {char: len(cells) for char, cells in placed.items()}


def furnish_sewer(grid: list[list[str]], *, seed: int = 0) -> dict[str, int]:
    """Two outflow pipes and one tag, on brick above a walkway."""
    height, width = len(grid), len(grid[0])
    faces = [(col, row) for row in range(height - 1)
             for col in range(2, width - 2)
             if all(grid[row][col + d] == SEWER_BRICK for d in (-2, -1, 0, 1, 2))
             and grid[row + 1][col] == SEWER_WALKWAY
             and grid[row + 1][col - 1] == SEWER_WALKWAY
             and grid[row + 1][col + 1] == SEWER_WALKWAY]
    placed: list[tuple[int, int]] = []
    counts = {SEWER_PIPE: 0, SEWER_GRAFFITI: 0}
    for cell in _spot_order(faces, seed):
        if all(max(abs(cell[0] - c), abs(cell[1] - r)) >= 10
               for c, r in placed):
            char = SEWER_PIPE if counts[SEWER_PIPE] < 2 else SEWER_GRAFFITI
            if counts[char] >= (2 if char == SEWER_PIPE else 1):
                break
            grid[cell[1]][cell[0]] = char
            counts[char] += 1
            placed.append(cell)
    return counts
