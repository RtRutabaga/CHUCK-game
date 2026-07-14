"""Unit tests for standing props and depth sorting.

Run from the project root with:

    python -m tests.test_props       (pure Python, no pygame needed)
    pytest                           (if you have pytest)
"""

from src.core import config
from src.entities.prop import Prop

TS = config.TILE_SIZE


class FakeImage:
    def __init__(self, w, h): self._s = (w, h)
    def get_size(self): return self._s


class FakeAssets:
    def __init__(self, w, h): self._img = FakeImage(w, h)
    def image(self, path): return self._img


def test_prop_anchors_to_tile_bottom_and_centers() -> None:
    p = Prop("barrel", col=9, row=4, assets=FakeAssets(14, 19))
    assert p.sort_y == 5 * TS                    # tile bottom edge
    assert p._draw_y == 5 * TS - 19              # sprite bottom aligned
    assert p._draw_x == 9 * TS + (TS - 14) // 2  # centered on the tile


def test_prop_taller_than_a_tile_rises_above_it() -> None:
    p = Prop("crate", col=2, row=3, assets=FakeAssets(16, 20))
    assert p._draw_y < 3 * TS  # top pokes above the tile's top edge


def test_bobert_barrel_is_a_valid_prop_kind() -> None:
    p = Prop("bobert_barrel", col=10, row=4, assets=FakeAssets(16, 24))
    assert p.sort_y == 5 * TS
    assert p._draw_y == 5 * TS - 24  # tall: head rises well over the tile


def test_tavern_door_is_human_scale() -> None:
    from src.core import config
    door = Prop("tavern_door", col=44, row=17, assets=FakeAssets(32, 34))
    assert door.dialogue_id is None  # it's a door; it has nothing to say
    x, y, w, h = door.interaction_bounds()
    # Taller than the dock worker: a human fits through.
    assert 34 >= config.NPC_FRAME_H + 4
    # Sprite wider than its tile: centered, spanning the old DD width.
    assert door._draw_x == 44 * 16 + (16 - 32) // 2


def test_chimney_is_a_valid_mute_prop() -> None:
    p = Prop("chimney", col=37, row=9, assets=FakeAssets(12, 22))
    assert p.dialogue_id is None
    assert p._draw_y == 10 * TS - 22  # rises above its roof tile


def test_house_door_is_a_valid_mute_prop() -> None:
    p = Prop("house_door", col=14, row=4, assets=FakeAssets(14, 20))
    assert p.dialogue_id is None  # decorative; these homes stay shut
    assert p._draw_y == 5 * TS - 20




def test_stall_props_are_valid_and_mute() -> None:
    for kind, w, h in (("stall_post", 6, 26), ("stall_table", 20, 16),
                       ("crate_green", 16, 20), ("crate_red", 16, 20),
                       ("crate_orange", 16, 20)):
        p = Prop(kind, col=45, row=29, assets=FakeAssets(w, h))
        assert p.dialogue_id is None
        assert p.sort_y == 30 * TS


def test_grate_carries_a_choice_not_a_line() -> None:
    grate = Prop("sewer_grate", col=52, row=6, assets=FakeAssets(16, 13))
    assert grate.choice_id == "sewer_grate"
    assert grate.dialogue_id is None       # a prop asks OR tells
    sign = Prop("herod_sign", col=43, row=18, assets=FakeAssets(16, 24))
    assert sign.choice_id is None


def test_unknown_prop_kind_is_loud() -> None:
    try:
        Prop("piano", 0, 0, FakeAssets(8, 8))
    except ValueError as exc:
        assert "piano" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_prop_dialogue_mapping() -> None:
    bobert = Prop("bobert_barrel", 10, 4, FakeAssets(16, 24))
    sign = Prop("herod_sign", 43, 18, FakeAssets(16, 24))
    barrel = Prop("barrel", 9, 4, FakeAssets(14, 19))
    crate = Prop("crate", 14, 6, FakeAssets(16, 20))
    assert bobert.dialogue_id == "bobert_sleeping"
    assert sign.dialogue_id == "herod_sign"
    assert barrel.dialogue_id is None and crate.dialogue_id is None


def test_prop_interaction_bounds_cover_the_sprite() -> None:
    p = Prop("herod_sign", col=43, row=18, assets=FakeAssets(16, 24))
    x, y, w, h = p.interaction_bounds()
    assert x <= p._draw_x and y <= p._draw_y
    assert w >= 16 and h >= 24


def test_depth_order_is_by_feet() -> None:
    class D:
        def __init__(self, sy): self.sort_y = sy
    a, b, c = D(80.0), D(64.0), D(96.0)
    ordered = sorted([a, b, c], key=lambda d: d.sort_y)
    assert ordered == [b, a, c]  # northmost first, southmost last


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
    print("All prop tests passed.")


if __name__ == "__main__":
    _run_all()
