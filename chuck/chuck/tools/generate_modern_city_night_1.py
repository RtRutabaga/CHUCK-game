"""Generate the first explorable rainy-city map.

City Night 1 is deliberately quiet.  It establishes the region's scale,
cross-shaped street grammar, side alleys, scattered cigarettes, rain, and
visible Astral truncation before traffic, people, or enemies are introduced.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 72
HEIGHT = 54


def _paint_office(
    grid: list[list[str]], left: int, top: int, right: int, bottom: int,
) -> None:
    """Paint one large, indivisible three-quarter-view office mass."""
    facade_top = bottom - 8
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            if row < facade_top:
                char = "#"  # broad inaccessible roof plane
            elif row == facade_top:
                char = "▱"  # roof lip establishes the perspective break
            elif col in (left, right):
                char = "▥"  # darker side columns imply the building's depth
            elif row == bottom:
                char = "▤"
            else:
                char = "w" if (col - left + row) % 3 else "▤"
            grid[row][col] = char


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
        _paint_office(grid, *bounds)

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

    # Reality has visibly severed every route not yet authored.  These are
    # real Astral fall-hazard tiles, not decorative blockers or portals.
    for row in range(0, 3):
        for col in range(21, 51):
            grid[row][col] = "V"
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
    for col, row in ((23, 8), (48, 9), (29, 20), (44, 33)):
        grid[row][col] = "ል"

    return ["".join(row) for row in grid]


def main() -> None:
    output = ROOT / "assets" / "maps" / "modern_city_arrival.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
