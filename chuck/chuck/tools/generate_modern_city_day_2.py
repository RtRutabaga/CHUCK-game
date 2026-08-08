"""Generate City Day 2: a live intersection under heavier damage.

City Day 1 was one broad avenue with a plaza off it. This map is its
opposite: a crossroads, two streets meeting at right angles with traffic
running on both, so the daytime region reads as a city rather than a
sequence of corridors.

The phase document asks for Astral blocks to grow more common as the
daytime progression goes on, so a whole quarter of this crossroads is
simply gone -- the north-west block and the streets that served it end
in visible damage.
"""

from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 76
HEIGHT = 58

ARRIVAL = (2, 33)
RETURN_EXIT = (0, 33)
ANCHOR = (12, 38)
FUTURE_EXIT = (38, 57)

# Traffic runs on both streets, so the crossing has to be timed twice.
TRAFFIC = (
    ((6, 30), "ሎ"), ((24, 30), "ሎ"), ((52, 30), "ሎ"),
    ((14, 34), "ሏ"), ((40, 34), "ሏ"), ((64, 34), "ሏ"),
    ((34, 10), "ሟ"), ((34, 42), "ሟ"),
    ((38, 24), "ሠ"), ((38, 52), "ሠ"),
)
BUSINESSPEOPLE = (((20, 27), "h"), ((56, 38), "h"), ((30, 50), "v"))
CIGARETTES = ((24, 27), (46, 27), (36, 14), (62, 38))
PUDDLES = ((10, 38), (26, 28), (44, 38), (30, 22), (58, 27), (36, 49))

HEADER = [
    "; PHASE 11 - CITY DAY 2, THE CROSSROADS (76x58 tiles).",
    "; Two streets meet at right angles with traffic on both, so the",
    "; crossing must be timed twice. The whole north-west quarter is gone:",
    "; daylight shows the collision damage plainly, and it is spreading.",
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

    # The east-west street.
    _room(grid, 1, 26, 74, 39)
    _room(grid, 1, 29, 74, 29, ",")
    _room(grid, 1, 30, 74, 35, "=")
    _room(grid, 1, 36, 74, 36, ",")
    # The north-south street crossing it.
    _room(grid, 30, 1, 43, 56)
    _room(grid, 33, 1, 33, 56, ",")
    _room(grid, 34, 1, 39, 56, "=")
    _room(grid, 40, 1, 40, 56, ",")
    # The junction itself is all road.
    _room(grid, 30, 29, 43, 36, "=")

    for col in (20, 56):                       # crossings on the avenue
        for row in range(29, 37):
            grid[row][col] = "▦"
            grid[row][col + 1] = "▦"
    for row in (18, 46):                       # ...and on the boulevard
        for col in range(33, 41):
            grid[row][col] = "▦"
            grid[row + 1][col] = "▦"

    _building(grid, 2, 42, 28, 55)
    _building(grid, 45, 42, 74, 55)
    _building(grid, 45, 4, 74, 25)

    for col, row in PUDDLES:
        assert grid[row][col] in {".", "="}, (col, row, grid[row][col])
        grid[row][col] = "ꞏ"

    # The north-west quarter is simply gone, and the streets that served
    # it end in it. This is the damage growing, not a wall.
    for row in range(0, 26):
        for col in range(0, 30):
            grid[row][col] = "V"
    for row in range(26, 29):
        for col in range(0, 18):
            grid[row][col] = "V"

    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][0] = "⮜"
    for col in range(FUTURE_EXIT[0] - 1, FUTURE_EXIT[0] + 2):
        grid[HEIGHT - 1][col] = "⮟"
    grid[RETURN_EXIT[1]][0] = "ቔ"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "ቕ"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ቖ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ቘ"
    for (col, row), char in TRAFFIC:
        assert grid[row][col] == "=", (col, row, grid[row][col])
        grid[row][col] = char
    for (col, row), axis in BUSINESSPEOPLE:
        assert grid[row][col] == ".", (col, row, grid[row][col])
        grid[row][col] = "ሖ" if axis == "h" else "ሞ"
    for col, row in CIGARETTES:
        assert grid[row][col] in {".", "="}, (col, row, grid[row][col])
        grid[row][col] = "ል"
    return ["".join(row) for row in grid]


SOLID = {"▥", "#", "▱", "▤", "w", "V"}


def _under(char: str) -> str:
    return {"ቔ": "⮜", "ቕ": "⮟", "ቖ": ".", "ቘ": ".", "ሖ": ".", "ሞ": ".",
            "ል": ".", "ꞏ": ".", "ሎ": "=", "ሏ": "=", "ሟ": "=",
            "ሠ": "="}.get(char, char)


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
    assert {ANCHOR, RETURN_EXIT, FUTURE_EXIT, *CIGARETTES, *PUDDLES} <= found
    for position, _axis in BUSINESSPEOPLE:
        assert position in found, position
    for position, _char in TRAFFIC:
        assert position in found, position

    # A crossroads, not another corridor: both streets carry traffic, and
    # both have to be crossed to see the whole map.
    text = "".join(rows)
    horizontal = sum(text.count(char) for char in ("ሎ", "ሏ"))
    vertical = sum(text.count(char) for char in ("ሟ", "ሠ"))
    assert horizontal >= 4 and vertical >= 4, (horizontal, vertical)

    # The damage is spreading: more Astral here than on City Day 1.
    day_one = (ROOT / "assets" / "maps" / "modern_city_day_1.txt")
    assert text.count("V") > day_one.read_text(encoding="utf-8").count("V")

    assert text.count("ቘ") == 1
    assert text.count("ል") == len(CIGARETTES)
    assert "ም" not in text, "no homeless man in the daytime city"
    assert "ቒ" not in text, "the woman in the red dress walks City Day 1"
    for material in ("#", "▱", "▤", "▥", "w", ".", ",", "=", "▦", "ꞏ", "V"):
        assert material in text, material


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_day_2.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
