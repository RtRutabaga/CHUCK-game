"""The system clipboard, where there is one.

Copying the save code out and pasting it back is the whole point of a
code, so this wraps `pygame.scrap` in something that never raises. SDL's
clipboard wants a display, is absent on some builds, and in a browser
build it depends on what the page is allowed to do -- none of which a
menu should have to know about.

Every call therefore answers honestly and quietly: `copy` returns False
if the text did not go anywhere, `paste` returns None if there was
nothing to take. The menu's fallback for both is the same and is not a
failure state: the code is on screen, large enough to read and type.
"""

from __future__ import annotations

import sys
import asyncio


def _scrap():
    """pygame.scrap, initialised, or None if this build has no clipboard."""
    try:
        import pygame
        from pygame import scrap
    except ImportError:
        return None
    try:
        if not scrap.get_init():
            scrap.init()
    except (pygame.error, NotImplementedError, AttributeError):
        return None
    return scrap


def available() -> bool:
    """Whether copy and paste can be offered at all."""
    return _scrap() is not None


def copy(text: str) -> bool:
    """Put text on the clipboard. False means the player must read it."""
    scrap = _scrap()
    if scrap is None:
        return False
    try:
        scrap.put_text(text)
    except Exception:       # noqa: BLE001 - a clipboard is never worth a crash
        return False
    return True


async def copy_browser(text: str) -> bool:
    """Copy through the secure browser Clipboard API when running on web.

    Pygame's SDL clipboard is not implemented by the WebAssembly build. The
    browser API returns a promise and may still be refused by a browser or
    device policy, so this keeps the same honest True/False contract.
    """
    if sys.platform != "emscripten":
        return copy(text)
    try:
        import platform
        bridge = platform.window.CHUCKClipboard
        request = bridge.beginCopy(text)
        try:
            for _ in range(100):
                status = str(bridge.copyStatus(request))
                if status != "pending":
                    return status == "copied"
                await asyncio.sleep(0.05)
            return False
        finally:
            bridge.finishCopy(request)
    except Exception:       # noqa: BLE001 - clipboard denial is ordinary
        return False
    return True


def enable_browser_paste(enabled: bool) -> None:
    if sys.platform != "emscripten":
        return
    try:
        import platform
        platform.window.CHUCKClipboard.enablePaste(enabled)
    except Exception:
        pass


def take_browser_paste() -> str | None:
    if sys.platform != "emscripten":
        return None
    try:
        import platform
        text = str(platform.window.CHUCKClipboard.takePaste())
        return text.replace("\x00", "") or None
    except Exception:
        return None


def paste() -> str | None:
    """Take text off the clipboard, or None if there is none to take."""
    scrap = _scrap()
    if scrap is None:
        return None
    try:
        text = scrap.get_text()
    except Exception:       # noqa: BLE001 - as above
        return None
    if not text:
        return None
    # SDL hands back whatever was copied, which may carry a trailing NUL
    # from another program.
    return text.replace("\x00", "")
