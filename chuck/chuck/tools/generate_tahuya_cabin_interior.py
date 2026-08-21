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

    # Reversible north/back and south/front thresholds.  The three-wide,
    # two-deep black recesses read as human-scale doorways while the centered
    # transition cells preserve exact route alignment.
    for x in range(9, 12):
        grid[0][x] = "Ƣ"
        grid[1][x] = "Ƣ"
    grid[2][10] = "ኅ"
    for x in range(9, 12):
        grid[31][x] = "Ɯ"
        grid[32][x] = "Ɯ"
    grid[30][10] = "ኄ"

    # The two couches sit flush against the north wall while continuing to
    # flank the full human-scale back doorway.
    _solid_rect(grid, 1, 1, 8, 3)
    grid[3][5] = "Ƈ"
    grid[2][5] = "₁"
    _solid_rect(grid, 13, 1, 19, 3)
    grid[3][16] = "Ƭ"
    grid[2][16] = "₂"

    # The long map table is tucked against the west wall beside the big couch.
    # Its rectangular D&D map is the surface that later awakens; the southern
    # sink/counter remains an ordinary kitchen fixture.
    _solid_rect(grid, 1, 8, 11, 11)
    grid[11][6] = "Ƒ"

    # Pull the two west-facing chairs north into the same living-room group
    # instead of spreading them down the east wall.
    _solid_rect(grid, 16, 5, 18, 7)
    grid[7][17] = "ƭ"
    grid[6][17] = "₃"
    _solid_rect(grid, 16, 9, 18, 11)
    grid[11][17] = "ƭ"
    grid[10][17] = "₄"

    # The green carpet holds every seated entity and the stove.  Everything
    # south of that living space is hardwood.  The ordinary southern kitchen
    # counter contains the sink only; it is not the portal table.
    for y in range(20, 32):
        for x in range(1, 20):
            grid[y][x] = "Ħ"
    # A narrow west-wall counter/shelf joins the long table to the southern
    # sink run, completing the real cabin's horseshoe without narrowing the
    # central circulation lane.  Author it after the floor change so the
    # hardwood pass cannot erase its lower half or its prop marker.
    _solid_rect(grid, 1, 12, 2, 28)
    grid[28][1] = "ƛ"
    _solid_rect(grid, 2, 29, 8, 31, "ħ")
    grid[31][5] = "ƕ"

    # The enlarged wood stove sits above a room-scale, fully enclosed southeast
    # room.  A complete wall perimeter replaces the former furniture-sized box.
    _solid_rect(grid, 15, 16, 18, 19)
    grid[19][16] = "Ʒ"
    for x in range(14, 20):
        grid[26][x] = "ć"
        grid[31][x] = "ć"
    for y in range(26, 32):
        grid[y][14] = "ć"
        grid[y][19] = "ć"
    for y in range(27, 31):
        for x in range(15, 19):
            grid[y][x] = "Ħ"

    # Restore the enlarged southern doorway and arrival after laying floors.
    for x in range(9, 12):
        grid[31][x] = "Ɯ"
        grid[32][x] = "Ɯ"
    grid[30][10] = "ኄ"

    # Exactly one interior Ashtray, reachable along the clear central lane.
    grid[20][13] = "ኆ"
    return ["".join(row) for row in grid]


def main():
    output = ROOT / "assets" / "maps" / "tahuya_cabin_interior.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
