"""Generate City Day 3: the street where the buildings ran out.

Day 1 was an avenue, Day 2 a crossroads. This one narrows: a single
street running south between tall faces, with two alleys off it and a
loading yard at the bottom. The geometry closes in as the damage grows.

And it has grown. Whole buildings on the east side are gone rather than
merely their frontages, so the street is open to the Astral Sea along
its whole length -- a guard rail of collapsed kerb is all that stands
between the pavement and nothing. Both officer types work this street,
and the phase document requires both to stay avoidable, so the tests
prove a route exists that never enters an Animal Control notice range
nor crosses a police lane.
"""

from collections import deque
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 58
HEIGHT = 64

ARRIVAL = (13, 3)
RETURN_EXIT = (13, 0)
ANCHOR = (13, 12)
FUTURE_EXIT = (20, 63)

# config.UNDEAD_NOTICE_RANGE is 112px; at 16px tiles that is seven.
NOTICE_TILES = 7.0

OFFICERS = ((28, 30), (5, 43))
POLICE = (((5, 22), "ቝ"), ((30, 56), "ቜ"))
BUSINESSPEOPLE = (((6, 24), "v"), ((27, 40), "v"))
CIGARETTES = ((13, 6), (32, 24), (10, 57), (3, 41))
PUDDLES = ((25, 5), (7, 21), (29, 34), (6, 45), (20, 57))

HEADER = [
    "; PHASE 11 - CITY DAY 3, THE OPEN EDGE (58x64 tiles).",
    "; The street narrows and runs south between tall faces. The whole",
    "; east side of the block is gone -- not its frontage, the buildings",
    "; themselves -- so the pavement runs along the edge of nothing.",
    "; Animal Control works the street; police hold two of the corners.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _building(grid, left, top, right, bottom):
    _room(grid, left, top, right, bottom, "#")
    _room(grid, left, bottom - 2, right, bottom - 2, "▱")
    _room(grid, left, bottom - 1, right, bottom, "▤")
    for col in range(left + 1, right, 3):
        grid[bottom - 1][col] = "w"


def build_map() -> list[str]:
    grid = [["▥" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # The street: pavement, kerb, road, kerb, pavement, running south.
    _room(grid, 4, 1, 34, 62)
    _room(grid, 14, 1, 14, 62, ",")
    _room(grid, 15, 1, 23, 62, "=")
    _room(grid, 24, 1, 24, 62, ",")
    for row in range(10, 60, 18):                  # crossings
        for col in range(14, 25):
            grid[row][col] = "▦"
            grid[row + 1][col] = "▦"

    # Two alleys west, and the loading yard at the bottom.
    _room(grid, 1, 18, 8, 24)
    _room(grid, 1, 40, 8, 46)
    _room(grid, 6, 52, 34, 60)

    _building(grid, 1, 1, 12, 16)
    _building(grid, 1, 26, 12, 38)
    _building(grid, 1, 48, 12, 50)
    _building(grid, 26, 1, 34, 20)

    for col, row in PUDDLES:
        assert grid[row][col] in {".", "="}, (col, row, grid[row][col])
        grid[row][col] = "ꞏ"

    # The east side of the block is simply gone. A rail of collapsed kerb
    # marks the edge, and beyond it there is nothing at all.
    for row in range(HEIGHT):
        for col in range(36, WIDTH):
            grid[row][col] = "V"
    for row in range(24, 50):
        grid[row][35] = "V"
    for row in range(HEIGHT):
        if grid[row][35] != "V":
            grid[row][35] = ","

    for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2):
        grid[0][col] = "⮝"
    for col in range(FUTURE_EXIT[0] - 1, FUTURE_EXIT[0] + 2):
        grid[HEIGHT - 1][col] = "⮟"
    grid[RETURN_EXIT[1]][RETURN_EXIT[0]] = "ቢ"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "ባ"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ቤ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ብ"
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
    return ["".join(row) for row in grid]


SOLID = {"▥", "#", "▱", "▤", "w", "V"}
LANES = {"ቝ": (1, 0), "ቜ": (-1, 0), "በ": (0, -1), "ቡ": (0, 1)}


def _under(char: str) -> str:
    return {"ቢ": "⮝", "ባ": "⮟", "ቤ": ".", "ብ": ".", "ቛ": ".", "ሖ": ".",
            "ሞ": ".", "ል": ".", "ꞏ": ".",
            **{char: "." for char in LANES}}.get(char, char)


def _lane_tiles(rows) -> set:
    """Every tile a bullet can occupy, out to the first wall."""
    covered = set()
    for row in range(HEIGHT):
        for col in range(WIDTH):
            step = LANES.get(rows[row][col])
            if step is None:
                continue
            for distance in range(1, 60):
                point = (col + step[0] * distance, row + step[1] * distance)
                if not (0 <= point[0] < WIDTH and 0 <= point[1] < HEIGHT):
                    break
                if _under(rows[point[1]][point[0]]) in SOLID:
                    break
                covered.add(point)
    return covered


def _flood(rows, start, *, avoid=()):
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT) or point in found:
                continue
            if _under(rows[y][x]) in SOLID or point in avoid:
                continue
            found.add(point)
            queue.append(point)
    return found


def validate(rows: list[str]) -> None:
    assert len(rows) == HEIGHT and all(len(row) == WIDTH for row in rows)

    walk = _flood(rows, ARRIVAL)
    assert {ANCHOR, RETURN_EXIT, FUTURE_EXIT, *CIGARETTES, *PUDDLES} <= walk
    for point, _axis in BUSINESSPEOPLE:
        assert point in walk, point
    for point in OFFICERS:
        assert point in walk, point

    # Both officer types must stay avoidable: a route down the street
    # exists that never enters a net's reach nor crosses a firing lane.
    hazard = set(_lane_tiles(rows))
    for col, row in OFFICERS:
        hazard |= {
            (x, y)
            for y in range(HEIGHT) for x in range(WIDTH)
            if math.dist((x, y), (col, row)) <= NOTICE_TILES
        }
    clear = _flood(rows, ARRIVAL, avoid=hazard)
    assert FUTURE_EXIT in clear, "the street cannot be walked safely"
    assert ANCHOR in clear, "the Ashtray is inside a hazard"
    assert RETURN_EXIT in clear

    # No lane fires along the respawn point or the way in.
    assert not ({ANCHOR, ARRIVAL, RETURN_EXIT, FUTURE_EXIT} & _lane_tiles(rows))

    text = "".join(rows)
    # The damage grows through the daytime run: more here than Day 2.
    day_two = (ROOT / "assets" / "maps" / "modern_city_day_2.txt")
    assert text.count("V") > day_two.read_text(encoding="utf-8").count("V")

    assert text.count("ብ") == 1
    assert text.count("ቛ") == len(OFFICERS)
    assert sum(text.count(char) for _p, char in POLICE) == len(POLICE)
    assert text.count("ል") == len(CIGARETTES)
    assert "ም" not in text, "no homeless man in the daytime city"
    for material in ("#", "▱", "▤", "▥", "w", ".", ",", "=", "▦", "ꞏ", "V"):
        assert material in text, material


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_day_3.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
