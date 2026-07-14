"""Bitmap pixel font.

Responsibilities:
    * Render text from a hand-drawn glyph sheet (assets/fonts/
      pixel_font.png, built by tools/generate_font.py) with zero
      anti-aliasing — every letter is crisp at native resolution.
    * Mirror enough of pygame.font.Font's API (size / get_height /
      render) that callers like the DialogueBox don't care which
      implementation they hold.

GLYPH_ORDER is the single source of truth for which characters exist
and their order in the sheet; the generator imports it from here.
Unknown characters are a loud error: dialogue is our own data, and a
character we can't draw is a writing bug to fix, not to hide.

pygame is imported only inside methods; GLYPH_ORDER and metrics are
usable headless (tests check that all dialogue text is renderable).
"""

from __future__ import annotations

GLYPH_ORDER = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    ".,!?'\"-:;()/ >"
)

GLYPH_W = 5   # glyph cell width in the sheet
GLYPH_H = 9   # 7px body + 2px descender
ADVANCE = 6   # horizontal step per character (cell + 1px spacing)


class BitmapFont:
    """A fixed-advance pixel font sliced from a glyph sheet."""

    def __init__(self, glyphs: dict[str, object]) -> None:
        """glyphs maps each character in GLYPH_ORDER to its Surface.
        Built by AssetManager.bitmap_font(); don't construct directly.
        """
        self._glyphs = glyphs

    # ------------------------------------------------------------------
    # Metrics (pure — no pygame)
    # ------------------------------------------------------------------
    def size(self, text: str) -> tuple[int, int]:
        """Pixel size of text when rendered (pygame.font.Font-compatible)."""
        if not text:
            return (0, GLYPH_H)
        return (len(text) * ADVANCE - 1, GLYPH_H)

    def get_height(self) -> int:
        return GLYPH_H

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def render(self, text: str, antialias: bool = False, color=None):
        """Render text to a new transparent Surface.

        antialias and color exist for pygame.font.Font compatibility
        and are ignored: pixel fonts are never anti-aliased, and the
        glyph color is baked into the sheet.
        """
        import pygame

        surface = pygame.Surface(self.size(text), pygame.SRCALPHA)
        for i, char in enumerate(text):
            glyph = self._glyphs.get(char)
            if glyph is None:
                raise KeyError(
                    f"Character {char!r} is not in the pixel font. "
                    f"Add it to tools/generate_font.py and regenerate, "
                    f"or fix the dialogue text."
                )
            surface.blit(glyph, (i * ADVANCE, 0))
        return surface
