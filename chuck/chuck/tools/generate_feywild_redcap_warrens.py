"""Author Feywild 8: the redcap camp and the ways around it.

This is the region's strongest ordinary-enemy area, so its central claim
is the one the phase document makes: the player must be able to cross it
without defeating a single redcap. The camp itself is the direct route
and it is genuinely dangerous; a northern game trail runs the whole width
of the map outside every notice zone, and two Chuck-only passages -- one
root arch, one toadstool cap -- stitch the two together for anyone caught
in the open.

The validator proves both halves: a plain flood shows the camp route
exists, a notice-aware flood shows the crossing can be made without ever
entering a redcap's notice range, and a large-actor flood shows the
redcaps genuinely cannot follow Chuck into the passages.
"""

from collections import deque
import math
from pathlib import Path

try:
    from tools.feywild_mushroom_dressing import dress_grid
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_mushroom_dressing import dress_grid
try:
    from tools.feywild_great_tree_dressing import (
        dress_grid as plant_great_tree,
    )
except ModuleNotFoundError:  # Direct execution from inside tools/.
    from feywild_great_tree_dressing import dress_grid as plant_great_tree

W, H = 76, 50
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "feywild_redcap_warrens.txt"
)

# config.REDCAP_NOTICE_RANGE is 112px; at 16px tiles that is seven tiles.
NOTICE_TILES = 7.0

RETURN_EXIT = (0, 26)
ARRIVAL = (1, 26)
FUTURE_RETURN = (74, 25)
FUTURE_EXIT = (75, 25)
ANCHOR = (66, 28)

REDCAPS = ((24, 22), (38, 30), (50, 20), (50, 38))
MITES = ((26, 6), (29, 6), (32, 6), (40, 32), (43, 32), (46, 33))

REFUGE_DOOR = (23, 30)      # root arch into the camp's southern refuge
REFUGE_GRASS = (23, 34)
SHORTCUT_SOUTH = (31, 15)   # toadstool caps linking camp to the game trail
SHORTCUT_NORTH = (31, 10)
SHORTCUT_GRASS = (33, 13)

HEADER = [
    "; PHASE 9 - FEYWILD 8, THE REDCAP WARRENS (76x50 tiles).",
    "; Four redcaps hold a camp of gnome-sized gear with separated notice",
    "; zones. A northern game trail crosses the map outside all of them, so",
    "; the warrens can be passed without a single fight. Two Chuck-only",
    "; passages join the trail and the camp; redcaps cannot follow through.",
]


def _room(grid, left, top, right, bottom, char="."):
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            grid[row][col] = char


def _root_box(grid, left, top, right, bottom, door):
    for col in range(left, right + 1):
        grid[top][col] = "※"
        grid[bottom][col] = "※"
    for row in range(top, bottom + 1):
        grid[row][left] = "※"
        grid[row][right] = "※"
    _room(grid, left + 1, top + 1, right - 1, bottom - 1, "'")
    grid[door[1]][door[0]] = "≀"


def build() -> list[list[str]]:
    grid = [["#"] * W for _ in range(H)]

    # The camp, and the west and east clearings that bracket it.
    _room(grid, 1, 22, 12, 30)
    _room(grid, 16, 16, 56, 40)
    _room(grid, 58, 20, 74, 32)
    _room(grid, 12, 24, 16, 28)
    _room(grid, 56, 24, 58, 28)

    # The game trail: a full-width northern route with a leg down at each
    # end. Nothing on it comes within notice range of the camp.
    _room(grid, 8, 4, 68, 9)
    _room(grid, 8, 9, 12, 22)
    _room(grid, 62, 9, 68, 22)

    # A band of fused toadstools walls the trail off from the camp.
    _room(grid, 14, 10, 61, 15, "ᛘ")

    # Cut a Chuck-sized pocket into that band, open at both ends: the
    # shortcut between the camp and the trail, with a grass cache in it.
    _room(grid, 28, 11, 35, 14, "ᛜ")
    grid[SHORTCUT_SOUTH[1]][SHORTCUT_SOUTH[0]] = "ᚿ"
    grid[SHORTCUT_NORTH[1]][SHORTCUT_NORTH[0]] = "ᚿ"
    grid[SHORTCUT_GRASS[1]][SHORTCUT_GRASS[0]] = "<"

    # The southern refuge: a root pocket to duck into mid-pursuit.
    _root_box(grid, 20, 30, 27, 38, REFUGE_DOOR)
    grid[REFUGE_GRASS[1]][REFUGE_GRASS[0]] = "<"

    # Ground the redcaps have worn bare. The blob is deliberately ragged
    # so the camp reads as trampled living-space rather than a room.
    for left, top, right, bottom in (
        (22, 21, 46, 33), (26, 18, 40, 21), (30, 33, 44, 37),
        (19, 24, 22, 30), (46, 24, 50, 31),
    ):
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                if grid[row][col] == ".":
                    grid[row][col] = "ᛜ"

    # Standing cover breaks the clearing up and gives a pursued rat
    # something to put between himself and a sickle.
    for col, row, char in (
        (19, 21, "ŧ"), (31, 20, "Ŧ"), (43, 19, "ŧ"), (52, 22, "Ɓ"),
        (18, 34, "Ŧ"), (30, 29, "ŧ"), (37, 27, "Ŧ"), (49, 26, "ŧ"),
        (24, 27, "Ŧ"), (44, 39, "Ɓ"), (54, 36, "ŧ"), (35, 39, "Ŧ"),
        (41, 17, "Ŧ"), (28, 36, "ŧ"), (52, 27, "Ŧ"), (21, 27, "ŧ"),
    ):
        assert grid[row][col] in {".", "ᛜ"}, (col, row)
        grid[row][col] = char

    # The camp's gear, all of it gnome-sized and none of it Chuck's.
    for col, row, char in (
        (20, 19, "ᚱ"), (34, 18, "ᚱ"), (46, 28, "ᚱ"), (26, 39, "ᚱ"),
        (30, 24, "ᚢ"), (44, 34, "ᚢ"),
        (26, 21, "ᚦ"), (42, 23, "ᚦ"), (36, 36, "ᚦ"), (52, 30, "ᚦ"),
        (28, 27, "ᚠ"), (40, 26, "ᚠ"), (22, 17, "ᚠ"), (48, 33, "ᚠ"),
        (33, 31, "ᚠ"), (54, 18, "ᚠ"),
    ):
        assert grid[row][col] in {".", "ᛜ"}, (col, row)
        grid[row][col] = char

    _dress_with_vegetation(grid)

    for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2):
        grid[row][RETURN_EXIT[0]] = "←"
    for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2):
        grid[row][FUTURE_EXIT[0]] = "→"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "բ"
    grid[ANCHOR[1]][ANCHOR[0]] = "գ"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "ե"
    grid[FUTURE_EXIT[1]][FUTURE_EXIT[0]] = "դ"
    for col, row in REDCAPS:
        grid[row][col] = "զ"
    for col, row in MITES:
        grid[row][col] = "է"
    dress_grid("feywild_redcap_warrens", grid)
    plant_great_tree("feywild_redcap_warrens", grid)
    return grid


