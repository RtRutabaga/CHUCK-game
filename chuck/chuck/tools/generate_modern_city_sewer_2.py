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
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 46
HEIGHT = 62

ARRIVAL = (5, 6)
RETURN_EXIT = (0, 6)
ANCHOR = (9, 19)
FUTURE_EXIT = (14, 61)

RATS = ((10, 13), (22, 24), (34, 34), (33, 42), (15, 52), (12, 22))
CIGARETTES = ((12, 8), (35, 30), (14, 56))


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
    room(10, 38, 20, 58)       # third shaft, down to the collided end
    room(10, 55, 24, 58)

    # A slab walkway runs beside the runoff wherever the shaft is wide
    # enough to carry both, so the descent still reads as maintained.
    for row in range(10, 24):
        grid[row][7] = ","
        grid[row][8] = ","
    for col in range(14, 30):
        grid[25][col] = ","
        grid[26][col] = ","
    for row in range(45, 58):
        grid[row][11] = ","
        grid[row][12] = ","
    for row in range(11, 23):
        grid[row][13] = "%"
    for row in range(27, 43):
        grid[row][37] = "%"
    for row in range(46, 57):
        grid[row][19] = "%"
    for col, row in ((9, 12), (11, 22), (24, 24), (35, 29),
                     (32, 41), (17, 47), (14, 57), (21, 56)):
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

    # The culvert back to Sewer 1, and the Ashtray on the first landing.
    for row in range(5, 8):
        grid[row][0] = "⮜"
    grid[RETURN_EXIT[1]][RETURN_EXIT[0]] = "ሾ"
    grid[ARRIVAL[1]][ARRIVAL[0]] = "ሿ"
    grid[ANCHOR[1]][ANCHOR[0]] = "ቀ"

    # The southern continuation is still collided, marked before it drops.
    for col in range(12, 18):
        for row in range(59, HEIGHT):
            grid[row][col] = "V"
        grid[58][col] = "ƻ"

    for col, row in RATS:
        assert grid[row][col] in {"d", ","}, (col, row, grid[row][col])
        grid[row][col] = "q"
    for col, row in CIGARETTES:
        assert grid[row][col] in {"d", ","}, (col, row, grid[row][col])
        grid[row][col] = "ል"
    return ["".join(row) for row in grid]


SOLID = {"#", "b", "R", "i", "V"}


def _under(char: str) -> str:
    return {"ሾ": "⮜", "ሿ": "d", "ቀ": "d", "q": "d", "ል": "."}.get(char, char)


def validate(rows: list[str]) -> None:
    assert len(rows) == HEIGHT and all(len(row) == WIDTH for row in rows)
    # The opposite shape to Sewer 1, which is wider than it is tall.
    assert HEIGHT > WIDTH

    found = {ARRIVAL}
    queue = deque([ARRIVAL])
    while queue:
        col, row = queue.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT) or point in found:
                continue
            if _under(rows[y][x]) in SOLID:
                continue
            found.add(point)
            queue.append(point)

    assert RETURN_EXIT in found
    assert ANCHOR in found
    for point in (*RATS, *CIGARETTES):
        assert point in found, point
    # No rat waits on top of the Ashtray Chuck respawns at.
    assert ANCHOR not in set(RATS)

    text = "".join(rows)
    assert text.count("ቀ") == 1
    assert text.count("ሿ") == 1 and text.count("ሾ") == 1
    assert text.count("q") == len(RATS)
    assert text.count("ል") == len(CIGARETTES)
    for material in ("#", "b", "R", "i", "d", ",", "M", "%", "ƻ", "V"):
        assert material in text, material
    # Sludge and the jump sequence are a later slice; nothing here yet.
    assert "≈" not in text


def main() -> None:
    rows = build_map()
    validate(rows)
    output = ROOT / "assets" / "maps" / "modern_city_sewer_2.txt"
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
