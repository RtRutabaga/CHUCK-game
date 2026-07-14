"""HUD — the in-world heads-up display.

Responsibilities:
    * Draw the sanity meter (the only HUD element for Phase One).
    * Stay minimal and quiet; the Game Bible's tone calls for a calm
      screen, not a busy one.

The meter IS a cigarette (diegetic, per the HUD design note): the
remaining paper is Chuck's remaining sanity, with the lit ember at the
burn line. As sanity drops, the cigarette burns down toward the filter.
A faint ash line marks the full extent, so the player can read
"how much is gone" at a glance. No numbers, no bar frame, no icons.
"""

from __future__ import annotations

from src.core import config

# Layout in native-resolution pixels.
_MARGIN_X, _MARGIN_Y = 4, 4
_FILTER_W, _H = 5, 4          # the filter never burns
_PAPER_MAX_W = 32             # full-sanity paper length
_EMBER_W = 2


class HUD:
    """Draws overlay UI on top of the world. Owned by the WorldScene."""

    def __init__(self, sanity_system) -> None:
        self.sanity = sanity_system

    def draw(self, surface) -> None:
        """Draw the cigarette meter in screen space (ignores camera)."""
        import pygame

        frac = max(0.0, min(1.0, self.sanity.fraction))
        paper_w = round(_PAPER_MAX_W * frac)

        x, y = _MARGIN_X, _MARGIN_Y
        # Faint ash line across the full extent (what has burned away).
        pygame.draw.rect(
            surface,
            config.COLOR_CIG_ASH,
            pygame.Rect(x + _FILTER_W, y + _H // 2, _PAPER_MAX_W + _EMBER_W, 1),
        )
        # Filter (constant).
        pygame.draw.rect(
            surface, config.COLOR_CIG_FILTER, pygame.Rect(x, y, _FILTER_W, _H)
        )
        # Remaining paper.
        if paper_w > 0:
            pygame.draw.rect(
                surface,
                config.COLOR_CIG_PAPER,
                pygame.Rect(x + _FILTER_W, y, paper_w, _H),
            )
            # The ember sits at the burn line. Always lit.
            pygame.draw.rect(
                surface,
                config.COLOR_CIG_EMBER,
                pygame.Rect(x + _FILTER_W + paper_w, y, _EMBER_W, _H),
            )
        # TODO (polish, much later): ember flicker of +-1 shade. Maybe.
