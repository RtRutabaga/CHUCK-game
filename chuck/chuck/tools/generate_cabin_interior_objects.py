"""Generate the Cabin interior's human-scale procedural furnishings."""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


ROOT = Path(__file__).resolve().parents[1]
OBJECTS = ROOT / "assets" / "sprites" / "objects"
PORTAL_COLOURS = (
    (205, 175, 190),
    (162, 150, 185),
    (120, 145, 171),
    (137, 164, 167),
    (145, 166, 151),
    (184, 174, 140),
    (194, 157, 132),
    (162, 151, 169),
)


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


def table(portal_frame=None):
    # Eleven tiles wide at its authored col-6 anchor: the visible tabletop
    # meets the west wall while leaving a four-tile circulation lane east.
    s = pygame.Surface((176, 57), pygame.SRCALPHA)
    outline = (48, 31, 23)
    edge = (91, 54, 34)
    top = (124, 74, 44)
    pygame.draw.polygon(s, outline, ((2, 10), (169, 3), (174, 39), (7, 48)))
    pygame.draw.polygon(s, top, ((5, 11), (167, 6), (170, 35), (9, 43)))
    for x in range(13, 166, 13):
        pygame.draw.line(s, edge, (x, 11), (x + 3, 41))
    pygame.draw.line(s, (164, 104, 59), (8, 13), (165, 8), 2)
    # Five mustard stools along the north edge, as on Sean's plan.
    for x in (18, 50, 82, 114, 146):
        pygame.draw.ellipse(s, outline, (x, 0, 11, 8))
        pygame.draw.ellipse(s, (154, 132, 73), (x + 1, 1, 9, 5))
        pygame.draw.rect(s, edge, (x + 3, 5, 2, 8))
        pygame.draw.rect(s, edge, (x + 7, 5, 2, 8))
    pygame.draw.rect(s, outline, (12, 43, 5, 13))
    pygame.draw.rect(s, outline, (159, 38, 5, 13))
    # The rectangular D&D map belongs to this table, not the sink counter.
    pygame.draw.rect(s, (48, 34, 34), (29, 17, 47, 17))
    if portal_frame is None:
        pygame.draw.polygon(s, (197, 178, 128),
                            ((31, 18), (72, 16), (74, 31), (33, 33)))
        pygame.draw.line(s, (77, 103, 82), (35, 29), (47, 18))
        pygame.draw.line(s, (111, 73, 61), (52, 18), (69, 29))
        pygame.draw.rect(s, (49, 87, 104), (46, 25, 4, 4))
    else:
        colour = PORTAL_COLOURS[portal_frame]
        glow = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (*colour, 30), (21, 8, 65, 35))
        s.blit(glow, (0, 0))
        pygame.draw.polygon(s, (81, 76, 85),
                            ((31, 18), (72, 16), (74, 31), (33, 33)))
        for x in range(32, 74):
            wave = (x + portal_frame * 4 + (x // 5) * 2) % 16
            band = PORTAL_COLOURS[(portal_frame + wave // 3) % 8]
            top = 18 + ((x + portal_frame) % 3)
            pygame.draw.line(s, band, (x, top), (x + 1, 31))
        pygame.draw.polygon(s, (198, 194, 198),
                            ((31, 18), (72, 16), (74, 31), (33, 33)), 1)
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
    return s


def woodstove(frame=0):
    s = pygame.Surface((72, 82), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (25, 23, 22), (28, 0, 17, 8))
    pygame.draw.rect(s, (31, 30, 29), (29, 4, 15, 37))
    pygame.draw.line(s, (68, 65, 59), (32, 5), (32, 38), 2)
    # Brick hearth under the stove echoes the reference photo.
    pygame.draw.polygon(s, (72, 44, 36), ((3, 59), (61, 50), (69, 72),
                                         (11, 81)))
    for y in (60, 70):
        pygame.draw.line(s, (125, 76, 55), (8, y), (65, y - 8))
    pygame.draw.rect(s, (24, 23, 22), (13, 34, 47, 35))
    pygame.draw.rect(s, (65, 61, 55), (17, 38, 39, 23))
    pygame.draw.rect(s, (15, 16, 16), (21, 42, 31, 15))
    sway = (-2, 0, 2, 3, 1, -2)[frame % 6]
    pygame.draw.polygon(s, (210, 57, 24),
                        ((24, 56), (29 + sway, 44), (36, 55)))
    pygame.draw.polygon(s, (247, 126, 35),
                        ((31, 56), (39 - sway, 42), (49, 56)))
    pygame.draw.polygon(s, (255, 209, 74),
                        ((35, 56), (39 + sway // 2, 47), (44, 56)))
    pygame.draw.rect(s, (30, 29, 27), (18, 67, 6, 10))
    pygame.draw.rect(s, (30, 29, 27), (49, 67, 6, 9))
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
    for index in range(len(PORTAL_COLOURS)):
        save(table(index), f"cabin_table_awakened_{index + 1}.png")
    save(kitchen(), "cabin_kitchen.png")
    for index in range(6):
        save(woodstove(index), f"cabin_woodstove_{index + 1}.png")
    save(wood_storage(), "cabin_wood_storage.png")


if __name__ == "__main__":
    main()
