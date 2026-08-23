"""Generate the authored compact Cabin interior map.

The hardwood room used to run eleven rows deep. At native scale that is
most of a screen of empty floor between the north wall's table and fire
and the south wall's sink and door, so the two halves of the cabin
never appeared together and the walk between them was dead ground. It
is six rows now, and the west counter that runs down the side of it
shrinks to match -- it is the only fixture long enough to have to.

Everything below the carpet is measured from the floor band rather than
written out, so the room can be lengthened or shortened again by one
number without the sink, the sealed room, the doorway and the arrival
drifting apart from each other.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 21

# The north wall is three rows of panel rather than one. Anything hung on
# it -- the curtained windows, the door that does not open -- is taller
# than a single tile, and on a one-row wall the tops were clipped off by
# the edge of the map and the bottoms hung out over the carpet.
WALL_ROWS = 3
WALL_BOTTOM = WALL_ROWS - 1             # last row of panel, where things sit
COUCH_TOP = WALL_ROWS                   # the couches stand clear of it
COUCH_ROW = COUCH_TOP + 2

FLOOR_TOP = 16                          # first hardwood row, under the carpet
FLOOR_ROWS = 6                          # ...and how deep the room runs
FLOOR_BOTTOM = FLOOR_TOP + FLOOR_ROWS - 1
COUNTER_TOP = FLOOR_BOTTOM + 1          # the south sink run, three rows deep
COUNTER_BOTTOM = COUNTER_TOP + 2
DOOR_ROW = COUNTER_BOTTOM               # the recess cut through the south wall
HEIGHT = COUNTER_BOTTOM + 2


def _solid_rect(grid, left, top, right, bottom, char="∎"):
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            grid[y][x] = char


def build_map():
    # The 21x29 interior fits inside the exterior shell's authored
    # footprint.  Warm olive carpet fills the living/dining space.
    grid = [["Ŀ" for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(WALL_ROWS):
        for x in range(WIDTH):
            grid[y][x] = "ć"
    for x in range(WIDTH):
        grid[HEIGHT - 1][x] = "ć"
    for y in range(HEIGHT):
        grid[y][0] = "ć"
        grid[y][WIDTH - 1] = "ć"

    # The compact exterior now has one south door. The north wall is complete;
    # the sole reversible threshold remains the human-scale south recess.
    for x in range(9, 12):
        grid[DOOR_ROW][x] = "Ɯ"
        grid[DOOR_ROW + 1][x] = "Ɯ"
    grid[COUNTER_BOTTOM - 1][10] = "ኄ"

    # The two couches sit flush against the north wall while continuing to
    # frame the north living wall.
    _solid_rect(grid, 1, COUCH_TOP, 8, COUCH_ROW)
    grid[COUCH_ROW][5] = "Ƈ"
    grid[COUCH_ROW - 1][5] = "₁"
    _solid_rect(grid, 13, COUCH_TOP, 19, COUCH_ROW)
    grid[COUCH_ROW][16] = "Ƭ"
    grid[COUCH_ROW - 1][16] = "₂"
    # One curtained window centred on the wall behind each couch, and a
    # door between them that does not open. All three hang from the last
    # row of panel, so they stand on the wall rather than on the carpet.
    grid[WALL_BOTTOM][5] = "Ɏ"
    grid[WALL_BOTTOM][16] = "Ɏ"
    grid[WALL_BOTTOM][10] = "Ɖ"
    # The knotted hanging from the real cabin, on the panel to the right
    # of the big couch's window.
    grid[WALL_BOTTOM][8] = "Ɱ"

    # The map table stays flush against the west wall but stops two tiles
    # earlier, leaving more breathing room at its east end.
    # Its rectangular D&D map is the surface that later awakens; the southern
    # sink/counter remains an ordinary kitchen fixture.
    _solid_rect(grid, 1, 12, 9, 15)
    grid[15][5] = "Ƒ"

    # Pull the two west-facing chairs north into the same living-room group
    # instead of spreading them down the east wall.
    _solid_rect(grid, 17, 6, 19, 8)
    grid[8][18] = "ƭ"
    grid[7][18] = "₃"
    _solid_rect(grid, 17, 9, 19, 11)
    grid[11][18] = "ƭ"
    grid[10][18] = "₄"

    # The green carpet holds every seated entity and the stove.  Everything
    # south of that living space is hardwood.  The ordinary southern kitchen
    # counter contains the sink only; it is not the portal table.
    for y in range(FLOOR_TOP, HEIGHT):
        for x in range(1, 20):
            grid[y][x] = "Ħ"
    # A narrow west-wall counter/shelf joins the long table to the southern
    # sink run, completing the real cabin's horseshoe without narrowing the
    # central circulation lane.  Author it after the floor change so the
    # hardwood pass cannot erase its lower half or its prop marker.
    _solid_rect(grid, 1, FLOOR_TOP, 2, FLOOR_BOTTOM)
    grid[FLOOR_BOTTOM][1] = "ƛ"
    _solid_rect(grid, 2, COUNTER_TOP, 8, COUNTER_BOTTOM, "ħ")
    grid[COUNTER_BOTTOM][5] = "ƕ"

    # Human-scale mini fridge tucked against the table's southeast corner.
    # Its collision stays under the visible body; an extra east tile would
    # invisibly catch Chuck while he walks south through the central lane.
    _solid_rect(grid, 10, 14, 10, 15)
    grid[15][10] = "Ɩ"

    # Table and fire share one east-west band. The enlarged sealed room begins
    # one tile below the fire, with an unreadable black interior and a solid
    # west-facing door that uses the ordinary closed-door interaction.
    _solid_rect(grid, 15, 12, 18, 15)
    grid[15][16] = "Ʒ"
    # The lava lamp stands on the strip between the stove and the east
    # wall, which is the only piece of floor in the room with nothing
    # else on it and a wall to put a lamp against.
    grid[14][19] = "Ɔ"
    sealed_top, sealed_bottom = FLOOR_TOP + 1, COUNTER_BOTTOM
    for x in range(14, 20):
        grid[sealed_top][x] = "ć"
        grid[sealed_bottom][x] = "ć"
    for y in range(sealed_top, sealed_bottom + 1):
        grid[y][14] = "ć"
        grid[y][19] = "ć"
    for y in range(sealed_top + 1, sealed_bottom):
        for x in range(15, 19):
            grid[y][x] = "◼"
    grid[(sealed_top + sealed_bottom) // 2][14] = "ƚ"

    # Restore the enlarged southern doorway and arrival after laying floors.
    for x in range(9, 12):
        grid[DOOR_ROW][x] = "Ɯ"
        grid[DOOR_ROW + 1][x] = "Ɯ"
    grid[COUNTER_BOTTOM - 1][10] = "ኄ"

    # Exactly one interior Ashtray, reachable along the clear central lane.
    grid[FLOOR_TOP + 2][13] = "ኆ"
    return ["".join(row) for row in grid]


def main():
    output = ROOT / "assets" / "maps" / "tahuya_cabin_interior.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
