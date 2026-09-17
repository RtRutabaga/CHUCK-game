"""Generate City Sewer 2: a deep vertical descent under the city.

City Sewer 1 is a wide map read as a long horizontal run. This one is
deliberately its opposite -- tall and narrow, three shafts stepping down
and westward -- so the region turns through north-south travel instead of
becoming four parallel corridors. Same modern materials throughout:
poured concrete, brick repairs, pipe walls, utility lights, slab
walkways, and dirty runoff.

Sludge and the harder Astral jump sequence belong to a later pass. The
southern end stays visibly collided, exactly as Sewer 1's did.
"""

from collections import deque
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_city_map_common import furnish_sewer  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 46
HEIGHT = 62

ARRIVAL = (5, 6)
RETURN_EXIT = (0, 6)
# The map's waypoint sits on the jog, in clear sight of the drop but
# outside it: the phase document forbids putting it inside the jump
# sequence, and a failed jump should cost the course, not the whole map.
WAYPOINT = (13, 41)
FUTURE_EXIT = (14, 61)

# Narrow ledges, each cleared by one committed jump over a single Astral
# gap. The course turns twice so it is never one straight drop.
LEDGES = (
    (10, 45, 14, 45),
    (10, 47, 14, 47),
    (10, 49, 14, 49),
    (16, 49, 19, 49),
    (21, 49, 24, 49),
    (21, 51, 24, 51),
    (21, 53, 24, 53),
    (16, 53, 19, 53),
    (10, 53, 14, 53),
)
# The chamber the course drops into. Not a ledge: sludge may pressure it.
CHAMBER = (10, 55, 24, 58)
# Every gap is exactly one tile across the axis it is crossed on, so no
# required jump ever asks for more than the committed jump gives.
GAPS = (
    (10, 46, 14, 46),
    (10, 48, 14, 48),
    (15, 49, 15, 49),
    (20, 49, 20, 49),
    (21, 50, 24, 50),
    (21, 52, 24, 52),
    (20, 53, 20, 53),
    (15, 53, 15, 53),
    (10, 54, 14, 54),
)
# Sludge pressures the approaches and the landing chamber. It is never
# laid on a ledge -- a slowed launch off a one-tile ledge is not fair.
SLUDGE = (
    (30, 22, 36, 25),
    (11, 39, 20, 40),
    (16, 56, 22, 58),
)

RATS = ((10, 13), (22, 24), (34, 34), (33, 43), (12, 22), (35, 39))
CIGARETTES = ((12, 8), (35, 30), (22, 53))


