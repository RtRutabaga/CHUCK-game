"""Generate the ship compartment tileset (session 147).

An internal wooden hull: plank floor, timber wall, and a brass porthole
onto the sunlit sea. The porthole's sky/sea/wave palette is the escape
cutscene's exact palette (escape_cutscene_scene.py), and its four frames
roll the wave crests sideways, so the playable compartment and the
cutscene read as the same place.
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

from src.world.tileset_layout import SHIP, TILE_PX

# The cutscene palette, shared so the two match exactly.
SKY = (196, 224, 240)
SEA = (96, 164, 214)
SEA_DEEP = (66, 138, 196)
CREST = (214, 236, 250)
WOOD = (120, 84, 52)        # plank floor
WALL = (92, 64, 40)         # hull timber
LINE = (78, 54, 34)
HL_FLOOR = (140, 100, 64)
HL_WALL = (110, 78, 48)
RIM = (150, 120, 66)        # brass
RIM_DARK = (96, 74, 38)


def draw_ship_floor(surface, variant: int, _frame: int) -> None:
    surface.fill(WOOD)
    for y in (4, 9, 14):
        pygame.draw.line(surface, LINE, (0, y), (15, y), 1)
        pygame.draw.line(surface, HL_FLOOR, (0, y + 1), (15, y + 1), 1)
    # A staggered plank butt-join so the boards don't line up.
    bx = (variant * 6 + 3) % 14
    pygame.draw.line(surface, LINE, (bx, 0), (bx, 4), 1)
    pygame.draw.line(surface, LINE, ((bx + 8) % 15, 10), ((bx + 8) % 15, 14), 1)
    surface.set_at((2 + variant * 3, 2), HL_FLOOR)


def draw_ship_wall(surface, variant: int, _frame: int) -> None:
    surface.fill(WALL)
    pygame.draw.line(surface, HL_WALL, (0, 0), (15, 0), 1)
    for y in (5, 11):
        pygame.draw.line(surface, LINE, (0, y), (15, y), 1)
    sx = 3 + variant * 5
    pygame.draw.line(surface, LINE, (sx, 0), (sx, 15), 1)
    # A bolt head or two in the timber.
    surface.set_at((sx - 2, 8), RIM_DARK)


def draw_porthole(surface, _variant: int, frame: int) -> None:
    """A brass porthole onto the sea, its wave crests rolled by `frame`."""
    draw_ship_wall(surface, 0, 0)  # timber background around the glass
    cx, cy, r = 8, 8, 6
    # Sky above, sea below, darker toward the bottom of the glass.
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r:
                continue
            if dy <= -2:
                col = SKY
            elif dy < 3:
                col = SEA
            else:
                col = SEA_DEEP
            surface.set_at((cx + dx, cy + dy), col)
    # Two rolling wave crests; the frame shifts their phase.
    for row, wy0 in enumerate((cy, cy + 3)):
        for dx in range(-r, r + 1):
            wy = wy0 + round(math.sin(dx * 0.9 + frame * 1.57 + row * 1.6) * 0.9)
            if dx * dx + (wy - cy) ** 2 <= r * r and (wy - cy) >= -1:
                surface.set_at((cx + dx, wy), CREST)
    # Brass rim and rivets, proud of the hull.
    pygame.draw.circle(surface, RIM, (cx, cy), r + 1, 2)
    pygame.draw.circle(surface, RIM_DARK, (cx, cy), r + 1, 1)
    for angle in (0, 90, 180, 270):
        rx = cx + round(math.cos(math.radians(angle)) * (r + 1))
        ry = cy + round(math.sin(math.radians(angle)) * (r + 1))
        surface.set_at((rx, ry), RIM_DARK)


DRAW = {
    "ship_floor": draw_ship_floor,
    "ship_wall": draw_ship_wall,
    "porthole": draw_porthole,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((SHIP.cols * TILE_PX, SHIP.rows * TILE_PX),
                           pygame.SRCALPHA)
    for row_i, (name, variants, frames) in enumerate(SHIP.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / SHIP.sheet
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
