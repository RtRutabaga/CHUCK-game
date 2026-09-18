"""Asset loading and caching.

Responsibilities:
    * Load images (and later: sounds, fonts) from the assets/ tree.
    * Cache everything so each file is loaded from disk exactly once.
    * Slice sprite sheets into frame grids.
    * Fail loudly and clearly when an asset is missing or malformed.

Gameplay code should never call pygame.image.load directly — it asks
this manager, so asset handling stays in one place.
"""

from __future__ import annotations

import pygame

from src.core import config
from src.core.runtime import audio_path
from src.ui.bitmap_font import ADVANCE, GLYPH_H, GLYPH_ORDER, GLYPH_W, BitmapFont


class AssetManager:
    """Loads and caches game assets. One instance, owned by Game."""

    def __init__(self) -> None:
        self._images: dict[str, pygame.Surface] = {}
        self._sounds: dict[str, "pygame.mixer.Sound"] = {}
        self._fonts: dict[tuple[str, int], "pygame.font.Font"] = {}
        self._bitmap_font: BitmapFont | None = None

    # ------------------------------------------------------------------
    # Images
    # ------------------------------------------------------------------
    def image(self, relative_path: str) -> pygame.Surface:
        """Return a cached Surface for a file under assets/sprites/.

        Uses convert_alpha() so per-pixel transparency works and blits
        are fast.
        """
        if relative_path not in self._images:
            path = config.SPRITES_DIR / relative_path
            if not path.is_file():
                raise FileNotFoundError(
                    f"Missing sprite {path}. If this is Chuck's sheet, run: "
                    f"python tools/generate_chuck_sprites.py"
                )
            self._images[relative_path] = pygame.image.load(
                str(path)
            ).convert_alpha()
        return self._images[relative_path]

    def sheet(
        self, relative_path: str, frame_w: int, frame_h: int
    ) -> list[list[pygame.Surface]]:
        """Slice a sprite sheet into a [row][col] grid of frames.

        Fails loudly if the image size isn't an exact multiple of the
        frame size — a silently misaligned sheet produces garbage art.
        """
        img = self.image(relative_path)
        w, h = img.get_size()
        if w % frame_w or h % frame_h:
            raise ValueError(
                f"Sheet {relative_path} is {w}x{h}, not a multiple of "
                f"frame size {frame_w}x{frame_h}"
            )
        return [
            [
                img.subsurface(
                    pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                )
                for col in range(w // frame_w)
            ]
            for row in range(h // frame_h)
        ]

    def tileset(self, filename: str, tile_px: int
                ) -> list[list["pygame.Surface"]]:
        """Slice a sheet from assets/tilesets/ into a [row][col] grid."""
        key = f"tileset:{filename}"
        if key not in self._images:
            path = config.TILESETS_DIR / filename
            if not path.is_file():
                raise FileNotFoundError(
                    f"Missing tileset {path}. Run: "
                    f"python tools/generate_tileset.py"
                )
            self._images[key] = pygame.image.load(str(path)).convert_alpha()
        img = self._images[key]
        w, h = img.get_size()
        return [
            [
                img.subsurface(pygame.Rect(c * tile_px, r * tile_px,
                                           tile_px, tile_px))
                for c in range(w // tile_px)
            ]
            for r in range(h // tile_px)
        ]

    # ------------------------------------------------------------------
    # Sounds / fonts (future sessions)
    # ------------------------------------------------------------------
    def sound(self, relative_path: str) -> "pygame.mixer.Sound":
        """Return a cached Sound for a file under assets/audio/sfx/."""
        if relative_path not in self._sounds:
            path = audio_path(config.SFX_DIR / relative_path)
            if not path.is_file():
                raise FileNotFoundError(
                    f"Missing sound {path}. Run: python tools/generate_audio.py"
                )
            self._sounds[relative_path] = pygame.mixer.Sound(str(path))
        return self._sounds[relative_path]

    def bitmap_font(self) -> BitmapFont:
        """The game's pixel font, sliced from assets/fonts/pixel_font.png.

        This is what all in-game text should use; pygame's default font
        is illegibly mangled at native resolution.
        """
        if self._bitmap_font is None:
            path = config.FONTS_DIR / "pixel_font.png"
            if not path.is_file():
                raise FileNotFoundError(
                    f"Missing font sheet {path}. Run: python tools/generate_font.py"
                )
            sheet = pygame.image.load(str(path)).convert_alpha()
            expected = (GLYPH_W * len(GLYPH_ORDER), GLYPH_H)
            if sheet.get_size() != expected:
                raise ValueError(
                    f"Font sheet is {sheet.get_size()}, expected {expected}. "
                    f"Regenerate with tools/generate_font.py"
                )
            glyphs = {
                char: sheet.subsurface(
                    pygame.Rect(i * GLYPH_W, 0, GLYPH_W, GLYPH_H)
                )
                for i, char in enumerate(GLYPH_ORDER)
            }
            self._bitmap_font = BitmapFont(glyphs)
        return self._bitmap_font

    def default_font(self, size: int) -> "pygame.font.Font":
        """pygame's built-in font, cached. Debug/tooling only — it is
        unreadable at native resolution. Game text uses bitmap_font().
        """
        key = ("__default__", size)
        if key not in self._fonts:
            pygame.font.init()
            self._fonts[key] = pygame.font.Font(None, size)
        return self._fonts[key]

    def font(self, relative_path: str, size: int) -> "pygame.font.Font":
        """Return a cached Font loaded from assets/fonts/.

        TODO: Implement when a real font file exists; use default_font
              until then.
        """
        raise NotImplementedError("Font files arrive with art direction.")
