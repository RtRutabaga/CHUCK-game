"""Generate the modern city's street furniture: lamps, hydrants, signs.

The city blocks were built and then never furnished. Every one of them
is a road, a kerb, a pavement and a wall of building, and between those
four things there is nothing on the ground at all -- which is why a
street in this game reads as a diagram of a street rather than as one.
The things that fix that are the boring ones: a lamp post every so many
paces, a hydrant on the corner, a stop sign where the road ends.

All three are drawn at the human scale the city already uses. The
businessman sprite is about thirty pixels; a lamp head has to be well
over anyone's head or it stops being a lamp post and becomes a bollard,
so the post is fifty-six. Chuck is fourteen. To him the hydrant is
chest height and the sign is a tower.

The lamp is drawn twice, and the difference between the two is the
whole of the day/night distinction on the object itself: one has a dark
glass head, one has a lit one. They are two files rather than a
two-frame sheet because this is a state and not an animation -- a lamp
is off all day and on all night. The light it *casts* is not here: that
is a pool on the pavement, it belongs to the map rather than to the
sprite, and only the night city gets it. See
src/entities/street_light.py.
"""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"

# The lamp: tall enough to be over a person's head, narrow enough that
# the post is a line rather than a column.
LAMP_W, LAMP_H = 28, 56
HYDRANT_W, HYDRANT_H = 14, 20
SIGN_W, SIGN_H = 18, 44

OUTLINE = (17, 19, 24, 255)
METAL_DARK = (46, 52, 60, 255)
METAL = (74, 82, 92, 255)
METAL_LIT = (112, 124, 134, 255)
SHADOW = (12, 10, 14, 140)

# The lamp's glass, off and on. Sodium rather than white: the city's
# night palette is cold blues, and a warm head is the only thing on the
# street that argues with it.
GLASS_DARK = (58, 62, 66, 255)
GLASS_DIM = (96, 96, 88, 255)
GLASS_LIT = (255, 214, 132, 255)
GLASS_CORE = (255, 246, 214, 255)
HALO = (255, 198, 108, 90)

HYDRANT_RED = (168, 44, 40, 255)
HYDRANT_LIT = (206, 74, 62, 255)
HYDRANT_DARK = (108, 26, 26, 255)
HYDRANT_CAP = (192, 176, 150, 255)

SIGN_RED = (172, 38, 40, 255)
SIGN_RIM = (232, 226, 218, 255)
SIGN_DARK = (112, 24, 28, 255)


