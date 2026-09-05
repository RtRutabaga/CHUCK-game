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
