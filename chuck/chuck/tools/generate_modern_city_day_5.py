"""Generate City Day 5: the overpass, and what is left of it.

The last ordinary daytime map before the collision tableau. A raised
roadway runs south across a city that is no longer there -- the deck is
all that survives, nine tiles wide with the Astral Sea on both sides,
and traffic still running on it because the lights have not been told.

Two spans have dropped out. Unlike City Day 4's square, these jumps are
not optional: the deck is the only way south, so the map is where the
committed jump stops being a reward and becomes the route. Each gap is
one tile, each landing is deck, and neither sits under a traffic lane,
so a jump is never taken blind into a car.
"""

from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 46
HEIGHT = 68

ARRIVAL = (22, 3)
RETURN_EXIT = (22, 0)
ANCHOR = (18, 8)
FUTURE_EXIT = (22, 67)

# The deck: pavement, kerb, two lanes, kerb, pavement.
DECK = (17, 1, 28, 66)
# Where the deck has dropped out. Each is a single row of the whole deck.
BROKEN_SPANS = (26, 44)

TRAFFIC = (((22, 14), "ሟ"), ((25, 34), "ሠ"), ((22, 58), "ሟ"))
OFFICERS = ((18, 20),)
POLICE = (((27, 60), "ቜ"),)
BUSINESSPEOPLE = (((27, 12), "v"),)
CIGARETTES = ((18, 30), (27, 38), (18, 50), (27, 22))
PUDDLES = ((18, 6), (27, 30), (18, 40), (27, 52), (18, 62))

HEADER = [
    "; PHASE 11 - CITY DAY 5, THE OVERPASS (46x68 tiles).",
    "; A raised roadway is all that survives here: nine tiles wide with",
    "; the Astral Sea on both sides, and traffic still running on it.",
    "; Two spans have dropped out. These jumps are the route, not a",
    "; reward - but no landing sits under a lane.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def build_map() -> list[str]:
    # Everything is the Sea; the deck is laid back over it.
    grid = [["V" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    _room(grid, *DECK)
    _room(grid, DECK[0] + 2, DECK[1], DECK[0] + 2, DECK[3], ",")
    _room(grid, DECK[0] + 3, DECK[1], DECK[2] - 3, DECK[3], "=")
    _room(grid, DECK[2] - 2, DECK[1], DECK[2] - 2, DECK[3], ",")
    for row in range(8, 64, 16):                    # crossings on the deck
        for col in range(DECK[0] + 2, DECK[2] - 1):
            grid[row][col] = "▦"

    # The two dropped spans.
    for row in BROKEN_SPANS:
        for col in range(DECK[0], DECK[2] + 1):
            grid[row][col] = "V"

    for col, row in PUDDLES:
        assert grid[row][col] in {".", "="}, (col, row, grid[row][col])
        grid[row][col] = "ꞏ"

    for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2):
        grid[0][col] = "⮝"
    for col in range(FUTURE_EXIT[0] - 1, FUTURE_EXIT[0] + 2):
        grid[HEIGHT - 1][col] = "⮟"
    grid[RETURN_EXIT[1]][RETURN_EXIT[0]] = "ቭ"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "ቮ"
    grid[FUTURE_EXIT[1] - 2][FUTURE_EXIT[0]] = "ቹ"  # back up from Day 6
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ቯ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ተ"
    for (col, row), char in TRAFFIC:
        assert grid[row][col] == "=", (col, row, grid[row][col])
        grid[row][col] = char
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


SOLID = {"#", "▱", "▤", "▥", "w"}
LANE_CHARS = {"ሟ", "ሠ", "ሎ", "ሏ"}


def _under(char: str) -> str:
    return {"ቭ": "⮝", "ቮ": "⮟", "ቯ": ".", "ተ": ".", "ቛ": ".", "ሖ": ".",
            "ቹ": ".",
            "ሞ": ".", "ል": ".", "ꞏ": ".", "ቜ": ".",
            **{char: "=" for char in LANE_CHARS}}.get(char, char)


def _flood(rows, start, *, hops):
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

    hopped = _flood(rows, ARRIVAL, hops=True)
    walked = _flood(rows, ARRIVAL, hops=False)

    assert FUTURE_EXIT in hopped, "the overpass cannot be crossed"
    assert FUTURE_EXIT not in walked, "the broken spans can be walked around"
    assert ANCHOR in walked, "the Ashtray is past a jump"
    for point in CIGARETTES:
        assert point in hopped, point

    # Each dropped span is one row, and the deck resumes directly beyond
    # it, so every required jump is the ordinary committed one.
    for row in BROKEN_SPANS:
        assert all(_under(rows[row][col]) == "V"
                   for col in range(DECK[0], DECK[2] + 1))
        for col in range(DECK[0], DECK[2] + 1):
            assert _under(rows[row - 1][col]) != "V", (col, row)
            assert _under(rows[row + 1][col]) != "V", (col, row)

    # Every span can be jumped on the pavement rather than in the road.
    # The deck's middle is carriageway by construction, so the property
    # worth proving is that a footway crosses each gap: a player is never
    # forced to launch from or land in a live lane.
    pavement = (DECK[0], DECK[0] + 1, DECK[2] - 1, DECK[2])
    for row in BROKEN_SPANS:
        safe = [
            col for col in pavement
            if _under(rows[row - 1][col]) not in {"=", "V"}
            and _under(rows[row + 1][col]) not in {"=", "V"}
        ]
        assert safe, row

    text = "".join(rows)
    # The damage ratchet: a greater share of void than the map before.
    previous = (ROOT / "assets" / "maps" / "modern_city_day_4.txt")
    before = previous.read_text(encoding="utf-8").splitlines()
    before_density = (sum(row.count("V") for row in before)
                      / (len(before) * len(before[0])))
    assert text.count("V") / (WIDTH * HEIGHT) > before_density

    assert text.count("ተ") == 1
    assert text.count("ል") == len(CIGARETTES)
    assert "ም" not in text, "no homeless man in the daytime city"
    for material in (".", ",", "=", "▦", "ꞏ", "V"):
        assert material in text, material


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_day_5.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
