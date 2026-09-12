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
_GROUP_GAP = 8                # between the death count and the cigarettes


# The death count's icon: a rat's skull over crossed bones, one pixel per
# character. A human skull at this size is a circle with two holes in it
# and could be anybody's; what makes it Chuck's is the long snout tapering
# to a pair of incisors, and the two round ears, which a real skull would
# not have and a rat at eleven pixels cannot do without.
#   B bone   S shadow side   D socket / outline
_DEATH_ICON = (
    "BBDDD...DDDBB",
    "BBDBBDDDBBDBB",
    "DDBBBBBBBBBDD",
    ".DBBBBBBBBBD.",
    ".DBDDBBBDDBD.",
    ".DBDDBBBDDSD.",
    "..DBBBBBBSD..",
    "..DDBBBBSDD..",
    "DDBBDBBSDBBDD",
    "BBDDDBDBDDDBB",
    "BBD..D.D..DBB",
)
_DEATH_COLOURS = {
    "B": (226, 218, 196),
    "S": (168, 156, 136),
    "D": (38, 30, 30),
}


def death_icon():
    """The skull and crossbones as a small alpha surface."""
    import pygame

    height, width = len(_DEATH_ICON), len(_DEATH_ICON[0])
    icon = pygame.Surface((width, height), pygame.SRCALPHA)
    for y, row in enumerate(_DEATH_ICON):
        for x, char in enumerate(row):
            if char in _DEATH_COLOURS:
                icon.set_at((x, y), _DEATH_COLOURS[char])
    return icon


class HUD:
    """Draws overlay UI on top of the world. Owned by the WorldScene."""

    def __init__(self, sanity_system, font=None, cigarettes=None,
                 deaths=None) -> None:
        self.sanity = sanity_system
        self._font = font
        self.cigarettes = cigarettes
        self.deaths = deaths
        self._death_icon = None

    def draw(self, surface) -> None:
        """Draw the cigarette meter in screen space (ignores camera)."""
        import pygame

        # The overall-game cigarette count (session 128), top-right and
        # quiet: a tiny unlit cigarette pictogram beside the total.
        if self.cigarettes is not None and self._font is not None:
            label = self._font.render(f"x{self.cigarettes.total}")
            label.set_alpha(200)
            x = config.NATIVE_WIDTH - _MARGIN_X - label.get_width()
            surface.blit(label, (x, _MARGIN_Y))
            icon_x = x - 12
            icon_y = _MARGIN_Y + 3
            pygame.draw.rect(surface, config.COLOR_CIG_PAPER,
                             pygame.Rect(icon_x, icon_y, 7, 3))
            pygame.draw.rect(surface, config.COLOR_CIG_FILTER,
                             pygame.Rect(icon_x, icon_y, 2, 3))

            # The death count, just left of it and in the same voice:
            # a rat's skull and crossbones and the total. Beside the
            # cigarettes rather than anywhere louder, because in this
            # game dying is quiet too.
            if self.deaths is not None:
                if self._death_icon is None:
                    self._death_icon = death_icon()
                deaths = self._font.render(f"x{self.deaths.total}")
                deaths.set_alpha(200)
                deaths_x = icon_x - _GROUP_GAP - deaths.get_width()
                surface.blit(deaths, (deaths_x, _MARGIN_Y))
                skull = self._death_icon
                skull_y = (_MARGIN_Y + deaths.get_height() // 2
                           - skull.get_height() // 2)
                surface.blit(skull, (deaths_x - skull.get_width() - 2,
                                     max(0, skull_y)))

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
