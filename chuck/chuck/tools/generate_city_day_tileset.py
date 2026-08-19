"""Generate the rainy daytime city tiles.

The daytime city is the same city. Its geometry, scale and traffic
language are unchanged, so this sheet reuses the night tileset's exact
draw functions and puts overcast daylight on them rather than authoring
a second set of buildings that would drift out of step.

Daylight here is flat and grey: the whole palette lifts, the deep blues
wash out toward slate, and lit windows stop glowing because nobody
leaves a light on at noon. One genuinely new row is added -- standing
puddles -- because rain reads on the ground in daylight and vanished
into the dark at night.
"""

import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import CITY_DAY, TILE_PX
import generate_chult_tileset as chult
import generate_city_tileset as night
from generate_sewer_tileset import draw_astral_void

# How far each channel is pulled toward the overcast sky colour, and the
# sky itself. Blue is lifted least so the result greys out rather than
# turning the city baby-blue.
SKY = (196, 202, 208)
LIFT = (0.42, 0.44, 0.34)


def _daylight(surface) -> None:
    """Wash one finished night tile into flat overcast daylight."""
    surface.lock()
    for y in range(TILE_PX):
        for x in range(TILE_PX):
            r, g, b, a = surface.get_at((x, y))
            if a == 0:
                continue
            surface.set_at((x, y), (
                round(r + (SKY[0] - r) * LIFT[0]),
                round(g + (SKY[1] - g) * LIFT[1]),
                round(b + (SKY[2] - b) * LIFT[2]),
                a,
            ))
    surface.unlock()


def _lit(draw):
    """Wrap a night draw function so its result comes out in daylight."""
    def drawn(surface, variant, frame):
        draw(surface, variant, frame)
        _daylight(surface)
    return drawn


def day_window(surface, variant, frame):
    """A window at noon: glass reflecting grey sky, never lit from within.

    The night sheet animates a warm interior glow across its frames; in
    daylight that would read as somebody's lamp on at midday, so this
    keeps the frame animation but spends it on rain running down glass.
    """
    night.facade(surface, variant, frame)
    _daylight(surface)
    pygame.draw.rect(surface, (126, 138, 150), (3, 2, 10, 11))
    pygame.draw.rect(surface, (150, 162, 172), (4, 3, 8, 5))
    pygame.draw.line(surface, (96, 108, 120), (3, 8), (12, 8))
    x = 4 + (variant + frame) % 8
    pygame.draw.line(surface, (176, 188, 196), (x, 3), (x, 12))
    pygame.draw.rect(surface, (72, 82, 92), (3, 2, 10, 11), 1)


def puddle(surface, variant, frame):
    """Standing water on the sidewalk, dimpled by the rain."""
    night.sidewalk(surface, variant, frame)
    _daylight(surface)
    pygame.draw.ellipse(surface, (138, 152, 164), (1, 4, 14, 10))
    pygame.draw.ellipse(surface, (158, 172, 182), (3, 6, 10, 6))
    for index in range(3):
        x = (variant * 5 + index * 6 + frame * 3) % 14 + 1
        y = (variant * 3 + index * 4 + frame) % 8 + 4
        pygame.draw.circle(surface, (196, 208, 214), (x, y), 1)


def doug_fir_block(surface, variant, frame):
    """A block of Douglas fir forest at night, standing in the street.

    The Astral damage on this map is a purple starfield, so this has to
    read as a different kind of elsewhere or the two blur together: a
    cold blue night sky with black conifer silhouettes against it, and
    the moon catching one edge of the needles.
    """
    # A four-frame blue-violet pulse makes this singular explicit portal read
    # immediately against the static city, while retaining the authored forest
    # view instead of turning it into generic glowing magic.
    pulse = (0, 1, 2, 1)[frame % 4]
    skies = ((14, 25, 48), (22, 28, 63), (38, 24, 78))
    edge = ((72, 154, 164), (128, 118, 204), (202, 92, 218))[pulse]
    sky = skies[pulse]
    for y in range(TILE_PX):
        depth = y // 3
        pygame.draw.line(
            surface,
            (sky[0] + depth, sky[1] + depth, sky[2] + depth),
            (0, y), (15, y),
        )
    # Thin aurora ribbons oscillate laterally behind the silhouettes. Their
    # stagger across tile variants prevents the 3x3 block reading as a grid.
    for ribbon in range(2):
        x = (variant * 5 + ribbon * 9 + frame * (2 + ribbon)) % 18 - 1
        pygame.draw.line(surface, edge, (x, 1), (x - 2, 14), 1)
    for index in range(2):
        x = 3 + index * 8 + (variant % 3)
        base = 15
        top = 2 + ((variant + index) % 3)
        # A conifer: stacked skirts narrowing to a point.
        for step, half in enumerate(range(1, 6)):
            y = top + step * 3
            if y >= base:
                break
            pygame.draw.line(surface, (8, 26, 22),
                             (x - half, y), (x + half, y), 3)
        pygame.draw.line(surface, (30, 24, 18), (x, base - 2), (x, base))
        # Moonlight down one side of the tree.
        pygame.draw.line(surface, edge,
                         (x - 1, top + 1), (x - 3, top + 7))
    pygame.draw.line(surface, (16, 30, 26), (0, 15), (15, 15), 2)
    for star in range(2):
        surface.set_at((
            (variant * 5 + frame * 4 + star * 7) % 16,
            (variant * 3 + frame + star * 3 + 1) % 7,
        ), (212, 208 - pulse * 18, 238))


DRAW = {
    "city_day_roof": _lit(night.roof),
    # The roof volume is drawn once, at night, and washed for daylight
    # like every other shared row. No day map places these chars yet.
    "city_day_parapet": _lit(night.parapet),
    "city_day_parapet_left": _lit(night.parapet_left),
    "city_day_parapet_right": _lit(night.parapet_right),
    "city_day_roof_vent": _lit(night.roof_vent),
    "city_day_skylight": _lit(night.skylight),
    "city_day_cornice": _lit(night.cornice),
    "city_day_facade": _lit(night.facade),
    "city_day_side_facade": _lit(night.side_facade),
    "city_day_window": day_window,
    "city_day_sidewalk": _lit(night.sidewalk),
    "city_day_curb": _lit(night.curb),
    "city_day_road": _lit(night.road),
    "city_day_road_line_h": _lit(night.road_line_h),
    "city_day_road_line_v": _lit(night.road_line_v),
    "city_day_crosswalk": _lit(night.crosswalk),
    "city_day_puddle": puddle,
    # A patch of Chult, embedded in the street exactly as it is in
    # the jungle: the same draws, unwashed, so it reads as another
    # world showing through rather than as city scenery.
    "chult_ground": chult.draw_ground,
    "chult_dense": chult.draw_dense_jungle,
    "doug_fir_block": doug_fir_block,
    "astral_void": draw_astral_void,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface(
        (CITY_DAY.cols * TILE_PX, CITY_DAY.rows * TILE_PX), pygame.SRCALPHA
    )
    for row, (name, variants, frames) in enumerate(CITY_DAY.order):
        draw = DRAW[name]
        for variant in range(variants):
            for frame in range(frames):
                tile = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                draw(tile, variant, frame)
                sheet.blit(tile, ((variant * frames + frame) * TILE_PX,
                                  row * TILE_PX))
    out = ROOT / "assets" / "tilesets" / "city_day.png"
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
