"""Generate the first playable Feywild terrain sheet."""

import math
import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import FEYWILD, TILE_PX


GROUND = (20, 55, 52)
GROUND_DARK = (13, 41, 42)
GROUND_LIGHT = (39, 86, 63)
LEAF_DARK = (12, 56, 47)
LEAF = (34, 120, 72)
LEAF_LIGHT = (79, 183, 99)
VIOLET = (184, 78, 235)
PINK = (238, 101, 184)
BLUE = (68, 184, 245)
GOLD = (239, 205, 80)
WATER_DEEP = (9, 45, 76)
WATER = (18, 114, 140)
WATER_LIGHT = (79, 220, 201)
BANK = (35, 85, 61)
BANK_DARK = (22, 63, 52)
PATH = (45, 76, 59)
PATH_LIGHT = (68, 105, 72)
ROOT_DARK = (42, 31, 34)
ROOT_BROWN = (82, 55, 45)
ROOT_LIGHT = (125, 83, 55)
# Redcap Warrens: giant toadstools, pale and cold beside the warm roots.
CAP_SHADOW = (58, 40, 62)
CAP = (146, 92, 122)
CAP_LIGHT = (206, 158, 178)
STALK = (198, 190, 168)
# Mushroom Underways: canopy shade underfoot, and still luminous pools.
SHADE_DARK = (10, 26, 30)
SHADE = (18, 40, 44)
SHADE_LIGHT = (32, 62, 62)
POOL_DEEP = (16, 62, 96)
POOL = (52, 158, 186)
POOL_LIGHT = (140, 240, 226)
# Luminous Rapids: fast bright water, wet stones, and giant flower pads.
RAPID_DEEP = (22, 78, 118)
RAPID = (86, 190, 214)
FOAM = (222, 250, 248)
STONE_DARK = (52, 58, 62)
STONE = (104, 112, 116)
STONE_LIGHT = (156, 164, 164)
PAD_DARK = (22, 78, 52)
PAD = (58, 138, 74)
PAD_LIGHT = (104, 190, 104)
PAD_SUNK = (34, 96, 108)
PAD_SUNK_LIGHT = (58, 130, 132)
DIRT_DARK = (44, 38, 32)
DIRT = (66, 57, 45)
DIRT_LIGHT = (92, 80, 60)
TABLE_DARK = (68, 43, 47)
TABLE = (119, 75, 65)
TABLE_LIGHT = (170, 111, 78)
TEA = (72, 118, 102)


def ground(surface, variant: int, _frame: int) -> None:
    surface.fill(GROUND)
    for index in range(4):
        x = (variant * 5 + index * 7 + 2) % 16
        y = (variant * 3 + index * 5 + 4) % 16
        color = GROUND_LIGHT if index == 0 else GROUND_DARK
        pygame.draw.rect(surface, color, (x, y, 2, 2))
    glow = (VIOLET, BLUE, PINK, GOLD)[variant]
    surface.set_at(((variant * 4 + 3) % 15, (variant * 6 + 8) % 15), glow)


