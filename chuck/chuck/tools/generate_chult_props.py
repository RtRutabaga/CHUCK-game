"""Generate oversized abandoned expedition props for Chult."""

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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("expedition_backpack", backpack()),
        ("abandoned_boot", boot()),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
