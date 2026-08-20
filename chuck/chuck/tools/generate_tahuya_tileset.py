"""Generate the dedicated Pacific Northwest terrain for Tahuya."""

import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import TAHUYA, TILE_PX


def _flecks(surface, variant, colours, count=5):
    for i in range(count):
        x = (variant * 7 + i * 11 + 3) % 16
        y = (variant * 13 + i * 5 + 2) % 16
        surface.set_at((x, y), colours[i % len(colours)])


def forest_ground(surface, variant, _frame):
    surface.fill((25, 37, 31))
    _flecks(surface, variant, ((42, 55, 39), (62, 50, 35), (18, 29, 27)), 8)
    pygame.draw.line(surface, (50, 42, 30),
                     ((variant * 5 + 1) % 13, 12),
                     ((variant * 5 + 4) % 13 + 2, 13))


def dense_forest(surface, variant, _frame):
    surface.fill((8, 22, 20))
    for i in range(7):
        x = (variant * 9 + i * 7) % 16
        y = (variant * 3 + i * 11) % 16
        pygame.draw.rect(surface, (12 + i % 2 * 8, 38 + i % 3 * 6, 31),
                         (x, y, 3, 3))
    pygame.draw.line(surface, (5, 15, 15), (0, 15), (15, 15))


def forest_path(surface, variant, _frame):
    surface.fill((51, 48, 37))
    _flecks(surface, variant, ((72, 66, 48), (37, 42, 34), (82, 57, 38)), 7)
    pygame.draw.line(surface, (29, 35, 30), (0, 15), (15, 15))


def cabin_roof(surface, variant, _frame):
    surface.fill((35, 48, 50))
    pygame.draw.line(surface, (65, 75, 70), (0, 0), (15, 0))
    pygame.draw.line(surface, (18, 29, 32), (0, 15), (15, 15))
    seam = (variant * 5 + 3) % 16
    pygame.draw.line(surface, (24, 36, 39), (seam, 0),
                     (max(0, seam - 5), 15))
    for i in range(3):
        x = (variant * 7 + i * 5) % 16
        surface.set_at((x, 2 + i), (47, 72, 46))


def cabin_wall(surface, variant, _frame):
    surface.fill((53, 73, 78))
    pygame.draw.line(surface, (76, 91, 91), (0, 0), (15, 0))
    pygame.draw.line(surface, (28, 43, 48), (0, 15), (15, 15))
    for x in range((variant * 3) % 5, 16, 5):
        pygame.draw.line(surface, (39, 58, 64), (x, 0), (x, 15))
    surface.set_at(((variant * 11 + 2) % 16, 9), (88, 80, 45))


def porch(surface, variant, _frame):
    surface.fill((78, 58, 42))
    for y in (3, 8, 13):
        pygame.draw.line(surface, (42, 33, 28), (0, y), (15, y))
    pygame.draw.line(surface, (111, 82, 55), (0, 0), (15, 0))
    surface.set_at(((variant * 7 + 3) % 16, 11), (40, 67, 44))


def porch_stair(surface, variant, _frame):
    surface.fill((43, 42, 34))
    for y in (2, 7, 12):
        pygame.draw.line(surface, (97, 70, 48), (1, y), (14, y))
        pygame.draw.line(surface, (35, 28, 25), (1, y + 2), (14, y + 2))
    if variant == 1:
        surface.set_at((13, 5), (46, 75, 45))


def dark_doorway(surface, variant, _frame):
    surface.fill((4, 7, 9))
    # One tile is only a piece of the 3x4 human-scale recess.  Keeping every
    # cell unframed lets adjoining pieces read as one open black doorway,
    # not as a grid of small windows.
    if variant:
        surface.set_at((14, 13), (8, 12, 14))


DRAW = {
    "forest_ground": forest_ground,
    "dense_forest": dense_forest,
    "forest_path": forest_path,
    "cabin_roof": cabin_roof,
    "cabin_wall": cabin_wall,
    "porch": porch,
    "porch_stair": porch_stair,
    "dark_doorway": dark_doorway,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface(
        (TAHUYA.cols * TILE_PX, TAHUYA.rows * TILE_PX), pygame.SRCALPHA
    )
    for row, (name, variants, frames) in enumerate(TAHUYA.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row * TILE_PX))
    output = ROOT / "assets" / "tilesets" / TAHUYA.sheet
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
