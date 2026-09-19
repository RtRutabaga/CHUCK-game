"""Dress the Feywild's root walls so they read as roots.

Two passes over every root wall, both solid-for-solid so neither can
change a route:

* Where a root wall stops above open ground, its bottom row becomes the
  wall's front face: the roots curl over and hang in tips into the
  shadow under the mass, which is what makes the wall a thing standing
  on the floor rather than a brown shape cut out of it.
* Along runs of wall, here and there, a knot: a boss where several
  roots have grown round each other, so a long wall has places in it
  instead of one texture all the way along.

Applied from each map's generator and straight into the shipped maps,
like the mushrooms and the great trees -- several of these maps carry
dressing their generators do not reproduce.
"""

from pathlib import Path


ROOT_WALL = "※"
ROOT_FACE = "ፒ"
ROOT_KNOT = "ፓ"          # a knot on ordinary wall
ROOT_KNOT_FACE = "ፔ"     # a knot on the wall's front face
ROOT_FAMILY = (ROOT_WALL, ROOT_FACE, ROOT_KNOT, ROOT_KNOT_FACE)

ROOT_MAPS = (
    "feywild_rootways",
    "feywild_redcap_warrens",
    "feywild_displacer_meadow",
    "feywild_twilight_crossroads",
)

# Knots sit at least this far apart, and on roughly one eligible tile in
# three of those that are far enough apart: a knot every few tiles is a
# pattern again.
KNOT_SPACING = 6


def _hash(col: int, row: int) -> int:
    value = (col * 374761393 + row * 668265263) & 0xFFFFFFFF
    value = (value ^ (value >> 13)) * 1274126177 & 0xFFFFFFFF
    return value ^ (value >> 16)


def dress_grid(map_name: str, grid: list[list[str]]) -> dict[str, int]:
    if map_name not in ROOT_MAPS:
        return {"faces": 0, "knots": 0}
    height, width = len(grid), len(grid[0])

    def rooty(col, row):
        return 0 <= row < height and 0 <= col < width \
            and grid[row][col] in ROOT_FAMILY

    faces = 0
    for row in range(height):
        for col in range(width):
            if grid[row][col] == ROOT_WALL and not rooty(col, row + 1):
                grid[row][col] = ROOT_FACE
                faces += 1

    placed: list[tuple[int, int]] = []
    for row in range(height):
        for col in range(width):
            if grid[row][col] not in (ROOT_WALL, ROOT_FACE):
                continue
            # A run of wall either side, so the knot's overhang lands on
            # roots and not on the floor.
            if not (rooty(col - 1, row) and rooty(col + 1, row)):
                continue
            if any(max(abs(col - c), abs(row - r)) < KNOT_SPACING
                   for c, r in placed):
                continue
            if _hash(col, row) % 3:
                continue
            grid[row][col] = (ROOT_KNOT if grid[row][col] == ROOT_WALL
                              else ROOT_KNOT_FACE)
            placed.append((col, row))
    return {"faces": faces, "knots": len(placed)}


def update_authored_maps() -> None:
    maps_dir = Path(__file__).resolve().parents[1] / "assets" / "maps"
    for map_name in ROOT_MAPS:
        path = maps_dir / f"{map_name}.txt"
        lines = path.read_text(encoding="utf-8").splitlines()
        header = [line for line in lines if line.startswith(";")]
        grid = [list(line) for line in lines if not line.startswith(";")]
        counts = dress_grid(map_name, grid)
        path.write_text(
            "\n".join(header + ["".join(row) for row in grid]) + "\n",
            encoding="utf-8",
        )
        print(f"Dressed the root walls on {map_name}: {counts}")


if __name__ == "__main__":
    update_authored_maps()
