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

import unicodedata

GLYPH_ORDER = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    ".,!?'\"-:;()/ >"
)

# Phase 12 deliberately uses four authored strings made from Yi symbols and
# distorted Latin combining marks. Keep this whitelist contained: arbitrary
# missing writing still fails loudly, while these exact characters receive a
# deterministic procedural rune/mark treatment instead of empty boxes.
STRANGE_GLYPHS = frozenset(
    "ꋖꁝꌅꊿꁲꂵꑀꃳꏳꈵꃔ"
    "̵̶̸̨̧̛̖̻͙̞̲͖̣̘̜̝̆͗͋ͬͣ̽̀͘͢͟͠҉͏̴̷̡́̕͜͡͞"
    "\u0322\u035d"
)

GLYPH_W = 5   # glyph cell width in the sheet
GLYPH_H = 9   # 7px body + 2px descender
ADVANCE = 6   # horizontal step per character (cell + 1px spacing)


def glyph_clusters(text: str) -> tuple[str, ...]:
    """Group combining marks with their base glyph for metrics/reveal."""
    clusters: list[str] = []
    for char in text:
        if unicodedata.combining(char) and clusters:
            clusters[-1] += char
        else:
            clusters.append(char)
    return tuple(clusters)


class BitmapFont:
    """A fixed-advance pixel font sliced from a glyph sheet."""

    def __init__(self, glyphs: dict[str, object]) -> None:
        """glyphs maps each character in GLYPH_ORDER to its Surface.
        Built by AssetManager.bitmap_font(); don't construct directly.
        """
        self._glyphs = glyphs
        self._strange_cache: dict[str, object] = {}

    # ------------------------------------------------------------------
    # Metrics (pure — no pygame)
    # ------------------------------------------------------------------
    def size(self, text: str) -> tuple[int, int]:
        """Pixel size of text when rendered (pygame.font.Font-compatible)."""
        if not text:
            return (0, GLYPH_H)
        return (len(glyph_clusters(text)) * ADVANCE - 1, GLYPH_H)

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
        for i, cluster in enumerate(glyph_clusters(text)):
            glyph = self._glyph_for_cluster(cluster)
            surface.blit(glyph, (i * ADVANCE, 0))
        return surface

    def _glyph_for_cluster(self, cluster: str):
        """Return ordinary baked art or the contained Phase 12 treatment."""
        base = cluster[0]
        marks = cluster[1:]
        if base not in self._glyphs and base not in STRANGE_GLYPHS:
            self._missing(base)
        for mark in marks:
            if mark not in STRANGE_GLYPHS:
                self._missing(mark)
        if not marks and base in self._glyphs:
            return self._glyphs[base]
        if cluster not in self._strange_cache:
            self._strange_cache[cluster] = self._build_strange_glyph(
                base, marks
            )
        return self._strange_cache[cluster]

    @staticmethod
    def _missing(char: str) -> None:
        raise KeyError(
            f"Character {char!r} is not in the pixel font. "
            f"Add it to tools/generate_font.py and regenerate, "
            f"or fix the dialogue text."
        )

    def _build_strange_glyph(self, base: str, marks: str):
        """Build one crisp 5x9 rune, retaining marks in the same cell."""
        import pygame
        from src.core import config

        glyph = pygame.Surface((GLYPH_W, GLYPH_H), pygame.SRCALPHA)
        color = (*config.COLOR_DIALOGUE_TEXT, 255)
        ordinary = self._glyphs.get(base)
        if ordinary is not None:
            glyph.blit(ordinary, (0, 0))
        else:
            # Stable strokes derived from the authored symbol's code point.
            seed = ord(base)
            for y in range(1, 7):
                x = (seed + y * 3 + (seed >> (y % 5))) % GLYPH_W
                glyph.set_at((x, y), color)
                if (seed >> y) & 1 and x + 1 < GLYPH_W:
                    glyph.set_at((x + 1, y), color)
            glyph.set_at((seed % GLYPH_W, 0), color)
            glyph.set_at(((seed // 7) % GLYPH_W, 6), color)

        # Combining marks become tiny deterministic accents above/below the
        # base. Multiple marks vary their x positions rather than taking the
        # extra character cells that would destroy the source's visual intent.
        for index, mark in enumerate(marks):
            seed = ord(mark) + index * 11
            x = seed % GLYPH_W
            y = 0 if index % 2 == 0 else 8
            glyph.set_at((x, y), color)
            if (seed & 1) and x + 1 < GLYPH_W:
                glyph.set_at((x + 1, y), color)
            if index >= 2:
                glyph.set_at(((x + 2) % GLYPH_W, 7), color)
        return glyph
