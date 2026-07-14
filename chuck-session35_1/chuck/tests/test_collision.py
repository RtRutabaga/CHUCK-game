"""Unit tests for src/world/collision.py.

Run from the project root with:

    python -m tests.test_collision      (plain asserts, no dependencies)
    pytest                              (if you have pytest)

These tests use a fake grid instead of a real TileMap, so they need
neither pygame nor any asset files.
"""

from src.core import config
from src.world.collision import move_and_collide

TS = config.TILE_SIZE  # 16


class FakeGrid:
    """A grid where a supplied set of (col, row) tiles are solid."""

    def __init__(self, solid: set[tuple[int, int]]) -> None:
        self._solid = solid

    def is_solid(self, col: int, row: int) -> bool:
        return (col, row) in self._solid


def test_free_movement_is_unblocked() -> None:
    grid = FakeGrid(set())
    x, y = move_and_collide(20.0, 20.0, 10, 8, 5.0, -3.0, grid)
    assert (x, y) == (25.0, 17.0), (x, y)


def test_moving_right_stops_flush_against_wall() -> None:
    # Wall column at col 3 (pixels 48..63). Body height spans row 1 only.
    grid = FakeGrid({(3, 1)})
    x, y = move_and_collide(30.0, 20.0, 10, 8, 40.0, 0.0, grid)
    assert x == 3 * TS - 10, x  # flush: right edge at pixel 48
    assert y == 20.0


def test_moving_left_stops_flush_against_wall() -> None:
    grid = FakeGrid({(1, 1)})  # wall at pixels 16..31
    x, y = move_and_collide(40.0, 20.0, 10, 8, -40.0, 0.0, grid)
    assert x == 2 * TS, x  # flush: left edge at pixel 32
    assert y == 20.0


def test_moving_down_stops_flush_against_floor_tile() -> None:
    grid = FakeGrid({(1, 3)})  # solid at rows of pixels 48..63
    x, y = move_and_collide(20.0, 30.0, 10, 8, 0.0, 40.0, grid)
    assert y == 3 * TS - 8, y
    assert x == 20.0


def test_moving_up_stops_flush_against_ceiling_tile() -> None:
    grid = FakeGrid({(1, 1)})
    x, y = move_and_collide(20.0, 40.0, 10, 8, 0.0, -40.0, grid)
    assert y == 2 * TS, y
    assert x == 20.0


def test_diagonal_into_wall_slides_along_it() -> None:
    # Solid wall column at col 3, rows 0..5. Moving down-right should
    # stop at the wall horizontally but keep the full vertical motion.
    grid = FakeGrid({(3, r) for r in range(6)})
    x, y = move_and_collide(30.0, 20.0, 10, 8, 40.0, 10.0, grid)
    assert x == 3 * TS - 10, x  # blocked
    assert y == 30.0            # slid


def test_edge_on_tile_boundary_does_not_snag() -> None:
    # Hitbox bottom edge exactly on a row boundary must not count as
    # occupying the next row: wall at (3, 2) shouldn't block a body in
    # rows 1..1 whose bottom edge sits at exactly y=32.
    grid = FakeGrid({(3, 2)})
    x, y = move_and_collide(20.0, 24.0, 10, 8, 40.0, 0.0, grid)  # y+h == 32
    assert x == 60.0, x  # moved freely


def test_wide_body_checks_all_spanned_columns() -> None:
    # Body spans cols 1..2; solid below at (2, 3) must block descent.
    grid = FakeGrid({(2, 3)})
    x, y = move_and_collide(24.0, 30.0, 20, 8, 0.0, 40.0, grid)
    assert y == 3 * TS - 8, y


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All collision tests passed.")


if __name__ == "__main__":
    _run_all()
