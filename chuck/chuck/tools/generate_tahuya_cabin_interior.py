"""Generate the authored compact 21x29 Cabin interior map."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 21
HEIGHT = 29


def _solid_rect(grid, left, top, right, bottom, char="∎"):
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            grid[y][x] = char


def build_map():
    # The 21x29 interior fits inside the exterior shell's authored
    # footprint.  Warm olive carpet fills the living/dining space.
    grid = [["Ŀ" for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for x in range(WIDTH):
        grid[0][x] = "ć"
        grid[HEIGHT - 1][x] = "ć"
    for y in range(HEIGHT):
        grid[y][0] = "ć"
        grid[y][WIDTH - 1] = "ć"

    # The compact exterior now has one south door. The north wall is complete;
    # the sole reversible threshold remains the human-scale south recess.
    for x in range(9, 12):
        grid[27][x] = "Ɯ"
        grid[28][x] = "Ɯ"
    grid[26][10] = "ኄ"

    # The two couches sit flush against the north wall while continuing to
    # frame the north living wall.
    _solid_rect(grid, 1, 1, 8, 3)
    grid[3][5] = "Ƈ"
    grid[2][5] = "₁"
    _solid_rect(grid, 13, 1, 19, 3)
    grid[3][16] = "Ƭ"
    grid[2][16] = "₂"

    # The map table stays flush against the west wall but stops two tiles
    # earlier, leaving more breathing room at its east end.
    # Its rectangular D&D map is the surface that later awakens; the southern
    # sink/counter remains an ordinary kitchen fixture.
    _solid_rect(grid, 1, 10, 9, 13)
    grid[13][5] = "Ƒ"

    # Pull the two west-facing chairs north into the same living-room group
    # instead of spreading them down the east wall.
    _solid_rect(grid, 16, 4, 18, 6)
    grid[6][17] = "ƭ"
    grid[5][17] = "₃"
    _solid_rect(grid, 16, 7, 18, 9)
    grid[9][17] = "ƭ"
    grid[8][17] = "₄"

    # The green carpet holds every seated entity and the stove.  Everything
    # south of that living space is hardwood.  The ordinary southern kitchen
    # counter contains the sink only; it is not the portal table.
    for y in range(14, 29):
        for x in range(1, 20):
            grid[y][x] = "Ħ"
    # A narrow west-wall counter/shelf joins the long table to the southern
    # sink run, completing the real cabin's horseshoe without narrowing the
    # central circulation lane.  Author it after the floor change so the
    # hardwood pass cannot erase its lower half or its prop marker.
    _solid_rect(grid, 1, 14, 2, 24)
    grid[24][1] = "ƛ"
    _solid_rect(grid, 2, 25, 8, 27, "ħ")
    grid[27][5] = "ƕ"

    # Human-scale mini fridge tucked against the table's southeast corner.
    # Its collision stays under the visible body; an extra east tile would
    # invisibly catch Chuck while he walks south through the central lane.
    _solid_rect(grid, 10, 12, 10, 13)
    grid[13][10] = "Ɩ"

    # Table and fire share one east-west band. The enlarged sealed room begins
    # one tile below the fire, with an unreadable black interior and a solid
    # west-facing door that uses the ordinary closed-door interaction.
    _solid_rect(grid, 15, 10, 18, 13)
    grid[13][16] = "Ʒ"
    for x in range(14, 20):
        grid[15][x] = "ć"
        grid[27][x] = "ć"
    for y in range(15, 28):
        grid[y][14] = "ć"
        grid[y][19] = "ć"
    for y in range(16, 27):
        for x in range(15, 19):
            grid[y][x] = "◼"
    grid[22][14] = "ƚ"

    # Restore the enlarged southern doorway and arrival after laying floors.
    for x in range(9, 12):
        grid[27][x] = "Ɯ"
        grid[28][x] = "Ɯ"
    grid[26][10] = "ኄ"

    # Exactly one interior Ashtray, reachable along the clear central lane.
    grid[20][13] = "ኆ"
    return ["".join(row) for row in grid]


def main():
    output = ROOT / "assets" / "maps" / "tahuya_cabin_interior.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
