"""Dialogue box — the text panel NPC lines appear in.

Responsibilities:
    * Render one line of dialogue in a bottom panel (ALttP style).
    * Typewriter reveal, completable instantly (the DialogueScene calls
      complete() when the player presses interact mid-reveal).
    * Show a small "more" indicator once the line is fully shown.

Pure presentation: this class renders text it is given. Which line to
show and when to advance is the DialogueScene's job.
"""

from __future__ import annotations

from src.core import config
from src.core.runtime import touch_host
from src.ui.bitmap_font import glyph_clusters
from src.ui.text import wrap_text

MARGIN = 6           # panel inset from screen edges
PANEL_H = 46         # panel height at native resolution
PAD = 6              # text inset inside the panel

# How far the panel rises when the phone's shell is drawing controls
# over the screen.
#
# A panel left where it has always been -- bottom edge at y=174 of 180
# -- is read straight through the d-pad and the jump and scratch
# buttons. Lifting it by this much puts its bottom edge at y=100, which
# clears the pad on every screen size at the default control size or
# smaller.
#
# It does not clear it at the very largest control setting on the
# smallest screens, and nothing could: lifting further puts the panel
# under the gear and pause chips along the top instead, where they would
# cover the first words rather than the last. The size slider is the
# player's own trade -- bigger controls cover more of the game -- and
# this is one of the things it trades.
#
# Dialogue holds the game still anyway, so covering more of the view
# while it is up costs nothing.
TOUCH_LIFT = 74


def panel_top(screen_height: int) -> int:
    """Where the dialogue panel's top edge sits.

    The foot of the screen, as it always has been, except on a phone,
    where the shell draws a d-pad and four buttons over the lower half
    and the text would be read through them.
    """
    top = screen_height - PANEL_H - MARGIN
    return top - TOUCH_LIFT if touch_host() else top

# Back-compat aliases for this module's existing internals.
_MARGIN, _PANEL_H, _PAD = MARGIN, PANEL_H, PAD
_LINE_SPACING = 3


class DialogueBox:
    """Renders a single dialogue line with a typewriter reveal."""

    def __init__(self, assets) -> None:
        self._font = assets.bitmap_font()
        self._text = ""
        self._clusters: tuple[str, ...] = ()
        self._shown_chars = 0.0

    def show(self, text: str) -> None:
        """Begin displaying a line (restarts the typewriter)."""
        self._text = text
        self._clusters = glyph_clusters(text)
        self._shown_chars = 0.0

    def complete(self) -> None:
        """Reveal the whole line instantly."""
        self._shown_chars = float(len(self._clusters))

    @property
    def is_complete(self) -> bool:
        return self._shown_chars >= len(self._clusters)

    def update(self, dt: float) -> None:
        """Advance the typewriter."""
        if not self.is_complete:
            self._shown_chars = min(
                float(len(self._clusters)),
                self._shown_chars + config.DIALOGUE_CPS * dt,
            )

    def draw(self, surface) -> None:
        """Draw the panel and the revealed portion of the line."""
        import pygame

        sw, sh = surface.get_size()
        panel = pygame.Rect(
            _MARGIN, panel_top(sh), sw - 2 * _MARGIN, _PANEL_H
        )
        pygame.draw.rect(surface, config.COLOR_DIALOGUE_PANEL, panel)
        pygame.draw.rect(surface, config.COLOR_DIALOGUE_BORDER, panel, 1)

        revealed = "".join(self._clusters[: int(self._shown_chars)])
        max_w = panel.width - 2 * _PAD
        y = panel.y + _PAD
        for line in wrap_text(revealed, max_w, lambda s: self._font.size(s)[0]):
            surface.blit(
                self._font.render(line, False, config.COLOR_DIALOGUE_TEXT),
                (panel.x + _PAD, y),
            )
            y += self._font.get_height() + _LINE_SPACING

        if self.is_complete:  # "more" indicator: a small triangle
            bx = panel.right - 8
            by = panel.bottom - 6
            for i in range(3):
                pygame.draw.rect(
                    surface,
                    config.COLOR_DIALOGUE_TEXT,
                    pygame.Rect(bx - (2 - i), by + i - 2, (2 - i) * 2 + 1, 1),
                )
