"""Unit tests for src/systems/sanity.py and the cigarette pickup.

Run from the project root with:

    python -m tests.test_sanity      (plain asserts, no dependencies)
    pytest                           (if you have pytest)
"""

from src.core import config
from src.entities.pickup import Cigarette
from src.systems.sanity import SanitySystem


def test_starts_at_configured_start() -> None:
    s = SanitySystem()
    assert s.current == config.SANITY_START
    assert s.maximum == config.SANITY_MAX


def test_restore_clamps_at_maximum() -> None:
    s = SanitySystem(start=90)
    s.restore(25)
    assert s.current == s.maximum


def test_damage_clamps_at_zero_and_fires_callback_once_per_hit() -> None:
    fired = []
    s = SanitySystem(on_depleted=lambda: fired.append(1), start=10)
    assert s.damage(25) is True
    assert s.current == 0
    assert fired == [1]


def test_invulnerability_frames_block_repeat_hits() -> None:
    s = SanitySystem(start=100)
    assert s.damage(20) is True
    assert s.current == 80
    assert s.is_invulnerable
    assert s.damage(20) is False   # inside the i-frame window
    assert s.current == 80
    s.update(config.HURT_COOLDOWN)  # window expires
    assert not s.is_invulnerable
    assert s.damage(20) is True
    assert s.current == 60


def test_refill_returns_to_maximum() -> None:
    s = SanitySystem(start=5)
    s.refill()
    assert s.current == s.maximum


def test_lethal_fall_depletes_through_invulnerability() -> None:
    fired = []
    s = SanitySystem(on_depleted=lambda: fired.append(1), start=100)
    s.damage(10)
    assert s.is_invulnerable
    s.deplete()
    assert s.current == 0 and fired == [1]


def test_fraction_matches_current_over_max() -> None:
    s = SanitySystem(start=25)
    assert abs(s.fraction - 25 / config.SANITY_MAX) < 1e-9


def test_cigarette_restores_and_dies() -> None:
    s = SanitySystem(start=40)
    cig = Cigarette(100.0, 100.0)
    cig.on_collect(s)
    assert s.current == 40 + config.CIGARETTE_SANITY_RESTORE
    assert not cig.alive


def test_cigarette_is_centered_on_its_spawn_point() -> None:
    cig = Cigarette(100.0, 60.0)
    assert cig.x + cig.width / 2 == 100.0
    assert cig.y + cig.height / 2 == 60.0


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
    print("All sanity/pickup tests passed.")


if __name__ == "__main__":
    _run_all()