def dense(surface, variant: int, _frame: int) -> None:
    surface.fill(GROUND_DARK)
    clusters = (
        ((-4, -3, 12, 11), (5, -3, 13, 10), (0, 7, 12, 11), (9, 7, 10, 11)),
        ((-3, 3, 12, 11), (3, -4, 13, 12), (10, 0, 10, 12), (5, 9, 12, 9)),
        ((-3, -3, 13, 11), (8, -2, 11, 11), (-2, 8, 11, 10), (7, 7, 13, 12)),
        ((-4, -4, 12, 13), (5, -2, 13, 11), (0, 9, 12, 10), (10, 6, 9, 11)),
    )[variant]
    for index, rect in enumerate(clusters):
        pygame.draw.ellipse(
            surface,
            LEAF_DARK if index == 0 else LEAF,
            rect,
        )
        x, y, width, height = rect
        pygame.draw.line(
            surface, LEAF_LIGHT,
            (max(0, x + width // 2), max(0, y + height // 2)),
            (min(15, x + width - 2), min(15, y + height - 2)),
        )
    pygame.draw.rect(
        surface, (VIOLET, BLUE, PINK, GOLD)[variant],
        ((variant * 5 + 2) % 14, (variant * 3 + 5) % 14, 2, 2),
    )


def river(surface, variant: int, frame: int) -> None:
    surface.fill(WATER_DEEP)
    phase = frame * 3 + variant * 2
    for y in range(16):
        amount = 0.35 + 0.25 * math.sin(y * 0.6 + phase)
        color = tuple(
            round(a + (b - a) * amount)
            for a, b in zip(WATER_DEEP, WATER)
        )
        pygame.draw.line(surface, color, (0, y), (15, y))
    for index, y in enumerate((3, 8, 13)):
        x = (phase + index * 7) % 16
        pygame.draw.line(
            surface, WATER_LIGHT, (x, y), (min(15, x + 6), y)
        )


def bank(surface, variant: int, _frame: int) -> None:
    surface.fill(BANK)
    pygame.draw.line(surface, BANK_DARK, (0, 0), (0, 15), 2)
    for index in range(4):
        x = (variant * 5 + index * 4 + 2) % 15
        y = (variant * 3 + index * 6 + 1) % 15
        pygame.draw.ellipse(
            surface,
            LEAF if index % 2 else LEAF_LIGHT,
            (x - 2, y - 1, 5, 3),
        )


def path(surface, variant: int, _frame: int) -> None:
    surface.fill(PATH)
    pygame.draw.line(surface, GROUND_DARK, (0, 15), (15, 15))
    for index in range(3):
        x = (variant * 4 + index * 6 + 1) % 15
        y = (variant * 7 + index * 5 + 3) % 15
        pygame.draw.rect(
            surface, PATH_LIGHT if index == 0 else GROUND_LIGHT,
            (x, y, 3, 2),
        )


def pollen(surface, variant: int, frame: int) -> None:
    """Low luminous flowers and drifting spores over readable ground."""
    surface.fill((49, 78, 54))
    pygame.draw.rect(surface, (61, 91, 58), (0, 12, 16, 4))
    petals = (GOLD, PINK, BLUE)
    for index in range(4):
        x = (variant * 5 + index * 4 + 1) % 15
        y = 9 + ((variant + index * 2) % 5)
        color = petals[(variant + index) % len(petals)]
        pygame.draw.line(surface, LEAF_LIGHT, (x, 15), (x, y + 1))
        surface.set_at((x, y), color)
        if x + 1 < 16:
            surface.set_at((x + 1, y + 1), color)
    # Three small motes rise and drift between animation frames. Their
    # stagger keeps adjacent tiles from resolving into a uniform grid.
    for index, color in enumerate((GOLD, PINK, BLUE)):
        x = (variant * 7 + index * 6 + frame * (index + 1)) % 16
        y = 8 - ((frame * 2 + index * 3 + variant) % 7)
        surface.set_at((x, y), color)


def opening(surface, variant: int, side: str) -> None:
    """A dense vegetation arch framing one cardinal wilderness handoff."""
    surface.fill((0, 0, 0, 0))
    throat = {
        "w": (0, 3, 13, 10),
        "e": (3, 3, 13, 10),
        "n": (3, 0, 10, 13),
        "s": (3, 3, 10, 13),
    }[side]
    # The dark recess is the readable negative space; it is surrounded by
    # leaves rather than masonry so it remains a wilderness trail opening.
    pygame.draw.rect(surface, GROUND_DARK, throat)
    pygame.draw.rect(surface, (8, 29, 31), throat, 1)
    bands = {
        "w": ((0, 0, 5, 16), (0, 0, 16, 4), (0, 12, 16, 4)),
        "e": ((11, 0, 5, 16), (0, 0, 16, 4), (0, 12, 16, 4)),
        "n": ((0, 0, 16, 5), (0, 0, 4, 16), (12, 0, 4, 16)),
        "s": ((0, 11, 16, 5), (0, 0, 4, 16), (12, 0, 4, 16)),
    }[side]
    for index, rect in enumerate(bands):
        pygame.draw.rect(surface, LEAF_DARK if index == 0 else LEAF, rect)
    accents = (VIOLET, BLUE, PINK)
    if side in {"w", "e"}:
        edge_x = 2 if side == "w" else 13
        pygame.draw.line(surface, LEAF_LIGHT, (edge_x, 1), (edge_x, 14), 2)
        pygame.draw.line(
            surface, accents[variant], (edge_x, 3 + variant),
            (8 if side == "w" else 7, 5 + variant), 1,
        )
        pygame.draw.line(
            surface, accents[(variant + 1) % 3], (edge_x, 12 - variant),
            (7 if side == "w" else 8, 10 - variant), 1,
        )
    else:
        edge_y = 2 if side == "n" else 13
        pygame.draw.line(surface, LEAF_LIGHT, (1, edge_y), (14, edge_y), 2)
        pygame.draw.line(
            surface, accents[variant], (3 + variant, edge_y),
            (5 + variant, 8 if side == "n" else 7), 1,
        )
        pygame.draw.line(
            surface, accents[(variant + 1) % 3], (12 - variant, edge_y),
            (10 - variant, 7 if side == "n" else 8), 1,
        )


def opening_w(surface, variant: int, _frame: int) -> None:
    opening(surface, variant, "w")


def opening_e(surface, variant: int, _frame: int) -> None:
    opening(surface, variant, "e")


def opening_n(surface, variant: int, _frame: int) -> None:
    opening(surface, variant, "n")


def opening_s(surface, variant: int, _frame: int) -> None:
    opening(surface, variant, "s")


# ---------------------------------------------------------------------
# Root walls
# ---------------------------------------------------------------------
# The first root wall was four parallel bands drawn diagonally across
# every tile. Tiled, that is an even stripe running across the whole
# wall -- bark shingles, or a brown rug -- and nothing about it said
# roots. Roots curve, cross over each other, and never repeat.
#
# So each tile is a small tangle of curved strands, and the strands only
# ever leave a tile at fixed points on its edges, at a fixed thickness,
# heading straight out. Every variant uses every one of those points, so
# whichever two variants end up side by side, each root that runs off one
# tile runs straight on into the next: the tangle is continuous across
# the whole wall, and the variant hash only decides how it tangles.
ROOT_GAP = (20, 14, 18)         # a deep hole into the mass
ROOT_SHADE = (38, 27, 28)       # the ordinary shadow between roots
ROOT_GAP_SOIL = (48, 34, 32)
ROOT_EDGE = (56, 38, 36)
ROOT_SIDE_PORTS = ((2, 1.8), (8, 2.9), (13, 2.2))    # (y, radius)
ROOT_END_PORTS = ((3, 2.2), (11, 2.7))                # (x, radius)
ROOT_WALL_VARIANTS = 8


def _root_ports():
    ports = []
    for y, radius in ROOT_SIDE_PORTS:
        ports.append(("left", (-0.5, y + 0.5), (1, 0), radius))
        ports.append(("right", (16.5, y + 0.5), (-1, 0), radius))
    for x, radius in ROOT_END_PORTS:
        ports.append(("top", (x + 0.5, -0.5), (0, 1), radius))
        ports.append(("bottom", (x + 0.5, 16.5), (0, -1), radius))
    return ports


def _variant_random(variant: int, salt: int):
    import random

    return random.Random(variant * 7919 + salt * 104729)


def _draw_strand(surface, p0, d0, r0, p3, d3, r3, *, reach=5.5,
                 bend=(0.0, 0.0), taper_end=False, sides=(None, None)) -> None:
    """One root, as a cubic curve painted with shaded discs.

    Lit on its upper-left side and rimmed dark, so where one strand
    passes over another the one on top has an edge -- which is the whole
    of what makes a tangle read as a tangle.
    """
    # The ends head straight out of the tile and the bend lives only in
    # the middle. Bending the control points instead also bent the root
    # where it crosses the edge, so the same edge point came out a
    # different width in every variant and the wall showed its seams.
    p1 = (p0[0] + d0[0] * reach, p0[1] + d0[1] * reach)
    p2 = (p3[0] + d3[0] * reach, p3[1] + d3[1] * reach)
    steps = 40
    samples = []
    for step in range(steps + 1):
        t = step / steps
        u = 1 - t
        sway = math.sin(math.pi * t) ** 2
        x = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0]             + t ** 3 * p3[0] + bend[0] * sway
        y = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1]             + t ** 3 * p3[1] + bend[1] * sway
        if taper_end:
            radius = r0 + (r3 - r0) * t
        else:
            # Swell a little in the middle: a root is thicker between
            # the places it bends than where it bends.
            radius = r0 + (r3 - r0) * t + 0.5 * math.sin(t * math.pi)
        samples.append((x, y, radius, t))
    # Shade each pixel from its nearest point on the curve. Stamping a
    # shaded disc at each step instead let every disc paint its dark rim
    # over the middle of the one before, and the strands came out as
    # rim-coloured sludge.
    for py in range(16):
        for px in range(16):
            best = None
            for x, y, radius, t in samples:
                ox, oy = px + 0.5 - x, py + 0.5 - y
                reach = math.hypot(ox, oy) / radius
                if best is None or reach < best[0]:
                    best = (reach, ox, oy, radius, t)
            reach, ox, oy, radius, t = best
            if reach > 1.0:
                continue
            # A root may only touch the tile's edge where it leaves the
            # tile, at its own edge point. Anywhere else it would run off
            # into a neighbour that has no root there to meet it, and the
            # wall would show its tile grid as a line of cut-off roots.
            edges = {side for side, on in (("left", px == 0),
                                           ("right", px == 15),
                                           ("top", py == 0),
                                           ("bottom", py == 15)) if on}
            if edges:
                if len(edges) > 1:
                    continue
                edge = next(iter(edges))
                along = px + 0.5 if edge in ("top", "bottom") else py + 0.5
                # Allowed only right at one of this root's own edge
                # points. Deciding by which end of the curve the pixel is
                # nearest failed where a root loops back past its start.
                if not any(
                    side == edge
                    and abs(along - (port[0] if edge in ("top", "bottom")
                                     else port[1])) <= width
                    for side, port, width in ((sides[0], p0, r0),
                                              (sides[1], p3, r3))
                ):
                    continue
            if reach > 1.0 - 0.75 / radius:
                colour = ROOT_EDGE
            elif (ox + oy) < -radius * 0.35:
                colour = ROOT_LIGHT
            else:
                colour = ROOT_BROWN
            surface.set_at((px, py), colour)


