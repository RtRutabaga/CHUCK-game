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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "breakable_grass.png"
    breakable_grass().save(path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
