"""Unit tests for dialogue loading, text wrapping, and NPC facing.

Run from the project root with:

    python -m tests.test_dialogue    (plain asserts, no dependencies)
    pytest                           (if you have pytest)
"""

import json
import tempfile
from pathlib import Path

from src.entities.npc import NPC
from src.systems.dialogue import DialogueSystem
from src.ui.text import wrap_text


def _dialogue_dir(*files: dict) -> Path:
    d = Path(tempfile.mkdtemp())
    for i, data in enumerate(files):
        (d / f"file{i}.json").write_text(json.dumps(data), encoding="utf-8")
    return d


def test_loads_and_serves_lines() -> None:
    ds = DialogueSystem(_dialogue_dir({"a": ["one", "two"]}))
    assert ds.get("a") == ["one", "two"]


def test_merges_multiple_files() -> None:
    ds = DialogueSystem(_dialogue_dir({"a": ["x"]}, {"b": ["y"]}))
    assert ds.get("a") == ["x"] and ds.get("b") == ["y"]


def test_duplicate_id_across_files_is_loud() -> None:
    try:
        DialogueSystem(_dialogue_dir({"a": ["x"]}, {"a": ["y"]}))
    except ValueError as exc:
        assert "Duplicate" in str(exc)
    else:
        raise AssertionError("expected ValueError for duplicate id")


def test_missing_id_is_loud_and_names_known_ids() -> None:
    ds = DialogueSystem(_dialogue_dir({"a": ["x"]}))
    try:
        ds.get("nope")
    except KeyError as exc:
        assert "nope" in str(exc) and "a" in str(exc)
    else:
        raise AssertionError("expected KeyError")


def test_empty_or_malformed_lines_are_loud() -> None:
    for bad in ({"a": []}, {"a": "not a list"}, {"a": [1, 2]}):
        try:
            DialogueSystem(_dialogue_dir(bad))
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad}")


def test_real_docks_dialogue_loads() -> None:
    ds = DialogueSystem()
    for dialogue_id in (
        "dock_worker", "bobert_sleeping", "herod_sign", "market_woman",
        "bartender", "patron", "musician", "cheese",
    ):
        lines = ds.get(dialogue_id)
        assert lines and all(isinstance(l, str) for l in lines)
    assert ds.get("bobert_sleeping") == ["... Zzzzz."]
    assert ds.get("herod_sign") == ["Herod Cover Band - Tonight Only"]
    assert ds.get("guard") == ["Stick to the docks, rat."]
    assert ds.get("market_woman") == [
        "No handouts here. If you're hungry, you should check the sewer for scraps"
    ]
    assert ds.get("bartender") == [
        "Oh, it's you again. There's some cheese in the back if you're hungry. "
        "I was planning to throw it out, it's gone a bit ...funky"
    ]
    assert ds.get("patron") == ["They're out of stew."]
    assert ds.get("musician") == [
        'Tonight I will be playing 37 different renditions of "Fortune Favors '
        'the Kobold",',
        "beginning with the Hurdy Gurdy arrangement",
    ]
    assert ds.get("cheese") == ["It is cheese."]


def test_all_dialogue_text_is_renderable_by_the_pixel_font() -> None:
    # Every character in every dialogue file must exist as a glyph,
    # so writing bugs surface here instead of mid-conversation.
    import json
    from src.core import config
    from src.ui.bitmap_font import GLYPH_ORDER

    unrenderable = set()
    for path in config.DIALOGUE_DIR.glob("*.json"):
        for lines in json.loads(path.read_text(encoding="utf-8")).values():
            for line in lines:
                unrenderable |= set(line) - set(GLYPH_ORDER)
    assert not unrenderable, f"no glyphs for: {sorted(unrenderable)}"


def test_font_metrics_are_consistent() -> None:
    from src.ui.bitmap_font import ADVANCE, GLYPH_H, BitmapFont

    font = BitmapFont(glyphs={})  # metrics don't touch glyphs
    assert font.size("") == (0, GLYPH_H)
    assert font.size("abc") == (3 * ADVANCE - 1, GLYPH_H)
    assert font.get_height() == GLYPH_H


def test_wrap_respects_width() -> None:
    measure = len  # 1px per char for testing
    lines = wrap_text("aa bb cc dd", 5, measure)
    assert lines == ["aa bb", "cc dd"]
    assert all(measure(l) <= 5 for l in lines)


def test_wrap_never_drops_or_splits_long_words() -> None:
    lines = wrap_text("hi extraordinarily hi", 6, len)
    assert lines == ["hi", "extraordinarily", "hi"]
    assert " ".join(lines).split() == "hi extraordinarily hi".split()


def test_interaction_zone_covers_the_whole_visible_person() -> None:
    # Regression: E must work when Chuck stands ON the (non-solid) NPC
    # or faces his tall sprite, not only his tiny feet hitbox.
    from src.core import config

    npc = NPC(100.0, 100.0, npc_id="x", dialogue_id="x")
    x, y, w, h = npc.interaction_bounds()
    feet = npc.hitbox_bounds = (npc.x, npc.y, npc.width, npc.height)
    # Zone spans at least the sprite's width and full height...
    assert w >= config.NPC_FRAME_W and h >= config.NPC_FRAME_H
    # ...its bottom reaches the feet, and it extends up over the body.
    assert y + h >= npc.y + npc.height
    assert y <= npc.y + npc.height - config.NPC_FRAME_H + 4
    # A point at the sprite's chest (18px above the feet) is inside.
    chest_y = npc.y + npc.height - 18
    assert y <= chest_y <= y + h


def test_npc_faces_the_interactor() -> None:
    npc = NPC(100.0, 100.0, npc_id="x", dialogue_id="x")

    class Probe:
        width = height = 10
        def __init__(self, x, y): self.x, self.y = x, y

    assert npc.interact(Probe(200, 100)) == "x"
    assert npc.facing == "right"
    npc.face_toward(Probe(0, 100));   assert npc.facing == "left"
    npc.face_toward(Probe(100, 300)); assert npc.facing == "down"
    npc.face_toward(Probe(100, -80)); assert npc.facing == "up"


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
    print("All dialogue tests passed.")


if __name__ == "__main__":
    _run_all()
