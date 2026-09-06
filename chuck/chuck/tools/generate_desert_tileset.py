"""Generate the Phase 13 Chult desert tileset.

The palette is lifted directly out of the arrival cutscene rather than
picked again by eye: the phase document asks for the playable desert to
match the desert Chuck was just standing in, and the only way to be
sure of that is to import the same constants the cutscene draws with.

Authored in one pass for the whole opening five-map region -- sand and
ripple and dune for the open ground, brown rock for the canyon walls,
ruin stone and floor for the scattered remains, dry scrub, and the
oasis's water, grass and palm shade -- so that later maps in the region
do not each churn the sheet.
"""

import math
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.scenes.desert_arrival_cutscene_scene import (
    _ROCK, _ROCK_DARK, _SAND, _SAND_LIT, _SAND_SHADE,
)
from src.world.tileset_layout import DESERT, TILE_PX
from generate_sewer_tileset import draw_astral_void

SAND = _SAND
SAND_LIT = _SAND_LIT
SAND_SHADE = _SAND_SHADE
ROCK = _ROCK
ROCK_DARK = _ROCK_DARK
ROCK_LIT = (186, 148, 108)
# Deeper than ROCK_DARK, for the bottom of a fissure. The face has
# to have somewhere genuinely dark in it or the fins have no depth.
ROCK_SHADE = (78, 58, 42)
# ...and a sun-bleached top edge, for the same reason at the other
# end: the reference's range is wide, and a narrow one reads as mud.
ROCK_PALE = (206, 172, 128)
# Two steps either side of ROCK, for the chunk faces themselves.
ROCK_MID_HI = (168, 132, 95)
ROCK_MID_LO = (130, 99, 70)
# The ruins are a greyer, older stone than the live rock of the cliffs:
# the desert made the canyon, somebody made these.
RUIN = (166, 142, 110)
RUIN_LIT = (192, 170, 136)
RUIN_DARK = (112, 92, 70)
SCRUB = (128, 128, 84)
SCRUB_LIT = (158, 158, 104)
SCRUB_DEAD = (150, 126, 88)
WATER = (58, 128, 138)
WATER_LIT = (96, 172, 174)
WATER_DARK = (34, 88, 104)
GRASS = (96, 130, 70)
GRASS_LIT = (128, 164, 88)
ASH = (128, 118, 108)
# Sand with a fire burnt onto it: still sand, still warm, much
# darker. Grey here and the camp's fires became puddles.
SCORCH = (170, 134, 88)
SCORCH_DARK = (126, 96, 62)
ASH_DARK = (88, 80, 74)
CHAR = (48, 42, 40)
# Darker than the turf it hangs over, or the shade disappears into the
# grass it is supposed to be shading.
PALM = (36, 68, 40)
PALM_LIT = (62, 104, 56)


def draw_sand(surface, variant: int, _frame: int) -> None:
    """Open sand. Almost nothing on it, because it is a desert.

    Four variants of two or three grains each: enough that a screenful
    does not tile visibly, few enough that the ground still reads as
    empty rather than as gravel.
    """
    surface.fill(SAND)
    grains = (
        ((3, 5), (10, 11)),
        ((7, 2), (13, 9)),
        ((1, 12), (8, 6), (14, 3)),
        ((5, 14), (11, 4)),
    )[variant]
    for index, (x, y) in enumerate(grains):
        surface.set_at((x, y), SAND_LIT if index % 2 else SAND_SHADE)


def draw_sand_ripple(surface, variant: int, _frame: int) -> None:
    """Wind-combed sand: the same ground with the weather written on it.

    The ripples run the same way in every variant. Wind does not change
    direction from tile to tile, and a field of these with the lines
    crossing each other reads as basketwork rather than as a desert.
    """
    surface.fill(SAND)
    for index in range(3):
        y = 2 + index * 5 + (variant % 2)
        start = (variant * 3 + index * 2) % 6
        pygame.draw.line(surface, SAND_LIT, (start, y), (start + 6, y))
        pygame.draw.line(surface, SAND_SHADE, (start, y + 1), (start + 6, y + 1))
        run = (start + 9) % 12
        pygame.draw.line(surface, SAND_SHADE, (run, y + 3), (run + 4, y + 3))


