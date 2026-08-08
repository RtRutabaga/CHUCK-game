"""Generate the Animal Control officer sheet (Phase 11).

An officer is an UndeadEnemy kind, so this sheet matches that layout
exactly: three facings (down, up, left) in 16x30 frames. He reads as
municipal rather than menacing -- a peaked cap, a drab uniform, a badge
-- with one thing that matters at a glance: a long pole over his
shoulder with a hoop of net on the end of it.
"""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
W, H = 16, 30

UNIFORM = (74, 86, 72)
UNIFORM_DARK = (52, 62, 52)
CAP = (44, 54, 46)
SKIN = (206, 164, 126)
BOOT = (34, 34, 38)
BADGE = (214, 186, 78)
POLE = (128, 100, 62)
NET = (208, 216, 222)


def draw_officer(surface: pygame.Surface, facing: str) -> None:
    # The pole first, so the body overlaps it and it reads as carried.
    if facing == "left":
        pygame.draw.line(surface, POLE, (12, 6), (2, 17), 2)
        hoop = (0, 15, 8, 8)
    else:
        pygame.draw.line(surface, POLE, (3, 6), (13, 17), 2)
        hoop = (9, 14, 8, 8)
    pygame.draw.ellipse(surface, NET, hoop, 1)
    for offset in (2, 4, 6):
        pygame.draw.line(surface, (150, 160, 170),
                         (hoop[0] + offset, hoop[1] + 1),
                         (hoop[0] + offset, hoop[1] + hoop[3] - 1))

    pygame.draw.rect(surface, CAP, (4, 5, 8, 3))          # peaked cap
    pygame.draw.rect(surface, CAP, (3, 7, 10, 1))
    pygame.draw.rect(surface, SKIN, (5, 8, 6, 5))
    pygame.draw.rect(surface, UNIFORM, (4, 13, 8, 11))    # tunic
    pygame.draw.rect(surface, UNIFORM_DARK, (4, 13, 2, 11))
    pygame.draw.rect(surface, UNIFORM_DARK, (4, 19, 8, 1))  # belt
    pygame.draw.rect(surface, BOOT, (4, 24, 3, 5))
    pygame.draw.rect(surface, BOOT, (9, 24, 3, 5))

    if facing == "down":
        pygame.draw.rect(surface, BADGE, (5, 15, 2, 2))
        surface.set_at((6, 11), (40, 34, 30))
        surface.set_at((9, 11), (40, 34, 30))
    elif facing == "up":
        pygame.draw.rect(surface, CAP, (4, 8, 8, 4))       # back of the cap
    else:
        pygame.draw.rect(surface, BADGE, (5, 15, 2, 2))
        surface.set_at((5, 11), (40, 34, 30))


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((W * 3, H), pygame.SRCALPHA)
    for index, facing in enumerate(("down", "up", "left")):
        frame = pygame.Surface((W, H), pygame.SRCALPHA)
        draw_officer(frame, facing)
        sheet.blit(frame, (index * W, 0))
    out = ROOT / "assets" / "sprites" / "hazards" / "animal_control.png"
    pygame.image.save(sheet, out)
    print(f"Wrote {out} ({W * 3}x{H})")


if __name__ == "__main__":
    main()
