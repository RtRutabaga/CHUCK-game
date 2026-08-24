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
EGGSHELL = (220, 214, 187)
EGGSHELL_LIGHT = (242, 237, 211)
EGGSHELL_SHADOW = (174, 164, 137)


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
    # Nine tiles wide at its authored col-5 anchor: the visible tabletop still
    # meets the west wall while stopping short of the room's eastern fixtures.
    s = pygame.Surface((144, 57), pygame.SRCALPHA)
    outline = (48, 31, 23)
    edge = EGGSHELL_SHADOW
    top = EGGSHELL
    pygame.draw.polygon(s, outline, ((2, 10), (137, 3), (142, 39), (7, 48)))
    pygame.draw.polygon(s, top, ((5, 11), (135, 6), (138, 35), (9, 43)))
    for x in range(13, 134, 13):
        pygame.draw.line(s, edge, (x, 11), (x + 3, 41))
    pygame.draw.line(s, EGGSHELL_LIGHT, (8, 13), (133, 8), 2)
    # Five mustard stools along the north edge, as on Sean's plan.
    for x in (14, 42, 70, 98, 126):
        pygame.draw.ellipse(s, outline, (x, 0, 11, 8))
        pygame.draw.ellipse(s, (154, 132, 73), (x + 1, 1, 9, 5))
        pygame.draw.rect(s, edge, (x + 3, 5, 2, 8))
        pygame.draw.rect(s, edge, (x + 7, 5, 2, 8))
    pygame.draw.rect(s, outline, (12, 43, 5, 13))
    pygame.draw.rect(s, outline, (127, 38, 5, 13))
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


# How many rows of west wall the counter runs down. This has to match
# the hardwood room's depth in generate_tahuya_cabin_interior, because
# the counter runs the whole side of it: shortening the room without
# shortening this left the cabinet standing up through the carpet and
# across the map table.
CONNECTOR_SHELF_TILES = 6
CONNECTOR_SHELF_SIZE = (48, CONNECTOR_SHELF_TILES * 16)


def connector_shelf():
    """West-wall counter joining the table to the southern sink run."""
    width, height = CONNECTOR_SHELF_SIZE
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    outline = (48, 31, 23)
    cabinet = (77, 43, 31)
    cabinet_light = (112, 67, 43)
    bottom = height - 1
    # The dark cabinet face remains visible along the room-facing east edge;
    # the broad eggshell worktop is deliberately clear of assorted clutter.
    pygame.draw.polygon(s, outline,
                        ((3, 0), (42, 0), (47, bottom - 5), (4, bottom)))
    pygame.draw.polygon(s, cabinet,
                        ((6, 4), (40, 4), (43, bottom - 7), (7, bottom - 3)))
    pygame.draw.polygon(s, EGGSHELL,
                        ((9, 1), (39, 1), (41, bottom - 11), (9, bottom - 6)))
    pygame.draw.line(s, EGGSHELL_LIGHT, (11, 3), (38, 3), 2)
    pygame.draw.line(s, EGGSHELL_LIGHT, (11, 4), (11, bottom - 9), 2)
    pygame.draw.line(s, EGGSHELL_SHADOW, (40, 5), (42, bottom - 8), 2)
    for y in range(24, height - 16, 24):
        pygame.draw.line(s, cabinet_light, (7, y), (42, y + 1))
        pygame.draw.circle(s, outline, (37, y + 12), 1)
    return s


