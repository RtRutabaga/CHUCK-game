"""Generate the Phase 11 businessperson sprite sheet."""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
W, H = 16, 30


def draw_person(surface: pygame.Surface, facing: str) -> None:
    # Umbrella, head, dark suit, shirt and human-scale shoes; kept readable
    # in the same 16x30 silhouette as Waterdeep's NPCs.
    pygame.draw.ellipse(surface, (27, 31, 42), (0, 0, 16, 7))
    pygame.draw.rect(surface, (17, 19, 26), (7, 4, 2, 11))
    skin = (202, 159, 121)
    pygame.draw.rect(surface, skin, (5, 7, 6, 6))
    pygame.draw.rect(surface, (38, 44, 56), (4, 13, 8, 11))
    pygame.draw.rect(surface, (213, 215, 207), (7, 13, 2, 7))
    pygame.draw.rect(surface, (27, 29, 37), (4, 23, 3, 6))
    pygame.draw.rect(surface, (27, 29, 37), (9, 23, 3, 6))
    if facing == "down":
        pygame.draw.rect(surface, (73, 52, 39), (6, 8, 4, 2))
        pygame.draw.rect(surface, (38, 32, 27), (6, 11, 1, 1))
        pygame.draw.rect(surface, (38, 32, 27), (9, 11, 1, 1))
    elif facing == "up":
        pygame.draw.rect(surface, (73, 52, 39), (5, 7, 6, 3))
    else:
        pygame.draw.rect(surface, (73, 52, 39), (5, 7, 5, 3))
        pygame.draw.rect(surface, (38, 32, 27), (5, 10, 1, 1))


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((W * 3, H), pygame.SRCALPHA)
    for index, facing in enumerate(("down", "up", "left")):
        frame = pygame.Surface((W, H), pygame.SRCALPHA)
        draw_person(frame, facing)
        sheet.blit(frame, (index * W, 0))
    output = ROOT / "assets" / "sprites" / "npcs" / "businessman.png"
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({W * 3}x{H})")


if __name__ == "__main__":
    main()
