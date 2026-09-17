"""Generate the modern city's added furniture, kept deliberately few.

* A bench and a litter bin for the pavements, day and night.
* Neon shop signs on the night maps' building fronts, flickering now
  and then, and a street grate breathing steam.
* In the city sewers: rusted outflow pipes and spray-painted tags on the
  brick.

Drawn like the hydrant and the stop sign already on these streets: a
dark outline, flat colour, one lit edge.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
CLEAR = (0, 0, 0, 0)

OUTLINE = (22, 24, 28, 255)
METAL_DARK = (52, 56, 62, 255)
METAL = (92, 98, 106, 255)
METAL_LIT = (146, 152, 160, 255)
SLAT_DARK = (58, 42, 30, 255)
SLAT = (104, 76, 50, 255)
SLAT_LIT = (140, 106, 70, 255)
BIN_DARK = (28, 60, 44, 255)
BIN = (46, 92, 64, 255)
BIN_LIT = (78, 128, 90, 255)
SIGN_BACK = (30, 30, 36, 255)
STEAM = (210, 214, 222)
RUST_DARK = (76, 40, 26, 255)
RUST = (122, 66, 40, 255)
RUST_LIT = (166, 102, 62, 255)
SLIME = (132, 196, 60, 255)

NEON = {
    "pink": ((120, 30, 80), (246, 84, 176), (255, 196, 232)),
    "blue": ((30, 60, 120), (80, 170, 255), (206, 236, 255)),
    "amber": ((120, 70, 20), (255, 170, 50), (255, 228, 170)),
}
# Three-by-five capitals, the minimum a sign can be read at.
LETTERS = {
    "B": ("110", "101", "110", "101", "110"),
    "A": ("010", "101", "111", "101", "101"),
    "R": ("110", "101", "110", "101", "101"),
    "O": ("111", "101", "101", "101", "111"),
    "P": ("110", "101", "110", "100", "100"),
    "E": ("111", "100", "110", "100", "111"),
    "N": ("101", "111", "111", "111", "101"),
    "2": ("110", "001", "010", "100", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "H": ("101", "101", "111", "101", "101"),
}
SIGNS = (("BAR", "pink"), ("OPEN", "blue"), ("24H", "amber"))
NEON_FRAMES = 4
STEAM_FRAMES = 6


def bench() -> Image.Image:
    image = Image.new("RGBA", (32, 20), CLEAR)
    draw = ImageDraw.Draw(image)
    # Back rest and seat slats, iron ends.
    for y, colour in ((3, SLAT_LIT), (7, SLAT), (12, SLAT_LIT)):
        draw.rectangle((2, y - 1, 29, y + 2), fill=OUTLINE)
        draw.rectangle((3, y, 28, y + 1), fill=colour)
    draw.line((3, 14, 28, 14), fill=SLAT_DARK)
    for x in (4, 26):
        draw.rectangle((x - 1, 1, x + 2, 19), fill=OUTLINE)
        draw.rectangle((x, 2, x + 1, 18), fill=METAL)
        draw.point((x, 3), fill=METAL_LIT)
    return image


def litter_bin() -> Image.Image:
    image = Image.new("RGBA", (14, 20), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.rectangle((1, 5, 12, 19), fill=OUTLINE)
    draw.rectangle((2, 6, 11, 18), fill=BIN)
    draw.rectangle((2, 6, 4, 18), fill=BIN_LIT)
    draw.rectangle((9, 6, 11, 18), fill=BIN_DARK)
    for y in (9, 14):
        draw.line((2, y, 11, y), fill=BIN_DARK)
    draw.rectangle((0, 2, 13, 5), fill=OUTLINE)
    draw.rectangle((1, 3, 12, 4), fill=METAL)
    draw.line((1, 3, 12, 3), fill=METAL_LIT)
    draw.rectangle((5, 0, 8, 2), fill=METAL_DARK)
    # Something poking out of the top.
    draw.line((9, 2, 11, 0), fill=(214, 210, 196, 255))
    return image


def neon_sign(index: int, frame: int) -> Image.Image:
    text, colour = SIGNS[index]
    deep, glow, core = NEON[colour]
    width = len(text) * 4 + 7
    height = 13
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    # One letter in the sign stutters on one frame out of four; the rest
    # of the time the whole sign is lit.
    dim = frame == 2
    halo = Image.new("RGBA", (width, height), CLEAR)
    ImageDraw.Draw(halo).rounded_rectangle(
        (0, 0, width - 1, height - 1), radius=3,
        fill=glow + (40 if dim else 70,))
    image.alpha_composite(halo)
    draw.rounded_rectangle((2, 2, width - 3, height - 3), radius=2,
                           fill=SIGN_BACK, outline=deep + (255,))
    for position, letter in enumerate(text):
        stutter = dim and position == len(text) - 1
        for row, bits in enumerate(LETTERS[letter]):
            for col, bit in enumerate(bits):
                if bit == "1":
                    x = 4 + position * 4 + col
                    y = 4 + row
                    draw.point((x, y), fill=(deep if stutter else
                                             (core if row == 0 else glow))
                               + (255,))
    # The bracket it hangs from.
    draw.line((1, 0, 1, 3), fill=METAL_DARK)
    draw.line((width - 2, 0, width - 2, 3), fill=METAL_DARK)
    return image


def storefront(index: int, frame: int, *, signed: bool = True) -> Image.Image:
    """Three tiles of ground-floor frontage beneath the existing neon.

    Bottom aligned with the facade tile, entirely inside the building's
    solid footprint. The sign still flickers; the closed shop never does.
    """
    image = Image.new("RGBA", (48, 48), CLEAR)
    draw = ImageDraw.Draw(image)
    trim = ((87, 48, 65), (47, 75, 91), (99, 79, 48))[index]
    light = ((154, 97, 119), (99, 141, 154), (167, 144, 97))[index]
    glass = (24, 34, 43)
    # Shallow projecting lintel, stone jambs and a wet stone sill.
    draw.rectangle((0, 0, 47, 47), fill=OUTLINE)
    draw.rectangle((1, 1, 46, 45), fill=(62, 65, 72))
    draw.rectangle((2, 2, 45, 12), fill=trim)
    draw.line((1, 0, 46, 0), fill=METAL)
    draw.line((2, 12, 45, 12), fill=light)
    draw.rectangle((3, 15, 26, 39), fill=OUTLINE)
    draw.rectangle((5, 17, 24, 36), fill=glass)
    # Each window tells the same story as its sign: bottles, a cafe
    # counter, or shelves of convenience-store packages.
    if index == 0:
        for y in (25, 34):
            draw.line((5, y, 24, y), fill=(100, 74, 63))
            for x, colour in ((7, (69, 104, 88)), (13, (135, 95, 61)),
                              (20, (84, 117, 103))):
                draw.rectangle((x, y - 5, x + 2, y - 1), fill=colour)
                draw.point((x + 1, y - 6), fill=colour)
        draw.rectangle((4, 40, 26, 44), fill=trim)
    elif index == 1:
        draw.rectangle((5, 30, 24, 33), fill=(131, 103, 79))
        for x in (8, 18):
            draw.rectangle((x, 26, x + 3, 29), fill=(170, 180, 178))
            draw.point((x + 4, 27), fill=(170, 180, 178))
            draw.line((x, 34, x, 36), fill=METAL_DARK)
        # A folded blind, not an opening in the facade.
        for y in (17, 19, 21):
            draw.line((5, y, 24, y), fill=(77, 93, 100))
    else:
        for y in (24, 33):
            draw.line((5, y, 24, y), fill=METAL)
            for x, colour in ((6, (158, 118, 69)), (12, (82, 120, 116)),
                              (19, (145, 86, 82))):
                draw.rectangle((x, y - 5, x + 3, y - 1), fill=colour)
                draw.line((x, y - 4, x + 3, y - 4), fill=(183, 183, 167))
        draw.line((15, 17, 15, 36), fill=METAL_DARK)
    # Glazing reflections stay sparse at native resolution.
    draw.line((6, 18, 10, 22), fill=(84, 108, 123))
    draw.line((20, 28, 23, 31), fill=(71, 89, 103))
    draw.line((4, 38, 26, 38), fill=METAL)
    # Human-height closed door: inset glass, a continuous lower panel,
    # latch, and a threshold flush with the existing pavement edge.
    draw.rectangle((29, 14, 44, 45), fill=OUTLINE)
    draw.rectangle((31, 16, 42, 43), fill=trim)
    draw.rectangle((33, 18, 40, 33), fill=glass)
    draw.line((34, 19, 38, 23), fill=(80, 103, 117))
    draw.rectangle((34, 26, 39, 29), fill=(149, 144, 129))
    draw.line((35, 27, 38, 27), fill=(57, 60, 65))
    draw.line((40, 35, 40, 38), fill=METAL_LIT)
    draw.line((33, 41, 40, 41), fill=light)
    draw.line((30, 45, 44, 45), fill=METAL_LIT)
    draw.line((1, 46, 46, 46), fill=(84, 91, 102))
    if signed:
        sign = neon_sign(index, frame)
        image.alpha_composite(sign, ((48 - sign.width) // 2, 0))
    else:
        # Unlettered canvas valance and a brighter overcast palette.
        for x in range(4, 45, 8):
            draw.rectangle((x, 3, x + 3, 10), fill=light)
        pixels = image.load()
        for y in range(48):
            for x in range(48):
                r, g, b, a = pixels[x, y]
                pixels[x, y] = (min(255, int(r * 1.15 + 12)),
                               min(255, int(g * 1.15 + 12)),
                               min(255, int(b * 1.15 + 12)), a)
    return image


def city_fountain(frame: int) -> Image.Image:
    """Low concrete basin, steel central jet, restrained rainy-day water."""
    image = Image.new("RGBA", (80, 48), CLEAR)
    d = ImageDraw.Draw(image)
    d.ellipse((0, 22, 79, 47), fill=OUTLINE)
    d.rectangle((2, 29, 77, 35), fill=(99, 108, 109))
    d.ellipse((2, 25, 77, 45), fill=(112, 121, 120))
    d.arc((3, 26, 76, 44), 0, 180, fill=(75, 87, 90), width=2)
    d.ellipse((1, 18, 78, 38), fill=(160, 168, 160), outline=OUTLINE)
    d.ellipse((7, 21, 72, 34), fill=(65, 105, 115))
    d.ellipse((10, 23, 69, 32), fill=(95, 139, 145))
    for x, y in ((18, 26), (52, 27), (32, 30)):
        d.arc((x-frame%2, y-2, x+10+frame%2, y+2), 0, 170,
              fill=(163, 190, 187))
    d.ellipse((34, 24, 45, 30), fill=METAL_DARK)
    d.rectangle((37, 17, 42, 27), fill=METAL)
    d.line((38, 17, 38, 25), fill=METAL_LIT)
    d.line((40, 20, 40, 3 + frame % 2), fill=(194, 220, 217), width=2)
    for direction in (-1, 1):
        points = [(40, 5), (40+direction*5, 3), (40+direction*10, 7),
                  (40+direction*14, 18)]
        d.line(points, fill=(153, 193, 194))
        d.point((40+direction*14, 20+frame), fill=(219, 230, 224))
    return image


def park_planter() -> Image.Image:
    image = Image.new("RGBA", (28, 32), CLEAR)
    d = ImageDraw.Draw(image)
    d.polygon(((2, 18), (25, 18), (23, 30), (5, 30)), fill=OUTLINE)
    d.polygon(((4, 20), (23, 20), (21, 28), (6, 28)), fill=(126, 138, 132))
    d.line((6, 28, 21, 28), fill=(79, 96, 92))
    d.ellipse((1, 15, 26, 22), fill=(160, 166, 151), outline=OUTLINE)
    d.ellipse((4, 16, 23, 20), fill=(59, 61, 46))
    for x, y, r in ((8, 11, 7), (18, 12, 8), (13, 7, 7)):
        d.ellipse((x-r,y-r,x+r,y+r), fill=(46, 77, 63), outline=OUTLINE)
        d.arc((x-r+2,y-r+2,x+r-2,y+r-2), 190, 310, fill=(105, 132, 94), width=2)
    return image


def newspaper_box() -> Image.Image:
    image = Image.new("RGBA", (20, 28), CLEAR)
    d = ImageDraw.Draw(image)
    d.rectangle((3, 3, 17, 26), fill=OUTLINE)
    d.rectangle((4, 5, 16, 24), fill=(58, 104, 120))
    d.polygon(((2, 3), (5, 0), (17, 0), (19, 3)), fill=(121, 155, 158))
    d.rectangle((6, 8, 14, 17), fill=(182, 188, 166))
    d.line((7, 10, 13, 10), fill=(55, 67, 72))
    for y in (12, 14, 16):
        d.line((7, y, 12, y), fill=(98, 112, 112))
    d.line((6, 21, 13, 21), fill=OUTLINE)
    d.point((15, 20), fill=METAL_LIT)
    return image


def steam_grate(frame: int) -> Image.Image:
    width, height = 20, 40
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    draw.rectangle((3, 34, 16, 39), fill=OUTLINE)
    draw.rectangle((4, 35, 15, 38), fill=METAL_DARK)
    for x in range(5, 15, 2):
        draw.line((x, 35, x, 38), fill=OUTLINE)
    draw.line((4, 35, 15, 35), fill=METAL)
    phase = frame / STEAM_FRAMES
    for puff in range(5):
        t = (puff / 5 + phase) % 1.0
        cy = 34 - t * 32
        cx = 10 + math.sin(t * 4 + puff * 1.7) * (1 + t * 3)
        radius = 2.5 + t * 4
        alpha = round(120 * (1 - t) ** 1.3)
        if alpha < 10:
            continue
        layer = Image.new("RGBA", (width, height), CLEAR)
        ImageDraw.Draw(layer).ellipse(
            (cx - radius, cy - radius * 0.8, cx + radius, cy + radius * 0.8),
            fill=STEAM + (alpha,))
        image.alpha_composite(layer)
    return image


def sewer_pipe(variant: int) -> Image.Image:
    """A rusted outflow pipe coming out of the brick, trickling."""
    # Drawn as a length of pipe jutting out of the wall and down, with its
    # mouth at the bottom: seen head-on, a round mouth over a green line
    # of water read as a flower on its stem.
    image = Image.new("RGBA", (20, 30), CLEAR)
    draw = ImageDraw.Draw(image)
    top = 2 if variant == 0 else 6
    # Flange against the brick.
    draw.rectangle((2, top, 17, top + 3), fill=OUTLINE)
    draw.rectangle((3, top + 1, 16, top + 2), fill=RUST_LIT)
    # The body, a cylinder lit from the west.
    draw.rectangle((4, top + 3, 15, 19), fill=OUTLINE)
    draw.rectangle((5, top + 3, 14, 19), fill=RUST)
    draw.rectangle((5, top + 3, 7, 19), fill=RUST_LIT)
    draw.rectangle((12, top + 3, 14, 19), fill=RUST_DARK)
    draw.line((5, top + 9, 14, top + 9), fill=RUST_DARK)     # a joint
    draw.point((6, top + 9), fill=METAL_LIT)
    # The open end, an ellipse seen from above.
    draw.ellipse((3, 17, 16, 23), fill=OUTLINE)
    draw.ellipse((4, 18, 15, 22), fill=RUST_DARK)
    draw.ellipse((6, 19, 13, 21), fill=(20, 16, 14, 255))
    # A thin fall of murky water and the splash it lands in.
    murk = (104, 124, 96, 220)
    draw.line((9, 22, 9, 27), fill=murk)
    draw.point((10, 25), fill=murk)
    draw.ellipse((5, 26, 14, 29), fill=(80, 100, 76, 200))
    draw.point((7, 26), fill=(170, 190, 160, 230))
    draw.point((12, 27), fill=(170, 190, 160, 230))
    return image


def sewer_graffiti(variant: int) -> Image.Image:
    """A spray-painted tag on the brick."""
    image = Image.new("RGBA", (22, 16), CLEAR)
    pixels = image.load()
    colours = (((226, 64, 96), (255, 180, 200)),
               ((64, 186, 220), (200, 240, 255)),
               ((236, 196, 48), (255, 240, 170)))[variant]
    main, highlight = colours
    # A looping tag stroke.
    for step in range(90):
        t = step / 90
        x = 2 + t * 17 + math.sin(t * 17 + variant) * 2.2
        y = 8 + math.sin(t * 9 + variant * 2) * 4.5
        for dx in (0, 1):
            px, py = round(x) + dx, round(y)
            if 0 <= px < 22 and 0 <= py < 16:
                pixels[px, py] = main + (230,)
        if step % 11 == 0 and 0 <= round(y) - 1 < 16:
            pixels[round(x), round(y) - 1] = highlight + (230,)
    # Drips.
    for x in (5 + variant, 13, 17 - variant):
        for y in range(9, 14 + (x % 3)):
            if pixels[x, y - 1][3]:
                pixels[x, y] = main + (200,)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    bench().save(OUT / "city_bench.png")
    litter_bin().save(OUT / "city_litter_bin.png")
    for index in range(3):
        storefront(index, 0, signed=False).save(OUT / f"city_shop_{index + 1}.png")
    for frame in range(4):
        city_fountain(frame).save(OUT / f"city_park_fountain_{frame + 1}.png")
    park_planter().save(OUT / "city_park_planter.png")
    newspaper_box().save(OUT / "city_newspaper_box.png")
    for index in range(len(SIGNS)):
        for frame in range(NEON_FRAMES):
            storefront(index, frame).save(
                OUT / f"city_neon_{index + 1}_{frame + 1}.png")
    for frame in range(STEAM_FRAMES):
        steam_grate(frame).save(OUT / f"city_steam_grate_{frame + 1}.png")
    for variant in range(2):
        sewer_pipe(variant).save(OUT / f"sewer_pipe_{variant + 1}.png")
    for variant in range(3):
        sewer_graffiti(variant).save(OUT / f"sewer_graffiti_{variant + 1}.png")
    print(f"Wrote city furnishing to {OUT}")


if __name__ == "__main__":
    main()
