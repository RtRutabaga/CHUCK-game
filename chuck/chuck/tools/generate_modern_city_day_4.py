"""Generate City Day 4: the square where the ground gave way.

The first three daytime maps lost buildings. This one loses the floor.
A civic square has broken into slabs with the Astral Sea showing between
them, so crossing it means committed jumps over one-tile gaps -- the
same jump the Moonmoth Fen and the sewer taught, now in daylight on
concrete, and the ramp toward City Day 6's heavier jump hazards.

The square is optional in the strict sense: a pavement runs around its
north and east sides. It is where the cigarettes are, and it is much
shorter than walking round, so it should be tempting rather than
mandatory. The validator proves both -- that the jumps work, and that
somebody who refuses to jump at all can still finish the map.
"""

from collections import deque
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_city_map_common import mark_roads, terrace_mass

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 70
HEIGHT = 52

ARRIVAL = (5, 6)
RETURN_EXIT = (5, 0)
ANCHOR = (9, 9)
FUTURE_EXIT = (69, 43)

# The broken square: slabs of pavement with single-tile gaps between.
SQUARE = (18, 15, 52, 37)
GAP_COLUMNS = (23, 30, 37, 44)
GAP_ROWS = (21, 29)

OFFICERS = ((6, 30), (66, 22))
POLICE = (((24, 43), "ቜ"),)
BUSINESSPEOPLE = (((6, 20), "v"), ((50, 9), "h"))
CIGARETTES = ((26, 25), (41, 25), (34, 33), (20, 17))
PUDDLES = ((6, 14), (26, 33), (50, 17), (20, 47), (66, 33))

