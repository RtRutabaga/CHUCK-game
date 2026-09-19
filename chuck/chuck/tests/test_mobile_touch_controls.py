"""The phone shell presses the same keys the desktop game binds.

There is only one CHUCK. `/mobile/` is a host page with an iframe around
the same `index.html`, running the same wasm build from the same `src/`,
so a fix made for the PC or the Xbox browser reaches the phone at the
next build without anyone carrying it across. Nothing needs syncing,
because nothing is forked.

Except one thing. The touch shell has to name the keys its buttons press,
and those names are a copy of `KEY_BINDINGS` written in HTML. That copy
is the only place the phone can drift away from the game, and it drifts
silently: rebind scratch tomorrow and the SCRATCH button goes on sending
`f` for ever, with no error anywhere.

So this is the seam, and these two tests watch it:

    every touch button presses a key the game actually binds
    every action the game binds can be reached from a touch button

The second is the one that earns its keep. Add an action to
`KEY_BINDINGS` and this test fails until the phone has a button for it,
which is the reminder nobody would otherwise get until a player found
the gap.

If a new action genuinely should not be on the phone, add it to
`NOT_ON_TOUCH` with the reason. Making that an explicit line, rather than
an omission, is the whole point.
"""

import os
import re

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.input import KEY_BINDINGS
from tools.build_web import MOBILE_SHELL


# The DOM's name for a key, as a browser reports it, to pygame's. Only
# the keys the shell actually uses; this is not a general table.
DOM_TO_PYGAME = {
    "ArrowUp": pygame.K_UP,
    "ArrowDown": pygame.K_DOWN,
    "ArrowLeft": pygame.K_LEFT,
    "ArrowRight": pygame.K_RIGHT,
    " ": pygame.K_SPACE,
    "e": pygame.K_e,
    "f": pygame.K_f,
    "Escape": pygame.K_ESCAPE,
    "Enter": pygame.K_RETURN,
}

# Escape is not in KEY_BINDINGS: scenes read it directly as "go back".
# The shell's pause button sends it, which is correct, so it is expected
# to have no action rather than a missing one.
UNBOUND_BY_DESIGN = frozenset({"Escape"})

# Actions deliberately absent from the phone. Empty, and a line added
# here should say why.
NOT_ON_TOUCH: frozenset[str] = frozenset()

_BUTTON = re.compile(
    r'data-key="([^"]*)"\s+data-code="([^"]*)"\s+data-keycode="(\d+)"'
)


def _buttons() -> list[tuple[str, str, int]]:
    found = [(key, code, int(number))
             for key, code, number in _BUTTON.findall(MOBILE_SHELL)]
    assert found, "no touch buttons found -- has the shell's markup changed?"
    return found


def test_every_touch_button_presses_a_key_the_game_binds() -> None:
    for key, _code, _number in _buttons():
        assert key in DOM_TO_PYGAME, (
            f"the shell sends {key!r}, which this test has no pygame name "
            f"for -- add it to DOM_TO_PYGAME")
        if key in UNBOUND_BY_DESIGN:
            continue
        assert DOM_TO_PYGAME[key] in KEY_BINDINGS, (
            f"the {key!r} button presses a key the game no longer binds")


def test_every_action_can_be_reached_from_a_touch_button() -> None:
    reachable = {
        KEY_BINDINGS[DOM_TO_PYGAME[key]]
        for key, _code, _number in _buttons()
        if key not in UNBOUND_BY_DESIGN and key in DOM_TO_PYGAME
        and DOM_TO_PYGAME[key] in KEY_BINDINGS
    }
    missing = set(KEY_BINDINGS.values()) - reachable - NOT_ON_TOUCH
    assert not missing, (
        f"no touch button reaches {sorted(missing)} -- add a button to "
        f"MOBILE_SHELL in tools/build_web.py, or list the action in "
        f"NOT_ON_TOUCH with a reason")


def test_each_button_carries_the_code_sdl_looks_its_scancode_up_from() -> None:
    """SDL2 maps `code`, not `key`. A letter must travel as "KeyF"."""
    for key, code, _number in _buttons():
        if len(key) == 1 and key.isalpha():
            assert code == f"Key{key.upper()}", (key, code)
        elif key == " ":
            assert code == "Space", code
        else:
            assert code == key, (key, code)


def test_the_shell_hosts_the_game_rather_than_forking_it() -> None:
    """The reason desktop fixes reach the phone for free.

    If this ever fails, the phone has its own copy of something and the
    rest of this file's reasoning stops being true.
    """
    assert 'src="../index.html' in MOBILE_SHELL, (
        "the mobile page no longer embeds the shared build")


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("All mobile touch-control tests passed.")


if __name__ == "__main__":
    _run_all()