def root_wall(surface, variant: int, _frame: int) -> None:
    """A tangle of roots that carries on into every neighbouring tile."""
    rng = _variant_random(variant, 1)
    # Ordinary shadow between the roots, the same all the way to every
    # edge, and a few deep holes kept well inside the tile. With the
    # whole gap drawn near-black, the edges -- where roots may only
    # cross at their own points -- came out as a line of dark dashes
    # along every tile boundary and drew the grid back on the wall.
    surface.fill(ROOT_SHADE)
    for index in range(3):
        cx, cy = rng.uniform(4, 12), rng.uniform(4, 12)
        radius = rng.uniform(1.2, 2.4)
        for py in range(16):
            for px in range(16):
                if math.hypot(px + 0.5 - cx, (py + 0.5 - cy) * 1.3) <= radius:
                    surface.set_at((px, py), ROOT_GAP)
    for index in range(7):                    # soil showing through the gaps
        surface.set_at((rng.randrange(1, 15), rng.randrange(1, 15)),
                       ROOT_GAP_SOIL)

    ports = _root_ports()
    # Pair every port with a port on a different side. Every variant uses
    # all ten, so no root ever stops dead at a tile edge.
    for _attempt in range(200):
        order = ports[:]
        rng.shuffle(order)
        pairs = [(order[i], order[i + 1]) for i in range(0, 10, 2)]
        if all(a[0] != b[0] for a, b in pairs):
            break
    rng.shuffle(pairs)
    for (side_a, p0, d0, r0), (side_b, p3, d3, r3) in pairs:
        # Loose and uneven: kept tight and regular, the tangle came out
        # as basketwork.
        bend = (rng.uniform(-6.0, 6.0), rng.uniform(-6.0, 6.0))
        _draw_strand(surface, p0, d0, r0, p3, d3, r3,
                     reach=rng.uniform(2.5, 9.0), bend=bend,
                     sides=(side_a, side_b))

    # Bark: a few darker grain marks along the lit strands.
    for index in range(5):
        x, y = rng.randrange(1, 15), rng.randrange(1, 15)
        if surface.get_at((x, y))[:3] == ROOT_BROWN:
            surface.set_at((x, y), ROOT_DARK)
    # A hair root or a leaf, and now and then one of the Feywild's motes.
    if variant % 2 == 0:
        x, y = rng.randrange(3, 13), rng.randrange(3, 13)
        if surface.get_at((x, y))[:3] in (ROOT_GAP, ROOT_SHADE):
            surface.set_at((x, y), LEAF)
            surface.set_at((x + 1, y - 1), LEAF_DARK)
    if variant % 3 == 1:
        x, y = rng.randrange(2, 14), rng.randrange(2, 14)
        if surface.get_at((x, y))[:3] in (ROOT_GAP, ROOT_SHADE):
            surface.set_at((x, y), (VIOLET, BLUE, PINK, GOLD)[variant % 4])


