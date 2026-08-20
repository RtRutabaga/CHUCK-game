"""Generate the exterior landmarks and asynchronous mushroom lights."""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
OBJECTS = ROOT / "assets" / "sprites" / "objects"


def save(surface, name):
    path = OBJECTS / name
    pygame.image.save(surface, path)
    print(f"Wrote {path}")


def make_fir(index):
    s = pygame.Surface((48, 68), pygame.SRCALPHA)
    trunk_x = 22 + index % 2
    pygame.draw.rect(s, (48, 37, 29), (trunk_x, 28, 6, 39))
    pygame.draw.line(s, (75, 57, 38), (trunk_x + 4, 30),
                     (trunk_x + 4, 65))
    for layer in range(9):
        y = 2 + layer * 6
        half = 5 + layer * 2 + index % 3
        colour = ((12, 43, 34), (16, 55, 40), (21, 65, 45))[layer % 3]
        pygame.draw.polygon(s, colour, (
            (24, y), (24 - half, y + 15), (24 + half, y + 15),
        ))
        pygame.draw.line(s, (31, 74, 51), (24, y + 2),
                         (24 + half - 2, y + 13))
    pygame.draw.ellipse(s, (8, 18, 17), (8, 62, 33, 6))
    return s


LIGHT_COLOURS = (
    (74, 220, 236), (120, 104, 239), (224, 82, 221), (247, 94, 158),
    (245, 175, 72), (201, 230, 80), (74, 217, 130), (67, 150, 237),
)


def make_light(colour):
    s = pygame.Surface((32, 28), pygame.SRCALPHA)
    # Restrained local spill: blocky concentric translucent pixels keep the
    # effect native-scale while still tinting the ground around the fixture.
    pygame.draw.ellipse(s, (*colour, 20), (1, 16, 30, 11))
    pygame.draw.ellipse(s, (*colour, 38), (6, 18, 20, 7))
    pygame.draw.rect(s, (*colour, 150), (15, 10, 2, 13))
    dark = tuple(max(0, c - 65) for c in colour)
    pygame.draw.ellipse(s, (*dark, 240), (10, 7, 12, 7))
    pygame.draw.ellipse(s, (*colour, 255), (11, 6, 10, 6))
    pygame.draw.line(s, (235, 238, 220), (13, 7), (18, 7))
    return s


def make_firepit():
    s = pygame.Surface((34, 27), pygame.SRCALPHA)
    for x, y in ((3, 20), (8, 17), (14, 19), (20, 17), (26, 20)):
        pygame.draw.ellipse(s, (87, 87, 80), (x, y, 7, 5))
        pygame.draw.line(s, (137, 132, 113), (x + 1, y), (x + 5, y))
    pygame.draw.line(s, (65, 38, 25), (8, 21), (26, 15), 3)
    pygame.draw.line(s, (84, 45, 25), (7, 15), (27, 22), 3)
    pygame.draw.polygon(s, (225, 75, 28), ((14, 18), (17, 6), (21, 18)))
    pygame.draw.polygon(s, (255, 184, 57), ((17, 18), (19, 10), (22, 18)))
    return s


def make_ufo():
    s = pygame.Surface((66, 38), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (16, 20, 24), (4, 19, 58, 15))
    pygame.draw.ellipse(s, (81, 91, 96), (1, 12, 64, 17))
    pygame.draw.ellipse(s, (124, 137, 137), (9, 7, 48, 16))
    pygame.draw.ellipse(s, (38, 45, 52), (22, 2, 22, 13))
    pygame.draw.ellipse(s, (84, 105, 116), (25, 3, 16, 8))
    for x, colour in ((12, (78, 224, 215)), (27, (229, 89, 207)),
                      (43, (246, 179, 72)), (55, (103, 138, 241))):
        pygame.draw.rect(s, colour, (x, 22, 3, 2))
    return s


def make_shed():
    s = pygame.Surface((66, 52), pygame.SRCALPHA)
    pygame.draw.rect(s, (43, 34, 29), (8, 18, 52, 32))
    pygame.draw.polygon(s, (27, 36, 35), ((3, 20), (15, 8), (58, 8),
                                         (64, 20)))
    pygame.draw.line(s, (56, 73, 55), (10, 8), (57, 8), 3)
    for x in range(12, 58, 8):
        pygame.draw.rect(s, (77, 48, 29), (x, 27, 7, 18))
        pygame.draw.line(s, (117, 71, 37), (x + 1, 29), (x + 5, 29))
    pygame.draw.rect(s, (24, 22, 21), (7, 18, 5, 33))
    pygame.draw.rect(s, (24, 22, 21), (57, 18, 5, 33))
    return s


def main():
    pygame.init()
    for index in range(3):
        save(make_fir(index), f"tahuya_fir_{index + 1}.png")
    for index, colour in enumerate(LIGHT_COLOURS):
        save(make_light(colour), f"tahuya_mushroom_light_{index + 1}.png")
    save(make_firepit(), "tahuya_firepit.png")
    save(make_ufo(), "tahuya_ufo.png")
    save(make_shed(), "tahuya_firewood_shed.png")


if __name__ == "__main__":
    main()
