"""Generate the Cabin interior's human-scale procedural furnishings."""

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


def couch(width, *, olive=False):
    s = pygame.Surface((width, 43), pygame.SRCALPHA)
    outline = (45, 34, 24)
    fabric = (113, 101, 65) if olive else (130, 113, 77)
    light = (153, 136, 92) if not olive else (137, 126, 78)
    shadow = (79, 67, 45)
    # High upholstered back and lower seat give a readable three-quarter top.
    pygame.draw.rect(s, outline, (2, 3, width - 4, 36))
    pygame.draw.rect(s, fabric, (5, 5, width - 10, 18))
    pygame.draw.rect(s, shadow, (5, 23, width - 10, 12))
    pygame.draw.rect(s, light, (8, 20, width - 16, 11))
    pygame.draw.rect(s, outline, (1, 18, 9, 21))
    pygame.draw.rect(s, outline, (width - 10, 18, 9, 21))
    pygame.draw.line(s, (181, 157, 101), (7, 7), (width - 8, 7))
    for x in range(17, width - 8, 18):
        pygame.draw.line(s, shadow, (x, 21), (x, 31))
    pygame.draw.rect(s, (54, 39, 27), (8, 38, 5, 4))
    pygame.draw.rect(s, (54, 39, 27), (width - 13, 38, 5, 4))
    return s


def chair():
    s = pygame.Surface((36, 44), pygame.SRCALPHA)
    outline = (55, 37, 24)
    wood = (91, 57, 33)
    fabric = (153, 132, 72)
    light = (188, 160, 87)
    pygame.draw.rect(s, outline, (4, 2, 28, 35))
    pygame.draw.rect(s, fabric, (7, 4, 22, 17))
    pygame.draw.line(s, light, (8, 5), (27, 5))
    pygame.draw.rect(s, outline, (7, 22, 22, 14))
    pygame.draw.rect(s, fabric, (9, 23, 18, 10))
    pygame.draw.rect(s, wood, (1, 18, 7, 20))
    pygame.draw.rect(s, wood, (28, 18, 7, 20))
    pygame.draw.rect(s, outline, (6, 36, 5, 7))
    pygame.draw.rect(s, outline, (25, 36, 5, 7))
    return s


def table():
    s = pygame.Surface((90, 59), pygame.SRCALPHA)
    outline = (48, 31, 23)
    edge = (91, 54, 34)
    top = (124, 74, 44)
    pygame.draw.polygon(s, outline, ((4, 11), (83, 4), (88, 40), (9, 49)))
    pygame.draw.polygon(s, top, ((7, 12), (81, 7), (84, 36), (11, 44)))
    for x in range(15, 80, 13):
        pygame.draw.line(s, edge, (x, 11), (x + 3, 41))
    pygame.draw.line(s, (164, 104, 59), (10, 13), (79, 8), 2)
    # Five mustard stools along the north edge, as on Sean's plan.
    for x in (12, 27, 42, 57, 72):
        pygame.draw.ellipse(s, outline, (x, 0, 11, 8))
        pygame.draw.ellipse(s, (154, 132, 73), (x + 1, 1, 9, 5))
        pygame.draw.rect(s, edge, (x + 3, 5, 2, 8))
        pygame.draw.rect(s, edge, (x + 7, 5, 2, 8))
    pygame.draw.rect(s, outline, (14, 44, 5, 13))
    pygame.draw.rect(s, outline, (76, 39, 5, 13))
    return s


def kitchen():
    s = pygame.Surface((108, 48), pygame.SRCALPHA)
    outline = (43, 27, 22)
    cabinet = (77, 43, 31)
    light = (112, 67, 43)
    counter = (173, 162, 127)
    pygame.draw.rect(s, outline, (2, 10, 104, 36))
    pygame.draw.rect(s, cabinet, (5, 15, 98, 29))
    pygame.draw.rect(s, counter, (1, 7, 106, 10))
    pygame.draw.line(s, (221, 207, 164), (4, 8), (104, 8), 2)
    for x in (7, 35, 63, 91):
        pygame.draw.line(s, outline, (x, 17), (x, 43))
        pygame.draw.rect(s, light, (x + 10, 27, 2, 2))
    # Sink basin and simple faucet at the left.
    pygame.draw.rect(s, (77, 82, 79), (10, 8, 27, 7))
    pygame.draw.rect(s, (126, 132, 125), (12, 9, 23, 4))
    pygame.draw.line(s, (150, 153, 143), (23, 7), (23, 2), 2)
    pygame.draw.line(s, (150, 153, 143), (23, 2), (29, 2), 2)
    # The ordinary rectangular D&D map waits on the right-hand counter.
    pygame.draw.rect(s, (48, 34, 34), (61, 6, 35, 12))
    pygame.draw.rect(s, (197, 178, 128), (63, 7, 31, 9))
    pygame.draw.line(s, (77, 103, 82), (65, 13), (75, 8))
    pygame.draw.line(s, (111, 73, 61), (78, 8), (91, 14))
    pygame.draw.rect(s, (49, 87, 104), (72, 11, 3, 3))
    return s


def woodstove():
    s = pygame.Surface((50, 60), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (25, 23, 22), (19, 0, 13, 7))
    pygame.draw.rect(s, (31, 30, 29), (20, 3, 11, 28))
    pygame.draw.line(s, (68, 65, 59), (22, 4), (22, 28), 2)
    # Brick hearth under the stove echoes the reference photo.
    pygame.draw.polygon(s, (72, 44, 36), ((2, 42), (42, 36), (48, 53),
                                         (8, 59)))
    for y in (43, 50):
        pygame.draw.line(s, (125, 76, 55), (6, y), (45, y - 5))
    pygame.draw.rect(s, (24, 23, 22), (9, 25, 33, 25))
    pygame.draw.rect(s, (65, 61, 55), (12, 28, 27, 16))
    pygame.draw.rect(s, (15, 16, 16), (15, 31, 21, 11))
    pygame.draw.rect(s, (124, 78, 38), (18, 34, 15, 6))
    pygame.draw.rect(s, (30, 29, 27), (12, 48, 5, 8))
    pygame.draw.rect(s, (30, 29, 27), (34, 48, 5, 7))
    return s


def wood_storage():
    s = pygame.Surface((50, 45), pygame.SRCALPHA)
    pygame.draw.rect(s, (44, 29, 24), (3, 5, 44, 38))
    pygame.draw.rect(s, (76, 44, 31), (6, 8, 38, 32))
    for y in (10, 20, 30):
        for x in (8, 19, 30):
            pygame.draw.rect(s, (103, 61, 35), (x, y, 12, 7))
            pygame.draw.ellipse(s, (52, 34, 27), (x + 6, y, 6, 7))
    pygame.draw.line(s, (122, 79, 45), (7, 7), (43, 7))
    return s


def main():
    pygame.init()
    save(couch(106), "cabin_big_couch.png")
    save(couch(82, olive=True), "cabin_couch.png")
    save(chair(), "cabin_chair.png")
    save(table(), "cabin_table.png")
    save(kitchen(), "cabin_kitchen.png")
    save(woodstove(), "cabin_woodstove.png")
    save(wood_storage(), "cabin_wood_storage.png")


if __name__ == "__main__":
    main()