def root_face(surface, variant: int, _frame: int) -> None:
    """The front of a root wall, where it stops above open ground.

    The roots coming down into this tile do not carry on: they curl over
    and hang, tapering to tips, into the shadow under the mass. That edge
    is what makes the wall a thing standing on the floor rather than a
    brown shape cut out of it.
    """
    rng = _variant_random(variant, 2)
    surface.fill(ROOT_GAP)
    # The hollow under the overhang deepens towards the floor.
    for y in range(9, 16):
        shade = max(0, 14 - (y - 9) * 2)
        for x in range(16):
            surface.set_at((x, y), (ROOT_GAP[0] - 14 + shade,
                                    ROOT_GAP[1] - 10 + shade,
                                    ROOT_GAP[2] - 10 + shade))

    ports = _root_ports()
    entries = [port for port in ports
               if port[0] == "top"
               or (port[0] in ("left", "right") and port[1][1] < 12)]
    rng.shuffle(entries)
    for side, p0, d0, r0 in entries:
        tip_x = p0[0] + (rng.uniform(-3, 3) if side == "top"
                         else d0[0] * rng.uniform(4, 7))
        tip = (max(1.0, min(15.0, tip_x)), rng.uniform(12.5, 15.0))
        _draw_strand(surface, p0, d0, r0, tip, (0, -1), 0.6,
                     reach=rng.uniform(3.5, 5.5),
                     bend=(rng.uniform(-2, 2), rng.uniform(0, 2)),
                     taper_end=True, sides=(side, "tip"))
    # Hair roots hanging from the underside.
    for index in range(3):
        x = rng.randrange(2, 14)
        for y in range(rng.randrange(9, 12), 16):
            if surface.get_at((x, y))[:3] in (ROOT_BROWN, ROOT_LIGHT,
                                              ROOT_EDGE):
                continue
            if rng.random() < 0.75:
                surface.set_at((x, y), ROOT_EDGE)
    # A little moss on the lip.
    for index in range(2):
        x = rng.randrange(1, 15)
        for y in range(4, 11):
            if surface.get_at((x, y))[:3] == ROOT_LIGHT:
                surface.set_at((x, y), LEAF_DARK)
                break


