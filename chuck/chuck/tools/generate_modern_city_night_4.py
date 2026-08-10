"""Generate City Night 4: the final ordinary rainy block before highway."""

from pathlib import Path

from generate_city_map_common import mark_roads, paint_office


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 84
HEIGHT = 60


def build_map() -> list[str]:
    grid = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # Unequal setbacks give this intersection a different silhouette while
    # preserving four broad, indivisible city-building footprints.
    for bounds in (
        (0, 0, 33, 20), (55, 0, 83, 20),
        (0, 39, 29, 59), (52, 37, 83, 59),
    ):
        paint_office(grid, *bounds)

    for row in range(HEIGHT):
        for col in range(WIDTH):
            vertical_road = 40 <= col <= 47
            horizontal_road = 27 <= row <= 32
            vertical_curb = col in (39, 48)
            horizontal_curb = row in (26, 33)
            vertical_walk = 34 <= col <= 53
            horizontal_walk = 21 <= row <= 38
            if vertical_road or horizontal_road:
                grid[row][col] = "="
            elif vertical_curb or horizontal_curb:
                if vertical_walk or horizontal_walk:
                    grid[row][col] = ","
            elif vertical_walk or horizontal_walk:
                grid[row][col] = "."

    for row in range(27, 33):
        for col in (35, 37):
            grid[row][col] = "▦"

    for row in range(0, 3):
        for col in range(34, 55):
            grid[row][col] = "V"
    for row in range(57, HEIGHT):
        for col in range(30, 53):
            grid[row][col] = "V"
    for row in range(21, 39):
        for col in range(0, 3):
            grid[row][col] = "V"
        for col in range(81, WIDTH):
            grid[row][col] = "V"

    # The western lower sidewalk now turns into the highway map. Its return
    # arrival remains one safe tile inside this five-tile opening.
    for row in range(34, 39):
        for col in range(0, 3):
            grid[row][col] = "⮜"
    grid[36][0] = "ሦ"
    grid[36][4] = "ሧ"

    # The only authored route is the southern return to City Night 3.
    for row in range(57, HEIGHT):
        for col in range(34, 39):
            grid[row][col] = "⮟"
    grid[59][36] = "ሥ"
    grid[55][36] = "ሣ"
    grid[51][36] = "ሤ"

    grid[24][17] = "ሕ"
    grid[35][64] = "ሕ"
    grid[24][71] = "ሖ"
    grid[35][20] = "ሗ"
    grid[24][67] = "ሗ"
    for col, row in ((36, 10), (51, 48), (9, 35), (76, 24)):
        grid[row][col] = "ል"
    grid[28][44] = "ሎ"
    grid[31][44] = "ሏ"
    mark_roads(grid)
    return ["".join(row) for row in grid]


def main() -> None:
    output = ROOT / "assets" / "maps" / "modern_city_night_4.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
