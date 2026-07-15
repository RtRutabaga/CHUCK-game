"""Generate the compact Waterdeep pantry tileset."""

import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import PANTRY, TILE_PX
from generate_sewer_tileset import draw_astral_void


FLOOR = {
    "base": (105, 69, 40), "light": (137, 91, 50),
    "dark": (68, 43, 29), "wear": (88, 57, 35),
}
WALL = {
    "plaster": (126, 103, 72), "shade": (82, 63, 45),
    "beam": (59, 39, 27), "light": (151, 128, 89),
}
SKY = {
    "teal": (30, 143, 154), "deep": (24, 112, 128),
    "cloud": (204, 232, 217), "shade": (151, 204, 197),
}


def draw_floor(surface, variant: int, _frame: int) -> None:
    surface.fill(FLOOR["base"])
    seam = 7 + variant % 2
    pygame.draw.line(surface, FLOOR["dark"], (0, seam), (15, seam))
    pygame.draw.line(surface, FLOOR["light"], (0, seam + 1), (15, seam + 1))
    pygame.draw.line(surface, FLOOR["dark"], (0, 15), (15, 15))
    for x in ((4 + variant * 5) % 16, (12 + variant * 3) % 16):
        pygame.draw.line(surface, FLOOR["wear"], (x, 1), (x, 6))
    # Short pale scuffs make these boards older than the common-room floor.
    for x, y in ((2 + variant * 3, 4), (11 - variant, 12)):
        pygame.draw.line(surface, FLOOR["light"], (x, y), (x + 2, y))


def draw_wall(surface, variant: int, _frame: int) -> None:
    surface.fill(WALL["plaster"])
    pygame.draw.rect(surface, WALL["beam"], (0, 0, 16, 3))
    pygame.draw.rect(surface, WALL["shade"], (0, 13, 16, 3))
    beam_x = 2 if variant == 0 else 12
    pygame.draw.rect(surface, WALL["beam"], (beam_x, 0, 2, 16))
    pygame.draw.line(surface, WALL["light"], (0, 3), (15, 3))


def draw_sky_cloud(surface, variant: int, frame: int) -> None:
    """A hard-edged view of teal open sky, not a glowing portal."""
    surface.fill(SKY["teal"])
    pygame.draw.line(surface, SKY["deep"], (0, 15), (15, 15))
    # Each stable terrain variant gets its own seeded cloud placement. The
    # runtime still picks variants deterministically per map coordinate, so the
    # floor never rearranges, but a field no longer exposes a two-tile stamp.
    rng = random.Random(0xC10D + variant * 7919)
    cloud_y = rng.randint(1, 10)
    cloud_w = rng.randint(6, 11)
    cloud_x = rng.randint(-4, 9)
    drift = frame * (-1 if variant % 3 == 0 else 1)
    x = cloud_x + drift
    cap_w = max(3, cloud_w - 4)
    cap_x = x + (cloud_w - cap_w) // 2
    pygame.draw.rect(surface, SKY["shade"], (x, cloud_y + 2, cloud_w, 3))
    pygame.draw.rect(surface, SKY["cloud"], (cap_x, cloud_y, cap_w, 4))
    pygame.draw.rect(surface, SKY["cloud"], (x, cloud_y + 2, cloud_w, 2))


DRAW = {
    "pantry_floor": draw_floor,
    "pantry_wall": draw_wall,
    "astral_void": draw_astral_void,
    "sky_cloud": draw_sky_cloud,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((PANTRY.cols * TILE_PX, PANTRY.rows * TILE_PX),
                           pygame.SRCALPHA)
    for row_i, (name, variants, frames) in enumerate(PANTRY.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                col = variant * frames + frame
                sheet.blit(cell, (col * TILE_PX, row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / PANTRY.sheet
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
