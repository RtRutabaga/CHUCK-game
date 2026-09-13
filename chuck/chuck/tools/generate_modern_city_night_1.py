"""Generate the first explorable rainy-city map.

City Night 1 is deliberately quiet.  It establishes the region's scale,
cross-shaped street grammar, side alleys, scattered cigarettes, rain, and
visible Astral truncation before traffic, people, or enemies are introduced.
"""

from pathlib import Path

from generate_city_map_common import dress_street, furnish_street, mark_roads, paint_office


ROOT = Path(__file__).resolve().parents[1]
SEED = 83
WIDTH = 72
HEIGHT = 54


def build_map() -> list[str]:
    grid = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # Four genuine city-block buildings occupy most of the map. The unequal
    # setbacks create explorable sidewalk pockets without carving thin wall
    # remnants out of an office footprint.
    offices = (
        (0, 0, 20, 17), (51, 0, 71, 17),
        (0, 36, 24, 53), (47, 36, 71, 53),
    )
    for bounds in offices:
        paint_office(grid, *bounds)

    # A broad boulevard crosses a narrower north/south street.  Sidewalks
    # remain generous enough for a one-foot rat to explore around the roads.
    for row in range(HEIGHT):
        for col in range(WIDTH):
            vertical_road = 32 <= col <= 39
            horizontal_road = 24 <= row <= 29
            vertical_curb = col in (31, 40)
            horizontal_curb = row in (23, 30)
            vertical_walk = 26 <= col <= 45
            horizontal_walk = 18 <= row <= 35

            if vertical_road or horizontal_road:
                grid[row][col] = "="
            elif vertical_curb or horizontal_curb:
                if vertical_walk or horizontal_walk:
                    grid[row][col] = ","
            elif vertical_walk or horizontal_walk:
                grid[row][col] = "."

    # A worn zebra crossing aligns exactly with the southern sidewalk route,
    # telling the player where to pause and observe the two teaching lanes.
    for row in range(24, 30):
        for col in (27, 29):
            grid[row][col] = "▦"

    # Reality has visibly severed every route not yet authored.  These are
    # real Astral fall-hazard tiles, not decorative blockers or portals.
    for row in range(0, 3):
        for col in range(21, 51):
            grid[row][col] = "V"
    # The northern sidewalk now continues into City Night 2. A five-tile
    # opening reads like the same city street carrying on between blocks.
    for row in range(0, 3):
        for col in range(26, 31):
            grid[row][col] = "⮝"
    for row in range(51, HEIGHT):
        for col in range(25, 47):
            grid[row][col] = "V"
    for row in range(18, 36):
        for col in range(0, 3):
            grid[row][col] = "V"
        for col in range(69, WIDTH):
            grid[row][col] = "V"

    # The Phase 10 landing hands control over at this southern sidewalk.
    # Its nearby Ashtray remains both the save point and death return point.
    grid[47][27] = "ላ"
    grid[43][27] = "ሌ"
    grid[0][28] = "ሐ"
    grid[4][28] = "ሑ"
    for col, row in ((23, 8), (48, 9), (29, 20), (44, 33)):
        grid[row][col] = "ል"
    # Two opposed, widely spaced lanes teach observation and timing before
    # later maps increase the number and density of vehicles.
    grid[25][36] = "ሎ"
    grid[28][36] = "ሏ"

    # Street furniture last, so it can see the finished pavement
    # and refuse to stand anywhere that would close a route.
    dress_street(grid, seed=SEED)
    furnish_street(grid, seed=SEED, night=True)
    mark_roads(grid)
    return ["".join(row) for row in grid]


def main() -> None:
    output = ROOT / "assets" / "maps" / "modern_city_arrival.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
