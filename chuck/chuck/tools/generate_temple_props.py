"""Generate reusable temple props: threshold arches and interior dressing.

The dressing set (serpent idols, glyph stelae, cracked urns, fallen
column drums) continues the game's style-add-on convention — the
three-quarter Waterdeep buildings, the market stall, the jungle cog,
trees, and shrubs — translated into ancient temple interior language.
All pieces are mute, y-sorted scenery drawn from the same restrained
temple masonry palette, plus a muted terracotta for the pottery.
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw


TRANSPARENT = (0, 0, 0, 0)
VOID = (7, 13, 14, 255)
STONE_DARK = (27, 38, 37, 255)
STONE = (52, 64, 55, 255)
STONE_LIGHT = (87, 91, 68, 255)
MOSS = (36, 76, 44, 255)
CLAY = (139, 90, 58, 255)
CLAY_DARK = (104, 66, 44, 255)
CLAY_LIGHT = (166, 116, 76, 255)
EYE = (216, 178, 96, 255)
GOLD = (198, 166, 74, 255)
BAND = (52, 92, 48, 255)
BAND_DARK = (36, 66, 38, 255)


def _blocks(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    """Add restrained masonry seams to a filled arch section."""
    x0, y0, x1, y1 = box
    for y in range(y0 + 7, y1, 7):
        draw.line((x0, y, x1, y), fill=STONE_DARK)
    for index, y in enumerate(range(y0, y1, 7)):
        seam = x0 + 5 + (index % 2) * 6
        if seam < x1:
            draw.line((seam, y, seam, min(y + 6, y1)), fill=STONE_DARK)


def north_south_arch() -> Image.Image:
    """A 48x38 frontal arch: roughly human NPC height, enormous to Chuck."""
    image = Image.new("RGBA", (48, 38), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Deep opening first, then stepped voussoirs and broad jambs.
    draw.rectangle((13, 11, 34, 37), fill=VOID)
    draw.rectangle((5, 15, 12, 37), fill=STONE)
    draw.rectangle((35, 15, 42, 37), fill=STONE)
    draw.rectangle((9, 8, 38, 15), fill=STONE)
    draw.rectangle((13, 4, 34, 9), fill=STONE)
    draw.rectangle((17, 1, 30, 5), fill=STONE)
    _blocks(draw, (5, 15, 12, 37))
    _blocks(draw, (35, 15, 42, 37))
    draw.line((9, 15, 13, 10, 17, 6, 30, 6, 34, 10, 38, 15),
              fill=STONE_LIGHT, width=2)
    draw.line((12, 37, 35, 37), fill=STONE_DARK, width=2)
    draw.line((7, 18, 11, 18), fill=MOSS, width=2)
    draw.line((38, 11, 40, 23), fill=MOSS)
    return image


def east_west_arch() -> Image.Image:
    """A side-wall arch with the same human-scale dark opening."""
    image = Image.new("RGBA", (38, 48), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 13, 37, 34), fill=VOID)
    draw.rectangle((10, 5, 37, 12), fill=STONE)
    draw.rectangle((10, 35, 37, 42), fill=STONE)
    draw.rectangle((5, 9, 12, 38), fill=STONE)
    draw.rectangle((1, 13, 6, 34), fill=STONE)
    _blocks(draw, (10, 5, 37, 12))
    _blocks(draw, (10, 35, 37, 42))
    draw.line((12, 9, 7, 13, 7, 34, 12, 38),
              fill=STONE_LIGHT, width=2)
    draw.line((37, 12, 37, 35), fill=STONE_DARK, width=2)
    draw.line((15, 7, 27, 7), fill=MOSS, width=2)
    draw.line((8, 30, 8, 37), fill=MOSS)
    return image


def serpent_idol(variant: int) -> Image.Image:
    """A 26x44 coiled-serpent idol on a stepped pedestal.

    Taller than the 30px human NPC scale: to Chuck, a monument. Variant
    0 faces left, variant 1 faces right; both keep the same silhouette
    weight so paired placements read as deliberate temple symmetry.
    """
    image = Image.new("RGBA", (26, 44), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    flip = variant % 2 == 1
    # Stepped pedestal (widest at the base, like the pyramid outside).
    draw.rectangle((1, 38, 24, 43), fill=STONE)
    draw.rectangle((3, 33, 22, 38), fill=STONE)
    draw.line((1, 38, 24, 38), fill=STONE_DARK)
    draw.line((3, 33, 22, 33), fill=STONE_LIGHT)
    draw.line((1, 43, 24, 43), fill=STONE_DARK)
    # Coiled body: three stacked stone coils, narrowing upward.
    draw.rectangle((4, 26, 21, 33), fill=STONE)
    draw.rectangle((6, 19, 19, 26), fill=STONE)
    draw.rectangle((8, 13, 17, 19), fill=STONE)
    for y in (26, 19, 13):
        draw.line((5, y, 20, y), fill=STONE_DARK)
    draw.line((4, 29, 21, 29), fill=STONE_DARK)
    draw.line((6, 22, 19, 22), fill=STONE_DARK)
    # Raised head with open jaw, feathered crest, and a gold eye.
    head_x = 3 if flip else 13
    draw.rectangle((head_x, 3, head_x + 9, 13), fill=STONE)
    jaw_x = head_x - 2 if flip else head_x + 9
    draw.rectangle((jaw_x, 8, jaw_x + 2, 12), fill=STONE_DARK)
    crest_x = head_x + 7 if flip else head_x
    draw.rectangle((crest_x, 0, crest_x + 2, 4), fill=STONE_LIGHT)
    draw.rectangle((crest_x - 3 if flip else crest_x + 3, 1,
                    crest_x - 1 if flip else crest_x + 5, 4),
                   fill=STONE_LIGHT)
    eye_x = head_x + 2 if flip else head_x + 6
    draw.rectangle((eye_x, 6, eye_x + 1, 7), fill=EYE)
    # Weathering: highlight along one flank, moss at the base coils.
    draw.line((4, 27, 4, 33), fill=STONE_LIGHT)
    draw.line((21 if flip else 4, 39, 24 if flip else 7, 39), fill=MOSS)
    draw.line((6, 20, 6, 25) if not flip else (19, 20, 19, 25), fill=MOSS)
    return image


def glyph_stela(variant: int) -> Image.Image:
    """A 20x34 rounded-top carved slab with rows of worn glyphs."""
    image = Image.new("RGBA", (20, 34), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Base plinth, slab body, rounded crown.
    draw.rectangle((1, 30, 18, 33), fill=STONE)
    draw.rectangle((3, 6, 16, 30), fill=STONE)
    draw.rectangle((5, 3, 14, 6), fill=STONE)
    draw.rectangle((7, 1, 12, 3), fill=STONE)
    draw.line((3, 6, 3, 30), fill=STONE_LIGHT)
    draw.line((16, 6, 16, 30), fill=STONE_DARK)
    draw.line((1, 30, 18, 30), fill=STONE_DARK)
    # Glyph rows: short dark strokes and dots, staggered per variant.
    for row, y in enumerate(range(8, 28, 4)):
        offset = (row + variant) % 2 * 2
        draw.line((5 + offset, y, 8 + offset, y), fill=STONE_DARK)
        draw.point((11 + offset, y), fill=STONE_DARK)
        draw.line((10 + offset, y + 1, 12 + offset, y + 1), fill=STONE_DARK)
    # A chipped corner and a thread of moss keep it ancient, not new.
    if variant % 2 == 0:
        draw.rectangle((13, 3, 16, 7), fill=TRANSPARENT)
        draw.line((4, 24, 4, 29), fill=MOSS)
    else:
        draw.rectangle((3, 25, 5, 30), fill=TRANSPARENT)
        draw.line((15, 8, 15, 13), fill=MOSS)
    return image


def cracked_urn(variant: int) -> Image.Image:
    """A 14x18 terracotta urn; the third variant lies toppled."""
    image = Image.new("RGBA", (14, 18), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    if variant % 3 == 2:
        # Toppled: the urn on its side, mouth spilling shadow.
        draw.rectangle((1, 10, 12, 16), fill=CLAY)
        draw.rectangle((0, 11, 2, 15), fill=CLAY_DARK)
        draw.ellipse((10, 10, 13, 16), fill=CLAY_DARK)
        draw.line((3, 11, 9, 11), fill=CLAY_LIGHT)
        draw.line((2, 16, 11, 16), fill=STONE_DARK)
        draw.line((5, 12, 7, 15), fill=CLAY_DARK)  # crack
        return image
    # Standing: narrow foot, swollen belly, lipped mouth.
    draw.rectangle((4, 15, 9, 17), fill=CLAY_DARK)
    draw.rectangle((2, 6, 11, 15), fill=CLAY)
    draw.rectangle((1, 8, 12, 12), fill=CLAY)
    draw.rectangle((3, 3, 10, 6), fill=CLAY_DARK)
    draw.rectangle((2, 1, 11, 3), fill=CLAY)
    draw.line((2, 1, 11, 1), fill=CLAY_LIGHT)
    draw.line((2, 8, 2, 12), fill=CLAY_LIGHT)
    # Painted band, then a crack on the second variant.
    draw.line((2, 7, 11, 7), fill=STONE_DARK)
    if variant % 3 == 1:
        draw.line((8, 8, 6, 12), fill=CLAY_DARK)
        draw.line((6, 12, 7, 15), fill=CLAY_DARK)
    return image


def fallen_column(variant: int) -> Image.Image:
    """A 24x16 pair of collapsed column drums, low and wide."""
    image = Image.new("RGBA", (24, 16), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    lean = variant % 2
    # Larger drum lying across, smaller drum tipped against it.
    draw.rectangle((1, 7, 15, 14), fill=STONE)
    draw.ellipse((13, 7, 18, 14), fill=STONE_DARK)
    draw.ellipse((14, 8, 17, 13), fill=STONE)
    draw.line((2, 8, 12, 8), fill=STONE_LIGHT)
    draw.line((1, 14, 15, 14), fill=STONE_DARK)
    draw.line((5, 7, 5, 14), fill=STONE_DARK)
    draw.line((10, 7, 10, 14), fill=STONE_DARK)
    small_x = 16 + lean * 2
    draw.rectangle((small_x, 3 + lean, small_x + 6, 10 + lean), fill=STONE)
    draw.line((small_x, 4 + lean, small_x + 6, 4 + lean), fill=STONE_LIGHT)
    draw.line((small_x, 10 + lean, small_x + 6, 10 + lean), fill=STONE_DARK)
    # Rubble crumbs and moss at the break.
    draw.point((17, 15), fill=STONE_DARK)
    draw.point((3, 15), fill=STONE_DARK)
    draw.line((1, 10, 1, 13), fill=MOSS)
    return image


def _stone_chunk(bw: int, bh: int, rng: random.Random) -> Image.Image:
    """One 3/4-view broken masonry block, bw x bh footprint, lit from
    above so it still reads right after a small tumble-rotation."""
    depth = rng.randint(3, 6)
    w, h = bw + depth + 2, bh + depth + 2
    img = Image.new("RGBA", (w, h), TRANSPARENT)
    d = ImageDraw.Draw(img)
    x0, y0 = 1, 1
    x1, yf = x0 + bw, y0 + depth          # yf: front face top
    yb = yf + bh                          # front face bottom
    # Front face, lit top face, shadowed right side.
    d.rectangle((x0, yf, x1, yb), fill=STONE)
    d.polygon([(x0, yf), (x0 + depth, y0), (x1 + depth, y0), (x1, yf)],
              fill=STONE_LIGHT)
    d.polygon([(x1, yf), (x1 + depth, y0), (x1 + depth, yb - depth),
               (x1, yb)], fill=STONE_DARK)
    d.line((x0, yf, x1, yf), fill=STONE_DARK)
    d.line((x0, yb, x1, yb), fill=STONE_DARK)
    d.line((x0, yf, x0, yb), fill=STONE_DARK)
    # A fracture or two down the front.
    for _ in range(rng.randint(1, 2)):
        cx = rng.randint(x0 + 2, x1 - 2)
        d.line((cx, yf + 1, cx + rng.randint(-2, 2), yb - 1), fill=STONE_DARK)
    # A broken-off corner and some moss.
    if rng.random() < 0.7:
        s = rng.randint(2, 4)
        d.polygon([(x0, yf), (x0 + s, yf), (x0, yf + s)], fill=TRANSPARENT)
    d.point((x0, yb - 1), fill=MOSS)
    if rng.random() < 0.5:
        d.point((x1 - 1, yb), fill=MOSS)
    return img


def rubble_block(variant: int) -> Image.Image:
    """A tile-cell of fallen ceiling debris: one or two big broken blocks
    dropped at random offsets and tumble-angles onto the floor, so a
    field of them looks like chaotic collapse, not orderly rows.

    Deterministic per variant; the map cycles ~12 of these across its
    tiles for a scattered, many-angled rubble field (session 143)."""
    rng = random.Random(variant * 97 + 13)
    w, h = 44, 36
    canvas = Image.new("RGBA", (w, h), TRANSPARENT)
    for _ in range(rng.choice((1, 1, 2))):
        chunk = _stone_chunk(rng.randint(12, 20), rng.randint(8, 14), rng)
        chunk = chunk.rotate(rng.uniform(-24, 24), expand=True,
                             resample=Image.NEAREST)
        maxx = max(0, w - chunk.width)
        maxy = max(0, h - chunk.height)
        px = rng.randint(0, maxx)
        py = rng.randint(max(0, maxy - 7), maxy)  # sitting on the floor
        canvas.alpha_composite(chunk, (px, py))
    return canvas


def _diamond(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """The recurring gold diamond glyph from the temple's stonework."""
    draw.polygon(((cx, cy - 2), (cx + 2, cy), (cx, cy + 2), (cx - 2, cy)),
                 outline=GOLD)


