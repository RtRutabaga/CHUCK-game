"""Generate luminous standing props for the first Feywild riverbank."""

from pathlib import Path
import math

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
TRANSPARENT = (0, 0, 0, 0)


def tree(variant: int) -> Image.Image:
    image = Image.new("RGBA", (42, 56), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    trunk_dark = (48, 37, 67, 255)
    trunk = (77, 53, 91, 255)
    trunk_light = (113, 67, 118, 255)
    leaves = (
        (18, 78, 66, 255),
        (29, 112, 70, 255),
        (62, 151, 85, 255),
        (92, 190, 105, 255),
    )
    lean = (-2, 0, 2)[variant]
    draw.ellipse((6, 49, 36, 55), fill=(8, 32, 35, 170))
    draw.polygon(
        ((16, 52), (25, 52), (23 + lean, 19), (18 + lean, 19)),
        fill=trunk_dark,
    )
    draw.polygon(
        ((19, 51), (23, 51), (21 + lean, 20), (19 + lean, 20)),
        fill=trunk,
    )
    draw.line((20, 48, 20 + lean, 22), fill=trunk_light)
    blobs = (
        (1, 7, 20, 17), (13, 1, 32, 19), (24, 8, 41, 25),
        (5, 18, 25, 34), (20, 18, 40, 35),
    )
    for index, box in enumerate(blobs):
        x0, y0, x1, y1 = box
        draw.ellipse(
            (x0 + lean, y0, x1 + lean, y1),
            fill=leaves[min(index, 3)],
        )
    glow = (
        (76, 194, 255, 255),
        (193, 82, 244, 255),
        (244, 108, 191, 255),
    )[variant]
    for x, y in ((9 + lean, 14), (29 + lean, 11), (19 + lean, 25)):
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(*glow[:3], 65))
        draw.point((x, y), fill=glow)
    draw.line(
        (8 + variant * 7, 16, 7 + variant * 7, 43),
        fill=(48, 139, 77, 255),
    )
    return image


def spiral(variant: int) -> Image.Image:
    image = Image.new("RGBA", (30, 40), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    stem = (38, 112, 67, 255)
    leaf = (74, 176, 88, 255)
    color = (
        (72, 191, 255, 255),
        (193, 83, 246, 255),
        (244, 111, 193, 255),
    )[variant]
    draw.ellipse((3, 35, 27, 39), fill=(8, 35, 36, 150))
    draw.line((15, 36, 15, 12), fill=stem, width=3)
    draw.polygon(((14, 27), (3, 22), (6, 30), (14, 32)), fill=leaf)
    draw.polygon(((16, 30), (28, 24), (25, 33), (16, 35)), fill=leaf)
    points = []
    for step in range(24):
        angle = step * 0.68
        radius = 10 - step * 0.34
        points.append((
            round(15 + math.cos(angle) * radius),
            round(11 + math.sin(angle) * radius),
        ))
    draw.line(points, fill=color, width=2)
    draw.ellipse((7, 3, 23, 19), outline=(*color[:3], 55), width=2)
    draw.point((15, 11), fill=(245, 238, 255, 255))
    return image


def mushroom(variant: int) -> Image.Image:
    image = Image.new("RGBA", (24, 24), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    cap = (
        (183, 76, 224, 255),
        (236, 92, 176, 255),
        (66, 166, 232, 255),
    )[variant]
    draw.ellipse((2, 19, 22, 23), fill=(9, 34, 35, 150))
    draw.rectangle((10, 9, 14, 20), fill=(205, 190, 151, 255))
    draw.rectangle((11, 10, 12, 19), fill=(242, 225, 184, 255))
    draw.ellipse((2, 2, 22, 13), fill=cap)
    draw.rectangle((4, 8, 20, 12), fill=cap)
    for x, y in ((7, 6), (13, 4), (18, 8)):
        draw.rectangle((x, y, x + 1, y + 1), fill=(244, 239, 211, 255))
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for index in range(3):
        tree(index).save(OUT / f"feywild_tree_{index + 1}.png")
        spiral(index).save(OUT / f"feywild_spiral_{index + 1}.png")
        mushroom(index).save(OUT / f"feywild_mushroom_{index + 1}.png")
    print("Generated Feywild trees, spiral plants, and mushrooms")


if __name__ == "__main__":
    main()
