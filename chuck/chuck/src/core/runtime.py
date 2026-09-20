"""Small platform differences shared by asset loaders."""

from pathlib import Path
import sys

# Settled once, on first ask: reading it crosses into JavaScript, and it
# cannot change while the page is open.
_TOUCH_HOST: bool | None = None


def audio_path(path: Path) -> Path:
    """Web builds ship OGG copies; authored cue names keep their WAV keys."""
    return path.with_suffix(".ogg") if sys.platform == "emscripten" else path


def _detect_touch_host() -> bool:
    if sys.platform != "emscripten":
        return False
    try:
        import platform
        return "mobile=1" in str(platform.window.location.search)
    except Exception:       # noqa: BLE001 - a guess is not worth a crash
        return False


def touch_host() -> bool:
    """Whether this build is running inside the phone's touch shell.

    The shell already marks the page it embeds -- `index.html?mobile=1`
    -- and the desktop page already reads that marker to hide its link
    to `/mobile/`. This is the same one signal read from the other side,
    so the phone is identified once and in one way rather than the game
    growing its own opinion about what a phone is.

    **Two things may depend on this, and nothing else:**

    1. *Wording* -- which control a line of text names. A player on a
       phone is told to tap INSPECT because that is what the button in
       front of them says; a player on a keyboard is told to press E.
    2. *Where the game's own UI sits*, so that it is not underneath the
       controls the shell draws over the screen. The phone has a d-pad
       and four buttons occupying the lower half; the dialogue panel
       moves out from under them.

    Both are the same game presented around a different physical screen,
    which is what any layout does. What must never depend on this is
    what the game **is**: no scene, no rule, no content, no control
    behaviour, nothing a player could describe as happening differently
    on a phone.

    That second clause was added deliberately, after the first was
    written as "wording, and only wording". It is the kind of line that
    slides, so it is worth being plain: if you find yourself wanting a
    third clause, you are probably building the fork `/mobile/` exists
    to avoid. See TWO-AGENT-GIT-WORKFLOW.md "There Is Only One CHUCK".
    """
    global _TOUCH_HOST
    if _TOUCH_HOST is None:
        _TOUCH_HOST = _detect_touch_host()
    return _TOUCH_HOST
