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


def sailing_cog(overgrown: bool = True) -> Image.Image:
    """A huge three-quarter-view cog between bird's-eye and side elevation.

    overgrown draws the jungle vines of the cog stranded in Chult. The
    same ship tied up in Waterdeep harbour at the end is drawn clean:
    nothing grows on a hull that has been at sea.
    """
    image = Image.new("RGBA", (224, 152), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    outline = (24, 25, 22, 255)
    wood_dark = (57, 43, 29, 255)
    wood = (105, 73, 42, 255)
    wood_light = (146, 102, 56, 255)
    sail_dark = (135, 127, 96, 255)
    sail = (191, 177, 128, 255)
    sail_light = (213, 197, 146, 255)
    iron = (45, 49, 45, 255)
    vine_dark = (19, 62, 34, 255)
    vine = (43, 104, 49, 255)

    # The visible deck is a broad diamond. Its depth is what moves the view
    # away from a street-level side profile while retaining a readable hull.
    deck_outline = ((7, 96), (21, 82), (145, 62), (216, 91),
                    (201, 113), (75, 131))
    draw.polygon(deck_outline, fill=outline)
    draw.polygon(((13, 95), (25, 86), (145, 67), (208, 92),
                  (197, 108), (76, 125)), fill=wood_light)
    for offset in range(0, 50, 8):
        draw.line((20 + offset * 2, 91 - offset // 3,
                   81 + offset * 2, 118 - offset // 3),
                  fill=wood, width=2)
    draw.line((15, 98, 145, 75, 201, 96), fill=wood_dark, width=3)

    # The southwest end now tapers into an upturned bow instead of the former
    # boxy stern face. The squared far end remains a readable cog transom.
    draw.polygon(((7, 96), (75, 131), (201, 113), (194, 137),
                  (77, 151), (29, 140), (13, 119)), fill=outline)
    draw.polygon(((13, 100), (77, 135), (195, 118), (189, 132),
                  (78, 146), (34, 136), (18, 117)), fill=wood)
    draw.line((12, 105, 35, 127, 78, 142), fill=wood_light, width=3)
    draw.line((18, 118, 39, 136, 76, 146), fill=wood_dark, width=3)
    draw.line((82, 134, 193, 119), fill=wood_dark, width=3)
    draw.line((8, 88, 8, 103), fill=wood_light, width=4)
    for x, y in ((101, 129), (128, 125), (155, 121), (181, 117)):
        draw.ellipse((x, y, x + 8, y + 7), fill=iron)
        draw.ellipse((x + 2, y + 2, x + 5, y + 5),
                     fill=(16, 22, 27, 255))
    for x in range(92, 196, 18):
        draw.line((x, 123 + (196 - x) // 24,
                   x - 2, 143 - (x - 92) // 12), fill=wood_dark, width=2)

    # Sparse wooden posts follow the deck edge. No connecting rope is drawn,
    # and the former northwest deck box is gone, leaving a clean open deck.
    for x, y in ((10, 88), (42, 80), (77, 74), (145, 59),
                 (173, 70), (199, 80), (214, 88), (75, 120)):
        draw.line((x, y, x, y + 11), fill=wood_dark, width=3)
    draw.polygon(((133, 83), (151, 79), (165, 85), (147, 90)), fill=outline)
    draw.polygon(((137, 83), (151, 81), (160, 85), (147, 88)), fill=wood_dark)

    # Paint the complete sail assembly after the hull. Its entire silhouette
    # stays visible and correctly blocks the rear deck instead of being cut off
    # by it. There is deliberately no rigging or rope detail.
    draw.line((115, 104, 113, 7), fill=outline, width=9)
    draw.line((115, 104, 114, 7), fill=wood_light, width=4)
    draw.polygon(((44, 17), (176, 28), (184, 84), (42, 69)), fill=outline)
    draw.polygon(((49, 21), (172, 32), (179, 79), (47, 65)), fill=sail)
    draw.polygon(((114, 27), (171, 33), (177, 76), (115, 70)),
                 fill=sail_light)
    draw.line((48, 42, 176, 53), fill=sail_dark, width=2)
    draw.line((46, 61, 179, 74), fill=sail_dark, width=2)
    draw.polygon(((67, 27), (83, 29), (84, 43), (67, 41)),
                 outline=sail_dark)
    draw.line((67, 27, 84, 43), fill=sail_dark, width=1)
    draw.polygon(((137, 55), (153, 57), (155, 70), (139, 68)),
                 outline=sail_dark)

    # The lower mast is redrawn over the sail and deck to remain visibly
    # planted in its broad wooden foot on the planks.
    draw.line((115, 77, 115, 108), fill=outline, width=9)
    draw.line((115, 77, 115, 107), fill=wood_light, width=4)
    draw.polygon(((106, 105), (123, 105), (128, 112), (103, 112)),
                 fill=outline)
    draw.polygon(((109, 104), (121, 104), (123, 109), (107, 109)),
                 fill=wood)

    if not overgrown:
        return image
    # Jungle growth tangles around the stranded base; there is no ladder.
    draw.line((20, 125, 48, 143, 77, 139), fill=vine_dark, width=3)
    draw.line((193, 128, 160, 144, 126, 141), fill=vine, width=3)
    for x, y in ((26, 128), (53, 143), (132, 143), (184, 132)):
        draw.ellipse((x - 3, y - 5, x + 3, y + 1), fill=vine)
        draw.line((x, y, x + 5, y - 7), fill=vine_dark, width=1)
    draw.line((111, 17, 120, 9, 130, 12), fill=vine_dark, width=1)
    return image


def skull_stake() -> Image.Image:
    """A restrained human skull on a weathered stake, enormous to Chuck."""
    image = Image.new("RGBA", (12, 30), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    outline = (29, 29, 25, 255)
    wood_dark = (53, 42, 28, 255)
    wood = (91, 66, 38, 255)
    bone_dark = (116, 111, 83, 255)
    bone = (181, 173, 128, 255)
    bone_light = (211, 199, 149, 255)

    draw.polygon(((5, 29), (7, 29), (7, 10), (6, 7), (5, 10)), fill=outline)
    draw.rectangle((5, 11, 6, 28), fill=wood)
    draw.line((7, 12, 7, 27), fill=wood_dark, width=1)
    draw.rectangle((3, 2, 9, 9), fill=outline)
    draw.rectangle((2, 3, 10, 7), fill=outline)
    draw.rectangle((3, 1, 8, 9), fill=bone)
    draw.rectangle((2, 3, 9, 7), fill=bone)
    draw.rectangle((4, 1, 7, 2), fill=bone_light)
    draw.rectangle((3, 5, 4, 6), fill=outline)
    draw.rectangle((7, 5, 8, 6), fill=outline)
    draw.point((6, 7), fill=bone_dark)
    draw.rectangle((4, 8, 8, 10), fill=bone_dark)
    draw.point((5, 9), fill=bone_light)
    draw.point((7, 9), fill=bone_light)
    return image


# The temple's own stone, and what is left of the paint on it. A
# Mesoamerican temple was stuccoed and painted red; a few centuries of
# jungle leaves ochre in the cut of the carving and bare stone elsewhere.
T_DARK = (45, 57, 49, 255)
T_STONE = (73, 83, 65, 255)
T_LIGHT = (112, 119, 84, 255)
T_PALE = (146, 150, 112, 255)
T_OCHRE = (122, 74, 52, 255)
T_OCHRE_LIGHT = (154, 96, 64, 255)
T_MOSS = (39, 82, 48, 255)
T_VOID = (10, 17, 17, 255)


def temple_serpent_head() -> Image.Image:
    """The serpent head at the foot of a balustrade.

    The one piece of a Mesoamerican pyramid everybody can name. Each
    ramp down the side of the stair ends in a head at plaza level, jaws
    open, facing whoever is walking up. Big features and few of them:
    at this size a finely carved snake is a grey smudge, and what has
    to survive is the brow, the eye and the open jaw.
    """
    image = Image.new("RGBA", (28, 26), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # The neck, the width of the ramp it comes out of.
    draw.rectangle((8, 0, 19, 6), fill=T_DARK)
    draw.rectangle((9, 0, 18, 5), fill=T_LIGHT)

    # The skull, wide at the brows.
    draw.rectangle((1, 5, 26, 17), fill=T_DARK)
    draw.rectangle((2, 6, 25, 16), fill=T_STONE)
    # Brow scrolls, and the ochre still sitting in the cut of them.
    draw.rectangle((2, 6, 11, 10), fill=T_LIGHT)
    draw.rectangle((16, 6, 25, 10), fill=T_LIGHT)
    draw.rectangle((2, 6, 11, 7), fill=T_OCHRE)
    draw.rectangle((16, 6, 25, 7), fill=T_OCHRE)
    # Eyes: dark, deep, and large enough to find at a glance.
    draw.rectangle((4, 9, 9, 13), fill=T_DARK)
    draw.rectangle((18, 9, 23, 13), fill=T_DARK)
    draw.rectangle((5, 10, 8, 12), fill=T_VOID)
    draw.rectangle((19, 10, 22, 12), fill=T_VOID)
    draw.point((6, 10), fill=T_PALE)
    draw.point((20, 10), fill=T_PALE)

    # The jaws, open. Upper lip, the dark of the throat, lower lip.
    draw.rectangle((2, 15, 25, 17), fill=T_PALE)
    draw.rectangle((3, 18, 24, 22), fill=T_VOID)
    for x in (5, 11, 17, 21):
        draw.rectangle((x, 17, x + 2, 20), fill=T_PALE)
    for x in (8, 14, 20):
        draw.rectangle((x, 20, x + 2, 23), fill=T_PALE)
    draw.rectangle((2, 23, 25, 25), fill=T_STONE)
    draw.line((2, 25, 25, 25), fill=T_DARK)
    draw.rectangle((10, 24, 17, 25), fill=T_OCHRE)

    draw.rectangle((3, 2, 5, 4), fill=T_MOSS)
    draw.rectangle((22, 13, 24, 15), fill=T_MOSS)
    return image


def temple_altar() -> Image.Image:
    """The round drum altar, out in the plaza on the stair's axis."""
    image = Image.new("RGBA", (26, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # The drum's side, then its top face sitting on it.
    draw.rectangle((0, 7, 25, 16), fill=T_DARK)
    draw.ellipse((0, 10, 25, 19), fill=T_DARK)
    draw.ellipse((1, 9, 24, 18), fill=T_STONE)
    draw.rectangle((1, 7, 24, 14), fill=T_STONE)
    # One recessed groove round it, which is where the paint survives.
    draw.line((1, 12, 24, 12), fill=T_OCHRE)
    draw.line((1, 13, 24, 13), fill=T_OCHRE_LIGHT)
    # The top face.
    draw.ellipse((0, 0, 25, 13), fill=T_DARK)
    draw.ellipse((1, 1, 24, 12), fill=T_LIGHT)
    draw.ellipse((4, 3, 21, 10), fill=T_PALE)
    draw.ellipse((9, 5, 16, 8), fill=T_LIGHT)
    draw.rectangle((5, 2, 8, 3), fill=T_MOSS)
    return image


def temple_roof_comb() -> Image.Image:
    """The house on the summit, and the crest standing on top of it.

    The cresteria: a tall pierced slab of masonry carried on the roof,
    there for no reason but to be seen from the plaza. Nothing else in
    the game's vocabulary reads so immediately as this particular part
    of the world.
    """
    image = Image.new("RGBA", (160, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # The house: battered walls under a corbel, sitting on the summit
    # platform, with the doorways below in the map's own tiles.
    draw.rectangle((34, 46, 125, 63), fill=T_DARK)
    draw.rectangle((36, 46, 123, 63), fill=T_STONE)
    draw.rectangle((38, 48, 121, 53), fill=T_LIGHT)
    # The frieze: a greca band across the facade, ochre in the recess.
    draw.rectangle((38, 54, 121, 61), fill=T_OCHRE)
    for base in range(40, 120, 12):
        draw.line((base, 55, base + 7, 55), fill=T_PALE)
        draw.line((base, 55, base, 60), fill=T_PALE)
        draw.line((base, 60, base + 4, 60), fill=T_PALE)
        draw.line((base + 4, 58, base + 4, 60), fill=T_PALE)

    # The corbelled roofline, flaring wider than the wall it sits on.
    draw.rectangle((30, 38, 129, 46), fill=T_DARK)
    draw.rectangle((32, 39, 127, 45), fill=T_STONE)
    draw.rectangle((32, 39, 127, 41), fill=T_LIGHT)

    # The comb itself: a slab standing on the ridge, stepped in twice,
    # pierced right through so the sky shows in it.
    draw.rectangle((54, 14, 105, 39), fill=T_DARK)
    draw.rectangle((56, 15, 103, 38), fill=T_STONE)
    draw.rectangle((62, 4, 97, 16), fill=T_DARK)
    draw.rectangle((64, 5, 95, 15), fill=T_STONE)
    draw.rectangle((73, 0, 86, 6), fill=T_DARK)
    draw.rectangle((75, 1, 84, 6), fill=T_LIGHT)
    for x in (61, 76, 91):
        draw.rectangle((x, 20, x + 7, 27), fill=T_VOID)
        draw.rectangle((x, 30, x + 7, 35), fill=T_VOID)
    for x in (68, 83):
        draw.rectangle((x, 7, x + 5, 12), fill=T_VOID)
    # Paint in the carving, and the jungle getting into the joints.
    draw.line((56, 17, 103, 17), fill=T_OCHRE)
    draw.line((56, 37, 103, 37), fill=T_OCHRE)
    draw.line((64, 6, 95, 6), fill=T_OCHRE_LIGHT)
    for spot in ((58, 28, 60, 34), (100, 22, 102, 31), (40, 42, 47, 44),
                 (112, 41, 120, 44), (88, 36, 94, 38)):
        draw.rectangle(spot, fill=T_MOSS)
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
        ("waterdeep_docked_ship", sailing_cog(overgrown=False)),
        ("skull_stake", skull_stake()),
        ("temple_serpent_head", temple_serpent_head()),
        ("temple_altar", temple_altar()),
        ("temple_roof_comb", temple_roof_comb()),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
