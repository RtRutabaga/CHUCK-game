"""Author Feywild 3: the safe slowing-pollen lesson."""

from collections import deque
from pathlib import Path


W, H = 62, 46
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_pollen_orchard.txt"
)

RETURN_EXIT = (6, 45)
ARRIVAL = (6, 44)
ANCHOR = (12, 43)
FLOWER = (43, 31)
OPEN_GATE = ((31, 27), (31, 28), (31, 29))
CLOSE_GATE = ((51, 27), (51, 28), (51, 29))
DEEPER_RETURN = (28, 1)
DEEPER = (28, 0)

POLLEN_BEDS = (
    # The first strip is only one tile deep in Chuck's direction of travel.
    ((14, 37), (15, 37), (16, 37)),
    ((30, 34), (30, 35), (30, 36)),
    ((51, 24), (52, 24), (53, 24)),
    ((38, 19), (38, 20), (38, 21)),
    ((23, 11), (23, 12), (23, 13)),
)

HEADER = [
    "; PHASE 9 - FEYWILD 3, THE POLLEN ORCHARD (62x46 tiles).",
    "; Enemy-free orchard lanes safely teach grounded slowing pollen.",
    "; Narrow beds can be cleared by Chuck's existing committed jump.",
    "; One reversible flower opens a direct optional route; Map 4 is inert.",
]


def _carve_segment(
    grid: list[list[str]],
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    char: str = "'",
) -> None:
    x0, y0 = start
    x1, y1 = end
    if x0 == x1:
        for row in range(min(y0, y1), max(y0, y1) + 1):
            for dx in (-1, 0, 1):
                grid[row][x0 + dx] = char
    elif y0 == y1:
        for col in range(min(x0, x1), max(x0, x1) + 1):
            for dy in (-1, 0, 1):
                grid[y0 + dy][col] = char
    else:
        raise ValueError("Pollen Orchard segments must remain cardinal")


def _carve_room(
    grid: list[list[str]],
    left: int,
    top: int,
    right: int,
    bottom: int,
) -> None:
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = "."


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    # A long, alternating orchard route creates five readable crossings.
    _carve_segment(grid, (6, H - 2), (15, H - 2))
    _carve_segment(grid, (15, H - 2), (15, 35))
    _carve_segment(grid, (15, 35), (45, 35))
    _carve_segment(grid, (45, 35), (45, 28))
    _carve_segment(grid, (45, 28), (52, 28))
    _carve_segment(grid, (52, 28), (52, 20))
    _carve_segment(grid, (52, 20), (18, 20))
    _carve_segment(grid, (18, 20), (18, 12))
    _carve_segment(grid, (18, 12), (28, 12))
    _carve_segment(grid, (28, 12), (28, 1))

    # The direct middle lane begins sealed. Its flower trades the eastern
    # detour for this shorter route while retaining complete connectivity.
    _carve_segment(grid, (18, 28), (45, 28))
    _carve_segment(grid, (18, 20), (18, 28))

    # Orchard clearings frame the flower and offer small reasons to wander.
    _carve_room(grid, 39, 29, 47, 34)
    _carve_room(grid, 7, 31, 13, 36)
    _carve_segment(grid, (12, 35), (9, 35))
    _carve_room(grid, 43, 15, 48, 20)
    _carve_room(grid, 23, 5, 31, 13)

    # Authored shallow pollen never shares a tile with another hazard.
    for bed in POLLEN_BEDS:
        for col, row in bed:
            if grid[row][col] == "#":
                raise ValueError(f"Pollen bed misses the path at {(col, row)}")
            grid[row][col] = "☼"

    # Repeated trunks make the winding lanes read as a deliberate orchard.
    for col, row in (
        (10, 39), (21, 33), (27, 38), (36, 32), (48, 34),
        (56, 25), (47, 23), (42, 17), (30, 23), (23, 17),
        (13, 16), (21, 9), (34, 9), (26, 3), (55, 12),
    ):
        if grid[row][col] == "#":
            grid[row][col] = "ł"
    for col, row in (
        (8, 33), (41, 33), (46, 17), (25, 8), (21, 19),
    ):
        if grid[row][col] == ".":
            grid[row][col] = "Ł"
    for col, row in (
        (11, 34), (44, 32), (45, 18), (28, 8), (20, 13),
    ):
        if grid[row][col] == ".":
            grid[row][col] = "ŋ"

    # A single optional grass reward sits off the first main bend.
    grid[33][9] = "<"

    for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2):
        grid[RETURN_EXIT[1]][col] = "⇩"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "Լ"
    grid[ANCHOR[1]][ANCHOR[0]] = "Ծ"
    grid[FLOWER[1]][FLOWER[0]] = "Ձ"
    for col, row in OPEN_GATE:
        grid[row][col] = "Ղ"
    for col, row in CLOSE_GATE:
        grid[row][col] = "Ճ"
    grid[DEEPER_RETURN[1]][DEEPER_RETURN[0]] = "Հ"
    for col in range(DEEPER[0] - 1, DEEPER[0] + 2):
        grid[DEEPER[1]][col] = "⇧"
    grid[DEEPER[1]][DEEPER[0]] = "Կ"
    return grid


def _under(char: str) -> str:
    return {
        "Լ": "'",
        "Ծ": "'",
        "Կ": "⇧",
        "Հ": "'",
        "Ձ": ".",
        "Ղ": "#",
        "Ճ": "'",
    }.get(char, char)


def _reachable(
    grid: list[list[str]],
    start: tuple[int, int],
    *,
    active: bool,
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
            if point in OPEN_GATE:
                char = "'" if active else "#"
            elif point in CLOSE_GATE:
                char = "#" if active else "'"
            if char in {"#", "ł", "Ł", "ŋ"}:
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def validate(grid: list[list[str]]) -> None:
    assert all(len(row) == W for row in grid)
    required = {RETURN_EXIT, ANCHOR, FLOWER, DEEPER, DEEPER_RETURN}
    for active in (False, True):
        reached = _reachable(grid, ARRIVAL, active=active)
        assert required <= reached
    assert all(_under(grid[row][col]) == "#" for col, row in OPEN_GATE)
    assert all(_under(grid[row][col]) == "'" for col, row in CLOSE_GATE)
    assert all(
        _under(grid[row][col]) == "☼"
        for bed in POLLEN_BEDS
        for col, row in bed
    )
    assert sum(row.count("☼") for row in grid) == 15
    assert sum(row.count("<") for row in grid) == 1
    assert all(
        grid[H - 1][col] == "⇩"
        for col in range(RETURN_EXIT[0] - 1, RETURN_EXIT[0] + 2)
    )
    assert all(
        grid[0][col] in {"⇧", "Կ"}
        for col in range(DEEPER[0] - 1, DEEPER[0] + 2)
    )
    map_text = "".join("".join(row) for row in grid)
    assert not any(
        marker in map_text for marker in ("(", ")", "¡", "¶", "Ѯ", "Ԟ")
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
