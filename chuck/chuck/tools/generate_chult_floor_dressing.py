"""Generate Chult's jungle-floor dressing.

Chult's open ground is one tone of dark earth with a speckle in it, and
every map of it was corridors of that between walls of canopy. What the
floor of a real jungle has on it is what fell off the jungle: ferns in
the gaps, dead leaves, trunks that came down, and in this one, pieces of
whoever built the temple.

* Ferns: low fronds Chuck walks through. Darker and flatter than the
  canopy walls, so nobody reads one as a place they cannot go.
* Leaf litter: flat, drawn under everyone.
* Fallen logs: three tiles long and solid, mossed along the top.
* Ruin fragments: the temple's green-grey stone, a carved block, a
  toppled head, a broken drum of column.

All at the game's resolution in Chult's own ramp.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
CLEAR = (0, 0, 0, 0)

GROUND = (37, 44, 28, 255)
OUTLINE = (14, 20, 12, 255)
FROND_DARK = (13, 49, 31, 255)
FROND = (22, 77, 40, 255)
FROND_LIT = (37, 105, 49, 255)
FROND_TIP = (68, 126, 58, 255)
LITTER = ((88, 70, 38, 255), (116, 88, 44, 255), (70, 58, 34, 255),
          (132, 104, 52, 255))
BARK_DARK = (46, 32, 22, 255)
BARK = (78, 56, 36, 255)
BARK_LIT = (108, 80, 52, 255)
HEARTWOOD = (150, 118, 76, 255)
MOSS = (51, 125, 52, 255)
MOSS_DARK = (27, 94, 40, 255)
STONE_DARK = (62, 70, 58, 255)
STONE = (92, 102, 84, 255)
STONE_LIT = (126, 136, 112, 255)
CARVE = (48, 54, 44, 255)


def _hash(*values: int) -> int:
    h = 2166136261
    for value in values:
        h = ((h ^ (value & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


# Ferns are drawn by hand rather than from curves. At this size a frond
# is a lit rib and a row of single-pixel leaflets, and anything computed
# came out as a green blot: the leaflets need gaps between them to read.
#   o outline  d shadow  m frond  l lit rib  t tip
FERN_GRIDS = (
    """
..........t....t..........
.....t....l...l....t......
....ol...dlm.mld...lo.....
...o.dl..mdl.ldm..ld.o....
..t..mdl.o.lml.o.ldm..t...
..lo..mdlomdldmoldm..ol...
.o.ld..mdldmlmdldm..dl.o..
t...mdl.omdlllldmo.ldm...t
lo...mdlmdmlllmdmdldm...ol
.ld...omdmdlllldmdmo...dl.
..mdl..odmdldldmdmo..ldm..
...omdldmdmdmdmdmdmdldmo..
.....oodmdmdmdmdmdmdoo....
........oooooooooooo......
""",
    """
.............t............
......t......l.....t......
.....ol.....dlm...lo......
....o.dl...mdlm..ld.o.....
.t...mdl..o.lm..ldm...t...
.lo...mdl.mdld.ldm...ol...
..ld...mdlmdlmldm...dl.o..
...mdl..mdmlllmdm..ldm...t
....omdlmdmlllmdmdldm...ol
......omdmdlllldmdmo...dl.
.......odmdldldmdmo..ldm..
......omdldmdmdmdmdmldmo..
.....oodmdmdmdmdmdmdoo....
........oooooooooooo......
""",
    """
