"""Generate the desert's ribcage landmark and the orc camp's gear.

* The ribcage: something very large died in the hub's open sand a long
  time ago, and its ribs still stand -- a horned skull on the ground at
  the west end, the spine running east from it half buried, and the
  ribs rising out of the sand in a row that shortens toward the tail.
  Seven tiles long; it fades like the ruin arch when anyone walks
  behind it.
* The orc camp: hide tents, weapon racks, and a war drum, all rough and
  orc-sized, in the camp's own browns and the desert ruin's bleached
  bone for the drum's frame.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
CLEAR = (0, 0, 0, 0)

BONE_PALE = (236, 226, 198, 255)
BONE = (212, 198, 164, 255)
BONE_MID = (176, 160, 126, 255)
BONE_DARK = (124, 108, 80, 255)
OUTLINE = (78, 60, 40, 255)
SOCKET = (60, 44, 30, 255)
SAND_SHADOW = (150, 112, 70, 110)
SAND_DRIFT = (214, 178, 122, 255)
SAND_DRIFT_DARK = (190, 150, 98, 255)

HIDE_DARK = (92, 62, 40, 255)
HIDE = (136, 96, 60, 255)
HIDE_LIT = (170, 128, 84, 255)
HIDE_PATCH = (112, 84, 58, 255)
POLE = (78, 56, 36, 255)
POLE_LIT = (110, 82, 54, 255)
IRON_DARK = (46, 44, 48, 255)
IRON = (96, 94, 98, 255)
IRON_LIT = (150, 148, 150, 255)
DRUM_SKIN = (206, 180, 132, 255)
DRUM_SKIN_DARK = (170, 142, 98, 255)
RED_PAINT = (150, 44, 34, 255)


def _hash(*values: int) -> int:
    h = 2166136261
    for value in values:
        h = ((h ^ (value & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def _thick_curve(image, points, radius_at, fill, outline=OUTLINE):
    """A tapering bone along a polyline, outlined."""
    layer = Image.new("RGBA", image.size, CLEAR)
    draw = ImageDraw.Draw(layer)
    for pass_index, colour in ((0, outline), (1, fill)):
        for index, (x, y) in enumerate(points):
            r = radius_at(index / max(1, len(points) - 1)) + (1 - pass_index)
            draw.ellipse((x - r, y - r, x + r, y + r), fill=colour)
    image.alpha_composite(layer)


def _bezier(a, b, c, steps=24):
    return [((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0],
             (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1])
            for t in (i / steps for i in range(steps + 1))]


def ribcage() -> Image.Image:
    width, height = 112, 84
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.ellipse((6, 70, 108, 83), fill=SAND_SHADOW)

    # Each rib is a hoop: up from the sand on the near side, over, and
    # down into the sand on the far side. The far half goes first and in
    # shadow. Drawn as thick close-set bars they read as a radiator; thin,
    # few and with daylight between them they read as a carcass.
    ribs = ((42, 14), (56, 11), (70, 17), (83, 26), (95, 38))
    for index, (x, top) in enumerate(ribs):
        points = _bezier((x + 11, 64), (x + 12, top), (x + 4, top - 1))
        _thick_curve(image, points, lambda t: 1.6 - t * 0.5, BONE_DARK)

    # The spine, half buried: a row of vertebrae along the sand.
    for index, x in enumerate(range(30, 106, 7)):
        size = 4 - index * 0.25
        draw.ellipse((x - size, 68 - size * 0.7, x + size, 68 + size * 0.7),
                     fill=OUTLINE)
        draw.ellipse((x - size + 1, 68 - size * 0.7, x + size - 1,
                      68 + size * 0.5), fill=BONE_MID)
        draw.point((x - 1, 67), fill=BONE_PALE)
        draw.line((x, 64 - size, x, 67), fill=BONE_DARK)     # the spur

    # The near ribs, big, lit from the west, arching up and over.
    for index, (x, top) in enumerate(ribs):
        if index == 3:
            # One rib snapped: its near half ends in the air.
            points = _bezier((x - 2, 74), (x - 8, top + 4), (x - 4, top + 10))
        else:
            points = _bezier((x - 2, 74), (x - 8, top + 2), (x + 4, top - 1))
        _thick_curve(image, points, lambda t: 2.6 - t * 1.0, BONE)
        # A pale line down the lit side, one pixel in from the outline.
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            draw.line((round(ax) - 1, round(ay), round(bx) - 1, round(by)),
                      fill=BONE_PALE)

    # The skull, lying on the sand at the west end, a horn curling up.
    draw.ellipse((2, 52, 34, 78), fill=OUTLINE)
    draw.ellipse((3, 53, 33, 76), fill=BONE)
    draw.ellipse((5, 54, 24, 66), fill=BONE_PALE)
    draw.polygon(((4, 68), (0, 76), (14, 79), (20, 72)), fill=OUTLINE)
    draw.polygon(((5, 69), (2, 75), (13, 77), (18, 72)), fill=BONE_MID)
    draw.ellipse((12, 60, 20, 67), fill=SOCKET)          # the eye socket
    draw.point((14, 62), fill=OUTLINE)
    for x in (5, 8, 11, 14):
        draw.line((x, 74, x, 77), fill=BONE_PALE)         # teeth
    horn = _bezier((24, 56), (34, 34), (20, 30), steps=18)
    _thick_curve(image, horn, lambda t: 3.0 - t * 2.4, BONE_MID)
    for px, py in horn[1:-5]:
        image.putpixel((round(px) - 1, round(py)), BONE)

    # Sand drifted up against the bones where they meet the ground.
    for x in range(4, 108):
        if _hash(x, 7) % 3 == 0:
            base = 76 if x < 34 else 72
            draw.line((x, base, x + 2, base), fill=SAND_DRIFT_DARK)
            draw.point((x + 1, base - 1), fill=SAND_DRIFT)
    return image


def hide_tent(variant: int) -> Image.Image:
    """An orc tent of stitched hides over crossed poles."""
    width, height = 48, 44
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 36, 46, 43), fill=SAND_SHADOW)
    peak = (24 + (variant - 1) * 2, 6)
    # Crossed poles sticking out of the top.
    draw.line((peak[0] - 5, peak[1] - 6, peak[0] + 3, peak[1] + 4),
              fill=POLE, width=2)
    draw.line((peak[0] + 5, peak[1] - 6, peak[0] - 3, peak[1] + 4),
              fill=POLE, width=2)
    draw.point((peak[0] - 5, peak[1] - 6), fill=POLE_LIT)
    # The hide body: a steep triangle, lit on the west.
    body = (peak, (44, 40), (4, 40))
    draw.polygon(body, fill=HIDE_DARK)
    draw.polygon((peak, (24, 40), (6, 40)), fill=HIDE)
    draw.polygon((peak, (14, 40), (7, 40)), fill=HIDE_LIT)
    # Stitched seams and patches.
    for step in range(4):
        t = 0.3 + step * 0.17
        y = round(peak[1] + (40 - peak[1]) * t)
        left = round(peak[0] + (4 - peak[0]) * t)
        right = round(peak[0] + (44 - peak[0]) * t)
        for x in range(left + 2, right - 1, 3):
            draw.point((x, y), fill=HIDE_DARK)
    draw.polygon(((30, 22), (36, 24), (34, 30), (28, 28)), fill=HIDE_PATCH)
    # The dark doorway flap, pinned open.
    draw.polygon(((peak[0], 18), (30, 40), (19, 40)), fill=(48, 32, 22, 255))
    draw.line((peak[0], 18, 19, 40), fill=HIDE_LIT)
    # A crude red handprint, or a tusk, on the hide.
    if variant != 2:
        draw.rectangle((10, 28, 12, 31), fill=RED_PAINT)
        draw.point((9, 27), fill=RED_PAINT)
        draw.point((13, 27), fill=RED_PAINT)
    else:
        draw.line((12, 30, 15, 25), fill=BONE, width=2)
    # Guy ropes and pegs.
    draw.line((4, 40, 0, 42), fill=POLE)
    draw.line((44, 40, 47, 42), fill=POLE)
    return image


def weapon_rack(variant: int) -> Image.Image:
    """A crude rack of orc axes and spears."""
    width, height = 26, 34
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 28, 24, 33), fill=SAND_SHADOW)
    # Frame: two posts and a crossbar lashed on.
    for x in (3, 22):
        draw.line((x, 31, x, 10), fill=OUTLINE, width=3)
        draw.line((x, 31, x, 10), fill=POLE)
    draw.line((2, 12, 24, 12), fill=OUTLINE, width=3)
    draw.line((2, 12, 24, 12), fill=POLE_LIT)
    draw.line((2, 26, 24, 26), fill=POLE)
    # Weapons leaning in it.
    weapons = ((("axe", 8), ("spear", 13), ("axe", 18)),
               (("spear", 7), ("axe", 12), ("spear", 17)))[variant % 2]
    for kind, x in weapons:
        draw.line((x, 30, x + 1, 4), fill=POLE, width=1)
        if kind == "axe":
            draw.polygon(((x + 1, 5), (x + 6, 3), (x + 6, 11), (x + 1, 9)),
                         fill=IRON_DARK)
            draw.polygon(((x + 2, 5), (x + 5, 4), (x + 5, 10), (x + 2, 8)),
                         fill=IRON)
            draw.line((x + 5, 4, x + 5, 10), fill=IRON_LIT)
        else:
            draw.polygon(((x, 4), (x + 2, 4), (x + 1, 0)), fill=IRON_LIT)
            draw.line((x, 5, x + 2, 5), fill=RED_PAINT)
    return image


def war_drum() -> Image.Image:
    """A big hide drum on a bone frame, a pair of beaters on top."""
    width, height = 30, 34
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 27, 28, 33), fill=SAND_SHADOW)
    # Body: a squat cylinder.
    draw.rectangle((4, 12, 25, 28), fill=OUTLINE)
    draw.rectangle((5, 12, 24, 27), fill=HIDE)
    draw.rectangle((5, 12, 10, 27), fill=HIDE_LIT)
    draw.rectangle((19, 12, 24, 27), fill=HIDE_DARK)
    # Lacing zig-zag down the body.
    for index, x in enumerate(range(6, 24, 3)):
        top, bottom = (14, 25) if index % 2 else (25, 14)
        draw.line((x, top, x + 3, bottom), fill=DRUM_SKIN_DARK)
    # The drum head, seen from above, and the bone rim.
    draw.ellipse((3, 6, 26, 17), fill=OUTLINE)
    draw.ellipse((4, 7, 25, 16), fill=DRUM_SKIN)
    draw.ellipse((7, 8, 18, 13), fill=(222, 200, 156, 255))
    draw.arc((4, 7, 25, 16), 20, 160, fill=DRUM_SKIN_DARK)
    draw.ellipse((12, 10, 16, 13), fill=RED_PAINT)       # painted eye
    # Bone legs.
    for x in (6, 22):
        draw.line((x, 27, x - 2, 32), fill=BONE_MID, width=2)
    # Two beaters crossed on the head.
    draw.line((6, 4, 20, 12), fill=POLE, width=2)
    draw.line((22, 3, 10, 12), fill=POLE, width=2)
    draw.ellipse((4, 2, 8, 6), fill=BONE)
    draw.ellipse((20, 1, 24, 5), fill=BONE)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ribcage().save(OUT / "desert_ribcage.png")
    for variant in range(3):
        hide_tent(variant).save(OUT / f"orc_tent_{variant + 1}.png")
    for variant in range(2):
        weapon_rack(variant).save(OUT / f"orc_weapon_rack_{variant + 1}.png")
    war_drum().save(OUT / "orc_war_drum.png")
    print(f"Wrote the ribcage and the orc camp's gear to {OUT}")


if __name__ == "__main__":
    main()
