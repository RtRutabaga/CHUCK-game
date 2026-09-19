"""How a save code gets into the game on a phone.

A phone could start CHUCK but not resume one: LOAD CODE wants twelve
characters and the touch shell has no keyboard. The fix is not a keyboard
drawn inside the game. `src/` has no pointer input at all -- no scene
reads a mouse or a touch -- so one would mean building that first, and it
would then be on screen for desktop players unless the game grew a
"this is a phone" branch, which is the fork `/mobile/` exists to avoid.

It is the phone's *own* keyboard instead, raised by a real HTML field in
the shell, outside the iframe. SDL never sees a keystroke. The finished
code goes in through the paste door the load page is already polling, so
the game's LOAD CODE screen is byte-for-byte the same on every host.

That leaves a seam, the same kind `test_mobile_touch_controls.py`
watches. The shell speaks to the game through three methods on
`CHUCKClipboard`:

    isPasteEnabled()   is a code field open? The game sets this itself
                       when its load page turns browser paste on; the
                       shell reads it rather than being told twice.
    offerPaste(text)   here is a code, by the door a paste uses
    pastePending()     has the game collected it yet?

Rename one of those in `tools/browser_clipboard.js` and the phone stops
being able to load a game -- silently, with no error anywhere, exactly
like a rebound key. So these tests hold the two files together.

There is no Node on every machine that runs this suite, so
`tests/test_browser_clipboard.js`, which exercises what those methods
actually *do*, is not part of it. These checks are the part that runs
anywhere: that the two sides still agree on the names, and that the
shell has not started deciding things the game should decide.
"""

import re
from pathlib import Path

from src.systems.save_code import ALPHABET
from tools.build_web import MOBILE_SHELL

BRIDGE = Path(__file__).resolve().parents[1] / "tools" / "browser_clipboard.js"

# The methods the shell relies on. Named here as well as found by
# parsing, so that a parse that silently returns nothing cannot let a
# rename through.
REQUIRED = ("isPasteEnabled", "offerPaste", "pastePending")


def _bridge_methods() -> set[str]:
    """The names `CHUCKClipboard` actually offers."""
    js = BRIDGE.read_text(encoding="utf-8")
    body = js[js.index("window.CHUCKClipboard"):]
    found = set(re.findall(r"^\s{4}(\w+)\(", body, re.M))
    assert {"enablePaste", "takePaste"} <= found, (
        "the bridge's methods could not be read -- has the file's shape "
        f"changed? found: {sorted(found)}")
    return found


def _shell_calls() -> set[str]:
    """The bridge methods the shell calls.

    The shell holds the bridge in a local called `link`, deliberately
    not something as reusable as `b`: the pointer handlers already use
    `b` for a button, and this needs to be greppable on its own.
    """
    return set(re.findall(r"(?:\blink|bridge\(\))\.(\w+)\(", MOBILE_SHELL))


def test_the_shell_only_calls_bridge_methods_that_exist() -> None:
    missing = _shell_calls() - _bridge_methods()
    assert not missing, (
        f"the mobile shell calls {sorted(missing)} on CHUCKClipboard, which "
        f"tools/browser_clipboard.js does not define -- the phone cannot "
        f"load a save code until these agree")


def test_the_bridge_still_offers_what_the_phone_needs() -> None:
    methods = _bridge_methods()
    for name in REQUIRED:
        assert name in methods, (
            f"{name}() is gone from tools/browser_clipboard.js; the phone's "
            f"save-code entry goes through it")
        assert name in MOBILE_SHELL, (
            f"the shell no longer calls {name}() -- if entry changed, this "
            f"test should change with it rather than be deleted")


def test_the_shell_waits_for_the_game_before_pressing_enter() -> None:
    """The ordering that makes the handoff work at any frame rate.

    The game drains key events before it polls for a paste, so an Enter
    sent in the same breath as the code arrives at a field that is still
    empty. The shell must hand the text over, wait for `pastePending()`
    to go false, and only then press the key.
    """
    script = MOBILE_SHELL[MOBILE_SHELL.index("codeLoad.onclick"):]
    offer = script.index("offerPaste")
    pending = script.index("pastePending")
    press = script.index("key(codeLoad")
    assert offer < pending < press, (
        "the shell must offer the code, wait for the game to take it, and "
        "only then press Enter")


def test_the_shell_does_not_know_what_a_save_code_is() -> None:
    """The shell collects characters; the game decides about them.

    Nothing here should validate, normalise, or know the alphabet -- all
    of that lives in `save_code.py` and is shared by every host. A copy
    out here would be a second opinion that could drift.
    """
    assert ALPHABET not in MOBILE_SHELL, (
        "the save-code alphabet has been copied into the mobile shell")
    for word in ("normalise", "decode", "checksum"):
        assert word not in MOBILE_SHELL, (
            f"the shell appears to be doing its own {word}")


def test_the_code_panel_is_offered_only_while_the_game_asks() -> None:
    """No field on screen except on the page that wants one.

    The signal is the game's own: its load page turns browser paste on
    when it opens and off when it leaves. The shell reads that rather
    than tracking scenes itself, so there is one source of truth.
    """
    assert "isPasteEnabled" in MOBILE_SHELL
    assert 'id="codefield"' in MOBILE_SHELL
    assert "#code.open" in MOBILE_SHELL, (
        "the panel is no longer shown and hidden by a class")


def test_the_field_is_set_up_to_raise_a_phone_keyboard_cleanly() -> None:
    """A save code is not prose, and iOS zooms small fields.

    Autocorrect and autocapitalise would mangle a code on the way in
    (the codec forgives case, but not a substituted word), and a font
    smaller than 16px makes Safari zoom the page when the field takes
    focus, which in landscape pushes the game off screen.
    """
    field = MOBILE_SHELL[MOBILE_SHELL.index('id="codefield"'):]
    field = field[:field.index(">")]
    assert 'autocorrect="off"' in field
    assert 'autocomplete="off"' in field
    assert 'spellcheck="false"' in field
    assert 'autocapitalize="characters"' in field
    rule = MOBILE_SHELL[MOBILE_SHELL.index("#codefield{"):]
    rule = rule[:rule.index("}")]
    assert "clamp(16px" in rule, (
        "the code field's font may be under 16px, which makes iOS Safari "
        "zoom when it is focused")


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("All mobile code-entry tests passed.")


if __name__ == "__main__":
    _run_all()
