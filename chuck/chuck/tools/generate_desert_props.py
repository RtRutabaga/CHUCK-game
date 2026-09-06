"""Generate the Phase 13 desert's standing props.

The region's tileset can only say what the ground is made of. Everything
in this file is the layer above that: the things a player walks up to
and around, drawn taller than the tile they stand on and y-sorted with
Chuck so he passes behind them.

Three groups, and each is answering a different complaint about how the
region looked with only terrain in it.

The ruins were rectangles of cut stone lying flat. A ruin reads as a
ruin because of what has *fallen*: columns snapped off at different
heights, one lying full length across the floor, blocks tipped out of
the wall they came from. None of that can live in a 16-pixel tile,
because all of it is taller than a tile and none of it repeats.

The oasis had palm shade with nothing underneath it. The canopy tiles
were always meant to be the top of something, and until there was a
trunk to go with them they read as bushes drawn on top of Chuck.

The orc camp's fires were one tile each. At that size the ring of
stones is three pixels of rock, which is why they read as pots rather
than as the place a camp is built around.

Everything here shares the tileset's own palette rather than picking
one again by eye, for the reason the whole region does: two copies of
a colour drift apart, and drift invisibly.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"

# The tileset's stone, one value either side of it, and the two extremes
# the fine detail needs.
RUIN = (166, 142, 110, 255)
RUIN_LIT = (192, 170, 136, 255)
RUIN_PALE = (214, 196, 164, 255)
RUIN_DARK = (112, 92, 70, 255)
RUIN_SHADE = (82, 66, 50, 255)
# Cast shadow on sand. Warm and translucent: a grey shadow on this
# ground reads as a hole in it.
CAST = (92, 62, 34, 96)

ROCK = (150, 116, 82, 255)
ROCK_LIT = (186, 148, 108, 255)
ROCK_DARK = (110, 82, 58, 255)
ROCK_SHADE = (78, 58, 42, 255)

TRUNK = (124, 96, 62, 255)
TRUNK_LIT = (158, 126, 84, 255)
TRUNK_DARK = (84, 62, 40, 255)
PALM = (36, 68, 40, 255)
PALM_MID = (48, 88, 46, 255)
PALM_LIT = (72, 116, 60, 255)
COCONUT = (96, 74, 46, 255)

ASH = (128, 118, 108, 255)
ASH_LIT = (158, 150, 142, 255)
ASH_DARK = (88, 80, 74, 255)
CHAR = (48, 42, 40, 255)
EMBER = (206, 96, 44, 255)
EMBER_HOT = (244, 168, 72, 255)
SMOKE = (150, 140, 132, 70)


# --------------------------------------------------------------------
# Ruins


def _cast_shadow(draw, box) -> None:
    """One flat ellipse on the ground, always cast the same way.

    The sun in this region comes from the upper left -- the sand tiles
    and the cliff faces are both lit that way -- so every shadow in the
    desert falls down and to the right. Props lit from different
    directions is the single fastest way to make a scene look assembled
    rather than drawn.
    """
    draw.ellipse(box, fill=CAST)


def desert_column(variant: int) -> Image.Image:
    """A column snapped off part way up. Solid; Chuck walks around it.

    Three heights rather than three decorations. What makes a field of
    these read as a ruin is that no two of them broke at the same
    place: the same column repeated at one height is a colonnade, which
    is a building that is still standing.
    """
    height = (46, 34, 24)[variant]
    image = Image.new("RGBA", (20, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    _cast_shadow(draw, (1, height - 8, 18, height - 1))
    # A plinth, because a column standing straight out of the sand has
    # nothing holding it up and reads as a pipe.
    draw.rectangle((1, height - 7, 18, height - 2), fill=RUIN_DARK)
    draw.rectangle((2, height - 7, 17, height - 4), fill=RUIN)
    draw.line((2, height - 7, 17, height - 7), fill=RUIN_LIT)

    top = 4
    # The shaft, and it is a thick one. Drawn ten pixels across it read
    # as a post: a column is a piece of a building, and the thing that
    # says so is that it is wider than the rat standing next to it.
    draw.rectangle((3, top, 16, height - 7), fill=RUIN)
    draw.rectangle((3, top, 6, height - 7), fill=RUIN_LIT)
    draw.rectangle((14, top, 16, height - 7), fill=RUIN_DARK)
    draw.line((3, top, 3, height - 7), fill=RUIN_PALE)
    draw.line((16, top, 16, height - 7), fill=RUIN_SHADE)

    # One flute, on the lit side of the middle. Cut in twos and threes
    # the shaft came back as a ladder -- at fourteen pixels across, the
    # groove is a detail, not the structure.
    draw.line((10, top + 2, 10, height - 8), fill=RUIN_DARK)
    draw.line((9, top + 2, 9, height - 8), fill=RUIN_LIT)

    # Drum joints. A column this size was built in sections and the
    # sections are what it comes apart along.
    for y in range(top + 8, height - 8, 11):
        draw.line((3, y, 16, y), fill=RUIN_DARK)
        draw.line((3, y + 1, 16, y + 1), fill=RUIN_PALE)

    # The break. An ellipse of the inside of the stone, with the near
    # rim chipped away: a flat top reads as a column somebody cut.
    draw.ellipse((3, top - 4, 16, top + 3), fill=RUIN_PALE)
    draw.ellipse((5, top - 2, 14, top + 2), fill=RUIN_LIT)
    for chip, depth in ((4, 3), (10, 4), (14, 2)):
        if (chip + variant) % 2:
            draw.rectangle((chip, top - 4, chip + 1, top - 4 + depth),
                           fill=(0, 0, 0, 0))
    return image


def desert_column_fallen(variant: int) -> Image.Image:
    """A column lying where it came down, in two or three pieces.

    Drawn as one long cylinder it looked like a pipe on the sand. What
    makes it read as fallen stone is the gaps: the drums have rolled
    slightly apart, so the joints are open and the line of it is not
    quite straight.
    """
    image = Image.new("RGBA", (36, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    _cast_shadow(draw, (2, 9, 34, 15))

    drums = (((1, 12), (14, 25), (27, 35)),
             ((2, 15), (17, 34), None),
             ((1, 9), (11, 21), (24, 34)))[variant]
    for index, span in enumerate(drums):
        if span is None:
            continue
        left, right = span
        # A pixel of sag on the far pieces, so the line of the column
        # bends where it broke rather than staying ruled.
        drop = 0 if index == 0 else 1
        draw.rectangle((left, 3 + drop, right, 11 + drop), fill=RUIN)
        draw.line((left, 3 + drop, right, 3 + drop), fill=RUIN_LIT)
        draw.line((left, 4 + drop, right, 4 + drop), fill=RUIN_PALE)
        draw.line((left, 10 + drop, right, 10 + drop), fill=RUIN_DARK)
        draw.line((left, 11 + drop, right, 11 + drop), fill=RUIN_SHADE)
        # The circular end of each piece, which is the whole tell.
        draw.ellipse((left, 3 + drop, left + 3, 11 + drop), fill=RUIN_DARK)
        draw.ellipse((left + 1, 4 + drop, left + 3, 10 + drop), fill=RUIN_PALE)
        for band in range(left + 6, right - 1, 6):
            draw.line((band, 4 + drop, band, 10 + drop), fill=RUIN_DARK)
    return image


def desert_rubble(variant: int) -> Image.Image:
    """Cut blocks tipped out of a wall and left in a heap.

    Each block is drawn with a lit top face and a shaded front, which is
    the only way a rectangle of one colour becomes a thing with a top
    you could stand on. Flat, they were glyphs; the pieces are
    square-edged rather than rounded because that is what separates
    these from the canyon -- the desert made the rock, somebody made
    these.
    """
    image = Image.new("RGBA", (24, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    _cast_shadow(draw, (1, 13, 23, 19))

    # Back to front, and overlapping. Laid out side by side they read as
    # a row of crates rather than as a pile of something knocked over.
    piles = (
        ((6, 3, 17, 11), (1, 8, 12, 18), (11, 9, 22, 18)),
        ((4, 2, 14, 9), (13, 5, 23, 13), (0, 9, 11, 18), (9, 11, 21, 18)),
        ((8, 4, 20, 12), (2, 7, 13, 18), (12, 10, 23, 18)),
    )[variant]
    for index, (left, top, right, bottom) in enumerate(piles):
        face = RUIN_LIT if index % 2 else RUIN
        draw.rectangle((left, top, right, bottom), fill=RUIN_SHADE)
        draw.rectangle((left, top, right - 1, bottom - 1), fill=face)
        # The top face: three pixels of it, paler than the front. This
        # is the whole trick -- without it a block is a swatch.
        draw.rectangle((left, top, right - 1, top + 2), fill=RUIN_PALE)
        draw.line((left, top + 3, right - 1, top + 3), fill=RUIN_DARK)
        draw.line((left, top, left, bottom - 1), fill=RUIN_LIT)
        draw.line((right - 1, top, right - 1, bottom - 1), fill=RUIN_DARK)
        # One course line across the front of the taller pieces: these
        # were cut, and the cut is what stops them being loose rock.
        if bottom - top > 8:
            mid = (top + bottom) // 2 + 1
            draw.line((left + 1, mid, right - 2, mid), fill=RUIN_DARK)
    return image


# --------------------------------------------------------------------
# The oasis


def desert_palm(variant: int) -> Image.Image:
    """A date palm: the trunk the canopy tiles never had.

    The oasis's shade is an overhead terrain -- art drawn above Chuck so
    he walks under it -- and it works, but a canopy with nothing holding
    it up reads as a bush someone has drawn on top of him. This is the
    other half of that: a solid trunk standing on the turf, tall enough
    that its own crown is well above his head.

    The trunk leans. A palm grown beside water leans over the water,
    and three of these standing perfectly upright in a row is an avenue
    rather than an oasis.
    """
    width, height = 30, (54, 46, 50)[variant]
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    lean = (-5, 3, 2)[variant]
    base_x = 15 - lean // 2
    crown = (base_x + lean, 13)

    _cast_shadow(draw, (base_x - 6, height - 7, base_x + 6, height - 1))

    # The trunk, drawn as a stack of short segments along a curve, which
    # is what gives a palm its ringed, slightly knobbly line.
    steps = height - 18
    for step in range(steps):
        t = step / max(1, steps - 1)
        x = base_x + round(lean * t * t)
        y = height - 4 - step
        half = 2 if t < 0.6 else 1
        draw.line((x - half, y, x + half, y), fill=TRUNK)
        draw.point((x - half, y), fill=TRUNK_LIT)
        draw.point((x + half, y), fill=TRUNK_DARK)
        # Leaf scars, at uneven spacing. Ruled every third pixel they
        # were the rungs of a ladder; a palm's scars crowd together
        # further up, where the tree grew more slowly.
        if step % (3 + (step // 9) % 2) == 0:
            draw.line((x - half, y, x + half - 1, y), fill=TRUNK_DARK)
            draw.point((x - half, y), fill=TRUNK_LIT)

    # Coconuts under the crown, on the shaded side.
    for index in range(2 + variant % 2):
        draw.ellipse((crown[0] - 3 + index * 3, crown[1] + 2,
                      crown[0] - 1 + index * 3, crown[1] + 4), fill=COCONUT)

    # The mass of the crown first, so the fronds have something behind
    # them. Without it the tree is seven strokes on the sky and the eye
    # sees through it to the ground.
    draw.ellipse((crown[0] - 9, crown[1] - 5, crown[0] + 9, crown[1] + 6),
                 fill=PALM)

    # Seven fronds. Each is drawn as a spine that bends downward at its
    # halfway point with leaflets combed off both sides of it: struck as
    # straight rays they read as a starburst, and a palm frond is heavy.
    for index in range(7):
        angle = -math.pi + index * (math.pi / 6.0) + (variant * 0.12)
        reach = 13 if index % 2 else 11
        mid = (crown[0] + math.cos(angle) * reach * 0.55,
               crown[1] + math.sin(angle) * reach * 0.45)
        tip = (crown[0] + math.cos(angle) * reach,
               crown[1] + math.sin(angle) * reach * 0.75 + 5)
        shade = PALM_LIT if index % 3 == 1 else PALM_MID
        draw.line((crown[0], crown[1], mid[0], mid[1]), fill=shade, width=2)
        draw.line((mid[0], mid[1], tip[0], tip[1]), fill=PALM, width=2)
        # Leaflets: three short strokes off each half of the spine.
        for leaf in range(1, 4):
            t = leaf / 4.0
            px = mid[0] + (tip[0] - mid[0]) * t
            py = mid[1] + (tip[1] - mid[1]) * t
            side = 3 if index < 4 else -3
            draw.line((px, py, px + side * 0.6, py + 2), fill=shade)
            draw.line((px, py, px - side * 0.6, py + 2), fill=PALM)

    draw.ellipse((crown[0] - 2, crown[1] - 2, crown[0] + 2, crown[1] + 2),
                 fill=PALM)
    return image


# --------------------------------------------------------------------
# The orc camp


def desert_fire_pit(frame: int) -> Image.Image:
    """A camp fire pit, at the size a camp is actually built around.

    The tile version of this was one 16-pixel square, which meant the
    ring of stones was three pixels of rock and the fire inside it was
    two. Orcs sit around this: it wants to be wider than a rat is tall,
    with stones you can tell are stones.

    It is burnt down rather than burning. That is what the camp already
    said before this was drawn, and lighting them would be answering a
    question nobody asked -- so what moves is the embers, breathing
    under the ash, and a thread of smoke off them.
    """
    image = Image.new("RGBA", (36, 26), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    _cast_shadow(draw, (2, 16, 34, 25))

    # The ash bed first, so the stones sit on its edge rather than
    # floating above it.
    draw.ellipse((5, 8, 30, 22), fill=ASH_DARK)
    draw.ellipse((7, 9, 28, 21), fill=ASH)
    draw.ellipse((11, 12, 24, 19), fill=ASH_DARK)
    for speck in range(9):
        sx = 8 + (speck * 5 + frame) % 20
        sy = 10 + (speck * 3) % 10
        draw.point((sx, sy), fill=ASH_LIT if speck % 2 else CHAR)

    # Charred logs across the middle, still recognisably logs.
    for (x0, y0, x1, y1) in ((11, 17, 23, 12), (13, 12, 25, 18),
                             (10, 14, 20, 15)):
        draw.line((x0, y0, x1, y1), fill=CHAR, width=3)
        draw.line((x0, y0 - 1, x1, y1 - 1), fill=(70, 60, 54, 255))

    # Embers, breathing. Their positions are fixed and only their heat
    # changes: embers that move around read as sparks, and sparks mean
    # something is still burning.
    embers = ((15, 16), (19, 14), (22, 17), (17, 13), (21, 12), (13, 15))
    for index, (ex, ey) in enumerate(embers):
        phase = (frame + index * 2) % 6
        if phase < 2:
            draw.point((ex, ey), fill=EMBER_HOT)
            draw.point((ex + 1, ey), fill=EMBER)
        elif phase < 4:
            draw.point((ex, ey), fill=EMBER)
        else:
            draw.point((ex, ey), fill=(120, 62, 40, 255))

    # The stone ring, laid round the outside so the ash is contained by
    # it. Uneven sizes and uneven spacing: a ring of identical stones is
    # a wall, and a camp fire is a thing somebody piled up in a hurry.
    stones = ((4, 11, 5, 6), (7, 6, 6, 5), (14, 4, 7, 5), (22, 5, 6, 5),
              (28, 9, 6, 6), (29, 15, 5, 6), (23, 18, 7, 5),
              (14, 20, 8, 5), (7, 18, 6, 5), (3, 16, 5, 5))
    for index, (x, y, w, h) in enumerate(stones):
        draw.rectangle((x, y, x + w, y + h), fill=ROCK_SHADE)
        draw.rectangle((x, y, x + w - 1, y + h - 1),
                       fill=ROCK_DARK if index % 3 == 0 else ROCK)
        draw.line((x, y, x + w - 1, y), fill=ROCK_LIT)
        draw.point((x + 1, y + 1), fill=ROCK_LIT)
        draw.point((x + w - 1, y + h - 1), fill=ROCK_SHADE)

    # ...and one thread of smoke, which is the only thing that says the
    # fire went out recently rather than a season ago.
    for step in range(5):
        sx = 19 + round(2.0 * math.sin((step + frame * 0.7) * 0.9))
        sy = 8 - step * 2
        if sy < 0:
            break
        draw.point((sx, sy), fill=SMOKE)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    images = []
    for index in range(3):
        images.append((f"desert_column_{index + 1}", desert_column(index)))
        images.append((f"desert_column_fallen_{index + 1}",
                       desert_column_fallen(index)))
        images.append((f"desert_rubble_{index + 1}", desert_rubble(index)))
        images.append((f"desert_palm_{index + 1}", desert_palm(index)))
    for frame in range(6):
        images.append((f"desert_fire_pit_{frame + 1}", desert_fire_pit(frame)))
    for name, image in images:
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path} ({image.width}x{image.height})")


if __name__ == "__main__":
    main()
