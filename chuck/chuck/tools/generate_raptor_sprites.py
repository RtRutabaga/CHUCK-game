"""Generate the two-frame, three-facing Chult raptor sprite sheet."""

from pathlib import Path

from PIL import Image, ImageDraw


BASE_W, BASE_H = 36, 24
FRAME_W, FRAME_H = 44, 30


def raptor_frame(facing: str, step: int) -> Image.Image:
    image = Image.new("RGBA", (BASE_W, BASE_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = (18, 31, 24, 170)
    body_dark = (37, 67, 43, 255)
    body = (57, 105, 57, 255)
    body_light = (91, 132, 66, 255)
    belly = (126, 128, 75, 255)
    claw = (190, 174, 116, 255)
    eye = (229, 176, 55, 255)

    if facing == "left":
        draw.ellipse((4, 20, 33, 23), fill=shadow)
        draw.polygon(((7, 12), (0, 7), (4, 14), (13, 18)), fill=body_dark)
        draw.ellipse((9, 7, 27, 18), fill=body)
        draw.polygon(((23, 10), (28, 3), (35, 4), (34, 12), (26, 15)),
                     fill=body)
        draw.line((29, 5, 35, 6), fill=body_light, width=2)
        draw.point((32, 5), fill=eye)
        draw.line((14, 16, 11 - step * 2, 22), fill=belly, width=3)
        draw.line((22, 16, 25 + step * 2, 22), fill=belly, width=3)
        draw.line((11 - step * 2, 22, 7 - step * 2, 22), fill=claw, width=1)
        draw.line((25 + step * 2, 22, 29 + step * 2, 22), fill=claw, width=1)
        draw.line((14, 9, 18, 5), fill=body_light, width=2)
        return image.resize((FRAME_W, FRAME_H), Image.Resampling.NEAREST)

    draw.ellipse((4, 20, 32, 23), fill=shadow)
    draw.polygon(((8, 15), (2, 11), (9, 8), (27, 8), (34, 11), (28, 15)),
                 fill=body_dark)
    draw.ellipse((9, 6, 27, 18), fill=body)
    head_y = 2 if facing == "up" else 3
    draw.polygon(((12, 9), (13, head_y), (23, head_y), (24, 9)), fill=body)
    draw.line((14, head_y + 1, 22, head_y + 1), fill=body_light, width=2)
    if facing == "down":
        draw.point((15, head_y + 3), fill=eye)
        draw.point((21, head_y + 3), fill=eye)
        draw.line((15, 10, 21, 10), fill=belly, width=2)
    left_foot = 10 + step * 2
    right_foot = 26 - step * 2
    draw.line((14, 16, left_foot, 22), fill=belly, width=3)
    draw.line((22, 16, right_foot, 22), fill=belly, width=3)
    draw.line((left_foot, 22, left_foot - 4, 22), fill=claw, width=1)
    draw.line((right_foot, 22, right_foot + 4, 22), fill=claw, width=1)
    return image.resize((FRAME_W, FRAME_H), Image.Resampling.NEAREST)


def main() -> None:
    out = (Path(__file__).resolve().parents[1] /
           "assets" / "sprites" / "hazards" / "raptor.png")
    sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H * 2), (0, 0, 0, 0))
    for row, step in enumerate((0, 1)):
        for col, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(
                raptor_frame(facing, step), (col * FRAME_W, row * FRAME_H)
            )
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
