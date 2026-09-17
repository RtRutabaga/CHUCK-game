"""Generate City Sewer 3: the flooded hall the crocodile has taken.

Sewer 1 ran east, Sewer 2 dropped south; this one doubles back and runs
west, so the region keeps turning. Its middle is a wide flooded hall
with a sludge channel down it, and a crocodile living in the channel.

The phase document is explicit that the crocodile must stay escapable or
avoidable rather than becoming a mandatory combat gate, so the hall has
two ways across -- a north maintenance walkway and a south ledge -- and
the validator proves a route exists that never enters its notice range.
"""

from collections import deque
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_city_map_common import furnish_sewer  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 84
HEIGHT = 40

# config.UNDEAD_NOTICE_RANGE is 112px; at 16px tiles that is seven.
NOTICE_TILES = 7.0

ARRIVAL = (78, 5)
RETURN_EXIT = (83, 5)
WAYPOINT = (63, 15)
FUTURE_EXIT = (0, 26)

CROCODILE = (38, 22)
RATS = ((70, 8), (58, 17), (20, 24), (9, 30))
CIGARETTES = ((66, 6), (28, 16), (6, 31))

# The flooded hall, its sludge channel, and the two ways across it.
HALL = (24, 14, 54, 30)
CHANNEL = (26, 20, 52, 25)
NORTH_WALK = (24, 15, 54, 18)
SOUTH_WALK = (24, 27, 54, 29)

HEADER = [
    "; PHASE 11 - CITY SEWER 3, THE FLOODED HALL (84x40 tiles).",
    "; The region doubles back: this map runs east to west. Its middle is a",
    "; wide hall with a sludge channel and a crocodile in it. Two ways",
    "; across - a north walkway and a south ledge - keep the animal",
    "; avoidable rather than a mandatory fight.",
]


def _room(grid, left, top, right, bottom, char="d"):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def build_map() -> list[str]:
    grid = [["#" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # In from Sewer 2 at the north-east, down, then west the whole way.
    _room(grid, 70, 3, 82, 9)
    _room(grid, 58, 3, 72, 19)
    _room(grid, 54, 12, 62, 19)
    _room(grid, *HALL)
    _room(grid, 8, 22, 26, 32)
    _room(grid, 1, 24, 12, 32)

    # The hall's sludge channel, and the dry ways along either wall.
    _room(grid, *CHANNEL, "ʓ")
    _room(grid, *NORTH_WALK)
    _room(grid, *SOUTH_WALK)
    for col in range(NORTH_WALK[0], NORTH_WALK[2] + 1, 6):
        grid[NORTH_WALK[1] + 1][col] = ","
        grid[NORTH_WALK[1] + 2][col] = ","
    # Two crossings between the walkways, so neither side is a dead end.
    for col in (30, 48):
        for row in range(CHANNEL[1], CHANNEL[3] + 1):
            grid[row][col] = "d"

    for col, row in ((74, 6), (60, 14), (20, 28), (5, 30)):
        grid[row][col] = "M"
    for col in range(60, 72):
        grid[10][col] = "%"

    # Brick repairs, pipe runs and utility lights, laid as a continuous
    # band on tiles that are already wall so nothing can close a route.
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

    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][RETURN_EXIT[0]] = "⮞"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][FUTURE_EXIT[0]] = "⮜"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ቂ"
    grid[RETURN_EXIT[1]][RETURN_EXIT[0]] = "ቄ"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "ቅ"
    grid[FUTURE_EXIT[1]][3] = "ቌ"    # where Sewer 4 sets Chuck back down
    grid[CROCODILE[1]][CROCODILE[0]] = "ቆ"
    for col, row in RATS:
        assert grid[row][col] in {"d", ","}, (col, row, grid[row][col])
        grid[row][col] = "q"
    for col, row in CIGARETTES:
        assert grid[row][col] in {"d", ","}, (col, row, grid[row][col])
        grid[row][col] = "ል"
    furnish_sewer(grid, seed=696)
    return ["".join(row) for row in grid]


SOLID = {"#", "b", "R", "i", "V"}


def _under(char: str) -> str:
    return {"ቂ": "d", "ቄ": "⮞", "ቅ": "⮜", "ቆ": "ʓ",
            "q": "d", "ል": ".", "ቌ": "d"}.get(char, char)


def _flood(rows, start, *, avoid_crocodile=False):
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
            if avoid_crocodile and math.dist(point, CROCODILE) <= NOTICE_TILES:
                continue
            found.add(point)
            queue.append(point)
    return found


def validate(rows: list[str]) -> None:
    assert len(rows) == HEIGHT and all(len(row) == WIDTH for row in rows)

    found = _flood(rows, ARRIVAL)
    assert {RETURN_EXIT, FUTURE_EXIT, WAYPOINT, CROCODILE,
            *RATS, *CIGARETTES} <= found

    # The promise: the hall can be crossed without ever entering the
    # crocodile's notice range, so it is never a mandatory fight.
    clear = _flood(rows, ARRIVAL, avoid_crocodile=True)
    assert FUTURE_EXIT in clear, "the crocodile blocks the only way through"
    assert WAYPOINT in clear, "the waypoint sits inside its notice range"
    # ...but it does hold the middle: the channel is genuinely contested.
    assert not any(math.dist(point, CROCODILE) <= 3 for point in clear)

    # It lives in the sludge, and the sludge is what makes it dangerous:
    # slowed, Chuck is still quicker, but not by much.
    assert _under(rows[CROCODILE[1]][CROCODILE[0]]) == "ʓ"

    text = "".join(rows)
    assert text.count("ቆ") == 1, "exactly one crocodile in the region"
    assert text.count("q") == len(RATS)
    assert text.count("ል") == len(CIGARETTES)
    for material in ("#", "b", "R", "i", "d", ",", "M", "%", "ʓ"):
        assert material in text, material


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_sewer_3.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
