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


def wall(surface, variant, _frame):
    surface.fill((49, 52, 61))
    pygame.draw.line(surface, (72, 74, 82), (0, 0), (15, 0))
    pygame.draw.line(surface, (31, 34, 43), (0, 15), (15, 15))
    y = 5 + (variant % 2) * 5
    pygame.draw.line(surface, (37, 40, 48), (0, y), (15, y))
    surface.set_at(((variant * 5 + 3) % 15, 3), (98, 108, 112))


def window(surface, variant, _frame):
    wall(surface, variant, 0)
    pygame.draw.rect(surface, (25, 51, 68), (3, 2, 10, 11))
    pygame.draw.rect(surface, (69, 104, 121), (4, 3, 8, 9))
    pygame.draw.line(surface, (27, 39, 52), (8, 3), (8, 11))
    pygame.draw.line(surface, (27, 39, 52), (4, 7), (12, 7))
    if variant == 3:
        pygame.draw.rect(surface, (172, 151, 84), (9, 3, 3, 4))


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
    "city_wall": wall,
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
