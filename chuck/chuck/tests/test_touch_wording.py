"""What the game calls a control when the player has no keyboard.

On a phone the shell puts its own buttons on screen -- JUMP, SCRATCH,
INSPECT / TALK, a pause button -- and until now the game went on telling
that player to press E, SPACE and ESC. Keys they do not have.

**This is wording and nothing else.** No layout, scene, rule or control
differs on a phone; it runs the same build as the PC and the Xbox. A
line that said "Press E to interact" says "Tap INSPECT to interact",
because that is what is written on the button under their thumb. If
anything beyond a string ever starts depending on `touch_host()`, that
is the fork `/mobile/` exists to avoid -- see TWO-AGENT-GIT-WORKFLOW.md
"There Is Only One CHUCK".

The signal is the marker the shell already puts on the page it embeds,
`index.html?mobile=1`, which the desktop page already reads to hide its
own link to `/mobile/`. One marker, read from both sides.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import runtime
from src.scenes.pause_scene import CONTROLS, controls_rows
from src.ui import prompts
from src.ui.bitmap_font import ADVANCE


class _Pad:
    """An input manager that says it is a controller."""

    def __init__(self, kind: str = "xbox") -> None:
        self.using_controller = True
        self.last_kind = kind


class _touching:
    """Pretend the build is running inside the touch shell."""

    def __enter__(self):
        self._was = runtime._TOUCH_HOST
        runtime._TOUCH_HOST = True
        return self

    def __exit__(self, *exc):
        runtime._TOUCH_HOST = self._was
        return False


def test_a_phone_is_told_to_tap_what_it_can_see() -> None:
    from src.core import config

    with _touching():
        assert prompts.label(None, "interact") == "INSPECT"
        assert prompts.label(None, "jump") == "JUMP"
        assert prompts.label(None, "scratch") == "SCRATCH"
        assert prompts.move_label(None) == prompts.TOUCH_MOVE
        assert prompts.hint(None, config.HINT_JUMP) == "Tap JUMP to jump"
        assert prompts.title_prompt(None) == "PAD UP / DOWN   INSPECT"


def test_no_hint_on_a_phone_still_names_a_key() -> None:
    """Every hint is either reworded for a thumb, or silenced.

    What must never happen is a hint falling through unchanged and
    telling a touch player to press something they do not have.
    """
    from src.core import config

    for text in (config.HINT_INTERACT, config.HINT_JUMP,
                 config.HINT_SCRATCH, config.HINT_PAUSE):
        with _touching():
            touched = prompts.hint(None, text)
        assert touched != text, f"no touch wording for {text!r}"
        for key in ("E", "SPACE", "ESC", "F"):
            assert f" {key} " not in f" {touched} ", (
                f"the touch hint {touched!r} still names the {key} key")


def test_the_phone_is_not_taught_to_pause() -> None:
    """Sean's call, and it is the right one.

    On a keyboard the line has to exist: nothing on screen says ESC
    pauses. On a phone the pause button sits in the corner the whole
    time, so the hint would teach a player to tap something already in
    front of them. Silent on touch, unchanged everywhere else.
    """
    from src.core import config

    with _touching():
        assert prompts.hint(None, config.HINT_PAUSE) == ""
    assert prompts.hint(None, config.HINT_PAUSE) == config.HINT_PAUSE
    assert prompts.hint(_Pad(), config.HINT_PAUSE) == "Press Y to pause"


def test_a_silent_hint_puts_nothing_on_the_screen() -> None:
    """Empty wording has to mean nothing drawn, not an empty line drawn."""
    import pygame

    from src.core import config
    from src.core.assets import AssetManager
    from src.ui.tutorial_hint import TutorialHint

    pygame.display.init()
    pygame.display.set_mode((1, 1))
    hint = TutorialHint(AssetManager(), None)
    blank = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
    surface = blank.copy()

    with _touching():
        hint.draw(surface, config.HINT_PAUSE)
    assert pygame.image.tobytes(surface, "RGB") ==         pygame.image.tobytes(blank, "RGB"), (
            "the silenced pause hint still drew something")

    # And the ones that do have wording still appear, so this is not
    # simply a hint system that stopped working.
    with _touching():
        hint.draw(surface, config.HINT_JUMP)
    assert pygame.image.tobytes(surface, "RGB") !=         pygame.image.tobytes(blank, "RGB"), "the jump hint drew nothing"


def test_the_controls_page_names_buttons_not_keys_on_a_phone() -> None:
    with _touching():
        rows = controls_rows(None)
    listed = " ".join(value for _action, value in rows)
    for key in ("WASD", "ARROW KEYS", "SPACE", "ESC", "ENTER", "F11"):
        assert key not in listed, (
            f"the phone's controls page still mentions {key}: {listed!r}")
    actions = [action for action, _value in rows]
    assert actions == ["MOVE", "TALK / EXAMINE", "JUMP", "SCRATCH", "PAUSE"]


def test_the_phone_controls_page_fits_the_panel_it_is_drawn_on() -> None:
    """Action on the left, control on the right, inside 230px.

    The keyboard's longest row already sits close to the edge, and the
    touch wording is longer. Drawn at `rect.x + 14` and right-aligned at
    `rect.right - 14`, so the two columns share 202px and need a gap.
    """
    with _touching():
        rows = controls_rows(None)
    usable = 230 - 14 - 14
    for action, value in rows + CONTROLS:
        width = (len(action) + len(value)) * ADVANCE - 2
        assert width + ADVANCE <= usable, (
            f"{action!r} and {value!r} need {width}px of the {usable}px "
            f"the controls panel has between its margins")


def test_a_controller_still_wins_over_the_shell() -> None:
    """A pad plugged into a phone is what is being played with."""
    with _touching():
        assert prompts.label(_Pad(), "interact") == "B"
        assert prompts.move_label(_Pad()) == prompts.PAD_MOVE
        assert "INSPECT" not in prompts.back_footer(_Pad())
        rows = controls_rows(_Pad())
    assert ("MOVE", prompts.PAD_MOVE) in rows


def test_nothing_changes_for_a_keyboard() -> None:
    """The desktop and Xbox wording is exactly what it always was."""
    assert not runtime.touch_host()
    assert prompts.label(None, "interact") == "E"
    assert prompts.move_label(None) == prompts.KEY_MOVE
    assert prompts.back_footer(None) == "E / ESC: BACK"
    assert prompts.title_prompt(None) == "UP / DOWN   E / ENTER"


def test_the_marker_is_the_one_the_shell_already_sends() -> None:
    """No second opinion about what a phone is."""
    from tools.build_web import MOBILE_SHELL

    assert "?mobile=1" in MOBILE_SHELL
    import inspect
    source = inspect.getsource(runtime._detect_touch_host)
    assert "mobile=1" in source
    assert "emscripten" in source, (
        "touch_host must stay inert off the web, or the desktop build "
        "could start naming buttons that are not there")


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("All touch-wording tests passed.")


if __name__ == "__main__":
    _run_all()
