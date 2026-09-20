"""Tutorial hint text.

A single line of pale text near the top of the screen, shown only
while Chuck is in reach of something he can interact with (and, later,
at the sewer's jump and combat teaching moments).

TEMPORARY BY DESIGN: this exists for the opening tutorial areas and must not
become permanent instructional UI. It is scoped by
config.TUTORIAL_MAPS, and deleting the system later means deleting
this file, its config block, and three lines in the WorldScene.

No panel, no border, no icon — just the words, the way a 1994 game
would have done it.
"""

from __future__ import annotations

from src.core import config


class TutorialHint:
    """Draws one centered line of hint text near the top of the view."""

    def __init__(self, assets, input_manager=None) -> None:
        self._font = assets.bitmap_font()
        self._input = input_manager

    def draw(self, surface, text: str) -> None:
        """Centered horizontally, TUTORIAL_HINT_TOP px from the top.

        Names the button rather than the key when the player is on a
        controller, and can be told there is nothing worth saying on
        this device at all (src/ui/prompts.py).
        """
        from src.ui import prompts

        line = prompts.hint(self._input, text)
        if not line:
            # A hint with no wording for this device is not shown. The
            # phone's pause button is on screen the whole time and needs
            # no teaching.
            return
        rendered = self._font.render(line)
        x = (surface.get_width() - rendered.get_width()) // 2
        surface.blit(rendered, (x, config.TUTORIAL_HINT_TOP))
