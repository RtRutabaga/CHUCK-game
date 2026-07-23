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


def captain_chest(opened: bool) -> Image.Image:
    """A broad brass-bound sea chest, closed or permanently opened."""
    image = Image.new("RGBA", (32, 24), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    if opened:
        draw.rectangle((2, 0, 29, 7), fill=WOOD_DARK)
        draw.rectangle((3, 1, 28, 5), fill=WOOD)
        draw.line((3, 6, 28, 6), fill=WOOD_LIGHT, width=1)
        draw.rectangle((2, 7, 29, 12), fill=DARK)
        # Muted wrapped leaf bundles remain visible in the deep chest.
        for x in (5, 11, 17, 23):
            draw.rectangle((x, 8, x + 4, 11), fill=LEAF)
            draw.line((x + 2, 8, x + 2, 11), fill=ROPE, width=1)
    else:
        draw.rounded_rectangle((1, 3, 30, 11), radius=4, fill=WOOD_DARK)
        draw.rounded_rectangle((2, 3, 29, 9), radius=3, fill=WOOD)
        draw.line((4, 4, 27, 4), fill=WOOD_LIGHT, width=1)
    draw.rectangle((1, 11, 30, 22), fill=WOOD)
    draw.rectangle((1, 19, 30, 22), fill=WOOD_DARK)
    draw.line((2, 12, 29, 12), fill=WOOD_LIGHT, width=1)
    for x in (5, 25):
        draw.rectangle((x, 3 if not opened else 7, x + 2, 22), fill=BRASS)
        draw.line((x + 1, 4 if not opened else 8, x + 1, 21),
                  fill=BRASS_LIGHT, width=1)
    draw.rectangle((14, 11, 18, 16), fill=BRASS)
    draw.rectangle((15, 12, 17, 14), fill=DARK)
    return image


def mast_sail() -> Image.Image:
    """A ship-scale hybrid-top-down mast and broad, fully visible sail."""
    image = Image.new("RGBA", (176, 160), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # The sail is enormous beside Chuck and deliberately overlaps the deck.
    sail = [(8, 16), (154, 26), (168, 114), (24, 103)]
    draw.polygon(sail, fill=DARK)
    inner = [(12, 20), (150, 30), (163, 109), (28, 99)]
    draw.polygon(inner, fill=SAIL)
    draw.line((14, 22, 149, 32), fill=SAIL_LIGHT, width=3)
    draw.line((28, 94, 162, 105), fill=SAIL_DARK, width=3)
    draw.line((86, 27, 92, 103), fill=SAIL_DARK, width=2)
    draw.line((17, 57, 159, 67), fill=SAIL_DARK, width=2)
    # Mast remains visibly planted into the deck beneath the complete sail.
    draw.rectangle((84, 2, 94, 150), fill=WOOD_DARK)
    draw.rectangle((85, 2, 89, 150), fill=WOOD_LIGHT)
    draw.rectangle((75, 147, 103, 157), fill=DARK)
    draw.rectangle((79, 145, 99, 153), fill=WOOD)
    draw.line((79, 146, 99, 146), fill=WOOD_LIGHT, width=2)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("ship_hammock", hammock()),
        ("ship_round_table", round_table()),
        ("ship_mast_sail", mast_sail()),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")
    closed = captain_chest(False)
    opened = captain_chest(True)
    sheet = Image.new("RGBA", (64, 24), TRANSPARENT)
    sheet.paste(closed, (0, 0))
    sheet.paste(opened, (32, 0))
    path = OUT / "ship_captain_chest.png"
    sheet.save(path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
