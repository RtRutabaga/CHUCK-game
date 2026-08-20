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
    s = pygame.Surface((52, 44), pygame.SRCALPHA)
    # Broad stone ring and crossed logs make the landmark read from the cabin
    # porch.  The tall two-tone flame remains chunky at native resolution.
    stones = ((3, 33), (8, 27), (15, 24), (23, 23), (32, 24),
              (40, 28), (44, 34), (35, 37), (24, 38), (13, 37))
    for index, (x, y) in enumerate(stones):
        colour = (92, 91, 82) if index % 2 else (108, 104, 91)
        pygame.draw.ellipse(s, colour, (x, y, 9, 6))
        pygame.draw.line(s, (151, 143, 121), (x + 2, y + 1), (x + 6, y + 1))
    pygame.draw.line(s, (66, 38, 24), (12, 35), (40, 25), 5)
    pygame.draw.line(s, (91, 48, 25), (11, 25), (41, 36), 5)
    pygame.draw.polygon(s, (207, 55, 25),
                        ((18, 30), (22, 12), (27, 3), (30, 29)))
    pygame.draw.polygon(s, (240, 103, 30),
                        ((24, 31), (31, 10), (37, 29)))
    pygame.draw.polygon(s, (255, 201, 67),
                        ((25, 31), (29, 15), (33, 30)))
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
