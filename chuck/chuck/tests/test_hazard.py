"""Unit tests for the cat hazard and the Astral Anchor system.

Run from the project root with:

    python -m tests.test_hazard      (plain asserts, no dependencies)
    pytest                           (if you have pytest)
"""

from src.core import config
from src.entities.hazard import Cat

TS = config.TILE_SIZE


class FakeGrid:
    """Solid everywhere except a horizontal corridor of open columns."""

    def __init__(self, open_cols: range, row: int) -> None:
        self._open_cols, self._row = open_cols, row

    def is_solid(self, col: int, row: int) -> bool:
        return not (row == self._row and col in self._open_cols)


def _corridor_cat() -> Cat:
    # Corridor: columns 2..7 of row 1 are open (pixels 32..127).
    cat = Cat(center_x=5 * TS, center_y=1 * TS + config.CAT_HITBOX_H / 2)
    cat.tilemap = FakeGrid(range(2, 8), 1)
    return cat


def test_cat_walks_its_direction() -> None:
    cat = _corridor_cat()
    x0 = cat.x
    cat.update(0.1)
    assert cat.x < x0  # starts walking left
    assert cat.direction == -1


def test_cat_turns_around_at_walls_both_ends() -> None:
    cat = _corridor_cat()
    for _ in range(200):  # plenty of time to hit the left wall
        cat.update(0.05)
        if cat.direction == 1:
            break
    assert cat.direction == 1, "never turned at the left wall"
    assert cat.x == 2 * TS, f"not flush at left wall: {cat.x}"
    for _ in range(400):
        cat.update(0.05)
        if cat.direction == -1:
            break
    assert cat.direction == -1, "never turned at the right wall"
    assert cat.x == 8 * TS - cat.width, f"not flush at right wall: {cat.x}"


def test_cat_stays_on_its_row() -> None:
    cat = _corridor_cat()
    y0 = cat.y
    for _ in range(300):
        cat.update(0.05)
    assert cat.y == y0


def test_the_respawn_point_is_where_he_came_in_and_stays_there() -> None:
    """It used to move when he touched an door. It does not now.

    One respawn point per visit to a map, set on arrival, unchanged for
    as long as he is in there.
    """
    from src.systems.respawn import RespawnPoint

    point = RespawnPoint((10.0, 20.0), "waterdeep_start")
    assert point.position_for_chuck() == (10.0, 20.0)
    assert not hasattr(point, "activate"), (
        "nothing may move the respawn point away from the door")


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


if __name__ == "__main__":
    _run_all()
