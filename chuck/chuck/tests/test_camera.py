"""Unit tests for src/world/camera.py.

Run from the project root with:

    python -m tests.test_camera      (plain asserts, no dependencies)
    pytest                           (if you have pytest)
"""

from src.world.camera import Camera

VIEW_W, VIEW_H = 320, 180
MAP_W, MAP_H = 640, 384  # the expanded docks


class Dummy:
    """Stand-in target with an Entity-shaped position."""

    def __init__(self, x: float, y: float, w: int = 10, h: int = 8) -> None:
        self.x, self.y, self.width, self.height = x, y, w, h


def _camera() -> Camera:
    cam = Camera(VIEW_W, VIEW_H)
    cam.set_bounds(MAP_W, MAP_H)
    return cam


def test_first_update_snaps_to_target() -> None:
    cam = _camera()
    target = Dummy(315.0, 188.0)  # center (320, 192)
    cam.follow(target)
    cam.update(0.016)
    assert cam.offset == (320 - VIEW_W // 2, 192 - VIEW_H // 2), cam.offset


def test_clamps_at_top_left() -> None:
    cam = _camera()
    cam.follow(Dummy(5.0, 5.0))
    cam.update(0.016)
    assert cam.offset == (0, 0), cam.offset


def test_clamps_at_bottom_right() -> None:
    cam = _camera()
    cam.follow(Dummy(MAP_W - 15.0, MAP_H - 10.0))
    cam.update(0.016)
    assert cam.offset == (MAP_W - VIEW_W, MAP_H - VIEW_H), cam.offset


def test_follow_is_smooth_not_teleporting() -> None:
    cam = _camera()
    target = Dummy(315.0, 188.0)
    cam.follow(target)
    cam.update(0.016)  # snap
    start_x = cam.x
    target.x += 100.0
    cam.update(0.016)
    moved = cam.x - start_x
    assert 0.0 < moved < 100.0, moved  # approaching, not jumping


def test_converges_on_stationary_target() -> None:
    cam = _camera()
    target = Dummy(315.0, 188.0)
    cam.follow(target)
    cam.update(0.016)
    target.x += 60.0
    for _ in range(300):  # ~5 seconds
        cam.update(0.016)
    desired = (target.x + target.width / 2) - VIEW_W / 2
    assert abs(cam.x - desired) < 0.5, (cam.x, desired)


def test_map_smaller_than_view_pins_top_left() -> None:
    cam = Camera(VIEW_W, VIEW_H)
    cam.set_bounds(160, 100)
    cam.follow(Dummy(80.0, 50.0))
    cam.update(0.016)
    assert cam.offset == (0, 0), cam.offset


def test_smoothing_is_framerate_independent() -> None:
    # One 0.1s step should land (nearly) where ten 0.01s steps land.
    a = _camera()
    b = _camera()
    ta, tb = Dummy(50.0, 50.0), Dummy(50.0, 50.0)
    a.follow(ta), b.follow(tb)
    a.update(0.016), b.update(0.016)  # snap both
    ta.x = tb.x = 250.0
    a.update(0.1)
    for _ in range(10):
        b.update(0.01)
    assert abs(a.x - b.x) < 1.0, (a.x, b.x)


def test_settle_is_finite_monotone_and_shake_free() -> None:
    # After the target stops, the camera must (a) never reverse, and
    # (b) arrive EXACTLY in finite frames and then hold bit-stable —
    # even with jittery frame times (the vsync/tick beat). This is the
    # regression test for the stop-shake.
    cam = Camera(VIEW_W, VIEW_H)
    cam.set_bounds(2000, 2000)
    target = Dummy(x=700.3, y=500.7)
    cam.follow(target)
    cam.update(0.016)          # snap frame
    target.x += 200            # target moved, then stopped for good
    dts = [0.012, 0.021] * 200 # alternating frame times
    last_ox, settled_at = cam.offset[0], None
    for i, dt in enumerate(dts):
        cam.update(dt)
        ox = cam.offset[0]
        assert ox >= last_ox, f"camera reversed at frame {i}"
        last_ox = ox
        if settled_at is None and cam.x == (
            target.x + target.width / 2 - VIEW_W / 2
        ):
            settled_at = i
    assert settled_at is not None and settled_at < 300, settled_at
    # And once settled, further jittery frames change nothing.
    frozen = cam.offset
    for dt in (0.009, 0.033, 0.016, 0.021):
        cam.update(dt)
        assert cam.offset == frozen


def test_offset_is_always_whole_pixels() -> None:
    # The camera position stays float (movement feel), but the render
    # offset must be integer so every world-to-screen draw lands on
    # whole native pixels — no subpixel shimmer inside the surface.
    cam = Camera(VIEW_W, VIEW_H)
    cam.x, cam.y = 123.456, 78.999
    ox, oy = cam.offset
    assert isinstance(ox, int) and isinstance(oy, int)
    assert (ox, oy) == (123, 79)


def test_shared_approach_helper_is_fps_independent() -> None:
    from src.core.mathutil import approach

    a = approach(0.0, 1.0, 2.5, 0.1)
    b = 0.0
    for _ in range(10):
        b = approach(b, 1.0, 2.5, 0.01)
    assert abs(a - b) < 0.01


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
    print("All camera tests passed.")


if __name__ == "__main__":
    _run_all()
