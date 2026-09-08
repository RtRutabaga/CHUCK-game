"""Generate the first playable Feywild terrain sheet."""

import math
import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import FEYWILD, TILE_PX


GROUND = (20, 55, 52)
GROUND_DARK = (13, 41, 42)
GROUND_LIGHT = (39, 86, 63)
LEAF_DARK = (12, 56, 47)
LEAF = (34, 120, 72)
LEAF_LIGHT = (79, 183, 99)
VIOLET = (184, 78, 235)
PINK = (238, 101, 184)
BLUE = (68, 184, 245)
GOLD = (239, 205, 80)
WATER_DEEP = (9, 45, 76)
WATER = (18, 114, 140)
WATER_LIGHT = (79, 220, 201)
BANK = (35, 85, 61)
BANK_DARK = (22, 63, 52)
PATH = (45, 76, 59)
PATH_LIGHT = (68, 105, 72)
ROOT_DARK = (42, 31, 34)
ROOT_BROWN = (82, 55, 45)
ROOT_LIGHT = (125, 83, 55)
# Redcap Warrens: giant toadstools, pale and cold beside the warm roots.
CAP_SHADOW = (58, 40, 62)
CAP = (146, 92, 122)
CAP_LIGHT = (206, 158, 178)
STALK = (198, 190, 168)
# Mushroom Underways: canopy shade underfoot, and still luminous pools.
SHADE_DARK = (10, 26, 30)
SHADE = (18, 40, 44)
SHADE_LIGHT = (32, 62, 62)
POOL_DEEP = (16, 62, 96)
POOL = (52, 158, 186)
POOL_LIGHT = (140, 240, 226)
# Luminous Rapids: fast bright water, wet stones, and giant flower pads.
RAPID_DEEP = (22, 78, 118)
RAPID = (86, 190, 214)
FOAM = (222, 250, 248)
STONE_DARK = (52, 58, 62)
STONE = (104, 112, 116)
STONE_LIGHT = (156, 164, 164)
PAD_DARK = (22, 78, 52)
PAD = (58, 138, 74)
PAD_LIGHT = (104, 190, 104)
PAD_SUNK = (34, 96, 108)
PAD_SUNK_LIGHT = (58, 130, 132)
DIRT_DARK = (44, 38, 32)
DIRT = (66, 57, 45)
DIRT_LIGHT = (92, 80, 60)
TABLE_DARK = (68, 43, 47)
TABLE = (119, 75, 65)
TABLE_LIGHT = (170, 111, 78)
TEA = (72, 118, 102)


def ground(surface, variant: int, _frame: int) -> None:
    surface.fill(GROUND)
    for index in range(4):
        x = (variant * 5 + index * 7 + 2) % 16
        y = (variant * 3 + index * 5 + 4) % 16
        color = GROUND_LIGHT if index == 0 else GROUND_DARK
        pygame.draw.rect(surface, color, (x, y, 2, 2))
    glow = (VIOLET, BLUE, PINK, GOLD)[variant]
    surface.set_at(((variant * 4 + 3) % 15, (variant * 6 + 8) % 15), glow)


