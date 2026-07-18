"""Generate the Phase 6 jungle-temple interior tileset."""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import TEMPLE, TILE_PX
from generate_sewer_tileset import draw_astral_void

FLOOR = (65, 70, 57)
FLOOR_LIGHT = (86, 87, 65)
FLOOR_DARK = (43, 52, 47)
STONE = (48, 59, 51)
STONE_LIGHT = (76, 81, 61)
STONE_DARK = (27, 38, 37)
MOSS = (35, 72, 43)
GLYPH = (108, 100, 62)
PIT = (10, 17, 17)
SPIKE = (148, 145, 111)
SPIKE_DARK = (79, 83, 70)
WOOD = (74, 48, 31)
FLAME_DARK = (180, 68, 24)
FLAME = (239, 145, 45)
FLAME_LIGHT = (255, 224, 105)


def draw_floor(surface, variant: int, _frame: int) -> None:
    surface.fill(FLOOR)
    pygame.draw.line(surface, FLOOR_DARK, (0, 15), (15, 15), 1)
    seam = (variant * 5 + 3) % 14
    pygame.draw.line(surface, FLOOR_DARK, (seam, 0), (seam, 7), 1)
    pygame.draw.line(surface, FLOOR_LIGHT, (1, 1), (14, 1), 1)
    cracks = (
        ((3, 10), (6, 8), (8, 11)),
        ((11, 4), (8, 7), (10, 9)),
        ((2, 5), (5, 7), (4, 11)),
        ((13, 12), (10, 10), (8, 13)),
    )[variant]
    pygame.draw.lines(surface, FLOOR_DARK, False, cracks, 1)


def draw_wall(surface, variant: int, _frame: int) -> None:
    surface.fill(STONE)
    pygame.draw.rect(surface, STONE_DARK, (0, 13, 16, 3))
    pygame.draw.line(surface, STONE_LIGHT, (0, 1), (15, 1), 1)
    pygame.draw.line(surface, STONE_DARK, (0, 7), (15, 7), 1)
    seam = 4 + variant * 3
    pygame.draw.line(surface, STONE_DARK, (seam, 0), (seam, 7), 1)
    pygame.draw.line(surface, MOSS, (variant, 3), (min(15, variant + 6), 3), 2)
    if variant == 2:
        # Restrained eye/serpent glyph: environmental texture, not exposition.
        pygame.draw.line(surface, GLYPH, (5, 10), (8, 8), 1)
        pygame.draw.line(surface, GLYPH, (8, 8), (11, 10), 1)
        pygame.draw.line(surface, GLYPH, (11, 10), (8, 12), 1)
        pygame.draw.line(surface, GLYPH, (8, 12), (5, 10), 1)
        surface.set_at((8, 10), GLYPH)


def draw_doorway(surface, variant: int, _frame: int) -> None:
    """Continuous darkness beneath the spanning human-scale arch prop."""
    surface.fill((8, 14, 14))
    # A sparse floor-edge fracture avoids a flat placeholder look without
    # recreating the repeated vertical bars the arch system replaces.
    if variant:
        pygame.draw.line(surface, STONE_DARK, (1, 14), (6, 12), 1)


def draw_spikes(surface, variant: int, _frame: int) -> None:
    """A deep black groove with large, immediately readable stone spikes."""
    surface.fill(PIT)
    pygame.draw.rect(surface, STONE_DARK, (0, 0, 16, 3))
    pygame.draw.line(surface, STONE_LIGHT, (0, 0), (15, 0), 1)
    pygame.draw.rect(surface, STONE_DARK, (0, 13, 16, 3))
    offsets = ((1, 7, 12), (0, 6, 11), (2, 8, 13))[variant]
    for x in offsets:
        pygame.draw.polygon(surface, SPIKE_DARK,
                            ((x - 2, 13), (x, 5 + variant % 2), (x + 2, 13)))
        pygame.draw.line(surface, SPIKE, (x, 6 + variant % 2), (x, 11), 1)


def draw_torch(surface, variant: int, frame: int) -> None:
    """Wall masonry with a compact two-frame brazier flame."""
    draw_wall(surface, variant, frame)
    pygame.draw.rect(surface, WOOD, (7, 7, 2, 7))
    pygame.draw.line(surface, STONE_DARK, (5, 13), (10, 13), 1)
    if frame == 0:
        pygame.draw.polygon(surface, FLAME_DARK,
                            ((5, 8), (8, 2), (11, 8), (8, 10)))
        pygame.draw.polygon(surface, FLAME,
                            ((6, 8), (8, 4), (10, 8), (8, 9)))
    else:
        pygame.draw.polygon(surface, FLAME_DARK,
                            ((6, 8), (9, 1), (11, 7), (8, 10)))
        pygame.draw.polygon(surface, FLAME,
                            ((7, 8), (9, 3), (10, 7), (8, 9)))
    surface.set_at((8, 7), FLAME_LIGHT)


def draw_brazier(surface, variant: int, frame: int) -> None:
    """A freestanding pedestal brazier on the floor — the facade's
    ceremonial fire, flickering on the same two-frame cadence as the
    wall torches."""
    draw_floor(surface, variant, frame)
    # Stepped stone pedestal with a shallow bowl.
    pygame.draw.rect(surface, STONE_DARK, (4, 14, 8, 2))
    pygame.draw.rect(surface, STONE, (5, 10, 6, 4))
    pygame.draw.rect(surface, STONE_LIGHT, (4, 9, 8, 2))
    pygame.draw.rect(surface, STONE_DARK, (3, 8, 10, 1))
    surface.set_at((5, 11), GLYPH)  # a worn gold fleck on the stem
    if frame == 0:
        pygame.draw.polygon(surface, FLAME_DARK,
                            ((4, 8), (8, 1), (12, 8)))
        pygame.draw.polygon(surface, FLAME,
                            ((6, 8), (8, 3), (10, 8)))
    else:
        pygame.draw.polygon(surface, FLAME_DARK,
                            ((5, 8), (9, 0), (12, 7)))
        pygame.draw.polygon(surface, FLAME,
                            ((6, 8), (9, 2), (10, 7)))
    surface.set_at((8, 6), FLAME_LIGHT)


def draw_dart_wall(surface, variant: int, frame: int) -> None:
    """Masonry launcher aperture; marker orientation supplies direction."""
    draw_wall(surface, variant, frame)
    pygame.draw.rect(surface, STONE_DARK, (4, 5, 8, 7))
    pygame.draw.rect(surface, PIT, (6, 7, 4, 4))
    pygame.draw.line(surface, STONE_LIGHT, (5, 5), (10, 5), 1)


DRAW = {
    "temple_floor": draw_floor,
    "temple_wall": draw_wall,
    "temple_doorway": draw_doorway,
    "temple_spikes": draw_spikes,
    "temple_torch": draw_torch,
    "temple_dart_wall": draw_dart_wall,
    "astral_void": draw_astral_void,
    "temple_brazier": draw_brazier,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((TEMPLE.cols * TILE_PX, TEMPLE.rows * TILE_PX),
                           pygame.SRCALPHA)
    for row_i, (name, variants, frames) in enumerate(TEMPLE.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / TEMPLE.sheet
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