def streetlight(lit: bool) -> Image.Image:
    """One cobra-head lamp on a post, off or on.

    The head is drawn as an arm reaching out over the road rather than
    as a bulb on a stick. That arm is the whole silhouette: a straight
    post with a lump on top reads as a signpost from any distance, and
    the thing that says "street lighting" is the overhang.
    """
    image = Image.new("RGBA", (LAMP_W, LAMP_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.ellipse((4, LAMP_H - 6, 20, LAMP_H - 1), fill=SHADOW)

    # Base and post. The base is wider than the post by two pixels a
    # side, which is the cheapest way to make a vertical line look bolted
    # to the ground rather than resting on it.
    draw.rectangle((8, LAMP_H - 6, 16, LAMP_H - 2), fill=OUTLINE)
    draw.rectangle((9, LAMP_H - 5, 15, LAMP_H - 3), fill=METAL_DARK)
    draw.rectangle((10, 10, 14, LAMP_H - 5), fill=OUTLINE)
    draw.rectangle((11, 11, 13, LAMP_H - 6), fill=METAL)
    draw.line((11, 12, 11, LAMP_H - 7), fill=METAL_LIT)

    # The arm: up, over, and down to the head.
    draw.line((12, 11, 12, 6), fill=OUTLINE, width=4)
    draw.line((12, 6, 21, 4), fill=OUTLINE, width=4)
    draw.line((12, 10, 12, 7), fill=METAL, width=2)
    draw.line((13, 7, 20, 5), fill=METAL, width=2)
    draw.line((13, 6, 19, 4), fill=METAL_LIT)

    # The head, hanging under the end of the arm.
    draw.polygon(((16, 5), (26, 3), (27, 8), (17, 10)), fill=OUTLINE)
    if lit:
        draw.polygon(((17, 6), (25, 4), (26, 8), (18, 9)), fill=GLASS_LIT)
        draw.polygon(((19, 6), (24, 5), (24, 7), (19, 8)), fill=GLASS_CORE)
        # A short throw under the head. The pool on the pavement is the
        # entity's job; this is only the air immediately below the glass,
        # which is what stops the lamp reading as a lit rectangle
        # floating on a dark street.
        for step in range(1, 7):
            spread = step
            alpha = max(0, HALO[3] - step * 12)
            draw.polygon(
                ((21 - spread, 9 + step * 2), (26 + spread, 9 + step * 2),
                 (25, 9 + (step - 1) * 2), (22, 9 + (step - 1) * 2)),
                fill=(*HALO[:3], alpha))
    else:
        draw.polygon(((17, 6), (25, 4), (26, 8), (18, 9)), fill=GLASS_DARK)
        draw.polygon(((19, 6), (24, 5), (24, 7), (19, 8)), fill=GLASS_DIM)
    return image


def fire_hydrant() -> Image.Image:
    """Squat, red, and capped. Chest height on Chuck, ankle height on us."""
    image = Image.new("RGBA", (HYDRANT_W, HYDRANT_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.ellipse((1, HYDRANT_H - 5, 13, HYDRANT_H - 1), fill=SHADOW)
    # Flange at the bottom, barrel above it, dome on top.
    draw.rectangle((2, HYDRANT_H - 4, 12, HYDRANT_H - 2), fill=OUTLINE)
    draw.rectangle((3, HYDRANT_H - 4, 11, HYDRANT_H - 3), fill=HYDRANT_DARK)
    draw.rectangle((4, 6, 10, HYDRANT_H - 4), fill=OUTLINE)
    draw.rectangle((5, 6, 9, HYDRANT_H - 5), fill=HYDRANT_RED)
    draw.line((5, 7, 5, HYDRANT_H - 6), fill=HYDRANT_LIT)
    # The collar, which is the line that makes it a hydrant and not a
    # post box.
    draw.rectangle((3, 8, 11, 10), fill=OUTLINE)
    draw.rectangle((4, 9, 10, 9), fill=HYDRANT_LIT)
    # Side outlets, one each way, and the bonnet.
    draw.rectangle((1, 11, 3, 14), fill=OUTLINE)
    draw.rectangle((11, 11, 13, 14), fill=OUTLINE)
    draw.rectangle((2, 12, 2, 13), fill=HYDRANT_CAP)
    draw.rectangle((12, 12, 12, 13), fill=HYDRANT_CAP)
    draw.ellipse((3, 2, 11, 8), fill=OUTLINE)
    draw.ellipse((4, 3, 10, 7), fill=HYDRANT_RED)
    draw.arc((4, 3, 10, 7), 160, 300, fill=HYDRANT_LIT)
    draw.rectangle((6, 0, 8, 3), fill=OUTLINE)
    draw.rectangle((6, 1, 7, 2), fill=HYDRANT_CAP)
    return image


def stop_sign() -> Image.Image:
    """An octagon on a pole, read by its shape rather than its word.

    STOP will not fit legibly across twelve pixels, and half-legible
    lettering is worse than none -- it reads as noise on the sign face
    and makes the octagon harder to see. The shape and the colour do the
    work; they are the only red octagon anywhere in this game.
    """
    image = Image.new("RGBA", (SIGN_W, SIGN_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    draw.ellipse((3, SIGN_H - 5, 15, SIGN_H - 1), fill=SHADOW)
    draw.rectangle((7, 14, 11, SIGN_H - 2), fill=OUTLINE)
    draw.rectangle((8, 15, 10, SIGN_H - 3), fill=METAL)
    draw.line((8, 16, 8, SIGN_H - 4), fill=METAL_LIT)

    # The octagon: a square with its corners taken off, which at this
    # size is the only way to get eight even sides.
    corner = 4
    draw.polygon((
        (corner, 0), (SIGN_W - 1 - corner, 0),
        (SIGN_W - 1, corner), (SIGN_W - 1, 15 - corner),
        (SIGN_W - 1 - corner, 15), (corner, 15),
        (0, 15 - corner), (0, corner),
    ), fill=OUTLINE)
    inner = 3
    draw.polygon((
        (inner + 1, 1), (SIGN_W - 2 - inner, 1),
        (SIGN_W - 2, inner + 1), (SIGN_W - 2, 14 - inner),
        (SIGN_W - 2 - inner, 14), (inner + 1, 14),
        (1, 14 - inner), (1, inner + 1),
    ), fill=SIGN_RIM)
    face = 3
    draw.polygon((
        (face + 1, 2), (SIGN_W - 3 - face, 2),
        (SIGN_W - 3, face + 1), (SIGN_W - 3, 13 - face),
        (SIGN_W - 3 - face, 13), (face + 1, 13),
        (2, 13 - face), (2, face + 1),
    ), fill=SIGN_RED)
    # One dark edge along the bottom so the face is not a flat chip.
    draw.line((4, 12, 13, 12), fill=SIGN_DARK)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Two files rather than a two-frame sheet. This is a state, not an
    # animation: a lamp is off all day and on all night, and the runtime
    # picks the sprite the same way the cabin's table picks its woken
    # one -- by which map is being loaded, once, at spawn.
    streetlight(False).save(OUT / "city_streetlight.png")
    streetlight(True).save(OUT / "city_streetlight_lit.png")
    fire_hydrant().save(OUT / "city_fire_hydrant.png")
    stop_sign().save(OUT / "city_stop_sign.png")
    print(f"Wrote {OUT / 'city_streetlight.png'} and its lit twin "
          f"({LAMP_W}x{LAMP_H})")
    print(f"Wrote {OUT / 'city_fire_hydrant.png'} ({HYDRANT_W}x{HYDRANT_H})")
    print(f"Wrote {OUT / 'city_stop_sign.png'} ({SIGN_W}x{SIGN_H})")


if __name__ == "__main__":
    main()
