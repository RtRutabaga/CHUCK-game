"""Generate reusable scratchable-overgrowth sprites."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"


def breakable_grass() -> Image.Image:
    image = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    dark = (66, 101, 38, 255)
    mid = (105, 151, 47, 255)
    light = (158, 188, 62, 255)
    shadow = (54, 73, 39, 180)
    draw.ellipse((1, 12, 15, 15), fill=shadow)
    blades = (
        ((2, 14), (1, 6), (4, 10), dark),
        ((5, 14), (4, 2), (7, 8), mid),
        ((7, 14), (8, 5), (9, 10), light),
        ((9, 14), (10, 1), (12, 8), mid),
        ((11, 14), (14, 4), (13, 11), light),
        ((13, 14), (15, 8), (14, 12), dark),
    )
    for base, tip, shoulder, color in blades:
        draw.polygon((base, tip, shoulder), fill=color)
    draw.line((2, 14, 14, 14), fill=dark, width=2)
    return image


def cigarette_carton() -> Image.Image:
    """A full carton of cigarettes — the temple urns' reward.

    12x8: to one-foot Chuck this is a crate of riches. Cream card with
    a warm red band and a row of filter tips showing at the open end.
    """
    image = Image.new("RGBA", (12, 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    card = (226, 220, 202, 255)
    card_shade = (196, 188, 168, 255)
    band = (170, 62, 48, 255)
    tip = (214, 168, 110, 255)
    paper = (240, 238, 230, 255)
    outline = (94, 84, 70, 255)
    draw.rectangle((0, 1, 11, 7), fill=card, outline=outline)
    draw.rectangle((1, 5, 10, 6), fill=card_shade)
    draw.rectangle((1, 2, 10, 3), fill=band)
    # The open flap end: three cigarette tips peeking out on top.
    for x in (2, 5, 8):
        draw.rectangle((x, 0, x + 1, 0), fill=paper)
        draw.point((x + 1, 0), fill=tip)
    return image


def golden_cigarette_carton() -> Image.Image:
    """The captain's conspicuous forty-cigarette carton."""
    image = Image.new("RGBA", (12, 8), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    gold_dark = (126, 82, 19, 255)
    gold = (221, 170, 43, 255)
    gold_light = (255, 222, 101, 255)
    band = (118, 45, 38, 255)
    paper = (248, 239, 196, 255)
    draw.rectangle((0, 1, 11, 7), fill=gold, outline=gold_dark)
    draw.line((1, 2, 10, 2), fill=gold_light, width=1)
    draw.rectangle((1, 4, 10, 5), fill=band)
    draw.line((1, 6, 10, 6), fill=gold_dark, width=1)
    for x in (2, 5, 8):
        draw.point((x, 0), fill=paper)
        draw.point((x + 1, 0), fill=gold_light)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("breakable_grass", breakable_grass()),
        ("cigarette_carton", cigarette_carton()),
        ("golden_cigarette_carton", golden_cigarette_carton()),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
