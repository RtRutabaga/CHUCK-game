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

FLOOR = {
    "base": (116, 76, 43),
    "light": (148, 100, 55),
    "dark": (78, 50, 32),
    "nail": (48, 38, 34),
}
WALL = {
    "plaster": (139, 113, 78),
    "shade": (94, 72, 52),
    "beam": (70, 45, 29),
    "light": (166, 139, 96),
}


def draw_floor(surface, variant: int, _frame: int) -> None:
    surface.fill(FLOOR["base"])
    split = 7 + (variant % 2)
    pygame.draw.line(surface, FLOOR["dark"], (0, split), (15, split))
    pygame.draw.line(surface, FLOOR["light"], (0, split + 1), (15, split + 1))
    pygame.draw.line(surface, FLOOR["dark"], (0, 15), (15, 15))
    upper_joint = (4 + variant * 5) % 16
    lower_joint = (11 + variant * 3) % 16
    pygame.draw.line(surface, FLOOR["dark"], (upper_joint, 0),
                     (upper_joint, split))
    pygame.draw.line(surface, FLOOR["dark"], (lower_joint, split + 1),
                     (lower_joint, 15))
    for x, y in ((2 + variant * 3, 3), (13 - variant * 2, 12)):
        surface.set_at((x % 16, y), FLOOR["nail"])


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


DRAW = {
    "tavern_floor": draw_floor,
    "tavern_interior_wall": draw_wall,
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
