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


# The pad's sector table, as the shell writes it: a span of degrees and
# the arrows it holds down.
_SECTOR = re.compile(r"\[(\d+),(\d+),\[([^\]]*)\]\]")


def _sectors() -> list[tuple[int, int, tuple[str, ...]]]:
    table = MOBILE_SHELL[MOBILE_SHELL.index("PAD_SECTORS"):]
    table = table[:table.index("];")]
    found = [(int(a), int(b),
              tuple(d.strip().strip("'") for d in dirs.split(",")))
             for a, b, dirs in _SECTOR.findall(table)]
    assert found, "the d-pad's sector table could not be read"
    return found


def test_the_pad_covers_every_angle_exactly_once() -> None:
    """A gap here is a direction that does nothing on a real phone.

    The pad is one control, not four buttons: the touch's angle from the
    centre picks a sector. So the sectors have to tile the circle -- a
    hole leaves a wedge of the pad dead, and an overlap makes the first
    match win silently.
    """
    spans = sorted((start, end) for start, end, _dirs in _sectors())
    assert spans[0][0] == 0 and spans[-1][1] == 360, (
        f"the sectors run {spans[0][0]}..{spans[-1][1]}, not 0..360")
    for (_, end), (start, _) in zip(spans, spans[1:]):
        assert end == start, (
            f"the sectors leave a gap or overlap between {end} and {start}")
    assert sum(end - start for start, end in spans) == 360


def test_a_diagonal_on_the_pad_holds_both_of_its_arrows() -> None:
    """The whole point: a keyboard player holds two arrows, so must this.

    Four buttons could never do it -- a pointer belongs to the element
    it lands on -- which is why the pad is read as one control.
    """
    diagonals = {dirs for _s, _e, dirs in _sectors() if len(dirs) == 2}
    assert diagonals == {("up", "right"), ("up", "left"),
                         ("down", "left"), ("down", "right")}, diagonals
    for _start, _end, dirs in _sectors():
        assert 1 <= len(dirs) <= 2
        for name in dirs:
            assert f'id="{name}"' in MOBILE_SHELL, (
                f"the pad names {name!r}, which is not a button on it")


def test_the_pad_favours_the_straight_directions() -> None:
    """Eight equal sectors make a clean "up" hard, and menus want up.

    So the cardinals are given more of the circle than the diagonals.
    """
    width: dict[tuple[str, ...], int] = {}
    for start, end, dirs in _sectors():
        width[dirs] = width.get(dirs, 0) + (end - start)
    cardinals = {d: w for d, w in width.items() if len(d) == 1}
    diagonals = {d: w for d, w in width.items() if len(d) == 2}
    assert len(cardinals) == 4 and len(diagonals) == 4
    assert len(set(cardinals.values())) == 1, (
        f"the four straight directions are not equal: {cardinals}")
    assert len(set(diagonals.values())) == 1, (
        f"the four diagonals are not equal: {diagonals}")
    assert min(cardinals.values()) > max(diagonals.values()), (
        f"straight directions ({cardinals}) should be easier to hit than "
        f"diagonals ({diagonals})")


def test_the_pad_has_a_dead_zone_and_is_driven_as_one_control() -> None:
    """A thumb resting at the centre should mean nothing."""
    dead = float(MOBILE_SHELL.split("PAD_DEAD=")[1].split(";")[0])
    assert 0 < dead < 0.5, f"a dead zone of {dead} is not a dead zone"
    # Its arrows must be out of the one-key-per-button binding, or each
    # would also fire on its own and fight the pad.
    assert ":not([data-pad])" in MOBILE_SHELL
    for name in ("up", "down", "left", "right"):
        marked = MOBILE_SHELL[MOBILE_SHELL.index(f'id="{name}"') - 40:]
        assert "data-pad" in marked[:60], (
            f"the {name} arrow is not marked as part of the pad")


def test_a_failed_pointer_capture_cannot_swallow_a_press() -> None:
    """Following the finger is worth having; a lost press is not.

    setPointerCapture throws if the pointer has already gone, and doing
    it before the press meant the throw ate the input.
    """
    assert "function capture(element,event){" in MOBILE_SHELL
    assert "catch(e){}" in MOBILE_SHELL[MOBILE_SHELL.index("function capture"):][:200]
    for press, follow in (("padApply(padDirections(e))", "capture(pad,e)"),
                          ("key(b,true)", "capture(b,e)")):
        assert MOBILE_SHELL.index(press) < MOBILE_SHELL.index(follow), (
            f"{follow} happens before {press}; a refused capture would "
            f"throw before the press was registered")


