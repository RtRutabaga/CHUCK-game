"""Generate the three-facing Phase 11 raccoon sprite."""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
W, H = 20, 14


def draw_raccoon(surface: pygame.Surface, facing: str) -> None:
    shadow = (20, 23, 29, 130)
    fur, light, dark = (82, 88, 94), (138, 143, 145), (28, 31, 36)
    pygame.draw.ellipse(surface, shadow, (2, 9, 16, 4))
    if facing in {"down", "up"}:
        pygame.draw.ellipse(surface, fur, (4, 3, 12, 9))
        pygame.draw.polygon(surface, fur, ((5, 4), (6, 0), (9, 4)))
        pygame.draw.polygon(surface, fur, ((11, 4), (14, 0), (15, 5)))
        if facing == "down":
            pygame.draw.rect(surface, dark, (5, 5, 10, 3))
            pygame.draw.rect(surface, (225, 218, 185), (7, 6, 1, 1))
            pygame.draw.rect(surface, (225, 218, 185), (12, 6, 1, 1))
            pygame.draw.rect(surface, light, (8, 8, 4, 3))
        else:
            pygame.draw.rect(surface, dark, (5, 3, 10, 2))
            pygame.draw.rect(surface, light, (7, 8, 6, 2))
    else:
        pygame.draw.ellipse(surface, fur, (5, 4, 12, 8))
        pygame.draw.polygon(surface, fur, ((5, 6), (2, 3), (3, 9)))
        pygame.draw.rect(surface, light, (8, 8, 7, 2))
        pygame.draw.rect(surface, dark, (2, 5, 5, 2))
        pygame.draw.rect(surface, light, (0, 5, 2, 2))


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((W * 3, H), pygame.SRCALPHA)
    for index, facing in enumerate(("down", "up", "left")):
        frame = pygame.Surface((W, H), pygame.SRCALPHA)
        draw_raccoon(frame, facing)
        sheet.blit(frame, (index * W, 0))
    output = ROOT / "assets" / "sprites" / "hazards" / "raccoon.png"
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({W * 3}x{H})")


if __name__ == "__main__":
    main()
