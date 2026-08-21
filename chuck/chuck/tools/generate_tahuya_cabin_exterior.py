"""Generate the authored two-porch Cabin grounds map."""

from pathlib import Path
import random


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 80
HEIGHT = 64


def _path(grid, start, end, radius=1):
    x0, y0 = start
    x1, y1 = end
    steps = max(abs(x1 - x0), abs(y1 - y0))
    for step in range(steps + 1):
        t = step / max(1, steps)
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        for oy in range(-radius, radius + 1):
            for ox in range(-radius, radius + 1):
                if 0 <= y + oy < HEIGHT and 0 <= x + ox < WIDTH:
                    grid[y + oy][x + ox] = "⌇"


def build_map():
    grid = [["♟" for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # The hand-drawn reference places a broad irregular clearing west of a
    # long north/south cabin.  Keep that silhouette rather than centring the
    # building as a generic game landmark.
    for y in range(4, 60):
        left = 4 + abs(y - 31) // 13
        right = 75 - abs(y - 31) // 20
        for x in range(left, right + 1):
            grid[y][x] = "ᶠ"

    # The western arrival begins as a narrow, slightly wandering foot trail,
    # then opens into the two real branches: north to the back porch and south
    # to the front porch/fire circle.
    west_approach = (
        ((5, 33), (10, 31)),
        ((10, 31), (16, 32)),
        ((16, 32), (23, 30)),
        ((23, 30), (30, 32)),
        ((30, 32), (37, 30)),
        ((37, 30), (44, 31)),
    )
    for start, end in west_approach:
        _path(grid, start, end, 0)
    _path(grid, (44, 31), (45, 7), 2)
    _path(grid, (45, 7), (58, 5), 2)
    _path(grid, (44, 31), (45, 47), 2)
    _path(grid, (45, 47), (59, 54), 2)
    _path(grid, (59, 54), (59, 59), 2)

    # Cabin shell: the interior fits inside this 21x33 exterior footprint.
    # Roof mass above a front wall creates the established three-quarter view.
    for y in range(12, 38):
        for x in range(49, 70):
            grid[y][x] = "▧"
    for y in range(38, 45):
        for x in range(49, 70):
            grid[y][x] = "▨"
    for y in range(12, 15):
        for x in range(58, 61):
            grid[y][x] = "◼"
    for y in range(41, 45):
        for x in range(58, 61):
            grid[y][x] = "◼"

    # Both raised porches are fully playable now.  Their central stairs line
    # up with the two doorway recesses exactly, ready for the interior pass.
    for y in range(7, 12):
        for x in range(50, 69):
            grid[y][x] = "▣"
    for y in range(4, 7):
        for x in range(58, 61):
            grid[y][x] = "↟"
    for y in range(45, 51):
        for x in range(48, 71):
            grid[y][x] = "▣"
    for y in range(51, 55):
        for x in range(58, 61):
            grid[y][x] = "↟"

    # The full width of each human-scale black recess is a live threshold.
    # Return arrivals remain centered on the matching porch, one tile clear.
    for x in range(58, 61):
        grid[12][x] = "Ɣ"
    grid[10][59] = "ኃ"
    for x in range(58, 61):
        grid[44][x] = "Ɛ"
    grid[47][59] = "ኂ"

    # Real-place landmarks from the authored drawing.
    grid[13][18] = "◌"       # circular UFO object at upper-left
    grid[59][59] = "⚉"       # fire circle due south of the front porch
    grid[55][72] = "⌘"       # firewood shed at the lower-right edge

    # The mushroom-light trail hugs the cabin's west side, rather than
    # wandering through the middle of the clearing.
    for x, y in ((44, 13), (45, 20), (44, 27), (45, 34),
                 (44, 41), (45, 48), (52, 55)):
        grid[y][x] = "✦"

    # A dense but irregular Douglas-fir stand fills the west side. A fixed
    # authored seed gives natural spacing without a tree-farm grid and keeps
    # the same forest on every load.
    rng = random.Random(1204)
    candidates = [
        (x, y)
        for y in range(5, 60)
        for x in range(6, 44)
        if grid[y][x] == "ᶠ"
    ]
    rng.shuffle(candidates)
    firs = []
    for x, y in candidates:
        if any(abs(x - px) <= 1 and abs(y - py) <= 1 for px, py in firs):
            continue
        grid[y][x] = "♣"
        firs.append((x, y))
        if len(firs) == 118:
            break
    for x, y in ((73, 12), (75, 45)):
        if grid[y][x] == "ᶠ":
            grid[y][x] = "♣"

    # A handful of the established scratchable cigarette-grass tufts soften
    # the clearing and reward inspecting the tighter west approach.
    for x, y in ((12, 29), (18, 34), (26, 28), (33, 34),
                 (40, 28), (47, 18), (47, 43), (54, 56)):
        if grid[y][x] in {"ᶠ", "♣"}:
            grid[y][x] = "ʛ"

    # The cutscene emerges onto the western trail; the one Ashtray is close
    # enough to discover naturally but does not interrupt the reveal.
    grid[31][10] = "ኀ"
    grid[36][24] = "ኁ"
    return ["".join(row) for row in grid]


def main():
    output = ROOT / "assets" / "maps" / "tahuya_cabin_exterior.txt"
    output.write_text("\n".join(build_map()) + "\n", encoding="utf-8")
    print(f"Wrote {output} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
