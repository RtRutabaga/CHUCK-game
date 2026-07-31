"""Generate the two-frame, three-facing Feywild redcap sprite sheet."""

from pathlib import Path

from PIL import Image, ImageDraw


FRAME_W, FRAME_H = 20, 24


def redcap_frame(facing: str, step: int) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = (17, 28, 27, 150)
    cap_dark = (80, 17, 30, 255)
    cap = (174, 35, 48, 255)
    skin = (137, 105, 70, 255)
    coat = (53, 67, 48, 255)
    boot = (42, 24, 20, 255)
    iron = (151, 154, 139, 255)
    eye = (235, 202, 77, 255)

    draw.ellipse((3, 20, 17, 23), fill=shadow)
    if facing == "left":
        draw.rectangle((7, 9, 14, 18), fill=coat)
        draw.rectangle((5, 5, 13, 11), fill=skin)
        draw.polygon(((3, 5), (15, 3), (13, 7), (5, 8)), fill=cap)
        draw.line((4, 5, 14, 4), fill=cap_dark, width=2)
        draw.point((6, 8), fill=eye)
        draw.line((12, 11, 17, 17), fill=iron, width=2)
        draw.line((17, 16, 15, 20), fill=iron, width=2)
        feet = (5 + step, 12 - step)
    else:
        draw.rectangle((6, 9, 14, 18), fill=coat)
        draw.rectangle((6, 5, 14, 11), fill=skin)
        draw.polygon(((3, 5), (10, 1), (17, 5), (14, 8), (5, 8)),
                     fill=cap)
        draw.line((4, 5, 16, 5), fill=cap_dark, width=2)
        if facing == "down":
            draw.point((8, 8), fill=eye)
            draw.point((12, 8), fill=eye)
        draw.line((14, 11, 18, 17), fill=iron, width=2)
        draw.line((18, 17, 15, 20), fill=iron, width=2)
        feet = (5 + step, 13 - step)
    draw.rectangle((feet[0], 17, feet[0] + 4, 22), fill=boot)
    draw.rectangle((feet[1], 17, feet[1] + 4, 22), fill=boot)
    draw.rectangle((feet[0] - 1, 21, feet[0] + 4, 23), fill=boot)
    draw.rectangle((feet[1] - 1, 21, feet[1] + 4, 23), fill=boot)
    return image


def main() -> None:
    out = (
        Path(__file__).resolve().parents[1]
        / "assets" / "sprites" / "hazards" / "redcap.png"
    )
    sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H * 2), (0, 0, 0, 0))
    for row, step in enumerate((0, 1)):
        for col, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(
                redcap_frame(facing, step), (col * FRAME_W, row * FRAME_H)
            )
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
