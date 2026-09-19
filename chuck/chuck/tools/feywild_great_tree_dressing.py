"""Where the Feywild's great trees stand.

One per map, on the maps with room for one. A tree this size is a
landmark -- the thing a player says "past the big tree" about -- and two
on the same map stop being that and start being a wood.

The spots were chosen by measuring rather than by eye, against four
rules, and the suite checks the shipped maps against the same four:

* the trunk's three-by-two footprint is plain Feywild ground;
* there is open ground all round it, so the roots have somewhere to go
  and Chuck can walk the whole way round;
* nothing that matters stands under the crown -- no enemy, arrival,
  marker, breakable or exit -- because even see-through, a crown this
  big is where a player would lose sight of the thing they need;
* setting the footprint solid cuts nothing off.

The anchor is the middle of the footprint's bottom row: the prop is
drawn up from there, eleven tiles across and fourteen tall, and the
other five tiles of the footprint are solid ground with nothing drawn on
them because the trunk covers them.

Applied the same two ways as the mushroom dressing: from each map's
generator, and to the shipped files directly by ``update_authored_maps``
-- the second because several of the earliest Feywild maps carry
vegetation their generators do not reproduce, and regenerating one of
them to plant a tree would cut down every other tree on it.
"""

from pathlib import Path


GREAT_TREE = "ፐ"          # the anchor, with the sprite drawn up from it
GREAT_TREE_ROOTS = "ፑ"    # the rest of the trunk's footprint: solid ground

GREAT_TREES_BY_MAP: dict[str, tuple[int, int]] = {
    "feywild_rootways": (15, 38),
    "feywild_needle_garden": (23, 16),
    "feywild_redcap_warrens": (67, 25),
    "feywild_displacer_meadow": (64, 26),
    "feywild_mushroom_underways": (60, 41),
    "feywild_luminous_rapids": (8, 30),
    "feywild_twilight_crossroads": (60, 37),
    "feywild_cloud_staircase": (46, 36),
}


def footprint(col: int, row: int) -> list[tuple[int, int]]:
    """The six solid tiles under the trunk, anchor last."""
    cells = [(col + dcol, row + drow) for drow in (-1, 0)
             for dcol in (-1, 0, 1)]
    cells.remove((col, row))
    return cells + [(col, row)]


def dress_grid(map_name: str, grid: list[list[str]]) -> None:
    """Plant this map's great tree, if it has one."""
    spot = GREAT_TREES_BY_MAP.get(map_name)
    if spot is None:
        return
    col, row = spot
    for x, y in footprint(col, row):
        current = grid[y][x]
        if current not in {".", GREAT_TREE, GREAT_TREE_ROOTS}:
            raise ValueError(
                f"Great tree at {(col, row)} overlaps {current!r} at "
                f"{(x, y)} in {map_name}"
            )
        grid[y][x] = GREAT_TREE_ROOTS
    grid[row][col] = GREAT_TREE


def update_authored_maps() -> None:
    """Plant the trees in the shipped maps, leaving every other cell alone."""
    maps_dir = Path(__file__).resolve().parents[1] / "assets" / "maps"
    for map_name in GREAT_TREES_BY_MAP:
        path = maps_dir / f"{map_name}.txt"
        lines = path.read_text(encoding="utf-8").splitlines()
        header = [line for line in lines if line.startswith(";")]
        grid = [list(line) for line in lines if not line.startswith(";")]
        dress_grid(map_name, grid)
        path.write_text(
            "\n".join(header + ["".join(row) for row in grid]) + "\n",
            encoding="utf-8",
        )
        print(f"Planted a great tree on {map_name}")


if __name__ == "__main__":
    update_authored_maps()
