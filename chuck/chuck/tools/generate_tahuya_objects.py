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


CABIN_SCALE = 1.4                      # how much bigger than the first draft
CABIN_BASE = (264, 188)             # the geometry below is written at 1x
CABIN_SIZE = (round(CABIN_BASE[0] * CABIN_SCALE),
              round(CABIN_BASE[1] * CABIN_SCALE))
# Where the porch deck meets the wall, as a fraction of the sprite's
# height measured up from its bottom edge. The cabin sorts against this
# line rather than against its own feet, so Chuck stays visible the
# whole way across the deck instead of disappearing behind it.
CABIN_DECK_BACK = 1.0 - 132 / CABIN_BASE[1]


def make_cabin():
    """The Tahuya cabin: a gable-roofed landmark in three-quarter view.

    Built to the reference photograph rather than to the tile grid. The
    near end is the gable, because that is the face the door and the
    covered porch are on, and it is what makes the building read as a
    cabin rather than as a shed: a peak, two roof slopes, and a triangle
    of siding under them.

    The geometry is written at a base size and multiplied on the way to
    the canvas, so the whole building can be resized by one number
    without the roof, the eaves and the porch falling out of agreement.
    """
    scale = CABIN_SCALE
    s = pygame.Surface(CABIN_SIZE, pygame.SRCALPHA)

    def pt(x, y):
        return (round(x * scale), round(y * scale))

    def poly(points):
        return [pt(x, y) for x, y in points]

    def wide(width):
        return max(1, round(width * scale))

    outline = (14, 18, 22)
    siding = (74, 100, 118)
    siding_light = (98, 124, 142)
    siding_dark = (54, 74, 90)
    side_wall = (56, 78, 94)
    side_line = (42, 60, 74)
    gable_face = (66, 90, 108)
    shingle = (52, 52, 46)
    shingle_dark = (38, 38, 34)
    moss = (100, 114, 58)
    moss_light = (126, 140, 74)
    ridge_cap = (78, 78, 68)
    wood = (104, 74, 48)
    wood_light = (138, 100, 64)
    wood_dark = (70, 48, 32)
    door = (88, 60, 40)
    door_dark = (58, 38, 26)
    frame = (96, 66, 44)
    glass = (34, 44, 52)
    glass_lit = (58, 74, 84)
    pier = (128, 128, 118)
    pier_dark = (78, 78, 72)
    grass = (60, 90, 48)
    grass_light = (84, 118, 60)

    def filled(points, colour):
        shape = poly(points)
        pygame.draw.polygon(s, outline, shape)
        pygame.draw.polygon(s, colour, shape)
        pygame.draw.polygon(s, outline, shape, wide(1))

    def stroke(colour, a, b, width=1):
        pygame.draw.line(s, colour, pt(*a), pt(*b), wide(width))

    def box(colour, x, y, w, h):
        pygame.draw.rect(s, colour, (*pt(x, y), wide(w), wide(h)))

    # ---- the frame the whole building is measured from -----------------
    near = (150, 172)                          # corner nearest the camera
    left_b, left_t = (58, 142), (58, 78)       # gable end, away to the left
    near_t = (150, 108)
    right_b, right_t = (234, 140), (234, 76)   # long side, away to the right
    peak = (104, 58)

    # ---- piers: the cabin stands off the ground on posts ---------------
    for x, y in ((66, 140), (104, 152), (146, 168), (190, 152), (226, 138)):
        box(outline, x - 1, y - 1, 9, 22)
        box(pier, x, y, 7, 20)
        box(pier_dark, x + 4, y, 3, 20)

    # ---- walls ---------------------------------------------------------
    # The long side, in shade because the light is on the gable end.
    filled((near_t, right_t, right_b, near), side_wall)
    for step in range(1, 10):
        x = near_t[0] + step * 11
        top = near_t[1] - step * 4.2
        stroke(side_line, (x, top), (x, top + 63))

    # The gable end: wall, and the triangle of siding above it.
    filled((left_t, near_t, near, left_b), siding)
    filled((left_t, peak, near_t), gable_face)
    for step in range(1, 9):
        x = left_t[0] + step * 10
        top = left_t[1] + step * 3.3
        stroke(siding_light, (x, top), (x, top + 63))
    stroke(siding_dark, left_t, near_t, 2)

    # ---- roof ----------------------------------------------------------
    # A sliver of the far slope shows above the ridge.
    filled(((92, 50), (198, 22), (190, 18), (84, 46)), shingle_dark)
    # The big slope facing the camera, which is the one carrying the moss.
    filled(((92, 50), (198, 22), (256, 82), (162, 118)), shingle)
    for step in range(1, 7):
        offset = step * 9.8
        stroke(shingle_dark, (92 + step * 11.7, 50 + offset),
               (198 + step * 9.7, 22 + offset))
    # Moss is a mat, not a crop of toadstools: short flat runs lying along
    # the courses, thickest up near the ridge where the rain sits longest.
    for index in range(1100):
        along = (index * 37 % 101) / 100.0
        down = (index * 61 % 97) / 96.0
        down = down * down          # crowd it toward the ridge
        clump = (round(along * 9) * 13 + round(down * 7) * 29) % 11
        if clump > 6:
            continue
        x = 92 + along * 106 + down * 64
        y = 50 - along * 28 + down * 62
        run = (2 + (index % 5)) / scale
        stroke(moss if index % 3 else moss_light, (x, y), (x + run, y))
    # Ridge cap, eaves fascia, and the barge board down the near gable.
    stroke(ridge_cap, (92, 50), (198, 22), 3)
    stroke(outline, (92, 50), (198, 22), 1)
    stroke((86, 86, 76), (162, 118), (256, 82), 3)
    stroke(outline, (162, 118), (256, 82), 1)
    stroke((92, 92, 82), (92, 50), (40, 92), 4)
    stroke(outline, (92, 50), (40, 92), 1)
    stroke((92, 92, 82), (92, 50), (162, 118), 4)
    stroke(outline, (92, 50), (162, 118), 1)

    # ---- porch: its own small gable on two posts ------------------------
    filled(((14, 150), (66, 166), (120, 148), (68, 132)), wood)
    for step in range(1, 6):
        stroke(wood_dark, (14 + step * 9, 150 - step * 3),
               (66 + step * 9, 166 - step * 3))
    for x, y in ((14, 96), (66, 112)):
        box(outline, x - 1, y - 1, 8, 58)
        box(wood, x, y, 6, 56)
        box(wood_light, x, y, 2, 56)
    stroke(wood_light, (17, 122), (69, 138), 3)
    stroke(outline, (17, 122), (69, 138), 1)
    for step in range(7):
        x = 18 + step * 7
        y = 124 + step * 2
        stroke(wood, (x, y), (x, y + 24), 2)
        stroke(wood_dark, (x + 1, y), (x + 1, y + 24), 1)
    filled(((30, 52), (82, 68), (88, 76), (36, 60)), shingle_dark)
    filled(((6, 92), (58, 108), (86, 74), (34, 58)), shingle)
    for step in range(1, 4):
        offset = step * 8
        stroke(shingle_dark, (34 - step * 7, 58 + offset),
               (86 - step * 7, 74 + offset))
    stroke(ridge_cap, (34, 58), (86, 74), 3)
    stroke((92, 92, 82), (6, 92), (58, 108), 3)
    stroke(outline, (6, 92), (58, 108), 1)
    stroke(outline, (34, 58), (86, 74), 1)

    # Steps down off the deck toward the viewer, in front of the door
    # rather than off the far end -- they have to land on the tiles the
    # map already authored as the way up onto the porch.
    for tread in range(4):
        dx, dy = 4 * tread, 5 * tread
        top = ((66 + dx, 166 + dy), (120 + dx, 148 + dy),
               (124 + dx, 153 + dy), (70 + dx, 171 + dy))
        shape = poly(top)
        pygame.draw.polygon(s, outline, shape)
        pygame.draw.polygon(s, wood if tread % 2 else wood_light, shape)
        stroke(wood_dark, (66 + dx, 167 + dy), (120 + dx, 149 + dy), 2)

    # ---- the door, its lamp, and the windows ---------------------------
    # Wide enough to walk into without lining up on it: this is a door in
    # a cabin, not a gap in a wall Chuck has to thread.
    filled(((72, 90), (106, 101), (106, 150), (72, 139)), door)
    pygame.draw.polygon(s, door_dark, poly(((77, 97), (101, 105),
                                            (101, 143), (77, 135))))
    box(glass_lit, 82, 104, 14, 12)
    pygame.draw.circle(s, (188, 152, 96), pt(103, 126), wide(1))
    # The lamp beside it: the one warm thing on the whole building.
    for radius, alpha in ((12, 40), (8, 64)):
        span = wide(radius)
        glow = pygame.Surface((span * 2, span * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 214, 130, alpha), (span, span), span)
        s.blit(glow, (pt(66, 94)[0] - span, pt(66, 94)[1] - span))
    pygame.draw.circle(s, (120, 92, 52), pt(66, 94), wide(4))
    pygame.draw.circle(s, (255, 214, 130), pt(66, 94), wide(3))
    pygame.draw.circle(s, (255, 244, 200), pt(66, 93), wide(1))

    def window(points, panes_x, panes_y):
        filled(points, frame)
        inset = ((3, 2), (-3, 3), (-3, -2), (3, -3))
        inner = [(x + dx, y + dy)
                 for (x, y), (dx, dy) in zip(points, inset)]
        pygame.draw.polygon(s, glass, poly(inner))
        left, right, bottom, top = inner
        for step in range(1, panes_x):
            t = step / panes_x
            stroke(frame,
                   (left[0] + (right[0] - left[0]) * t,
                    left[1] + (right[1] - left[1]) * t),
                   (top[0] + (bottom[0] - top[0]) * t,
                    top[1] + (bottom[1] - top[1]) * t))
        for step in range(1, panes_y):
            t = step / panes_y
            stroke(frame,
                   (left[0] + (top[0] - left[0]) * t,
                    left[1] + (top[1] - left[1]) * t),
                   (right[0] + (bottom[0] - right[0]) * t,
                    right[1] + (bottom[1] - right[1]) * t))

    # One on the gable end, right of the door; one on the long side.
    window(((114, 105), (138, 112), (138, 138), (114, 131)), 2, 2)
    window(((176, 108), (222, 90), (222, 120), (176, 138)), 3, 2)

    # ---- grass tufts round the base ------------------------------------
    for x, y in ((100, 176), (134, 184), (170, 174),
                 (200, 162), (226, 152), (238, 146), (150, 180)):
        for blade in range(4):
            bx = x + blade * 3 - 4
            height = 5 + (blade % 3) * 3
            stroke(grass, (bx, y), (bx + 1, y - height))
            if blade % 2:
                stroke(grass_light, (bx, y - 1), (bx + 1, y - height + 1))
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