def test_every_control_is_sized_from_the_one_slider() -> None:
    """The settings wheel was very nearly a no-op.

    It used to widen the *bounds* of each `clamp()` rather than scale
    the result. On a phone the floor wins at those viewports, so at full
    stretch a button grew by half a pixel -- and the d-pad, which sizes
    itself from its own variable, never moved at all. Measured before
    the fix: pad 150px to 150px, JUMP 52px to 52.5px.

    So every control size now multiplies by one variable, and this
    checks each of them still does.
    """
    root = MOBILE_SHELL[MOBILE_SHELL.index(":root{"):]
    root = root[:root.index("}")]
    for name in ("--button", "--pad", "--chip"):
        assert name in root, f"{name} is gone from the shell's sizes"
        value = root.split(name + ":")[1].split(";")[0]
        assert "var(--scale)" in value, (
            f"{name} is {value!r}, which does not follow the size slider")
    assert "--scale:1" in root, "no default scale"
    assert "setProperty('--scale'" in MOBILE_SHELL, (
        "the size slider no longer drives --scale")


def test_no_control_carries_a_size_the_slider_cannot_reach() -> None:
    """A hardcoded width is a control that ignores the setting.

    The pause and gear chips were literally `46px` and stayed that size
    at every slider position.
    """
    import re

    for rule_id in ("#pause{", "#settings{", "#fullscreen{"):
        rule = MOBILE_SHELL[MOBILE_SHELL.index(rule_id):]
        rule = rule[:rule.index("}")]
        for prop in ("min-width", "min-height"):
            value = rule.split(prop + ":")[1].split(";")[0]
            assert re.fullmatch(r"var\(--\w+\)", value), (
                f"{rule_id[:-1]} sets {prop} to {value!r} rather than a "
                f"variable, so the size slider cannot move it")


def test_the_controls_remember_their_size() -> None:
    """These are sized to a hand; re-finding it every visit is a tax."""
    assert "localStorage.setItem" in MOBILE_SHELL
    assert "localStorage.getItem" in MOBILE_SHELL
    # Storage throws in private mode rather than returning null, and a
    # thrown settings read would take the whole shell down with it.
    read = MOBILE_SHELL[MOBILE_SHELL.index("localStorage.getItem"):]
    assert "catch" in read[:400], "the settings read is not guarded"


def test_the_tap_to_play_label_never_takes_the_tap() -> None:
    """If this label ever catches the touch, the game cannot start.

    Safari will not run a page that makes sound until it has had a real
    touch, and pygbag says nothing about it -- its only message is the
    "Loading" line, hidden by then. So the shell shows the prompt. The
    tap it asks for has to pass straight through into the iframe, which
    is the frame Safari wants the gesture in; a label that swallowed it
    would leave the player tapping a black screen for ever.
    """
    rule = MOBILE_SHELL[MOBILE_SHELL.index("#start{"):]
    rule = rule[:rule.index("}")]
    assert "pointer-events:none" in rule, (
        "the tap-to-play label would swallow the tap that starts the game")
    assert "display:none" in rule, (
        "the label is not hidden by default, so it would sit over the "
        "game while it is still loading")
    assert "#start.ready{display:grid" in MOBILE_SHELL, (
        "nothing shows the label once the game is ready for its tap")


def test_the_shell_watches_for_the_tap_inside_the_game() -> None:
    """The parent never sees a touch that lands in the iframe.

    So the listener has to be added to the iframe's own document, which
    is reachable only because the two are the same origin.
    """
    watch = MOBILE_SHELL[MOBILE_SHELL.index("startLayer.classList.add('ready')"):]
    watch = watch[:600]
    assert "frame.contentDocument.addEventListener('pointerdown'" in watch, (
        "the shell is not listening for the tap where it actually lands")
    assert "dismissStart" in watch
    # And a player who reaches for a control has plainly started too.
    assert "getElementById('controls').addEventListener('pointerdown',dismissStart"         in MOBILE_SHELL


def test_portrait_is_told_to_turn_sideways() -> None:
    """The game is 16:9. Held upright it is a sliver with controls on it."""
    assert 'id="rotate"' in MOBILE_SHELL
    assert "@media (orientation:portrait)" in MOBILE_SHELL
    rule = MOBILE_SHELL[MOBILE_SHELL.index("#rotate{"):]
    rule = rule[:rule.index("}")]
    assert "display:none" in rule, (
        "the rotate prompt is not hidden by default, so it would cover "
        "the game in landscape too")


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
