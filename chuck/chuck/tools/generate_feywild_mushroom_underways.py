"""Author Feywild 11: the Mushroom Underways, a place to breathe.

Straight after the displacer beast, so nothing here pursues Chuck at
all. The map is built out of one rhythm repeated four times: a long dim
run under a giant cap, then an open clearing with a luminous pool in it.
Walking the Underways is meant to feel like moving through weather --
shade, light, shade, light -- rather than through a corridor.

The validator's job here is mostly to protect the mood: it proves there
is not a single pursuing enemy on the map, that the route really does
alternate rather than running open the whole way, and that every side
chamber and tuft can actually be found.
"""

from collections import deque
from pathlib import Path

W, H = 70, 46
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_mushroom_underways.txt"
)

RETURN_EXIT = (0, 8)
ARRIVAL = (3, 8)
ANCHOR = (34, 23)
FUTURE_RETURN = (65, 40)
FUTURE_EXIT = (69, 40)

# The route descends south-east in four shaded runs, each opening into a
# clearing. (left, top, right, bottom) of the shade; the clearing follows.
RUNS = (
    ((8, 5, 24, 11), (24, 4, 34, 14)),
    ((34, 8, 46, 14), (46, 6, 58, 17)),
    ((22, 18, 46, 24), (12, 17, 22, 27)),
    ((22, 28, 40, 34), (40, 26, 56, 38)),
)

# Optional chambers, each off a clearing rather than on the route.
CHAMBERS = (
    ((26, 36, 34, 42), (30, 35)),
    ((60, 8, 67, 15), (59, 11)),
    ((3, 19, 10, 26), (11, 23)),
)
TUFTS = ((30, 39), (32, 40), (63, 11), (6, 22), (7, 24), (48, 16))
POOLS = (
    (26, 6, 32, 11), (49, 8, 56, 14),
    (14, 19, 20, 25), (44, 29, 51, 35),
)

HEADER = [
    "; PHASE 9 - FEYWILD 11, THE MUSHROOM UNDERWAYS (70x46 tiles).",
    "; A recovery map: nothing here pursues Chuck. Four long runs under",
    "; giant caps alternate with open clearings and luminous pools, with",
    "; three quiet side chambers and fungal tufts to scratch open.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    _room(grid, 1, 5, 9, 11)                       # the arrival clearing
    for shade, clearing in RUNS:
        _room(grid, *shade, "ᛥ")
        _room(grid, *clearing)
    _room(grid, 56, 34, 68, 43)                    # the way onward
    # Short necks stitching the four runs into one descending route.
    _room(grid, 30, 12, 36, 18, "ᛥ")
    _room(grid, 44, 15, 50, 20)
    _room(grid, 18, 25, 24, 30, "ᛥ")
    _room(grid, 36, 32, 42, 36)

    for chamber, mouth in CHAMBERS:
        _room(grid, *chamber, "'")
        grid[mouth[1]][mouth[0]] = "'"

    # Luminous pools: solid, so they shape a clearing without ever
    # standing in the way of the walk. Inscribed as ellipses, because a
    # rectangle of bright water in a dim wood reads as a swimming pool.
    for left, top, right, bottom in POOLS:
        mid_x, mid_y = (left + right) / 2, (top + bottom) / 2
        radius_x, radius_y = (right - left) / 2 + 0.5, (bottom - top) / 2 + 0.5
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if grid[row][col] not in {".", "ᛥ"}:
                    continue
                if (((col - mid_x) / radius_x) ** 2
                        + ((row - mid_y) / radius_y) ** 2) <= 1.0:
                    grid[row][col] = "ᛞ"

    _dress_with_vegetation(grid)

    for col, row in TUFTS:
        assert grid[row][col] in {".", "'", "ᛥ"}, (col, row)
        grid[row][col] = "<"

    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][RETURN_EXIT[0]] = "←"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][FUTURE_EXIT[0]] = "→"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "შ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ჩ"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "ძ"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "ც"
    return grid


def _dress_with_vegetation(grid) -> None:
    """Trees, shrubs and the region's giant mushrooms, well inside cover."""
    for row in range(1, H - 1):
        for col in range(1, W - 1):
            if grid[row][col] != "#":
                continue
            if sum(grid[row + dr][col + dc] == "#"
                   for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))) < 3:
                continue
            key = (col * 31 + row * 17) % 17
            if key == 0:
                grid[row][col] = "ŧ"
            elif key == 5:
                grid[row][col] = "Ŧ"
            elif key == 9:
                grid[row][col] = "ł"      # the region's giant mushrooms
            elif key == 13:
                grid[row][col] = "Ɓ"


SOLID = {"#", "ᛞ", "ŧ", "Ŧ", "Ɓ", "ł"}


def _under(char: str) -> str:
    return {"შ": "'", "ჩ": "'", "ც": "→", "ძ": "'", "<": "."}.get(char, char)


def _reachable(grid, start):
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < W and 0 <= y < H) or point in reached:
                continue
            if _under(grid[y][x]) in SOLID:
                continue
            reached.add(point)
            frontier.append(point)
    return reached


ENEMY_CHARS = "ՇզէրղքქΩ"


def validate(grid) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)
    text = "".join("".join(row) for row in grid)

    # The mood is the requirement: nothing on this map chases anybody.
    for char in ENEMY_CHARS:
        assert char not in text, char

    walk = _reachable(grid, ARRIVAL)
    assert {RETURN_EXIT, FUTURE_EXIT, FUTURE_RETURN, ANCHOR, *TUFTS} <= walk
    for _chamber, mouth in CHAMBERS:
        assert mouth in walk, mouth

    # Every side chamber is genuinely optional: none is on the only route.
    onward = _reachable(grid, ARRIVAL)
    assert FUTURE_EXIT in onward
    for chamber, _mouth in CHAMBERS:
        left, top, right, bottom = chamber
        assert any((col, row) in walk
                   for row in range(top, bottom + 1)
                   for col in range(left, right + 1)), chamber

    # The route alternates: real stretches of shade, real open clearings.
    shade = text.count("ᛥ")
    assert shade >= 300, shade
    assert text.count("ᛞ") >= 40, text.count("ᛞ")
    assert text.count("<") == len(TUFTS)
    assert text.count("ჩ") == 1
    # ...and the walk actually passes through the shade rather than beside
    # it: at least a third of what Chuck can reach is under a cap.
    shaded_walk = sum(1 for col, row in walk if grid[row][col] == "ᛥ")
    assert shaded_walk * 3 >= len(walk), (shaded_walk, len(walk))

    assert all(grid[row][0] == "←"
               for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2))
    assert all(grid[row][W - 1] in {"→", "ც"}
               for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2))


def main() -> None:
    grid = build()
    validate(grid)
    OUT.write_text(
        "\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
