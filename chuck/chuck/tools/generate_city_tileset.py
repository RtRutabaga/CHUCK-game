"""Generate the rain-dark modern-city arrival tiles."""

import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import CITY, TILE_PX
from generate_sewer_tileset import draw_astral_void


def roof(surface, variant, _frame):
    """Flat upper plane of a very large office building."""
    surface.fill((43, 46, 55))
    pygame.draw.line(surface, (58, 61, 70), (0, 0), (15, 0))
    pygame.draw.line(surface, (32, 35, 43), (0, 15), (15, 15))
    seam = 4 + (variant % 3) * 4
    pygame.draw.line(surface, (37, 40, 48), (seam, 0), (seam, 15))
    surface.set_at(((variant * 5 + 3) % 15, 5), (82, 88, 91))


def cornice(surface, variant, _frame):
    surface.fill((47, 50, 59))
    pygame.draw.rect(surface, (78, 80, 87), (0, 7, 16, 5))
    pygame.draw.line(surface, (112, 114, 118), (0, 7), (15, 7))
    pygame.draw.line(surface, (26, 29, 37), (0, 13), (15, 13), 2)
    surface.set_at(((variant * 5 + 2) % 16, 9), (137, 140, 139))


def facade(surface, variant, _frame):
    surface.fill((49, 52, 61))
    pygame.draw.line(surface, (72, 74, 82), (0, 0), (15, 0))
    pygame.draw.line(surface, (31, 34, 43), (0, 15), (15, 15))
    pygame.draw.line(surface, (38, 41, 49), (0, 7), (15, 7))
    x = 3 + (variant % 3) * 5
    pygame.draw.line(surface, (58, 60, 68), (x, 0), (x, 15))


def side_facade(surface, variant, _frame):
    surface.fill((36, 39, 48))
    pygame.draw.line(surface, (59, 61, 69), (0, 0), (15, 0))
    pygame.draw.line(surface, (25, 28, 36), (0, 15), (15, 15))
    for y in (5, 11):
        pygame.draw.line(surface, (45, 48, 57), (0, y), (15, y + 2))
    pygame.draw.line(surface, (73, 75, 81),
                     (2 + variant % 2, 0), (2 + variant % 2, 15))


def window(surface, variant, frame):
    facade(surface, variant, frame)
    pygame.draw.rect(surface, (25, 51, 68), (3, 2, 10, 11))
    pane = (67 + frame * 3, 101 + frame * 3, 119 + frame * 2)
    if variant == 3:
        pane = ((166, 145, 80), (180, 157, 88), (171, 151, 84))[frame]
    pygame.draw.rect(surface, pane, (4, 3, 8, 9))
    pygame.draw.line(surface, (27, 39, 52), (8, 3), (8, 11))
    pygame.draw.line(surface, (27, 39, 52), (4, 7), (12, 7))
    # A restrained moving rain glint gives the office face life without
    # making windows flash like signs.
    glint_x = 5 + (frame * 3 + variant) % 6
    surface.set_at((glint_x, 4), (132, 166, 178))


def sidewalk(surface, variant, _frame):
    surface.fill((68, 70, 76))
    pygame.draw.line(surface, (43, 46, 53), (0, 15), (15, 15))
    pygame.draw.line(surface, (52, 55, 61), (15, 0), (15, 15))
    pygame.draw.line(surface, (95, 98, 101), (0, 0), (15, 0))
    surface.set_at(((variant * 7 + 2) % 14, 5 + variant * 2), (112, 121, 123))


def curb(surface, variant, _frame):
    surface.fill((79, 80, 82))
    pygame.draw.rect(surface, (114, 114, 110), (0, 0, 16, 5))
    pygame.draw.line(surface, (151, 155, 151), (0, 0), (15, 0))
    pygame.draw.line(surface, (43, 45, 50), (0, 6), (15, 6))
    surface.set_at(((variant * 5 + 1) % 16, 3), (65, 68, 72))


def road(surface, variant, frame):
    surface.fill((25, 29, 36))
    pygame.draw.line(surface, (35, 39, 47), (0, 4 + variant * 3), (15, 4 + variant * 3))
    glint = (variant * 5 + frame * 4) % 16
    pygame.draw.line(surface, (50, 68, 79), (glint, 11), (min(15, glint + 5), 11))
    surface.set_at(((variant * 11 + frame * 3) % 16, 2 + frame * 4), (64, 84, 94))


DRAW = {
    "city_roof": roof,
    "city_cornice": cornice,
    "city_facade": facade,
    "city_side_facade": side_facade,
    "city_window": window,
    "city_sidewalk": sidewalk,
    "city_curb": curb,
    "city_road": road,
    "astral_void": draw_astral_void,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((CITY.cols * TILE_PX, CITY.rows * TILE_PX), pygame.SRCALPHA)
    for row, (name, variants, frames) in enumerate(CITY.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX, row * TILE_PX))
    output = ROOT / "assets" / "tilesets" / CITY.sheet
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
