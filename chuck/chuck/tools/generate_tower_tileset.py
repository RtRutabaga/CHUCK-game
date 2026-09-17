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


# One bank of cloud, lit from the far side. The body is nearly flat and
# the rims carry all of the form: a field whose every tile draws its own
# billow reads as wallpaper printed with clouds, not as a cloud.
CLOUD_LIT = (252, 253, 255)
CLOUD_TOP = (238, 245, 251)
CLOUD_BODY = (219, 231, 243)
CLOUD_SHADE = (190, 209, 229)
CLOUD_DEEP = (162, 185, 212)
CLOUD_UNDER = (134, 162, 195)


CLOUD_SOFT = (205, 220, 236)
CLOUD_SOFT_LIT = (223, 234, 245)
CLOUD_SOFT_DIM = (180, 200, 222)


def _cloud_body(surface, variant, base, lit, dim) -> None:
    """The body of the platform: as near flat as pixel art gets.

    Two soft wisps a single step either side of the base colour, short
    and never in the same place twice. Anything stronger than this and
    the tile becomes a puff with a visible edge, and forty of those in a
    grid is what the platform is not supposed to look like.
    """
    surface.fill(base)
    light = (variant * 7 + 3) % 16
    dark = (variant * 11 + 9) % 16
    y_light = (variant * 5 + 2) % 15
    y_dark = (variant * 9 + 8) % 15
    pygame.draw.line(surface, lit,
                     (max(0, light - 5), y_light), (min(15, light + 5), y_light))
    if variant % 3:
        pygame.draw.line(surface, dim,
                         (max(0, dark - 4), y_dark), (min(15, dark + 4), y_dark))


def cloud(surface, variant, _frame):
    """The top of the bank, where it faces the light square on."""
    _cloud_body(surface, variant, CLOUD_BODY, CLOUD_TOP, CLOUD_SHADE)


def cloud_soft(surface, variant, _frame):
    """The same body a step down, in the band where the bank turns away.

    A field lit evenly corner to corner is a disc. One band of this
    inside the rim gives the platform a middle and a side, which is the
    difference between a cloud and a plate.
    """
    _cloud_body(surface, variant, CLOUD_SOFT, CLOUD_SOFT_LIT, CLOUD_SOFT_DIM)


def cloud_top(surface, variant, _frame):
    """The far edge, where the light lands: the bank's lit crest.

    The rim tiles paint sky in the part of themselves the cloud does not
    fill, and the boundary between the two bulges. Without that the
    platform's outline is the staircase of square tiles it is made of,
    and a cloud with a stepped outline is a floor tile that happens to
    be white.
    """
    surface.fill(SKY)
    pygame.draw.rect(surface, CLOUD_BODY, (0, 6, 16, 10))
    for index in range(2):
        x = (variant * 7 + index * 8) % 16 - 4
        pygame.draw.ellipse(surface, CLOUD_BODY, (x, 1, 12, 11))
        pygame.draw.ellipse(surface, CLOUD_LIT, (x + 1, 2, 10, 6))
    pygame.draw.rect(surface, CLOUD_TOP, (0, 8, 16, 3))


def cloud_base(surface, variant, _frame):
    """The near edge: the underside, turned away from the light.

    This is what tells you the platform has a thickness and that it
    stops here, so it is the darkest cloud on the map and it hangs in
    billows rather than ending on a straight lip.
    """
    surface.fill(SKY)
    pygame.draw.rect(surface, CLOUD_BODY, (0, 0, 16, 4))
    pygame.draw.rect(surface, CLOUD_SHADE, (0, 3, 16, 5))
    # One soft billow per tile with a slightly deeper core, overlapping
    # its neighbours. Two hard tones stacked read as cobbles hung under
    # the platform; vapour has no edge that sharp.
    for index in range(2):
        x = (variant * 5 + index * 9) % 16 - 5
        pygame.draw.ellipse(surface, CLOUD_SHADE, (x, 1, 15, 13))
        pygame.draw.ellipse(surface, CLOUD_DEEP, (x + 2, 6, 11, 7))


def _cloud_flank(surface, variant, west: bool) -> None:
    """A side rim: the bank turning away from the light, left or right."""
    surface.fill(SKY)
    inner = (4, 0, 12, 16) if west else (0, 0, 12, 16)
    shade = (4, 0, 6, 16) if west else (6, 0, 6, 16)
    pygame.draw.rect(surface, CLOUD_BODY, inner)
    pygame.draw.rect(surface, CLOUD_SHADE, shade)
    for index in range(2):
        y = (variant * 6 + index * 8) % 16 - 4
        x = -3 if west else 8
        pygame.draw.ellipse(surface, CLOUD_SHADE, (x, y, 12, 13))
        pygame.draw.ellipse(surface, CLOUD_DEEP,
                            (x + 1 if west else x + 3, y + 3, 8, 7))


def cloud_west(surface, variant, _frame):
    _cloud_flank(surface, variant, west=True)


def cloud_east(surface, variant, _frame):
    _cloud_flank(surface, variant, west=False)


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
    "tower_cloud_soft": cloud_soft,
    "tower_cloud_top": cloud_top,
    "tower_cloud_base": cloud_base,
    "tower_cloud_west": cloud_west,
    "tower_cloud_east": cloud_east,
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
