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
from generate_sewer_tileset import draw_astral_void

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
STREAM = (23, 68, 67)
STREAM_LIGHT = (47, 111, 101)
STREAM_DARK = (16, 47, 51)
TEMPLE = (73, 83, 65)
TEMPLE_LIGHT = (112, 119, 84)
TEMPLE_DARK = (45, 57, 49)
TEMPLE_MOSS = (39, 82, 48)
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
    """Tightly interlocked broad leaves instead of a brick-like green wall."""
    surface.fill(GROUND_DARK)
    clusters = (
        ((-3, -2, 10, 9), (6, -3, 12, 10), (1, 6, 12, 11), (10, 7, 9, 11)),
        ((-4, 3, 11, 10), (3, -4, 12, 11), (9, 1, 11, 12), (4, 9, 12, 9)),
        ((-2, -3, 12, 11), (8, -2, 10, 10), (-3, 8, 11, 10), (7, 7, 12, 12)),
        ((-4, -4, 11, 12), (5, -2, 13, 10), (0, 8, 11, 11), (10, 7, 9, 10)),
    )[variant]
    for index, rect in enumerate(clusters):
        color = CANOPY if index % 2 == 0 else CANOPY_LIGHT
        pygame.draw.ellipse(surface, color, rect)
        x, y, w, h = rect
        vein_start = (max(0, x + w // 2), max(0, y + h // 2))
        vein_end = (min(15, x + w - 1), min(15, y + h - 1))
        pygame.draw.line(surface, VINE, vein_start, vein_end, 1)
    highlights = (
        ((2, 3), (9, 1), (6, 11), (13, 9)),
        ((1, 8), (7, 2), (12, 5), (8, 13)),
        ((3, 2), (11, 3), (2, 12), (10, 10)),
        ((1, 2), (8, 3), (4, 12), (13, 11)),
    )[variant]
    for x, y in highlights:
        pygame.draw.rect(surface, LEAF, (x, y, 3, 2))
    # Dark woody seams and hanging vines keep adjacent tiles from reading as
    # one flat hedge while preserving a continuous impassable canopy.
    pygame.draw.line(surface, TRUNK, (variant * 4 % 13, 0),
                     ((variant * 4 + 3) % 16, 15), 2)
    vine_x = 2 + variant * 4
    pygame.draw.line(surface, VINE, (vine_x, 0), (max(0, vine_x - 2), 15), 1)


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


def draw_jungle_stream(surface, variant: int, frame: int) -> None:
    """Dark humid water with a restrained lateral pixel shimmer."""
    surface.fill(STREAM)
    offset = (frame * 2 + variant * 3) % 8
    pygame.draw.rect(surface, STREAM_DARK, (0, 0, 16, 2))
    pygame.draw.rect(surface, STREAM_DARK, (0, 14, 16, 2))
    for y, length in ((4, 6), (9, 5), (12, 3)):
        x = (offset + y + variant * 2) % 16
        pygame.draw.line(surface, STREAM_LIGHT, (x, y),
                         (min(15, x + length), y), 1)
        if x + length > 15:
            pygame.draw.line(surface, STREAM_LIGHT, (0, y),
                             ((x + length) - 16, y), 1)
    pygame.draw.line(surface, STREAM_DARK,
                     ((offset + 10) % 16, 6), ((offset + 14) % 16, 6), 1)


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


def draw_temple_stone(surface, variant: int, _frame: int) -> None:
    """Weathered blockwork with restrained moss and stepped edge shading."""
    surface.fill(TEMPLE)
    pygame.draw.line(surface, TEMPLE_DARK, (0, 7), (15, 7), 1)
    pygame.draw.line(surface, TEMPLE_DARK, (0, 15), (15, 15), 1)
    seam = (variant * 5 + 3) % 14
    pygame.draw.line(surface, TEMPLE_DARK, (seam, 0), (seam, 7), 1)
    pygame.draw.line(surface, TEMPLE_LIGHT, (1, 1), (14, 1), 1)
    if variant in (1, 3):
        pygame.draw.rect(surface, TEMPLE_MOSS, (variant, 3, 6, 2))
        pygame.draw.line(surface, TEMPLE_MOSS,
                         (variant + 2, 4), (variant + 1, 11), 1)
    if variant == 2:
        pygame.draw.line(surface, TEMPLE_DARK, (11, 8), (7, 13), 1)


def draw_temple_stairs(surface, variant: int, _frame: int) -> None:
    surface.fill(TEMPLE)
    for y in (3, 7, 11, 15):
        pygame.draw.line(surface, TEMPLE_DARK, (0, y), (15, y), 1)
        if y < 15:
            pygame.draw.line(surface, TEMPLE_LIGHT, (0, y + 1), (15, y + 1), 1)
    if variant:
        pygame.draw.rect(surface, TEMPLE_MOSS, (variant * 5, 12, 4, 2))


def draw_temple_entrance(surface, variant: int, _frame: int) -> None:
    surface.fill((10, 17, 17))
    pygame.draw.rect(surface, TEMPLE_DARK, (0, 0, 16, 3))
    pygame.draw.rect(surface, TEMPLE_DARK, (0, 0, 3, 16))
    pygame.draw.rect(surface, TEMPLE_DARK, (13, 0, 3, 16))
    pygame.draw.line(surface, TEMPLE_MOSS,
                     (2 + variant * 8, 0), (3 + variant * 7, 10), 1)


DRAW = {
    "jungle_ground": draw_ground,
    "dense_jungle": draw_dense_jungle,
    "fallen_log": draw_fallen_log,
    "thorn_patch": draw_thorn_patch,
    "jungle_stream": draw_jungle_stream,
    "jungle_trail": draw_jungle_trail,
    "jungle_exit": draw_jungle_exit,
    "temple_stone": draw_temple_stone,
    "temple_stairs": draw_temple_stairs,
    "temple_entrance": draw_temple_entrance,
    "astral_void": draw_astral_void,
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
