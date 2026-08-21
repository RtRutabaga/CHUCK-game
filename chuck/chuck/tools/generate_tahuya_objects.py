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


def make_firepit(frame=0):
    s = pygame.Surface((64, 56), pygame.SRCALPHA)
    # Broad stone ring and crossed logs make the landmark read from the cabin
    # porch.  The tall two-tone flame remains chunky at native resolution.
    stones = ((5, 43), (10, 35), (18, 31), (28, 29), (39, 31),
              (49, 36), (53, 44), (43, 49), (31, 51), (17, 49))
    for index, (x, y) in enumerate(stones):
        colour = (92, 91, 82) if index % 2 else (108, 104, 91)
        pygame.draw.ellipse(s, colour, (x, y, 11, 7))
        pygame.draw.line(s, (151, 143, 121), (x + 2, y + 1), (x + 8, y + 1))
    pygame.draw.line(s, (66, 38, 24), (15, 46), (49, 32), 6)
    pygame.draw.line(s, (91, 48, 25), (14, 33), (50, 47), 6)
    sway = (-3, -1, 2, 3, 1, -2)[frame % 6]
    pygame.draw.polygon(s, (207, 55, 25),
                        ((21, 41), (25 + sway, 15), (32 + sway, 3),
                         (37, 40)))
    pygame.draw.polygon(s, (240, 103, 30),
                        ((28, 42), (35 - sway, 13), (44, 40)))
    pygame.draw.polygon(s, (255, 201, 67),
                        ((30, 42), (34 + sway // 2, 21), (40, 41)))
    return s


def make_ufo():
    s = pygame.Surface((132, 76), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (16, 20, 24), (8, 38, 116, 30))
    pygame.draw.ellipse(s, (81, 91, 96), (2, 24, 128, 34))
    pygame.draw.ellipse(s, (124, 137, 137), (18, 14, 96, 32))
    pygame.draw.ellipse(s, (38, 45, 52), (44, 4, 44, 26))
    pygame.draw.ellipse(s, (84, 105, 116), (50, 6, 32, 16))
    for x, colour in ((24, (78, 224, 215)), (54, (229, 89, 207)),
                      (86, (246, 179, 72)), (110, (103, 138, 241))):
        pygame.draw.rect(s, colour, (x, 44, 6, 4))
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


def make_cabin():
    """Compact three-quarter-view cabin, authored as one readable landmark."""
    s = pygame.Surface((208, 150), pygame.SRCALPHA)
    outline = (12, 18, 18)
    siding_dark = (39, 61, 66)
    siding = (55, 82, 88)
    siding_light = (77, 101, 103)
    wood = (94, 61, 39)
    wood_light = (137, 87, 49)
    roof_dark = (31, 34, 25)
    roof = (48, 51, 31)
    moss = (63, 69, 36)

    # Raised posts and the two visible wall planes.
    for x, y in ((30, 104), (92, 124), (120, 127), (180, 101)):
        pygame.draw.rect(s, outline, (x, y, 7, 28))
        pygame.draw.rect(s, (63, 49, 37), (x + 2, y, 3, 24))
    front = ((24, 55), (105, 76), (105, 125), (24, 105))
    side = ((105, 76), (184, 45), (184, 101), (105, 132))
    pygame.draw.polygon(s, outline, front)
    pygame.draw.polygon(s, outline, side)
    pygame.draw.polygon(s, siding, ((28, 59), (101, 78),
                                    (101, 120), (28, 102)))
    pygame.draw.polygon(s, siding_dark, ((109, 79), (180, 51),
                                         (180, 98), (109, 126)))
    for x in range(34, 99, 9):
        pygame.draw.line(s, siding_light, (x, 61), (x, 114), 1)
    for x in range(116, 179, 10):
        pygame.draw.line(s, (49, 72, 76), (x, 75), (x, 121), 1)

    # Moss-darkened shallow roof with a strong diagonal ridge and eaves.
    pygame.draw.polygon(s, outline, ((11, 53), (73, 6), (197, 39),
                                     (106, 83)))
    pygame.draw.polygon(s, roof, ((17, 51), (76, 11), (190, 41),
                                  (105, 77)))
    pygame.draw.polygon(s, roof_dark, ((76, 11), (190, 41),
                                       (181, 48), (74, 20)))
    for step in range(5):
        y = 26 + step * 9
        pygame.draw.line(s, moss, (28 + step * 10, y),
                         (168 + step * 3, y + 16), 3)
        pygame.draw.line(s, (73, 65, 35), (31 + step * 10, y + 2),
                         (165 + step * 3, y + 18), 1)
    pygame.draw.line(s, (89, 87, 64), (14, 53), (105, 81), 3)
    pygame.draw.line(s, (89, 87, 64), (105, 81), (194, 40), 3)

    # South-facing door, warm porch lamp, and one side window.
    pygame.draw.polygon(s, outline, ((50, 66), (70, 71), (70, 111),
                                     (50, 106)))
    pygame.draw.polygon(s, (35, 48, 52), ((54, 70), (67, 73),
                                         (67, 106), (54, 103)))
    pygame.draw.circle(s, (232, 175, 65), (48, 76), 3)
    pygame.draw.circle(s, (255, 211, 95), (48, 76), 1)
    pygame.draw.polygon(s, outline, ((134, 70), (166, 58), (166, 78),
                                     (134, 90)))
    pygame.draw.polygon(s, (20, 31, 34), ((138, 71), (162, 63),
                                         (162, 76), (138, 85)))
    pygame.draw.line(s, siding_light, (150, 67), (150, 81), 2)

    # Compact raised porch and broad stairs toward the player/south.
    pygame.draw.polygon(s, outline, ((23, 105), (77, 118), (106, 108),
                                     (50, 96)))
    pygame.draw.polygon(s, wood, ((28, 104), (76, 115), (100, 107),
                                  (51, 99)))
    for y, left, right in ((116, 48, 84), (125, 43, 87),
                           (135, 38, 91), (145, 33, 95)):
        pygame.draw.polygon(s, outline, ((left, y - 5), (right, y + 2),
                                         (right - 4, y + 7),
                                         (left - 4, y)))
        pygame.draw.line(s, wood_light, (left, y - 4), (right - 1, y + 2), 3)
    return s


def main():
    pygame.init()
    for index in range(3):
        save(make_fir(index), f"tahuya_fir_{index + 1}.png")
    for index, colour in enumerate(LIGHT_COLOURS):
        save(make_light(colour), f"tahuya_mushroom_light_{index + 1}.png")
    for index in range(6):
        save(make_firepit(index), f"tahuya_firepit_{index + 1}.png")
    save(make_ufo(), "tahuya_ufo.png")
    save(make_shed(), "tahuya_firewood_shed.png")
    save(make_cabin(), "tahuya_cabin.png")


if __name__ == "__main__":
    main()