def root_passage(surface, variant: int, _frame: int) -> None:
    """A low arch drawn over Chuck while leaving the path visible beneath."""
    surface.fill((0, 0, 0, 0))
    pygame.draw.line(surface, ROOT_DARK, (0, 2), (15, 2 + variant), 7)
    pygame.draw.line(surface, ROOT_BROWN, (0, 1), (15, 1 + variant), 4)
    pygame.draw.line(surface, ROOT_LIGHT, (0, 0), (15, variant), 1)
    pygame.draw.line(surface, ROOT_DARK, (1, 0), (1, 8), 3)
    pygame.draw.line(surface, ROOT_DARK, (14, 2), (14, 9), 3)
    pygame.draw.line(surface, LEAF, (2, 1), (8 + variant, 4), 1)


def camp_dirt(surface, variant: int, _frame: int) -> None:
    """Packed earth the redcaps have trampled bare.

    Deliberately free of the path tile's edge line: this fills wide areas,
    and any directional mark would band into stripes across the camp.
    """
    surface.fill(DIRT)
    for index in range(6):
        x = (variant * 5 + index * 7 + 1) % 15
        y = (variant * 11 + index * 5 + 2) % 15
        surface.fill(DIRT_DARK if index % 2 else DIRT_LIGHT, (x, y, 2, 1))
    for index in range(2):                 # trodden scraps of the old turf
        x = (variant * 3 + index * 9 + 4) % 14
        y = (variant * 7 + index * 6 + 6) % 14
        surface.set_at((x, y), LEAF_DARK)


def rapids(surface, variant: int, frame: int) -> None:
    """Fast bright water: the Luminous Rapids' impassable middle."""
    surface.fill(RAPID_DEEP)
    for y in range(16):
        amount = 0.45 + 0.35 * math.sin(y * 0.8 + frame * 2.2 + variant)
        colour = tuple(round(a + (b - a) * amount)
                       for a, b in zip(RAPID_DEEP, RAPID))
        pygame.draw.line(surface, colour, (0, y), (15, y))
    # Broken crests, scattered rather than ruled, so a wide river does
    # not resolve into horizontal bands.
    for index in range(4):
        x = (variant * 5 + index * 6 + frame * 4) % 16
        y = (variant * 7 + index * 4 + frame) % 16
        pygame.draw.line(surface, FOAM, (x, y), (min(15, x + 3), y))
    surface.set_at(((variant * 9 + frame * 3) % 16,
                    (variant * 5 + 9) % 16), (240, 254, 250))


def stepping_stone(surface, variant: int, _frame: int) -> None:
    """A static safe stone: wet, blunt, and obviously standable."""
    surface.fill(RAPID_DEEP)
    pygame.draw.ellipse(surface, STONE_DARK, (0, 1, 16, 15))
    pygame.draw.ellipse(surface, STONE, (1, 2, 14, 12))
    pygame.draw.ellipse(surface, STONE_LIGHT, (3 + variant, 4, 7, 4))
    for index in range(2):
        x = (variant * 5 + index * 7 + 3) % 12
        y = (variant * 3 + index * 5 + 7) % 12
        surface.set_at((x, y), STONE_DARK)


