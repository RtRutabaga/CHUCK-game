"""Generate City Day 6: the collision, and the way out of the phase.

The most damaged map in the city and the phase's culminating tableau.
Three worlds are visible at once: the daytime street, a patch of Chult
jungle grown through the road with raptors in it, and -- inside the
damaged northern building -- a block of Douglas fir forest at night,
which is the phase's one planar portal.

Everything here is spectacle Chuck routes around rather than fights. The
dinosaur is scenery with teeth, the raptors and police have their own
argument, and the phase document is explicit that the chaos must not
create unavoidable damage at the Ashtray or the arrival. The validator
proves exactly that: a clear route exists from the arrival to the portal
that never crosses a police lane or comes within notice of the dinosaur.

This slice lays the ground and the standing cast. The fleeing
businesspeople and the spinning officer are their own pass.
"""

from collections import deque
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 80
HEIGHT = 60

ARRIVAL = (38, 3)
RETURN_EXIT = (38, 0)
ANCHOR = (10, 13)
PORTAL = (34, 8)

# The jungle grown through the road, and what came with it.
CHULT_PATCH = (24, 26, 52, 44)
RAPTORS = ((30, 32), (44, 38), (36, 41))
DINOSAUR = (40, 34)
PRONE = (42, 36)

POLICE = (((22, 34), "ቝ"), ((54, 30), "ቜ"))
BUSINESSPEOPLE = (((12, 50), "h"), ((70, 50), "h"))
CIGARETTES = ((8, 21), (72, 21), (22, 40), (54, 40))
JUMPS = ((18, 18), (62, 18), (18, 48), (62, 48))

