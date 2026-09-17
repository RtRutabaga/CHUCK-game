"""Generate City Night 2: people, a raccoon, and another wet crossing."""

from pathlib import Path

from generate_city_map_common import dress_street, furnish_street, mark_roads, paint_office, seal_open_edges


ROOT = Path(__file__).resolve().parents[1]
SEED = 84
WIDTH = 76
HEIGHT = 56


def build_map() -> list[str]:
    grid = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # Four full-size buildings frame one connected city intersection. They
    # remain large masses instead of implausible strips of tiny offices.
    for bounds in (
        (0, 0, 27, 19), (48, 0, 75, 19),
        (0, 38, 27, 55), (48, 38, 75, 55),
    ):
        paint_office(grid, *bounds)

    for row in range(HEIGHT):
        for col in range(WIDTH):
            vertical_road = 34 <= col <= 41
            horizontal_road = 26 <= row <= 31
            vertical_curb = col in (33, 42)
            horizontal_curb = row in (25, 32)
            vertical_walk = 28 <= col <= 47
            horizontal_walk = 20 <= row <= 37
            if vertical_road or horizontal_road:
                grid[row][col] = "="
            elif vertical_curb or horizontal_curb:
                if vertical_walk or horizontal_walk:
                    grid[row][col] = ","
            elif vertical_walk or horizontal_walk:
                grid[row][col] = "."

    # Crosswalk on the western approach; traffic remains readable before
    # later Phase 11 maps turn the road into the main challenge.
    for row in range(26, 32):
        for col in (30, 32):
            grid[row][col] = "▦"

    # Every unauthored continuation ends visibly in the Astral Sea.
    for row in range(0, 3):
        for col in range(28, 48):
            grid[row][col] = "V"
    for row in range(53, HEIGHT):
        for col in range(28, 48):
            grid[row][col] = "V"
    for row in range(20, 38):
        for col in range(0, 3):
            grid[row][col] = "V"
        for col in range(73, WIDTH):
            grid[row][col] = "V"

    # The lower eastern sidewalk turns into City Night 3, breaking the
    # previous northbound rhythm. The named return sits one safe tile in.
    for row in range(33, 38):
        for col in range(73, WIDTH):
            grid[row][col] = "⮞"
    grid[35][75] = "መ"
    grid[35][71] = "ሙ"

    # South returns to City Night 1 through the same five-tile street mouth.
    for row in range(53, HEIGHT):
        for col in range(28, 33):
            grid[row][col] = "⮟"
    grid[55][30] = "ሔ"
    grid[51][30] = "ሒ"

    # Ordinary city life: two people lingering, one pacing a long sidewalk.
    grid[22][13] = "ሕ"
    grid[35][56] = "ሕ"
    grid[35][65] = "ሖ"
    # A single optional-sidewalk raccoon introduces the city's first enemy.
    grid[22][63] = "ሗ"

    for col, row in ((30, 10), (45, 44), (8, 22), (67, 35)):
        grid[row][col] = "ል"
    grid[27][38] = "ሎ"
    grid[30][38] = "ሏ"
    # Street furniture last, so it can see the finished pavement
    # and refuse to stand anywhere that would close a route.
    dress_street(grid, seed=SEED)
    furnish_street(grid, seed=SEED, night=True)
    mark_roads(grid)
    seal_open_edges(grid, "modern_city_night_2")
    return ["".join(row) for row in grid]


def main() -> None:
    output = ROOT / "assets" / "maps" / "modern_city_night_2.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
