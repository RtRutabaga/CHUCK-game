"""Generate the sewer tileset: assets/tilesets/sewer.png.

Run from the project root (uses pygame, already a project dependency —
no Pillow needed, unlike the older docks generator):

    python tools/generate_sewer_tileset.py

The sheet is laid out per src/world/tileset_layout.SEWER (the shared
contract with the runtime): one row per terrain, each row holding
`variants * frames` 16x16 cells ordered [v0f0, v0f1, v1f0, ...], exactly
what art_index() indexes into.

Art direction (Game Bible: the world is worn, not gross): a damp brick
tunnel a rat's-eye below the docks. Brick walls, a stone entrance
landing, packed dirt and wet mud underfoot, and a murky drainage
channel that flows across three frames. Texture reads at a glance and
disappears at a stare — the ground is a stage, not the show.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import SEWER, TILE_PX

# --- palette (RGB) ---------------------------------------------------------
WALL = {"base": (72, 66, 58), "mortar": (40, 38, 36),
        "hi": (92, 84, 72), "low": (56, 50, 44)}
STONE = {"slab": (88, 86, 82), "seam": (56, 54, 52),
         "hi": (106, 104, 100), "speck": (72, 70, 68)}
DIRT = {"base": (74, 62, 48), "dark": (58, 48, 38),
        "light": (94, 80, 60), "pebble": (110, 94, 70)}
MUD = {"base": (58, 50, 38), "dark": (44, 38, 28),
       "glint": (86, 80, 58), "wet": (70, 64, 46)}
CHAN = {"water": (46, 56, 46), "dark": (34, 44, 36),
        "mid": (60, 72, 58), "glint": (96, 112, 90)}
ASTRAL = {"deep": (14, 16, 38), "blue": (28, 38, 82),
          "purple": (72, 42, 104), "bright": (158, 132, 210),
          "star": (228, 232, 248)}


def _rand(x: int, y: int, salt: int) -> float:
    """Stable pseudo-random in [0, 1) from a tile coordinate + salt."""
    h = (x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)
    return (h & 0xFFFFFFFF) % 1000 / 1000.0


def draw_wall(surf, variant, _frame):
    surf.fill(WALL["base"])
    course_h = 4
    for cy in range(0, TILE_PX, course_h):
        course = cy // course_h
        offset = 4 if (course + variant) % 2 else 0
        # top highlight of each brick course, then its bottom mortar line
        pygame.draw.line(surf, WALL["hi"], (0, cy), (15, cy))
        pygame.draw.line(surf, WALL["mortar"],
                         (0, cy + course_h - 1), (15, cy + course_h - 1))
        for vx in range(offset, TILE_PX, 8):  # vertical joints
            pygame.draw.line(surf, WALL["mortar"],
                             (vx, cy), (vx, cy + course_h - 1))
    for y in range(TILE_PX):  # a little grime so bricks aren't flat
        for x in range(TILE_PX):
            r = _rand(x, y, variant + 1)
            if r > 0.93:
                surf.set_at((x, y), WALL["low"])


def draw_stone(surf, variant, _frame):
    surf.fill(STONE["slab"])
    off = 4 * variant
    pygame.draw.line(surf, STONE["seam"], (0, 7), (15, 7))
    pygame.draw.line(surf, STONE["seam"], (0, 15), (15, 15))
    pygame.draw.line(surf, STONE["seam"],
                     ((5 + off) % 16, 0), ((5 + off) % 16, 7))
    pygame.draw.line(surf, STONE["seam"],
                     ((11 + off) % 16, 8), ((11 + off) % 16, 15))
    pygame.draw.line(surf, STONE["hi"], (0, 8), (15, 8))  # slab top catches light
    for y in range(TILE_PX):
        for x in range(TILE_PX):
            r = _rand(x, y, variant + 2)
            if r > 0.90:
                surf.set_at((x, y), STONE["speck"])
            elif r < 0.05:
                surf.set_at((x, y), STONE["hi"])


def draw_dirt(surf, variant, _frame):
    surf.fill(DIRT["base"])
    for y in range(TILE_PX):
        for x in range(TILE_PX):
            r = _rand(x, y, variant + 3)
            if r > 0.88:
                surf.set_at((x, y), DIRT["light"])
            elif r < 0.14:
                surf.set_at((x, y), DIRT["dark"])
    # a couple of small pebbles per variant
    for i in range(2):
        px = int(_rand(i, variant, 5) * 12) + 1
        py = int(_rand(variant, i, 9) * 12) + 1
        surf.fill(DIRT["pebble"], (px, py, 2, 2))
        surf.set_at((px, py), DIRT["light"])


def draw_mud(surf, variant, _frame):
    surf.fill(MUD["base"])
    for y in range(TILE_PX):
        for x in range(TILE_PX):
            r = _rand(x, y, variant + 4)
            if r < 0.16:
                surf.set_at((x, y), MUD["dark"])
            elif r > 0.93:
                surf.set_at((x, y), MUD["glint"])
            elif r > 0.86:
                surf.set_at((x, y), MUD["wet"])


def draw_channel(surf, _variant, frame):
    surf.fill(CHAN["water"])
    for y in range(TILE_PX):  # murky base with dark motes
        for x in range(TILE_PX):
            if _rand(x, y, 50) < 0.06:
                surf.set_at((x, y), CHAN["dark"])
    # flowing ripples: light bands whose phase slides with the frame
    for ry in (1, 4, 7, 10, 13):
        phase = ry * 3 + frame * 5
        for x in range(TILE_PX):
            if (x + phase) % 6 < 2:
                surf.set_at((x, ry), CHAN["mid"])
            if (x + phase) % 12 == 0:
                    surf.set_at((x, ry), CHAN["glint"])


def draw_astral_void(surf, variant, frame):
    """A hard-edged chunk of another map, never a swirling portal."""
    surf.fill(ASTRAL["deep"])
    # Blocky nebula bands shift by whole pixels, preserving the visibly
    # incorrect tile-grid language instead of reading as liquid or mist.
    phase = frame * 2 + variant * 3
    for y in range(TILE_PX):
        for x in range(TILE_PX):
            band = (x // 3 + y // 2 + phase) % 9
            if band in (0, 1):
                surf.set_at((x, y), ASTRAL["blue"])
            elif band == 5 and (x + y + variant) % 3 == 0:
                surf.set_at((x, y), ASTRAL["purple"])
    stars = ((2, 3), (11, 2), (7, 9), (14, 13))
    for i, (x, y) in enumerate(stars):
        if (i + frame + variant) % 3 != 0:
            surf.set_at((x, y), ASTRAL["star"])
        elif i == 0:
            surf.set_at((x, y), ASTRAL["bright"])


DRAW = {
    "sewer_wall": draw_wall,
    "sewer_stone": draw_stone,
    "sewer_dirt": draw_dirt,
    "sewer_mud": draw_mud,
    "sewer_channel": draw_channel,
    "astral_void": draw_astral_void,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((SEWER.cols * TILE_PX, SEWER.rows * TILE_PX),
                           pygame.SRCALPHA)
    sheet.fill((0, 0, 0, 0))
    for row_i, (name, variants, frames) in enumerate(SEWER.order):
        draw = DRAW[name]
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX))
                draw(cell, variant, frame)
                col = variant * frames + frame
                sheet.blit(cell, (col * TILE_PX, row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / "sewer.png"
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()}, "
          f"{SEWER.rows} terrains).")


if __name__ == "__main__":
    main()
