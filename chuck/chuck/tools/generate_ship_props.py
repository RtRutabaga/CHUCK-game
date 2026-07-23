"""Generate human-scale crew-quarter furniture in native pixel art."""

from pathlib import Path

from PIL import Image, ImageDraw


OUT = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "objects"
TRANSPARENT = (0, 0, 0, 0)
WOOD_DARK = (63, 42, 29, 255)
WOOD = (112, 74, 43, 255)
WOOD_LIGHT = (151, 102, 57, 255)
CANVAS_DARK = (95, 75, 62, 255)
CANVAS = (151, 126, 96, 255)
CANVAS_LIGHT = (184, 158, 119, 255)
ROPE = (184, 149, 91, 255)
BRASS = (183, 142, 58, 255)
BRASS_LIGHT = (225, 190, 91, 255)
DARK = (31, 24, 22, 255)
LEAF = (91, 105, 55, 255)
SAIL_DARK = (161, 145, 102, 255)
SAIL = (218, 202, 151, 255)
SAIL_LIGHT = (239, 225, 174, 255)


def hammock() -> Image.Image:
    """A hanging human bunk looming two tiles above its anchor."""
    image = Image.new("RGBA", (20, 34), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.line((2, 0, 5, 11), fill=ROPE, width=1)
    draw.line((17, 0, 14, 11), fill=ROPE, width=1)
    draw.line((2, 0, 2, 28), fill=WOOD_DARK, width=2)
    draw.line((17, 0, 17, 28), fill=WOOD_DARK, width=2)
    draw.line((4, 10, 15, 10), fill=ROPE, width=1)
    # Deep curved canvas belly; Chuck can visibly pass under its overhang.
    for y, inset in ((11, 0), (12, 0), (13, 1), (14, 1), (15, 2),
                     (16, 2), (17, 3), (18, 4), (19, 5)):
        draw.line((4 + inset, y, 15 - inset, y), fill=CANVAS, width=1)
    draw.line((5, 11, 14, 11), fill=CANVAS_LIGHT, width=1)
    draw.line((9, 13, 12, 18), fill=CANVAS_DARK, width=1)
    draw.rectangle((1, 27, 4, 31), fill=WOOD)
    draw.rectangle((15, 27, 18, 31), fill=WOOD)
    draw.line((1, 31, 4, 31), fill=WOOD_LIGHT, width=1)
    draw.line((15, 31, 18, 31), fill=WOOD_LIGHT, width=1)
    return image


def round_table() -> Image.Image:
    """An enormous round mess table, architectural at Chuck's scale."""
    image = Image.new("RGBA", (34, 25), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.ellipse((1, 1, 32, 17), fill=WOOD_DARK)
    draw.ellipse((2, 1, 31, 15), fill=WOOD)
    draw.arc((3, 2, 30, 14), 195, 345, fill=WOOD_LIGHT, width=2)
    draw.line((6, 8, 27, 8), fill=WOOD_DARK, width=1)
    draw.line((17, 2, 17, 15), fill=WOOD_DARK, width=1)
    draw.rectangle((7, 14, 11, 23), fill=WOOD_DARK)
    draw.rectangle((23, 14, 27, 23), fill=WOOD_DARK)
    draw.line((6, 23, 12, 23), fill=WOOD_LIGHT, width=1)
    draw.line((22, 23, 28, 23), fill=WOOD_LIGHT, width=1)
    return image


def captain_chest(stage: int) -> Image.Image:
    """A broad brass-bound sea chest across four opening stages."""
    image = Image.new("RGBA", (32, 24), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    if stage == 3:
        draw.rectangle((2, 0, 29, 7), fill=WOOD_DARK)
        draw.rectangle((3, 1, 28, 5), fill=WOOD)
        draw.line((3, 6, 28, 6), fill=WOOD_LIGHT, width=1)
        draw.rectangle((2, 7, 29, 12), fill=DARK)
    elif stage == 2:
        draw.polygon(((2, 2), (29, 2), (27, 9), (4, 9)),
                     fill=WOOD_DARK)
        draw.polygon(((4, 3), (27, 3), (25, 7), (6, 7)), fill=WOOD)
        draw.line((5, 3, 26, 3), fill=WOOD_LIGHT, width=1)
        draw.rectangle((2, 8, 29, 12), fill=DARK)
    elif stage == 1:
        draw.polygon(((2, 3), (29, 3), (28, 9), (3, 9)),
                     fill=WOOD_DARK)
        draw.polygon(((3, 4), (28, 4), (27, 7), (4, 7)), fill=WOOD)
        draw.line((4, 4, 27, 4), fill=WOOD_LIGHT, width=1)
        draw.rectangle((2, 8, 29, 12), fill=DARK)
    else:
        draw.rounded_rectangle((1, 3, 30, 11), radius=4, fill=WOOD_DARK)
        draw.rounded_rectangle((2, 3, 29, 9), radius=3, fill=WOOD)
        draw.line((4, 4, 27, 4), fill=WOOD_LIGHT, width=1)
    draw.rectangle((1, 11, 30, 22), fill=WOOD)
    draw.rectangle((1, 19, 30, 22), fill=WOOD_DARK)
    draw.line((2, 12, 29, 12), fill=WOOD_LIGHT, width=1)
    for x in (5, 25):
        lid_top = 3 if stage == 0 else (7 if stage == 3 else 8)
        draw.rectangle((x, lid_top, x + 2, 22), fill=BRASS)
        draw.line((x + 1, lid_top + 1, x + 1, 21),
                  fill=BRASS_LIGHT, width=1)
    draw.rectangle((14, 11, 18, 16), fill=BRASS)
    draw.rectangle((15, 12, 17, 14), fill=DARK)
    return image


def mast_sail() -> Image.Image:
    """A ship-scale hybrid-top-down mast and broad, fully visible sail."""
    image = Image.new("RGBA", (224, 192), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # The sail is enormous beside Chuck and deliberately overlaps the deck.
    sail = [(9, 18), (197, 31), (214, 137), (30, 124)]
    draw.polygon(sail, fill=DARK)
    inner = [(14, 23), (191, 36), (207, 131), (35, 119)]
    draw.polygon(inner, fill=SAIL)
    draw.line((16, 25, 190, 38), fill=SAIL_LIGHT, width=4)
    draw.line((35, 113, 206, 127), fill=SAIL_DARK, width=4)
    draw.line((109, 33, 117, 123), fill=SAIL_DARK, width=3)
    draw.line((20, 68, 202, 81), fill=SAIL_DARK, width=3)
    # Mast remains visibly planted into the deck beneath the complete sail.
    draw.rectangle((107, 2, 119, 181), fill=WOOD_DARK)
    draw.rectangle((108, 2, 113, 181), fill=WOOD_LIGHT)
    draw.rectangle((95, 178, 132, 189), fill=DARK)
    draw.rectangle((100, 175, 127, 184), fill=WOOD)
    draw.line((100, 176, 127, 176), fill=WOOD_LIGHT, width=2)
    return image


def helm() -> Image.Image:
    """An oblique human-scale wheel viewed from the ship's starboard side."""
    image = Image.new("RGBA", (56, 54), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # The pedestal leans slightly aft. It is broad enough to read as a ship
    # fitting but does not turn the wheel into a front-facing sign.
    draw.polygon([(17, 46), (37, 43), (42, 51), (20, 53)], fill=DARK)
    draw.polygon([(22, 35), (32, 33), (37, 47), (26, 49)],
                 fill=WOOD_DARK)
    draw.polygon([(25, 34), (29, 33), (34, 47), (30, 48)], fill=WOOD)

    # The wheel's transverse plane is strongly foreshortened from the
    # starboard three-quarter viewpoint. A second offset rim supplies depth.
    back_rim = [(31, 2), (41, 8), (40, 23), (34, 40),
                (27, 47), (21, 40), (21, 24), (27, 7)]
    front_rim = [(27, 5), (36, 10), (35, 24), (30, 40),
                 (24, 45), (18, 38), (18, 24), (23, 9)]
    draw.line(back_rim + [back_rim[0]], fill=DARK, width=4)
    draw.line(front_rim + [front_rim[0]], fill=WOOD, width=4)
    for front, back in zip(front_rim[::2], back_rim[::2]):
        draw.line((*front, *back), fill=WOOD_DARK, width=2)

    # Eight spokes and handles retain the iconic helm silhouette, compressed
    # into the same oblique plane rather than facing the camera flush.
    hub = (28, 25)
    for end in front_rim:
        draw.line((*hub, *end), fill=WOOD_LIGHT, width=2)
    for point in front_rim:
        px, py = point
        dx = -1 if px < hub[0] else 1
        dy = -1 if py < hub[1] else 1
        draw.line((px, py, px + dx * 3, py + dy * 3),
                  fill=WOOD_LIGHT, width=2)
    draw.ellipse((23, 20, 33, 30), fill=BRASS)
    draw.ellipse((26, 23, 30, 27), fill=BRASS_LIGHT)
    return image


def bowsprit() -> Image.Image:
    """A massive timber spar projecting east from the actual bow edge."""
    image = Image.new("RGBA", (400, 96), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # The generic prop anchor sits at x=200: art begins there, exactly on the
    # rail tile, then runs more than twelve tiles east across open water.
    draw.polygon([(194, 47), (395, 19), (399, 39), (196, 88)], fill=DARK)
    draw.polygon([(198, 50), (393, 23), (395, 36), (200, 82)], fill=WOOD)
    draw.line((200, 52, 392, 25), fill=WOOD_LIGHT, width=4)
    draw.line((199, 80, 393, 35), fill=WOOD_DARK, width=5)
    # A wide reinforced heel makes the spar read as structural, not a rope.
    draw.rectangle((190, 44, 205, 91), fill=WOOD_DARK)
    draw.rectangle((194, 47, 201, 87), fill=WOOD)
    draw.line((195, 48, 200, 48), fill=WOOD_LIGHT, width=2)
    draw.line((395, 20, 399, 38), fill=BRASS, width=3)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("ship_hammock", hammock()),
        ("ship_round_table", round_table()),
        ("ship_mast_sail", mast_sail()),
        ("ship_helm", helm()),
        ("ship_bowsprit", bowsprit()),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")
    frames = [captain_chest(stage) for stage in range(4)]
    sheet = Image.new("RGBA", (32 * len(frames), 24), TRANSPARENT)
    for index, frame in enumerate(frames):
        sheet.paste(frame, (index * 32, 0))
    path = OUT / "ship_captain_chest.png"
    sheet.save(path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
