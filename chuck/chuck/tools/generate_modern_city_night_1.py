"""Generate the first explorable rainy-city map.

City Night 1 is deliberately quiet.  It establishes the region's scale,
cross-shaped street grammar, side alleys, scattered cigarettes, rain, and
visible Astral truncation before traffic, people, or enemies are introduced.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 56
HEIGHT = 36


def build_map() -> list[str]:
    grid = [["#" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # A broad boulevard crosses a narrower north/south street.  Sidewalks
    # remain generous enough for a one-foot rat to explore around the roads.
    for row in range(HEIGHT):
        for col in range(WIDTH):
            vertical_road = 25 <= col <= 32
            horizontal_road = 15 <= row <= 20
            vertical_curb = col in (24, 33)
            horizontal_curb = row in (14, 21)
            vertical_walk = 20 <= col <= 37
            horizontal_walk = 10 <= row <= 25

            if vertical_road or horizontal_road:
                grid[row][col] = "="
            elif vertical_curb or horizontal_curb:
                if vertical_walk or horizontal_walk:
                    grid[row][col] = ","
            elif vertical_walk or horizontal_walk:
                grid[row][col] = "."

    # Lit and unlit windows articulate the four building masses without
    # turning their walls into separate collision logic.
    for col in range(0, 20):
        if col % 3 != 1:
            grid[9][col] = "w"
            grid[26][col] = "w"
    for col in range(38, WIDTH):
        if col % 3 != 1:
            grid[9][col] = "w"
            grid[26][col] = "w"
    for row in range(0, 10):
        if row % 3 != 1:
            grid[row][19] = "w"
            grid[row][38] = "w"
    for row in range(26, HEIGHT):
        if row % 3 != 1:
            grid[row][19] = "w"
            grid[row][38] = "w"

    # Two optional pockets reward leaving the obvious cross street.
    for row in range(6, 9):
        for col in range(6, 21):
            grid[row][col] = "."
    for row in range(28, 34):
        for col in range(37, 51):
            grid[row][col] = "."

    # Reality has visibly severed every route not yet authored.  These are
    # real Astral fall-hazard tiles, not decorative blockers or portals.
    for row in range(0, 3):
        for col in range(20, 38):
            grid[row][col] = "V"
    for row in range(34, HEIGHT):
        for col in range(20, 38):
            grid[row][col] = "V"
    for row in range(10, 26):
        for col in range(0, 3):
            grid[row][col] = "V"
        for col in range(53, WIDTH):
            grid[row][col] = "V"

    # The Phase 10 landing hands control over at this southern sidewalk.
    # Its nearby Ashtray remains both the save point and death return point.
    grid[31][21] = "ላ"
    grid[28][21] = "ሌ"
    for col, row in ((10, 7), (36, 12), (45, 30), (7, 23)):
        grid[row][col] = "ል"

    return ["".join(row) for row in grid]


def main() -> None:
    output = ROOT / "assets" / "maps" / "modern_city_arrival.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