def temple_gate() -> Image.Image:
    """An 80x48 monumental facade for the entrance hall's deeper door.

    Reference-directed: a stepped corbelled crown over a tall dark
    opening, flanking engaged pillars with capitals, moss threads, and
    the gold diamond glyphs. Spans the full three-tile doorway plus a
    pillar's width to either side; nearly three tiles tall.
    """
    image = Image.new("RGBA", (80, 48), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Stepped crown: three corbelled tiers narrowing upward.
    draw.rectangle((28, 0, 51, 7), fill=STONE)
    draw.rectangle((20, 6, 59, 15), fill=STONE)
    draw.rectangle((12, 14, 67, 23), fill=STONE)
    # The tall dark opening beneath the lintel.
    draw.rectangle((24, 18, 55, 47), fill=VOID)
    draw.rectangle((16, 22, 23, 47), fill=STONE)   # inner jambs
    draw.rectangle((56, 22, 63, 47), fill=STONE)
    # Flanking engaged pillars with capitals.
    for x0 in (2, 68):
        draw.rectangle((x0, 20, x0 + 9, 25), fill=STONE_LIGHT)
        draw.rectangle((x0 + 1, 25, x0 + 8, 47), fill=STONE)
        for y in range(31, 47, 6):
            draw.line((x0 + 1, y, x0 + 8, y), fill=STONE_DARK)
    # Masonry seams across crown and jambs.
    _blocks(draw, (12, 14, 67, 18))
    _blocks(draw, (16, 22, 23, 47))
    _blocks(draw, (56, 22, 63, 47))
    draw.line((28, 0, 51, 0), fill=STONE_LIGHT)
    draw.line((20, 6, 59, 6), fill=STONE_LIGHT)
    draw.line((12, 14, 67, 14), fill=STONE_LIGHT)
    draw.line((24, 18, 55, 18), fill=STONE_DARK, width=2)
    # Gold diamond glyphs: crown center and both pillar capitals.
    _diamond(draw, 39, 3)
    _diamond(draw, 6, 22)
    _diamond(draw, 73, 22)
    # Moss threads working through the joints.
    draw.line((14, 16, 20, 16), fill=MOSS, width=2)
    draw.line((60, 15, 66, 15), fill=MOSS, width=2)
    draw.line((17, 30, 17, 38), fill=MOSS)
    draw.line((62, 26, 62, 34), fill=MOSS)
    draw.line((4, 40, 4, 46), fill=MOSS)
    draw.line((75, 36, 75, 43), fill=MOSS)
    return image


def temple_skull() -> Image.Image:
    """A 28x36 carved stone skull on a stepped plinth (the reference's
    flanking guardians). Mute environmental storytelling, like the
    approach's skull stakes — but monumental, carved, and mossy."""
    image = Image.new("RGBA", (28, 36), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Stepped plinth.
    draw.rectangle((1, 31, 26, 35), fill=STONE)
    draw.rectangle((3, 27, 24, 31), fill=STONE)
    draw.line((1, 31, 26, 31), fill=STONE_DARK)
    draw.line((3, 27, 24, 27), fill=STONE_LIGHT)
    _diamond(draw, 13, 33)
    # Cranium: broad and rounded, jaw narrowing below.
    draw.rectangle((4, 4, 23, 21), fill=STONE)
    draw.rectangle((6, 1, 21, 4), fill=STONE)
    draw.rectangle((6, 21, 21, 26), fill=STONE)
    draw.line((6, 1, 21, 1), fill=STONE_LIGHT)
    draw.line((4, 4, 4, 21), fill=STONE_LIGHT)
    # Eye sockets: deep, square-ish voids.
    draw.rectangle((7, 9, 12, 15), fill=VOID)
    draw.rectangle((15, 9, 20, 15), fill=VOID)
    # Nasal cavity and the tooth row.
    draw.polygon(((13, 17), (14, 17), (14, 20), (13, 20)), fill=VOID)
    for x in range(7, 21, 3):
        draw.line((x, 23, x, 25), fill=STONE_DARK)
    draw.line((6, 22, 21, 22), fill=STONE_DARK)
    # Weathering: moss creeping up one side of the plinth and brow.
    draw.line((2, 32, 2, 35), fill=MOSS)
    draw.line((5, 5, 5, 8), fill=MOSS)
    draw.line((19, 2, 22, 2), fill=MOSS)
    return image


def temple_monument(variant: int, face: str = "skull") -> Image.Image:
    """A 48x64 ziggurat monument (reference-directed), in two faces.

    Stepped stone tiers with green painted bands and gold diamond
    glyphs, a carved figure at its heart — a broad skull, or a coiled
    serpent in the same niche — stepped shoulders, and a tiny
    ceremonial stair at the base. Stands on a 3x2 solid footprint and
    rises two tiles above it, placed in guardian rows through the
    temple's open halls. Variant 1 puts the stair front-center; variant
    2 offsets it and weathers differently, so alternating statues in a
    row don't read as copies.
    """
    image = Image.new("RGBA", (48, 64), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    offset = variant % 2
    # Base plinth with a thin painted band.
    draw.rectangle((0, 52, 47, 63), fill=STONE)
    draw.line((0, 52, 47, 52), fill=STONE_LIGHT)
    draw.rectangle((1, 60, 46, 61), fill=BAND)
    draw.line((14, 55, 14, 58), fill=STONE_DARK)
    draw.line((33, 55, 33, 58), fill=STONE_DARK)
    # Second tier: a green stripe and the gold diamond plaque.
    draw.rectangle((3, 44, 44, 52), fill=STONE)
    draw.line((3, 44, 44, 44), fill=STONE_LIGHT)
    draw.rectangle((4, 48, 43, 49), fill=BAND)
    draw.line((4, 50, 43, 50), fill=BAND_DARK)
    draw.rectangle((20, 45, 27, 51), fill=STONE_DARK)
    _diamond(draw, 23, 48)
    # The skull heart between stepped shoulders.
    draw.rectangle((2, 28, 11, 44), fill=STONE)      # shoulders
    draw.rectangle((36, 28, 45, 44), fill=STONE)
    _blocks(draw, (2, 28, 11, 44))
    _blocks(draw, (36, 28, 45, 44))
    draw.rectangle((12, 20, 35, 44), fill=STONE_DARK)  # niche shadow
    if face == "skull":
        draw.rectangle((13, 21, 34, 43), fill=STONE_LIGHT)  # the skull
        draw.rectangle((13, 40, 34, 43), fill=STONE)   # jaw underside
        draw.rectangle((15, 26, 21, 33), fill=VOID)    # eye sockets
        draw.rectangle((26, 26, 32, 33), fill=VOID)
        draw.rectangle((23, 34, 24, 37), fill=VOID)    # nasal notch
        for x in range(15, 33, 3):                     # tooth row
            draw.line((x, 39, x, 43), fill=STONE_DARK)
        draw.line((13, 38, 34, 38), fill=STONE_DARK)
    else:
        # A serpent coiled in the same niche: three stacked coils, the
        # head rising over them with a gold eye and forked tongue.
        for top, bottom, inset in ((38, 43, 1), (32, 37, 3), (27, 31, 5)):
            draw.rectangle((13 + inset, top, 34 - inset, bottom),
                           fill=STONE_LIGHT)
            draw.line((13 + inset, top, 34 - inset, top), fill=STONE)
            draw.line((13 + inset, bottom, 34 - inset, bottom),
                      fill=STONE_DARK)
        draw.rectangle((19, 21, 28, 28), fill=STONE_LIGHT)  # raised head
        draw.line((19, 21, 28, 21), fill=STONE)
        draw.rectangle((21, 23, 22, 25), fill=VOID)    # eye sockets
        draw.rectangle((25, 23, 26, 25), fill=VOID)
        draw.point((21, 23), fill=EYE)                 # a gold glint
        draw.point((25, 23), fill=EYE)
        draw.line((23, 29, 23, 31), fill=STONE_DARK)   # forked tongue
        draw.line((22, 32, 22, 33), fill=STONE_DARK)
        draw.line((24, 32, 24, 33), fill=STONE_DARK)
    # Upper tier with its stripe, diamond plaque, and the cap block.
    draw.rectangle((8, 8, 39, 20), fill=STONE)
    draw.line((8, 8, 39, 8), fill=STONE_LIGHT)
    draw.rectangle((9, 13, 38, 14), fill=BAND)
    draw.line((9, 15, 38, 15), fill=BAND_DARK)
    draw.rectangle((19, 10, 28, 18), fill=STONE_DARK)
    _diamond(draw, 23, 14)
    draw.rectangle((14, 0, 33, 8), fill=STONE)
    draw.line((14, 0, 33, 0), fill=STONE_LIGHT)
    # The tiny stair, and weathering that differs per variant.
    stair_x = 20 if not offset else 30
    draw.rectangle((stair_x, 56, stair_x + 7, 57), fill=STONE_LIGHT)
    draw.rectangle((stair_x, 58, stair_x + 7, 63), fill=STONE)
    draw.line((stair_x, 60, stair_x + 7, 60), fill=STONE_DARK)
    if offset:
        draw.line((4, 30, 4, 38), fill=MOSS)
        draw.line((10, 53, 16, 53), fill=MOSS)
        draw.line((38, 22, 41, 22), fill=MOSS)
    else:
        draw.line((43, 30, 43, 38), fill=MOSS)
        draw.line((30, 53, 37, 53), fill=MOSS)
        draw.line((6, 22, 9, 22), fill=MOSS)
        draw.line((36, 45, 41, 45), fill=MOSS)
    return image


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "objects"
    out_dir.mkdir(parents=True, exist_ok=True)
    images = {
        "temple_arch_ns": north_south_arch(),
        "temple_arch_ew": east_west_arch(),
        "temple_gate": temple_gate(),
        "temple_skull": temple_skull(),
        "temple_monument_1": temple_monument(0),
        "temple_monument_2": temple_monument(1),
        "temple_serpent_monument_1": temple_monument(0, face="serpent"),
        "temple_serpent_monument_2": temple_monument(1, face="serpent"),
        "temple_idol_1": serpent_idol(0),
        "temple_idol_2": serpent_idol(1),
        "temple_stela_1": glyph_stela(0),
        "temple_stela_2": glyph_stela(1),
        "temple_urn_1": cracked_urn(0),
        "temple_urn_2": cracked_urn(1),
        "temple_urn_3": cracked_urn(2),
        "temple_column_1": fallen_column(0),
        "temple_column_2": fallen_column(1),
        **{f"temple_rubble_block_{i + 1}": rubble_block(i)
           for i in range(12)},
    }
    for name, image in images.items():
        out = out_dir / f"{name}.png"
        image.save(out)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
