"""Generate City Day 1: the first rainy daytime street.

Chuck comes up a manhole into a different part of the city. Same scale,
same traffic language, same buildings -- but daylight, and a street
geometry deliberately unlike the night region's tight blocks: one broad
avenue running east, a plaza opening off it, and a side street north.

Daylight also shows the damage. The avenue visibly continues west past
the plaza and simply stops in Astral blocks, because a road that leads
nowhere should read as broken rather than as an invisible wall.
"""

from collections import deque
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_city_map_common import dress_street, furnish_street, mark_roads, seal_open_edges, terrace_mass, sidewalk_approaches, dress_day_storefronts, dress_day_park

ROOT = Path(__file__).resolve().parents[1]
SEED = 57
WIDTH = 88
HEIGHT = 44

ARRIVAL = (10, 30)
WAYPOINT = (16, 31)
FUTURE_EXIT = (87, 29)

# Businesspeople keep their short patrols; the woman in the red dress
# walks the whole southern pavement, which is what makes her a landmark.
BUSINESSPEOPLE = (((30, 29), "h"), ((58, 27), "v"), ((70, 37), "h"))
RED_DRESS = (44, 37)
CIGARETTES = ((36, 17), (52, 36), (60, 12), (62, 24))
PUDDLES = ((14, 30), (27, 37), (39, 20), (55, 33), (58, 6), (80, 29))

HEADER = [
    "; PHASE 11 - CITY DAY 1, THE WET AVENUE (88x44 tiles).",
    "; Chuck comes up out of the sewer into daylight. One broad avenue",
    "; east, a plaza off it, and a side street north - a looser geometry",
    "; than the night blocks. The avenue's west end is visibly collided.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _building(grid, left, top, right, bottom):
    """A city block: roof, a cornice course, and a windowed face."""
    # Just the mass. The terrace pass at the end of the map gives it a
    # parapet, a roofline and a front, the same as a night block gets.
    _room(grid, left, top, right, bottom, "#")


def build_map() -> list[str]:
    grid = [["▥" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # The avenue: pavement, curb, road, curb, pavement.
    _room(grid, 4, 28, 86, 37)
    _room(grid, 4, 31, 86, 31, ",")
    _room(grid, 4, 32, 86, 34, "=")
    _room(grid, 4, 35, 86, 35, ",")
    for col in range(20, 84, 22):                     # crossings
        for row in range(31, 36):
            grid[row][col] = "▦"
            grid[row][col + 1] = "▦"

    # A plaza off the avenue, and a side street climbing north from it.
    _room(grid, 30, 14, 52, 28)
    # Join the plaza to the side-street pavement. Leaving column 53
    # solid made a one-tile-wide tower out of the seam between them.
    _room(grid, 53, 14, 53, 28)
    _room(grid, 54, 4, 64, 28)
    _room(grid, 56, 8, 62, 26, "=")
    _room(grid, 55, 8, 55, 26, ",")
    _room(grid, 63, 8, 63, 26, ",")

    # The blocks that shape them.
    _building(grid, 2, 4, 28, 27)
    _building(grid, 34, 2, 50, 12)
    _building(grid, 66, 2, 86, 27)
    _building(grid, 6, 39, 40, 43)
    _building(grid, 46, 39, 84, 43)

    for col, row in PUDDLES:
        assert grid[row][col] in {".", "="}, (col, row, grid[row][col])
        grid[row][col] = "ꞏ"

    # Daylight shows the damage: the avenue runs west and stops.
    for row in range(28, 38):
        for col in range(0, 4):
            grid[row][col] = "V"
    # ...as does the plaza's northern arm.
    for col in range(30, 52):
        grid[0][col] = "V"
        grid[1][col] = "V"

    # The sidewalk continues; the carriageway visibly ends in the Sea.
    for row in range(31, 38):
        grid[row][WIDTH - 1] = "V"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][WIDTH - 1] = "⮞"
    grid[FUTURE_EXIT[1]][WIDTH - 1] = "ቑ"
    grid[FUTURE_EXIT[1]][WIDTH - 3] = "ቚ"  # where Day 2 sets Chuck down
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ቍ"
    for (col, row), axis in BUSINESSPEOPLE:
        assert grid[row][col] == ".", (col, row, grid[row][col])
        grid[row][col] = "ሖ" if axis == "h" else "ሞ"
    grid[RED_DRESS[1]][RED_DRESS[0]] = "ቒ"
    for col, row in CIGARETTES:
        assert grid[row][col] in {".", "="}, (col, row, grid[row][col])
        grid[row][col] = "ል"
    # Dress the whole map: undifferentiated mass becomes buildings, and
    # every carriageway gets its centre line.
    terrace_mass(grid)
    # Street furniture last, so it can see the finished pavement
    # and refuse to stand anywhere that would close a route.
    protected = sidewalk_approaches(grid)
    dress_street(grid, seed=SEED, protected=protected)
    furnish_street(grid, seed=SEED, night=False, protected=protected)
    dress_day_storefronts(grid, seed=SEED)
    dress_day_park(grid)
    mark_roads(grid)
    seal_open_edges(grid, "modern_city_day_1")
    return ["".join(row) for row in grid]


SOLID = {"▥", "#", "▱", "▤", "w", "V"}


def _under(char: str) -> str:
    return {"ቍ": ".", "ቑ": "⮞", "ሖ": ".", "ሞ": ".", "ቒ": ".",
            "ል": ".", "ꞏ": ".", "ቚ": "."}.get(char, char)


def _flood(rows, start):
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT) or point in found:
                continue
            if _under(rows[y][x]) in SOLID:
                continue
            found.add(point)
            queue.append(point)
    return found


def validate(rows: list[str]) -> None:
    assert len(rows) == HEIGHT and all(len(row) == WIDTH for row in rows)

    found = _flood(rows, ARRIVAL)
    assert {WAYPOINT, FUTURE_EXIT, RED_DRESS, *CIGARETTES, *PUDDLES} <= found
    for position, _axis in BUSINESSPEOPLE:
        assert position in found, position

    # The woman in the red dress patrols a longer stretch than anyone
    # else: that length, not a subplot, is what makes her readable.
    row = RED_DRESS[1]
    stretch = 0
    col = RED_DRESS[0]
    while col > 0 and _under(rows[row][col - 1]) not in SOLID:
        col -= 1
        stretch += 1
    col = RED_DRESS[0]
    while col < WIDTH - 1 and _under(rows[row][col + 1]) not in SOLID:
        col += 1
        stretch += 1
    assert stretch >= 40, stretch

    text = "".join(rows)
    assert text.count("ቒ") == 1, "exactly one woman in a red dress"
    assert text.count("ል") == len(CIGARETTES)
    assert "ም" not in text, "no homeless man in the daytime city"
    # Every road that runs off the map ends in visible Astral damage.
    assert all(rows[row][0] == "V" for row in range(28, 38))
    for material in ("#", "▱", "▤", "▥", "w", ".", ",", "=", "▦", "ꞏ", "V"):
        assert material in text, material


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_day_1.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