def build_map() -> list[str]:
    grid = [["#" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    def room(left, top, right, bottom, char="d"):
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                grid[row][col] = char

    # Three shafts, each joined by a short jog, stepping down and back
    # west. The route turns four times without ever running straight.
    room(1, 4, 14, 9)          # the culvert in from Sewer 1
    room(6, 4, 14, 24)         # first shaft, dropping south
    room(6, 20, 38, 26)        # jog east
    room(30, 20, 38, 44)       # second shaft
    room(10, 38, 38, 44)       # jog back west
    room(10, 38, 24, 44)       # the landing above the drop

    # A slab walkway runs beside the runoff wherever the shaft is wide
    # enough to carry both, so the descent still reads as maintained.
    for row in range(10, 24):
        grid[row][7] = ","
        grid[row][8] = ","
    for col in range(14, 30):
        grid[25][col] = ","
        grid[26][col] = ","
    for col in range(10, 25):
        grid[44][col] = ","
    for row in range(11, 23):
        grid[row][13] = "%"
    for row in range(27, 43):
        grid[row][37] = "%"

    for col, row in ((9, 12), (11, 22), (24, 24), (35, 29),
                     (32, 41), (14, 57), (21, 57)):
        grid[row][col] = "M"

    # Brick repairs, exposed pipe runs, and regularly spaced utility
    # lights: the same modern language Sewer 1 established. These only
    # ever redecorate a tile that is already wall, so a decoration can
    # never accidentally close a shaft or a jog.
    def facing_floor(col, row):
        return grid[row][col] == "#" and any(
            grid[row + dr][col + dc] in {"d", ",", "%", "M"}
            for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1))
            if 0 <= col + dc < WIDTH and 0 <= row + dr < HEIGHT
        )

    for row in range(1, HEIGHT - 1):
        for col in range(1, WIDTH - 1):
            if not facing_floor(col, row):
                continue
            # A continuous band, alternating in runs, so every shaft and
            # jog gets a crisp edge -- the same read Sewer 1's bricked
            # rows give. Scattering these individually looks like noise.
            run = ((col + row) // 6) % 2
            grid[row][col] = "b" if run == 0 else "R"
            if (col * 3 + row * 7) % 19 == 0:
                grid[row][col] = "i"

    # The Astral jump course. The shaft below the jog is solid rock except
    # for the ledges and the single-tile gaps between them, so the course
    # is the only way down rather than one option beside a safe path.
    for left, top, right, bottom in GAPS:
        room(left, top, right, bottom, "V")
    for left, top, right, bottom in LEDGES:
        room(left, top, right, bottom, "d")
    room(*CHAMBER, "d")
    for left, top, right, bottom in SLUDGE:
        room(left, top, right, bottom, "ʓ")

    # The culvert back to Sewer 1.
    for row in range(5, 8):
        grid[row][0] = "⮜"
    grid[RETURN_EXIT[1]][RETURN_EXIT[0]] = "ሾ"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ሿ"

    # The southern end: collided either side, with a marked opening in the
    # middle where the floor gave way into Sewer 3.
    for col in range(12, 18):
        for row in range(59, HEIGHT):
            grid[row][col] = "V"
        grid[58][col] = "ƻ"
    for col in (14, 15):
        for row in range(59, HEIGHT):
            grid[row][col] = "⮟"
        grid[58][col] = "d"
    # The way back up sets Chuck down on the floor beside the hole, not
    # in it -- standing on a transition tile would bounce him straight
    # back through.
    grid[58][15] = "ቇ"

    for col, row in RATS:
        assert grid[row][col] in {"d", ","}, (col, row, grid[row][col])
        grid[row][col] = "q"
    for col, row in CIGARETTES:
        assert grid[row][col] in {"d", ","}, (col, row, grid[row][col])
        grid[row][col] = "ል"
    furnish_sewer(grid, seed=695)
    return ["".join(row) for row in grid]


SOLID = {"#", "b", "R", "i", "V"}


def _under(char: str) -> str:
    return {"ሾ": "⮜", "ሿ": "d", "q": "d", "ል": ".",
            "ቇ": "⮟"}.get(char, char)


def _flood(rows, start, *, hops):
    """Walk the map; optionally allow the established committed jump,
    which clears exactly one tile of Astral onto safe floor."""
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            step = (col + dc, row + dr)
            land = (col + 2 * dc, row + 2 * dr)
            for point in (step, land) if hops else (step,):
                x, y = point
                if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                    continue
                if point in found:
                    continue
                if point is land:
                    gap = _under(rows[step[1]][step[0]])
                    if gap != "V" or _under(rows[y][x]) in SOLID | {"V"}:
                        continue
                elif _under(rows[y][x]) in SOLID | {"V"}:
                    continue
                found.add(point)
                queue.append(point)
    return found


def validate(rows: list[str]) -> None:
    assert len(rows) == HEIGHT and all(len(row) == WIDTH for row in rows)
    # The opposite shape to Sewer 1, which is wider than it is tall.
    assert HEIGHT > WIDTH

    found = _flood(rows, ARRIVAL, hops=True)
    assert RETURN_EXIT in found
    assert WAYPOINT in found
    for point in (*RATS, *CIGARETTES):
        assert point in found, point
    # No rat waits on top of the waypoint.
    assert WAYPOINT not in set(RATS)

    # The bottom chamber is only reachable by making the jumps.
    landing = (CHAMBER[0] + 2, CHAMBER[1] + 1)
    assert landing in found, landing
    walked = _flood(rows, ARRIVAL, hops=False)
    assert landing not in walked, "the jump course can be walked around"

    # Every gap is exactly one tile wide on the axis it is crossed, so no
    # required jump ever asks for more than the committed jump gives.
    for left, top, right, bottom in GAPS:
        # A gap is crossed across its narrow axis; that axis must be one
        # tile. A wide gap crossed the long way would be unjumpable.
        assert min(right - left, bottom - top) == 0, (left, top)
        assert right - left == 0 or bottom - top == 0, (left, top)

    # ...and no two gaps may meet, which would silently create a two-tile
    # crossing that the committed jump cannot clear.
    void = {(col, row)
            for row in range(HEIGHT) for col in range(WIDTH)
            if _under(rows[row][col]) == "V"}
    for col, row in void:
        # The reserved southern block is collided ground, not a crossing.
        if not 44 <= row < 59:
            continue
        horizontal = {(col - 1, row), (col + 1, row)} & void
        vertical = {(col, row - 1), (col, row + 1)} & void
        assert not (horizontal and vertical), (col, row)

    # Sludge pressures approaches, never a ledge: launching off a one-tile
    # ledge while slowed would not be fair.
    ledge_tiles = {
        (col, row)
        for left, top, right, bottom in LEDGES
        for row in range(top, bottom + 1)
        for col in range(left, right + 1)
    }
    sludge_tiles = {
        (col, row)
        for row in range(HEIGHT) for col in range(WIDTH)
        if rows[row][col] == "ʓ"
    }
    assert sludge_tiles, "the sewer's new hazard never appears"
    assert not (sludge_tiles & ledge_tiles), sorted(sludge_tiles & ledge_tiles)
    # The tiles a jump actually launches from and lands on must be clean,
    # including where the course drops into the chamber.
    landings = set()
    for left, top, right, bottom in GAPS:
        for row in range(top, bottom + 1):
            for col in range(left, right + 1):
                for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    neighbour = (col + dc, row + dr)
                    if not (0 <= neighbour[0] < WIDTH
                            and 0 <= neighbour[1] < HEIGHT):
                        continue
                    if _under(rows[neighbour[1]][neighbour[0]]) not in SOLID | {
                            "V"}:
                        landings.add(neighbour)
    assert not (sludge_tiles & landings), sorted(sludge_tiles & landings)
    # ...and the waypoint sits outside the course entirely.
    assert WAYPOINT not in ledge_tiles and WAYPOINT not in sludge_tiles
    assert WAYPOINT[1] < LEDGES[0][1], "the waypoint is inside the jump course"

    text = "".join(rows)
    assert text.count("ሿ") == 1 and text.count("ሾ") == 1
    assert text.count("q") == len(RATS)
    assert text.count("ል") == len(CIGARETTES)
    for material in ("#", "b", "R", "i", "d", ",", "M", "%", "ƻ", "V",
                     "ʓ"):
        assert material in text, material


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_sewer_2.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