def _dress_with_vegetation(grid) -> None:
    """Scatter the region's trees and shrubs through the dense growth.

    Same rule as the Phase 9 vegetation pass: only tiles that are already
    solid dense growth, and only well inside it, so the silhouette of
    every route is untouched.
    """
    for row in range(1, H - 1):
        for col in range(1, W - 1):
            if grid[row][col] != "#":
                continue
            neighbours = sum(
                grid[row + dr][col + dc] == "#"
                for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            if neighbours < 2:
                continue
            key = (col * 31 + row * 17) % 23
            if key == 0:
                grid[row][col] = "ŧ"
            elif key == 7:
                grid[row][col] = "Ŧ"
            elif key == 15:
                grid[row][col] = "Ɓ"


def _under(char: str) -> str:
    return {
        "բ": "'", "գ": ".", "դ": "→", "ե": "'", "զ": ".", "է": ".",
        "<": ".",
    }.get(char, char)


SOLID = {"#", "※", "ᛘ", "ŧ", "Ŧ", "Ɓ", "ŋ", "ᚱ", "ᚢ", "ᚦ", "ᚠ"}
PASSAGES = {"≀", "ᚿ"}


def _reachable(grid, start, *, large_actor=False, avoid_notice=False):
    def open_tile(point):
        col, row = point
        char = _under(grid[row][col])
        if char in SOLID:
            return False
        if large_actor and char in PASSAGES:
            return False
        if avoid_notice and any(
            math.hypot(col - rc, row - rr) <= NOTICE_TILES
            for rc, rr in REDCAPS
        ):
            return False
        return True

    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < W and 0 <= y < H) or point in reached:
                continue
            if not open_tile(point):
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def validate(grid) -> None:
    assert len(grid) == H and all(len(row) == W for row in grid)

    walk = _reachable(grid, ARRIVAL)
    assert {RETURN_EXIT, FUTURE_EXIT, FUTURE_RETURN, ANCHOR,
            REFUGE_DOOR, REFUGE_GRASS, SHORTCUT_SOUTH, SHORTCUT_NORTH,
            SHORTCUT_GRASS, *REDCAPS, *MITES} <= walk

    # The claim the phase document makes: the warrens can be crossed
    # without ever entering a redcap's notice range.
    safe = _reachable(grid, ARRIVAL, avoid_notice=True)
    assert FUTURE_EXIT in safe, "the warrens cannot be crossed safely"
    assert ANCHOR in safe, "the Ashtray is not safely reachable"
    # ...but the camp itself is still genuinely guarded.
    assert not any(
        (col, row) in safe
        for col in range(20, 53) for row in range(18, 40)
        if math.hypot(col - 38, row - 30) <= 4
    ), "the camp centre is not actually contested"

    # Redcaps hold the open ground but cannot follow through the passages.
    large = _reachable(grid, ARRIVAL, large_actor=True)
    assert REFUGE_GRASS not in large
    assert SHORTCUT_GRASS not in large

    # Their notice zones must stay separate, so pursuit never becomes a mob.
    for index, (col, row) in enumerate(REDCAPS):
        for other_col, other_row in REDCAPS[index + 1:]:
            gap = math.hypot(col - other_col, row - other_row)
            assert gap > NOTICE_TILES * 2, ((col, row), gap)

    text = "".join("".join(row) for row in grid)
    assert text.count("զ") == 4
    assert text.count("է") == 6
    assert text.count("գ") == 1
    assert text.count("<") == 2
    assert text.count("ᚿ") == 2 and text.count("≀") == 1
    assert all(grid[row][0] == "←"
               for row in range(RETURN_EXIT[1] - 1, RETURN_EXIT[1] + 2))
    assert all(grid[row][W - 1] in {"→", "դ"}
               for row in range(FUTURE_EXIT[1] - 1, FUTURE_EXIT[1] + 2))


def main() -> None:
    grid = build()
    validate(grid)
    OUT.write_text(
        "\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
