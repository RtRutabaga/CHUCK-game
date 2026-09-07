"""Generate the castle banners that hang on the collided desert's walls.

The castle fragment out east is the one world in the collision Chuck has
never been to, so there is no tileset anywhere to import it from and
nothing about it is established except that it is cold grey ashlar. What
that left was a walled courtyard nobody could tell the allegiance of --
correct stone, no owner.

A banner fixes that in one object, and it is the only thing in the
fragment with a colour in it. Everything else out there is grey stone,
grey rubble and sand; three metres of dyed cloth hanging off a wall is
the whole of what says somebody lived here and cared whose castle it
was.

Four frames of a slow lift and fall. Not a flap: the desert air on
these maps is dead still -- the fires are out, the snow falls straight
down -- and a banner snapping in a wind nothing else on the map can
feel would be the one thing moving for its own reasons.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"

# Two tiles wide and two deep, and the depth is not a style choice.
#
# Props in this game anchor to the bottom edge of their tile and draw
# upward, so a banner authored on the wall itself would rise off the
# battlements like a flag on a pole. What is wanted is cloth hanging
# down a wall -- so it is authored on the ground tile in front of the
# wall instead, and cut to exactly two tiles so that drawing up from
# there puts the bracket on top of the stone and the hem on the floor
# below it. One tile shorter and the bracket sinks into the wall; one
# taller and it floats above it with nothing holding it up.
W, H = 26, 34
FRAMES = 4

# Cloth. Deep red and gold, because the fragment it hangs on is
# unrelieved grey and this is the only warm thing that will ever be in
# it -- and because the one other castle in this game, Waterdeep's, is
# gold on brown, and these two should not be the same house.
CLOTH_DARK = (98, 22, 34, 255)
CLOTH = (146, 34, 46, 255)
CLOTH_LIT = (178, 56, 62, 255)
TRIM = (196, 162, 78, 255)
TRIM_DARK = (140, 112, 48, 255)
DEVICE = (214, 190, 120, 255)
POLE = (66, 60, 54, 255)
POLE_LIT = (98, 88, 78, 255)
IRON = (54, 56, 60, 255)


def banner(frame: int) -> Image.Image:
    """One banner, at one moment of its lift.

    The sway is applied as a per-row horizontal offset that grows toward
    the hem, which is how cloth actually moves -- pinned at the top,
    free at the bottom. Offsetting the whole shape instead made it a
    sign swinging on a hinge.
    """
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    phase = frame / FRAMES * math.tau

    # The iron bracket and the pole it is slung from, bolted to the wall
    # above. Without these the cloth reads as painted onto the stone.
    draw.rectangle((3, 1, 22, 3), fill=IRON)
    draw.rectangle((4, 2, 21, 2), fill=POLE_LIT)
    draw.rectangle((2, 0, 4, 6), fill=IRON)
    draw.rectangle((21, 0, 23, 6), fill=IRON)
    draw.rectangle((5, 4, 20, 5), fill=POLE)

    left, right = 5, 20
    hem = H - 6
    for y in range(5, hem):
        along = (y - 5) / (hem - 5)
        # Pinned at the top, free at the hem.
        sway = math.sin(phase + along * 1.6) * along * 2.2
        offset = round(sway)
        # A vertical fold down each third of the cloth: the shading is
        # what gives it a surface, and without it the banner is a red
        # rectangle with a stripe.
        for x in range(left, right + 1):
            fold = math.sin((x - left) / (right - left) * math.pi * 3 + phase)
            if fold > 0.45:
                colour = CLOTH_LIT
            elif fold < -0.45:
                colour = CLOTH_DARK
            else:
                colour = CLOTH
            image.putpixel((min(W - 1, max(0, x + offset)), y), colour)

    # The gold band across the top, and the device below it.
    band_sway = round(math.sin(phase + 0.3) * 0.6)
    draw.rectangle((left + band_sway, 6, right + band_sway, 8), fill=TRIM)
    draw.line((left + band_sway, 8, right + band_sway, 8), fill=TRIM_DARK)

    # The device: a plain lozenge, because a heraldic charge at eleven
    # pixels across is a smudge and a smudge reads as damage. A shape
    # that is obviously a shape reads as a device.
    centre = 12 + round(math.sin(phase + 0.8) * 1.2)
    for step in range(7):
        spread = 4 - abs(step - 3)
        draw.line((centre - spread, 13 + step, centre + spread, 13 + step),
                  fill=DEVICE)
    for step in range(5):
        spread = 2 - abs(step - 2)
        draw.line((centre - spread, 15 + step, centre + spread, 15 + step),
                  fill=CLOTH_DARK)

    # The hem: cut into two points, which is what a banner has and a
    # curtain does not.
    hem_sway = round(math.sin(phase + 1.6) * 2.2)
    for step in range(6):
        span = 6 - step
        draw.line((left + hem_sway, hem + step,
                   left + hem_sway + span, hem + step), fill=CLOTH_DARK)
        draw.line((right + hem_sway - span, hem + step,
                   right + hem_sway, hem + step), fill=CLOTH_DARK)
    draw.line((left + hem_sway, hem, right + hem_sway, hem), fill=TRIM_DARK)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for frame in range(FRAMES):
        banner(frame).save(OUT / f"castle_banner_{frame + 1}.png")
    print(f"Wrote {FRAMES} frames of {W}x{H} to {OUT / 'castle_banner_N.png'}")


if __name__ == "__main__":
    main()
