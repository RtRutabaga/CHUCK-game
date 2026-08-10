"""Generate the open manhole Chuck goes down into the sewer through.

This used to be a human-sized concrete portal cut into an office
foundation, which read as the mouth of a subway rather than as a way
into a sewer. What a sewer entrance actually looks like from above is
much plainer: a round hole in the pavement, a rusted rim, black
underneath, and the cover levered off and left lying beside it at an
angle with SEWER cast into its face.

Drawn from overhead like everything else on a city map. The cover sits
off to one side rather than centred behind the hole, because a cover
directly behind it reads as a second, closed hole.
"""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]

# Props are drawn centred on their tile with their bottom edge on the
# tile's bottom edge, so the canvas is sized to put the HOLE -- not the
# sprite -- over the middle of the tile that is actually solid.
WIDTH, HEIGHT = 92, 48
HOLE = (46, 36)          # centre of the open hole: dead centre of the tile
HOLE_RX, HOLE_RY = 14, 11
COVER = (74, 22)         # the cover, off to one side and slightly behind
COVER_R = 13

_APRON = (96, 98, 102)
_APRON_DARK = (74, 76, 82)
_RIM = (86, 62, 40)
_RIM_LIT = (122, 92, 58)
_DARK = (6, 7, 9)
_WALL = (38, 36, 34)
_RUNG = (72, 76, 80)
_COVER = (118, 74, 48)
_COVER_LIT = (150, 100, 66)
_COVER_DARK = (72, 44, 28)
_LETTER = (48, 28, 16)
_TREAD = (104, 64, 42)

# 3x5 pixel letters: only the five this cover needs.
_GLYPHS = {
    "S": ("111", "100", "111", "001", "111"),
    "E": ("111", "100", "110", "100", "111"),
    "W": ("101", "101", "101", "111", "101"),
    "R": ("111", "101", "110", "101", "101"),
}


def _text(surface, word: str, left: int, top: int, colour) -> None:
    for index, character in enumerate(word):
        glyph = _GLYPHS[character]
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    surface.set_at((left + index * 4 + col, top + row), colour)


def _cover(size: int) -> pygame.Surface:
    """The lifted cover, drawn face-on before it is tilted into place."""
    face = pygame.Surface((size, size), pygame.SRCALPHA)
    middle = size // 2
    pygame.draw.circle(face, _COVER_DARK, (middle, middle), middle)
    pygame.draw.circle(face, _COVER, (middle, middle), middle - 1)
    pygame.draw.circle(face, _COVER_LIT, (middle, middle), middle - 1, 1)
    # The diamond tread: widely spaced, and barely darker than the iron,
    # because at this size a dense pattern turns the whole cover to noise.
    for offset in range(-size, size, 7):
        pygame.draw.line(face, _TREAD,
                         (middle + offset, 1), (middle + offset + size, size))
        pygame.draw.line(face, _TREAD,
                         (middle + offset, size), (middle + offset + size, 1))
    # A raised band across the middle, kept clear of tread, with the word
    # cast into it -- the one thing on the cover that has to read.
    pygame.draw.rect(face, _COVER_LIT, (1, middle - 4, size - 2, 9))
    pygame.draw.line(face, _COVER_DARK, (1, middle + 5), (size - 2, middle + 5))
    _text(face, "SEWER", middle - 9, middle - 2, _LETTER)
    # Clip the tread back inside the disc.
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (middle, middle), middle)
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return face


def main() -> None:
    pygame.init()
    image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # A worn concrete apron, so the hole is not floating on clean paving.
    pygame.draw.ellipse(image, _APRON_DARK,
                        (HOLE[0] - HOLE_RX - 7, HOLE[1] - HOLE_RY - 6,
                         (HOLE_RX + 7) * 2, (HOLE_RY + 6) * 2))
    pygame.draw.ellipse(image, _APRON,
                        (HOLE[0] - HOLE_RX - 6, HOLE[1] - HOLE_RY - 5,
                         (HOLE_RX + 6) * 2, (HOLE_RY + 5) * 2))

    # The rusted rim, and the hole itself.
    pygame.draw.ellipse(image, _RIM,
                        (HOLE[0] - HOLE_RX - 2, HOLE[1] - HOLE_RY - 2,
                         (HOLE_RX + 2) * 2, (HOLE_RY + 2) * 2))
    pygame.draw.ellipse(image, _RIM_LIT,
                        (HOLE[0] - HOLE_RX - 2, HOLE[1] - HOLE_RY - 2,
                         (HOLE_RX + 2) * 2, (HOLE_RY + 2) * 2), 1)
    pygame.draw.ellipse(image, _DARK,
                        (HOLE[0] - HOLE_RX, HOLE[1] - HOLE_RY,
                         HOLE_RX * 2, HOLE_RY * 2))

    # Looking in: the far wall of the shaft catches a little daylight,
    # and there is a ladder on it going down out of sight.
    pygame.draw.ellipse(image, _WALL,
                        (HOLE[0] - HOLE_RX + 2, HOLE[1] - HOLE_RY + 2,
                         HOLE_RX * 2 - 4, HOLE_RY))
    pygame.draw.ellipse(image, _DARK,
                        (HOLE[0] - HOLE_RX + 3, HOLE[1] - HOLE_RY + 5,
                         HOLE_RX * 2 - 6, HOLE_RY + 2))
    for step, y in enumerate((HOLE[1] - 6, HOLE[1] - 3)):
        inset = 8 + step * 2
        pygame.draw.line(image, _RUNG,
                         (HOLE[0] - HOLE_RX + inset, y),
                         (HOLE[0] + HOLE_RX - inset, y))

    # The cover, levered off and dropped beside the hole at an angle. It
    # overlaps the apron so it plainly came from this hole.
    tilted = pygame.transform.rotate(_cover(COVER_R * 2), -18)
    shadow = pygame.Surface(tilted.get_size(), pygame.SRCALPHA)
    shadow.fill((0, 0, 0, 90))
    shadow.blit(tilted, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    image.blit(shadow, (COVER[0] - tilted.get_width() // 2 + 2,
                        COVER[1] - tilted.get_height() // 2 + 3))
    image.blit(tilted, (COVER[0] - tilted.get_width() // 2,
                        COVER[1] - tilted.get_height() // 2))

    output = ROOT / "assets" / "sprites" / "objects" / "city_sewer_entrance.png"
    pygame.image.save(image, output)
    print(f"Wrote {output} ({image.get_width()}x{image.get_height()})")
    pygame.quit()


if __name__ == "__main__":
    main()
