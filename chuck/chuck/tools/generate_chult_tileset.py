"""Generate the first playable Chult jungle tileset."""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import CHULT, TILE_PX

GROUND = (37, 44, 28)
GROUND_LIGHT = (65, 69, 38)
GROUND_DARK = (27, 35, 25)
CANOPY = (17, 54, 34)
CANOPY_LIGHT = (25, 70, 40)
LEAF = (43, 102, 53)
VINE = (37, 83, 48)
TRUNK = (31, 55, 35)
LOG_BARK = (54, 57, 35)
LOG_LIGHT = (78, 73, 42)
LOG_DARK = (25, 34, 25)
THORN = (66, 111, 47)
THORN_LIGHT = (129, 143, 70)
TRAIL = (47, 46, 29)
TRAIL_LIGHT = (68, 62, 35)
TRAIL_DARK = (30, 35, 24)


def draw_ground(surface, variant: int, _frame: int) -> None:
    surface.fill(GROUND)
    marks = (
        ((2, 4), (9, 12), (13, 6)),
        ((4, 13), (11, 3), (14, 10)),
        ((1, 9), (7, 5), (12, 14)),
        ((3, 2), (8, 11), (15, 7)),
    )[variant]
    for index, (x, y) in enumerate(marks):
        color = GROUND_LIGHT if index == 0 else GROUND_DARK
        pygame.draw.rect(surface, color, (x, y, 3, 2))
    pygame.draw.line(surface, TRUNK, (6 + variant, 15), (9 + variant, 11), 2)


def draw_dense_jungle(surface, variant: int, _frame: int) -> None:
    surface.fill(CANOPY)
    pygame.draw.rect(surface, TRUNK, (variant * 3 % 12, 0, 5, 16))
    for index, (x, y) in enumerate(((1, 2), (8, 1), (4, 8), (11, 10))):
        dx = (x + variant * 2) % 14
        color = CANOPY_LIGHT if index % 2 else LEAF
        pygame.draw.rect(surface, color, (dx, y, 6, 4))
    vine_x = 3 + variant * 4
    pygame.draw.line(surface, VINE, (vine_x, 0), (vine_x - 2, 15), 2)
    pygame.draw.line(surface, GROUND_DARK, (0, 15), (15, 15))


def draw_fallen_log(surface, variant: int, _frame: int) -> None:
    """Human-scale trunk overhead; Chuck's feet remain visible beneath."""
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, LOG_DARK, (0, 2, 16, 12))
    pygame.draw.rect(surface, LOG_BARK, (0, 1, 16, 10))
    pygame.draw.line(surface, LOG_LIGHT, (0, 2 + variant % 2),
                     (15, 2 + variant % 2), 2)
    pygame.draw.line(surface, TRUNK, (3 + variant * 2, 5),
                     (6 + variant * 2, 9), 2)
    pygame.draw.rect(surface, LOG_DARK, (0, 11, 16, 3))


def draw_thorn_patch(surface, variant: int, _frame: int) -> None:
    draw_ground(surface, variant, 0)
    stems = (
        ((2, 14, 5, 5), (8, 15, 10, 4), (13, 14, 12, 7)),
        ((1, 13, 4, 4), (7, 15, 8, 5), (14, 13, 11, 6)),
        ((3, 15, 2, 6), (9, 14, 12, 4), (15, 15, 13, 8)),
    )[variant]
    for base_x, base_y, tip_x, tip_y in stems:
        pygame.draw.line(surface, THORN, (base_x, base_y), (tip_x, tip_y), 2)
        pygame.draw.line(surface, THORN_LIGHT, (tip_x, tip_y),
                         (tip_x + (1 if tip_x < base_x else -1), tip_y + 2), 1)


def draw_jungle_trail(surface, variant: int, _frame: int) -> None:
    """A restrained worn track that remains part of the humid ground."""
    surface.fill(TRAIL)
    marks = (
        ((2, 5), (10, 12), (14, 3)),
        ((4, 13), (8, 4), (13, 9)),
        ((1, 9), (7, 14), (12, 5)),
    )[variant]
    for index, (x, y) in enumerate(marks):
        color = TRAIL_LIGHT if index == 0 else TRAIL_DARK
        pygame.draw.rect(surface, color, (x, y, 3, 2))
    pygame.draw.line(surface, GROUND_DARK, (0, 15), (15, 15))


def draw_jungle_exit(surface, variant: int, _frame: int) -> None:
    """Dense canopy arch over the stable northward handoff boundary."""
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, CANOPY, (0, 0, 16, 5))
    pygame.draw.rect(surface, CANOPY, (0, 0, 3, 16))
    pygame.draw.rect(surface, CANOPY, (13, 0, 3, 16))
    pygame.draw.rect(surface, LEAF, ((variant * 5) % 10, 1, 7, 4))
    pygame.draw.rect(surface, CANOPY_LIGHT, (10 - variant * 2, 4, 6, 3))
    pygame.draw.line(surface, VINE, (2 + variant, 0), (4 + variant, 12), 1)
    pygame.draw.line(surface, VINE, (14 - variant, 0), (12 - variant, 10), 1)


DRAW = {
    "jungle_ground": draw_ground,
    "dense_jungle": draw_dense_jungle,
    "fallen_log": draw_fallen_log,
    "thorn_patch": draw_thorn_patch,
    "jungle_trail": draw_jungle_trail,
    "jungle_exit": draw_jungle_exit,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((CHULT.cols * TILE_PX, CHULT.rows * TILE_PX),
                           pygame.SRCALPHA)
    for row_i, (name, variants, frames) in enumerate(CHULT.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / CHULT.sheet
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
