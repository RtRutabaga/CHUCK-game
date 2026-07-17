"""Generate reusable human-scale stone arches for temple thresholds."""

from pathlib import Path

from PIL import Image, ImageDraw


TRANSPARENT = (0, 0, 0, 0)
VOID = (7, 13, 14, 255)
STONE_DARK = (27, 38, 37, 255)
STONE = (52, 64, 55, 255)
STONE_LIGHT = (87, 91, 68, 255)
MOSS = (36, 76, 44, 255)


def _blocks(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    """Add restrained masonry seams to a filled arch section."""
    x0, y0, x1, y1 = box
    for y in range(y0 + 7, y1, 7):
        draw.line((x0, y, x1, y), fill=STONE_DARK)
    for index, y in enumerate(range(y0, y1, 7)):
        seam = x0 + 5 + (index % 2) * 6
        if seam < x1:
            draw.line((seam, y, seam, min(y + 6, y1)), fill=STONE_DARK)


def north_south_arch() -> Image.Image:
    """A 48x38 frontal arch: roughly human NPC height, enormous to Chuck."""
    image = Image.new("RGBA", (48, 38), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Deep opening first, then stepped voussoirs and broad jambs.
    draw.rectangle((13, 11, 34, 37), fill=VOID)
    draw.rectangle((5, 15, 12, 37), fill=STONE)
    draw.rectangle((35, 15, 42, 37), fill=STONE)
    draw.rectangle((9, 8, 38, 15), fill=STONE)
    draw.rectangle((13, 4, 34, 9), fill=STONE)
    draw.rectangle((17, 1, 30, 5), fill=STONE)
    _blocks(draw, (5, 15, 12, 37))
    _blocks(draw, (35, 15, 42, 37))
    draw.line((9, 15, 13, 10, 17, 6, 30, 6, 34, 10, 38, 15),
              fill=STONE_LIGHT, width=2)
    draw.line((12, 37, 35, 37), fill=STONE_DARK, width=2)
    draw.line((7, 18, 11, 18), fill=MOSS, width=2)
    draw.line((38, 11, 40, 23), fill=MOSS)
    return image


def east_west_arch() -> Image.Image:
    """A side-wall arch with the same human-scale dark opening."""
    image = Image.new("RGBA", (38, 48), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 13, 37, 34), fill=VOID)
    draw.rectangle((10, 5, 37, 12), fill=STONE)
    draw.rectangle((10, 35, 37, 42), fill=STONE)
    draw.rectangle((5, 9, 12, 38), fill=STONE)
    draw.rectangle((1, 13, 6, 34), fill=STONE)
    _blocks(draw, (10, 5, 37, 12))
    _blocks(draw, (10, 35, 37, 42))
    draw.line((12, 9, 7, 13, 7, 34, 12, 38),
              fill=STONE_LIGHT, width=2)
    draw.line((37, 12, 37, 35), fill=STONE_DARK, width=2)
    draw.line((15, 7, 27, 7), fill=MOSS, width=2)
    draw.line((8, 30, 8, 37), fill=MOSS)
    return image


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "objects"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("temple_arch_ns", north_south_arch()),
        ("temple_arch_ew", east_west_arch()),
    ):
        out = out_dir / f"{name}.png"
        image.save(out)
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
