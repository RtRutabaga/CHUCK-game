"""Author phlegethos_rubble_pass.txt -- an east-west infernal breather.

The fifth Phase 8 map breaks the region's northward cadence. Chuck enters
from the lava lake at the west edge and follows a broad, winding basalt path
east through dark collapsed rubble. A cliff-fed lava fall pours into a narrow
two-tile river; one intact slab carries the path across it. The map is low
pressure: one slow lemure lurks behind a rubble pocket and one horned devil
paces on the far side of the lava, well outside the required route.

The generator proves the complete arrival -> Ashtray -> exit route without
walking through lava or solid rubble before it writes the authored map.
"""

from collections import deque
import math
from pathlib import Path


W, H = 64, 34
OUT = (
    Path(__file__).resolve().parents[1]
    / "assets" / "maps" / "phlegethos_rubble_pass.txt"
)

# The way in from the lava lake, at the temple's scale: three tiles with
# the arch over the middle. It is in the south wall because that is the
# way Chuck was walking when he left the lake -- coming out against the
# west wall facing east was a quarter turn nothing in the region made.
SOUTH_GATE = (10, 32)
EAST_PASS = (62, 6)
ARRIVAL = (10, 30)
ANCHOR = (11, 25)
RETURN_ARRIVAL = (60, 6)
LEMURE = (8, 19)
HORNED_DEVIL = (38, 26)
LAVA_FALL = (52, 14)

PATH_POINTS = (
    (10, 31),
    (10, 26),
    (14, 26),
    (14, 20),
    (27, 20),
    (27, 12),
    (42, 12),
    (42, 6),
    RETURN_ARRIVAL,
)

HEADER = [
    "; PHASE 8 - PHLEGETHOS 4, THE RUBBLE PASS (64x34 tiles).",
    "; A low-pressure route in from the south gate and out to the east,",
    "; winding through dark basalt rubble.",
    "; A cliff-fed lava fall enters a narrow lava river; an intact slab",
    "; carries the path across. One lemure and one distant horned devil",
    "; are the map's only enemies. One Ashtray serves this map.",
]


