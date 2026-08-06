"""Generate the Aerie griffon in the shared massive-hazard sheet layout."""

from pathlib import Path

from PIL import Image, ImageDraw


FRAME_W, FRAME_H = 72, 60
CLEAR = (0, 0, 0, 0)
SHADOW = (51, 50, 66, 150)
FEATHER_DARK = (92, 72, 53, 255)
FEATHER = (188, 151, 91, 255)
FEATHER_LIGHT = (232, 207, 145, 255)
LION = (172, 112, 55, 255)
LION_LIGHT = (218, 157, 80, 255)
BEAK = (231, 178, 61, 255)
TALON = (102, 76, 48, 255)
EYE = (244, 231, 105, 255)


def _wing(draw, root_x, root_y, side, lifted):
    reach = 27 if lifted else 23
    tip_y = root_y - (19 if lifted else 12)
    points = [
        (root_x, root_y + 10),
        (root_x + side * reach, tip_y),
        (root_x + side * 22, tip_y + 12),
        (root_x + side * 29, tip_y + 17),
        (root_x + side * 18, root_y + 15),
    ]
    draw.polygon(points, fill=FEATHER_DARK)
    for index in range(4):
        x = root_x + side * (10 + index * 4)
        draw.line((root_x + side * 3, root_y + 5 + index,
                   x, tip_y + 7 + index * 4), fill=FEATHER_LIGHT, width=2)


def frame(facing: str, step: int) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), CLEAR)
    draw = ImageDraw.Draw(image)
    cx = FRAME_W // 2
    lift = -1 if step else 0
    ground = 55
    draw.ellipse((7, 49, 65, 59), fill=SHADOW)

    if facing == "left":
        _wing(draw, cx + 5, 26 + lift, 1, bool(step))
        draw.ellipse((29, 25 + lift, 62, 49 + lift), fill=LION)
        draw.rectangle((20, 25 + lift, 47, 43 + lift), fill=FEATHER)
        draw.ellipse((8, 19 + lift, 29, 37 + lift), fill=FEATHER_LIGHT)
        draw.polygon(((8, 27 + lift), (0, 31 + lift), (9, 34 + lift)),
                     fill=BEAK)
        draw.polygon(((14, 20 + lift), (17, 12 + lift), (21, 22 + lift)),
                     fill=FEATHER_DARK)
        draw.rectangle((13, 25 + lift, 16, 28 + lift), fill=EYE)
        draw.line((58, 30 + lift, 69, 21 + lift, 65, 12 + lift),
                  fill=LION, width=4)
        for x in (25, 43, 55):
            drop = 7 + ((x + step) % 2) * 2
            draw.rectangle((x - 3, 42 + lift, x + 3, 42 + lift + drop),
                           fill=LION_LIGHT if x > 30 else FEATHER)
            draw.line((x - 4, 42 + lift + drop, x + 4, 42 + lift + drop),
                      fill=TALON, width=2)
    elif facing == "down":
        # Broad frontal silhouette: eagle head and chest sit distinctly over
        # a tawny lion body, with both wings readable instead of a round blob.
        _wing(draw, cx - 7, 27 + lift, -1, bool(step))
        _wing(draw, cx + 7, 27 + lift, 1, bool(step))
        draw.ellipse((19, 24 + lift, 53, 50 + lift), fill=LION)
        draw.ellipse((24, 17 + lift, 48, 43 + lift), fill=FEATHER)
        draw.polygon(((23, 31 + lift), (13, 41 + lift), (27, 39 + lift)),
                     fill=FEATHER_LIGHT)
        draw.polygon(((49, 31 + lift), (59, 41 + lift), (45, 39 + lift)),
                     fill=FEATHER_LIGHT)
        draw.ellipse((25, 7 + lift, 47, 28 + lift), fill=FEATHER_LIGHT)
        draw.polygon(((27, 11 + lift), (30, 2 + lift), (34, 12 + lift)),
                     fill=FEATHER_DARK)
        draw.polygon(((38, 11 + lift), (42, 2 + lift), (45, 13 + lift)),
                     fill=FEATHER_DARK)
        for x in (30, 41):
            draw.rectangle((x, 15 + lift, x + 2, 18 + lift), fill=EYE)
        draw.polygon(((30, 21 + lift), (42, 21 + lift), (36, 31 + lift)),
                     fill=BEAK)
        for x in (24, 48):
            drop = 7 + ((x + step) % 2) * 2
            draw.rectangle((x - 3, 43 + lift, x + 3, 43 + lift + drop),
                           fill=LION_LIGHT)
            draw.line((x - 5, 43 + lift + drop, x + 5, 43 + lift + drop),
                      fill=TALON, width=2)
    else:
        _wing(draw, cx - 5, 27 + lift, -1, bool(step))
        _wing(draw, cx + 5, 27 + lift, 1, bool(step))
        draw.ellipse((21, 22 + lift, 51, 49 + lift), fill=LION)
        draw.ellipse((25, 19 + lift, 47, 43 + lift), fill=FEATHER)
        head_y = 13 + lift
        draw.ellipse((26, head_y, 46, head_y + 17), fill=FEATHER_LIGHT)
        draw.polygon(((31, head_y + 1), (34, head_y - 7),
                      (37, head_y + 2)), fill=FEATHER_DARK)
        draw.polygon(((39, head_y + 1), (42, head_y - 7),
                      (45, head_y + 2)), fill=FEATHER_DARK)
        for x in (25, 47):
            drop = 7 + ((x + step) % 2) * 2
            draw.rectangle((x - 3, 44 + lift, x + 3, 44 + lift + drop),
                           fill=LION_LIGHT)
            draw.line((x - 4, 44 + lift + drop, x + 4, 44 + lift + drop),
                      fill=TALON, width=2)
    return image


def main() -> None:
    out = (Path(__file__).resolve().parents[1] /
           "assets" / "sprites" / "hazards" / "griffon.png")
    sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H * 2), CLEAR)
    for row, step in enumerate((0, 1)):
        for col, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(frame(facing, step),
                                  (col * FRAME_W, row * FRAME_H))
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