def draw_dune(surface, variant: int, _frame: int) -> None:
    """Sand lying in shadow: the low ground between the banks.

    This was drawn as an actual dune, with a lit crest and a shaded face
    above it. One tile of that looks right and a patch of them does not:
    every tile puts its shadow band at the same height, so a field of
    them reads as planks laid across the sand. A tiling texture cannot
    carry a feature that big -- so it carries the value instead, and the
    shape of the dune comes from where the patch is drawn on the map.
    """
    surface.fill(SAND_SHADE)
    for index in range(5):
        x = (index * 7 + variant * 3) % 14
        y = (index * 5 + variant * 4) % 14
        pygame.draw.rect(surface, SAND, (x, y, 3, 2))
    surface.set_at(((variant * 5 + 3) % 16, (variant * 7 + 2) % 16), SAND_LIT)


def draw_desert_rock(surface, variant: int, _frame: int) -> None:
    """Brown canyon rock, redrawn from a photograph of a sandstone face.

    Two things came out of the reference. The rock is broken into
    chunks that are taller than they are wide, and every surface of it
    is grained -- there is no flat area anywhere, which is exactly what
    the first version of this tile had too much of.

    The hard constraint is that a tile's variant is chosen from its
    position, so it changes from row to row: any feature drawn at a
    different x in different variants stops dead at every tile boundary.
    So there is exactly one thing here that is identical in all four --
    the deep fissure that enters the top edge at x=4 and leaves the
    bottom edge at the same place -- and that one runs unbroken down a
    whole cliff. Everything else is free to differ, and does.

    Drawn with a fissure every five pixels instead, which is what the
    reference looks like at its own scale, a wall of these came out as
    wickerwork: at sixteen pixels a fin has to be most of a tile wide
    or the eye reads the repetition before it reads the rock.
    """
    surface.fill(ROCK_DARK)
    # Chunks, taller than wide, tiled over the whole face with no gaps.
    # Deliberately uneven: no two the same height, and the joins between
    # them do not line up into courses.
    chunks = (
        ((0, 0, 5, 9), (5, 0, 6, 6), (11, 0, 5, 11),
         (0, 9, 4, 7), (4, 6, 7, 6), (4, 12, 7, 4), (11, 11, 5, 5)),
        ((0, 0, 6, 7), (6, 0, 4, 10), (10, 0, 6, 5),
         (0, 7, 6, 9), (6, 10, 4, 6), (10, 5, 6, 8), (10, 13, 6, 3)),
        ((0, 0, 4, 12), (4, 0, 7, 5), (11, 0, 5, 7),
         (4, 5, 7, 8), (11, 7, 5, 9), (0, 12, 4, 4), (4, 13, 7, 3)),
        ((0, 0, 7, 6), (7, 0, 4, 9), (11, 0, 5, 6),
         (0, 6, 7, 10), (7, 9, 4, 7), (11, 6, 5, 5), (11, 11, 5, 5)),
    )[variant]
    # Three near-neighbour values, not the whole palette. Drawn with the
    # full range the chunks read as crazy paving: at this size a strong
    # value step between two touching shapes is a *boundary*, and a face
    # with a boundary round every chunk is a mosaic, not a rock.
    faces = (ROCK, ROCK_MID_HI, ROCK, ROCK_MID_LO, ROCK_MID_HI, ROCK,
             ROCK_MID_LO)
    for index, (x, y, w, h) in enumerate(chunks):
        face = faces[(index + variant) % len(faces)]
        pygame.draw.rect(surface, face, (x, y, w, h))
        # Sun above and to the left, shadow below and to the right --
        # the same light the sand is lit by, so the two agree. Only some
        # chunks get either, or the edges themselves become the grid.
        # ...and never on the tile's own border. An edge drawn there is
        # an edge drawn along every seam in the sheet, and a cliff built
        # out of it comes back as a grid however good one tile looks.
        if (index + variant) % 3 != 2 and y > 0:
            pygame.draw.line(surface, ROCK_LIT, (x, y), (x + w - 2, y))
        if (index + variant * 2) % 3 != 1 and y + h < TILE_PX:
            pygame.draw.line(surface, ROCK_DARK,
                             (x, y + h - 1), (x + w - 1, y + h - 1))
        if (index + variant) % 4 == 0 and x + w < TILE_PX:
            pygame.draw.line(surface, ROCK_DARK,
                             (x + w - 1, y), (x + w - 1, y + h - 1))

    # Grain. A sandstone face has no flat area on it at any distance,
    # and this is most of what the reference has that the old tile did
    # not: every chunk speckled in both directions from its own value.
    # Always one step from whatever is already there, never a jump: a
    # speckle that ignores the surface it lands on reads as dirt on the
    # screen rather than as grain in the stone.
    lighter = {ROCK_SHADE: ROCK_DARK, ROCK_DARK: ROCK_MID_LO,
               ROCK_MID_LO: ROCK, ROCK: ROCK_MID_HI,
               ROCK_MID_HI: ROCK_LIT, ROCK_LIT: ROCK_PALE}
    darker = {value: key for key, value in lighter.items()}
    for step in range(26):
        gx = (step * 7 + variant * 5) % TILE_PX
        gy = (step * 11 + variant * 3) % TILE_PX
        pixel = surface.get_at((gx, gy))[:3]
        table = lighter if step % 2 else darker
        surface.set_at((gx, gy), table.get(pixel, pixel))

    # The one continuous feature: a fissure entering the top edge and
    # leaving the bottom edge at the same x in every variant, so it
    # chains from tile to tile down the whole height of a cliff. It
    # wanders in the middle, where it is free to.
    jog = (0, 1, 1, 0)[variant]
    # Its depth varies with the variant as well, so the line breathes
    # down the height of a cliff instead of being ruled.
    floor_colour = (ROCK_SHADE, ROCK_DARK, ROCK_SHADE, ROCK_DARK)[variant]
    for y in range(TILE_PX):
        x = 4 + (jog if 4 <= y <= 11 else 0)
        surface.set_at((x, y), floor_colour)
        if x + 1 < TILE_PX and y % 4 != variant % 4:
            surface.set_at((x + 1, y), ROCK_DARK)
        if x - 1 >= 0 and y % 5 == 0:
            surface.set_at((x - 1, y), ROCK_LIT)

    # ...and one short crack that does not, so the face is not a row of
    # identically fissured slabs. Kept as a plain stroke: given a shape
    # of its own it became a motif, and a motif is the one thing a
    # four-variant row cannot afford -- it repeats every fourth tile and
    # the eye finds it immediately.
    cx = (10, 13, 9, 12)[variant]
    top = (3, 8, 6, 1)[variant]
    for y in range(top, min(TILE_PX - 1, top + 6)):
        surface.set_at((cx, y), ROCK_DARK)


