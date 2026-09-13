"""Generate the jungle temple's added dressing.

The temple's big rooms were a floor tile and a wall tile repeated to the
edges. What an old building has that a new one does not is damage and
leftovers: cracks running across several slabs rather than inside one,
slabs gone altogether, moss working in from the walls, the bones of
whoever did not get out, and carving on the walls it was built to carry.

* Floor pieces (cracks, missing slabs, moss, bones) lie flat and are
  walked over.
* Wall carvings are relief panels set into the wall face, like the
  carved skulls already there.
* Toppled pillars and broken stumps for the skeleton hall.
* A grand arch for the sanctum: the desert ruin's arch, which is the
  same kind of building, cut in the temple's green-grey stone, whole,
  and mossed.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_desert_props  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
CLEAR = (0, 0, 0, 0)

FLOOR = (65, 70, 57, 255)
GROOVE = (43, 52, 47, 255)
FLOOR_LIT = (86, 87, 65, 255)
VOID = (18, 24, 22, 255)
WALL = (48, 59, 51, 255)
WALL_DARK = (27, 38, 37, 255)
WALL_LIT = (76, 81, 61, 255)
STONE_PALE = (108, 110, 82, 255)
MOSS_DARK = (30, 62, 38, 255)
MOSS = (35, 72, 43, 255)
MOSS_LIT = (58, 102, 56, 255)
GOLD = (108, 100, 62, 255)
GOLD_LIT = (150, 134, 76, 255)
BONE = (214, 206, 176, 255)
BONE_LIT = (236, 230, 204, 255)
BONE_DARK = (150, 142, 116, 255)


def _hash(*values: int) -> int:
    h = 2166136261
    for value in values:
        h = ((h ^ (value & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def floor_crack(variant: int) -> Image.Image:
    """A crack running across several slabs, lit along its upper lip."""
    image = Image.new("RGBA", (30, 18), CLEAR)
    pixels = image.load()
    x, y = 1.0, 4.0 + variant * 4
    points = []
    for step in range(28):
        h = _hash(step, variant, 7)
        x += 1.0
        y += ((h % 5) - 2) * 0.55
        y = max(2.0, min(15.0, y))
        points.append((round(x), round(y)))
    for index, (px, py) in enumerate(points):
        pixels[px, py] = VOID
        if index % 3 == 0 and py + 1 < 18:
            pixels[px, py + 1] = GROOVE
        if py - 1 >= 0 and not pixels[px, py - 1][3]:
            pixels[px, py - 1] = FLOOR_LIT
        # Branches.
        if _hash(index, variant, 11) % 9 == 0:
            bx, by = px, py
            for _ in range(4):
                bx += 1
                by += 1 if _hash(bx, variant) % 2 else -1
                if 0 <= bx < 30 and 0 <= by < 18:
                    pixels[bx, by] = GROOVE
    return image


def missing_slabs(variant: int) -> Image.Image:
    """Where a slab or two has gone: a sunken bed of earth and broken
    pieces. Kept well short of black -- a black hole in a temple floor
    reads as a pit to fall down, and these are not."""
    image = Image.new("RGBA", (24, 18), CLEAR)
    draw = ImageDraw.Draw(image)
    shapes = (((2, 3), (15, 2), (21, 6), (20, 15), (6, 16), (1, 10)),
              ((4, 2), (20, 4), (22, 12), (13, 16), (2, 13)))
    outline = shapes[variant % len(shapes)]
    draw.polygon(outline, fill=(40, 44, 36, 255))
    inner = [(round((px - 12) * 0.8 + 12), round((py - 9) * 0.75 + 10))
             for px, py in outline]
    draw.polygon(inner, fill=(52, 54, 42, 255))
    # The lip of the slabs around it, lit on the far side and in shadow
    # on the near.
    for index in range(len(outline)):
        a, b = outline[index], outline[(index + 1) % len(outline)]
        colour = FLOOR_LIT if a[1] + b[1] < 18 else GROOVE
        draw.line((a, b), fill=colour)
    # A few pieces of broken slab lying in it.
    for index in range(4):
        h = _hash(index, variant, 3)
        cx, cy = 6 + h % 12, 7 + (h >> 8) % 6
        draw.rectangle((cx, cy, cx + 2, cy + 1), fill=FLOOR)
        draw.point((cx, cy), fill=FLOOR_LIT)
    return image


def moss_patch(variant: int) -> Image.Image:
    """Moss working in across the floor from a wall."""
    image = Image.new("RGBA", (26, 16), CLEAR)
    pixels = image.load()
    blobs = 5 + variant
    for index in range(blobs):
        h = _hash(index, variant, 19)
        cx, cy = 3 + h % 20, 3 + (h >> 8) % 10
        radius = 2 + (h >> 16) % 3
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius - 1, cx + radius + 2):
                if not (0 <= x < 26 and 0 <= y < 16):
                    continue
                d = ((x - cx) / (radius + 1)) ** 2 + ((y - cy) / radius) ** 2
                if d > 1.0 or _hash(x, y, variant) % 5 == 0:
                    continue
                colour = MOSS_LIT if (y < cy and x < cx) else (
                    MOSS if d < 0.6 else MOSS_DARK)
                pixels[x, y] = colour
    return image


def bones(variant: int) -> Image.Image:
    """Somebody who did not get out: a skull and a few long bones."""
    image = Image.new("RGBA", (22, 14), CLEAR)
    draw = ImageDraw.Draw(image)

    def long_bone(x0, y0, x1, y1):
        draw.line((x0, y0, x1, y1), fill=BONE_DARK, width=2)
        draw.line((x0, y0 - 1, x1, y1 - 1), fill=BONE)
        for ex, ey in ((x0, y0), (x1, y1)):
            draw.rectangle((ex - 1, ey - 1, ex + 1, ey), fill=BONE_LIT)

    layouts = (
        ((2, 10, 13, 7), (6, 12, 17, 12)),
        ((3, 6, 10, 12), (11, 11, 20, 9)),
        ((1, 12, 9, 12), (12, 5, 19, 11)),
    )
    for bone in layouts[variant]:
        long_bone(*bone)
    # The skull.
    sx, sy = ((15, 3), (4, 1), (4, 3))[variant]
    draw.ellipse((sx, sy, sx + 6, sy + 6), fill=BONE_DARK)
    draw.ellipse((sx, sy, sx + 5, sy + 5), fill=BONE)
    draw.point((sx + 1, sy + 1), fill=BONE_LIT)
    draw.point((sx + 2, sy + 3), fill=VOID)
    draw.point((sx + 4, sy + 3), fill=VOID)
    draw.line((sx + 2, sy + 6, sx + 4, sy + 6), fill=BONE_DARK)
    # A couple of small bones.
    for index in range(3):
        h = _hash(index, variant, 23)
        x, y = 2 + h % 18, 2 + (h >> 8) % 10
        draw.line((x, y, x + 2, y), fill=BONE)
    return image


def wall_carving(variant: int) -> Image.Image:
    """A relief panel set into the wall face."""
    image = Image.new("RGBA", (16, 22), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 15, 21), fill=WALL_DARK)
    draw.rectangle((1, 1, 14, 20), fill=WALL)
    draw.line((1, 1, 14, 1), fill=WALL_LIT)
    draw.line((1, 1, 1, 20), fill=WALL_LIT)
    draw.rectangle((3, 3, 12, 18), fill=WALL_DARK)      # the recess
    draw.rectangle((3, 3, 12, 4), fill=(20, 28, 26, 255))
    if variant == 0:
        # A coiled serpent.
        for t in range(40):
            angle = t * 0.42
            r = 3.6 - t * 0.075
            x = round(7.5 + math.cos(angle) * r)
            y = round(11 + math.sin(angle) * r * 1.3)
            draw.point((x, y), fill=WALL_LIT if t % 5 else GOLD)
        draw.point((8, 6), fill=GOLD_LIT)
    elif variant == 1:
        # A rayed sun.
        draw.ellipse((5, 8, 10, 13), fill=GOLD)
        draw.point((6, 9), fill=GOLD_LIT)
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x = round(7.5 + math.cos(rad) * 4.5)
            y = round(10.5 + math.sin(rad) * 5.5)
            draw.point((x, y), fill=WALL_LIT)
    else:
        # A stepped glyph face.
        draw.rectangle((5, 6, 10, 15), fill=WALL)
        draw.line((5, 6, 10, 6), fill=WALL_LIT)
        draw.point((6, 9), fill=GOLD)
        draw.point((9, 9), fill=GOLD)
        draw.line((6, 13, 9, 13), fill=WALL_DARK)
        draw.rectangle((4, 16, 11, 17), fill=WALL_LIT)
    # Moss in the recess's bottom corner.
    draw.point((4, 18), fill=MOSS)
    draw.point((5, 18), fill=MOSS_DARK)
    draw.line((0, 21, 15, 21), fill=WALL_DARK)
    return image


def toppled_pillar(variant: int) -> Image.Image:
    """A pillar lying where it came down, drums rolled a little apart."""
    image = Image.new("RGBA", (48, 22), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 15, 46, 21), fill=(20, 26, 22, 110))
    spans = (((1, 15), (17, 31), (33, 46)), ((2, 20), (22, 45), None),
             ((1, 12), (14, 28), (31, 45)))[variant]
    for index, span in enumerate(spans):
        if span is None:
            continue
        left, right = span
        drop = 0 if index == 0 else 1
        top = 5 + drop
        draw.rectangle((left, top, right, top + 11), fill=WALL_DARK)
        draw.rectangle((left, top + 1, right, top + 9), fill=WALL)
        draw.line((left, top + 1, right, top + 1), fill=WALL_LIT)
        draw.line((left, top + 2, right, top + 2), fill=STONE_PALE)
        for band in range(left + 5, right - 1, 5):
            draw.line((band, top + 3, band, top + 9), fill=WALL_DARK)
        draw.ellipse((left, top, left + 4, top + 11), fill=WALL_DARK)
        draw.ellipse((left + 1, top + 1, left + 4, top + 10), fill=WALL_LIT)
        for x in range(left + 2, right, 3):
            if _hash(x, variant, index) % 3 == 0:
                draw.point((x, top + 1), fill=MOSS)
    return image


def pillar_stump(variant: int) -> Image.Image:
    """The base a pillar broke off, jagged at the top."""
    image = Image.new("RGBA", (20, 28), CLEAR)
    draw = ImageDraw.Draw(image)
    height = (12, 16, 9)[variant]
    top = 25 - height
    draw.ellipse((1, 21, 19, 27), fill=(20, 26, 22, 110))
    draw.rectangle((0, 21, 19, 26), fill=WALL_DARK)
    draw.rectangle((1, 21, 18, 23), fill=WALL_LIT)
    draw.rectangle((3, top, 16, 22), fill=WALL_DARK)
    for x in range(4, 16):
        light = 1.0 - abs((x - 4) / 11 - 0.3) * 1.8
        colour = STONE_PALE if light > 0.7 else WALL_LIT if light > 0.35 \
            else WALL
        draw.line((x, top + 2, x, 21), fill=colour)
    # The break: a jagged top.
    for x in range(3, 17):
        jag = _hash(x, variant) % 4
        for y in range(top, top + jag):
            image.putpixel((x, y), CLEAR)
        image.putpixel((x, top + jag), STONE_PALE)
    for y in range(top + 6, 21, 4):
        draw.line((4, y, 15, y), fill=WALL)
    draw.point((5, 20), fill=MOSS)
    draw.point((6, 20), fill=MOSS_DARK)
    return image


def grand_arch() -> Image.Image:
    """The desert ruin's arch, recut in temple stone, whole and mossed."""
    gen = generate_desert_props
    saved = (gen.RUIN, gen.RUIN_LIT, gen.RUIN_PALE, gen.RUIN_DARK,
             gen.RUIN_SHADE, gen.CAST)
    # The generator reads its stone from module globals; point them at the
    # temple's stone for the one call and put them back.
    gen.RUIN, gen.RUIN_LIT, gen.RUIN_PALE = WALL, WALL_LIT, STONE_PALE
    gen.RUIN_DARK, gen.RUIN_SHADE = (40, 50, 44, 255), WALL_DARK
    gen.CAST = (12, 18, 16, 110)
    try:
        image = gen.desert_ruin_arch()
    finally:
        (gen.RUIN, gen.RUIN_LIT, gen.RUIN_PALE, gen.RUIN_DARK,
         gen.RUIN_SHADE, gen.CAST) = saved
    pixels = image.load()
    width, height = image.size
    # Whole: fill the corner of the cornice the desert one lost.
    draw = ImageDraw.Draw(image)
    draw.rectangle((62, 0, 79, 6), fill=(40, 50, 44, 255))
    draw.rectangle((62, 0, 78, 4), fill=WALL)
    draw.line((62, 0, 78, 0), fill=WALL_LIT)
    for x in range(69, 77):
        for y in range(6, 6 + (x - 68)):
            draw.point((x, y), fill=WALL if (y - 6) % 7 > 1 else WALL_DARK)
    # Moss down the shaded pier and along the cornice's top.
    for y in range(0, height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if not a:
                continue
            below = y + 1 < height and pixels[x, y + 1][3]
            if y < 3 and _hash(x, y, 61) % 3 == 0:
                pixels[x, y] = MOSS_LIT if _hash(x, 62) % 2 else MOSS
            elif x > 64 and y > 40 and _hash(x, y, 63) % 9 == 0:
                pixels[x, y] = MOSS_DARK
            elif not below and _hash(x, y, 64) % 4 == 0 and y > 90:
                pixels[x, y] = MOSS
    # The same glyph gold as the monuments on the keystone.
    draw.point((40, 0), fill=GOLD_LIT)
    draw.rectangle((39, 1, 41, 3), fill=GOLD)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for variant in range(3):
        floor_crack(variant).save(OUT / f"temple_floor_crack_{variant + 1}.png")
        moss_patch(variant).save(OUT / f"temple_moss_{variant + 1}.png")
        bones(variant).save(OUT / f"temple_bones_{variant + 1}.png")
        wall_carving(variant).save(OUT / f"temple_wall_carving_{variant + 1}.png")
        toppled_pillar(variant).save(
            OUT / f"temple_toppled_pillar_{variant + 1}.png")
        pillar_stump(variant).save(OUT / f"temple_pillar_stump_{variant + 1}.png")
    for variant in range(2):
        missing_slabs(variant).save(
            OUT / f"temple_missing_slabs_{variant + 1}.png")
    grand_arch().save(OUT / "temple_grand_arch.png")
    print(f"Wrote temple dressing to {OUT}")


if __name__ == "__main__":
    main()
