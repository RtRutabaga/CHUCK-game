"""Author Feywild 6: the spitting-orchid Needle Garden."""

from collections import deque
from pathlib import Path

try:
    from tools.feywild_mushroom_dressing import dress_grid
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_mushroom_dressing import dress_grid
try:
    from tools.feywild_great_tree_dressing import (
        dress_grid as plant_great_tree,
    )
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_great_tree_dressing import dress_grid as plant_great_tree


W, H = 72, 50
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_needle_garden.txt"
)

RETURN_EXIT = (10, 0)
ARRIVAL = (10, 1)
ANCHOR = (16, 6)
FUTURE_RETURN = (70, 43)
FUTURE_EXIT = (71, 43)

ORCHIDS = (
    (5, 14, "Ց", "right"),
    (58, 25, "Ր", "left"),
    (20, 34, "Ց", "right"),
    (44, 32, "Վ", "down"),
)
POLLEN = ((40, 39), (41, 39), (42, 39))

HEADER = [
    "; PHASE 9 - FEYWILD 6, THE NEEDLE GARDEN (72x50 tiles).",
    "; Rooted orchids telegraph and fire along authored cardinal lanes.",
    "; A pollen side path bypasses the densest crossing after the safe lesson.",
    "; One physical Ashtray is outside every firing lane; Map 7 is inert.",
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


def _segment(
    grid: list[list[str]],
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    half_width: int = 1,
) -> None:
    x0, y0 = start
    x1, y1 = end
    if x0 == x1:
        for row in range(min(y0, y1), max(y0, y1) + 1):
            for dx in range(-half_width, half_width + 1):
                grid[row][x0 + dx] = "."
    elif y0 == y1:
        for col in range(min(x0, x1), max(x0, x1) + 1):
            for dy in range(-half_width, half_width + 1):
                grid[y0 + dy][col] = "."
    else:
        raise ValueError("Needle Garden paths remain cardinal")


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    # Quiet arrival and checkpoint garden. The first visible orchid waits
    # below a broad approach with ample room to watch its swelling petals.
    _segment(grid, (RETURN_EXIT[0], 0), (RETURN_EXIT[0], 11), half_width=2)
    _room(grid, 5, 2, 22, 10)
    _room(grid, 5, 10, 60, 18)

    # The route turns east after crossing the first broad horizontal shot,
    # then enters a narrower, three-tile lane fired from the right.
    _segment(grid, (54, 16), (54, 25), half_width=2)
    _segment(grid, (23, 25), (58, 25))
    _room(grid, 20, 22, 27, 28)
    _room(grid, 54, 22, 60, 28)

    # The late crossing combines a horizontal orchid with one vertical shot.
    # A lower side route bypasses that intersection, trading pressure for the
    # already-understood slowing pollen terrain.
    _segment(grid, (24, 25), (24, 34))
    _segment(grid, (21, 34), (58, 34))
    _segment(grid, (34, 34), (34, 39))
    _segment(grid, (34, 39), (56, 39))
    _segment(grid, (56, 34), (56, 43))
    _room(grid, 52, 39, 70, 46)

    # Solid flowering beds distinguish the authored lanes from ordinary
    # forest edges without adding another terrain mechanic.
    for left, top, right, bottom in (
        (7, 12, 18, 13),
        (25, 19, 47, 21),
        (29, 27, 50, 29),
        (7, 31, 19, 37),
        (36, 36, 51, 37),
        (61, 10, 66, 31),
        (6, 40, 27, 45),
    ):
        _room(grid, left, top, right, bottom, "✿")

    # Orchids root in their own solid beds. The blocker immediately below the
    # vertical crossing stops its seeds before the optional pollen bypass.
    grid[36][44] = "✿"
    for col, row, marker, _direction in ORCHIDS:
        grid[row][col] = marker

    for col, row in POLLEN:
        if grid[row][col] != ".":
            raise ValueError(f"Pollen misses bypass at {(col, row)}")
        grid[row][col] = "☼"

    # Small rewards pull Chuck into safe observation pockets rather than into
    # projectile lanes.
    for col, row in ((23, 23), (65, 45)):
        grid[row][col] = "<"

    # Chult-style openings sit on true outer edges.
    for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2):
        grid[0][col] = "⇧"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "Ւ"
    grid[ANCHOR[1]][ANCHOR[0]] = "Փ"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "Օ"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][W - 1] = "→"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "Ք"
    dress_grid("feywild_needle_garden", grid)
    plant_great_tree("feywild_needle_garden", grid)
    return grid


def _under(char: str) -> str:
    return {
        "Վ": "✿", "Տ": "✿", "Ր": "✿", "Ց": "✿",
        "Ւ": ".", "Փ": ".", "Ք": "→", "Օ": ".",
        "<": ".",
    }.get(char, char)


def _reachable(
    grid: list[list[str]], start: tuple[int, int],
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
            if _under(grid[y][x]) in {"#", "✿", "ŋ"}:
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def _ray(
    grid: list[list[str]], start: tuple[int, int], direction: str,
) -> list[tuple[int, int]]:
    vectors = {
        "up": (0, -1), "down": (0, 1),
        "left": (-1, 0), "right": (1, 0),
    }
    dx, dy = vectors[direction]
    col, row = start
    cells = []
    while True:
        col += dx
        row += dy
        if not (0 <= col < W and 0 <= row < H):
            break
        if _under(grid[row][col]) in {"#", "✿", "ŋ"}:
            break
        cells.append((col, row))
    return cells


def validate(grid: list[list[str]]) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)
    reached = _reachable(grid, ARRIVAL)
    assert {RETURN_EXIT, ANCHOR, FUTURE_RETURN, FUTURE_EXIT} <= reached
    assert all(position in reached for position in POLLEN)
    rays = [
        _ray(grid, (col, row), direction)
        for col, row, _marker, direction in ORCHIDS
    ]
    assert min(map(len, rays[:3])) >= 8
    assert len(rays[3]) == 3  # crossing shot stops before the bypass
    assert ANCHOR not in {cell for ray in rays for cell in ray}
    assert all(cell not in POLLEN for cell in rays[:2])
    assert len({(col + row * 3) % 4
                for col, row, _marker, _direction in ORCHIDS}) == len(ORCHIDS)
    text = "".join("".join(row) for row in grid)
    assert text.count("Փ") == 1
    assert text.count("☼") == 3
    assert text.count("<") == 2
    assert all(grid[0][col] == "⇧" for col in range(9, 12))
    assert all(
        grid[row][W - 1] in {"→", "Ք"} for row in range(42, 45)
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
