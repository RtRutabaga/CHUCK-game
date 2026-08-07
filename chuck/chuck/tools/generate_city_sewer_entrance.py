"""Generate the human-scale open concrete entrance used by City Night 6."""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    pygame.init()
    image = pygame.Surface((80, 64), pygame.SRCALPHA)
    concrete = (75, 78, 84)
    light = (111, 114, 118)
    shadow = (40, 43, 49)
    pygame.draw.rect(image, shadow, (2, 4, 76, 60))
    pygame.draw.rect(image, concrete, (5, 1, 70, 63))
    pygame.draw.line(image, light, (6, 2), (73, 2), 2)

    opening = [(14, 63), (14, 20), (18, 20), (18, 13), (24, 13),
               (24, 9), (56, 9), (56, 13), (62, 13), (62, 20),
               (66, 20), (66, 63)]
    pygame.draw.polygon(image, (7, 9, 13), opening)
    pygame.draw.lines(image, shadow, False, opening[:-1], 2)
    for index, y in enumerate((44, 51, 57, 62)):
        inset = index * 3
        gray = 48 + index * 5
        pygame.draw.line(image, (gray, gray, gray),
                         (18 + inset, y), (62 - inset, y), 2)

    steel = (112, 122, 126)
    for x in (19, 61):
        pygame.draw.line(image, steel, (x, 25), (x, 55), 2)
        pygame.draw.line(image, steel, (x, 25),
                         (27 if x < 40 else 53, 37), 2)
    pygame.draw.rect(image, (184, 142, 54), (7, 39, 5, 9))
    pygame.draw.rect(image, (184, 142, 54), (68, 39, 5, 9))

    output = ROOT / "assets" / "sprites" / "objects" / "city_sewer_entrance.png"
    pygame.image.save(image, output)
    print(f"Wrote {output} ({image.get_width()}x{image.get_height()})")
    pygame.quit()


if __name__ == "__main__":
    main()
