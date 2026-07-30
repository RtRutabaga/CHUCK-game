"""Generate the rubble-pass basalt debris and cliff-fed lava fall."""

from pathlib import Path
import random

from PIL import Image, ImageDraw


OUT = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "objects"
TRANSPARENT = (0, 0, 0, 0)
BASALT = (47, 39, 43, 255)
BASALT_DARK = (27, 25, 30, 255)
BASALT_LIGHT = (74, 58, 55, 255)
EMBER = (218, 64, 20, 255)
LAVA = (239, 91, 18, 255)
LAVA_LIGHT = (255, 177, 43, 255)


def rubble(variant: int) -> Image.Image:
    rng = random.Random(811 + variant * 97)
    canvas = Image.new("RGBA", (32, 26), TRANSPARENT)
    draw = ImageDraw.Draw(canvas)
    for _ in range(1 + (variant % 3 == 0)):
        width = rng.randint(10, 17)
        height = rng.randint(6, 10)
        x = rng.randint(1, 30 - width)
        y = rng.randint(12, 24 - height)
        lean = rng.randint(-3, 3)
        top = (
            (x, y + 4), (x + 5 + lean, y),
            (x + width, y + 1), (x + width - 4, y + 5),
        )
        front = (
            (x, y + 4), (x + width - 4, y + 5),
            (x + width - 4, y + height), (x + 2, y + height),
        )
        side = (
            (x + width - 4, y + 5), (x + width, y + 1),
            (x + width, y + height - 4), (x + width - 4, y + height),
        )
        draw.polygon(top, fill=BASALT_LIGHT)
        draw.polygon(front, fill=BASALT)
        draw.polygon(side, fill=BASALT_DARK)
        crack_x = x + width // 2
        draw.line(
            (crack_x, y + 5, crack_x - 2, y + 9, crack_x + 1, y + height - 1),
            fill=BASALT_DARK,
        )
        if variant % 2 == 0:
            draw.point((crack_x, y + height - 2), fill=EMBER)
    return canvas


def lava_fall(frame: int) -> Image.Image:
    image = Image.new("RGBA", (48, 96), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Jagged cliff lip and shadowed cleft.
    draw.polygon(
        ((0, 4), (9, 0), (19, 4), (31, 1), (47, 6),
         (47, 25), (35, 30), (12, 28), (0, 23)),
        fill=BASALT_DARK,
    )
    draw.polygon(
        ((0, 4), (9, 0), (19, 4), (31, 1), (47, 6),
         (42, 12), (5, 11)),
        fill=BASALT_LIGHT,
    )
    draw.line((2, 22, 12, 28, 35, 30, 46, 24), fill=BASALT)
    # Hard pixel-stepped ribbons match the existing lava tiles. Their edges,
    # highlights, and impact splash shift across four authored frames.
    phase = frame % 4
    sway = (-1, 0, 1, 0)[phase]
    draw.polygon(
        ((14 + sway, 11), (35, 12), (38 - sway, 34), (33, 58),
         (38 + sway, 82), (34, 95), (12, 95), (16 - sway, 76),
         (11 + sway, 54), (16, 31)),
        fill=LAVA,
    )
    draw.polygon(
        ((19 + sway, 11), (25 + sway, 12), (23 - sway, 35), (28, 51),
         (24 + sway, 71), (27, 94), (18, 94), (20 - sway, 73),
         (16, 54), (21 + sway, 31)),
        fill=LAVA_LIGHT,
    )
    highlight_y = phase * 5
    for y in range(17 - highlight_y, 91, 20):
        if y >= 12:
            draw.line((34 - sway, y, 31 + sway, min(93, y + 10)),
                      fill=EMBER, width=2)
    # Foam-equivalent molten splash where the fall meets the river.
    draw.rectangle((7, 90, 40, 95), fill=LAVA)
    draw.rectangle((3 + phase, 93, 44 - (3 - phase), 95), fill=EMBER)
    draw.rectangle((14 - sway * 2, 90, 31 + sway, 92), fill=LAVA_LIGHT)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for index in range(10):
        rubble(index).save(OUT / f"phlegethos_rubble_{index + 1}.png")
    for frame in range(4):
        suffix = "" if frame == 0 else f"_{frame + 1}"
        lava_fall(frame).save(OUT / f"phlegethos_lava_fall{suffix}.png")
    print("Generated 10 dark rubble variants and 4 lava-fall frames")


if __name__ == "__main__":
    main()
