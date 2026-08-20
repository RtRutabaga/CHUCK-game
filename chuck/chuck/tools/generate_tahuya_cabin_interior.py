"""Generate the authored 21x33 Cabin interior map."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 21
HEIGHT = 33


def _solid_rect(grid, left, top, right, bottom, char="∎"):
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            grid[y][x] = char


def build_map():
    # The 21x33 interior exactly matches the exterior shell's authored
    # footprint.  Warm olive carpet fills the living/dining space.
    grid = [["Ŀ" for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for x in range(WIDTH):
        grid[0][x] = "ć"
        grid[HEIGHT - 1][x] = "ć"
    for y in range(HEIGHT):
        grid[y][0] = "ć"
        grid[y][WIDTH - 1] = "ć"

    # Reversible north/back and south/front thresholds.  Their arrivals sit
    # two cells in, preventing an immediate transition bounce.
    grid[0][10] = "Ƣ"
    grid[2][10] = "ኅ"
    grid[32][10] = "Ɯ"
    grid[30][10] = "ኄ"

    # The two couches flank the back doorway exactly as on Sean's plan.
    _solid_rect(grid, 1, 3, 8, 5)
    grid[5][5] = "Ƈ"
    grid[4][5] = "₁"
    _solid_rect(grid, 13, 3, 19, 5)
    grid[5][16] = "Ƭ"
    grid[4][16] = "₂"

    # Central dining table and five stools; the east wall keeps its paired
    # mustard chairs, both at human scale relative to Chuck.
    _solid_rect(grid, 6, 12, 12, 15)
    grid[15][9] = "Ƒ"
    _solid_rect(grid, 16, 9, 18, 11)
    grid[11][17] = "ƭ"
    grid[10][17] = "₃"
    _solid_rect(grid, 16, 14, 18, 16)
    grid[16][17] = "ƭ"
    grid[15][17] = "₄"

    # The southern kitchen switches to the photographed patterned linoleum.
    # Its long cabinet includes the sink and the ordinary rectangular D&D map.
    for y in range(22, 31):
        for x in range(1, 10):
            grid[y][x] = "Ƃ"
    _solid_rect(grid, 2, 27, 8, 29, "▰")
    grid[29][5] = "ƕ"

    # Wood stove on its brick hearth and the closet/firewood mass beneath it.
    _solid_rect(grid, 15, 22, 18, 25)
    grid[25][16] = "Ʒ"
    _solid_rect(grid, 16, 27, 18, 29)
    grid[29][17] = "Ə"

    # Exactly one interior Ashtray, reachable along the clear east-side lane.
    grid[20][13] = "ኆ"
    return ["".join(row) for row in grid]


def main():
    output = ROOT / "assets" / "maps" / "tahuya_cabin_interior.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
