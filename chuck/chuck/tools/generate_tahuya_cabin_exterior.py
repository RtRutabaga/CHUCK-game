"""Generate the authored two-porch Tahuya cabin grounds map."""

from pathlib import Path


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

    # Winding approach and its two real branches: north to the back porch,
    # south to the front porch and fire circle.
    _path(grid, (9, 31), (28, 31), 2)
    _path(grid, (28, 31), (39, 22), 2)
    _path(grid, (39, 22), (57, 5), 2)
    _path(grid, (29, 32), (37, 43), 2)
    _path(grid, (37, 43), (59, 54), 2)
    _path(grid, (36, 44), (33, 50), 2)

    # Cabin shell: the future interior must fit inside this 21x33 exterior
    # footprint.  Roof mass above a front wall creates the established
    # three-quarter view; the dark recesses are visible but inert this pass.
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

    # Real-place landmarks from the authored drawing.
    grid[13][18] = "◌"       # circular UFO object at upper-left
    grid[49][34] = "⚉"       # fire circle west of the cabin
    grid[55][72] = "⌘"       # firewood shed at the lower-right edge

    # Unsynchronised colour-changing mushroom lights follow the drawn route.
    for x, y in ((15, 29), (24, 33), (34, 27), (43, 18),
                 (39, 42), (48, 48), (61, 54)):
        grid[y][x] = "✦"

    # Tall fir silhouettes dress the solid edge without changing the clearing.
    for x, y in ((8, 8), (15, 5), (28, 5), (39, 6), (73, 12),
                 (7, 47), (15, 57), (27, 59), (43, 58), (75, 45)):
        grid[y][x] = "♣"

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
