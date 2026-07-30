"""Place reusable carton-filled temple urns across the Phlegethos maps.

These are the established floor urn marker (¢): ordinary basalt is drawn
beneath it, the shared BreakableUrn entity supplies terracotta art/shards,
and one scratch drops the existing 20-cigarette carton. Placements stay on
broad safe ground, away from required paths, lava hops, checkpoints, and the
fortress battle aisle.
"""

from pathlib import Path


MAPS = Path(__file__).resolve().parents[1] / "assets" / "maps"

PLACEMENTS = {
    "phlegethos_arrival": ((8, 12), (35, 17), (33, 25)),
    "phlegethos_road": ((12, 8), (40, 10), (6, 23)),
    "phlegethos_lake": ((6, 6), (37, 7), (7, 29), (37, 26)),
    "phlegethos_fortress_approach": (
        (6, 16), (41, 17), (7, 24), (40, 24),
    ),
}


def place(map_name: str, positions: tuple[tuple[int, int], ...]) -> None:
    path = MAPS / f"{map_name}.txt"
    lines = path.read_text(encoding="utf-8").splitlines()
    grid_indices = [
        index for index, line in enumerate(lines)
        if line and not line.startswith(";")
    ]
    grid = [list(lines[index]) for index in grid_indices]
    width = len(grid[0])
    assert all(len(row) == width for row in grid), map_name

    for col, row in positions:
        current = grid[row][col]
        assert current in {"·", "¢"}, (
            f"{map_name} urn at {(col, row)} must replace open basalt, "
            f"found {current!r}"
        )
        grid[row][col] = "¢"

    for index, row in zip(grid_indices, grid):
        lines[index] = "".join(row)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{map_name}: {len(positions)} breakable urns")


def main() -> None:
    for map_name, positions in PLACEMENTS.items():
        place(map_name, positions)


if __name__ == "__main__":
    main()
