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


def reactive_flower(active: bool) -> Image.Image:
    """A broad, scratch-readable switch flower in closed/open states."""
    image = Image.new("RGBA", (26, 30), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 25, 24, 29), fill=(7, 31, 34, 170))
    draw.line((13, 26, 13, 13), fill=(39, 131, 71, 255), width=3)
    draw.polygon(
        ((12, 21), (3, 17), (5, 23), (12, 25)),
        fill=(71, 176, 91, 255),
    )
    draw.polygon(
        ((14, 22), (23, 17), (21, 24), (14, 26)),
        fill=(87, 194, 101, 255),
    )
    if active:
        petals = (
            (1, 4, 12, 15), (14, 4, 25, 15),
            (7, 0, 19, 12), (7, 10, 19, 21),
        )
        colors = (
            (82, 219, 207, 255),
            (190, 83, 242, 255),
            (245, 110, 194, 255),
            (93, 192, 250, 255),
        )
        for box, color in zip(petals, colors):
            draw.ellipse(box, fill=color)
        draw.ellipse((9, 7, 17, 15), fill=(247, 218, 86, 255))
        draw.point((13, 10), fill=(255, 249, 211, 255))
    else:
        draw.polygon(
            ((5, 14), (8, 4), (13, 10), (18, 4), (21, 14),
             (13, 18)),
            fill=(171, 69, 214, 255),
        )
        draw.line((7, 14, 13, 10, 19, 14), fill=(236, 105, 190, 255))
        draw.ellipse((10, 10, 16, 16), fill=(231, 194, 74, 255))
    return image


def table_leg(variant: int) -> Image.Image:
    image = Image.new("RGBA", (34, 70), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    lean = (-2, 2)[variant]
    draw.ellipse((2, 62, 32, 69), fill=(7, 27, 30, 185))
    draw.polygon(
        ((7 + lean, 3), (27 + lean, 3), (25, 62), (9, 62)),
        fill=(67, 42, 47, 255),
    )
    draw.polygon(
        ((10 + lean, 4), (24 + lean, 4), (21, 59), (12, 59)),
        fill=(119, 75, 65, 255),
    )
    draw.line((13 + lean, 5, 15, 58), fill=(174, 111, 78, 255), width=2)
    draw.rectangle((6, 58, 28, 65), fill=(74, 45, 48, 255))
    draw.line((8, 59, 26, 59), fill=(158, 96, 72, 255))
    draw.line((20 + lean, 7, 22 + lean, 43), fill=(42, 116, 70, 255))
    return image


def plate() -> Image.Image:
    image = Image.new("RGBA", (52, 28), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 20, 50, 27), fill=(58, 37, 42, 150))
    draw.ellipse((1, 2, 51, 24), fill=(205, 198, 170, 255))
    draw.ellipse((6, 5, 46, 21), fill=(119, 177, 160, 255))
    draw.ellipse((10, 7, 42, 19), fill=(224, 216, 183, 255))
    draw.arc((8, 6, 44, 20), 190, 345, fill=(245, 233, 200, 255), width=2)
    return image


def teacup() -> Image.Image:
    image = Image.new("RGBA", (34, 38), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.ellipse((2, 31, 32, 37), fill=(53, 35, 40, 150))
    draw.ellipse((4, 8, 27, 18), fill=(225, 211, 181, 255))
    draw.rectangle((5, 13, 26, 30), fill=(197, 188, 163, 255))
    draw.ellipse((5, 25, 26, 32), fill=(172, 164, 148, 255))
    draw.ellipse((8, 10, 24, 16), fill=(66, 112, 96, 255))
    draw.ellipse((24, 16, 33, 27), outline=(220, 207, 177, 255), width=3)
    for x, y in ((12, 7), (17, 4), (21, 1)):
        draw.point((x, y), fill=(151, 216, 195, 180))
    return image


def napkin() -> Image.Image:
    image = Image.new("RGBA", (42, 30), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.polygon(
        ((3, 8), (30, 2), (39, 20), (12, 28)),
        fill=(177, 92, 166, 255),
    )
    draw.polygon(
        ((12, 8), (30, 3), (29, 18), (12, 27)),
        fill=(219, 127, 193, 255),
    )
    draw.line((12, 8, 29, 18), fill=(245, 174, 218, 255), width=2)
    return image


def crumbs(variant: int) -> Image.Image:
    image = Image.new("RGBA", (24, 14), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    colors = ((229, 188, 102, 255), (193, 143, 76, 255))
    points = (
        ((3, 9), (9, 4), (16, 10), (21, 3)),
        ((2, 3), (7, 10), (14, 5), (20, 11)),
        ((4, 11), (10, 2), (15, 8), (22, 6)),
    )[variant]
    for index, (x, y) in enumerate(points):
        draw.rectangle((x, y, x + 2, y + 2), fill=colors[index % 2])
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for index in range(3):
        tree(index).save(OUT / f"feywild_tree_{index + 1}.png")
        spiral(index).save(OUT / f"feywild_spiral_{index + 1}.png")
        mushroom(index).save(OUT / f"feywild_mushroom_{index + 1}.png")
    reactive_flower(False).save(
        OUT / "feywild_reactive_flower_closed.png"
    )
    reactive_flower(True).save(
        OUT / "feywild_reactive_flower_open.png"
    )
    for index in range(2):
        table_leg(index).save(OUT / f"fey_table_leg_{index + 1}.png")
    plate().save(OUT / "fey_plate.png")
    teacup().save(OUT / "fey_teacup.png")
    napkin().save(OUT / "fey_napkin.png")
    for index in range(3):
        crumbs(index).save(OUT / f"fey_crumbs_{index + 1}.png")
    print("Generated Feywild vegetation and Giant Tea Table props")


if __name__ == "__main__":
    main()