def draw_ruin_stone(surface, variant: int, _frame: int) -> None:
    """A standing block of whatever this used to be. Solid.

    Cut stone rather than rock: straight courses, square corners, and a
    broken top edge on two of the four so a wall of them does not run
    perfectly level.
    """
    surface.fill(RUIN)
    pygame.draw.rect(surface, RUIN_DARK, (0, 0, 16, 16), 1)
    for y in (5, 10):
        pygame.draw.line(surface, RUIN_DARK, (0, y), (15, y))
    seam = 4 + variant * 3
    pygame.draw.line(surface, RUIN_DARK, (seam, 0), (seam, 5))
    pygame.draw.line(surface, RUIN_DARK, ((seam + 7) % 16, 10),
                     ((seam + 7) % 16, 15))
    pygame.draw.line(surface, RUIN_LIT, (1, 1), (14, 1))
    if variant >= 2:
        # Weathered, but with shadow rather than with sand. Capping the
        # top courses in pale sand put a yellow block on every second
        # stone, and a wall of them came out as a checkerboard.
        for x in range(variant * 2, 16, 5):
            pygame.draw.rect(surface, RUIN_DARK, (x, 0, 3, 2))


def draw_ruin_floor(surface, variant: int, _frame: int) -> None:
    """Flagstones with the desert half over them again."""
    # Much sandier than the standing blocks above it, and drawn with
    # thin joints instead of thick ones. Given the same weight as
    # ruin_stone the floor and the wall were indistinguishable, and a
    # player has to be able to see at a glance what they can walk on.
    # Sand first, stone showing through it. Drawn the other way round --
    # a stone floor with sand drifted onto it -- the inside of every
    # ruin came out as a pale tiled room dropped into a desert.
    draw_sand(surface, variant, 0)
    # Every variant puts a joint on its top and left edge, so the joints
    # meet across tile boundaries and a field of them is one continuous
    # pavement. Placed at variant-dependent offsets instead, they came
    # out as loose dashes scattered over the sand -- the joints have to
    # line up or they stop reading as a floor at all.
    pygame.draw.line(surface, RUIN, (0, 0), (TILE_PX - 1, 0))
    pygame.draw.line(surface, RUIN, (0, 0), (0, TILE_PX - 1))
    pygame.draw.line(surface, RUIN_DARK, (0, 1), (TILE_PX - 1, 1))
    # One interior joint splits some of the flags in half, so the
    # pavement is not laid in one size.
    if variant % 2:
        pygame.draw.line(surface, RUIN, (8, 1), (8, TILE_PX - 1))
    else:
        pygame.draw.line(surface, RUIN, (1, 8), (TILE_PX - 1, 8))
    # ...and sand lying over a corner of it, which is what stops the
    # grid reading as freshly laid paving.
    drift = ((0, 10, 9, 6), (8, 0, 8, 7), (0, 0, 6, 6),
             (10, 9, 6, 7))[variant]
    pygame.draw.rect(surface, SAND, drift)
    surface.set_at((drift[0] + 1, drift[1] + 1), SAND_LIT)
    surface.set_at((drift[0] + drift[2] - 2, drift[1] + drift[3] - 2),
                   SAND_SHADE)


