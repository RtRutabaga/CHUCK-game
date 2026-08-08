"""Generate City Sewer 1: a long concrete utility-tunnel introduction."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 92
HEIGHT = 38


def build_map() -> list[str]:
    grid = [["#" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # A three-leg service route: north from the city stairs, east beside the
    # runoff, then south toward the still-collided continuation.
    for row in range(17, HEIGHT):
        for col in range(7, 16):
            grid[row][col] = "d"
    for row in range(15, 23):
        for col in range(7, 84):
            grid[row][col] = "d"
    for row in range(15, 36):
        for col in range(74, 84):
            grid[row][col] = "d"

    # Concrete slab walkway, wet patches, and a side drainage channel create
    # the modern maintenance-tunnel language without introducing sludge.
    for col in range(18, 71):
        grid[21][col] = ","
        grid[22][col] = ","
    for col in range(20, 68):
        grid[16][col] = "%"
    for col, row in ((10, 25), (14, 20), (31, 19), (46, 21),
                     (62, 18), (76, 24), (81, 30)):
        grid[row][col] = "M"

    # Brick repairs, exposed utility pipes, and regular artificial lights
    # replace Waterdeep's earthen medieval tunnel walls.
    for col in range(18, 70):
        grid[14][col] = "b" if (col // 8) % 2 == 0 else "R"
        grid[23][col] = "R" if (col // 9) % 2 == 0 else "b"
    for col in (20, 34, 48, 62, 76):
        grid[14][col] = "i"
    for row in (17, 27):
        grid[row][85] = "i"

    # Entry stairs remain open and reciprocal. The unauthored southern
    # continuation is visibly consumed by Astral terrain, not a fake exit.
    for row in range(35, HEIGHT):
        for col in range(9, 14):
            grid[row][col] = "⮟"
    grid[37][11] = "ሻ"
    grid[34][11] = "ሹ"
    grid[30][11] = "ሺ"
    for row in range(35, HEIGHT):
        for col in range(76, 81):
            grid[row][col] = "V"
    for row in range(31, 35):
        for col in range(76, 81):
            grid[row][col] = "ƻ"

    # The way on is a side culvert off the east leg. The southern end
    # stays collided and ruined -- that damage is scenery now, not a
    # placeholder, so the route turns rather than pushing through it.
    for row in range(29, 34):
        for col in range(84, WIDTH):
            grid[row][col] = "d"
    for col in range(84, WIDTH):
        grid[28][col] = "R" if (col // 4) % 2 == 0 else "b"
        grid[34][col] = "b" if (col // 5) % 2 == 0 else "R"
    grid[28][86] = "i"
    for row in range(30, 33):
        grid[row][WIDTH - 1] = "⮞"
    grid[31][WIDTH - 1] = "ሽ"
    grid[31][88] = "ቁ"    # where Sewer 2 sets Chuck back down

    # Aggressive rats are spaced into distinct pressure beats, never at the
    # entry Ashtray. Loose cigarettes reward inspecting the long turns.
    for col, row in ((27, 20), (42, 18), (56, 21), (75, 17), (80, 29)):
        grid[row][col] = "q"
    for col, row in ((14, 17), (49, 17), (82, 33)):
        grid[row][col] = "ል"
    return ["".join(row) for row in grid]


def main() -> None:
    output = ROOT / "assets" / "maps" / "modern_city_sewer_1.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
