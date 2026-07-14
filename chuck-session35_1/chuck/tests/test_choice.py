"""Unit tests for the dialogue choice system (data + validation).

Run from the project root with:

    python -m tests.test_choice      (pure Python, no pygame needed)
    pytest                           (if you have pytest)
"""

import json
import tempfile
from pathlib import Path

from src.systems.choice import ChoiceSystem
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
        {"c": {"prompt": "Q?", "options": [{"label": "A"},
                                           {"label": "B", "dialogue": "y"}]}},
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


def test_every_choice_branch_has_dialogue_that_exists() -> None:
    # A choice pointing at a missing branch would be a dead end mid-
    # conversation. Catch it here instead.
    cs, ds = ChoiceSystem(), DialogueSystem()
    for choice_id in cs.ids():
        for option in cs.get(choice_id).options:
            lines = ds.get(option.dialogue)  # raises if missing
            assert lines and all(isinstance(l, str) for l in lines)


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