def draw_desert_scrub(surface, variant: int, _frame: int) -> None:
    """A dry bush on sand. Solid: it is chest-high on a one-foot rat."""
    draw_sand(surface, variant % 4, 0)
    stems = (
        ((8, 15), (4, 6), (12, 7)),
        ((7, 15), (3, 8), (13, 5)),
        ((9, 15), (5, 5), (11, 9)),
    )[variant]
    base = stems[0]
    for tip in stems[1:]:
        pygame.draw.line(surface, SCRUB_DEAD, base, tip)
        pygame.draw.line(surface, SCRUB, (base[0], base[1] - 3), tip)
    for index, (x, y) in enumerate(stems[1:]):
        pygame.draw.rect(surface, SCRUB_LIT if index else SCRUB, (x - 1, y - 1, 3, 3))
    pygame.draw.rect(surface, SCRUB, (base[0] - 2, base[1] - 4, 5, 4))


def draw_oasis_water(surface, variant: int, frame: int) -> None:
    """Standing water, the one cool thing in the region."""
    surface.fill(WATER)
    for index in range(4):
        y = index * 4 + ((frame + variant) % 3)
        if y >= TILE_PX:
            continue
        run = (index * 6 + frame * 3 + variant * 2) % 12
        pygame.draw.line(surface, WATER_LIT, (run, y), (run + 4, y))
        pygame.draw.line(surface, WATER_DARK, (run + 5, y), (run + 8, y))
    surface.set_at(((frame * 5 + variant * 3) % 16, (frame * 7) % 16), WATER_LIT)


def draw_oasis_grass(surface, variant: int, _frame: int) -> None:
    """Green, because there is water under it. Walkable."""
    surface.fill(GRASS)
    blades = (
        ((2, 13), (7, 15), (12, 12)),
        ((4, 15), (9, 12), (14, 14)),
        ((1, 14), (6, 11), (11, 15)),
        ((3, 12), (8, 14), (13, 11)),
    )[variant]
    for index, (x, y) in enumerate(blades):
        pygame.draw.line(surface, GRASS_LIT if index % 2 else PALM,
                         (x, y), (x + (1 if index % 2 else -1), y - 4))
    pygame.draw.rect(surface, SAND_SHADE, ((variant * 5) % 14, 0, 3, 2))


