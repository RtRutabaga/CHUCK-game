"""Unit tests for the dialogue choice system (data + validation).

Run from the project root with:

    python -m tests.test_choice      (pure Python, no pygame needed)
    pytest                           (if you have pytest)
"""

import json
import tempfile
from pathlib import Path

from src.scenes.dialogue_scene import DialogueScene
from src.systems.choice import (
    KNOWN_CHOICE_ACTIONS, Choice, ChoiceSystem, Option,
)
from src.systems.dialogue import DialogueSystem


def _write(data: dict) -> Path:
    d = Path(tempfile.mkdtemp())
    (d / "test.json").write_text(json.dumps(data), encoding="utf-8")
    return d


_VALID = {
    "grate": {
        "prompt": "Jump in?",
        "options": [
            {"label": "YES", "dialogue": "yes_lines"},
            {"label": "NO", "dialogue": "no_lines"},
        ],
    }
}


def test_loads_prompt_and_options_in_order() -> None:
    cs = ChoiceSystem(_write(_VALID))
    choice = cs.get("grate")
    assert choice.prompt == "Jump in?"
    assert [o.label for o in choice.options] == ["YES", "NO"]
    assert choice.options[0].dialogue == "yes_lines"


def test_unknown_id_is_loud_and_names_known_ids() -> None:
    cs = ChoiceSystem(_write(_VALID))
    try:
        cs.get("nope")
    except KeyError as exc:
        assert "grate" in str(exc)
    else:
        raise AssertionError("expected KeyError")


def test_malformed_choices_are_loud() -> None:
    bad = [
        {"c": {"prompt": "", "options": [{"label": "A", "dialogue": "x"},
                                         {"label": "B", "dialogue": "y"}]}},
        {"c": {"prompt": "Q?", "options": [{"label": "A", "dialogue": "x"}]}},
        {"c": {"prompt": "Q?", "options": [{"label": "", "dialogue": "x"},
                                           {"label": "B", "dialogue": "y"}]}},
        {"c": {"prompt": "Q?", "options": [
            {"label": "A", "dialogue": "x", "goto": "somewhere"},
            {"label": "B", "dialogue": "y"},
        ]}},
        {"c": {"prompt": "Q?", "options": [
            {"label": "A", "arrival": "dock"}, {"label": "B"},
        ]}},
        {"c": {"prompt": "Q?", "options": [
            {"label": "A", "goto": "map", "climb_from_water": "yes"},
            {"label": "B"},
        ]}},
        {"c": {"prompt": "Q?", "options": [
            {"label": "A", "action": "not_a_real_action"}, {"label": "B"},
        ]}},
        {"c": {"prompt": "Q?", "options": [
            {"label": "A", "goto": "map", "action": "tower_arrival"},
            {"label": "B"},
        ]}},
    ]
    for data in bad:
        try:
            ChoiceSystem(_write(data))
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted malformed choice: {data}")


def test_real_grate_choice_asks_the_right_question() -> None:
    cs = ChoiceSystem()
    choice = cs.get("sewer_grate")
    assert choice.prompt == "Jump into the sewer?"
    assert [o.label for o in choice.options] == ["YES", "NO"]
    assert choice.options[1].dialogue is None
    assert choice.options[1].goto is None


def test_real_sewer_exit_choice_carries_arrival_choreography() -> None:
    choice = ChoiceSystem().get("sewer_exit")
    assert choice.prompt == "Leave the sewer?"
    assert [o.label for o in choice.options] == ["YES", "NO"]
    yes, no = choice.options
    assert yes.goto == "waterdeep_docks"
    assert yes.arrival == "sewer_outflow"
    assert yes.climb_from_water
    assert no.dialogue is None and no.goto is None


def test_silent_choice_closes_dialogue_immediately() -> None:
    class Input:
        @staticmethod
        def was_pressed(action):
            return action == "interact"

    class Audio:
        played = []

        @classmethod
        def play_sfx(cls, name):
            cls.played.append(name)

    class Scenes:
        pops = 0

        @classmethod
        def pop(cls):
            cls.pops += 1

    scene = object.__new__(DialogueScene)
    scene.game = type("Game", (), {
        "input": Input(), "audio": Audio(), "scenes": Scenes(),
    })()
    scene._choice = Choice("Jump?", [Option("NO"), Option("YES", goto="sewer")])
    scene._selected = 0
    scene._on_choice = None
    scene._dialogue = None
    scene._update_choice()
    assert Scenes.pops == 1
    assert Audio.played == ["interact"]


def test_every_choice_branch_resolves() -> None:
    # Spoken options point at real lines and navigation options at real maps.
    # A third valid kind has neither target and simply closes the choice.
    from src.core import config
    cs, ds = ChoiceSystem(), DialogueSystem()
    for choice_id in cs.ids():
        for option in cs.get(choice_id).options:
            assert option.dialogue is None or option.goto is None
            if option.dialogue is not None:
                lines = ds.get(option.dialogue)  # raises if missing
                assert lines and all(isinstance(l, str) for l in lines)
            elif option.goto is not None:
                assert (config.MAPS_DIR / f"{option.goto}.txt").is_file()
            elif option.action is not None:
                assert option.action in KNOWN_CHOICE_ACTIONS


def test_choice_text_is_renderable_by_the_pixel_font() -> None:
    from src.ui.bitmap_font import GLYPH_ORDER

    cs = ChoiceSystem()
    unrenderable = set()
    for choice_id in cs.ids():
        choice = cs.get(choice_id)
        unrenderable |= set(choice.prompt) - set(GLYPH_ORDER)
        for option in choice.options:
            # The caret and a space are drawn with each label.
            unrenderable |= set(f"> {option.label}") - set(GLYPH_ORDER)
    assert not unrenderable, f"no glyphs for: {sorted(unrenderable)}"


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
    print("All choice tests passed.")


if __name__ == "__main__":
    _run_all()
