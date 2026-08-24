"""Generate City Day 6's oval gray tie-dye planar portal.

The portal is a single human-scale standing prop rather than a tiled terrain
patch. Twelve transparent frames rotate soft bands through a gray oval and
cast the same restrained color onto the pavement below it.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys

import pygame

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.entities.planar_portal import GRAY, PALETTE, blend, portal_colour

OUT = ROOT / "assets" / "sprites" / "objects"
WIDTH = HEIGHT = 80
FRAMES = 12

_blend = blend


def _frame(index: int) -> pygame.Surface:
    image = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    phase = math.tau * index / FRAMES

    # Light spills forward across the pavement. Layered ellipses and short
    # rays keep it soft and pixel-readable rather than becoming a neon halo.
    glow = PALETTE[(index // 3) % len(PALETTE)]
    pygame.draw.ellipse(image, (*glow, 34), (4, 59, 72, 18))
    pygame.draw.ellipse(image, (*_blend(GRAY, glow, 0.55), 58),
                        (13, 62, 54, 12))
    for band, color in enumerate(PALETTE):
        x = 8 + band * 15 + round(math.sin(phase + band) * 3)
        pygame.draw.ellipse(image, (*color, 48), (x, 64, 24, 8))
    for ray in range(5):
        x = 18 + ray * 11 + round(math.sin(phase + ray) * 3)
        pygame.draw.line(image, (*glow, 44), (40, 55), (x, 76), 2)

    center_x, center_y = 40.0, 34.0
    radius_x, radius_y = 26.0, 31.0
    # Dark backing and a broad silver-gray rim establish one smooth oval.
    pygame.draw.ellipse(image, (34, 34, 42, 220), (10, 1, 60, 68))
    pygame.draw.ellipse(image, (104, 102, 114, 255), (11, 2, 58, 66), 4)
    pygame.draw.ellipse(image, (190, 188, 198, 230), (14, 5, 52, 60), 2)

    for y in range(5, 65):
        for x in range(14, 67):
            nx = (x - center_x) / radius_x
            ny = (y - center_y) / radius_y
            distance = math.hypot(nx, ny)
            if distance >= 0.94:
                continue
            # The surface itself is shared with the Douglas fir at the
            # end of the phase, so the two portals cannot drift apart.
            image.set_at((x, y), (*portal_colour(nx, ny, phase), 244))

    # Traveling highlights help the eye see rotation without hard lines.
    for mote in range(7):
        theta = phase + mote * math.tau / 7
        x = round(center_x + math.cos(theta) * radius_x * 0.72)
        y = round(center_y + math.sin(theta) * radius_y * 0.72)
        pygame.draw.circle(image, (224, 222, 230, 150), (x, y), 1)
    return image


def main() -> None:
    pygame.init()
    for index in range(FRAMES):
        output = OUT / f"city_planar_portal_{index + 1}.png"
        pygame.image.save(_frame(index), output)
    print(f"Wrote {FRAMES} city planar portal frames ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
