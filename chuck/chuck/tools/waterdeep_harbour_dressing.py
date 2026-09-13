"""Waterdeep docks' harbour dressing, applied to the shipped map.

Two kinds of placement, for two kinds of thing.

**The pier's edges are derived, never authored.** Every water tile is
looked at against the planks around it, and gets exactly what the camera
could see there:

* planks directly north -- the pier's front face (plank ends, the shade
  under the deck, a piling, the waterline);
* planks directly west -- the deck's shadow on the water, and no face,
  because the pier's east side points along our line of sight;
* both -- the face with the shadow down its left;
* planks only at the north-west diagonal -- the small corner where the
  face's shade and the side shadow meet.

Water with planks only to its south or east gets nothing: those are the
pier's north and west sides, which face away from us or along our view.

**Everything else is placed by hand, against the rules of the vantage:**

* Mooring posts stand on edge planks. On a south edge the post sits in
  the middle of its tile, right above the face; on a west edge it sits
  toward the water. None on north or east edges, where a boat tied up
  would be hidden behind the pier or seen end-on.
* Rowboats lie on the water two tiles south of a south-edge post, so the
  hull sits against the pier's face and the line runs up to the post's
  foot. Never north of a pier: from here a boat there would be half
  behind the deck.
* Lamps stand on stone, clear of doors, markers and the ways through.
* Signs hang on a facade tile beside a door, and window boxes on the
  window tiles themselves, both flat to the wall.
* Washing lines cross the two alleys between the north houses at eave
  height, hook to hook between the walls.

Every solid piece is checked against the map's walkable area before it
is kept.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chult_floor_dressing import reachable  # noqa: E402

MAP_NAME = "waterdeep_docks"
WATER = "~"
PLANK = "="

PIER_FACE = "ꜭ"
PIER_FACE_SHADOW = "ꜯ"
PIER_SHADOW = "ꜱ"
PIER_CORNER = "ꜳ"
BOLLARD = "ꜵ"
BOLLARD_WEST = "ꜷ"
ROWBOAT = "ꜹ"
ROWBOAT_WEST = "ꝍ"
LAMP = "ꜻ"
SIGN_BREAD = "ꜽ"
SIGN_FISH = "ꜿ"
SIGN_BARREL = "ꝁ"
WINDOW_BOX = "ꝃ"
WASHING_6 = "ꝅ"
WASHING_4 = "ꝇ"
EDGES = {PIER_FACE, PIER_FACE_SHADOW, PIER_SHADOW, PIER_CORNER}
DRESSING = EDGES | {BOLLARD, BOLLARD_WEST, ROWBOAT, ROWBOAT_WEST, LAMP,
                    SIGN_BREAD,
                    SIGN_FISH, SIGN_BARREL, WINDOW_BOX, WASHING_6, WASHING_4}

BOLLARDS_SOUTH = ((8, 26), (17, 26), (10, 30), (3, 20))
BOLLARDS_WEST = ((7, 11), (7, 15), (1, 18), (7, 23))
# Each boat is moored to the south-edge post two tiles above it. Only the
# one, off the west pier: in the finale the docked ship fills the water
# south of the big pier, the sewer outflow's climb comes up the far pier's
# face, and the fisherman casts into the basin east of it. An empty post
# is what most mooring posts are.
BOATS = ((3, 22),)
# ...and one on the water west of the big pier, bow to the west-edge post
# two tiles east of it: the post beside Bobert's barrel, which is the
# boat the opening cutscene shows tied up by the posts where Chuck wakes.
BOATS_WEST = ((5, 11),)
# (20, 10) rather than (21, 11): one tile further north-west, beside the
# west gate's pillar instead of standing in the mouth of it.
LAMPS = ((19, 7), (24, 7), (20, 10), (38, 18), (50, 18))
SIGNS = ((13, 4, SIGN_BREAD), (27, 4, SIGN_FISH), (40, 4, SIGN_BARREL))
WINDOW_BOXES = ((11, 4), (16, 4), (25, 4), (30, 4), (37, 4), (42, 4),
                (40, 16), (48, 16))
# (anchor col, row, char): anchor is the alley's left column plus half
# its width, so the lines hook onto the walls either side.
WASHING_LINES = ((21, 4, WASHING_6), (34, 4, WASHING_4))


def _is_deck(char: str) -> bool:
    from src.world.tilemap import MARKER_DEFS, TILE_DEFS

    if char == PLANK:
        return True
    tile = TILE_DEFS.get(char)
    if tile is not None:
        return tile.under == PLANK
    marker = MARKER_DEFS.get(char)
    return marker is not None and marker.under == PLANK


def edge_for(grid, col: int, row: int) -> str | None:
    """What the camera sees on this water tile, from the planks round it."""
    if grid[row][col] != WATER:
        return None

    def deck(x, y):
        return 0 <= y < len(grid) and 0 <= x < len(grid[y]) \
            and _is_deck(grid[y][x])

    north, west = deck(col, row - 1), deck(col - 1, row)
    if north and west:
        return PIER_FACE_SHADOW
    if north:
        return PIER_FACE
    if west:
        return PIER_SHADOW
    if deck(col - 1, row - 1):
        return PIER_CORNER
    return None


def dress_grid(grid: list[list[str]]) -> None:
    # Hand-placed pieces first, so the derived edges see the finished
    # planks -- a post is still a plank to the water beside it.
    baseline = len(reachable(grid))

    def put(col, row, char, expect, solid=True):
        nonlocal baseline
        current = grid[row][col]
        assert current in expect, (char, col, row, current)
        grid[row][col] = char
        if solid and current not in ("t", "W", WATER):
            after = len(reachable(grid))
            assert after == baseline - 1, (char, col, row, "cuts a route")
            baseline = after

    for col, row in BOLLARDS_SOUTH:
        assert grid[row + 1][col] == WATER, (col, row)
        put(col, row, BOLLARD, {PLANK})
    for col, row in BOLLARDS_WEST:
        assert grid[row][col - 1] == WATER, (col, row)
        put(col, row, BOLLARD_WEST, {PLANK})
    for col, row in BOATS:
        assert grid[row - 2][col] == BOLLARD, (col, row)
        put(col, row, ROWBOAT, {WATER})
    for col, row in BOATS_WEST:
        assert grid[row][col + 2] == BOLLARD_WEST, (col, row)
        put(col, row, ROWBOAT_WEST, {WATER})
    for col, row in LAMPS:
        put(col, row, LAMP, {","})
    for col, row, char in SIGNS:
        put(col, row, char, {"t"})
    for col, row in WINDOW_BOXES:
        put(col, row, WINDOW_BOX, {"W"})
    for col, row, char in WASHING_LINES:
        put(col, row, char, {","}, solid=False)

    edges = [(col, row, edge_for(grid, col, row))
             for row in range(len(grid)) for col in range(len(grid[row]))]
    for col, row, char in edges:
        if char is not None:
            grid[row][col] = char


def _read():
    path = ROOT / "assets" / "maps" / f"{MAP_NAME}.txt"
    lines = path.read_text(encoding="utf-8").splitlines()
    header = [line for line in lines if line.startswith(";")]
    grid = [list(line) for line in lines if not line.startswith(";")]
    return path, header, grid


def update_authored_map() -> None:
    path, header, grid = _read()
    if any(char in DRESSING for row in grid for char in row):
        raise ValueError(f"{MAP_NAME} is already dressed")
    dress_grid(grid)
    path.write_text("\n".join(header + ["".join(r) for r in grid]) + "\n",
                    encoding="utf-8")
    print(f"Dressed {MAP_NAME}")


if __name__ == "__main__":
    update_authored_map()
