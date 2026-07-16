"""Generate the reference-informed massive Chult dinosaur sprite sheet."""

from pathlib import Path

from PIL import Image, ImageDraw


FRAME_W, FRAME_H = 72, 60


def dinosaur_frame(facing: str, step: int) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    shadow = (15, 29, 23, 180)
    dark = (31, 70, 42, 255)
    body = (47, 103, 55, 255)
    light = (62, 119, 62, 255)
    belly = (116, 119, 70, 255)
    plate = (135, 143, 78, 255)
    claw = (207, 190, 124, 255)
    eye = (255, 185, 36, 255)

    draw.ellipse((8, 54, 66, 59), fill=shadow)

    if facing == "left":
        # Long tail, huge haunches, blunt head, tiny forearms.
        draw.polygon(((29, 26), (3, 35), (0, 31), (24, 18), (41, 18)),
                     fill=dark)
        draw.ellipse((20, 16, 51, 45), fill=body)
        draw.polygon(((42, 13), (50, 5), (69, 7), (71, 24),
                      (62, 31), (46, 29)), fill=body)
        draw.rectangle((55, 25, 69, 31), fill=light)
        draw.rectangle((61, 12, 64, 15), fill=eye)
        for x, y in ((25, 14), (31, 10), (38, 8), (45, 6)):
            draw.polygon(((x, y + 8), (x + 4, y), (x + 8, y + 8)), fill=plate)
        draw.ellipse((29, 28, 49, 47), fill=belly)
        draw.line((48, 29, 54, 36), fill=belly, width=3)
        draw.line((54, 36, 58, 34), fill=claw, width=2)
        left_x, right_x = (24 + step * 3, 43 - step * 3)
        draw.polygon(((25, 39), (left_x, 55), (left_x + 12, 55), (38, 40)),
                     fill=dark)
        draw.polygon(((39, 39), (right_x, 55), (right_x + 13, 55), (50, 38)),
                     fill=body)
        draw.rectangle((left_x, 53, left_x + 13, 57), fill=belly)
        draw.rectangle((right_x, 53, right_x + 14, 57), fill=belly)
        for x in (left_x, left_x + 6, right_x + 2, right_x + 9):
            draw.rectangle((x, 56, x + 3, 58), fill=claw)
        return image

    # Front/back views retain the supplied broad head, dorsal plates, belly,
    # tiny hands, heavy legs, and square pale claws.
    draw.polygon(((18, 30), (3, 38), (0, 34), (20, 21), (50, 21), (68, 34),
                  (62, 39), (49, 31)), fill=dark)
    draw.ellipse((16, 15, 55, 48), fill=body)
    head_top = 5 if facing == "up" else 7
    draw.polygon(((24, 19), (27, head_top), (57, head_top), (68, 17),
                  (68, 30), (55, 34), (31, 31)), fill=body)
    draw.rectangle((46, 16, 67, 30), fill=light)
    for x, y in ((17, 19), (21, 13), (27, 8), (35, 5), (44, 4)):
        draw.polygon(((x, y + 9), (x + 4, y), (x + 9, y + 9)), fill=plate)
    if facing == "down":
        draw.rectangle((34, 14, 37, 18), fill=eye)
        draw.rectangle((56, 14, 59, 18), fill=eye)
    draw.ellipse((26, 29, 49, 48), fill=belly)
    draw.line((25, 30, 18, 38), fill=belly, width=3)
    draw.line((51, 30, 57, 38), fill=belly, width=3)
    draw.line((18, 38, 14, 36), fill=claw, width=2)
    draw.line((57, 38, 61, 36), fill=claw, width=2)
    left_x, right_x = (17 + step * 3, 43 - step * 3)
    draw.polygon(((22, 40), (left_x, 55), (left_x + 15, 55), (35, 42)),
                 fill=dark)
    draw.polygon(((40, 41), (right_x, 55), (right_x + 15, 55), (52, 39)),
                 fill=body)
    draw.rectangle((left_x, 53, left_x + 15, 57), fill=belly)
    draw.rectangle((right_x, 53, right_x + 15, 57), fill=belly)
    for x in (left_x, left_x + 7, right_x + 2, right_x + 9):
        draw.rectangle((x, 56, x + 3, 59), fill=claw)
    return image


def main() -> None:
    out = (Path(__file__).resolve().parents[1] /
           "assets" / "sprites" / "hazards" / "massive_dinosaur.png")
    sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H * 2), (0, 0, 0, 0))
    for row, step in enumerate((0, 1)):
        for col, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(
                dinosaur_frame(facing, step), (col * FRAME_W, row * FRAME_H)
            )
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
