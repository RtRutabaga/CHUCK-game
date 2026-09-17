"""Author the first playable top-down platform outside Zephyros' tower."""

from collections import deque
from pathlib import Path


# The platform is standing cloud rather than the aerie's pale stone.
CLOUD = "ᚡ"        # walkable cloud floor
# The rim, one char per side it is open on. A single edge tile used all
# the way round gave the platform the same shading on its far edge, its
# near edge and both flanks, and a shape lit the same on every side has
# no form: it reads as a patch of cloud tiles rather than as one bank
# with a top and an underside.
RIM_TOP = "ᚤ"      # the far edge, where the light lands
RIM_BASE = "ᚥ"     # the near edge: the underside, in shadow
RIM_WEST = "ᚩ"
RIM_EAST = "ᚪ"
RIMS = (RIM_TOP, RIM_BASE, RIM_WEST, RIM_EAST)
# ...and one band of shaded body just inside it, so the bank has a
# middle that faces the light and a side that turns away from it.
CLOUD_SOFT = "ᚫ"

W, H = 44, 34
OUT = Path(__file__).resolve().parents[1] / "assets/maps/zephyros_tower_exterior.txt"
ARRIVAL = (22, 27)
WAYPOINT = (17, 25)
ARCH_PROP = (22, 9)
ARCH = (22, 10)
FUTURE_RETURN = (22, 11)

HEADER = [
    "; PHASE 10 - ZEPHYROS TOWER EXTERIOR (44x34 tiles).",
    "; A compact circular platform of standing cloud at an immense tower",
    "; facade.",
    "; Chuck arrives on the southern tongue; the giant north arch enters",
    "; Zephyros' Aerie.",
]


def build():
    grid = [["~"] * W for _ in range(H)]
    cx, cy = 22, 19
    for row in range(8, 31):
        for col in range(11, 34):
            dx = (col - cx) / 10.0
            dy = (row - cy) / 10.0
            if dx * dx + dy * dy <= 1.0:
                grid[row][col] = CLOUD



    # Southern landing tongue and a short approach. The surrounding sky now
    # presses close, keeping the platform subordinate to the tower facade.
    for row in range(24, 30):
        for col in range(19, 26):
            grid[row][col] = CLOUD
    for row in range(9, 26):
        for col in range(19, 26):
            if grid[row][col] != "~":
                grid[row][col] = CLOUD
    _rim(grid)
    grid[ARCH_PROP[1]][ARCH_PROP[0]] = "Ƶ"
    grid[ARCH[1]][ARCH[0]] = "ህ"
    grid[FUTURE_RETURN[1]][FUTURE_RETURN[0]] = "ሆ"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ሃ"
    return grid


def _rim(grid) -> None:
    """Edge every tile of the platform that touches open sky.

    Done once, after the tongue and the approach are cut, so the rim
    follows the shape that is actually there rather than the ellipse it
    started as -- including the tongue's sides and its tip, which the
    ring pass used to paint over and leave bare.
    """
    floor = {(col, row) for row in range(H) for col in range(W)
             if grid[row][col] == CLOUD}
    for col, row in floor:
        def open_sky(dcol: int, drow: int) -> bool:
            return (col + dcol, row + drow) not in floor

        if open_sky(0, -1):
            grid[row][col] = RIM_TOP
        elif open_sky(0, 1):
            grid[row][col] = RIM_BASE
        elif open_sky(-1, 0):
            grid[row][col] = RIM_WEST
        elif open_sky(1, 0):
            grid[row][col] = RIM_EAST

    rim = {(col, row) for col, row in floor if grid[row][col] in RIMS}
    for col, row in floor - rim:
        if any((col + dcol, row + drow) in rim
               for dcol in (-1, 0, 1) for drow in (-1, 0, 1)):
            grid[row][col] = CLOUD_SOFT


def _base(char):
    return {"ሃ": CLOUD, "ህ": "Ƶ",
            "ሆ": CLOUD}.get(char, char)


def validate(grid):
    assert len(grid) == H and all(len(row) == W for row in grid)
    walkable = {(col, row) for row in range(H) for col in range(W)
                if _base(grid[row][col]) in {CLOUD, "Ƶ"}}
    reached = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in walkable and point not in reached:
                reached.add(point)
                frontier.append(point)
    assert WAYPOINT in reached and ARCH in reached and FUTURE_RETURN in reached
    text = "".join("".join(row) for row in grid)
    assert text.count("Ƶ") == 1
    assert text.count("~") > text.count(CLOUD), (
        "open sky no longer dominates")


def main():
    grid = build()
    validate(grid)
    OUT.write_text("\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
                   encoding="utf-8")
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
