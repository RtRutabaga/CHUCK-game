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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("ship_hammock", hammock()),
        ("ship_round_table", round_table()),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
