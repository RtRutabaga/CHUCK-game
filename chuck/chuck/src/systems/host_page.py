"""Telling the page around the game the little it needs to know.

The browser build runs inside a page that has furniture of its own: the
desktop page carries a link to `/mobile/`, and the phone's shell carries
its controls and panels. Some of that furniture is only right at certain
moments. The link is for somebody who has just arrived and is holding a
phone, so it belongs on the title screen and nowhere else -- left up it
sits across the bottom of the game for the rest of the session, and a
player on a controller has no way to be rid of it.

This is the same one-way arrangement `clipboard.enable_browser_paste`
already uses: the game says where it is, the page decides what to do
about that, and nothing in the game depends on the answer. Off the web
it does nothing at all.
"""

from __future__ import annotations

import sys


def set_at_title(at_title: bool) -> None:
    """Say whether the title screen is the thing on screen."""
    if sys.platform != "emscripten":
        return
    try:
        import platform
        platform.window.CHUCKPage.setAtTitle(bool(at_title))
    except Exception:       # noqa: BLE001 - page furniture is never worth a crash
        pass
