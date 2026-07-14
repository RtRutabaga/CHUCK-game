"""Shared text-grid sprite rendering (dev tooling, requires Pillow).

Both sprite generators (Chuck, the cat, and whoever comes next) define
their art as character grids and call render_sheet(). Validation is
loud: wrong grid sizes or unknown pixel characters raise immediately.
"""

from __future__ import annotations

from PIL import Image

Palette = dict[str, tuple[int, int, int, int]]


def parse_frame(
    grid: str, name: str, frame_w: int, frame_h: int, palette: Palette
) -> list[str]:
    """Validate a text grid and return its rows. Fails loudly."""
    rows = [line for line in grid.splitlines() if line.strip()]
    if len(rows) != frame_h:
        raise ValueError(f"{name}: expected {frame_h} rows, got {len(rows)}")
    for r_i, row in enumerate(rows):
        if len(row) != frame_w:
            raise ValueError(
                f"{name}: row {r_i} has {len(row)} chars, expected {frame_w}"
            )
        for c_i, char in enumerate(row):
            if char not in palette:
                raise ValueError(
                    f"{name}: unknown pixel char {char!r} at row {r_i}, col {c_i}"
                )
    return rows


def render_sheet(
    sheet: list[list[str]],
    names: list[list[str]],
    frame_w: int,
    frame_h: int,
    palette: Palette,
) -> Image.Image:
    """Render a [row][col] grid of text-grid frames into one image."""
    img = Image.new(
        "RGBA", (frame_w * len(sheet[0]), frame_h * len(sheet)), (0, 0, 0, 0)
    )
    for row_i, frame_row in enumerate(sheet):
        for col_i, grid in enumerate(frame_row):
            rows = parse_frame(
                grid, names[row_i][col_i], frame_w, frame_h, palette
            )
            for y, row in enumerate(rows):
                for x, char in enumerate(row):
                    img.putpixel(
                        (col_i * frame_w + x, row_i * frame_h + y), palette[char]
                    )
    return img
