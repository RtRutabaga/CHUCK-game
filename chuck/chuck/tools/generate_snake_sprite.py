"""Generate the compact three-facing temple snake sprite sheet."""

from pathlib import Path

from PIL import Image, ImageDraw


FRAME_W, FRAME_H = 18, 10


def snake_frame(facing: str) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    outline = (29, 37, 25, 255)
    body = (76, 117, 50, 255)
    light = (126, 153, 65, 255)
    eye = (229, 181, 61, 255)
    tongue = (179, 58, 59, 255)

    if facing in {"down", "up"}:
        # A tight S coil reads clearly when approached vertically.
        draw.line((4, 2, 12, 2, 14, 4, 6, 5, 4, 7, 12, 7),
                  fill=outline, width=3)
        draw.line((4, 2, 12, 2, 14, 4, 6, 5, 4, 7, 12, 7),
                  fill=body, width=1)
        head_y = 7 if facing == "down" else 2
        draw.rectangle((11, head_y - 1, 15, head_y + 1), fill=outline)
        draw.rectangle((12, head_y, 15, head_y), fill=light)
        draw.point((14, head_y), fill=eye)
        tongue_y = head_y + (2 if facing == "down" else -2)
        draw.point((15, tongue_y), fill=tongue)
    else:
        # The side silhouette keeps a blunt head and a curled tail.
        draw.line((2, 7, 4, 4, 7, 7, 10, 4, 13, 6),
                  fill=outline, width=3)
        draw.line((2, 7, 4, 4, 7, 7, 10, 4, 13, 6),
                  fill=body, width=1)
        draw.rectangle((12, 4, 16, 7), fill=outline)
        draw.rectangle((13, 5, 16, 6), fill=light)
        draw.point((15, 5), fill=eye)
        draw.point((17, 6), fill=tongue)
    return image


def main() -> None:
    out = (
        Path(__file__).resolve().parents[1]
        / "assets" / "sprites" / "hazards" / "snake.png"
    )
    sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H), (0, 0, 0, 0))
    for index, facing in enumerate(("down", "up", "left")):
        sheet.alpha_composite(snake_frame(facing), (index * FRAME_W, 0))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
