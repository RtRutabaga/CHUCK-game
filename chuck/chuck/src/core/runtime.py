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

    **What this may change is wording, and only wording:** which control
    a line of text tells the player to press. There is no layout, scene,
    rule or control behind it, because there is one CHUCK and the phone
    runs the same build as the PC and the Xbox. A player on a phone is
    told to tap INSPECT because that is what the button in front of them
    says; a player on a keyboard is told to press E. Both are the same
    game doing the same thing.

    Anything more than wording belongs in the shell, not here. See
    TWO-AGENT-GIT-WORKFLOW.md "There Is Only One CHUCK".
    """
    global _TOUCH_HOST
    if _TOUCH_HOST is None:
        _TOUCH_HOST = _detect_touch_host()
    return _TOUCH_HOST
