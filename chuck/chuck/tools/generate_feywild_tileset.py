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


DRAW = {
    "fey_ground": ground,
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
