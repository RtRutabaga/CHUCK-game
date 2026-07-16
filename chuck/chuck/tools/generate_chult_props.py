"""Generate dense-jungle props for Chult."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"


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


def jungle_shrub(variant: int) -> Image.Image:
    """Low, overlapping broad leaves inspired by dense tropical understory."""
    image = Image.new("RGBA", (28, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = (22, 34, 22, 190)
    leaf_dark = (14, 57, 29, 255)
    leaf_mid = (27, 94, 40, 255)
    leaf = (51, 125, 52, 255)
    leaf_light = (91, 151, 64, 255)
    vein = (25, 70, 36, 255)
    stem = (44, 67, 32, 255)

    center_x = 14 + (-1, 0, 1)[variant]
    center_y = 19
    draw.ellipse((2, 19, 26, 23), fill=shadow)
    draw.line((center_x, 21, center_x, 8), fill=stem, width=2)

    # Each leaf is a pointed four-corner polygon with a darker underside and
    # single-pixel central vein. Overlap builds the compact reference shape.
    leaves = (
        ((center_x, 19), (2, 15), (1, 8), (11, 15)),
        ((center_x, 18), (5, 9), (9, 2), (15, 14)),
        ((center_x, 17), (10, 8), (14, 0), (19, 10)),
        ((center_x, 18), (18, 8), (25, 4), (26, 13)),
        ((center_x, 19), (21, 13), (27, 15), (20, 21)),
        ((center_x, 20), (8, 15), (3, 20), (11, 23)),
    )
    order = ((0, 3, 1, 4, 2, 5), (3, 0, 4, 1, 5, 2), (1, 4, 0, 5, 3, 2))[variant]
    palette = (leaf_dark, leaf_mid, leaf, leaf_mid, leaf_light, leaf)
    for draw_index, leaf_index in enumerate(order):
        points = leaves[leaf_index]
        shifted = tuple((x + (variant - 1 if draw_index % 2 else 0), y)
                        for x, y in points)
        draw.polygon(shifted, fill=palette[leaf_index])
        tip = shifted[2]
        draw.line((center_x, center_y - 1, tip[0], tip[1]),
                  fill=vein, width=1)
    draw.rectangle((center_x - 1, 18, center_x + 1, 22), fill=leaf_dark)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("jungle_tree_1", jungle_tree(0)),
        ("jungle_tree_2", jungle_tree(1)),
        ("jungle_tree_3", jungle_tree(2)),
        ("jungle_shrub_1", jungle_shrub(0)),
        ("jungle_shrub_2", jungle_shrub(1)),
        ("jungle_shrub_3", jungle_shrub(2)),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
