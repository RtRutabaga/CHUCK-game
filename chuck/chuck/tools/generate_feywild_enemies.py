"""Generate native-scale Feywild enemy and hazard sprites."""

from pathlib import Path

from PIL import Image, ImageDraw


OUT = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "hazards"
CLEAR = (0, 0, 0, 0)
W, H = 20, 24

STEM_DARK = (38, 78, 60, 255)
STEM = (55, 128, 79, 255)
LEAF = (77, 157, 88, 255)
PETAL_DARK = (99, 49, 125, 255)
PETAL = (184, 85, 184, 255)
PETAL_BRIGHT = (236, 142, 224, 255)
BULB = (223, 181, 96, 255)
CORE = (88, 42, 95, 255)


def orchid_frame(facing: str, stage: int) -> Image.Image:
    """A directional orchid: closed, swelling, then open to spit."""
    image = Image.new("RGBA", (W, H), CLEAR)
    draw = ImageDraw.Draw(image)
    # Rooted base and broad leaves.
    draw.ellipse((4, 19, 16, 23), fill=STEM_DARK)
    draw.polygon(((9, 20), (1, 16), (7, 14), (10, 19)), fill=LEAF)
    draw.polygon(((11, 20), (19, 16), (13, 14), (10, 19)), fill=LEAF)
    draw.rectangle((9, 10, 11, 20), fill=STEM)

    if facing == "down":
        center = (10, 11)
        mouth = (10, 14)
    elif facing == "up":
        center = (10, 8)
        mouth = (10, 5)
    else:
        center = (8, 10)
        mouth = (5, 10)

    cx, cy = center
    spread = 3 + stage
    petal_color = PETAL_BRIGHT if stage == 2 else PETAL
    draw.ellipse(
        (cx - spread, cy - 3, cx + spread, cy + 3), fill=PETAL_DARK
    )
    draw.polygon(
        (
            (cx, cy - 1 - spread),
            (cx + 3, cy - 1),
            (cx, cy + 1),
            (cx - 3, cy - 1),
        ),
        fill=petal_color,
    )
    draw.polygon(
        (
            (cx - spread, cy),
            (cx, cy - 2),
            (cx + spread, cy),
            (cx, cy + 2),
        ),
        fill=petal_color,
    )
    bulb_radius = 1 + (1 if stage else 0)
    draw.ellipse(
        (
            cx - bulb_radius, cy - bulb_radius,
            cx + bulb_radius, cy + bulb_radius,
        ),
        fill=(PETAL_BRIGHT if stage == 2 else BULB),
    )
    if stage == 2:
        mx, my = mouth
        draw.rectangle((mx - 1, my - 1, mx + 1, my + 1), fill=CORE)
        draw.point((mx, my), fill=(247, 226, 164, 255))
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (W * 3, H * 3), CLEAR)
    for stage in range(3):
        for col, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(
                orchid_frame(facing, stage), (col * W, stage * H)
            )
    path = OUT / "spitting_orchid.png"
    sheet.save(path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