def mini_fridge():
    """A black mini fridge. The handles are the light thing on it now.

    White, it was the brightest object in a dark olive room and pulled
    the eye off the table it stands beside.
    """
    s = pygame.Surface((32, 42), pygame.SRCALPHA)
    outline = (12, 13, 16)
    body = (44, 46, 52)
    shadow = (28, 30, 35)
    sheen = (70, 74, 82)
    handle = (150, 154, 160)
    pygame.draw.rect(s, outline, (2, 2, 28, 38))
    pygame.draw.rect(s, body, (5, 4, 22, 33))
    # One soft highlight down the left edge, which is all the shape a
    # black box gets before it stops reading as black.
    pygame.draw.line(s, sheen, (6, 5), (6, 35))
    pygame.draw.line(s, shadow, (5, 14), (27, 14), 2)
    pygame.draw.rect(s, handle, (23, 6, 2, 6))
    pygame.draw.rect(s, handle, (23, 18, 2, 11))
    pygame.draw.rect(s, shadow, (6, 36, 20, 2))
    return s


def closed_door_west():
    s = pygame.Surface((24, 48), pygame.SRCALPHA)
    outline = (38, 24, 20)
    wood = (91, 53, 37)
    panel = (119, 70, 45)
    pygame.draw.rect(s, outline, (2, 1, 20, 46))
    pygame.draw.rect(s, wood, (5, 3, 14, 42))
    pygame.draw.rect(s, panel, (7, 6, 10, 15))
    pygame.draw.rect(s, panel, (7, 25, 10, 16))
    pygame.draw.circle(s, (185, 151, 72), (7, 23), 2)
    pygame.draw.line(s, (151, 91, 56), (18, 4), (18, 44), 1)
    return s


def kitchen():
    s = pygame.Surface((108, 48), pygame.SRCALPHA)
    outline = (43, 27, 22)
    cabinet = (77, 43, 31)
    light = (112, 67, 43)
    counter = EGGSHELL
    pygame.draw.rect(s, outline, (2, 10, 104, 36))
    pygame.draw.rect(s, cabinet, (5, 15, 98, 29))
    pygame.draw.rect(s, counter, (1, 7, 106, 10))
    pygame.draw.line(s, EGGSHELL_LIGHT, (4, 8), (104, 8), 2)
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


LAVA_GLASS = (250, 196, 118)
LAVA_GLASS_DEEP = (232, 152, 78)
LAVA_BLOB = (226, 62, 74)
LAVA_BLOB_LIGHT = (247, 116, 96)
CHROME = (188, 192, 198)
CHROME_LIGHT = (232, 236, 240)
CHROME_DARK = (108, 114, 124)
TABLE_BLUE = (156, 186, 206)
TABLE_BLUE_LIGHT = (196, 218, 232)
TABLE_BLUE_DARK = (104, 132, 152)