def _wide_path() -> set[tuple[int, int]]:
    lane: set[tuple[int, int]] = set()
    for (x0, y0), (x1, y1) in zip(PATH_POINTS, PATH_POINTS[1:]):
        if x0 == x1:
            for row in range(min(y0, y1), max(y0, y1) + 1):
                lane.update((x0 + dx, row) for dx in (-1, 0, 1))
        else:
            for col in range(min(x0, x1), max(x0, x1) + 1):
                lane.update((col, y0 + dy) for dy in (-1, 0, 1))
    for cx, cy in (ARRIVAL, ANCHOR, RETURN_ARRIVAL):
        lane.update(
            (cx + dx, cy + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
        )
    return {
        (col, row) for col, row in lane
        if 2 <= col < W - 2 and 2 <= row < H - 2
    }


def build() -> list[list[str]]:
    grid = [["·"] * W for _ in range(H)]
    for col in range(W):
        for row in (0, 1, H - 2, H - 1):
            grid[row][col] = "█"
    for row in range(H):
        for col in (0, 1, W - 2, W - 1):
            grid[row][col] = "█"

    lane = _wide_path()

    # A narrow lava river cuts east-west across the map. The winding route
    # crosses on one intact three-wide slab rather than adding another jump
    # gauntlet to this deliberately quieter map.
    for row in (15, 16):
        for col in range(18, W - 2):
            grid[row][col] = "≋"
    for row in range(14, 18):
        for col in range(26, 29):
            grid[row][col] = "≡"

    # A broken cliff shelf occupies the northeast. Its central cleft feeds a
    # visible falling-lava prop and a molten channel into the river.
    cliff_bottom = {
        col: 10 + ((col * 7 + 3) % 3)
        for col in range(45, 59)
    }
    for col, bottom in cliff_bottom.items():
        for row in range(9, bottom + 1):
            grid[row][col] = "█"
    for row in range(10, 15):
        for col in (51, 52, 53):
            grid[row][col] = "≋"
    grid[LAVA_FALL[1]][LAVA_FALL[0]] = "ƒ"

    # Pave last so the required route stays visibly continuous, including the
    # crossing slab. The river remains lethal everywhere outside that slab.
    for col, row in lane:
        if grid[row][col] in {"·", "≡"}:
            grid[row][col] = "≡"

    # Dark rubble clusters fill the negative space like the temple collapse,
    # but use their own basalt-and-ember art. Probability rises around chosen
    # pile centers, producing heaps rather than an even noise field.
    piles = (
        (7, 7), (15, 11), (10, 29), (22, 6), (22, 25),
        (33, 7), (34, 27), (47, 22), (56, 25), (58, 11),
    )
    lane_buffer = {
        (col + dx, row + dy)
        for col, row in lane
        for dx in range(-2, 3)
        for dy in range(-2, 3)
    }
    protected = lane_buffer | {
        (LEMURE[0] + dx, LEMURE[1] + dy)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
    } | {
        (HORNED_DEVIL[0] + dx, HORNED_DEVIL[1] + dy)
        for dx in range(-3, 4)
        for dy in range(-2, 3)
    }
    for row in range(2, H - 2):
        for col in range(2, W - 2):
            if grid[row][col] != "·" or (col, row) in protected:
                continue
            near = min(math.hypot(col - px, row - py) for px, py in piles)
            probability = 0.04 + 0.38 * max(0.0, 1.0 - near / 5.5)
            roll = ((col * 43 + row * 97 + col * row * 11) % 100) / 100
            if roll < probability:
                grid[row][col] = "þ"
            elif (col * 19 + row * 31) % 83 == 0:
                grid[row][col] = "♨"

    # The lemure's three-block pocket opens away from the path, slowing its
    # approach without trapping it. Lava contains the horned devil south of
    # the late route, keeping the giant readable but optional.
    for col, row in ((7, 18), (8, 18), (9, 18)):
        if (col, row) not in lane:
            grid[row][col] = "þ"
    grid[LEMURE[1]][LEMURE[0]] = "Ѯ"
    grid[HORNED_DEVIL[1]][HORNED_DEVIL[0]] = "Ԟ"

    # Continue the established Phlegethos rule: each exterior map scatters
    # temple-derived breakable urns with the usual carton reward.
    for col, row in ((10, 5), (34, 6), (56, 19)):
        assert grid[row][col] == "·", (col, row, grid[row][col])
        grid[row][col] = "¢"

    # Human-readable edge thresholds and the three map-local markers. The
    # east opening is a one-tile-wide, human-height vertical cleft centered
    # exactly on the paved approach; every visible dark cell is an active
    # threshold, so the art and transition footprint cannot disagree.
    grid[SOUTH_GATE[1]][SOUTH_GATE[0] - 1] = "Δ"
    grid[SOUTH_GATE[1]][SOUTH_GATE[0]] = "⌄"
    grid[SOUTH_GATE[1]][SOUTH_GATE[0] + 1] = "Δ"
    for row in range(EAST_PASS[1] - 1, EAST_PASS[1] + 2):
        grid[row][EAST_PASS[0]] = "›"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "Ԯ"
    grid[ANCHOR[1]][ANCHOR[0]] = "԰"
    grid[RETURN_ARRIVAL[1]][RETURN_ARRIVAL[0]] = "Բ"
    return grid


def validate(grid: list[list[str]]) -> int:
    blocked = {"█", "þ", "≋", "ƒ"}
    reached = {ARRIVAL}
    frontier = deque([ARRIVAL])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            x, y = point
            if (
                0 <= x < W and 0 <= y < H
                and point not in reached
                and grid[y][x] not in blocked
            ):
                reached.add(point)
                frontier.append(point)
    for label, point in (
        ("Ashtray", ANCHOR),
        ("east arrival", RETURN_ARRIVAL),
        ("east pass", EAST_PASS),
        ("south gate", SOUTH_GATE),
    ):
        assert point in reached, f"{label} is unreachable"
    assert grid[LEMURE[1]][LEMURE[0]] == "Ѯ"
    assert grid[HORNED_DEVIL[1]][HORNED_DEVIL[0]] == "Ԟ"
    assert sum(row.count("≋") for row in grid) >= 90
    assert {
        (EAST_PASS[0], EAST_PASS[1] - 1),
        EAST_PASS,
        (EAST_PASS[0], EAST_PASS[1] + 1),
    } == {
        (col, row)
        for row in range(H)
        for col in range(W)
        if grid[row][col] == "›"
    }
    return sum(row.count("þ") for row in grid)


def main() -> None:
    grid = build()
    rubble = validate(grid)
    OUT.write_text(
        "\n".join(HEADER + ["".join(row) for row in grid]) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} ({W}x{H}); {rubble} dark rubble blocks")


if __name__ == "__main__":
    main()