def pad_open(surface, variant: int, _frame: int) -> None:
    """A giant flower pad, risen and broad enough to stand on."""
    surface.fill(RAPID_DEEP)
    pygame.draw.ellipse(surface, PAD_DARK, (0, 0, 16, 16))
    pygame.draw.ellipse(surface, PAD, (1, 1, 14, 14))
    pygame.draw.ellipse(surface, PAD_LIGHT, (4, 3, 8, 6))
    # The notch every lily pad has, turned by variant so a chain of pads
    # never looks stamped.
    notch = ((7, 0), (0, 7), (7, 14))[variant % 3]
    pygame.draw.line(surface, RAPID_DEEP, (8, 8), notch, 2)
    surface.set_at((8, 8), GOLD)


def pad_closed(surface, variant: int, _frame: int) -> None:
    """The same pad furled under the water: visibly there, visibly not
    yet safe, so a broken chain can be read before it is jumped."""
    surface.fill(RAPID_DEEP)
    pygame.draw.ellipse(surface, PAD_SUNK, (2, 4, 12, 10))
    pygame.draw.ellipse(surface, PAD_SUNK_LIGHT, (4, 6, 8, 5))
    pygame.draw.line(surface, PAD_SUNK_LIGHT, (3, 9 + variant % 2),
                     (12, 9 + variant % 2))
    for index in range(2):
        x = (variant * 6 + index * 7 + 2) % 15
        pygame.draw.line(surface, FOAM, (x, 2), (x + 2, 2))


def cap_shade(surface, variant: int, frame: int) -> None:
    """The floor beneath a giant cap: dark, gilled, quietly alive.

    Tiles seamlessly in long runs, because the Underways are meant to be
    walked under a canopy for a while rather than through a doorway.
    """
    surface.fill(SHADE)
    # Gill shadows fall on the ground in broken strokes. They are kept
    # short deliberately: a full-width line would band into stripes the
    # moment the shade covers more than a few tiles.
    for index in range(4):
        x = (variant * 5 + index * 7) % 13
        y = (variant * 3 + index * 5 + 1) % 15
        length = 3 + ((variant + index) % 3)
        pygame.draw.line(surface, SHADE_DARK, (x, y), (x + length, y + 1))
    x = (variant * 7 + 2) % 12
    y = (variant * 11 + 6) % 14
    pygame.draw.line(surface, SHADE_LIGHT, (x, y), (x + 3, y))
    # Spores drifting in the dark, turning over between frames.
    for index, colour in enumerate((BLUE, VIOLET, GOLD)):
        x = (variant * 6 + index * 5 + frame * 2) % 16
        y = (variant * 4 + index * 7 + frame * 3) % 16
        surface.set_at((x, y), colour)


def glow_pool(surface, variant: int, frame: int) -> None:
    """A still luminous pool. Solid: something to walk around and admire."""
    surface.fill(POOL_DEEP)
    for y in range(16):
        amount = 0.4 + 0.3 * math.sin(y * 0.5 + frame * 2 + variant)
        colour = tuple(round(a + (b - a) * amount)
                       for a, b in zip(POOL_DEEP, POOL))
        pygame.draw.line(surface, colour, (0, y), (15, y))
    for index in range(2):
        x = (variant * 5 + index * 8 + frame * 3) % 16
        y = (variant * 3 + index * 9 + 2) % 15
        pygame.draw.line(surface, POOL_LIGHT, (x, y), (min(15, x + 4), y))
    surface.set_at(((variant * 7 + frame * 5) % 16,
                    (variant * 9 + 6) % 16), (236, 252, 246))


def mushroom_thicket(surface, variant: int, _frame: int) -> None:
    """Fused toadstool stalks: a solid wall of caps at redcap height."""
    surface.fill(CAP_SHADOW)
    for index in range(3):
        x = (index * 6 + variant * 2) % 14
        # Stagger the caps hard vertically: at four variants a shallow
        # offset still resolves into visible rows across a whole thicket.
        top = 1 + ((index * 5 + variant * 3) % 8)
        pygame.draw.rect(surface, STALK, (x + 1, top + 4, 4, 12))
        pygame.draw.ellipse(surface, CAP, (x - 1, top, 9, 7))
        pygame.draw.ellipse(surface, CAP_LIGHT, (x + 1, top + 1, 5, 3))
        surface.set_at((x + 3, top + 4), CAP_SHADOW)
    pygame.draw.line(surface, LEAF_DARK, (0, 15), (15, 15))


