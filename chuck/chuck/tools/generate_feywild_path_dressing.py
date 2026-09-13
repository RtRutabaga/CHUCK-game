"""Generate the Feywild's path lanterns and edging, and the fen's water plants.

* Lanterns: a crooked post with a glass lantern hung off it, glowing the
  Feywild's teal or violet, set at the edge of the stone paths. Animated
  so the light breathes rather than flickers -- nothing fey gutters.
* Path stones: a couple of mossy rounded stones lying along a path's
  edge, flat.
* Lily pads: small clusters on open water, deliberately too small to
  mistake for somewhere to land on a map made of committed hops.
* Reeds: clumps standing in the shallows off the fen's banks.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
CLEAR = (0, 0, 0, 0)

OUTLINE = (12, 24, 26, 255)
WOOD_DARK = (40, 30, 44, 255)
WOOD = (70, 52, 74, 255)
WOOD_LIT = (104, 80, 104, 255)
IRON = (34, 40, 48, 255)
IRON_LIT = (70, 80, 92, 255)
STONE_DARK = (54, 66, 64, 255)
STONE = (86, 100, 94, 255)
STONE_LIT = (124, 140, 128, 255)
MOSS = (58, 124, 78, 255)
MOSS_LIT = (92, 160, 96, 255)
# Brighter than the island grass: the fen's water is dark and busy, and
# pads in the grass's own greens disappeared into it.
PAD_DARK = (36, 104, 66, 255)
PAD = (68, 150, 86, 255)
PAD_LIT = (124, 196, 112, 255)
BLOOM = (244, 150, 206, 255)
BLOOM_LIT = (255, 214, 236, 255)
REED_DARK = (30, 72, 50, 255)
REED = (52, 110, 64, 255)
REED_LIT = (96, 150, 84, 255)
CATTAIL = (98, 64, 44, 255)

GLOWS = {
    "teal": ((40, 120, 150), (76, 194, 255), (196, 244, 255)),
    "violet": ((100, 44, 130), (193, 82, 244), (240, 200, 255)),
}
LANTERN_FRAMES = 4


def lantern(colour: str, frame: int) -> Image.Image:
    # Wide enough for the halo at its fullest, which the lantern's own
    # outline would otherwise crop into a flat edge.
    width, height = 22, 34
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    deep, glow, core = GLOWS[colour]
    breathe = 0.5 + 0.5 * math.sin(frame / LANTERN_FRAMES * math.tau)

    # The glow round the lantern, drawn first and soft.
    halo = Image.new("RGBA", (width, height), CLEAR)
    radius = 6 + breathe * 1.5
    ImageDraw.Draw(halo).ellipse(
        (11 - radius, 12 - radius, 11 + radius, 12 + radius),
        fill=glow + (round(40 + 30 * breathe),))
    image.alpha_composite(halo)

    # A crooked post, and the arm the lantern hangs from.
    draw.line((5, 33, 5, 6), fill=OUTLINE, width=3)
    draw.line((5, 33, 5, 6), fill=WOOD)
    draw.line((4, 30, 4, 8), fill=WOOD_LIT)
    draw.point((6, 20), fill=WOOD_DARK)
    draw.line((5, 5, 11, 4), fill=OUTLINE, width=2)
    draw.line((5, 4, 11, 3), fill=WOOD_LIT)
    draw.line((11, 4, 11, 7), fill=IRON)
    # The lantern: iron cap, glass, iron base.
    draw.polygon(((8, 8), (14, 8), (12, 6), (10, 6)), fill=IRON)
    draw.rectangle((8, 9, 14, 16), fill=OUTLINE)
    draw.rectangle((9, 9, 13, 15), fill=deep + (255,))
    draw.rectangle((10, 10, 12, 14), fill=glow + (255,))
    draw.point((11, 12), fill=core + (255,))
    if breathe > 0.6:
        draw.point((10, 11), fill=core + (255,))
    draw.line((9, 9, 9, 15), fill=IRON_LIT)
    draw.rectangle((8, 16, 14, 17), fill=IRON)
    # A moss foot where the post meets the ground.
    draw.line((3, 33, 8, 33), fill=MOSS)
    draw.point((4, 32), fill=MOSS_LIT)
    return image


def path_stones(variant: int) -> Image.Image:
    image = Image.new("RGBA", (18, 10), CLEAR)
    draw = ImageDraw.Draw(image)
    stones = (((1, 3, 8, 9), (9, 5, 15, 9)),
              ((2, 4, 10, 9), (11, 2, 16, 7)),
              ((4, 3, 12, 9),))[variant]
    for x0, y0, x1, y1 in stones:
        draw.ellipse((x0, y0, x1, y1), fill=OUTLINE)
        draw.ellipse((x0 + 1, y0, x1 - 1, y1 - 1), fill=STONE)
        draw.ellipse((x0 + 1, y0, x1 - 3, y1 - 3), fill=STONE_LIT)
        draw.line((x0 + 2, y1 - 1, x1 - 2, y1 - 1), fill=STONE_DARK)
        draw.point((x0 + 2, y0 + 1), fill=MOSS_LIT)
        draw.point((x0 + 3, y0 + 1), fill=MOSS)
    return image


def lily_pads(variant: int) -> Image.Image:
    image = Image.new("RGBA", (20, 12), CLEAR)
    draw = ImageDraw.Draw(image)
    pads = (((2, 3, 5), (11, 6, 4), (15, 2, 3)),
            ((4, 5, 5), (13, 3, 4)),
            ((3, 2, 3), (8, 7, 4), (15, 5, 3)))[variant]
    for index, (cx, cy, r) in enumerate(pads):
        draw.ellipse((cx - r, cy - r * 0.6, cx + r, cy + r * 0.6), fill=PAD_DARK)
        draw.ellipse((cx - r + 1, cy - r * 0.6, cx + r - 1, cy + r * 0.45),
                     fill=PAD)
        draw.line((cx, cy, cx + r - 1, cy - 1), fill=PAD_DARK)   # the notch
        draw.point((cx - 1, cy - 1), fill=PAD_LIT)
        if index == 0 and variant != 1:
            draw.point((cx, cy - 1), fill=BLOOM)
            draw.point((cx + 1, cy - 1), fill=BLOOM)
            draw.point((cx, cy - 2), fill=BLOOM_LIT)
    return image


def reeds(variant: int) -> Image.Image:
    image = Image.new("RGBA", (18, 26), CLEAR)
    draw = ImageDraw.Draw(image)
    stems = ((3, 11), (6, 4), (9, 8), (12, 2), (15, 10))
    if variant == 1:
        stems = stems[1:]
    elif variant == 2:
        stems = ((4, 7), (8, 1), (11, 6), (14, 3))
    for index, (x, top) in enumerate(stems):
        lean = ((index * 7 + variant) % 3) - 1
        draw.line((x, 25, x + lean, top), fill=REED_DARK, width=2)
        draw.line((x, 25, x + lean, top), fill=REED if index % 2 else REED_LIT)
        if index % 2 == 0:
            # A cattail head.
            draw.rectangle((x + lean - 1, top + 1, x + lean, top + 5),
                           fill=CATTAIL)
    # Ripples at the foot.
    draw.arc((1, 22, 17, 26), 200, 340, fill=(110, 170, 190, 160))
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for colour in GLOWS:
        for frame in range(LANTERN_FRAMES):
            lantern(colour, frame).save(
                OUT / f"fey_lantern_{colour}_{frame + 1}.png")
    for variant in range(3):
        path_stones(variant).save(OUT / f"fey_path_stones_{variant + 1}.png")
        lily_pads(variant).save(OUT / f"fen_lily_pads_{variant + 1}.png")
        reeds(variant).save(OUT / f"fen_reeds_{variant + 1}.png")
    print(f"Wrote Feywild path and fen dressing to {OUT}")


if __name__ == "__main__":
    main()
