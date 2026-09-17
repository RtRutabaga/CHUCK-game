"""The code field: typing into it, pasting into it, and reading it back.

The widget is the game's only text input, so the tests cover the three
ways a code gets in -- typed, pasted, dialled on a pad -- and the two
things that go wrong: a character that is not in the alphabet, and a
field that is not full yet. Drawing is checked only for the caret, which
is the one part of it that moves.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.systems import clipboard
from src.systems.save_code import ALPHABET, CODE_LENGTH
from src.ui.bitmap_font import ADVANCE, GLYPH_ORDER
from src.ui.code_entry import BLANK, SEPARATOR, CodeEntry

# The golden code from tests/test_save_code.py, typed rather than decoded.
GOLDEN_CODE = "K6PT-6EX1-BV41-7S96"


def _key(key: int, unicode: str = "", mod: int = 0):
    return pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode,
                              mod=mod)


def _type(field: CodeEntry, text: str) -> None:
    for char in text:
        field.handle_event(_key(ord(char) if len(char) == 1 else 0, char))


class _Pad:
    """Just enough of InputManager for handle_pad."""

    def __init__(self, *actions: str) -> None:
        self._actions = set(actions)

    def was_pressed(self, action: str) -> bool:
        return action in self._actions


def test_a_new_field_is_empty_and_shows_its_shape() -> None:
    field = CodeEntry()
    assert field.empty and not field.complete
    assert field.text == ""
    # Every slot a blank, and the groups already marked out, so the
    # player can see how long a code is before typing one.
    assert field.display() == SEPARATOR.join([BLANK * 4] * 4)
    assert len(field.display()) == CODE_LENGTH + 3


def test_typing_a_code_fills_it_and_it_decodes() -> None:
    field = CodeEntry()
    _type(field, GOLDEN_CODE.replace("-", ""))
    assert field.complete
    assert field.display() == GOLDEN_CODE
    record = field.decode()
    assert record is not None and record.checkpoint_id == "temple_9"
    assert field.error is None


def test_the_field_is_as_forgiving_as_the_codec() -> None:
    """Lower case, dashes, and an O for a zero all land as the same code."""
    field = CodeEntry()
    _type(field, "k6pt-6ex1-bv41-7s96")
    assert field.display() == GOLDEN_CODE
    assert field.decode() is not None


def test_a_character_that_is_not_in_the_alphabet_does_nothing() -> None:
    field = CodeEntry()
    assert not field.type_character("U")       # Crockford leaves U out
    for char in "U!? ":
        assert not field.handle_event(_key(ord(char), char))
    assert field.empty
    # And the ones that are in it all go in.
    for char in ALPHABET:
        single = CodeEntry()
        assert single.type_character(char)
        assert single.text == char


def test_typing_past_the_end_does_not_overflow() -> None:
    field = CodeEntry()
    _type(field, GOLDEN_CODE.replace("-", "") + "ZZZ")
    assert field.text == GOLDEN_CODE.replace("-", "")
    assert len(field.text) == CODE_LENGTH


def test_backspace_walks_back_from_the_end() -> None:
    field = CodeEntry()
    _type(field, GOLDEN_CODE.replace("-", ""))
    field.handle_event(_key(pygame.K_BACKSPACE))
    assert not field.complete
    assert field.display().endswith(BLANK)
    # And it can be retyped into the hole it left.
    _type(field, GOLDEN_CODE[-1])
    assert field.display() == GOLDEN_CODE


def test_backspace_on_an_empty_field_is_harmless() -> None:
    field = CodeEntry()
    for _ in range(3):
        field.handle_event(_key(pygame.K_BACKSPACE))
    assert field.empty and field.cursor == 0


def test_arrows_move_the_caret_and_stay_inside_the_field() -> None:
    field = CodeEntry()
    _type(field, "K6PT6")
    field.handle_event(_key(pygame.K_LEFT))
    field.handle_event(_key(pygame.K_LEFT))
    assert field.cursor == 3
    _type(field, "X")
    assert field.display().startswith("K6PX")
    for _ in range(CODE_LENGTH * 2):
        field.handle_event(_key(pygame.K_RIGHT))
    assert field.cursor == CODE_LENGTH - 1
    for _ in range(CODE_LENGTH * 2):
        field.handle_event(_key(pygame.K_LEFT))
    assert field.cursor == 0


def test_end_goes_to_the_first_slot_still_waiting() -> None:
    field = CodeEntry()
    _type(field, "K6PT6")
    field.handle_event(_key(pygame.K_HOME))
    assert field.cursor == 0
    field.handle_event(_key(pygame.K_END))
    assert field.cursor == 5


def test_a_pad_dials_a_slot_through_the_alphabet() -> None:
    field = CodeEntry()
    assert field.handle_pad(_Pad("move_up"))
    assert field.text == ALPHABET[0]
    field.handle_pad(_Pad("move_up"))
    assert field.text == ALPHABET[1]
    field.handle_pad(_Pad("move_down"))
    field.handle_pad(_Pad("move_down"))
    # Wrapping backwards past the start lands on the last character
    # rather than going nowhere.
    assert field.text == ALPHABET[-1]
    assert field.handle_pad(_Pad("move_right"))
    assert field.cursor == 1
    assert not field.handle_pad(_Pad("interact"))


def test_a_whole_code_can_be_dialled_in_on_a_pad_alone() -> None:
    field = CodeEntry()
    for char in GOLDEN_CODE.replace("-", ""):
        while field._slots[field.cursor] != char:
            field.handle_pad(_Pad("move_up"))
        field.handle_pad(_Pad("move_right"))
    assert field.display() == GOLDEN_CODE
    assert field.decode() is not None


def test_a_paste_replaces_the_field_in_one_go() -> None:
    field = CodeEntry()
    _type(field, "ZZZ")
    assert field.set_text(f"  {GOLDEN_CODE.lower()}\n")
    assert field.display() == GOLDEN_CODE
    assert field.cursor == CODE_LENGTH
    # Short paste: the rest stays blank rather than keeping old characters.
    assert field.set_text("K6PT")
    assert field.display() == "K6PT" + SEPARATOR + SEPARATOR.join(
        [BLANK * 4] * 3)
    assert not field.complete
    # Nothing usable in it at all.
    assert not field.set_text("!!! ???")
    assert field.display().startswith("K6PT")


def test_ctrl_v_takes_the_clipboard_and_says_so_when_it_is_empty() -> None:
    field = CodeEntry()
    original = clipboard.paste
    try:
        clipboard.paste = lambda: GOLDEN_CODE
        assert field.handle_event(_key(pygame.K_v, "v", pygame.KMOD_CTRL))
        assert field.display() == GOLDEN_CODE
        clipboard.paste = lambda: None
        field.clear()
        field.handle_event(_key(pygame.K_v, "v", pygame.KMOD_META))
        assert field.empty and field.error == "Nothing to paste."
        clipboard.paste = lambda: "!!! ???"
        field.handle_event(_key(pygame.K_v, "v", pygame.KMOD_CTRL))
        assert field.error == "That is not a save code."
    finally:
        clipboard.paste = original


def test_a_plain_v_is_a_character_and_not_a_paste() -> None:
    field = CodeEntry()
    original = clipboard.paste
    try:
        clipboard.paste = lambda: GOLDEN_CODE
        field.handle_event(_key(pygame.K_v, "v"))
        assert field.text == "V"
    finally:
        clipboard.paste = original


def test_a_half_typed_code_complains_about_its_length() -> None:
    field = CodeEntry()
    _type(field, "K6PT6")
    assert field.decode() is None
    assert "16 characters" in field.error
    # And the complaint goes as soon as the player types again.
    _type(field, "0")
    assert field.error is None


def test_a_mistyped_code_is_refused_with_something_to_read() -> None:
    field = CodeEntry()
    wrong = GOLDEN_CODE.replace("-", "")
    wrong = wrong[:7] + ("Z" if wrong[7] != "Z" else "Y") + wrong[8:]
    _type(field, wrong)
    assert field.decode() is None
    assert field.error and field.error[0].isupper() and field.error.endswith(".")


def test_clearing_puts_it_back_to_new() -> None:
    field = CodeEntry()
    _type(field, GOLDEN_CODE.replace("-", ""))
    field.decode()
    field.clear()
    assert field.empty and field.cursor == 0 and field.error is None


def test_the_caret_sits_under_the_slot_it_is_filling() -> None:
    field = CodeEntry()
    assert field.caret_x() == 0
    _type(field, "K6PT")
    # Past a group separator, so the caret has to count the dash too.
    assert field.caret_x() == 5 * ADVANCE
    _type(field, "6EX1BV")
    assert field.caret_x() == 12 * ADVANCE
    assert field.width() == len(field.display()) * ADVANCE - 1


def test_the_caret_blinks_and_an_edit_shows_it_again() -> None:
    field = CodeEntry()
    seen = set()
    for _ in range(40):
        seen.add(field.caret_visible())
        field.update(0.07)
    assert seen == {True, False}, "the caret should blink, not sit"
    # Wound forward to a dark moment, then typed into: the caret has to
    # be visible where it moved to, not still mid-blink somewhere else.
    while field.caret_visible():
        field.update(0.05)
    _type(field, "0")
    assert field.caret_visible()
    field.update(0.5)
    assert not field.caret_visible()
    field.handle_event(_key(pygame.K_LEFT))
    assert field.caret_visible()


def test_the_caret_is_only_drawn_while_it_is_visible() -> None:
    field = CodeEntry()
    font = _FakeFont()
    row = font.get_height()
    assert field.caret_visible()
    assert _pixel(field, font, row) == (255, 0, 0)
    while field.caret_visible():
        field.update(0.05)
    assert _pixel(field, font, row) == (0, 0, 0)


def test_the_clipboard_answers_instead_of_raising() -> None:
    """Whatever this build has, copy and paste return rather than throw.

    Headless, in a browser, on a machine with no clipboard at all: the
    menu's fallback is the same either way, so the only thing that must
    never happen is an exception out of a key press.
    """
    assert clipboard.available() in (True, False)
    assert clipboard.copy(GOLDEN_CODE) in (True, False)
    taken = clipboard.paste()
    assert taken is None or isinstance(taken, str)


def test_a_clipboard_that_throws_is_still_only_a_false() -> None:
    class _Broken:
        @staticmethod
        def get_init():
            return True

        @staticmethod
        def put_text(_text):
            raise RuntimeError("no clipboard here")

        @staticmethod
        def get_text():
            raise RuntimeError("nor here")

    original = clipboard._scrap
    try:
        clipboard._scrap = lambda: _Broken
        assert clipboard.copy("ANYTHING") is False
        assert clipboard.paste() is None
        clipboard._scrap = lambda: None
        assert clipboard.available() is False
        assert clipboard.copy("ANYTHING") is False
        assert clipboard.paste() is None
    finally:
        clipboard._scrap = original


def test_every_character_the_field_can_show_is_in_the_pixel_font() -> None:
    for char in ALPHABET + BLANK + SEPARATOR:
        assert char in GLYPH_ORDER, char


def test_drawing_puts_the_code_on_the_surface() -> None:
    pygame.display.init()
    field = CodeEntry()
    _type(field, GOLDEN_CODE.replace("-", ""))
    surface = pygame.Surface((320, 180))
    surface.fill((0, 0, 0))
    field.draw(surface, _FakeFont(), 10, 20, tint=(246, 214, 140))
    assert surface.get_at((10, 20))[:3] != (0, 0, 0)


class _FakeFont:
    """A font that draws a solid block per character, at the real metrics."""

    def get_height(self) -> int:
        return 9

    def render(self, text: str):
        image = pygame.Surface((max(1, len(text) * ADVANCE - 1), 9),
                               pygame.SRCALPHA)
        image.fill((255, 255, 255, 255))
        return image


def _pixel(field: CodeEntry, font, row: int):
    """The colour under the caret, drawn in red on black so it stands out."""

    surface = pygame.Surface((320, 180))
    surface.fill((0, 0, 0))
    field.draw(surface, font, 0, 0, tint=(255, 0, 0))
    return surface.get_at((field.caret_x(), row))[:3]


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
    print("All code entry tests passed.")


if __name__ == "__main__":
    _run_all()
