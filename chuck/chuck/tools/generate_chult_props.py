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
    """A huge three-quarter-view cog between bird's-eye and side elevation."""
    image = Image.new("RGBA", (224, 152), (0, 0, 0, 0))
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

    # Rigging and sail establish the shallow three-quarter angle before the
    # hull is layered over them. The mast leans with the projected deck axis.
    draw.line((113, 91, 110, 10), fill=outline, width=8)
    draw.line((113, 91, 111, 10), fill=wood_light, width=3)
    draw.line((15, 88, 111, 10), fill=rope, width=1)
    draw.line((213, 93, 111, 10), fill=rope, width=1)
    draw.polygon(((54, 25), (158, 32), (165, 69), (116, 87),
                  (48, 62)), fill=outline)
    draw.polygon(((57, 27), (155, 34), (161, 67), (116, 83),
                  (52, 60)), fill=sail)
    draw.polygon(((111, 31), (154, 35), (158, 64), (116, 79)),
                 fill=sail_light)
    draw.line((111, 29, 114, 82), fill=sail_dark, width=2)
    draw.line((54, 43, 158, 49), fill=sail_dark, width=1)
    draw.line((52, 57, 159, 64), fill=sail_dark, width=1)
    draw.polygon(((70, 32), (84, 33), (85, 45), (69, 43)),
                 outline=sail_dark)
    draw.line((70, 32, 85, 45), fill=sail_dark, width=1)
    draw.polygon(((128, 51), (143, 52), (145, 63), (130, 67)),
                 outline=sail_dark)

    # The visible deck is a broad diamond. Its depth is what moves the view
    # away from a street-level side profile while retaining a readable hull.
    deck_outline = ((11, 84), (139, 61), (215, 91), (77, 121))
    draw.polygon(deck_outline, fill=outline)
    draw.polygon(((17, 84), (139, 66), (207, 92), (77, 115)), fill=wood_light)
    for offset in range(0, 50, 8):
        draw.line((29 + offset * 2, 84 - offset // 3,
                   90 + offset * 2, 108 - offset // 3),
                  fill=wood, width=2)
    draw.line((21, 89, 139, 71, 197, 94), fill=wood_dark, width=3)

    # A tall starboard side and foreshortened stern make the hull substantial.
    draw.polygon(((77, 115), (215, 91), (196, 132), (77, 149)), fill=outline)
    draw.polygon(((80, 119), (208, 96), (191, 127), (80, 144)), fill=wood)
    draw.polygon(((11, 84), (77, 115), (77, 149), (22, 126)), fill=outline)
    draw.polygon(((17, 88), (73, 118), (73, 143), (27, 123)), fill=wood_dark)
    draw.line((82, 126, 203, 105), fill=wood_light, width=3)
    draw.line((81, 138, 196, 120), fill=wood_dark, width=3)
    for x, y in ((101, 124), (128, 119), (155, 114), (181, 109)):
        draw.ellipse((x, y, x + 8, y + 7), fill=iron)
        draw.ellipse((x + 2, y + 2, x + 5, y + 5),
                     fill=(16, 22, 27, 255))
    for x in range(92, 196, 18):
        draw.line((x, 116 + (196 - x) // 20,
                   x - 2, 139 - (x - 92) // 10), fill=wood_dark, width=2)

    # Railings follow all three visible deck edges; a raised stern cabin and
    # hatch make the top plane usable visual space for the later sailor.
    for x, y in ((20, 80), (43, 76), (68, 72), (94, 68), (139, 58),
                 (165, 68), (190, 78), (211, 87), (57, 103), (76, 112)):
        draw.line((x, y, x, y + 11), fill=wood_dark, width=3)
    draw.line((19, 80, 139, 58, 213, 87), fill=rope, width=2)
    draw.line((18, 86, 76, 116), fill=rope, width=2)
    draw.polygon(((23, 76), (63, 69), (88, 79), (47, 88)), fill=outline)
    draw.polygon(((28, 76), (62, 72), (81, 79), (47, 84)), fill=wood)
    draw.polygon(((40, 75), (59, 73), (69, 78), (49, 81)),
                 fill=(29, 30, 26, 255))
    draw.polygon(((133, 83), (151, 79), (165, 85), (147, 90)), fill=outline)
    draw.polygon(((137, 83), (151, 81), (160, 85), (147, 88)), fill=wood_dark)

    # Rope ladder on the near face and jungle growth around the stranded base.
    draw.line((44, 106, 39, 132), fill=rope, width=2)
    draw.line((53, 110, 49, 136), fill=rope, width=2)
    for y in range(113, 134, 6):
        draw.line((43, y, 51, y + 3), fill=rope, width=1)
    draw.line((20, 125, 48, 143, 77, 139), fill=vine_dark, width=3)
    draw.line((193, 128, 160, 144, 126, 141), fill=vine, width=3)
    for x, y in ((26, 128), (53, 143), (132, 143), (184, 132)):
        draw.ellipse((x - 3, y - 5, x + 3, y + 1), fill=vine)
        draw.line((x, y, x + 5, y - 7), fill=vine_dark, width=1)
    draw.line((111, 17, 120, 9, 130, 12), fill=vine_dark, width=1)
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
