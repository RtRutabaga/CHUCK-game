"""Generate the authored Cabin grounds and compact exterior landmark."""

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
    # then opens toward the compact cabin's sole south door and fire circle.
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
    _path(grid, (44, 31), (52, 34), 2)
    _path(grid, (52, 34), (59, 37), 2)
    _path(grid, (59, 37), (59, 54), 2)
    _path(grid, (59, 54), (59, 59), 2)

    # The exterior cabin is intentionally much smaller than its interior map.
    # One procedural three-quarter-view landmark carries its roof, walls,
    # windows, porch, and stairs. Collision follows the visible building mass,
    # while a narrow porch corridor reaches the sole south-facing door.
    for y in range(27, 35):
        for x in range(56, 69):
            grid[y][x] = "♟"
    for y in range(32, 35):
        for x in range(58, 62):
            grid[y][x] = "▣"
    for y in range(35, 38):
        for x in range(59, 61):
            grid[y][x] = "↟"
    grid[31][59] = "Ɛ"
    grid[36][59] = "ኂ"
    grid[34][62] = "ℂ"

    # Real-place landmarks from the authored drawing.
    grid[13][18] = "◌"       # circular UFO object at upper-left
    grid[59][59] = "⚉"       # fire circle due south of the front porch
    grid[55][72] = "⌘"       # firewood shed at the lower-right edge

    # The mushroom-light trail hugs the cabin clearing's west side, rather than
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
