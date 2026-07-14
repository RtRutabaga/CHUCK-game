"""Collision.

Responsibilities:
    * Resolve entity movement against solid tiles, one axis at a time
      (move X, resolve, move Y, resolve) — the standard approach that
      makes sliding along walls feel natural and dependable.
    * Detect entity-vs-entity overlaps (Chuck touching a cigarette,
      a cat's pounce hitting Chuck, stepping on an Astral Anchor).

This module deliberately does NOT import pygame at runtime, so it can
be unit-tested without a display or pygame installed. It only needs an
object with an `is_solid(col, row) -> bool` method (the TileMap).
"""

from __future__ import annotations

from typing import Protocol

from src.core import config

# Nudges edge coordinates inward so a hitbox whose edge sits exactly on
# a tile boundary doesn't count as touching the next tile over.
_EPS = 1e-4


class SolidGrid(Protocol):
    """Anything that can answer 'is this tile solid?' (e.g. TileMap)."""

    def is_solid(self, col: int, row: int) -> bool: ...


def move_and_collide(
    x: float,
    y: float,
    width: float,
    height: float,
    dx: float,
    dy: float,
    grid: SolidGrid,
) -> tuple[float, float]:
    """Move a hitbox by (dx, dy), stopping flush against solid tiles.

    Positions are world pixels (top-left origin). Returns the resolved
    (x, y). Axes are resolved separately so pressing into a wall while
    also moving along it slides instead of sticking.

    Movement is swept: every tile the leading edge crosses is checked,
    so even a large dt (lag spike) can't tunnel through a thin wall.
    """
    ts = config.TILE_SIZE

    # ----- X axis -----
    if dx != 0.0:
        old_x = x
        x += dx
        top_row = int(y // ts)
        bottom_row = int((y + height - _EPS) // ts)
        if dx > 0.0:
            first_col = int((old_x + width - _EPS) // ts) + 1  # first newly entered
            last_col = int((x + width - _EPS) // ts)
            for col in range(first_col, last_col + 1):
                if any(grid.is_solid(col, r) for r in range(top_row, bottom_row + 1)):
                    x = col * ts - width
                    break
        else:
            first_col = int(old_x // ts) - 1
            last_col = int(x // ts)
            for col in range(first_col, last_col - 1, -1):
                if any(grid.is_solid(col, r) for r in range(top_row, bottom_row + 1)):
                    x = (col + 1) * ts
                    break

    # ----- Y axis -----
    if dy != 0.0:
        old_y = y
        y += dy
        left_col = int(x // ts)
        right_col = int((x + width - _EPS) // ts)
        if dy > 0.0:
            first_row = int((old_y + height - _EPS) // ts) + 1
            last_row = int((y + height - _EPS) // ts)
            for row in range(first_row, last_row + 1):
                if any(grid.is_solid(c, row) for c in range(left_col, right_col + 1)):
                    y = row * ts - height
                    break
        else:
            first_row = int(old_y // ts) - 1
            last_row = int(y // ts)
            for row in range(first_row, last_row - 1, -1):
                if any(grid.is_solid(c, row) for c in range(left_col, right_col + 1)):
                    y = (row + 1) * ts
                    break

    return x, y


def overlaps(a, b) -> bool:
    """Return True if two pygame.Rect-like hitboxes intersect."""
    return a.colliderect(b)
