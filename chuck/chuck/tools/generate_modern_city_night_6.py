"""Generate City Night 6: the final rainy block and sewer threshold."""

from pathlib import Path

from generate_city_map_common import dress_street, mark_roads, paint_office


ROOT = Path(__file__).resolve().parents[1]
SEED = 88
WIDTH = 88
HEIGHT = 60


def build_map() -> list[str]:
    grid = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for bounds in (
        (0, 0, 31, 19), (56, 0, 87, 19),
        (0, 40, 31, 59), (56, 40, 87, 59),
    ):
        paint_office(grid, *bounds)

    # Chuck enters from the east, crosses north/south traffic, then reaches
    # the tunnel mouth set into the northwest office's ground-level facade.
    for row in range(HEIGHT):
        for col in range(WIDTH):
            vertical_road = 42 <= col <= 49
            horizontal_road = 30 <= row <= 35
            vertical_curb = col in (41, 50)
            horizontal_curb = row in (29, 36)
            vertical_walk = 32 <= col <= 55
            horizontal_walk = 20 <= row <= 39
            if vertical_road or horizontal_road:
                grid[row][col] = "="
            elif vertical_curb or horizontal_curb:
                if vertical_walk or horizontal_walk:
                    grid[row][col] = ","
            elif vertical_walk or horizontal_walk:
                grid[row][col] = "."

    for row in (22, 24, 26):
        for col in range(42, 50):
            grid[row][col] = "▦"

    # Every non-route edge is visibly severed by shared Astral terrain.
    for row in range(0, 3):
        for col in range(32, 56):
            grid[row][col] = "V"
    for row in range(57, HEIGHT):
        for col in range(32, 56):
            grid[row][col] = "V"
    for row in range(20, 40):
        for col in range(0, 3):
            grid[row][col] = "V"
        for col in range(85, WIDTH):
            grid[row][col] = "V"

    # Sole map transition: the safe eastern return to the highway.
    for row in range(22, 27):
        for col in range(85, WIDTH):
            grid[row][col] = "⮞"
    grid[24][87] = "ሷ"
    grid[24][83] = "ስ"
    grid[24][80] = "ሶ"

    # An open manhole in the pavement, with the prompt on the approach
    # to it. It is out in the sidewalk rather than cut into the building
    # behind: a sewer is reached through the street, not through a wall.
    grid[22][20] = "ƺ"
    # The one-tile prompt sits directly at the lip, not out on the approach.
    grid[23][20] = "ሸ"
    grid[26][20] = "ሼ"

    grid[22][72] = "ሕ"
    grid[37][18] = "ሕ"
    grid[44][53] = "ሞ"
    grid[38][72] = "ሗ"
    for col, row in ((78, 26), (54, 22), (35, 38), (15, 22)):
        grid[row][col] = "ል"
    grid[12][44] = "ሟ"
    grid[48][47] = "ሠ"
    # Street furniture last, so it can see the finished pavement
    # and refuse to stand anywhere that would close a route.
    dress_street(grid, seed=SEED)
    mark_roads(grid)
    return ["".join(row) for row in grid]


def main() -> None:
    output = ROOT / "assets" / "maps" / "modern_city_night_6.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
