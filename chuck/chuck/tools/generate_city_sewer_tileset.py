"""Generate the modern concrete utility-sewer tileset."""

import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import math

import pygame

from generate_sewer_tileset import draw_astral_void
from src.world.tileset_layout import CITY_SEWER, TILE_PX


def wall(surface, variant, _frame):
    surface.fill((54, 61, 64))
    pygame.draw.line(surface, (78, 85, 87), (0, 0), (15, 0))
    pygame.draw.line(surface, (35, 41, 44), (0, 15), (15, 15), 2)
    seam = 5 + variant * 4
    pygame.draw.line(surface, (43, 49, 52), (seam, 0), (seam, 15))
    pygame.draw.rect(surface, (91, 87, 69),
                     ((variant * 5 + 2) % 13, 7, 2, 2))


def brick(surface, variant, _frame):
    surface.fill((69, 65, 63))
    for y in range(0, 16, 5):
        pygame.draw.line(surface, (37, 40, 41), (0, y + 4), (15, y + 4))
        offset = 4 if (y // 5 + variant) % 2 else 0
        for x in range(offset, 16, 8):
            pygame.draw.line(surface, (42, 43, 43), (x, y), (x, y + 4))
    pygame.draw.line(surface, (91, 83, 78), (0, 0), (15, 0))


def pipe_wall(surface, variant, _frame):
    wall(surface, variant, 0)
    y = 4 + variant * 3
    pygame.draw.rect(surface, (39, 44, 46), (0, y + 2, 16, 5))
    pygame.draw.rect(surface, (91, 101, 102), (0, y, 16, 5))
    pygame.draw.line(surface, (133, 140, 138), (0, y), (15, y))
    for x in (3, 12):
        pygame.draw.rect(surface, (52, 58, 60), (x, y - 1, 2, 7))


def utility_light(surface, variant, frame):
    wall(surface, variant, frame)
    glow = (174, 162, 102) if frame == 0 else (197, 181, 111)
    pygame.draw.rect(surface, (31, 36, 38), (2, 3, 12, 7))
    pygame.draw.rect(surface, glow, (4, 4, 8, 4))
    pygame.draw.line(surface, (210, 204, 156), (5, 4), (10, 4))


def floor(surface, variant, _frame):
    surface.fill((67, 73, 74))
    pygame.draw.line(surface, (46, 51, 53), (0, 15), (15, 15))
    pygame.draw.line(surface, (82, 88, 88), (0, 0), (15, 0))
    x = (variant * 5 + 3) % 15
    y = (variant * 7 + 5) % 14
    surface.set_at((x, y), (107, 106, 94))
    surface.set_at(((x + 7) % 16, (y + 3) % 16), (42, 49, 50))


def walkway(surface, variant, _frame):
    floor(surface, variant, 0)
    pygame.draw.line(surface, (105, 109, 107), (0, 7), (15, 7))
    pygame.draw.line(surface, (39, 44, 46), (0, 8), (15, 8))
    pygame.draw.line(surface, (48, 53, 54),
                     (4 + variant * 4, 0), (4 + variant * 4, 15))


def wet(surface, variant, frame):
    floor(surface, variant, frame)
    pygame.draw.rect(surface, (44, 57, 58), (1, 8, 14, 6))
    x = (variant * 5 + frame * 4) % 12 + 1
    pygame.draw.line(surface, (80, 103, 102), (x, 10), (min(15, x + 5), 10))


def warning(surface, variant, _frame):
    floor(surface, variant, 0)
    for x in range(-12, 20, 8):
        pygame.draw.line(surface, (181, 142, 48),
                         (x, 15), (x + 14, 1), 3)
    pygame.draw.line(surface, (51, 48, 39), (0, 0), (15, 0), 2)


def channel(surface, variant, frame):
    surface.fill((31, 46, 46))
    pygame.draw.line(surface, (17, 28, 30), (0, 0), (15, 0), 2)
    pygame.draw.line(surface, (17, 28, 30), (0, 15), (15, 15), 2)
    phase = variant * 3 + frame * 4
    for y in (4, 8, 12):
        for x in range(16):
            if (x + y + phase) % 7 < 2:
                surface.set_at((x, y), (58, 77, 73))


def sludge(surface, variant, frame):
    """Toxic runoff. Deliberately a colour nothing else in the sewer uses,
    so it can never be mistaken for the channel or a safe wet patch."""
    surface.fill((44, 74, 22))
    phase = variant * 2 + frame * 3
    for y in range(16):
        amount = 0.5 + 0.4 * math.sin(y * 0.7 + phase)
        colour = tuple(
            round(a + (b - a) * amount)
            for a, b in zip((44, 74, 22), (126, 196, 44))
        )
        pygame.draw.line(surface, colour, (0, y), (15, y))
    # Slow bubbles surfacing and popping between frames.
    for index in range(3):
        x = (variant * 5 + index * 6 + frame * 2) % 16
        y = (variant * 3 + index * 7 + frame * 4) % 16
        pygame.draw.circle(surface, (196, 236, 118), (x, y), 1)
    surface.set_at(((phase * 3) % 16, (phase * 5 + 4) % 16), (226, 250, 168))


def ladder_top(surface, variant, frame):
    """The head of the maintenance ladder, and the daylight above it."""
    wall(surface, variant, frame)
    pygame.draw.rect(surface, (88, 96, 104), (3, 0, 3, 16))
    pygame.draw.rect(surface, (88, 96, 104), (10, 0, 3, 16))
    for y in range(1, 16, 4):
        pygame.draw.rect(surface, (146, 154, 160), (3, y, 10, 2))
    # A hatch open on grey daylight: the only light in the sewer that is
    # not a utility lamp, so the way out reads before it is reached.
    pygame.draw.rect(surface, (150, 162, 170), (5, 0, 6, 3))
    pygame.draw.rect(surface, (196, 206, 210), (6, 0, 4, 2))


def ladder_bottom(surface, variant, frame):
    """Its foot, where Chuck stands to look up."""
    floor(surface, variant, frame)
    pygame.draw.rect(surface, (72, 80, 88), (3, 0, 3, 14))
    pygame.draw.rect(surface, (72, 80, 88), (10, 0, 3, 14))
    for y in range(1, 14, 4):
        pygame.draw.rect(surface, (124, 132, 140), (3, y, 10, 2))
    pygame.draw.rect(surface, (46, 52, 56), (2, 14, 12, 2))


DRAW = {
    "city_sewer_wall": wall,
    "city_sewer_brick": brick,
    "city_sewer_pipe_wall": pipe_wall,
    "city_sewer_light": utility_light,
    "city_sewer_floor": floor,
    "city_sewer_walkway": walkway,
    "city_sewer_wet": wet,
    "city_sewer_warning": warning,
    "city_sewer_channel": channel,
    "city_sewer_sludge": sludge,
    "city_sewer_ladder_top": ladder_top,
    "city_sewer_ladder_bottom": ladder_bottom,
    "astral_void": draw_astral_void,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface(
        (CITY_SEWER.cols * TILE_PX, CITY_SEWER.rows * TILE_PX),
        pygame.SRCALPHA,
    )
    for row, (name, variants, frames) in enumerate(CITY_SEWER.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row * TILE_PX))
    output = ROOT / "assets" / "tilesets" / CITY_SEWER.sheet
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({sheet.get_width()}x{sheet.get_height()})")
    pygame.quit()


if __name__ == "__main__":
    main()