..........................
.........t.....t..........
........ol.....lo.........
..t....o.dl...ld.o....t...
..lo....mdl.o.ldm....ol...
...ld....mdlmldm....dl....
....mdl..mdlllmd..ldm.....
.....omdlmdlllmdldmo......
......omdmdlllmdmdo.......
.......odmdldldmdo........
......omdldmdmdmdldmo.....
.....oodmdmdmdmdmdmoo.....
........ooooooooooo.......
..........................
""",
)
FERN_PALETTE = {
    ".": CLEAR, "o": OUTLINE, "d": FROND_DARK, "m": FROND,
    "l": FROND_LIT, "t": FROND_TIP,
}


def fern(variant: int) -> Image.Image:
    """A low spray of fronds from one root, a tile and a half across."""
    rows = [row for row in FERN_GRIDS[variant].strip("\n").split("\n")]
    width = max(len(row) for row in rows)
    image = Image.new("RGBA", (width, len(rows)), CLEAR)
    pixels = image.load()
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            pixels[x, y] = FERN_PALETTE[char]
    return image


def leaf_litter(variant: int) -> Image.Image:
    """A scatter of dead leaves lying flat."""
    image = Image.new("RGBA", (22, 14), CLEAR)
    pixels = image.load()
    for index in range(7 + variant):
        h = _hash(index, variant, 31)
        cx = 3 + h % 16
        cy = 2 + (h >> 8) % 10
        colour = LITTER[(h >> 16) % len(LITTER)]
        long = (h >> 20) % 2
        cells = ((0, 0), (1, 0), (-1, 0), (2, 0)) if long else \
            ((0, 0), (1, 0), (0, 1), (1, 1))
        for dx, dy in cells:
            x, y = cx + dx, cy + dy
            if 0 <= x < 22 and 0 <= y < 14:
                pixels[x, y] = colour
        if 0 <= cx + 1 < 22 and cy - 1 >= 0 and long:
            pixels[cx + 1, cy - 1] = LITTER[2]
    return image


def fallen_log(variant: int) -> Image.Image:
    """A trunk lying east-west across three tiles, mossed along its top."""
    image = Image.new("RGBA", (48, 20), CLEAR)
    draw = ImageDraw.Draw(image)
    left, right = 2, 43
    top, bottom = 5, 17
    draw.rectangle((left, top - 1, right, bottom + 1), fill=OUTLINE)
    draw.rectangle((left + 1, top, right - 1, bottom), fill=BARK)
    draw.rectangle((left + 1, top, right - 1, top + 3), fill=BARK_LIT)
    draw.rectangle((left + 1, bottom - 3, right - 1, bottom), fill=BARK_DARK)
    for index in range(9):
        h = _hash(index, variant, 5)
        x = left + 3 + h % (right - left - 6)
        y = top + 3 + (h >> 8) % 7
        draw.line((x, y, x + 3 + (h >> 12) % 4, y), fill=BARK_DARK)
    # The cut end, rings showing, on the east.
    draw.ellipse((right - 4, top - 1, right + 4, bottom + 1), fill=OUTLINE)
    draw.ellipse((right - 3, top, right + 3, bottom), fill=HEARTWOOD)
    draw.ellipse((right - 2, top + 3, right + 2, bottom - 3), fill=BARK_LIT)
    draw.point((right, (top + bottom) // 2), fill=BARK_DARK)
    # A broken branch stub.
    stub = 14 + variant * 7
    draw.polygon(((stub, top), (stub + 4, top), (stub + 1, top - 4)),
                 fill=BARK)
    draw.line((stub + 1, top - 4, stub + 3, top), fill=BARK_LIT)
    # Moss along the top, patchy.
    for x in range(left + 1, right - 3):
        if _hash(x, variant, 9) % 5 < 3:
            draw.point((x, top), fill=MOSS)
            if _hash(x, variant, 10) % 3 == 0:
                draw.point((x, top + 1), fill=MOSS_DARK)
                draw.point((x, top - 1), fill=MOSS)
    return image


def ruin_fragment(variant: int) -> Image.Image:
    """A piece of the temple's builders, lying where it fell."""
    image = Image.new("RGBA", (24, 22), CLEAR)
    draw = ImageDraw.Draw(image)
    if variant == 0:
        # A squared block with a carved glyph on its face.
        draw.rectangle((2, 5, 21, 21), fill=OUTLINE)
        draw.rectangle((3, 6, 20, 10), fill=STONE_LIT)
        draw.rectangle((3, 11, 20, 20), fill=STONE)
        draw.line((3, 11, 20, 11), fill=STONE_DARK)
        draw.rectangle((8, 13, 15, 18), outline=CARVE)
        draw.point((11, 15), fill=CARVE)
        draw.point((12, 16), fill=CARVE)
        draw.line((17, 6, 20, 9), fill=STONE_DARK)     # a broken corner
    elif variant == 1:
        # A toppled carved head, face turned up to the canopy.
        draw.ellipse((1, 6, 22, 21), fill=OUTLINE)
        draw.ellipse((2, 7, 21, 20), fill=STONE)
        draw.ellipse((3, 7, 17, 15), fill=STONE_LIT)
        draw.rectangle((6, 11, 9, 12), fill=CARVE)      # brow
        draw.rectangle((13, 11, 16, 12), fill=CARVE)
        draw.line((11, 13, 11, 16), fill=STONE_DARK)    # nose
        draw.line((7, 18, 15, 18), fill=CARVE)          # mouth
        draw.rectangle((2, 3, 21, 8), fill=OUTLINE)     # headdress band
        draw.rectangle((3, 4, 20, 7), fill=STONE_DARK)
        for x in range(4, 20, 3):
            draw.point((x, 5), fill=STONE_LIT)
    else:
        # A broken drum of column, on its side.
        draw.rectangle((2, 9, 20, 20), fill=OUTLINE)
        draw.rectangle((3, 10, 19, 19), fill=STONE)
        draw.rectangle((3, 10, 19, 12), fill=STONE_LIT)
        draw.rectangle((3, 17, 19, 19), fill=STONE_DARK)
        for x in (7, 12, 16):
            draw.line((x, 12, x, 18), fill=STONE_DARK)  # fluting
        draw.ellipse((16, 8, 23, 21), fill=OUTLINE)
        draw.ellipse((17, 9, 22, 20), fill=STONE_LIT)
        draw.ellipse((18, 12, 21, 17), fill=STONE)
    # Moss creeping over it from the ground.
    pixels = image.load()
    for x in range(24):
        for y in range(22):
            if pixels[x, y][3] and pixels[x, y] != OUTLINE \
                    and _hash(x, y, variant, 3) % 7 == 0 and y > 12:
                pixels[x, y] = MOSS_DARK if _hash(x, y) % 2 else MOSS
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for variant in range(3):
        fern(variant).save(OUT / f"chult_fern_{variant + 1}.png")
        leaf_litter(variant).save(OUT / f"chult_leaf_litter_{variant + 1}.png")
        fallen_log(variant).save(OUT / f"chult_fallen_log_{variant + 1}.png")
        ruin_fragment(variant).save(
            OUT / f"chult_ruin_fragment_{variant + 1}.png")
    print(f"Wrote Chult floor dressing to {OUT}")


if __name__ == "__main__":
    main()
