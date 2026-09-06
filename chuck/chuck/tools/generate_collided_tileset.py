"""Generate the Phase 13 collided-world tileset.

Everything east of the hub draws with this sheet rather than the
opening region's. It is the desert plus whatever has fallen into it,
and it grows as the traversal does: this first pass carries the desert
materials and one intrusion, and later maps add rows without touching
the maps already built on it.

Every row is *imported* rather than redrawn. A fragment of the modern
city has to be the modern city -- the same rain-dark asphalt, the same
worn lane paint -- or the player does not recognise what they are
looking at, and a lookalike drawn from memory drifts a shade at a time
until it is simply a grey road. So the desert rows come from the desert
generator and the city rows come from the city generator, and neither
can quietly diverge from the place it belongs to.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import COLLIDED, TILE_PX
from generate_sewer_tileset import draw_astral_void
from generate_desert_tileset import (
    draw_desert_rock, draw_desert_scrub, draw_dune, draw_ruin_floor,
    draw_ruin_stone, draw_sand, draw_sand_ripple,
)
from generate_city_tileset import road as draw_city_road
from generate_city_tileset import road_line_h as draw_city_road_line
from generate_chult_tileset import (
    draw_dense_jungle, draw_ground as draw_jungle_ground, draw_jungle_stream,
)
from generate_feywild_tileset import (
    dense as draw_fey_dense, glow_pool as draw_fey_glow_pool,
    ground as draw_fey_ground, pollen as draw_fey_pollen,
)
from generate_phlegethos_tileset import draw_basalt, draw_cliff, draw_lava
from generate_ship_tileset import draw_ship_floor


# ---------------------------------------------------------------------
# The one world with no home.
#
# Everything else on this sheet is imported from the generator that owns
# it. Chuck has never been to a castle, so there is nothing to import --
# these two are drawn here, and the provenance suite records them as
# belonging to this sheet. There is no second copy for them to drift
# away from, which is the only reason that is safe.
#
# Deliberately not the docks sheet's castle. That one is Waterdeep's own
# backdrop and the phase document asks for somewhere distinct: this is
# cold grey ashlar with moss in the joints, not warm keep stone.
# ---------------------------------------------------------------------
COURTYARD = (128, 126, 122)
COURTYARD_LIT = (156, 154, 148)
COURTYARD_DARK = (86, 86, 88)
WALL = (92, 92, 96)
WALL_LIT = (122, 122, 126)
WALL_DARK = (58, 58, 62)
MOSS = (74, 96, 68)


def draw_courtyard_stone(surface, variant: int, _frame: int) -> None:
    """Cut flagstones, laid square and swept.

    The desert's ruin floor is sand with stone showing through it. This
    is the opposite and has to read that way at a glance: a floor that
    somebody is still keeping.
    """
    surface.fill(COURTYARD)
    # Joints on the top and left edges, so a field of them is one
    # continuous pavement -- the same trick the ruin floor uses.
    pygame.draw.line(surface, COURTYARD_DARK, (0, 0), (TILE_PX - 1, 0))
    pygame.draw.line(surface, COURTYARD_DARK, (0, 0), (0, TILE_PX - 1))
    pygame.draw.line(surface, COURTYARD_LIT, (1, 1), (TILE_PX - 1, 1))
    # One flag split in half, alternating direction, so the paving is
    # not laid in a single size.
    if variant % 2:
        pygame.draw.line(surface, COURTYARD_DARK, (8, 1), (8, TILE_PX - 1))
    else:
        pygame.draw.line(surface, COURTYARD_DARK, (1, 8), (TILE_PX - 1, 8))
    # A little moss in the joints, and a chip or two.
    surface.set_at((1 + variant * 3, 1), MOSS)
    surface.set_at((TILE_PX - 2, 9 + (variant % 4)), MOSS)
    surface.set_at((4 + (variant * 5) % 9, 11 - (variant % 3)), COURTYARD_DARK)


def draw_courtyard_wall(surface, variant: int, _frame: int) -> None:
    """Ashlar: big squared blocks in even courses, mossed at the joints.

    Coursed rather than broken, because that is the whole difference
    between a castle and a ruin -- the desert already has three kinds of
    fallen-down stone in it and this must not read as a fourth.
    """
    surface.fill(WALL_DARK)
    for index, top in enumerate((0, 6, 11)):
        height = 5 if index < 2 else 5
        # Courses offset by half a block, the way real ashlar is laid.
        offset = 0 if index % 2 == 0 else 5
        for x in range(-offset, TILE_PX, 9):
            pygame.draw.rect(surface, WALL, (x, top, 8, height - 1))
            pygame.draw.line(surface, WALL_LIT, (x, top), (x + 7, top))
    for spot in ((1, 5), (10, 10), (6, 15)):
        surface.set_at(((spot[0] + variant * 3) % TILE_PX, spot[1]), MOSS)


DRAW = {
    "sand": draw_sand,
    "sand_ripple": draw_sand_ripple,
    "dune": draw_dune,
    "desert_rock": draw_desert_rock,
    "ruin_stone": draw_ruin_stone,
    "ruin_floor": draw_ruin_floor,
    "desert_scrub": draw_desert_scrub,
    # The first intrusion: a piece of the rained-on city, unchanged.
    "city_road": draw_city_road,
    "city_road_line_h": draw_city_road_line,
    # ...and the second: the jungle Chuck crossed to get to any of this.
    "jungle_ground": draw_jungle_ground,
    "dense_jungle": draw_dense_jungle,
    "jungle_stream": draw_jungle_stream,
    # ...the Feywild, which is the only thing in the desert with a
    # colour of its own rather than a shade of one.
    "fey_ground": draw_fey_ground,
    "fey_dense": draw_fey_dense,
    "fey_pollen": draw_fey_pollen,
    "fey_glow_pool": draw_fey_glow_pool,
    # ...and the Nine Hells, which bring the first fragment that is
    # dangerous to stand on rather than merely strange to look at.
    "basalt": draw_basalt,
    "cliff": draw_cliff,
    "lava": draw_lava,
    # ...the ship, which is a deck and nothing else out here.
    "ship_floor": draw_ship_floor,
    # ...and the castle, drawn here because there is nowhere to take it
    # from: Chuck has never been to one.
    "courtyard_stone": draw_courtyard_stone,
    "courtyard_wall": draw_courtyard_wall,
    "astral_void": draw_astral_void,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((COLLIDED.cols * TILE_PX, COLLIDED.rows * TILE_PX),
                           pygame.SRCALPHA)
    for row_i, (name, variants, frames) in enumerate(COLLIDED.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / COLLIDED.sheet
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
