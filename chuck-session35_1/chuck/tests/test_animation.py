"""Unit tests for src/core/animation.py.

Run from the project root with:

    python -m tests.test_animation      (plain asserts, no dependencies)
    pytest                              (if you have pytest)
"""

from src.core.animation import Animation


def test_starts_on_first_frame() -> None:
    a = Animation(["a", "b", "c"], 0.1)
    assert a.current_frame == "a"


def test_advances_at_frame_duration() -> None:
    a = Animation(["a", "b", "c"], 0.1)
    a.update(0.1)
    assert a.current_frame == "b"
    a.update(0.1)
    assert a.current_frame == "c"


def test_accumulates_small_dts() -> None:
    a = Animation(["a", "b"], 0.1)
    for _ in range(6):  # 6 * 0.02 = 0.12
        a.update(0.02)
    assert a.current_frame == "b"


def test_loops_by_default() -> None:
    a = Animation(["a", "b", "c"], 0.1)
    a.update(0.35)  # past the end
    assert a.current_frame == "a"
    assert not a.finished


def test_non_loop_holds_last_frame_and_finishes() -> None:
    a = Animation(["a", "b", "c"], 0.1, loop=False)
    a.update(1.0)
    assert a.current_frame == "c"
    assert a.finished


def test_reset_restarts() -> None:
    a = Animation(["a", "b"], 0.1)
    a.update(0.15)
    assert a.current_frame == "b"
    a.reset()
    assert a.current_frame == "a"


def test_rejects_empty_frames_and_bad_duration() -> None:
    for bad in (lambda: Animation([], 0.1), lambda: Animation(["a"], 0.0)):
        try:
            bad()
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")


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
    print("All animation tests passed.")


if __name__ == "__main__":
    _run_all()
