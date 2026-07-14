"""Unit tests for the shared interaction search and the tutorial hint.

Run from the project root with:

    python -m tests.test_tutorial    (pure Python, no pygame needed)
    pytest                           (if you have pytest)

The point of these: the hint and the interact key must agree, always.
If the hint says "Press E" and E does nothing, that's a lie to the
player — so both read find_target(), and it's tested directly.
"""

from src.core import config
from src.systems.interaction import find_target, in_reach, rects_overlap


class FakeTarget:
    """An NPC/prop stand-in: a bounds box and maybe a line to say."""

    def __init__(self, x, y, w=16, h=30, dialogue_id="x"):
        self._b = (x, y, w, h)
        self.dialogue_id = dialogue_id

    def interaction_bounds(self):
        return self._b


def test_rects_overlap_handles_tuples_and_edges() -> None:
    assert rects_overlap((0, 0, 10, 10), (5, 5, 10, 10))
    assert not rects_overlap((0, 0, 10, 10), (10, 0, 10, 10))  # flush edge
    assert not rects_overlap((0, 0, 10, 10), (0, 20, 10, 10))


def test_in_reach_by_probe_or_by_standing_on_it() -> None:
    npc = FakeTarget(100, 100)
    far_probe, far_box = (0, 0, 12, 8), (0, 0, 10, 8)
    assert not in_reach(npc, far_probe, far_box)
    # Facing it from below: the probe touches.
    assert in_reach(npc, (104, 124, 12, 8), far_box)
    # Standing on it (NPCs aren't solid): the body overlaps.
    assert in_reach(npc, far_probe, (104, 110, 10, 8))


def test_npcs_answer_before_props() -> None:
    npc = FakeTarget(100, 100, dialogue_id="guard")
    prop = FakeTarget(100, 100, dialogue_id="herod_sign")
    box = (104, 110, 10, 8)
    assert find_target((0, 0, 1, 1), box, [npc], [prop]) is npc


def test_props_with_a_choice_are_targets_too() -> None:
    # The grate has no dialogue_id — it has a choice_id. The hint and
    # the key must still offer it.
    grate = FakeTarget(100, 100, dialogue_id=None)
    grate.choice_id = "sewer_grate"
    box = (104, 110, 10, 8)
    assert find_target((0, 0, 1, 1), box, [], [grate]) is grate


def test_mute_props_are_never_targets() -> None:
    crate = FakeTarget(100, 100, dialogue_id=None)
    box = (104, 110, 10, 8)
    assert find_target((0, 0, 1, 1), box, [], [crate]) is None


def test_no_target_when_nothing_is_near() -> None:
    assert find_target((0, 0, 12, 8), (0, 0, 10, 8), [], []) is None


def test_hint_is_scoped_to_the_tutorial_areas_only() -> None:
    # The hint must not become permanent instructional UI (Phase 2 doc).
    assert "waterdeep_docks" in config.TUTORIAL_MAPS
    assert "sewer" in config.TUTORIAL_MAPS
    assert len(config.TUTORIAL_MAPS) == 2


def test_hint_text_names_the_real_interact_key() -> None:
    # If the wording says E, E had better be bound to interact. The
    # bindings live in src/core/input.py (which imports pygame, so it
    # can't be imported headless); read the source instead.
    import re
    from pathlib import Path

    key = re.search(r"Press (\w+) to interact", config.HINT_INTERACT)
    assert key and key.group(1) == "E"
    src = (Path(__file__).resolve().parents[1]
           / "src" / "core" / "input.py").read_text()
    assert re.search(r"pygame\.K_e:\s*\"interact\"", src), \
        "hint says E but E is not bound to interact"


def test_space_is_jump_not_interact() -> None:
    import re
    from pathlib import Path

    assert config.HINT_JUMP == "Press SPACE to jump"
    src = (Path(__file__).resolve().parents[1]
           / "src" / "core" / "input.py").read_text()
    assert re.search(r"pygame\.K_SPACE:\s*\"jump\"", src)
    assert not re.search(r"pygame\.K_SPACE:\s*\"interact\"", src)


def test_scratch_hint_names_the_f_binding() -> None:
    import re
    from pathlib import Path

    assert config.HINT_SCRATCH == "Press F to scratch"
    src = (Path(__file__).resolve().parents[1]
           / "src" / "core" / "input.py").read_text()
    assert re.search(r"pygame\.K_f:\s*\"scratch\"", src)


def test_anchor_hint_uses_the_requested_tutorial_text() -> None:
    assert config.HINT_ANCHOR == "Ashtrays save your progress"


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
    print("All tutorial tests passed.")


if __name__ == "__main__":
    _run_all()
