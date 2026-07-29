"""Generate the Phlegethos horned devil sprite sheet (Phase 8).

A horned devil reuses the Chult massive-dinosaur gameplay wholesale, so
this sheet matches that layout exactly: 72x60 frames, two step rows by
three facings (down, up, left). Where the dinosaur is a towering animal,
this is a towering *soldier* -- slab-muscled, batwinged, horned, dragging
a barbed iron fork -- so the scale threat reads as infernal, not Jurassic.
"""

from pathlib import Path

from PIL import Image, ImageDraw

FRAME_W, FRAME_H = 72, 60
CLEAR = (0, 0, 0, 0)

SHADOW = (18, 10, 12, 170)
HIDE_DARK = (96, 26, 26, 255)
HIDE = (146, 42, 36, 255)
HIDE_LIGHT = (182, 66, 46, 255)
BELLY = (108, 52, 44, 255)
HORN = (226, 208, 178, 255)
HORN_DARK = (158, 142, 116, 255)
WING = (72, 22, 26, 255)
WING_EDGE = (52, 16, 20, 255)
IRON = (118, 118, 126, 255)
IRON_LIGHT = (170, 172, 178, 255)
EYE = (255, 206, 84, 255)
EMBER = (248, 132, 36, 255)


def devil_frame(facing: str, step: int) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), CLEAR)
    draw = ImageDraw.Draw(image)
    cx = FRAME_W // 2
    lift = -1 if step else 0          # a heavy, rocking stride
    ground = FRAME_H - 4

    # The shadow it throws: this thing is enormous beside a one-foot rat.
    draw.ellipse((cx - 24, ground - 6, cx + 24, ground + 3), fill=SHADOW)

    # Wings spread wide behind the torso.
    span = 30 + (1 if step else 0)
    for side in (-1, 1):
        tip_x = cx + side * span
        draw.polygon(((cx + side * 8, 18 + lift), (tip_x, 8 + lift),
                      (tip_x - side * 4, 34 + lift),
                      (cx + side * 9, 32 + lift)), fill=WING)
        draw.line((cx + side * 8, 18 + lift, tip_x, 8 + lift),
                  fill=WING_EDGE, width=2)
        for rib in (1, 2):
            draw.line((cx + side * 9, 24 + lift,
                       tip_x - side * rib * 6, 14 + lift + rib * 6),
                      fill=WING_EDGE)

    # Legs: a wide, planted stride that alternates with the step.
    front, back = (6, -6) if step else (-6, 6)
    for dx in (front, back):
        draw.rectangle((cx + dx - 5, 38 + lift, cx + dx + 4, ground - 2),
                       fill=HIDE_DARK)
        draw.rectangle((cx + dx - 6, ground - 3, cx + dx + 5, ground),
                       fill=HORN_DARK)   # cloven hooves

    # Slab torso and gut.
    draw.rectangle((cx - 13, 18 + lift, cx + 13, 40 + lift), fill=HIDE)
    draw.rectangle((cx - 9, 28 + lift, cx + 9, 39 + lift), fill=BELLY)
    draw.line((cx - 13, 22 + lift, cx + 13, 22 + lift), fill=HIDE_LIGHT)

    # Head, sunk between the shoulders, crowned with sweeping horns.
    draw.rectangle((cx - 8, 6 + lift, cx + 8, 19 + lift), fill=HIDE)
    draw.rectangle((cx - 6, 8 + lift, cx + 6, 17 + lift), fill=HIDE_LIGHT)
    for side in (-1, 1):
        draw.line((cx + side * 7, 8 + lift, cx + side * 15, 0 + lift),
                  fill=HORN, width=3)
        draw.line((cx + side * 14, 1 + lift, cx + side * 16, 5 + lift),
                  fill=HORN_DARK, width=2)
    if facing == "down":
        draw.rectangle((cx - 5, 11 + lift, cx - 3, 13 + lift), fill=EYE)
        draw.rectangle((cx + 3, 11 + lift, cx + 5, 13 + lift), fill=EYE)
        # A fanged grin.
        draw.rectangle((cx - 4, 16 + lift, cx + 4, 17 + lift), fill=HORN)
    elif facing == "left":
        draw.rectangle((cx - 6, 11 + lift, cx - 4, 13 + lift), fill=EYE)
        draw.rectangle((cx - 8, 15 + lift, cx - 3, 17 + lift), fill=HORN)
    else:
        # From behind: the skull and horn bases only, no face.
        draw.rectangle((cx - 6, 8 + lift, cx + 6, 17 + lift), fill=HIDE_DARK)

    # The barbed iron fork, carried in the near hand.
    if facing == "left":
        shaft_x = cx - 18
    else:
        shaft_x = cx + 18
    draw.rectangle((shaft_x - 1, 12 + lift, shaft_x + 1, ground - 6),
                   fill=IRON)
    draw.line((shaft_x, 12 + lift, shaft_x, ground - 6), fill=IRON_LIGHT)
    for tine in (-4, 0, 4):
        draw.line((shaft_x + tine, 12 + lift, shaft_x + tine, 3 + lift),
                  fill=IRON_LIGHT, width=2)
    draw.line((shaft_x - 4, 12 + lift, shaft_x + 4, 12 + lift),
              fill=IRON, width=2)

    # A whipping tail with a burning barb.
    tail_x = cx + (14 if facing != "left" else -14)
    sweep = 4 if step else -4
    draw.line((cx, 36 + lift, tail_x, 42 + lift,
               tail_x + sweep, ground - 4), fill=HIDE_DARK, width=3)
    draw.rectangle((tail_x + sweep - 1, ground - 6,
                    tail_x + sweep + 1, ground - 4), fill=EMBER)
    return image


def main() -> None:
    out = (Path(__file__).resolve().parents[1] /
           "assets" / "sprites" / "hazards" / "horned_devil.png")
    sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H * 2), CLEAR)
    for row, step in enumerate((0, 1)):
        for col, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(devil_frame(facing, step),
                                  (col * FRAME_W, row * FRAME_H))
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