HEADER = [
    "; PHASE 11 - CITY DAY 6, THE COLLISION (80x60 tiles).",
    "; Three worlds at once: the daytime street, a patch of Chult grown",
    "; through the road, and a block of Douglas fir forest at night inside",
    "; the damaged northern building. The jungle is spectacle to route",
    "; around; the forest block is the way out of the phase.",
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
    grid = [["V" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # A ring road around the whole scene, and the plaza it encloses.
    _room(grid, 4, 12, 76, 56)
    _room(grid, 4, 20, 76, 22, "=")
    _room(grid, 4, 19, 76, 19, ",")
    _room(grid, 4, 23, 76, 23, ",")
    _room(grid, 4, 46, 76, 48, "=")
    _room(grid, 4, 45, 76, 45, ",")
    _room(grid, 4, 49, 76, 49, ",")
    for col in range(12, 72, 20):
        for row in list(range(19, 24)) + list(range(45, 50)):
            grid[row][col] = "▦"
            grid[row][col + 1] = "▦"

    # The northern block, with the street opened into it.
    _building(grid, 20, 1, 60, 10)
    _room(grid, 30, 5, 44, 11)
    _room(grid, 36, 11, 40, 12)
    # The way in from City Day 5, down through the ruined frontage.
    _room(grid, 37, 0, 39, 5)

    # The Chult patch, grown up through the plaza.
    _room(grid, *CHULT_PATCH, "ᵹ")
    for col in range(CHULT_PATCH[0], CHULT_PATCH[2] + 1):
        for row in range(CHULT_PATCH[1], CHULT_PATCH[3] + 1):
            if (col * 7 + row * 11) % 9 == 0:
                grid[row][col] = "ᵺ"

    # The Douglas fir block, standing inside the damaged building.
    _room(grid, PORTAL[0] - 1, PORTAL[1] - 2, PORTAL[0] + 1, PORTAL[1], "ᶂ")
    # ...and the street-view Astral damage that opened the wall for it.
    for col in range(24, 30):
        for row in range(4, 11):
            grid[row][col] = "V"
    for col in range(46, 56):
        for row in range(3, 10):
            grid[row][col] = "V"

    # Most of the plaza has already gone. What is left is a corridor down
    # each side of the jungle and the ring road around it -- the phase
    # document calls this the most visibly damaged city map, and this is
    # what that means on the ground.
    for left, top, right, bottom in (
        (6, 25, 21, 43), (55, 25, 74, 43),
        (24, 14, 34, 17), (42, 14, 52, 17),
        (24, 51, 34, 54), (42, 51, 52, 54),
    ):
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                grid[row][col] = "V"

    # Committed jumps at the plaza's four corners: the ground is going.
    for col, row in JUMPS:
        for offset in (-1, 0, 1):
            grid[row][col + offset] = "V"

    for col, row in CIGARETTES:
        assert grid[row][col] in {".", "="}, (col, row, grid[row][col])
        grid[row][col] = "ል"

    for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2):
        grid[0][col] = "⮝"
    grid[RETURN_EXIT[1]][RETURN_EXIT[0]] = "ቲ"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ታ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ቴ"
    grid[PORTAL[1] + 1][PORTAL[0]] = "ት"
    grid[DINOSAUR[1]][DINOSAUR[0]] = "ቶ"
    grid[PRONE[1]][PRONE[0]] = "ቷ"
    for col, row in RAPTORS:
        grid[row][col] = "ቸ"
    for (col, row), char in POLICE:
        assert grid[row][col] == ".", (col, row, grid[row][col])
        grid[row][col] = char
    for (col, row), axis in BUSINESSPEOPLE:
        assert grid[row][col] == ".", (col, row, grid[row][col])
        grid[row][col] = "ሖ" if axis == "h" else "ሞ"
    return ["".join(row) for row in grid]


SOLID = {"#", "▱", "▤", "▥", "w", "ᵺ", "ᶂ"}
LANES = {"ቝ": (1, 0), "ቜ": (-1, 0), "በ": (0, -1), "ቡ": (0, 1)}
# config.DINOSAUR_NOTICE_RANGE is 128px; at 16px tiles that is eight.
DINOSAUR_NOTICE = 8.0


def _under(char: str) -> str:
    return {"ቲ": "⮝", "ታ": ".", "ቴ": ".", "ት": ".", "ቶ": "ᵹ", "ቷ": "ᵹ",
            "ቸ": "ᵹ", "ሖ": ".", "ሞ": ".", "ል": ".",
            **{char: "." for char in LANES}}.get(char, char)


def _lane_tiles(rows) -> set:
    covered = set()
    for row in range(HEIGHT):
        for col in range(WIDTH):
            step = LANES.get(rows[row][col])
            if step is None:
                continue
            for distance in range(1, 80):
                point = (col + step[0] * distance, row + step[1] * distance)
                if not (0 <= point[0] < WIDTH and 0 <= point[1] < HEIGHT):
                    break
                if _under(rows[point[1]][point[0]]) in SOLID:
                    break
                covered.add(point)
    return covered


def _flood(rows, start, *, hops=True, avoid=frozenset()):
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
                if char in SOLID or char == "V" or point in avoid:
                    continue
                if point is land and _under(rows[step[1]][step[0]]) != "V":
                    continue
                found.add(point)
                queue.append(point)
    return found


def validate(rows: list[str]) -> None:
    assert len(rows) == HEIGHT and all(len(row) == WIDTH for row in rows)

    portal_step = (PORTAL[0], PORTAL[1] + 1)
    reach = _flood(rows, ARRIVAL)
    assert {ANCHOR, RETURN_EXIT, portal_step, *CIGARETTES} <= reach

    # The chaos must never make the Ashtray or the arrival unsafe, and a
    # clear route to the portal must exist: no police lane, and never
    # inside the dinosaur's notice.
    hazard = set(_lane_tiles(rows))
    hazard |= {
        (col, row)
        for row in range(HEIGHT) for col in range(WIDTH)
        if math.dist((col, row), DINOSAUR) <= DINOSAUR_NOTICE
    }
    assert ANCHOR not in hazard and ARRIVAL not in hazard
    clear = _flood(rows, ARRIVAL, avoid=hazard)
    assert portal_step in clear, "the portal cannot be reached safely"
    assert ANCHOR in clear

    # The dinosaur is over the prone businessperson, and both are in the
    # jungle rather than on the street.
    # Close enough that the animal is plainly over him.
    assert math.dist(DINOSAUR, PRONE) <= 3, math.dist(DINOSAUR, PRONE)
    for point in (DINOSAUR, PRONE, *RAPTORS):
        assert CHULT_PATCH[0] <= point[0] <= CHULT_PATCH[2], point
        assert CHULT_PATCH[1] <= point[1] <= CHULT_PATCH[3], point

    text = "".join(rows)
    # The phase document calls this the most visibly damaged *city* map,
    # and that is what is checked: more void than any of the street-block
    # maps. City Day 5 is deliberately excluded -- an overpass is three
    # quarters sky because it is a bridge, not because the city there is
    # more broken, so comparing against it would measure the wrong thing.
    density = text.count("V") / (WIDTH * HEIGHT)
    for name in ("modern_city_day_1", "modern_city_day_2",
                 "modern_city_day_3", "modern_city_day_4"):
        other = (ROOT / "assets" / "maps" / f"{name}.txt")
        lines = other.read_text(encoding="utf-8").splitlines()
        assert density > (sum(row.count("V") for row in lines)
                          / (len(lines) * len(lines[0]))), name

    assert text.count("ቴ") == 1 and text.count("ት") == 1
    assert text.count("ቶ") == 1, "exactly one massive dinosaur"
    assert text.count("ቷ") == 1, "exactly one prone businessperson"
    assert text.count("ቸ") == len(RAPTORS)
    assert text.count("ል") == len(CIGARETTES)
    assert "ም" not in text, "no homeless man in the daytime city"
    for material in ("#", "▱", "▤", "w", ".", ",", "=", "▦", "V",
                     "ᵹ", "ᵺ", "ᶂ"):
        assert material in text, material


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_day_6.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