def dense(surface, variant: int, _frame: int) -> None:
    surface.fill(GROUND_DARK)
    clusters = (
        ((-4, -3, 12, 11), (5, -3, 13, 10), (0, 7, 12, 11), (9, 7, 10, 11)),
        ((-3, 3, 12, 11), (3, -4, 13, 12), (10, 0, 10, 12), (5, 9, 12, 9)),
        ((-3, -3, 13, 11), (8, -2, 11, 11), (-2, 8, 11, 10), (7, 7, 13, 12)),
        ((-4, -4, 12, 13), (5, -2, 13, 11), (0, 9, 12, 10), (10, 6, 9, 11)),
    )[variant]
    for index, rect in enumerate(clusters):
        pygame.draw.ellipse(
            surface,
            LEAF_DARK if index == 0 else LEAF,
            rect,
        )
        x, y, width, height = rect
        pygame.draw.line(
            surface, LEAF_LIGHT,
            (max(0, x + width // 2), max(0, y + height // 2)),
            (min(15, x + width - 2), min(15, y + height - 2)),
        )
    pygame.draw.rect(
        surface, (VIOLET, BLUE, PINK, GOLD)[variant],
        ((variant * 5 + 2) % 14, (variant * 3 + 5) % 14, 2, 2),
    )


def river(surface, variant: int, frame: int) -> None:
    surface.fill(WATER_DEEP)
    phase = frame * 3 + variant * 2
    for y in range(16):
        amount = 0.35 + 0.25 * math.sin(y * 0.6 + phase)
        color = tuple(
            round(a + (b - a) * amount)
            for a, b in zip(WATER_DEEP, WATER)
        )
        pygame.draw.line(surface, color, (0, y), (15, y))
    for index, y in enumerate((3, 8, 13)):
        x = (phase + index * 7) % 16
        pygame.draw.line(
            surface, WATER_LIGHT, (x, y), (min(15, x + 6), y)
        )


def bank(surface, variant: int, _frame: int) -> None:
    surface.fill(BANK)
    pygame.draw.line(surface, BANK_DARK, (0, 0), (0, 15), 2)
    for index in range(4):
        x = (variant * 5 + index * 4 + 2) % 15
        y = (variant * 3 + index * 6 + 1) % 15
        pygame.draw.ellipse(
            surface,
            LEAF if index % 2 else LEAF_LIGHT,
            (x - 2, y - 1, 5, 3),
        )


def path(surface, variant: int, _frame: int) -> None:
    surface.fill(PATH)
    pygame.draw.line(surface, GROUND_DARK, (0, 15), (15, 15))
    for index in range(3):
        x = (variant * 4 + index * 6 + 1) % 15
        y = (variant * 7 + index * 5 + 3) % 15
        pygame.draw.rect(
            surface, PATH_LIGHT if index == 0 else GROUND_LIGHT,
            (x, y, 3, 2),
        )


def pollen(surface, variant: int, frame: int) -> None:
    """Low luminous flowers and drifting spores over readable ground."""
    surface.fill((49, 78, 54))
    pygame.draw.rect(surface, (61, 91, 58), (0, 12, 16, 4))
    petals = (GOLD, PINK, BLUE)
    for index in range(4):
        x = (variant * 5 + index * 4 + 1) % 15
        y = 9 + ((variant + index * 2) % 5)
        color = petals[(variant + index) % len(petals)]
        pygame.draw.line(surface, LEAF_LIGHT, (x, 15), (x, y + 1))
        surface.set_at((x, y), color)
        if x + 1 < 16:
            surface.set_at((x + 1, y + 1), color)
    # Three small motes rise and drift between animation frames. Their
    # stagger keeps adjacent tiles from resolving into a uniform grid.
    for index, color in enumerate((GOLD, PINK, BLUE)):
        x = (variant * 7 + index * 6 + frame * (index + 1)) % 16
        y = 8 - ((frame * 2 + index * 3 + variant) % 7)
        surface.set_at((x, y), color)


def opening(surface, variant: int, side: str) -> None:
    """A dense vegetation arch framing one cardinal wilderness handoff."""
    surface.fill((0, 0, 0, 0))
    throat = {
        "w": (0, 3, 13, 10),
        "e": (3, 3, 13, 10),
        "n": (3, 0, 10, 13),
        "s": (3, 3, 10, 13),
    }[side]
    # The dark recess is the readable negative space; it is surrounded by
    # leaves rather than masonry so it remains a wilderness trail opening.
    pygame.draw.rect(surface, GROUND_DARK, throat)
    pygame.draw.rect(surface, (8, 29, 31), throat, 1)
    bands = {
        "w": ((0, 0, 5, 16), (0, 0, 16, 4), (0, 12, 16, 4)),
        "e": ((11, 0, 5, 16), (0, 0, 16, 4), (0, 12, 16, 4)),
        "n": ((0, 0, 16, 5), (0, 0, 4, 16), (12, 0, 4, 16)),
        "s": ((0, 11, 16, 5), (0, 0, 4, 16), (12, 0, 4, 16)),
    }[side]
    for index, rect in enumerate(bands):
        pygame.draw.rect(surface, LEAF_DARK if index == 0 else LEAF, rect)
    accents = (VIOLET, BLUE, PINK)
    if side in {"w", "e"}:
        edge_x = 2 if side == "w" else 13
        pygame.draw.line(surface, LEAF_LIGHT, (edge_x, 1), (edge_x, 14), 2)
        pygame.draw.line(
            surface, accents[variant], (edge_x, 3 + variant),
            (8 if side == "w" else 7, 5 + variant), 1,
        )
        pygame.draw.line(
            surface, accents[(variant + 1) % 3], (edge_x, 12 - variant),
            (7 if side == "w" else 8, 10 - variant), 1,
        )
    else:
        edge_y = 2 if side == "n" else 13
        pygame.draw.line(surface, LEAF_LIGHT, (1, edge_y), (14, edge_y), 2)
        pygame.draw.line(
            surface, accents[variant], (3 + variant, edge_y),
            (5 + variant, 8 if side == "n" else 7), 1,
        )
        pygame.draw.line(
            surface, accents[(variant + 1) % 3], (12 - variant, edge_y),
            (10 - variant, 7 if side == "n" else 8), 1,
        )


def opening_w(surface, variant: int, _frame: int) -> None:
    opening(surface, variant, "w")


def opening_e(surface, variant: int, _frame: int) -> None:
    opening(surface, variant, "e")


def opening_n(surface, variant: int, _frame: int) -> None:
    opening(surface, variant, "n")


def opening_s(surface, variant: int, _frame: int) -> None:
    opening(surface, variant, "s")


def root_wall(surface, variant: int, _frame: int) -> None:
    """Tangled roots dense enough to read as a continuous solid barrier."""
    surface.fill(ROOT_DARK)
    offsets = (0, 3, 6, 9)
    for index, offset in enumerate(offsets):
        y = (offset + variant * 2) % 13
        color = ROOT_BROWN if index % 2 else ROOT_LIGHT
        pygame.draw.line(surface, color, (-2, y), (17, y + 7), 3)
        pygame.draw.line(surface, ROOT_DARK, (-2, y + 2), (17, y + 9), 1)
    pygame.draw.line(surface, LEAF, (variant * 3, 0), (15, 12), 1)
    surface.set_at(((variant * 5 + 3) % 16, (variant * 7 + 5) % 16),
                   (VIOLET, BLUE, PINK, GOLD)[variant])


def root_passage(surface, variant: int, _frame: int) -> None:
    """A low arch drawn over Chuck while leaving the path visible beneath."""
    surface.fill((0, 0, 0, 0))
    pygame.draw.line(surface, ROOT_DARK, (0, 2), (15, 2 + variant), 7)
    pygame.draw.line(surface, ROOT_BROWN, (0, 1), (15, 1 + variant), 4)
    pygame.draw.line(surface, ROOT_LIGHT, (0, 0), (15, variant), 1)
    pygame.draw.line(surface, ROOT_DARK, (1, 0), (1, 8), 3)
    pygame.draw.line(surface, ROOT_DARK, (14, 2), (14, 9), 3)
    pygame.draw.line(surface, LEAF, (2, 1), (8 + variant, 4), 1)


def camp_dirt(surface, variant: int, _frame: int) -> None:
    """Packed earth the redcaps have trampled bare.

    Deliberately free of the path tile's edge line: this fills wide areas,
    and any directional mark would band into stripes across the camp.
    """
    surface.fill(DIRT)
    for index in range(6):
        x = (variant * 5 + index * 7 + 1) % 15
        y = (variant * 11 + index * 5 + 2) % 15
        surface.fill(DIRT_DARK if index % 2 else DIRT_LIGHT, (x, y, 2, 1))
    for index in range(2):                 # trodden scraps of the old turf
        x = (variant * 3 + index * 9 + 4) % 14
        y = (variant * 7 + index * 6 + 6) % 14
        surface.set_at((x, y), LEAF_DARK)


def rapids(surface, variant: int, frame: int) -> None:
    """Fast bright water: the Luminous Rapids' impassable middle."""
    surface.fill(RAPID_DEEP)
    for y in range(16):
        amount = 0.45 + 0.35 * math.sin(y * 0.8 + frame * 2.2 + variant)
        colour = tuple(round(a + (b - a) * amount)
                       for a, b in zip(RAPID_DEEP, RAPID))
        pygame.draw.line(surface, colour, (0, y), (15, y))
    # Broken crests, scattered rather than ruled, so a wide river does
    # not resolve into horizontal bands.
    for index in range(4):
        x = (variant * 5 + index * 6 + frame * 4) % 16
        y = (variant * 7 + index * 4 + frame) % 16
        pygame.draw.line(surface, FOAM, (x, y), (min(15, x + 3), y))
    surface.set_at(((variant * 9 + frame * 3) % 16,
                    (variant * 5 + 9) % 16), (240, 254, 250))


def stepping_stone(surface, variant: int, _frame: int) -> None:
    """A static safe stone: wet, blunt, and obviously standable."""
    surface.fill(RAPID_DEEP)
    pygame.draw.ellipse(surface, STONE_DARK, (0, 1, 16, 15))
    pygame.draw.ellipse(surface, STONE, (1, 2, 14, 12))
    pygame.draw.ellipse(surface, STONE_LIGHT, (3 + variant, 4, 7, 4))
    for index in range(2):
        x = (variant * 5 + index * 7 + 3) % 12
        y = (variant * 3 + index * 5 + 7) % 12
        surface.set_at((x, y), STONE_DARK)


def pad_open(surface, variant: int, _frame: int) -> None:
    """A giant flower pad, risen and broad enough to stand on."""
    surface.fill(RAPID_DEEP)
    pygame.draw.ellipse(surface, PAD_DARK, (0, 0, 16, 16))
    pygame.draw.ellipse(surface, PAD, (1, 1, 14, 14))
    pygame.draw.ellipse(surface, PAD_LIGHT, (4, 3, 8, 6))
    # The notch every lily pad has, turned by variant so a chain of pads
    # never looks stamped.
    notch = ((7, 0), (0, 7), (7, 14))[variant % 3]
    pygame.draw.line(surface, RAPID_DEEP, (8, 8), notch, 2)
    surface.set_at((8, 8), GOLD)


def pad_closed(surface, variant: int, _frame: int) -> None:
    """The same pad furled under the water: visibly there, visibly not
    yet safe, so a broken chain can be read before it is jumped."""
    surface.fill(RAPID_DEEP)
    pygame.draw.ellipse(surface, PAD_SUNK, (2, 4, 12, 10))
    pygame.draw.ellipse(surface, PAD_SUNK_LIGHT, (4, 6, 8, 5))
    pygame.draw.line(surface, PAD_SUNK_LIGHT, (3, 9 + variant % 2),
                     (12, 9 + variant % 2))
    for index in range(2):
        x = (variant * 6 + index * 7 + 2) % 15
        pygame.draw.line(surface, FOAM, (x, 2), (x + 2, 2))


def cap_shade(surface, variant: int, frame: int) -> None:
    """The floor beneath a giant cap: dark, gilled, quietly alive.

    Tiles seamlessly in long runs, because the Underways are meant to be
    walked under a canopy for a while rather than through a doorway.
    """
    surface.fill(SHADE)
    # Gill shadows fall on the ground in broken strokes. They are kept
    # short deliberately: a full-width line would band into stripes the
    # moment the shade covers more than a few tiles.
    for index in range(4):
        x = (variant * 5 + index * 7) % 13
        y = (variant * 3 + index * 5 + 1) % 15
        length = 3 + ((variant + index) % 3)
        pygame.draw.line(surface, SHADE_DARK, (x, y), (x + length, y + 1))
    x = (variant * 7 + 2) % 12
    y = (variant * 11 + 6) % 14
    pygame.draw.line(surface, SHADE_LIGHT, (x, y), (x + 3, y))
    # Spores drifting in the dark, turning over between frames.
    for index, colour in enumerate((BLUE, VIOLET, GOLD)):
        x = (variant * 6 + index * 5 + frame * 2) % 16
        y = (variant * 4 + index * 7 + frame * 3) % 16
        surface.set_at((x, y), colour)


def glow_pool(surface, variant: int, frame: int) -> None:
    """A still luminous pool. Solid: something to walk around and admire."""
    surface.fill(POOL_DEEP)
    for y in range(16):
        amount = 0.4 + 0.3 * math.sin(y * 0.5 + frame * 2 + variant)
        colour = tuple(round(a + (b - a) * amount)
                       for a, b in zip(POOL_DEEP, POOL))
        pygame.draw.line(surface, colour, (0, y), (15, y))
    for index in range(2):
        x = (variant * 5 + index * 8 + frame * 3) % 16
        y = (variant * 3 + index * 9 + 2) % 15
        pygame.draw.line(surface, POOL_LIGHT, (x, y), (min(15, x + 4), y))
    surface.set_at(((variant * 7 + frame * 5) % 16,
                    (variant * 9 + 6) % 16), (236, 252, 246))


def mushroom_thicket(surface, variant: int, _frame: int) -> None:
    """Fused toadstool stalks: a solid wall of caps at redcap height."""
    surface.fill(CAP_SHADOW)
    for index in range(3):
        x = (index * 6 + variant * 2) % 14
        # Stagger the caps hard vertically: at four variants a shallow
        # offset still resolves into visible rows across a whole thicket.
        top = 1 + ((index * 5 + variant * 3) % 8)
        pygame.draw.rect(surface, STALK, (x + 1, top + 4, 4, 12))
        pygame.draw.ellipse(surface, CAP, (x - 1, top, 9, 7))
        pygame.draw.ellipse(surface, CAP_LIGHT, (x + 1, top + 1, 5, 3))
        surface.set_at((x + 3, top + 4), CAP_SHADOW)
    pygame.draw.line(surface, LEAF_DARK, (0, 15), (15, 15))


def mushroom_passage(surface, variant: int, _frame: int) -> None:
    """A cap arching overhead: the gap beneath is Chuck's alone.

    Drawn like the root passage so the two read as the same promise --
    a way through that a gnome-sized redcap simply cannot follow.
    """
    surface.fill((0, 0, 0, 0))
    pygame.draw.ellipse(surface, CAP_SHADOW, (-4, -5, 24, 11))
    pygame.draw.ellipse(surface, CAP, (-3, -6, 22, 10))
    pygame.draw.ellipse(surface, CAP_LIGHT, (2 + variant, -4, 8, 3))
    for x in (1, 13):                      # the stalks framing the gap
        pygame.draw.rect(surface, STALK, (x, 2, 2, 7))
        pygame.draw.line(surface, CAP_SHADOW, (x, 3), (x, 8))
    surface.set_at((6 + variant, 1), GOLD)  # a spore catching the light


def tabletop(surface, variant: int, _frame: int) -> None:
    """Warm impossible-scale boards for the abandoned Fey tea table."""
    surface.fill(TABLE)
    pygame.draw.line(surface, TABLE_DARK, (0, 15), (15, 15))
    pygame.draw.line(surface, TABLE_LIGHT, (0, 1), (15, 1))
    for index in range(2):
        x = (variant * 7 + index * 9 + 2) % 15
        y = (variant * 3 + index * 7 + 5) % 14
        length = 3 + ((variant + index) % 3)
        pygame.draw.line(
            surface, TABLE_LIGHT,
            (x, y), (min(15, x + length), y),
        )
        if index == 1:
            pygame.draw.line(
                surface, TABLE_DARK,
                (max(0, x - 2), y + 2), (min(15, x + 2), y + 2),
            )


def table_shadow(surface, variant: int, _frame: int) -> None:
    """Cool under-table ground: clearly traversable, visibly sheltered."""
    surface.fill((11, 34, 37))
    for index in range(4):
        x = (variant * 5 + index * 4 + 1) % 16
        y = (variant * 7 + index * 5 + 2) % 16
        pygame.draw.rect(surface, (19, 52, 48), (x, y, 2, 2))
    pygame.draw.line(surface, (39, 72, 55), (0, 15), (15, 15))


def table_apron(surface, variant: int, _frame: int) -> None:
    """Heavy table lip overhead; Chuck remains visible beneath the lower half."""
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, TABLE_DARK, (0, 0, 16, 6))
    pygame.draw.rect(surface, TABLE, (0, 0, 16, 4))
    pygame.draw.line(surface, TABLE_LIGHT, (0, 0), (15, 0))
    pygame.draw.rect(surface, TABLE_DARK, (variant * 5, 5, 5, 2))
    pygame.draw.line(surface, (43, 104, 69),
                     (2 + variant * 4, 1), (4 + variant * 4, 9))


def _table_apron_rail(surface, variant: int, outer: int) -> None:
    """One tile of the table's lip seen along its western or eastern edge.

    The lip is a beam, and a beam has a direction. Drawn with the north
    and south art -- a band across the top of the tile -- a run of it
    down the side of the table came out as eight loose planks with a gap
    between each one, which is what a ladder looks like and not what the
    edge of a table looks like.

    ``outer`` is the x of the table's outside face: 0 on the west edge
    and 15 on the east. Everything else is measured inward from there,
    so the two runs mirror each other and together outline the table's
    real footprint rather than floating somewhere inside it.
    """
    surface.fill((0, 0, 0, 0))
    step = 1 if outer == 0 else -1
    near = 0 if outer == 0 else 10
    # Six pixels of beam with the last two in shadow, which is the
    # horizontal lip turned on its side: the light edge is the one
    # facing out of the table and the dark one is where it overhangs.
    pygame.draw.rect(surface, TABLE_DARK, (near, 0, 6, 16))
    pygame.draw.rect(surface, TABLE, (outer if step > 0 else outer - 3,
                                      0, 4, 16))
    pygame.draw.line(surface, TABLE_LIGHT, (outer, 0), (outer, 15))
    # The same knot and trailing vine as the horizontal lip, hanging
    # inward under the table so the four sides read as one piece of
    # furniture rather than four.
    knot = outer + step * 2
    pygame.draw.rect(surface, TABLE_DARK,
                     (min(knot, knot + step), variant * 5, 2, 5))
    pygame.draw.line(surface, (43, 104, 69),
                     (outer + step, 2 + variant * 4),
                     (outer + step * 9, 4 + variant * 4))


def table_apron_w(surface, variant: int, _frame: int) -> None:
    """The table's west lip: the beam runs down the tile, not across it."""
    _table_apron_rail(surface, variant, 0)


def table_apron_e(surface, variant: int, _frame: int) -> None:
    """The table's east lip, mirrored so its light edge faces outward."""
    _table_apron_rail(surface, variant, 15)


def tea_spill(surface, variant: int, _frame: int) -> None:
    tabletop(surface, variant, 0)
    points = (
        ((1, 5), (11, 3), (15, 8), (12, 14), (3, 13)),
        ((0, 8), (5, 2), (13, 4), (15, 12), (8, 15), (2, 13)),
        ((3, 2), (14, 5), (13, 13), (6, 15), (0, 10)),
    )[variant]
    pygame.draw.polygon(surface, (48, 91, 82), points)
    pygame.draw.lines(surface, TEA, True, points, 1)
    surface.set_at(((variant * 5 + 5) % 14, 7 + variant), (111, 180, 143))


def needle_bed(surface, variant: int, _frame: int) -> None:
    """Dense flowering foliage used to frame the orchid firing lanes."""
    surface.fill(GROUND_DARK)
    for index in range(7):
        x = (variant * 5 + index * 7 + 1) % 16
        y = (variant * 9 + index * 5 + 2) % 16
        color = (LEAF_LIGHT if index % 3 == 0 else LEAF)
        pygame.draw.line(
            surface, color, (x, min(15, y + 3)), (x, max(0, y - 2)), 1
        )
        if index % 2:
            pygame.draw.line(
                surface, color,
                (x, y), (max(0, x - 2), max(0, y - 2)), 1,
            )
        bloom = (
            (211, 92, 191) if (index + variant) % 2
            else (234, 174, 103)
        )
        pygame.draw.rect(
            surface, bloom, ((x - 1) % 16, max(0, y - 3), 2, 2)
        )
    pygame.draw.line(surface, GROUND_LIGHT, (0, 15), (15, 15), 1)


def channel(surface, variant: int, frame: int) -> None:
    """A narrow fen channel: shallower and brighter than the deep river,
    with reed-lit banks so a one-tile hop reads as obviously crossable."""
    river(surface, variant, frame)
    # Lighter shallows: the bed shows through where Chuck can clear it.
    phase = frame * 3 + variant * 2
    for y in range(3, 13):
        amount = 0.55 + 0.3 * math.sin(y * 0.5 + phase)
        color = tuple(
            round(a + (b - a) * amount)
            for a, b in zip(WATER, WATER_LIGHT)
        )
        pygame.draw.line(surface, color, (2, y), (13, y))
    # Reeds leaning in from both banks mark it as the narrow crossing.
    for x, top in ((1, 4), (14, 6), (3, 11), (12, 2)):
        pygame.draw.line(surface, GROUND_LIGHT, (x, top), (x, top + 3))
    pygame.draw.line(surface, WATER_DEEP, (0, 0), (15, 0))
    pygame.draw.line(surface, WATER_DEEP, (0, 15), (15, 15))


DRAW = {
    "fey_ground": ground,
    "fey_channel": channel,
    "fey_dense": dense,
    "fey_river": river,
    "fey_bank": bank,
    "fey_path": path,
    "fey_pollen": pollen,
    "fey_opening_w": opening_w,
    "fey_opening_e": opening_e,
    "fey_opening_n": opening_n,
    "fey_opening_s": opening_s,
    "fey_root_wall": root_wall,
    "fey_root_passage": root_passage,
    "fey_camp_dirt": camp_dirt,
    "fey_rapids": rapids,
    "fey_stepping_stone": stepping_stone,
    "fey_pad_open": pad_open,
    "fey_pad_closed": pad_closed,
    "fey_cap_shade": cap_shade,
    "fey_glow_pool": glow_pool,
    "fey_mushroom_thicket": mushroom_thicket,
    "fey_mushroom_passage": mushroom_passage,
    "fey_tabletop": tabletop,
    "fey_table_shadow": table_shadow,
    "fey_table_apron": table_apron,
    "fey_table_apron_w": table_apron_w,
    "fey_table_apron_e": table_apron_e,
    "fey_tea_spill": tea_spill,
    "fey_needle_bed": needle_bed,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface(
        (FEYWILD.cols * TILE_PX, FEYWILD.rows * TILE_PX),
        pygame.SRCALPHA,
    )
    for row_index, (name, variants, frames) in enumerate(FEYWILD.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(
                    cell,
                    ((variant * frames + frame) * TILE_PX, row_index * TILE_PX),
                )
    output = ROOT / "assets" / "tilesets" / FEYWILD.sheet
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
