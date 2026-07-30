"""Generate the Phlegethos (Nine Hells) overworld tileset (Phase 8).

Dark cracked basalt, volcanic cliffs, worn stone paths, glowing fissures,
and animated lava (a walkable fall hazard). The basalt/lava palette is the
hell-fall cutscene's HELL_BASALT/LAVA colours so the ground and the descent
read as the same place.
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

from src.world.tileset_layout import PHLEGETHOS, TILE_PX

BASALT = (42, 28, 27)
BASALT_DARK = (28, 22, 23)
BASALT_MID = (58, 35, 30)
BASALT_LIGHT = (76, 43, 32)
CLIFF = (34, 25, 26)
CLIFF_DARK = (20, 16, 18)
CLIFF_LIGHT = (66, 44, 38)
PATH = (70, 60, 56)
PATH_DARK = (48, 40, 39)
PATH_LIGHT = (94, 82, 74)
LAVA = (178, 45, 12)
LAVA_DEEP = (112, 28, 13)
LAVA_HOT = (235, 83, 15)
LAVA_BRIGHT = (255, 157, 31)
ASTRAL = {
    "deep": (14, 16, 38),
    "blue": (28, 38, 82),
    "purple": (72, 42, 104),
    "bright": (158, 132, 210),
    "star": (228, 232, 248),
}


def draw_basalt(surface, variant: int, _frame: int) -> None:
    surface.fill(BASALT)
    pygame.draw.line(surface, BASALT_DARK, (0, 15), (15, 15))
    # Angular cracked plates, shaded per variant so the ground breaks up.
    plates = (
        (((1, 1), (9, 2), (7, 8), (0, 6)), ((10, 3), (15, 5), (13, 12))),
        (((4, 0), (14, 1), (12, 7), (3, 6)), ((0, 8), (6, 9), (2, 14))),
        (((0, 2), (7, 0), (8, 7), (1, 9)), ((9, 6), (15, 8), (11, 15))),
        (((2, 3), (11, 1), (14, 9), (5, 11)), ((0, 11), (5, 13), (1, 15))),
    )[variant]
    pygame.draw.polygon(surface, BASALT_MID, plates[0])
    pygame.draw.polygon(surface, BASALT_DARK, plates[1])
    pygame.draw.line(surface, BASALT_LIGHT, plates[0][0], plates[0][1])
    # A couple of ash flecks.
    surface.set_at(((variant * 5 + 3) % 15, (variant * 3 + 4) % 14),
                   BASALT_LIGHT)


def draw_cliff(surface, variant: int, _frame: int) -> None:
    surface.fill(CLIFF)
    pygame.draw.rect(surface, CLIFF_DARK, (0, 13, 16, 3))
    pygame.draw.line(surface, CLIFF_LIGHT, (0, 0), (15, 0))
    for y in (5, 10):
        pygame.draw.line(surface, CLIFF_DARK, (0, y), (15, y))
    seam = 4 + variant * 4
    pygame.draw.line(surface, CLIFF_DARK, (seam, 0), (seam, 12))
    pygame.draw.line(surface, CLIFF_LIGHT, (seam + 1, 1), (seam + 1, 4))


def draw_path(surface, variant: int, _frame: int) -> None:
    surface.fill(PATH)
    pygame.draw.line(surface, PATH_DARK, (0, 15), (15, 15))
    # Worn, mortared flagstones.
    joints = (((5, 0), (5, 7), (11, 7), (11, 15)),
              ((8, 0), (3, 6), (3, 15)))[variant]
    pygame.draw.lines(surface, PATH_DARK, False, joints)
    pygame.draw.line(surface, PATH_LIGHT, (1, 1), (13, 1))
    surface.set_at((2 + variant * 6, 9), PATH_DARK)


def draw_lava(surface, variant: int, frame: int) -> None:
    """Molten lava with a slow crust; three frames roll the glow."""
    surface.fill(LAVA_DEEP)
    phase = frame * 2.0 + variant * 1.3
    for y in range(16):
        glow = 0.5 + 0.5 * math.sin(y * 0.7 + phase)
        col = tuple(round(a + (b - a) * glow)
                    for a, b in zip(LAVA_DEEP, LAVA))
        pygame.draw.line(surface, col, (0, y), (15, y))
    # Bright cracks between cooling crust plates.
    for i in range(3):
        x = (i * 6 + round(math.sin(phase + i) * 2)) % 15
        y0 = (i * 5 + variant * 2) % 12
        pygame.draw.line(surface, LAVA_HOT, (x, y0), (x + 2, y0 + 4))
        surface.set_at((x + 1, y0 + 2), LAVA_BRIGHT)
    # Dark crust islands.
    pygame.draw.polygon(surface, BASALT_DARK,
                        ((2, 6), (6, 5), (5, 9), (1, 9)))


def draw_fissure(surface, variant: int, _frame: int) -> None:
    """Basalt cracked open on a glowing lava seam."""
    draw_basalt(surface, variant, 0)
    if variant == 0:
        crack = ((3, 1), (7, 6), (5, 11), (9, 15))
    else:
        crack = ((13, 1), (8, 5), (11, 10), (6, 15))
    pygame.draw.lines(surface, LAVA_DEEP, False, crack, 3)
    pygame.draw.lines(surface, LAVA, False, crack, 1)
    for x, y in crack[1:3]:
        surface.set_at((x, y), LAVA_HOT)


def draw_pass(surface, _variant: int, _frame: int) -> None:
    """A dark gap in the cliff wall: the way onward, worn smooth."""
    surface.fill(CLIFF_DARK)
    pygame.draw.rect(surface, (12, 9, 11), (2, 0, 12, 16))
    pygame.draw.line(surface, CLIFF, (0, 0), (0, 15))
    pygame.draw.line(surface, CLIFF, (15, 0), (15, 15))
    pygame.draw.line(surface, CLIFF_LIGHT, (1, 0), (1, 4))
    pygame.draw.line(surface, CLIFF_LIGHT, (14, 0), (14, 4))
    # A worn threshold underfoot so it reads as walkable.
    pygame.draw.line(surface, PATH_DARK, (2, 14), (13, 14))
    pygame.draw.line(surface, PATH, (3, 15), (12, 15))


def draw_astral_void(surface, variant: int, frame: int) -> None:
    """The exact hard-edged Astral hazard language used in earlier regions."""
    surface.fill(ASTRAL["deep"])
    phase = frame * 2 + variant * 3
    for y in range(TILE_PX):
        for x in range(TILE_PX):
            band = (x // 3 + y // 2 + phase) % 9
            if band in (0, 1):
                surface.set_at((x, y), ASTRAL["blue"])
            elif band == 5 and (x + y + variant) % 3 == 0:
                surface.set_at((x, y), ASTRAL["purple"])
    stars = ((2, 3), (11, 2), (7, 9), (14, 13))
    for i, (x, y) in enumerate(stars):
        if (i + frame + variant) % 3 != 0:
            surface.set_at((x, y), ASTRAL["star"])
        elif i == 0:
            surface.set_at((x, y), ASTRAL["bright"])


FORT = (44, 40, 46)
FORT_DARK = (26, 24, 30)
FORT_LIGHT = (70, 64, 72)
FORT_IRON = (96, 92, 100)


def draw_fortress(surface, variant: int, _frame: int) -> None:
    """Iron-black fortress masonry: colder and harder than the cliffs."""
    surface.fill(FORT)
    pygame.draw.rect(surface, FORT_DARK, (0, 13, 16, 3))
    pygame.draw.line(surface, FORT_LIGHT, (0, 0), (15, 0))
    for y in (4, 9):
        pygame.draw.line(surface, FORT_DARK, (0, y), (15, y))
    seam = (variant * 5 + 2) % 14
    pygame.draw.line(surface, FORT_DARK, (seam, 0), (seam, 4))
    pygame.draw.line(surface, FORT_DARK, ((seam + 7) % 15, 5),
                     ((seam + 7) % 15, 9))
    # Iron rivets and a faint ember bleeding from the joints.
    surface.set_at((seam + 2 if seam < 13 else 1, 7), FORT_IRON)
    if variant == 1:
        surface.set_at((11, 11), LAVA_HOT)


def draw_fortress_gate(surface, _variant: int, _frame: int) -> None:
    """A barred gate, shut: the fortress interior is not this phase."""
    surface.fill(FORT_DARK)
    for x in range(1, 16, 3):
        pygame.draw.line(surface, FORT_IRON, (x, 0), (x, 15))
        pygame.draw.line(surface, FORT_LIGHT, (x, 0), (x, 3))
    for y in (3, 11):
        pygame.draw.line(surface, FORT_IRON, (0, y), (15, y))
    # Hellfire glimmering somewhere far behind the bars.
    for x, y in ((3, 8), (9, 6), (13, 9)):
        surface.set_at((x, y), LAVA_DEEP)


DRAW = {
    "basalt": draw_basalt,
    "cliff": draw_cliff,
    "path": draw_path,
    "lava": draw_lava,
    "fissure": draw_fissure,
    "pass": draw_pass,
    "astral_void": draw_astral_void,
    "fortress": draw_fortress,
    "fortress_gate": draw_fortress_gate,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((PHLEGETHOS.cols * TILE_PX,
                            PHLEGETHOS.rows * TILE_PX), pygame.SRCALPHA)
    for row_i, (name, variants, frames) in enumerate(PHLEGETHOS.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / PHLEGETHOS.sheet
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
