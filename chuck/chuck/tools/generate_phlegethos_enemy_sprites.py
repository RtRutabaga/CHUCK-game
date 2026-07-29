"""Generate the Phlegethos enemy sprite sheets (Phase 8).

The lemure is a third UndeadEnemy kind and the fire snake a TempleSnake
variant, so those sheets match the established frame layouts exactly:
three facings (down, up, left) on one row. The spined devil follows the
same three-facing convention; the flameskull is a single hovering frame.
"""

from pathlib import Path

from PIL import Image, ImageDraw

UNDEAD_W, UNDEAD_H = 16, 30
SNAKE_W, SNAKE_H = 18, 10
CLEAR = (0, 0, 0, 0)

# A lemure: a wretched, half-molten blob of damned flesh.
FLESH = (176, 146, 132, 255)
FLESH_DARK = (126, 96, 90, 255)
FLESH_LIGHT = (206, 178, 160, 255)
SORE = (150, 62, 48, 255)
EMBER = (235, 118, 40, 255)
MOUTH = (56, 30, 32, 255)

# A fire snake: cooling black crust over molten orange.
CRUST = (58, 34, 30, 255)
MOLTEN = (206, 66, 16, 255)
HOT = (243, 132, 32, 255)
BRIGHT = (255, 196, 84, 255)


def lemure_frame(facing: str) -> Image.Image:
    """A hunched, sagging wretch -- wider and lumpier than a zombie."""
    image = Image.new("RGBA", (UNDEAD_W, UNDEAD_H), CLEAR)
    draw = ImageDraw.Draw(image)
    # A drooping head sunk into rounded shoulders.
    draw.ellipse((4, 3, 11, 11), fill=FLESH_DARK)
    draw.ellipse((5, 4, 10, 10), fill=FLESH)
    if facing == "down":
        draw.point((6, 7), fill=MOUTH)
        draw.point((9, 7), fill=MOUTH)
        draw.rectangle((7, 9, 8, 9), fill=MOUTH)   # a slack, open mouth
    elif facing == "left":
        draw.point((5, 7), fill=MOUTH)
        draw.rectangle((4, 9, 5, 9), fill=MOUTH)
    # A sagging, formless body: no clothes, just running flesh.
    draw.ellipse((2, 11, 13, 25), fill=FLESH_DARK)
    draw.ellipse((3, 12, 12, 23), fill=FLESH)
    draw.ellipse((5, 13, 10, 18), fill=FLESH_LIGHT)
    # Weeping sores and a few embers caught in the flesh.
    for x, y in ((4, 17), (11, 20), (7, 22)):
        draw.point((x, y), fill=SORE)
    draw.point((10, 15), fill=EMBER)
    draw.point((5, 21), fill=EMBER)
    # Stubby arms; the left one swings forward on the side facing.
    arm_shift = -2 if facing == "left" else 0
    draw.rectangle((0 + arm_shift, 14, 2 + arm_shift, 22), fill=FLESH_DARK)
    draw.rectangle((13, 15, 15, 23), fill=FLESH_DARK)
    # It has no legs to speak of -- it drags a melted base.
    draw.ellipse((3, 24, 12, 29), fill=FLESH_DARK)
    draw.ellipse((5, 25, 10, 28), fill=FLESH)
    return image


def fire_snake_frame(facing: str) -> Image.Image:
    """The temple snake's silhouette rendered as living lava."""
    image = Image.new("RGBA", (SNAKE_W, SNAKE_H), CLEAR)
    draw = ImageDraw.Draw(image)
    coil = (4, 2, 12, 2, 14, 4, 6, 5, 4, 7, 12, 7)
    if facing in {"down", "up"}:
        draw.line(coil, fill=CRUST, width=3)
        draw.line(coil, fill=MOLTEN, width=1)
        head_y = 7 if facing == "down" else 2
        draw.rectangle((11, head_y - 1, 15, head_y + 1), fill=CRUST)
        draw.rectangle((12, head_y, 15, head_y), fill=HOT)
        draw.point((14, head_y), fill=BRIGHT)
        tongue_y = head_y + (2 if facing == "down" else -2)
        draw.point((14, tongue_y), fill=HOT)
    else:
        # Side view: a long molten body with a raised head.
        body = (1, 7, 6, 6, 10, 7, 14, 5)
        draw.line(body, fill=CRUST, width=4)
        draw.line(body, fill=MOLTEN, width=2)
        draw.rectangle((13, 2, 17, 5), fill=CRUST)
        draw.rectangle((14, 3, 17, 4), fill=HOT)
        draw.point((16, 3), fill=BRIGHT)
        draw.point((17, 5), fill=HOT)
    # Cooling crust flecks so the body reads as crusted lava, not paint.
    for x, y in ((5, 3), (9, 6), (3, 6)):
        if 0 <= x < SNAKE_W and 0 <= y < SNAKE_H:
            draw.point((x, y), fill=BRIGHT)
    return image