def draw_palm_canopy(surface, variant: int, _frame: int) -> None:
    """Palm shade, drawn over Chuck: he walks under the fronds."""
    surface.fill((0, 0, 0, 0))
    centre = (7 + variant, 7)
    # Five fronds, each drawn as two segments so it bends downward at
    # the halfway point. Struck as straight rays from a hub they read as
    # a green starburst; a palm frond is heavy and it droops.
    for index in range(5):
        angle = index * 1.257 + variant * 0.5
        reach = 8 if index % 2 else 6
        mid = (centre[0] + round(math.cos(angle) * reach * 0.55),
               centre[1] + round(math.sin(angle) * reach * 0.4))
        tip = (centre[0] + round(math.cos(angle) * reach),
               centre[1] + round(math.sin(angle) * reach * 0.7) + 3)
        pygame.draw.line(surface, PALM, centre, mid, 3)
        pygame.draw.line(surface, PALM, mid, tip, 2)
        pygame.draw.line(surface, PALM_LIT, centre, mid, 1)
    pygame.draw.circle(surface, PALM, centre, 2)


def draw_camp_scorch(surface, variant: int, _frame: int) -> None:
    """Ground a fire has been burning on. Walkable.

    This row used to be the fire itself: stones, ash and embers, all
    inside one sixteen-pixel square, which meant the stones were three
    pixels across and the whole thing read as a pot. The ring is a prop
    now, and what is left here is the mark it made on the sand -- so a
    camp fire covers a patch of ground rather than a tile of it.

    Sand first and burn over it, the same way round as the ruin floor
    and for the same reason: drawn as ash with sand scattered on it,
    every fire in the camp came out as a grey disc laid on a desert.
    """
    draw_sand(surface, variant, 0)
    # Mostly burnt, with the burn running off every edge of the tile.
    # Drawn as a handful of small blobs sitting inside the tile it came
    # back as scattered charcoal -- gravel rather than ground -- because
    # every tile was making its own little island instead of joining the
    # ones beside it. The patch is several tiles across and no single
    # tile may have an edge of its own.
    for index in range(4):
        x = (index * 7 + variant * 5) % TILE_PX - 4
        y = (index * 11 + variant * 3) % TILE_PX - 4
        pygame.draw.ellipse(surface, SCORCH, (x, y, 11, 9))
    for index in range(2):
        x = (index * 9 + variant * 6) % TILE_PX - 2
        y = (index * 5 + variant * 7) % TILE_PX - 2
        pygame.draw.ellipse(surface, SCORCH_DARK, (x, y, 7, 5))
    # Ash and cinders lying on it. Two tones, because a burn with one
    # value on it is a shadow.
    for index in range(6):
        x = (index * 6 + variant * 7) % TILE_PX
        y = (index * 9 + variant * 4) % TILE_PX
        surface.set_at((x, y), ASH if index % 2 else CHAR)
        if index % 3 == 0:
            surface.set_at(((x + 1) % TILE_PX, y), ASH_DARK)


DRAW = {
    "sand": draw_sand,
    "sand_ripple": draw_sand_ripple,
    "dune": draw_dune,
    "desert_rock": draw_desert_rock,
    "ruin_stone": draw_ruin_stone,
    "ruin_floor": draw_ruin_floor,
    "desert_scrub": draw_desert_scrub,
    "camp_scorch": draw_camp_scorch,
    "oasis_water": draw_oasis_water,
    "oasis_grass": draw_oasis_grass,
    "palm_canopy": draw_palm_canopy,
    "astral_void": draw_astral_void,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((DESERT.cols * TILE_PX, DESERT.rows * TILE_PX),
                           pygame.SRCALPHA)
    for row_i, (name, variants, frames) in enumerate(DESERT.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / DESERT.sheet
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
