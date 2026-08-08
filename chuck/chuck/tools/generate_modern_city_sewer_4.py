"""Generate City Sewer 4: the last tunnel, and the way back up.

The region has run east, dropped south, and doubled back west; this one
turns north and climbs. It is the shortest of the four on the map but the
tallest, and it ends at a human-scale maintenance ladder with grey
daylight showing at the top of it.

The ladder is authored scenery for now. Its "Climb up ladder?" prompt
belongs to the pass that builds City Day 1, exactly as the sewer
entrance's prompt waited for City Sewer 1 -- a visible way on is honest;
a prompt that leads nowhere is not.
"""

from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 54
HEIGHT = 50

ARRIVAL = (50, 44)
RETURN_EXIT = (53, 44)
ANCHOR = (30, 33)
LADDER = (26, 4)

RATS = ((44, 41), (33, 36), (20, 27), (24, 15))
CIGARETTES = ((44, 42), (16, 22), (30, 9))
SLUDGE = ((14, 28, 24, 33), (34, 18, 40, 23))

HEADER = [
    "; PHASE 11 - CITY SEWER 4, THE WAY UP (54x50 tiles).",
    "; The last tunnel turns north and climbs toward a maintenance ladder",
    "; with daylight at its head. The ladder is visible scenery until the",
    "; pass that builds City Day 1 authors its climb prompt.",
]


def _room(grid, left, top, right, bottom, char="d"):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def build_map() -> list[str]:
    grid = [["#" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # In from Sewer 3 at the south-east, west, then north the whole way.
    _room(grid, 40, 40, 52, 47)
    _room(grid, 12, 26, 44, 42)
    _room(grid, 12, 8, 26, 30)
    _room(grid, 20, 4, 34, 12)

    for left, top, right, bottom in SLUDGE:
        _room(grid, left, top, right, bottom, "ʓ")
    for col in range(14, 26, 4):                  # slab walkways
        grid[25][col] = ","
        grid[24][col] = ","
    for row in range(30, 40):
        grid[row][38] = "%"
    for col, row in ((46, 43), (30, 28), (17, 14), (28, 8)):
        grid[row][col] = "M"

    # Brick repairs, pipe runs and lights, laid only on tiles that are
    # already wall so a decoration can never close the route.
    def facing_floor(col, row):
        return grid[row][col] == "#" and any(
            grid[row + dr][col + dc] in {"d", ",", "%", "M", "ʓ"}
            for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 0 <= col + dc < WIDTH and 0 <= row + dr < HEIGHT
        )

    for row in range(1, HEIGHT - 1):
        for col in range(1, WIDTH - 1):
            if not facing_floor(col, row):
                continue
            grid[row][col] = "b" if ((col + row) // 6) % 2 == 0 else "R"
            if (col * 3 + row * 7) % 19 == 0:
                grid[row][col] = "i"

    # The ladder: one human-scale structure in two cells, daylight above.
    # Set against the chamber's north wall, so it climbs into the
    # ceiling rather than standing free in the middle of the room.
    grid[LADDER[1]][LADDER[0]] = "Ɫ"
    grid[LADDER[1] + 1][LADDER[0]] = "ɬ"

    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][RETURN_EXIT[0]] = "⮞"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ቈ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ቊ"
    grid[RETURN_EXIT[1]][RETURN_EXIT[0]] = "ቋ"
    for col, row in RATS:
        assert grid[row][col] in {"d", ","}, (col, row, grid[row][col])
        grid[row][col] = "q"
    for col, row in CIGARETTES:
        assert grid[row][col] in {"d", ","}, (col, row, grid[row][col])
        grid[row][col] = "ል"
    return ["".join(row) for row in grid]


SOLID = {"#", "b", "R", "i", "V"}


def _under(char: str) -> str:
    return {"ቈ": "d", "ቊ": "d", "ቋ": "⮞", "q": "d", "ል": ".",
            "Ɫ": "d", "ɬ": "d"}.get(char, char)


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
    # The region's fourth turn: the route climbs more than it runs, which
    # is the property that matters -- not the shape of the bounding box.
    climb = abs(ARRIVAL[1] - LADDER[1])
    run = abs(ARRIVAL[0] - LADDER[0])
    assert climb > run, (climb, run)

    found = _flood(rows, ARRIVAL)
    assert {RETURN_EXIT, ANCHOR, LADDER, *RATS, *CIGARETTES} <= found
    assert (LADDER[0], LADDER[1] + 1) in found, "the ladder's foot"
    assert ANCHOR not in set(RATS)

    # The ladder is one structure in two cells, the ship ladder's shape.
    assert rows[LADDER[1]][LADDER[0]] == "Ɫ"
    assert rows[LADDER[1] + 1][LADDER[0]] == "ɬ"

    text = "".join(rows)
    assert text.count("Ɫ") == 1 and text.count("ɬ") == 1
    assert text.count("ቊ") == 1
    assert text.count("q") == len(RATS)
    assert text.count("ል") == len(CIGARETTES)
    assert "ቆ" not in text, "the region has exactly one crocodile"
    for material in ("#", "b", "R", "i", "d", ",", "M", "%", "ʓ"):
        assert material in text, material


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_sewer_4.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