def mushroom_passage(surface, variant: int, _frame: int) -> None:
    """A cap arching overhead: the gap beneath is Chuck's alone.

    Drawn like the root passage so the two read as the same promise --
    a way through that a gnome-sized redcap simply cannot follow.
    """
    surface.fill((0, 0, 0, 0))
    pygame.draw.ellipse(surface, CAP_SHADOW, (-4, -5, 24, 11))
    pygame.draw.ellipse(surface, CAP, (-3, -6, 22, 10))
    pygame.draw.ellipse(surface, CAP_LIGHT, (2 + variant, -4, 8, 3))
    for x in (1, 13):                      # the stalks framing the gap
        pygame.draw.rect(surface, STALK, (x, 2, 2, 7))
        pygame.draw.line(surface, CAP_SHADOW, (x, 3), (x, 8))
    surface.set_at((6 + variant, 1), GOLD)  # a spore catching the light


def tabletop(surface, variant: int, _frame: int) -> None:
    """Warm impossible-scale boards for the abandoned Fey tea table."""
    surface.fill(TABLE)
    pygame.draw.line(surface, TABLE_DARK, (0, 15), (15, 15))
    pygame.draw.line(surface, TABLE_LIGHT, (0, 1), (15, 1))
    for index in range(2):
        x = (variant * 7 + index * 9 + 2) % 15
        y = (variant * 3 + index * 7 + 5) % 14
        length = 3 + ((variant + index) % 3)
        pygame.draw.line(
            surface, TABLE_LIGHT,
            (x, y), (min(15, x + length), y),
        )
        if index == 1:
            pygame.draw.line(
                surface, TABLE_DARK,
                (max(0, x - 2), y + 2), (min(15, x + 2), y + 2),
            )


def _shade(colour, amount: float = 0.42):
    return tuple(round(channel * amount) for channel in colour)


def table_shadow(surface, variant: int, _frame: int) -> None:
    """The Feywild's own ground, in the dark under the table.

    This is the same tile as `ground`, at the same speckle positions,
    with every colour taken down to a bit under half. That is the whole
    of the change and the whole of the point: shade is the same floor
    with less light on it, so a shaded floor reads as being under
    something, where a different floor reads as a different room.

    The frame this used to have -- a wooden lip drawn round the ring of
    the shadow -- is gone, and it was the frame doing the explaining
    before. From above at this distance a thin border round a dark
    rectangle is a picture frame, not the edge of a table.

    Two things went with it. The old tile carried a green line along
    its bottom edge, which on a field ten tiles deep drew ten stripes
    across the underside of the table and read as floorboards. And the
    pollen glow is gone too: every other ground tile out here catches
    one lit mote, and the one place in the Feywild where nothing should
    be catching the light is under the furniture.
    """
    surface.fill(_shade(GROUND))
    for index in range(4):
        x = (variant * 5 + index * 7 + 2) % 16
        y = (variant * 3 + index * 5 + 4) % 16
        colour = GROUND_LIGHT if index == 0 else GROUND_DARK
        pygame.draw.rect(surface, _shade(colour), (x, y, 2, 2))


# How much of the ground still shows through the boards from under the
# table. Not opaque: from under a table you see the boards over you and
# the floor past them, and a solid ceiling here would black out a ten
# tile band of the map until Chuck was already standing in it.
TABLE_UNDER_ALPHA = 182


def table_under(surface, variant: int, _frame: int) -> None:
    """The table's underside, drawn OVER Chuck while he walks below it.

    The same boards as the top, turned away from the light: no lit edge
    catching the sun, the grain in shadow, and the seams between planks
    running across rather than being polished out. It is drawn over the
    shaded ground rather than instead of it, so the floor he is walking
    on stays faintly visible through it -- and it thins out the rest of
    the way while he is under it, like the market's awning.
    """
    surface.fill((*_shade(TABLE, 0.66), TABLE_UNDER_ALPHA))
    seam = (*_shade(TABLE_DARK, 0.8), TABLE_UNDER_ALPHA)
    grain = (*_shade(TABLE, 0.82), TABLE_UNDER_ALPHA)
    # A plank seam on one tile in four, not one in two: a line every
    # other row across a field ten tiles deep is brickwork, and a table
    # is not made of bricks. The grain runs the length of the plank.
    if variant == 0:
        pygame.draw.line(surface, seam, (0, 15), (15, 15))
    for index in range(2):
        y = (variant * 5 + index * 6 + 3) % 14
        start = (variant * 7 + index * 9) % 16 - 6
        pygame.draw.line(surface, grain,
                         (max(0, start), y), (min(15, start + 11), y))


