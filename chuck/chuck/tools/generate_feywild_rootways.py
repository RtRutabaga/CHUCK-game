"""Author Feywild 4: broad root-divided pursuit grounds and safe ratways."""

from collections import deque
from pathlib import Path

try:
    from tools.feywild_great_tree_dressing import (
        dress_grid as plant_great_tree,
    )
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_great_tree_dressing import dress_grid as plant_great_tree
try:
    from tools.feywild_root_dressing import dress_grid as dress_root_walls
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_root_dressing import dress_grid as dress_root_walls


W, H = 68, 46
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_rootways.txt"
)

RETURN_EXIT = (0, 40)
ARRIVAL = (1, 40)
ANCHOR = (11, 41)
FUTURE_RETURN = (66, 18)
FUTURE_EXIT = (67, 18)
REDCAPS = ((28, 28), (52, 17))
REFUGE_DOOR = (27, 35)
CACHE_DOOR = (49, 30)
CACHE = (53, 30)

HEADER = [
    "; PHASE 9 - FEYWILD 4, THE ROOTWAYS (68x46 tiles).",
    "; Two redcaps pressure the exposed route but stop at low root gaps.",
    "; One refuge and one optional cigarette cache belong to Chuck alone.",
    "; The eastern Map 5 boundary remains inert until its authored session.",
]


def _room(
    grid: list[list[str]],
    left: int,
    top: int,
    right: int,
    bottom: int,
    char: str = ".",
) -> None:
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _root_box(
    grid: list[list[str]],
    left: int,
    top: int,
    right: int,
    bottom: int,
    door: tuple[int, int],
) -> None:
    for col in range(left, right + 1):
        grid[top][col] = "※"
        grid[bottom][col] = "※"
    for row in range(top, bottom + 1):
        grid[row][left] = "※"
        grid[row][right] = "※"
    _room(grid, left + 1, top + 1, right - 1, bottom - 1, "'")
    grid[door[1]][door[0]] = "≀"


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    # A broad path changes direction twice, giving the two pursuits room to
    # breathe without becoming a corridor or a combat gate.
    _room(grid, 1, 35, 20, 44)
    _room(grid, 16, 27, 39, 42)
    _room(grid, 34, 19, 50, 31)
    _room(grid, 44, 11, 66, 32)
    _room(grid, 61, 16, 67, 21, "'")

    # Knotted root masses divide the open floor and force a gentle meander.
    for left, top, right, bottom in (
        (20, 27, 25, 32),
        (20, 39, 25, 42),
        (31, 27, 36, 31),
        (36, 35, 39, 42),
        (40, 19, 45, 23),
        (44, 28, 47, 32),
        (57, 11, 61, 16),
        (58, 24, 64, 29),
    ):
        _room(grid, left, top, right, bottom, "※")

    # A visible refuge teaches the scale escape during the first pursuit.
    _root_box(grid, 27, 32, 34, 39, REFUGE_DOOR)
    # The optional grass cache is completely sealed except for its low arch.
    _root_box(grid, 49, 26, 57, 35, CACHE_DOOR)
    grid[CACHE[1]][CACHE[0]] = "<"

    # Small enchanted landmarks keep the broad terrain authored and legible.
    for col, row, char in (
        (8, 37, "Ł"), (15, 43, "ŋ"), (18, 29, "ł"),
        (29, 29, "ŋ"), (38, 22, "Ł"), (46, 14, "ł"),
        (60, 21, "ŋ"), (64, 13, "Ł"),
    ):
        if grid[row][col] == ".":
            grid[row][col] = char

    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][RETURN_EXIT[0]] = "←"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "Յ"
    grid[ANCHOR[1]][ANCHOR[0]] = "Ն"
    for col, row in REDCAPS:
        grid[row][col] = "Շ"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "Չ"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][FUTURE_EXIT[0]] = "→"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "Ո"
    dress_root_walls("feywild_rootways", grid)
    plant_great_tree("feywild_rootways", grid)
    return grid


def _under(char: str) -> str:
    return {
        "Յ": "'", "Ն": "'", "Շ": ".", "Ո": "→", "Չ": "'",
        "<": ".",
    }.get(char, char)


def _reachable(
    grid: list[list[str]],
    start: tuple[int, int],
    *,
    large_actor: bool = False,
) -> set[tuple[int, int]]:
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            x, y = point
            if not (0 <= x < W and 0 <= y < H) or point in reached:
                continue
            char = _under(grid[y][x])
            if char in {"#", "※", "ፒ", "ፓ", "ፔ", "ł", "Ł", "ŋ"}:
                continue
            if large_actor and char == "≀":
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def validate(grid: list[list[str]]) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)
    chuck_reach = _reachable(grid, ARRIVAL)
    assert {
        RETURN_EXIT, ANCHOR, FUTURE_RETURN, FUTURE_EXIT,
        REFUGE_DOOR, CACHE_DOOR, CACHE, *REDCAPS,
    } <= chuck_reach
    large_reach = _reachable(grid, ARRIVAL, large_actor=True)
    assert CACHE not in large_reach
    assert (30, 35) not in large_reach
    text = "".join("".join(row) for row in grid)
    assert text.count("Ն") == 1
    assert text.count("Շ") == 2
    assert text.count("≀") == 2
    assert text.count("<") == 1
    assert all(
        grid[row][0] == "←"
        for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2)
    )
    assert all(
        grid[row][W - 1] in {"→", "Ո"}
        for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2)
    )


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
