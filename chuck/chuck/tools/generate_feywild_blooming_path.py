"""Author Feywild 2: a safe introduction to reversible flower switches."""

from collections import deque
from pathlib import Path


W, H = 60, 42
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_blooming_path.txt"
)

ARRIVAL = (4, 33)
RETURN_EXIT = (2, 33)
ANCHOR = (10, 33)
FLOWER = (22, 25)
OPEN_GATE = ((27, 24), (27, 25), (27, 26))
CLOSE_GATE = ((27, 19), (27, 20), (27, 21))
DEEPER = (54, 9)
DEEPER_RETURN = (51, 9)

HEADER = [
    "; PHASE 9 - FEYWILD 2, THE BLOOMING PATH (60x42 tiles).",
    "; A quiet two-route clearing introduces one reversible flower switch.",
    "; Scratching the flower opens the lower vine gate and closes the upper.",
    "; One Ashtray serves the map; the deeper boundary remains inert.",
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
        raise ValueError("Blooming Path segments must remain cardinal")


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

    # Arrival lane and the broad flower clearing.
    _carve_segment(grid, RETURN_EXIT, (18, 33))
    _carve_segment(grid, (18, 33), (18, 25))
    _carve_room(grid, 15, 22, 25, 29)

    # Two routes join the same eastern clearing. The upper route begins open;
    # the direct lower route begins sealed by three authored vine targets.
    _carve_segment(grid, (18, 25), (18, 20))
    _carve_segment(grid, (18, 20), (36, 20))
    _carve_segment(grid, (36, 20), (36, 25))
    _carve_segment(grid, (24, 25), (45, 25))

    # The main path turns north and east to a stable later-phase boundary.
    _carve_segment(grid, (36, 25), (45, 25))
    _carve_segment(grid, (45, 25), (45, 9))
    _carve_segment(grid, (45, 9), DEEPER)

    # Optional upper pocket rewards inspection before or after toggling.
    _carve_segment(grid, (22, 20), (22, 16))
    _carve_segment(grid, (22, 16), (16, 16))
    _carve_room(grid, 13, 13, 18, 18)

    # Small secondary clearings keep the map exploratory without enemies.
    _carve_room(grid, 39, 29, 48, 35)
    _carve_segment(grid, (44, 25), (44, 29))
    _carve_room(grid, 48, 5, 56, 12)

    # Reintroduce an irregular dense silhouette around the authored route.
    # Runtime generation is never used; this deterministic pass writes the map.
    for row in range(2, H - 2):
        for col in range(2, W - 2):
            if grid[row][col] != "#":
                continue
            roll = (col * 37 + row * 71 + col * row * 11) % 23
            if roll == 0:
                # Tiny floor pockets soften the hedge edge but never connect
                # across its three-or-more-tile mass.
                neighbors = sum(
                    grid[row + dy][col + dx] != "#"
                    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
                )
                if neighbors >= 2:
                    grid[row][col] = "."

    # Standing silhouettes decorate only non-route cells.
    for col, row in (
        (8, 29), (13, 22), (30, 16), (39, 20), (51, 15),
        (35, 31), (52, 33), (11, 12), (31, 35),
    ):
        if grid[row][col] == "#":
            grid[row][col] = "ł"
    for col, row in (
        (14, 27), (20, 28), (40, 31), (50, 10), (42, 7),
    ):
        if grid[row][col] == ".":
            grid[row][col] = "Ł"
    for col, row in (
        (16, 14), (23, 23), (41, 33), (52, 7), (47, 19),
    ):
        if grid[row][col] == ".":
            grid[row][col] = "ŋ"

    # One optional cigarette-grass tuft sits in the upper side pocket.
    grid[15][15] = "<"

    # Metadata and switch targets. Marker under-terrain is authoritative.
    grid[RETURN_EXIT[1]][RETURN_EXIT[0]] = "←"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "Զ"
    grid[ANCHOR[1]][ANCHOR[0]] = "Է"
    grid[FLOWER[1]][FLOWER[0]] = "Թ"
    for col, row in OPEN_GATE:
        grid[row][col] = "Ժ"
    for col, row in CLOSE_GATE:
        grid[row][col] = "Ի"
    grid[DEEPER_RETURN[1]][DEEPER_RETURN[0]] = "Մ"
    grid[DEEPER[1]][DEEPER[0]] = "Ը"
    return grid


def _under(char: str) -> str:
    return {
        "Զ": "'",
        "Է": "'",
        "Ը": "'",
        "Թ": ".",
        "Ժ": "#",
        "Ի": "'",
        "Մ": "'",
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
    for active in (False, True):
        reached = _reachable(grid, ARRIVAL, active=active)
        assert ANCHOR in reached
        assert FLOWER in reached
        assert DEEPER in reached
        assert DEEPER_RETURN in reached
        assert RETURN_EXIT in reached
    assert all(_under(grid[row][col]) == "#" for col, row in OPEN_GATE)
    assert all(_under(grid[row][col]) == "'" for col, row in CLOSE_GATE)
    assert sum(row.count("<") for row in grid) == 1
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