def tea_spill(surface, variant: int, _frame: int) -> None:
    tabletop(surface, variant, 0)
    points = (
        ((1, 5), (11, 3), (15, 8), (12, 14), (3, 13)),
        ((0, 8), (5, 2), (13, 4), (15, 12), (8, 15), (2, 13)),
        ((3, 2), (14, 5), (13, 13), (6, 15), (0, 10)),
    )[variant]
    pygame.draw.polygon(surface, (48, 91, 82), points)
    pygame.draw.lines(surface, TEA, True, points, 1)
    surface.set_at(((variant * 5 + 5) % 14, 7 + variant), (111, 180, 143))


def needle_bed(surface, variant: int, _frame: int) -> None:
    """Dense flowering foliage used to frame the orchid firing lanes."""
    surface.fill(GROUND_DARK)
    for index in range(7):
        x = (variant * 5 + index * 7 + 1) % 16
        y = (variant * 9 + index * 5 + 2) % 16
        color = (LEAF_LIGHT if index % 3 == 0 else LEAF)
        pygame.draw.line(
            surface, color, (x, min(15, y + 3)), (x, max(0, y - 2)), 1
        )
        if index % 2:
            pygame.draw.line(
                surface, color,
                (x, y), (max(0, x - 2), max(0, y - 2)), 1,
            )
        bloom = (
            (211, 92, 191) if (index + variant) % 2
            else (234, 174, 103)
        )
        pygame.draw.rect(
            surface, bloom, ((x - 1) % 16, max(0, y - 3), 2, 2)
        )
    pygame.draw.line(surface, GROUND_LIGHT, (0, 15), (15, 15), 1)


def channel(surface, variant: int, frame: int) -> None:
    """A narrow fen channel: shallower and brighter than the deep river,
    with reed-lit banks so a one-tile hop reads as obviously crossable."""
    river(surface, variant, frame)
    # Lighter shallows: the bed shows through where Chuck can clear it.
    phase = frame * 3 + variant * 2
    for y in range(3, 13):
        amount = 0.55 + 0.3 * math.sin(y * 0.5 + phase)
        color = tuple(
            round(a + (b - a) * amount)
            for a, b in zip(WATER, WATER_LIGHT)
        )
        pygame.draw.line(surface, color, (2, y), (13, y))
    # Reeds leaning in from both banks mark it as the narrow crossing.
    for x, top in ((1, 4), (14, 6), (3, 11), (12, 2)):
        pygame.draw.line(surface, GROUND_LIGHT, (x, top), (x, top + 3))
    pygame.draw.line(surface, WATER_DEEP, (0, 0), (15, 0))
    pygame.draw.line(surface, WATER_DEEP, (0, 15), (15, 15))


DRAW = {
    "fey_ground": ground,
    "fey_channel": channel,
    "fey_dense": dense,
    "fey_river": river,
    "fey_bank": bank,
    "fey_path": path,
    "fey_pollen": pollen,
    "fey_opening_w": opening_w,
    "fey_opening_e": opening_e,
    "fey_opening_n": opening_n,
    "fey_opening_s": opening_s,
    "fey_root_wall": root_wall,
    "fey_root_face": root_face,
    "fey_root_passage": root_passage,
    "fey_camp_dirt": camp_dirt,
    "fey_rapids": rapids,
    "fey_stepping_stone": stepping_stone,
    "fey_pad_open": pad_open,
    "fey_pad_closed": pad_closed,
    "fey_cap_shade": cap_shade,
    "fey_glow_pool": glow_pool,
    "fey_mushroom_thicket": mushroom_thicket,
    "fey_mushroom_passage": mushroom_passage,
    "fey_tabletop": tabletop,
    "fey_table_shadow": table_shadow,
    "fey_table_under": table_under,
    "fey_tea_spill": tea_spill,
    "fey_needle_bed": needle_bed,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface(
        (FEYWILD.cols * TILE_PX, FEYWILD.rows * TILE_PX),
        pygame.SRCALPHA,
    )
    for row_index, (name, variants, frames) in enumerate(FEYWILD.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(
                    cell,
                    ((variant * frames + frame) * TILE_PX, row_index * TILE_PX),
                )
    output = ROOT / "assets" / "tilesets" / FEYWILD.sheet
    pygame.image.save(sheet, output)
    print(f"Wrote {output} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
