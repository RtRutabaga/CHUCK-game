"""Shared authored-map helpers for Phase 11 city blocks."""


def paint_office(
    grid: list[list[str]], left: int, top: int, right: int, bottom: int,
) -> None:
    """Paint one large, indivisible three-quarter-view office mass."""
    facade_top = bottom - 8
    for row in range(top, bottom + 1):
        for col in range(left, right + 1):
            if row < facade_top:
                char = "#"
            elif row == facade_top:
                char = "▱"
            elif col in (left, right):
                char = "▥"
            elif row == bottom:
                char = "▤"
            else:
                char = "w" if (col - left + row) % 3 else "▤"
            grid[row][col] = char