# A spined devil: a lean red imp bristling with barbed tail spines.
HIDE = (150, 46, 38, 255)
HIDE_DARK = (98, 28, 28, 255)
HIDE_LIGHT = (192, 74, 50, 255)
HORN = (222, 200, 172, 255)
WING = (74, 26, 30, 255)
EYE = (255, 214, 96, 255)

DEVIL_W, DEVIL_H = 16, 22
SKULL_W, SKULL_H = 14, 14

# A flameskull: a bleached skull wreathed in fire.
BONE = (226, 220, 198, 255)
BONE_DARK = (166, 158, 138, 255)
SOCKET = (38, 24, 26, 255)
FLAME = (240, 128, 34, 255)
FLAME_HOT = (255, 196, 84, 255)


def spined_devil_frame(facing: str) -> Image.Image:
    """A perched imp: hunched wings, barbed tail arced over its back."""
    image = Image.new("RGBA", (DEVIL_W, DEVIL_H), CLEAR)
    draw = ImageDraw.Draw(image)
    # Ragged wings behind, hunched high on the shoulders.
    draw.polygon(((1, 8), (5, 5), (5, 15)), fill=WING)
    draw.polygon(((14, 8), (10, 5), (10, 15)), fill=WING)
    # Squat body and clawed feet.
    draw.ellipse((4, 9, 11, 19), fill=HIDE_DARK)
    draw.ellipse((5, 10, 10, 17), fill=HIDE)
    draw.rectangle((5, 19, 6, 21), fill=HIDE_DARK)
    draw.rectangle((9, 19, 10, 21), fill=HIDE_DARK)
    # Head with swept horns.
    draw.ellipse((4, 2, 11, 9), fill=HIDE)
    draw.ellipse((5, 3, 10, 8), fill=HIDE_LIGHT)
    draw.line((4, 3, 2, 0), fill=HORN, width=1)
    draw.line((11, 3, 13, 0), fill=HORN, width=1)
    if facing == "down":
        draw.point((6, 5), fill=EYE)
        draw.point((9, 5), fill=EYE)
    elif facing == "left":
        draw.point((5, 5), fill=EYE)
    # The barbed tail, arced up and ready to flick.
    draw.line((11, 17, 14, 13, 13, 9), fill=HIDE_DARK, width=2)
    for x, y in ((14, 12), (13, 10), (14, 14)):
        draw.point((x, y), fill=FLAME_HOT)
    return image


def flameskull_frame(_facing: str) -> Image.Image:
    """A grinning skull inside a corona of fire."""
    image = Image.new("RGBA", (SKULL_W, SKULL_H), CLEAR)
    draw = ImageDraw.Draw(image)
    # The fire corona.
    draw.ellipse((0, 0, 13, 13), fill=FLAME)
    draw.ellipse((1, 1, 12, 12), fill=FLAME_HOT)
    # The skull itself.
    draw.ellipse((2, 2, 11, 10), fill=BONE)
    draw.ellipse((3, 3, 10, 8), fill=BONE)
    draw.rectangle((4, 5, 5, 7), fill=SOCKET)
    draw.rectangle((8, 5, 9, 7), fill=SOCKET)
    draw.rectangle((6, 8, 7, 9), fill=BONE_DARK)
    # A row of teeth.
    draw.rectangle((4, 10, 9, 11), fill=BONE)
    for x in (5, 7, 9):
        draw.point((x, 11), fill=SOCKET)
    return image


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "hazards"
    out.mkdir(parents=True, exist_ok=True)
    # The flameskull is one hovering frame, not a three-facing sheet.
    flameskull_frame("down").save(out / "flameskull.png")
    print(f"Wrote {out / 'flameskull.png'}")
    for name, make, (w, h) in (
        ("lemure", lemure_frame, (UNDEAD_W, UNDEAD_H)),
        ("fire_snake", fire_snake_frame, (SNAKE_W, SNAKE_H)),
        ("spined_devil", spined_devil_frame, (DEVIL_W, DEVIL_H)),
    ):
        sheet = Image.new("RGBA", (w * 3, h), CLEAR)
        for index, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(make(facing), (index * w, 0))
        path = out / f"{name}.png"
        sheet.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
