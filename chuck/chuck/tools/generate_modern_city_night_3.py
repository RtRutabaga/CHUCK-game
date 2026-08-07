"""Generate City Night 3: the quiet bottle-sidewalk encounter."""

from pathlib import Path

from generate_city_map_common import paint_office


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 80
HEIGHT = 56


def build_map() -> list[str]:
    grid = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # The same full city-block language frames a slightly wider intersection.
    for bounds in (
        (0, 0, 29, 18), (50, 0, 79, 18),
        (0, 37, 31, 55), (48, 37, 79, 55),
    ):
        paint_office(grid, *bounds)

    for row in range(HEIGHT):
        for col in range(WIDTH):
            vertical_road = 37 <= col <= 44
            horizontal_road = 24 <= row <= 29
            vertical_curb = col in (36, 45)
            horizontal_curb = row in (23, 30)
            vertical_walk = 31 <= col <= 50
            horizontal_walk = 19 <= row <= 36
            if vertical_road or horizontal_road:
                grid[row][col] = "="
            elif vertical_curb or horizontal_curb:
                if vertical_walk or horizontal_walk:
                    grid[row][col] = ","
            elif vertical_walk or horizontal_walk:
                grid[row][col] = "."

    # A horizontal zebra crossing teaches the same observation with traffic
    # now moving north/south rather than repeating the earlier lane direction.
    for col in range(37, 45):
        for row in (32, 34):
            grid[row][col] = "▦"

    for row in range(0, 3):
        for col in range(30, 50):
            grid[row][col] = "V"
    for row in range(53, HEIGHT):
        for col in range(32, 48):
            grid[row][col] = "V"
    for row in range(19, 37):
        for col in range(0, 3):
            grid[row][col] = "V"
        for col in range(77, WIDTH):
            grid[row][col] = "V"

    # West returns to Map 2. All other continuations remain visibly severed
    # until their destination maps actually exist.
    for row in range(31, 36):
        for col in range(0, 3):
            grid[row][col] = "⮜"
    grid[33][0] = "ሜ"
    grid[33][4] = "ሚ"
    grid[33][7] = "ማ"
    # One quiet human scene: seated on the broad lower sidewalk, with bottle
    # clusters large enough to make Chuck's scale obvious.
    grid[33][13] = "ም"
    grid[32][12] = "Ƀ"
    grid[34][15] = "Ƀ"

    grid[21][58] = "ሕ"
    grid[11][47] = "ሞ"
    # Both raccoons occupy optional sidewalk arms, never a mandatory gate.
    grid[21][20] = "ሗ"
    grid[33][69] = "ሗ"
    for col, row in ((33, 8), (46, 44), (65, 33), (26, 21)):
        grid[row][col] = "ል"

    grid[26][39] = "ሟ"
    grid[27][42] = "ሠ"
    return ["".join(row) for row in grid]


def main() -> None:
    output = ROOT / "assets" / "maps" / "modern_city_night_3.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
