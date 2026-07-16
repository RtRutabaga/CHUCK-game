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


def sailing_cog() -> Image.Image:
    """A one-masted human vessel, dramatically oversized beside Chuck."""
    image = Image.new("RGBA", (144, 112), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    outline = (24, 25, 22, 255)
    wood_dark = (57, 43, 29, 255)
    wood = (105, 73, 42, 255)
    wood_light = (146, 102, 56, 255)
    rope = (157, 137, 89, 255)
    sail_dark = (135, 127, 96, 255)
    sail = (191, 177, 128, 255)
    sail_light = (213, 197, 146, 255)
    iron = (45, 49, 45, 255)
    vine_dark = (19, 62, 34, 255)
    vine = (43, 104, 49, 255)

    # Mast and rigging rise first so the hull and rail sit naturally in front.
    draw.rectangle((69, 10, 75, 79), fill=outline)
    draw.rectangle((71, 10, 74, 79), fill=wood_light)
    draw.line((18, 77, 72, 10), fill=rope, width=1)
    draw.line((126, 79, 74, 10), fill=rope, width=1)
    draw.rectangle((34, 24, 111, 28), fill=outline)
    draw.rectangle((36, 25, 109, 26), fill=wood_light)

    # A broad, weathered square sail with an uneven lower edge.
    draw.polygon(((39, 29), (106, 29), (110, 60), (99, 66),
                  (75, 63), (54, 67), (36, 59)), fill=outline)
    draw.polygon(((41, 30), (103, 30), (107, 58), (97, 63),
                  (75, 60), (55, 64), (39, 57)), fill=sail)
    draw.polygon(((74, 31), (101, 31), (104, 57), (96, 61),
                  (76, 58)), fill=sail_light)
    draw.line((72, 30, 73, 61), fill=sail_dark, width=2)
    draw.line((43, 43, 105, 43), fill=sail_dark, width=1)
    draw.line((46, 56, 101, 57), fill=sail_dark, width=1)
    # Repairs keep the vessel used rather than storybook-pristine.
    draw.rectangle((49, 35, 58, 43), outline=sail_dark)
    draw.line((49, 35, 58, 43), fill=sail_dark, width=1)
    draw.rectangle((84, 48, 94, 57), outline=sail_dark)

    # High-sided cog hull, broad enough to dominate a native viewport.
    hull = ((7, 75), (25, 69), (121, 69), (138, 80),
            (126, 101), (104, 107), (30, 109), (13, 99))
    draw.polygon(hull, fill=outline)
    draw.polygon(((11, 77), (27, 73), (119, 73), (133, 81),
                  (122, 97), (102, 103), (32, 105), (17, 96)), fill=wood)
    draw.line((20, 82, 129, 82), fill=wood_light, width=3)
    draw.line((23, 91, 126, 90), fill=wood_dark, width=3)
    draw.line((31, 101, 116, 99), fill=wood_light, width=2)
    for x in range(34, 121, 15):
        draw.line((x, 75, x - 2, 102), fill=wood_dark, width=2)
    for x in (43, 67, 91, 115):
        draw.ellipse((x, 84, x + 6, 90), fill=iron)
        draw.ellipse((x + 2, 86, x + 4, 88), fill=(16, 22, 27, 255))

    # Deck, rails, raised stern, and a rope ladder readable at native scale.
    draw.rectangle((23, 67, 124, 73), fill=outline)
    draw.rectangle((25, 67, 122, 70), fill=wood_light)
    for x in range(27, 123, 12):
        draw.rectangle((x, 61, x + 2, 70), fill=wood_dark)
    draw.line((27, 62, 121, 62), fill=rope, width=2)
    draw.rectangle((105, 58, 126, 70), fill=outline)
    draw.rectangle((108, 60, 124, 69), fill=wood)
    draw.rectangle((111, 62, 120, 68), fill=(30, 31, 27, 255))
    draw.line((28, 72, 28, 94), fill=rope, width=1)
    draw.line((35, 72, 35, 93), fill=rope, width=1)
    for y in range(76, 94, 5):
        draw.line((28, y, 35, y), fill=rope, width=1)

    # Jungle growth tangles around the stranded hull without hiding its shape.
    draw.line((15, 96, 35, 104, 58, 101), fill=vine_dark, width=2)
    draw.line((119, 96, 101, 104, 83, 102), fill=vine, width=2)
    for x, y in ((20, 99), (40, 104), (91, 103), (113, 98)):
        draw.ellipse((x - 3, y - 5, x + 3, y + 1), fill=vine)
        draw.line((x, y, x + 5, y - 7), fill=vine_dark, width=1)
    draw.line((71, 16, 79, 8, 89, 10), fill=vine_dark, width=1)
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
        ("sailing_cog", sailing_cog()),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