HEADER = [
    "; PHASE 11 - CITY DAY 4, THE BROKEN SQUARE (70x52 tiles).",
    "; The earlier maps lost buildings; this one loses the floor. A civic",
    "; square has broken into slabs with the Astral Sea between them, so",
    "; crossing it takes committed jumps. A pavement runs the long way",
    "; round for anyone who would rather not.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _building(grid, left, top, right, bottom):
    # Just the mass. The terrace pass at the end of the map gives it a
    # parapet, a roofline and a front, the same as a night block gets.
    _room(grid, left, top, right, bottom, "#")


def build_map() -> list[str]:
    # The city ends here. Everything is the Astral Sea except what is
    # explicitly laid back over it: the street in, the ridge round, and
    # the broken square floating between them.
    grid = [["V" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # The street in from the north-west, still intact.
    _room(grid, 1, 1, 8, 41)
    _room(grid, 1, 42, 26, 50)
    _room(grid, 1, 44, 26, 44, ",")
    _room(grid, 1, 45, 26, 47, "=")
    _room(grid, 1, 48, 26, 48, ",")
    for col in range(10, 26, 8):
        for row in range(44, 49):
            grid[row][col] = "▦"
            grid[row][col + 1] = "▦"
    # A ridge of surviving pavement runs north and east around the square.
    # Reaches to row 13 so the drop onto the square is one tile, not two.
    _room(grid, 8, 8, 68, 13)
    _room(grid, 64, 8, 68, 45)
    _room(grid, 26, 42, 68, 45)

    _building(grid, 16, 1, 40, 7)
    _building(grid, 44, 1, 62, 7)

    # The square itself, floating, and the cracks through it.
    _room(grid, *SQUARE)
    for col in GAP_COLUMNS:
        for row in range(SQUARE[1], SQUARE[3] + 1):
            grid[row][col] = "V"
    for row in GAP_ROWS:
        for col in range(SQUARE[0], SQUARE[2] + 1):
            grid[row][col] = "V"

    for col, row in PUDDLES:
        assert grid[row][col] in {".", "="}, (col, row, grid[row][col])
        grid[row][col] = "ꞏ"

    for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2):
        grid[0][col] = "⮝"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][WIDTH - 1] = "⮞"
    grid[RETURN_EXIT[1]][RETURN_EXIT[0]] = "ቨ"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "ቩ"
    grid[FUTURE_EXIT[1]][WIDTH - 3] = "ቱ"  # back west from Day 5
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ቪ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ቫ"
    for col, row in OFFICERS:
        assert grid[row][col] == ".", (col, row, grid[row][col])
        grid[row][col] = "ቛ"
    for (col, row), char in POLICE:
        assert grid[row][col] == ".", (col, row, grid[row][col])
        grid[row][col] = char
    for (col, row), axis in BUSINESSPEOPLE:
        assert grid[row][col] == ".", (col, row, grid[row][col])
        grid[row][col] = "ሖ" if axis == "h" else "ሞ"
    for col, row in CIGARETTES:
        assert grid[row][col] in {".", "="}, (col, row, grid[row][col])
        grid[row][col] = "ል"
    # Dress the whole map: undifferentiated mass becomes buildings, and
    # every carriageway gets its centre line.
    terrace_mass(grid)
    mark_roads(grid)
    return ["".join(row) for row in grid]


SOLID = {"▥", "#", "▱", "▤", "w"}


def _under(char: str) -> str:
    return {"ቨ": "⮝", "ቩ": "⮞", "ቪ": ".", "ቫ": ".", "ቛ": ".", "ሖ": ".",
            "ቱ": ".",
            "ሞ": ".", "ል": ".", "ꞏ": ".", "ቜ": "."}.get(char, char)


def _flood(rows, start, *, hops):
    """Walk the map; with hops, allow the committed one-tile jump."""
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            step = (col + dc, row + dr)
            land = (col + 2 * dc, row + 2 * dr)
            for point in ((step, land) if hops else (step,)):
                x, y = point
                if not (0 <= x < WIDTH and 0 <= y < HEIGHT) or point in found:
                    continue
                char = _under(rows[y][x])
                if char in SOLID or char == "V":
                    continue
                if point is land and _under(rows[step[1]][step[0]]) != "V":
                    continue
                found.add(point)
                queue.append(point)
    return found


def validate(rows: list[str]) -> None:
    assert len(rows) == HEIGHT and all(len(row) == WIDTH for row in rows)

    # Every crack is exactly one tile across, so no jump is impossible.
    for col in GAP_COLUMNS:
        assert _under(rows[SQUARE[1] + 1][col - 1]) not in SOLID
        assert _under(rows[SQUARE[1] + 1][col + 1]) not in SOLID
    for row in GAP_ROWS:
        assert _under(rows[row - 1][SQUARE[0] + 1]) not in SOLID
        assert _under(rows[row + 1][SQUARE[0] + 1]) not in SOLID

    hopped = _flood(rows, ARRIVAL, hops=True)
    walked = _flood(rows, ARRIVAL, hops=False)

    assert {ANCHOR, RETURN_EXIT, FUTURE_EXIT} <= walked, (
        "the map cannot be finished without jumping")
    for point, _axis in BUSINESSPEOPLE:
        assert point in walked, point
    for point in OFFICERS:
        assert point in walked, point

    # The square's rewards are behind the jumps -- tempting, not required.
    for cache in CIGARETTES:
        assert cache in hopped, cache
    inner = [cache for cache in CIGARETTES if cache not in walked]
    assert inner, "no cigarette actually needs a jump"

    text = "".join(rows)
    # The damage ratchet. Density is the honest measure of "increasingly
    # common" -- a bigger map with the same proportion of void is not a
    # more damaged one -- so the rule is that no daytime map may be less
    # damaged than the one before it, by share of its own area.
    previous = (ROOT / "assets" / "maps" / "modern_city_day_3.txt")
    before = previous.read_text(encoding="utf-8").splitlines()
    before_density = (sum(row.count("V") for row in before)
                      / (len(before) * len(before[0])))
    density = text.count("V") / (WIDTH * HEIGHT)
    assert density > before_density, (density, before_density)

    assert text.count("ቫ") == 1
    assert text.count("ቛ") == len(OFFICERS)
    assert text.count("ል") == len(CIGARETTES)
    assert "ም" not in text, "no homeless man in the daytime city"
    # No side facades here: there are no side streets left to face onto.
    for material in ("#", "▱", "▤", "w", ".", ",", "=", "▦", "ꞏ", "V"):
        assert material in text, material


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_day_4.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
