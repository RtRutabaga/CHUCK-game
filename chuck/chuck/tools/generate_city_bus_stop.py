"""Generate the human-scale modern bus shelter displaced into Phlegethos."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects" / "city_bus_stop.png"
W, H = 72, 64


def _pixel_letter(draw: ImageDraw.ImageDraw, x: int, y: int,
                  rows: tuple[str, ...], colour) -> None:
    for row, pattern in enumerate(rows):
        for col, bit in enumerate(pattern):
            if bit == "1":
                draw.rectangle((x + col * 2, y + row * 2,
                                x + col * 2 + 1, y + row * 2 + 1),
                               fill=colour)


def main() -> None:
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    outline = (20, 23, 29, 255)
    metal = (72, 82, 92, 255)
    metal_lit = (111, 124, 132, 255)
    glass = (84, 119, 135, 92)
    glass_glint = (151, 188, 198, 126)
    bench = (54, 58, 62, 255)

    draw.ellipse((5, 58, 67, 63), fill=(12, 9, 12, 150))
    # Roof and two rear posts establish the scale before the transparent wall.
    draw.rectangle((4, 8, 68, 13), fill=outline)
    draw.rectangle((7, 9, 65, 11), fill=metal_lit)
    draw.rectangle((7, 12, 11, 60), fill=outline)
    draw.rectangle((9, 14, 10, 58), fill=metal)
    draw.rectangle((61, 12, 65, 60), fill=outline)
    draw.rectangle((62, 14, 63, 58), fill=metal)
    draw.rectangle((12, 14, 60, 55), fill=glass)
    draw.line((35, 14, 35, 55), fill=(35, 44, 52, 180), width=2)
    for x, y in ((17, 20), (45, 17), (25, 34), (51, 39)):
        draw.line((x, y, x + 5, y - 5), fill=glass_glint, width=1)

    # A broad bench reads at once as furniture built for somebody enormous.
    draw.rectangle((15, 43, 56, 48), fill=outline)
    draw.rectangle((17, 43, 54, 45), fill=bench)
    draw.rectangle((18, 48, 21, 59), fill=outline)
    draw.rectangle((50, 48, 53, 59), fill=outline)

    # Pixel BUS sign: legible at native resolution without importing a font.
    draw.rectangle((22, 0, 50, 12), fill=outline)
    draw.rectangle((24, 2, 48, 10), fill=(210, 216, 205, 255))
    ink = (37, 48, 58, 255)
    _pixel_letter(draw, 26, 2, ("110", "101", "110", "101", "110"), ink)
    _pixel_letter(draw, 34, 2, ("101", "101", "101", "101", "111"), ink)
    _pixel_letter(draw, 42, 2, ("111", "100", "111", "001", "111"), ink)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUT)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
