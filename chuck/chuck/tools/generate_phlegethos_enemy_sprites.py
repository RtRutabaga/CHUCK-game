"""Generate the Phlegethos lemure and fire-snake sprite sheets (Phase 8).

Both reuse existing gameplay wholesale -- the lemure is a third
UndeadEnemy kind (Chultan zombie/skeleton lifecycle) and the fire snake
is a TempleSnake variant -- so these sheets match those frame layouts
exactly: three facings (down, up, left) on one row.
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


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "hazards"
    out.mkdir(parents=True, exist_ok=True)
    for name, make, (w, h) in (
        ("lemure", lemure_frame, (UNDEAD_W, UNDEAD_H)),
        ("fire_snake", fire_snake_frame, (SNAKE_W, SNAKE_H)),
    ):
        sheet = Image.new("RGBA", (w * 3, h), CLEAR)
        for index, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(make(facing), (index * w, 0))
        path = out / f"{name}.png"
        sheet.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