def lava_lamp(frame=0):
    """A lava lamp on a small pale blue side table.

    The lamp is drawn as one prop with the table it stands on, because
    at this scale they are a single silhouette: a chrome cone, a taper
    of lit amber glass with blobs drifting through it, and a chrome cap.
    The blobs rise and fall on their own cycles, so the six frames never
    line up into a pulse.
    """
    s = pygame.Surface((34, 58), pygame.SRCALPHA)
    outline = (28, 34, 40)

    # ---- the table ----------------------------------------------------
    pygame.draw.rect(s, outline, (2, 40, 30, 8))
    pygame.draw.rect(s, TABLE_BLUE, (3, 41, 28, 6))
    pygame.draw.line(s, TABLE_BLUE_LIGHT, (4, 41), (30, 41))
    pygame.draw.line(s, TABLE_BLUE_DARK, (4, 46), (30, 46))
    for x in (5, 26):
        pygame.draw.rect(s, outline, (x, 47, 4, 10))
        pygame.draw.rect(s, TABLE_BLUE_DARK, (x + 1, 47, 2, 9))

    # ---- the lamp -----------------------------------------------------
    # Chrome cone below, chrome cap above, glass between them.
    pygame.draw.polygon(s, outline, ((11, 40), (23, 40), (19, 31), (15, 31)))
    pygame.draw.polygon(s, CHROME_DARK,
                        ((12, 39), (22, 39), (18, 32), (16, 32)))
    pygame.draw.polygon(s, CHROME,
                        ((13, 39), (20, 39), (18, 32), (16, 32)))
    pygame.draw.line(s, CHROME_LIGHT, (15, 38), (16, 32), 1)
    pygame.draw.line(s, CHROME_LIGHT, (12, 39), (22, 39))

    glass = ((14, 32), (20, 32), (21, 20), (19, 9), (15, 9), (13, 20))
    pygame.draw.polygon(s, outline, glass)
    pygame.draw.polygon(s, LAVA_GLASS_DEEP,
                        ((15, 31), (19, 31), (20, 20), (18, 10),
                         (16, 10), (14, 20)))
    # The lit column: brighter up the middle, like a bulb below it.
    pygame.draw.polygon(s, LAVA_GLASS,
                        ((16, 30), (18, 30), (19, 20), (18, 11),
                         (16, 11), (15, 20)))

    # Blobs, each on its own slow cycle so the lamp never seems to beat.
    for index, (span, size, phase) in enumerate(
        ((16, 4, 0), (13, 3, 2), (10, 3, 4), (18, 5, 3))
    ):
        step = (frame + phase) % 6 / 6.0
        y = 29 - round(span * abs(2.0 * step - 1.0))
        x = 17 + ((index % 2) * 2 - 1) * (1 if index < 2 else 0)
        pygame.draw.ellipse(s, LAVA_BLOB,
                            (x - size // 2, y - size // 2, size, size))
        pygame.draw.ellipse(s, LAVA_BLOB_LIGHT,
                            (x - size // 2, y - size // 2, size - 1, size - 2))

    pygame.draw.rect(s, outline, (14, 6, 6, 4))
    pygame.draw.rect(s, CHROME, (15, 7, 4, 3))
    pygame.draw.line(s, CHROME_LIGHT, (15, 7), (18, 7))

    # No painted spill on the table top: with the room lit normally it
    # read as a stain, and when the room goes dark the projector scene
    # gives the lamp a real pool of its own.
    return s


def curtain_window(index=0):
    """A window with the curtains drawn across it.

    Mostly curtain: the whole point is that it is closed, so the glass
    is a sliver at each edge and everything else is cloth hanging in
    folds, with a pelmet across the top.
    """
    # Exactly two tiles tall: hung a row above the couch it sits behind,
    # a taller sprite than this has its pelmet clipped off by the top of
    # the map, which is the one part of it that always shows.
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    outline = (34, 24, 20)
    frame_wood = (96, 64, 42)
    frame_light = (130, 92, 58)
    night = (18, 26, 34)
    cloth = ((168, 142, 110), (194, 170, 138), (138, 114, 88))

    pygame.draw.rect(s, outline, (1, 2, 30, 29))
    pygame.draw.rect(s, frame_wood, (2, 3, 28, 27))
    pygame.draw.rect(s, night, (5, 7, 22, 21))
    # Curtains meeting in the middle, hem to hem. They have to overlap:
    # drawn to meet exactly, the seam between them plus each hem line
    # left a dark band up the middle that read as curtains parted.
    for side in (0, 1):
        left = 5 + side * 11
        for fold in range(6):
            x = left + fold * 2
            shade = cloth[(fold + side + index) % 3]
            pygame.draw.rect(s, shade, (x, 7, 2, 21))
    pygame.draw.line(s, outline, (16, 7), (16, 27))
    # The pelmet, and the sill under it.
    pygame.draw.rect(s, outline, (0, 0, 32, 6))
    pygame.draw.rect(s, cloth[1], (1, 1, 30, 4))
    pygame.draw.line(s, cloth[0], (1, 4), (30, 4))
    pygame.draw.line(s, frame_light, (2, 29), (29, 29))
    return s


def closed_door_north():
    """A panelled door in the north wall, shut.

    Drawn face-on rather than in three-quarter, because it is set in the
    wall the camera looks straight at. It matches the west door's timber
    so the two read as the same house.
    """
    s = pygame.Surface((28, 46), pygame.SRCALPHA)
    outline = (30, 20, 16)
    jamb = (86, 58, 38)
    door_wood = (112, 74, 46)
    door_dark = (78, 50, 32)
    door_light = (140, 96, 60)

    pygame.draw.rect(s, outline, (0, 0, 28, 46))
    pygame.draw.rect(s, jamb, (1, 1, 26, 45))
    pygame.draw.rect(s, outline, (4, 3, 20, 43))
    pygame.draw.rect(s, door_wood, (5, 4, 18, 42))
    for top in (7, 26):
        pygame.draw.rect(s, door_dark, (8, top, 12, 16))
        pygame.draw.rect(s, door_wood, (9, top + 1, 10, 14))
        pygame.draw.line(s, door_light, (9, top + 1), (18, top + 1))
    pygame.draw.line(s, door_light, (5, 4), (5, 45))
    pygame.draw.circle(s, (198, 168, 96), (20, 25), 1)
    return s


def macrame():
    """The knotted wall hanging from the real cabin.

    Two weathered sticks with jute worked between them: a block of
    square knots hanging off the top one, twisted spirals sweeping down
    from its ends and *inward* to meet at a point, then a lower stick
    with a cut tassel under it.

    The spirals have to close inward. Fanned outward -- which is the
    obvious way to draw a V -- the silhouette came out as a round body
    with two antennae and a fringe of legs, and read as a beetle on the
    wall rather than as anything hanging on it.
    """
    s = pygame.Surface((30, 42), pygame.SRCALPHA)
    bark = (92, 66, 44)
    bark_light = (128, 96, 62)
    bark_dark = (58, 40, 26)
    jute = (176, 138, 92)
    jute_light = (206, 172, 122)
    jute_dark = (132, 100, 62)

    def stick(y, left, right):
        pygame.draw.line(s, bark_dark, (left, y + 1), (right, y + 1), 3)
        pygame.draw.line(s, bark, (left, y), (right, y), 2)
        pygame.draw.line(s, bark_light, (left + 2, y - 1), (right - 3, y - 1))
        # Stubs where a twig was broken off: these are branches, not dowel.
        s.set_at((left, y - 1), bark_dark)
        s.set_at((right, y + 2), bark_dark)

    stick(3, 1, 28)

    # Twisted cords from the ends of the top stick, sweeping down and in
    # to meet at a point. Alternating light and dark reads as the twist.
    for side in (-1, 1):
        for step in range(16):
            t = step / 15.0
            x = round(15 + side * 13 * (1.0 - t * t))
            y = 5 + round(t * 22)
            shade = jute_light if (step + (side > 0)) % 2 else jute_dark
            pygame.draw.line(s, shade, (x, y), (x - side, y + 1), 2)

    # The square-knot panel, hanging straight off the top stick.
    for row in range(6):
        y = 6 + row * 3
        width = 13 - abs(row - 2)
        left = 15 - width // 2
        pygame.draw.rect(s, jute, (left, y, width, 2))
        pygame.draw.line(s, jute_light, (left, y), (left + width - 1, y))
        for notch in range(left + 2, left + width - 1, 4):
            s.set_at((notch, y + 1), jute_dark)

    stick(30, 6, 24)

    # The tassel: cut ends hanging below the lower stick.
    for index in range(9):
        x = 8 + index * 2
        drop = 5 + (index * 5 % 5)
        shade = jute if index % 2 else jute_dark
        pygame.draw.line(s, shade, (x, 32), (x, 32 + drop))
    return s


def goose_mount():
    """A Canada goose head mounted on the cabin's west wall.

    Laid on its side: the plaque flat against the wall on the left, the
    neck running out horizontally, the head and bill over the room on
    the right. That is what a mount on a side wall looks like from this
    camera. Stood upright -- plaque under the bird, neck rising -- it
    read as a decoy on the floor in front of the wall, however small it
    was drawn.
    """
    # Eight columns of empty canvas on the right. Props are centred on
    # their tile, so the padding is what pushes the plaque left onto the
    # wall itself rather than leaving it hanging half over the carpet.
    s = pygame.Surface((38, 22), pygame.SRCALPHA)
    outline = (40, 28, 18)
    plaque = (168, 128, 74)
    plaque_light = (204, 166, 104)
    plaque_dark = (112, 80, 46)
    black = (26, 26, 28)
    sheen = (62, 62, 68)
    cheek = (238, 238, 232)
    cheek_shade = (188, 188, 182)
    bill = (44, 44, 48)

    # The board against the wall, seen almost edge-on: an upright oval,
    # taller than it is wide, with its turned rim catching the light.
    pygame.draw.ellipse(s, outline, (0, 1, 12, 20))
    pygame.draw.ellipse(s, plaque_dark, (1, 2, 10, 18))
    pygame.draw.ellipse(s, plaque, (2, 3, 8, 16))
    pygame.draw.ellipse(s, plaque_light, (3, 5, 4, 11))

    # The neck, running out of the board and over the room.
    pygame.draw.polygon(s, outline, ((7, 6), (19, 4), (19, 15), (7, 15)))
    pygame.draw.polygon(s, black, ((8, 7), (18, 5), (18, 14), (8, 14)))
    pygame.draw.line(s, sheen, (10, 8), (17, 7))

    # The head at the far end, with the bill angled down over the floor.
    pygame.draw.ellipse(s, outline, (16, 1, 13, 14))
    pygame.draw.ellipse(s, black, (17, 2, 11, 12))
    # The chinstrap: the one marking that names the bird.
    pygame.draw.polygon(s, outline, ((21, 2), (28, 3), (28, 7), (22, 6)))
    pygame.draw.polygon(s, cheek_shade, ((22, 3), (27, 4), (27, 6), (22, 5)))
    pygame.draw.polygon(s, cheek, ((22, 3), (26, 4), (26, 5), (22, 4)))
    # The bill, kept clear of the head by its own outline so the two do
    # not merge into one dark blob.
    pygame.draw.polygon(s, outline, ((21, 11), (28, 13), (25, 21), (20, 16)))
    pygame.draw.polygon(s, bill, ((22, 12), (26, 14), (24, 19), (21, 15)))
    pygame.draw.line(s, (80, 80, 86), (23, 13), (25, 16))

    # One glass eye. It is not winking.
    s.set_at((21, 8), (18, 12, 10))
    s.set_at((22, 8), (12, 8, 6))
    s.set_at((21, 7), (176, 164, 138))
    return s


def main():
    pygame.init()
    save(couch(106), "cabin_big_couch.png")
    save(couch(82, olive=True), "cabin_couch.png")
    save(chair(), "cabin_chair.png")
    save(table(), "cabin_table.png")
    for index in range(len(PORTAL_COLOURS)):
        save(table(index), f"cabin_table_awakened_{index + 1}.png")
    save(connector_shelf(), "cabin_connector_shelf.png")
    save(mini_fridge(), "cabin_mini_fridge.png")
    save(closed_door_west(), "cabin_closed_door_west.png")
    save(kitchen(), "cabin_kitchen.png")
    for index in range(6):
        save(woodstove(index), f"cabin_woodstove_{index + 1}.png")
    save(wood_storage(), "cabin_wood_storage.png")
    for index in range(6):
        save(lava_lamp(index), f"cabin_lava_lamp_{index + 1}.png")
    for index in range(3):
        save(curtain_window(index),
             f"cabin_curtain_window_{index + 1}.png")
    save(closed_door_north(), "cabin_closed_door_north.png")
    save(macrame(), "cabin_macrame.png")
    save(goose_mount(), "cabin_goose_mount.png")


if __name__ == "__main__":
    main()
