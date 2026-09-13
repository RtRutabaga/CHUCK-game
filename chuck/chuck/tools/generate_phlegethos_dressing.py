"""Generate Phlegethos's added dressing.

The basalt between Phlegethos's lava pools was one cracked tile, a few
fissures and not much else. Hell should have things lying about in it:

* bone heaps, pale against the dark red rock -- solid;
* clusters of rusted iron spikes driven into the basalt -- solid;
* ember cracks, wider than the fissure tiles and glowing -- flat;
* vents breathing a slow column of smoke -- walked past, animated.

And for the fortress approach, towers and banners on the fortress wall
either side of the gate: the wall's own iron-black brick with ember
glints in it, red light in the slits, and black cloth with an ember
device, so the fortress says whose it is the way the castle out in the
desert does.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_castle_banner  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
CLEAR = (0, 0, 0, 0)

BASALT = (58, 35, 30, 255)
BASALT_DARK = (28, 22, 23, 255)
BASALT_LIT = (76, 43, 32, 255)
EMBER_DARK = (112, 28, 13, 255)
EMBER = (196, 70, 20, 255)
EMBER_HOT = (246, 150, 50, 255)
EMBER_WHITE = (255, 222, 150, 255)
BONE = (196, 184, 156, 255)
BONE_LIT = (226, 216, 190, 255)
BONE_DARK = (130, 116, 96, 255)
SOOT = (40, 30, 28, 255)
IRON_DARK = (30, 26, 28, 255)
IRON = (62, 50, 48, 255)
IRON_LIT = (98, 78, 66, 255)
RUST = (122, 62, 38, 255)
WALL = (44, 40, 46, 255)
WALL_DARK = (26, 24, 30, 255)
WALL_LIT = (66, 60, 68, 255)
SLIT_GLOW = (220, 70, 30, 255)

INFERNAL_BANNER = {
    "cloth_dark": (30, 12, 14, 255),
    "cloth": (54, 18, 20, 255),
    "cloth_lit": (84, 26, 26, 255),
    "trim": (196, 90, 30, 255),
    "trim_dark": (130, 50, 20, 255),
    "device": (240, 150, 50, 255),
}


def _hash(*values: int) -> int:
    h = 2166136261
    for value in values:
        h = ((h ^ (value & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def bone_heap(variant: int) -> Image.Image:
    """A heap of old bones with a skull or two on top."""
    image = Image.new("RGBA", (24, 20), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.ellipse((1, 12, 23, 19), fill=SOOT)
    for index in range(9 + variant):
        h = _hash(index, variant, 3)
        x0 = 2 + h % 14
        y0 = 9 + (h >> 8) % 8
        dx = 4 + (h >> 12) % 6
        dy = ((h >> 16) % 5) - 2
        draw.line((x0, y0, x0 + dx, y0 + dy), fill=BONE_DARK, width=2)
        draw.line((x0, y0 - 1, x0 + dx, y0 + dy - 1), fill=BONE)
        draw.point((x0, y0 - 1), fill=BONE_LIT)
        draw.point((x0 + dx, y0 + dy - 1), fill=BONE_LIT)
    skulls = ((9, 4), (14, 7)) if variant != 1 else ((6, 6),)
    for sx, sy in skulls:
        draw.ellipse((sx - 1, sy - 1, sx + 6, sy + 6), fill=BONE_DARK)
        draw.ellipse((sx, sy - 1, sx + 5, sy + 4), fill=BONE)
        draw.point((sx + 1, sy), fill=BONE_LIT)
        draw.rectangle((sx + 1, sy + 2, sx + 2, sy + 3), fill=SOOT)
        draw.rectangle((sx + 3, sy + 2, sx + 4, sy + 3), fill=SOOT)
        draw.line((sx + 1, sy + 5, sx + 4, sy + 5), fill=BONE_DARK)
    return image


def iron_spikes(variant: int) -> Image.Image:
    """Rusted iron stakes driven into the rock at angles."""
    image = Image.new("RGBA", (22, 28), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 22, 20, 27), fill=SOOT)
    stakes = (((5, 24, 3, 6), (11, 25, 11, 1), (17, 24, 19, 8)),
              ((7, 25, 5, 3), (14, 24, 16, 5)),
              ((4, 25, 6, 9), (10, 24, 9, 2), (15, 25, 17, 4),
               (19, 24, 20, 13)))[variant]
    for bx, by, tx, ty in stakes:
        # Dark outline, iron body, a lit western edge: without the lit
        # edge a black stake on black rock is not there at all.
        draw.line((bx, by, tx, ty), fill=IRON_DARK, width=4)
        draw.line((bx, by, tx, ty), fill=IRON, width=2)
        draw.line((bx - 1, by, tx - 1, ty), fill=IRON_LIT)
        draw.point((tx, ty - 1), fill=(150, 126, 104, 255))
        # Rust down the lower half.
        for step in range(3):
            t = 0.55 + step * 0.15
            x = round(bx + (tx - bx) * t)
            y = round(by + (ty - by) * t)
            draw.point((x, y), fill=RUST)
        draw.rectangle((bx - 2, by - 1, bx + 1, by), fill=BASALT_LIT)
    return image


def ember_crack(variant: int) -> Image.Image:
    """A wide crack with the fire showing through it."""
    image = Image.new("RGBA", (32, 18), CLEAR)
    pixels = image.load()
    x, y = 2.0, 5.0 + variant * 3
    for step in range(28):
        h = _hash(step, variant, 13)
        x += 1.0
        y = max(3.0, min(14.0, y + ((h % 5) - 2) * 0.6))
        px, py = round(x), round(y)
        width = 1 if step < 3 or step > 24 else 2
        for dy in range(-1, width + 1):
            yy = py + dy
            if not 0 <= yy < 18:
                continue
            if dy == -1:
                colour = BASALT_DARK
            elif dy == width:
                colour = EMBER_DARK
            else:
                colour = EMBER_HOT if (step + dy) % 4 else EMBER_WHITE
                if width == 1:
                    colour = EMBER
            pixels[px, yy] = colour
        # The glow on the rock either side.
        for gy in (py - 2, py + width + 1):
            if 0 <= gy < 18 and not pixels[px, gy][3] and h % 3 == 0:
                pixels[px, gy] = (92, 40, 28, 255)
    return image


VENT_FRAMES = 6


def vent(frame: int) -> Image.Image:
    """A vent in the rock and the slow smoke coming off it."""
    width, height = 20, 44
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    # The vent: a ragged split in the rock with the glow down in it. Not
    # a ring -- concentric rounds with a red centre read as an eye.
    draw.polygon(((2, 40), (6, 37), (10, 38), (15, 36), (18, 39), (14, 42),
                  (8, 43), (4, 42)), fill=BASALT_LIT)
    draw.polygon(((4, 40), (7, 38), (11, 39), (15, 37), (16, 39), (13, 41),
                  (8, 42)), fill=BASALT_DARK)
    draw.line((6, 40, 9, 40, 12, 39, 14, 39), fill=EMBER_DARK)
    draw.point((10, 40), fill=EMBER)
    draw.point((13, 39), fill=EMBER)
    # Smoke: puffs that rise and spread, cycling through the frames.
    phase = frame / VENT_FRAMES
    for puff in range(5):
        t = (puff / 5 + phase) % 1.0
        cy = 36 - t * 34
        cx = 10 + math.sin(t * 5 + puff) * (1 + t * 3)
        radius = 2 + t * 4
        alpha = round(150 * (1 - t) ** 1.2)
        if alpha < 12:
            continue
        shade = 70 + round(t * 30)
        colour = (shade, shade - 8, shade - 10, alpha)
        box = (cx - radius, cy - radius * 0.8, cx + radius, cy + radius * 0.8)
        layer = Image.new("RGBA", (width, height), CLEAR)
        ImageDraw.Draw(layer).ellipse(box, fill=colour)
        image.alpha_composite(layer)
    return image


TOWER_W, TOWER_H = 40, 104


def infernal_tower() -> Image.Image:
    """A square tower of the fortress wall's brick, spiked at the top."""
    image = Image.new("RGBA", (TOWER_W, TOWER_H), CLEAR)
    draw = ImageDraw.Draw(image)
    left, right, top = 2, TOWER_W - 3, 14
    draw.rectangle((left - 1, top - 1, right + 1, TOWER_H - 1), fill=WALL_DARK)
    draw.rectangle((left, top, right, TOWER_H - 4), fill=WALL)
    for course, y in enumerate(range(top + 3, TOWER_H - 4, 5)):
        draw.line((left, y, right, y), fill=WALL_DARK)
        shift = 0 if course % 2 else 5
        for x in range(left + shift, right, 10):
            draw.line((x, y - 4, x, y - 1), fill=WALL_DARK)
        draw.line((left, y - 4, left + 8, y - 4), fill=WALL_LIT)
        # Embers caught in the joints, the way the wall has them.
        h = _hash(course, 5)
        ex = left + 3 + h % (right - left - 6)
        draw.point((ex, y), fill=EMBER if h % 3 else EMBER_HOT)
    # Shaded east side.
    draw.rectangle((right - 5, top, right, TOWER_H - 4), fill=WALL_DARK)
    # Spiked merlons: horn-like points rather than square teeth.
    draw.rectangle((left - 2, top - 2, right + 2, top + 5), fill=WALL_DARK)
    draw.line((left - 2, top - 2, right + 2, top - 2), fill=WALL_LIT)
    for x in range(left, right + 1, 7):
        draw.polygon(((x, top - 2), (x + 5, top - 2), (x + 3, 1)),
                     fill=WALL_DARK)
        draw.line((x + 1, top - 3, x + 3, 2), fill=WALL_LIT)
    # Slit windows with the fire inside.
    for y in (34, 62):
        draw.rectangle((17, y, 21, y + 13), fill=WALL_DARK)
        draw.rectangle((18, y + 1, 20, y + 12), fill=EMBER_DARK)
        draw.line((19, y + 2, 19, y + 11), fill=SLIT_GLOW)
        draw.point((19, y + 6), fill=EMBER_HOT)
    # Iron bands, and a plinth.
    for y in (48, 78):
        draw.rectangle((left, y, right, y + 2), fill=IRON_DARK)
        draw.line((left, y, right, y), fill=IRON)
        for x in range(left + 3, right, 8):
            draw.point((x, y + 1), fill=IRON_LIT)
    draw.rectangle((left - 2, TOWER_H - 8, right + 2, TOWER_H - 1),
                   fill=WALL_DARK)
    draw.line((left - 2, TOWER_H - 8, right + 2, TOWER_H - 8), fill=WALL_LIT)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for variant in range(3):
        bone_heap(variant).save(OUT / f"phlegethos_bone_heap_{variant + 1}.png")
        iron_spikes(variant).save(
            OUT / f"phlegethos_iron_spikes_{variant + 1}.png")
        ember_crack(variant).save(
            OUT / f"phlegethos_ember_crack_{variant + 1}.png")
    for frame in range(VENT_FRAMES):
        vent(frame).save(OUT / f"phlegethos_vent_{frame + 1}.png")
    infernal_tower().save(OUT / "phlegethos_fortress_tower.png")
    for frame in range(generate_castle_banner.FRAMES):
        generate_castle_banner.banner(frame, INFERNAL_BANNER).save(
            OUT / f"phlegethos_banner_{frame + 1}.png")
    print(f"Wrote Phlegethos dressing to {OUT}")


if __name__ == "__main__":
    main()
