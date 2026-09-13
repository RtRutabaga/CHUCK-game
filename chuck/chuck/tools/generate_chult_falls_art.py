"""Generate the hidden Chult waterfall's art: the cliff and falls, and boulders.

The reference is a jungle plunge pool: a dark, wet rock face furred with
ferns and moss, green crowding in over its top, a white fall dropping
out of a notch in the lip into a small clear pool, mist boiling up where
it lands, and round boulders sitting at the water's edge.

From this game's vantage -- south of everything, above it -- the cliff is
a face seen from the front, rising up the screen from the pool's far
shore; the fall is a column down that face; the mist spreads left and
right along its foot and over the top of the water, which is the part of
the pool nearest the cliff and so the part furthest from us.

* The cliff and falls are one animated prop, twenty tiles wide: the
  water only reads as falling if the streaks in it move, and the mist
  only reads as mist if it breathes.
* Boulders: rounded, mossy on top, lit from the upper left, three cuts.
  A second set sits in the water with a ripple ring round its foot.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
CLEAR = (0, 0, 0, 0)

ROCK_DEEP = (26, 30, 30)
ROCK_DARK = (44, 50, 48)
ROCK = (66, 74, 68)
ROCK_LIT = (96, 106, 92)
ROCK_WET = (34, 42, 44)
MOSS_DARK = (27, 94, 40)
MOSS = (51, 125, 52)
MOSS_LIT = (92, 160, 72)
FERN = (37, 105, 49)
FERN_LIT = (68, 140, 62)
CANOPY_DARK = (13, 49, 31)
CANOPY = (22, 77, 40)
CANOPY_LIT = (37, 105, 49)
WATER_WHITE = (236, 244, 246)
WATER_PALE = (196, 222, 228)
WATER_BLUE = (140, 186, 200)
WATER_SHADE = (96, 146, 162)

CLIFF_W, CLIFF_H = 320, 152
FALL_X = 160          # the notch the water comes over
FALL_TOP = 26
FALL_BASE = 138
FRAMES = 4


def _hash(*values: int) -> int:
    h = 2166136261
    for value in values:
        h = ((h ^ (value & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def _rgba(colour, alpha=255):
    return colour + (alpha,)


def _cliff_base() -> Image.Image:
    """Everything that does not move: rock, ledges, green."""
    image = Image.new("RGBA", (CLIFF_W, CLIFF_H), CLEAR)
    pixels = image.load()

    def lip(x):
        wave = math.sin(x * 0.045) * 6 + math.sin(x * 0.13 + 1.3) * 3
        notch = 10 * math.exp(-((x - FALL_X) / 18) ** 2)
        return 22 + wave - notch

    def inset(y):
        # The face narrows toward the top, raggedly: jungle eats into
        # both sides at different depths rather than along a ruled line.
        base = 40 - y * 0.26
        return max(0, int(base + math.sin(y * 0.21) * 5
                          + math.sin(y * 0.07 + 2) * 6))

    def foot(x):
        # The foot is not a line: ledges and fallen blocks step it.
        return CLIFF_H - 4 - int(abs(math.sin(x * 0.07)) * 5
                                 + (_hash(x // 9, 3) % 4))

    # Rock in blocks: columns of jointed stone, each block a shade, so
    # the face reads as broken basalt rather than as painted stripes.
    for y in range(CLIFF_H):
        left = inset(y)
        right = CLIFF_W - inset(y + 7)
        for x in range(left, right):
            if y < lip(x) or y > foot(x):
                continue
            column = (x + (_hash(y // 11, 5) % 5)) // 9
            shift = _hash(column, 9) % 13
            block = (y + shift) // 13
            h = _hash(column, block, 17) % 100
            along = (x + (_hash(y // 11, 5) % 5)) % 9
            down = (y + shift) % 13
            if down == 0:
                colour = ROCK_LIT            # the top of a block, lit
            elif along == 0 or down == 12:
                colour = ROCK_DEEP           # the joints
            elif h < 22:
                colour = ROCK_LIT
            elif h < 62:
                colour = ROCK
            else:
                colour = ROCK_DARK
            # Light from the upper left; the far right is in shade.
            if x > CLIFF_W * 0.64 and colour in (ROCK, ROCK_LIT):
                colour = ROCK_DARK if h % 2 else ROCK
            # The rock the fall has kept wet for ever.
            if abs(x - FALL_X) < 30 + (y - FALL_TOP) * 0.1:
                colour = ROCK_WET if colour != ROCK_LIT else ROCK_DARK
            pixels[x, y] = _rgba(colour)
    draw = ImageDraw.Draw(image)
    # Moss and fern clumps, heaviest on the lit left.
    for index in range(95):
        h = _hash(index, 23)
        x = 8 + h % (CLIFF_W - 16)
        y = 24 + (h >> 8) % (CLIFF_H - 36)
        if abs(x - FALL_X) < 24 or not pixels[x, y][3]:
            continue
        size = 2 + (h >> 16) % 4
        colour = MOSS if x < CLIFF_W * 0.64 else MOSS_DARK
        draw.ellipse((x - size, y - size // 2, x + size, y + size // 2),
                     fill=_rgba(colour))
        draw.point((x - size // 2, y - 1), fill=_rgba(MOSS_LIT))
        if h % 3 == 0:
            for step in range(7):
                draw.point((x + step - 3, y + 1 + abs(step - 3) // 2),
                           fill=_rgba(FERN_LIT if step % 2 else FERN))
    # Vines hanging from the lip.
    for index in range(20):
        h = _hash(index, 37)
        x = 12 + h % (CLIFF_W - 24)
        if abs(x - FALL_X) < 22:
            continue
        top = int(lip(x)) - 2
        length = 18 + (h >> 8) % 60
        for step in range(length):
            vx = x + round(math.sin(step * 0.3 + index) * 1.2)
            vy = top + step
            if 0 <= vx < CLIFF_W and vy < foot(vx) - 2 and pixels[vx, vy][3]:
                draw.point((vx, vy), fill=_rgba(MOSS_DARK if step % 3
                                                else MOSS))
    # The jungle over the lip and down both ragged sides.
    for index in range(110):
        h = _hash(index, 51)
        if index < 50:
            x = h % CLIFF_W
            cy = int(lip(x)) - 1 - (h >> 8) % 10
            if abs(x - FALL_X) < 13 and cy < 28:
                continue
        else:
            y = (h >> 8) % (CLIFF_H - 6)
            left_side = index % 2 == 0
            edge = inset(y) if left_side else CLIFF_W - inset(y + 7)
            x = edge + ((h >> 4) % 9 - 4)
            cy = y
        radius = 4 + (h >> 16) % 7
        draw.ellipse((x - radius, cy - radius, x + radius, cy + radius),
                     fill=_rgba(CANOPY_DARK))
        draw.ellipse((x - radius + 1, cy - radius, x + radius - 2,
                      cy + radius - 3), fill=_rgba(CANOPY))
        draw.ellipse((x - radius + 2, cy - radius + 1, x, cy - 1),
                     fill=_rgba(CANOPY_LIT))
    # Fallen blocks at the foot, half in the water.
    for index in range(9):
        h = _hash(index, 91)
        x = 30 + h % (CLIFF_W - 60)
        if abs(x - FALL_X) < 20:
            continue
        y = foot(x) - 1
        w = 6 + (h >> 8) % 8
        draw.ellipse((x - w, y - 5, x + w, y + 3), fill=_rgba(ROCK_DEEP))
        draw.ellipse((x - w + 1, y - 5, x + w - 2, y + 1), fill=_rgba(ROCK))
        draw.line((x - w + 2, y - 4, x, y - 5), fill=_rgba(ROCK_LIT))
    return image


def cliff_and_falls(frame: int) -> Image.Image:
    image = _cliff_base()
    layer = Image.new("RGBA", image.size, CLEAR)
    draw = ImageDraw.Draw(layer)
    phase = frame / FRAMES
    for y in range(FALL_TOP, FALL_BASE):
        t = (y - FALL_TOP) / (FALL_BASE - FALL_TOP)
        half = 7 + t * 9
        wobble = math.sin(y * 0.2 + phase * math.tau) * 0.8
        left, right = FALL_X - half + wobble, FALL_X + half + wobble
        for x in range(int(left), int(right) + 1):
            across = (x - left) / max(1, right - left)
            edge = abs(across - 0.5) * 2
            streak = (y * 0.5 - phase * 18 + (x - FALL_X) * 1.7) % 7
            if edge > 0.82:
                colour, alpha = WATER_SHADE, 215
            elif streak < 1.2:
                colour, alpha = WATER_BLUE, 240
            elif streak < 3.5:
                colour, alpha = WATER_PALE, 250
            else:
                colour, alpha = WATER_WHITE, 255
            draw.point((x, y), fill=_rgba(colour, alpha))
    draw.ellipse((FALL_X - 9, FALL_TOP - 3, FALL_X + 9, FALL_TOP + 3),
                 fill=_rgba(WATER_WHITE))
    image.alpha_composite(layer)
    # Mist: white, and bright where it is thick, in several soft layers
    # so it is a cloud over rock and water rather than a grey blot.
    mist = Image.new("RGBA", image.size, CLEAR)
    md = ImageDraw.Draw(mist)
    for index in range(22):
        h = _hash(index, 71)
        spread = (h % 110) - 55
        t = (index / 22 + phase) % 1.0
        cx = FALL_X + spread * (0.45 + t * 0.7)
        cy = FALL_BASE + 6 - t * 22 + (h >> 8) % 5
        radius = 4 + t * 9 + (h >> 12) % 4
        alpha = round(210 * (1 - t) ** 1.5)
        md.ellipse((cx - radius, cy - radius * 0.55, cx + radius,
                    cy + radius * 0.55), fill=_rgba(WATER_WHITE, alpha))
    # Spray: bright points thrown out of the cloud.
    for index in range(40):
        h = _hash(index, frame, 83)
        x = FALL_X + (h % 80) - 40
        y = FALL_BASE - (h >> 8) % 24
        md.point((x, y), fill=_rgba(WATER_WHITE, 230))
    for x in range(FALL_X - 30, FALL_X + 31):
        if _hash(x, frame) % 3:
            md.point((x, FALL_BASE + 3 + _hash(x, 5) % 4),
                     fill=_rgba(WATER_WHITE, 240))
    image.alpha_composite(mist)
    return image


def boulder(variant: int, in_water: bool) -> Image.Image:
    width, height = 24, 20
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    shapes = ((2, 4, 21, 18), (4, 2, 20, 18), (1, 7, 22, 18))
    x0, y0, x1, y1 = shapes[variant]
    if in_water:
        draw.ellipse((x0 - 1, y1 - 4, x1 + 1, y1 + 1),
                     fill=_rgba(WATER_PALE, 170))
    else:
        draw.ellipse((x0 + 2, y1 - 3, x1 + 2, y1 + 1), fill=(10, 16, 10, 90))
    draw.ellipse((x0, y0, x1, y1), fill=_rgba(ROCK_DEEP))
    draw.ellipse((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=_rgba(ROCK))
    draw.ellipse((x0 + 2, y0 + 1, (x0 + x1) // 2 + 2, (y0 + y1) // 2),
                 fill=_rgba(ROCK_LIT))
    draw.arc((x0 + 1, y0 + 1, x1 - 1, y1 - 1), 20, 160,
             fill=_rgba(ROCK_DARK))
    # Moss on top.
    for index in range(7):
        h = _hash(index, variant, 3)
        x = x0 + 3 + h % max(1, (x1 - x0 - 6))
        y = y0 + 1 + (h >> 8) % 3
        draw.point((x, y), fill=_rgba(MOSS if h % 2 else MOSS_LIT))
        draw.point((x + 1, y), fill=_rgba(MOSS_DARK))
    if in_water:
        draw.line((x0 - 2, y1, x1 + 2, y1), fill=_rgba(WATER_WHITE, 200))
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for frame in range(FRAMES):
        cliff_and_falls(frame).save(OUT / f"chult_falls_{frame + 1}.png")
    for variant in range(3):
        boulder(variant, False).save(OUT / f"chult_boulder_{variant + 1}.png")
        boulder(variant, True).save(
            OUT / f"chult_boulder_water_{variant + 1}.png")
    print(f"Wrote the Chult falls art to {OUT}")


if __name__ == "__main__":
    main()
