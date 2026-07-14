"""Choice options, drawn inside the dialogue panel.

A short list of labels under the prompt, with a caret marking the
selection. No box-within-a-box, no highlight bar: the caret is the UI,
which is how a 1994 RPG would have done it.
"""

from __future__ import annotations

from src.core import config
from src.ui.dialogue_box import MARGIN, PAD, PANEL_H


class ChoiceBox:
    """Draws option labels with a caret on the selected one."""

    def __init__(self, assets) -> None:
        self._font = assets.bitmap_font()

    def draw(self, surface, labels: list[str], selected: int) -> None:
        """Options stack upward from the panel's bottom-left."""
        line_h = self._font.get_height() + config.CHOICE_LINE_GAP
        panel_top = surface.get_height() - PANEL_H - MARGIN
        y = panel_top + config.CHOICE_TOP_OFFSET
        for i, label in enumerate(labels):
            caret = ">" if i == selected else " "
            rendered = self._font.render(f"{caret} {label}")
            surface.blit(rendered, (MARGIN + PAD + config.CHOICE_LEFT,
                                    y + i * line_h))
