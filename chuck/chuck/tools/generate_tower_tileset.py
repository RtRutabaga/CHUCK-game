"""Generate the pale stone and moving sky of Zephyros' tower."""

import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import TILE_PX, TOWER


SKY = (91, 156, 210)
SKY_DARK = (68, 132, 190)
CLOUD = (208, 224, 235)
CLOUD_LIGHT = (239, 241, 236)
STONE = (174, 180, 192)
STONE_DARK = (109, 116, 137)
STONE_LIGHT = (220, 218, 207)
GOLD = (205, 169, 76)


def sky(surface, variant, frame):
    surface.fill(SKY)
    drift = (frame * 4 + variant * 7) % 22 - 6
    y = 3 + (variant * 5) % 10
    pygame.draw.ellipse(surface, CLOUD, (drift, y, 15, 6))
    pygame.draw.ellipse(surface, CLOUD_LIGHT, (drift + 5, y - 2, 12, 7))
    pygame.draw.line(surface, SKY_DARK, (0, 15), (15, 15))


def stone(surface, variant, _frame):
    surface.fill(STONE)
    pygame.draw.line(surface, STONE_LIGHT, (0, 0), (15, 0))
    pygame.draw.line(surface, STONE_DARK, (0, 15), (15, 15))
    offset = (variant * 5 + 3) % 14
    pygame.draw.line(surface, STONE_DARK,
                     (offset, 5), (min(15, offset + 4), 5))
    surface.set_at(((variant * 7 + 2) % 15, 10), GOLD)


def edge(surface, variant, _frame):
    surface.fill(STONE_DARK)
    pygame.draw.rect(surface, STONE, (1, 0, 14, 11))
    pygame.draw.line(surface, STONE_LIGHT, (1, 0), (14, 0))
    pygame.draw.line(surface, (63, 72, 101), (0, 12), (15, 15), 3)
    if variant % 2:
        pygame.draw.line(surface, GOLD, (4, 4), (11, 4))


CLOUD_TOP = (247, 250, 253)
CLOUD_BODY = (206, 221, 238)
CLOUD_SHADE = (176, 198, 222)
CLOUD_DEEP = (128, 158, 194)


def cloud(surface, variant, _frame):
    """Standing cloud: the platform outside the tower.

    No lit top edge and no shaded base -- those are what make masonry
    read as courses, and drawn on every tile of a field they would band
    the whole platform. Billows offset by variant instead, so the floor
    reads as one mass of cloud rather than a grid of cells.
    """
    surface.fill(CLOUD_BODY)
    # Eight variants rather than four, each a differently sized billow in
    # a different place: with fewer, the neighbouring tiles line their
    # puffs up and the bank reads as wallpaper.
    high = (variant * 5 + variant * variant * 3) % 16
    drop = (variant * 7) % 6
    wide = 11 + (variant % 3) * 3
    pygame.draw.ellipse(surface, CLOUD_TOP,
                        (high - 5, drop - 1, wide, 8 + variant % 3))
    pygame.draw.ellipse(surface, CLOUD_SHADE,
                        ((high + 9) % 16 - 4, (drop + 9) % 13, 8, 4))


def cloud_edge(surface, variant, _frame):
    """The rim, where the cloud stops and the drop begins.

    The top half is the same bank as the floor behind it; the bottom is
    its underside, turned away from the light. That, rather than a lip,
    is what tells Chuck where the platform ends.
    """
    surface.fill(CLOUD_BODY)
    pygame.draw.ellipse(surface, CLOUD_TOP, ((variant * 7) % 12 - 3, 0, 12, 7))
    pygame.draw.rect(surface, CLOUD_SHADE, (0, 8, 16, 8))
    pygame.draw.ellipse(surface, CLOUD_DEEP, (-3, 9, 12, 7))
    pygame.draw.ellipse(surface, CLOUD_DEEP, (6, 10, 13, 6))
    if variant % 2:
        pygame.draw.ellipse(surface, CLOUD_SHADE, (2, 10, 9, 4))


def interior(surface, variant, _frame):
    """Unlit depth inside the tower's central shaft."""
    surface.fill((7, 8, 14))
    # Sparse, subdued masonry catches far below give the black area depth
    # without making it look like animated sky or a traversable floor.
    if variant % 2:
        pygame.draw.line(surface, (16, 17, 27), (0, 14), (15, 12))
    surface.set_at(((variant * 5 + 3) % 16, 5 + variant * 2), (24, 22, 31))


DRAW = {
    "tower_sky": sky,
    "tower_stone": stone,
    "tower_edge": edge,
    "tower_interior": interior,
    "tower_cloud": cloud,
    "tower_cloud_edge": cloud_edge,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface(
        (TOWER.cols * TILE_PX, TOWER.rows * TILE_PX), pygame.SRCALPHA
    )
    for row, (name, variants, frames) in enumerate(TOWER.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row * TILE_PX))
    output = ROOT / "assets" / "tilesets" / TOWER.sheet
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
