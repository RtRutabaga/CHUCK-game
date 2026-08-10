"""Generate City Night 5: the major staged highway crossing."""

from pathlib import Path

from generate_city_map_common import mark_roads, paint_office


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 112
HEIGHT = 48


def build_map() -> list[str]:
    grid = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # Four full office masses frame the pedestrian approaches. The enormous
    # central void is occupied by two highway carriageways, not tiny buildings.
    for bounds in (
        (0, 0, 23, 17), (88, 0, 111, 17),
        (0, 30, 23, 47), (88, 30, 111, 47),
    ):
        paint_office(grid, *bounds)

    # West/east sidewalks, two four-lane carriageways, and a ten-tile median.
    for row in range(HEIGHT):
        for col in range(24, 88):
            if 35 <= col <= 50 or 61 <= col <= 76:
                grid[row][col] = "="
            elif col in (34, 51, 60, 77):
                grid[row][col] = ","
            else:
                grid[row][col] = "."

    # A broad human-scale zebra route crosses both carriageways. Chuck can
    # wait between individual lanes and on the central median.
    for row in (22, 24, 26):
        for col in (*range(35, 51), *range(61, 77)):
            grid[row][col] = "▦"

    # The east/west pedestrian corridor splits the office pairs.
    for row in range(18, 30):
        for col in (*range(0, 24), *range(88, WIDTH)):
            grid[row][col] = "."
    for row in range(18, 30):
        for col in range(0, 3):
            grid[row][col] = "V"
        for col in range(109, WIDTH):
            grid[row][col] = "V"

    # The western approach now continues into the final night-city block.
    for row in range(22, 27):
        for col in range(0, 3):
            grid[row][col] = "⮜"
    grid[24][0] = "ሳ"
    grid[24][4] = "ሴ"

    # East returns to City Night 4 through the only currently authored edge.
    for row in range(22, 27):
        for col in range(109, WIDTH):
            grid[row][col] = "⮞"
    grid[24][111] = "ሪ"
    grid[24][107] = "ረ"
    grid[24][104] = "ሩ"

    # Two four-lane fields with alternating directions and staggered phases.
    for col, marker in (
        (37, "ራ"), (41, "ሬ"), (45, "ር"), (49, "ሮ"),
        (63, "ሯ"), (67, "ሰ"), (71, "ሱ"), (75, "ሲ"),
    ):
        grid[12][col] = marker

    # People stay on safe zones; one raccoon rewards reaching the far side
    # without mixing combat into the active highway itself.
    grid[21][101] = "ሕ"
    grid[26][17] = "ሕ"
    grid[27][56] = "ሖ"
    grid[21][12] = "ሗ"
    for col, row in ((99, 27), (82, 20), (56, 20), (29, 27), (8, 24)):
        grid[row][col] = "ል"
    mark_roads(grid)
    return ["".join(row) for row in grid]


def main() -> None:
    output = ROOT / "assets" / "maps" / "modern_city_night_5.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
