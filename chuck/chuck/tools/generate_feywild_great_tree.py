"""Generate the Feywild's great trees.

Every tree in the Feywild so far is Chuck-sized in the way a hedge is
Chuck-sized: taller than him, but a thing he walks past. The wood's
spiral trees, the washed Chult silhouettes and the one plain oak are all
two or three tiles of canopy. Nothing in the region is old.

These are. Eleven tiles across and fourteen tall, a trunk three tiles
wide at the base with roots running out across the ground from it, and
a crown big enough to stand under -- the kind of tree a forest grows up
round rather than alongside. No face in the bark: it is just a tree, and
the size is the whole of the strangeness.

Drawn with the same shaded primitives as the title screen -- capsules
for trunk, roots and boughs, ellipsoids for the leaf masses, lit from
the upper left, ordered-dithered between tones of a fixed ramp -- but in
the game's own palette and at the game's own resolution, so it stands
in a map rather than on a poster. The bark is the Feywild's violet-brown
and the leaves are its teal-green, with a handful of the region's motes
caught in the crown.

Three variants, so two great trees on neighbouring maps are not the same
tree twice.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_title_art import Piece, _hash, _outline  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"

# Eleven tiles by fourteen. The prop is centred on its anchor tile, so an
# odd number of tiles across puts the trunk dead centre over the solid
# footprint beneath it.
W, H = 176, 224
BASE_X, BASE_Y = 88, 214
VARIANTS = 3

BARK = ((30, 22, 40), (54, 38, 62), (82, 58, 90), (112, 82, 116),
        (146, 110, 142))
LEAF = ((10, 42, 44), (18, 70, 60), (30, 104, 70), (58, 144, 84),
        (100, 186, 108))
LEAF_DEEP = ((6, 28, 34), (12, 50, 50), (20, 76, 60), (34, 106, 70),
             (58, 140, 84))
MOSS = ((28, 70, 52), (46, 104, 64), (74, 140, 80), (104, 170, 96),
        (132, 196, 112))
GLOWS = ((76, 194, 255), (193, 82, 244), (244, 108, 191), (150, 236, 200))


def great_tree(variant: int) -> Image.Image:
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lean = (-4, 0, 5)[variant]
    spread = (0, 6, -4)[variant]

    # ------------------------------------------------------------------
    # Roots, running out across the ground. Drawn before the trunk so it
    # grows out of them rather than standing on top of them.
    # ------------------------------------------------------------------
    roots = (
        ((70, 196), (44, 204), (18 - spread, 214), 11, 2.2),
        ((76, 202), (60, 214), (40, 221), 9, 2.0),
        ((104, 198), (132, 204), (158 + spread, 212), 11, 2.2),
        ((100, 204), (118, 214), (140, 220), 9, 2.0),
        ((84, 206), (80, 216), (70, 222), 8, 2.0),
        ((92, 206), (98, 216), (108, 222), 8, 2.0),
    )
    for index, (a, b, c, r0, r1) in enumerate(roots):
        root = Piece(BARK, fur=True, salt=100 + variant * 7 + index,
                     ambient=0.2)
        steps = 10
        previous = None
        for step in range(steps + 1):
            t = step / steps
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]
            radius = r0 + (r1 - r0) * t
            if previous is not None:
                root.capsule(previous[0], (x, y), previous[1], radius)
            previous = ((x, y), radius)
        root.paint(image)

    # ------------------------------------------------------------------
    # Boughs, then the trunk over their bases.
    # ------------------------------------------------------------------
    boughs = (
        ((82 + lean, 128), (48 + lean, 100), (30 + lean, 84), 11, 5),
        ((94 + lean, 124), (126 + lean, 98), (146 + lean, 80), 11, 5),
        ((88 + lean, 118), (84 + lean, 88), (92 + lean, 56), 12, 6),
        ((80 + lean, 140), (60 + lean, 124), (44 + lean, 118), 7, 3),
    )
    for index, (a, b, c, r0, r1) in enumerate(boughs):
        bough = Piece(BARK, fur=True, salt=200 + variant * 5 + index,
                      ambient=0.18)
        previous = None
        for step in range(9):
            t = step / 8
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]
            radius = r0 + (r1 - r0) * t
            if previous is not None:
                bough.capsule(previous[0], (x, y), previous[1], radius)
            previous = ((x, y), radius)
        bough.paint(image)

    trunk = Piece(BARK, fur=True, salt=300 + variant, ambient=0.2)
    # Wide. The crown is eleven tiles across, and a trunk in proportion to
    # an ordinary tree read as a stalk holding up a head of broccoli.
    trunk.capsule((BASE_X, 198), (BASE_X + lean * 0.4, 160), 33, 26)
    trunk.capsule((BASE_X + lean * 0.4, 160), (BASE_X + lean, 118), 26, 24)
    trunk.ellipse((BASE_X - 28, 204), 16, 11)       # the flare into the roots
    trunk.ellipse((BASE_X + 28, 204), 16, 11)
    trunk.paint(image)

    pixels = image.load()

    # Bark: long twisting ridges up the trunk. The twist is what makes it
    # old -- a young trunk grows straight.
    for ridge in range(7):
        phase = ridge * 0.9 + variant
        for y in range(118, 214):
            t = (y - 118) / 96
            half = 24 + 9 * t
            x = round(BASE_X + lean * (1 - t) + (ridge - 3) * half / 3.6
                      + 2.4 * math.sin(y * 0.07 + phase))
            if 0 <= x < W and pixels[x, y][3] and pixels[x, y][:3] in BARK:
                pixels[x, y] = BARK[0 if (y + ridge) % 5 else 1] + (255,)
                if x + 1 < W and pixels[x + 1, y][3]:
                    pixels[x + 1, y] = BARK[3] + (255,)
    # No knots and no hollow. Two dark holes stacked up the middle of a
    # trunk this size read as a pair of eyes the moment they were drawn,
    # and this is a tree with no face. The bark splits instead: one long
    # seam, off to the shaded side.
    for y in range(140, 204):
        x = round(BASE_X + 12 + lean * (1 - (y - 118) / 96)
                  + 1.6 * math.sin(y * 0.11 + variant))
        if pixels[x, y][3]:
            pixels[x, y] = BARK[0] + (255,)
            pixels[x - 1, y] = BARK[1] + (255,)

    # Moss, on the shaded side of the base, where it would actually grow.
    moss = Piece(MOSS, fur=True, rim=False, salt=400 + variant, ambient=0.3)
    for mx, my, rx, ry in ((BASE_X + 22, 200, 8, 5), (BASE_X + 30, 208, 6, 3)):
        moss.ellipse((mx, my), rx, ry)
    moss_image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    moss.paint(moss_image)
    moss_pixels = moss_image.load()
    for (x, y) in moss.pixels:
        if 0 <= x < W and 0 <= y < H and pixels[x, y][3] \
                and _hash(x, y, 41) % 3:
            pixels[x, y] = moss_pixels[x, y]

    # ------------------------------------------------------------------
    # The crown: one dome, and the leaf masses are its surface.
    #
    # Drawn first as thirty separate balls, it came out as a tiered cake
    # -- a top layer of balls, a gap with the trunk showing through it,
    # and a skirt of darker balls underneath. A tree this size carries a
    # single crown. So the dome is one shaded mass, lit like a sphere,
    # and the clumps sit on it as bumps: soft inside the outline, rimmed
    # only where they break the silhouette.
    # ------------------------------------------------------------------
    crown_x, crown_y = BASE_X + lean, 70
    crown_rx, crown_ry = 80, 54
    dome = Piece(LEAF, fur=True, salt=590 + variant, ambient=0.16)
    dome.ellipse((crown_x, crown_y), crown_rx, crown_ry)
    dome.ellipse((crown_x, crown_y + 30), crown_rx * 0.86, 30)
    dome.paint(image)

    clumps = []
    for index in range(46):
        h = _hash(index, variant, 501)
        angle = (h % 1000) / 1000 * math.tau
        reach = math.sqrt(((h >> 10) % 1000) / 1000)
        radius = 9 + (h >> 20) % 9
        cx = crown_x + math.cos(angle) * (crown_rx - radius * 0.6) * reach
        cy = crown_y + 8 + math.sin(angle) * (crown_ry - radius * 0.4) * reach
        cx = max(radius + 3, min(W - radius - 3, cx))
        clumps.append((cy, cx, radius, index, reach))
    clumps.sort()
    for cy, cx, radius, index, reach in clumps:
        below = (cy - crown_y) / crown_ry
        right = (cx - crown_x) / crown_rx
        shade = below * 0.7 + right * 0.4
        ramp = LEAF_DEEP if shade > 0.45 else LEAF
        edge = reach > 0.82
        mass = Piece(ramp, fur=True, rim=edge,
                     salt=600 + variant * 13 + index,
                     ambient=0.3 - 0.12 * max(0.0, shade))
        mass.ellipse((cx, cy), radius * 1.2, radius * 0.95)
        mass.paint(image)

    pixels = image.load()
    # Leaf edges: the outline of a canopy is leaves, not a curve. Sprigs
    # break the top of the silhouette so it does not read as a pebble.
    for y in range(2, 132):
        for x in range(1, W - 1):
            if pixels[x, y][3] and not pixels[x, y - 1][3] \
                    and _hash(x, y, 77) % 3 == 0:
                pixels[x, y - 1] = LEAF[2] + (255,)
                if _hash(x, y, 78) % 2 == 0:
                    pixels[x, y - 2] = LEAF[3] + (255,)

    # Hanging moss from the underside of the crown.
    for strand in range(9):
        h = _hash(strand, variant, 811)
        sx = 24 + (h % 128)
        top = None
        for y in range(80, 140):
            if pixels[sx, y][3] and pixels[sx, y][:3] in LEAF_DEEP:
                top = y
        if top is None:
            continue
        length = 6 + (h >> 8) % 14
        for step in range(length):
            y = top + step
            x = sx + round(math.sin(step * 0.5 + strand) * 0.8)
            if 0 <= x < W and y < H and not pixels[x, y][3]:
                pixels[x, y] = MOSS[1 if step % 3 else 2] + (255,)

    # The Feywild's motes, caught in the crown.
    for index in range(10):
        h = _hash(index, variant, 907)
        x = 18 + h % (W - 36)
        y = 14 + (h >> 9) % 100
        if pixels[x, y][3]:
            glow = GLOWS[(h >> 17) % len(GLOWS)]
            pixels[x, y] = glow + (255,)
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                r, g, b, a = pixels[x + ox, y + oy]
                if a:
                    pixels[x + ox, y + oy] = (
                        (r + glow[0]) // 2, (g + glow[1]) // 2,
                        (b + glow[2]) // 2, 255)

    outlined = _outline(image)
    # The shadow goes underneath everything, and outside the outline.
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse((16, 204, 160, 223),
                                   fill=(6, 26, 30, 150))
    shadow.alpha_composite(outlined)
    return shadow


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for variant in range(VARIANTS):
        great_tree(variant).save(OUT / f"feywild_great_tree_{variant + 1}.png")
    print(f"Wrote {VARIANTS} great trees ({W}x{H}) to {OUT}")


if __name__ == "__main__":
    main()
