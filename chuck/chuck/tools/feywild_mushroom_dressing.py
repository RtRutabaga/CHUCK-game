"""Shared authored mushroom dressing for the later Feywild maps."""

from pathlib import Path


MUSHROOM = "ŋ"

# Maps 1--4 already establish freestanding mushrooms. From the Giant Tea Table
# onward the distribution becomes denser, with six widely spaced silhouettes
# per map. Coordinates stay in broad pockets or replace already-solid hedge
# growth so this visual pass cannot close a route or alter a jump landing.
MUSHROOMS_BY_MAP: dict[str, tuple[tuple[int, int], ...]] = {
    "feywild_needle_garden": (
        (9, 3), (68, 45), (45, 17), (6, 17), (26, 11), (54, 40),
    ),
    "feywild_moonmoth_fen": (
        (25, 13), (50, 21), (12, 21), (36, 27), (32, 19), (20, 19),
    ),
    "feywild_redcap_warrens": (
        (19, 5), (72, 31), (33, 39), (3, 29), (58, 6), (43, 17),
    ),
    "feywild_shifting_hedge": (
        (6, 23), (11, 17), (25, 32), (15, 28), (22, 26), (18, 33),
    ),
    "feywild_displacer_meadow": (
        (29, 7), (70, 25), (3, 29), (40, 33), (53, 13), (16, 18),
    ),
    "feywild_mushroom_underways": (
        (5, 9), (66, 42), (47, 14), (37, 35), (21, 19), (32, 5),
    ),
    "feywild_luminous_rapids": (
        (56, 9), (3, 31), (74, 32), (31, 21), (12, 13), (55, 30),
    ),
    "feywild_twilight_crossroads": (
        (61, 10), (22, 43), (3, 11), (50, 35), (32, 19), (17, 26),
    ),
    "feywild_cloud_staircase": (
        (55, 19), (9, 36), (41, 37), (22, 20), (30, 30), (39, 21),
    ),
}


def dress_grid(map_name: str, grid: list[list[str]]) -> None:
    """Place this map's mushrooms without disturbing authored geometry."""
    for col, row in MUSHROOMS_BY_MAP[map_name]:
        current = grid[row][col]
        if current not in {".", "#", MUSHROOM}:
            raise ValueError(
                f"Mushroom at {(col, row)} overlaps {current!r} in {map_name}"
            )
        grid[row][col] = MUSHROOM


def update_authored_maps() -> None:
    """Apply the shared coordinates while preserving all other map cells."""
    maps_dir = Path(__file__).resolve().parents[1] / "assets" / "maps"
    for map_name in MUSHROOMS_BY_MAP:
        path = maps_dir / f"{map_name}.txt"
        lines = path.read_text(encoding="utf-8").splitlines()
        header = [line for line in lines if line.startswith(";")]
        grid = [list(line) for line in lines if not line.startswith(";")]
        dress_grid(map_name, grid)
        path.write_text(
            "\n".join(header + ["".join(row) for row in grid]) + "\n",
            encoding="utf-8",
        )
        print(
            f"Dressed {map_name} with "
            f"{len(MUSHROOMS_BY_MAP[map_name])} mushrooms"
        )


if __name__ == "__main__":
    update_authored_maps()
