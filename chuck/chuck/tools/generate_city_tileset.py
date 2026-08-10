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


def roof(surface, variant, _frame):
    """Tar and gravel, seen from above.

    A roof is the single most common tile in the night city, so a flat
    fill of it reads as unpainted stone across half the screen. What
    stops that is texture at two scales: the big membrane panels a roof
    is actually built from, and the grit lying on top of them.
    """
    surface.fill((41, 44, 52))
    # The membrane seams: a panel grid, offset per variant so a block
    # never tiles into stripes.
    seam = (38, 41, 49)
    bright = (52, 55, 63)
    across = (variant * 5) % 16
    down = (variant * 7 + 3) % 16
    pygame.draw.line(surface, seam, (across, 0), (across, 15))
    pygame.draw.line(surface, bright, (across + 1, 0), (across + 1, 15))
    pygame.draw.line(surface, seam, (0, down), (15, down))
    pygame.draw.line(surface, bright, (0, down + 1), (15, down + 1))
    # Grit, and one puddle per few tiles catching what light there is.
    for index in range(7):
        x = (variant * 11 + index * 5) % 16
        y = (variant * 3 + index * 7) % 16
        surface.set_at((x, y), (49, 52, 60) if index % 2 else (35, 38, 46))
    if variant == 2:
        pygame.draw.ellipse(surface, (54, 60, 68), (4, 8, 8, 4))
        pygame.draw.ellipse(surface, (72, 80, 88), (5, 9, 4, 2))


def parapet(surface, variant, _frame):
    """The low wall around a roof, seen from just off vertical.

    This is what gives a block a top edge instead of ending at nothing:
    a lit cap, a shadowed inner face, and the roof carrying on below.
    """
    roof(surface, variant, 0)
    pygame.draw.rect(surface, (74, 77, 85), (0, 1, 16, 6))
    pygame.draw.line(surface, (118, 121, 126), (0, 1), (15, 1))
    pygame.draw.line(surface, (92, 95, 102), (0, 2), (15, 2))
    pygame.draw.line(surface, (24, 27, 34), (0, 7), (15, 7), 2)
    surface.set_at(((variant * 5 + 2) % 16, 4), (146, 148, 147))


def _parapet_side(surface, variant, mirrored: bool) -> None:
    """The same low wall, running down a roof's left or right edge.

    The back parapet is a horizontal cap; laid down a vertical edge it
    reads as rungs. A wall running away from the camera catches light on
    its outer face instead, so this is drawn as its own tile rather than
    reusing the horizontal one turned on its side.
    """
    roof(surface, variant, 0)
    pygame.draw.rect(surface, (74, 77, 85), (0, 0, 6, 16))
    pygame.draw.line(surface, (118, 121, 126), (0, 0), (0, 15))
    pygame.draw.line(surface, (92, 95, 102), (1, 0), (1, 15))
    pygame.draw.line(surface, (24, 27, 34), (6, 0), (6, 15), 2)
    surface.set_at((3, (variant * 5 + 2) % 16), (146, 148, 147))
    if mirrored:
        flipped = pygame.transform.flip(surface, True, False)
        surface.blit(flipped, (0, 0))


def parapet_left(surface, variant, _frame):
    """The parapet down a roof's left edge: lit face outward, to the left."""
    _parapet_side(surface, variant, mirrored=False)


def parapet_right(surface, variant, _frame):
    """...and down its right edge."""
    _parapet_side(surface, variant, mirrored=True)


def roof_vent(surface, variant, _frame):
    """A boxed air handler bolted to the roof, with its own shadow."""
    roof(surface, variant, 0)
    pygame.draw.rect(surface, (18, 20, 26), (4, 11, 11, 4))
    pygame.draw.rect(surface, (62, 65, 72), (2, 4, 11, 8))
    pygame.draw.rect(surface, (86, 89, 96), (2, 4, 11, 3))
    pygame.draw.line(surface, (110, 113, 118), (2, 4), (12, 4))
    for x in range(4, 12, 3):
        pygame.draw.line(surface, (40, 43, 50), (x, 8), (x, 11))


