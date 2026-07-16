"""Generate oversized expedition and dense-jungle props for Chult."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"


def backpack() -> Image.Image:
    image = Image.new("RGBA", (30, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = (43, 38, 27, 255)
    canvas = (112, 91, 52, 255)
    light = (151, 126, 69, 255)
    leather = (73, 49, 31, 255)
    wet = (49, 69, 49, 255)
    draw.ellipse((3, 27, 27, 31), fill=shadow)
    draw.rounded_rectangle((4, 6, 25, 29), radius=4, fill=canvas, outline=leather, width=2)
    draw.rectangle((6, 3, 23, 9), fill=wet, outline=leather)
    draw.rectangle((8, 9, 21, 15), fill=light)
    draw.line((7, 16, 22, 16), fill=leather, width=2)
    draw.line((10, 6, 10, 28), fill=leather, width=2)
    draw.line((20, 6, 20, 28), fill=leather, width=2)
    draw.rectangle((1, 17, 5, 27), fill=canvas, outline=leather)
    draw.rectangle((24, 18, 28, 27), fill=canvas, outline=leather)
    return image


def boot() -> Image.Image:
    image = Image.new("RGBA", (26, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = (39, 37, 27, 255)
    leather = (71, 52, 35, 255)
    light = (105, 75, 44, 255)
    mud = (46, 61, 39, 255)
    draw.ellipse((1, 12, 24, 15), fill=shadow)
    draw.polygon(((3, 1), (13, 1), (14, 9), (23, 10), (24, 14),
                  (8, 14), (3, 11)), fill=leather)
    draw.line((5, 3, 12, 3), fill=light, width=2)
    draw.line((6, 6, 12, 6), fill=light)
    draw.rectangle((8, 12, 24, 14), fill=mud)
    return image


def jungle_tree(variant: int) -> Image.Image:
    """A human-scale tropical tree rising well above its solid canopy tile."""
    image = Image.new("RGBA", (34, 46), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = (24, 34, 24, 210)
    trunk_dark = (45, 51, 31, 255)
    trunk = (76, 67, 37, 255)
    trunk_light = (102, 82, 43, 255)
    leaf_dark = (13, 49, 31, 255)
    leaf_mid = (22, 77, 40, 255)
    leaf = (37, 105, 49, 255)
    leaf_light = (68, 126, 58, 255)
    vine = (36, 88, 47, 255)

    lean = (-2, 0, 2)[variant]
    crown_x = 17 + lean
    draw.ellipse((7, 40, 28, 45), fill=shadow)
    draw.polygon(((14, 42), (20, 42), (19 + lean, 17),
                  (15 + lean, 17)), fill=trunk_dark)
    draw.polygon(((16, 41), (19, 41), (18 + lean, 18),
                  (16 + lean, 18)), fill=trunk)
    draw.line((17, 39, 17 + lean, 20), fill=trunk_light, width=1)

    # Dense layered crown: dark mass first, then individual broad leaves.
    blobs = (
        (-13, -3, 15, 15), (-7, -9, 15, 16), (1, -10, 16, 17),
        (7, -3, 14, 15), (-10, 5, 15, 14), (2, 5, 16, 14),
    )
    for index, (dx, dy, w, h) in enumerate(blobs):
        x = crown_x + dx + ((index + variant) % 3 - 1)
        y = 13 + dy
        draw.ellipse((x, y, x + w, y + h),
                     fill=leaf_dark if index < 2 else leaf_mid)

    leaf_tips = (
        ((17, 15), (3, 4), (12, 17), (1, 22)),
        ((17, 14), (8, 1), (15, 17), (6, 10)),
        ((18, 14), (18, 0), (20, 18), (23, 5)),
        ((18, 15), (31, 5), (21, 18), (33, 20)),
        ((17, 16), (28, 27), (18, 20), (22, 31)),
        ((16, 16), (6, 29), (14, 20), (1, 24)),
    )
    for index, polygon in enumerate(leaf_tips):
        shifted = tuple((x + lean, y + (variant if index % 2 else 0))
                        for x, y in polygon)
        draw.polygon(shifted, fill=leaf if index % 2 else leaf_light)
        draw.line(shifted[:2], fill=vine, width=1)

    draw.line((8 + variant * 3, 14, 7 + variant * 3, 35), fill=vine, width=1)
    draw.line((26 - variant * 2, 13, 29 - variant * 2, 31), fill=vine, width=1)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("expedition_backpack", backpack()),
        ("abandoned_boot", boot()),
        ("jungle_tree_1", jungle_tree(0)),
        ("jungle_tree_2", jungle_tree(1)),
        ("jungle_tree_3", jungle_tree(2)),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
