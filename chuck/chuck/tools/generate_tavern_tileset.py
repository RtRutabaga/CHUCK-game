"""Generate the compact Waterdeep tavern interior tileset."""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import TAVERN, TILE_PX
from generate_pantry_tileset import draw_floor as draw_pantry_floor

WALL = {
    "plaster": (139, 113, 78),
    "shade": (94, 72, 52),
    "beam": (70, 45, 29),
    "light": (166, 139, 96),
}


def draw_wall(surface, variant: int, _frame: int) -> None:
    surface.fill(WALL["plaster"])
    pygame.draw.rect(surface, WALL["beam"], (0, 0, 16, 3))
    pygame.draw.rect(surface, WALL["shade"], (0, 13, 16, 3))
    beam_x = 3 if variant == 0 else 12
    pygame.draw.rect(surface, WALL["beam"], (beam_x, 0, 2, 16))
    pygame.draw.line(surface, WALL["light"], (0, 3), (15, 3))
    # A few fixed plaster flecks keep the wall handmade without noise.
    for x, y in ((7 + variant, 6), (11 - variant * 2, 10), (2, 8)):
        surface.set_at((x, y), WALL["shade"])


def draw_stage_top(surface, variant: int, _frame: int) -> None:
    """Raised but restrained boards for the tavern's tiny wall stage."""
    surface.fill((129, 83, 43))
    pygame.draw.line(surface, (169, 112, 56), (0, 2), (15, 2))
    pygame.draw.line(surface, (73, 45, 29), (0, 15), (15, 15))
    seam = 5 + variant * 6
    pygame.draw.line(surface, (91, 55, 33), (seam, 3), (seam, 14))
    surface.set_at(((2 + variant * 9) % 16, 10), (54, 39, 31))


def draw_stage_front(surface, variant: int, _frame: int) -> None:
    surface.fill((78, 46, 29))
    pygame.draw.rect(surface, (109, 65, 34), (0, 0, 16, 4))
    pygame.draw.line(surface, (49, 33, 27), (0, 15), (15, 15))
    post_x = 3 if variant == 0 else 12
    pygame.draw.rect(surface, (58, 37, 27), (post_x, 4, 2, 12))
    surface.set_at((8, 8), (178, 128, 57))


DRAW = {
    "tavern_floor": draw_pantry_floor,
    "tavern_interior_wall": draw_wall,
    "tavern_stage_top": draw_stage_top,
    "tavern_stage_front": draw_stage_front,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((TAVERN.cols * TILE_PX, TAVERN.rows * TILE_PX),
                           pygame.SRCALPHA)
    for row_i, (name, variants, frames) in enumerate(TAVERN.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / TAVERN.sheet
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