def skylight(surface, variant, _frame):
    """A run of dirty glass, lit faintly from the floor below."""
    roof(surface, variant, 0)
    pygame.draw.rect(surface, (20, 22, 28), (2, 12, 13, 3))
    pygame.draw.rect(surface, (74, 77, 84), (1, 3, 14, 10))
    pygame.draw.rect(surface, (58, 74, 84), (2, 4, 12, 8))
    for x in (5, 9):
        pygame.draw.line(surface, (74, 77, 84), (x, 4), (x, 11))
    pygame.draw.line(surface, (74, 77, 84), (2, 8), (13, 8))
    surface.set_at((3 + variant % 8, 5), (128, 146, 152))


def cornice(surface, variant, _frame):
    surface.fill((47, 50, 59))
    pygame.draw.rect(surface, (78, 80, 87), (0, 7, 16, 5))
    pygame.draw.line(surface, (112, 114, 118), (0, 7), (15, 7))
    pygame.draw.line(surface, (26, 29, 37), (0, 13), (15, 13), 2)
    surface.set_at(((variant * 5 + 2) % 16, 9), (137, 140, 139))


def facade(surface, variant, _frame):
    surface.fill((49, 52, 61))
    pygame.draw.line(surface, (72, 74, 82), (0, 0), (15, 0))
    pygame.draw.line(surface, (31, 34, 43), (0, 15), (15, 15))
    pygame.draw.line(surface, (38, 41, 49), (0, 7), (15, 7))
    x = 3 + (variant % 3) * 5
    pygame.draw.line(surface, (58, 60, 68), (x, 0), (x, 15))


def side_facade(surface, variant, _frame):
    """The wall that turns away from the camera.

    This is the face that makes the city three-quarter rather than flat,
    so it carries its own windows -- squeezed narrow and stepped down
    the tile, the way a receding wall foreshortens.
    """
    surface.fill((34, 37, 46))
    pygame.draw.line(surface, (57, 59, 67), (0, 0), (15, 0))
    pygame.draw.line(surface, (23, 26, 34), (0, 15), (15, 15))
    for y in (5, 11):
        pygame.draw.line(surface, (43, 46, 55), (0, y), (15, y + 2))
    pygame.draw.line(surface, (71, 73, 79),
                     (2 + variant % 2, 0), (2 + variant % 2, 15))
    # Two narrow panes, offset down the tile so the run of them reads as
    # a wall going away rather than a column of dots.
    for index, top in enumerate((1, 8)):
        left = 8 + ((variant + index) % 2) * 3
        lit = (variant + index) % 4 == 3
        pygame.draw.rect(surface, (22, 25, 33), (left - 1, top, 6, 6))
        pygame.draw.rect(
            surface, (150, 132, 74) if lit else (44, 74, 94),
            (left, top + 1, 4, 4))


def window(surface, variant, frame):
    facade(surface, variant, frame)
    pygame.draw.rect(surface, (25, 51, 68), (3, 2, 10, 11))
    pane = (67 + frame * 3, 101 + frame * 3, 119 + frame * 2)
    if variant == 3:
        pane = ((166, 145, 80), (180, 157, 88), (171, 151, 84))[frame]
    pygame.draw.rect(surface, pane, (4, 3, 8, 9))
    pygame.draw.line(surface, (27, 39, 52), (8, 3), (8, 11))
    pygame.draw.line(surface, (27, 39, 52), (4, 7), (12, 7))
    # A restrained moving rain glint gives the office face life without
    # making windows flash like signs.
    glint_x = 5 + (frame * 3 + variant) % 6
    surface.set_at((glint_x, 4), (132, 166, 178))


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


def crosswalk(surface, variant, frame):
    road(surface, variant, frame)
    paint = (174, 178, 176) if variant == 0 else (151, 156, 155)
    pygame.draw.rect(surface, paint, (2, 0, 11, 16))
    pygame.draw.line(surface, (112, 118, 118), (3, 0), (3, 15))
    # Small asphalt breaks keep the rain-worn markings from feeling pristine.
    for y in (4 + variant * 3, 12 - variant * 2):
        pygame.draw.rect(surface, (49, 54, 61), (9, y, 4, 2))


DRAW = {
    "city_roof": roof,
    "city_parapet": parapet,
    "city_parapet_left": parapet_left,
    "city_parapet_right": parapet_right,
    "city_roof_vent": roof_vent,
    "city_skylight": skylight,
    "city_cornice": cornice,
    "city_facade": facade,
    "city_side_facade": side_facade,
    "city_window": window,
    "city_sidewalk": sidewalk,
    "city_curb": curb,
    "city_road": road,
    "city_crosswalk": crosswalk,
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
