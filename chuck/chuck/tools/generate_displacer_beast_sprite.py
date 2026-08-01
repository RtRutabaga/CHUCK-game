"""Generate the Feywild displacer beast sprite sheet (Phase 9).

The beast reuses the massive-dinosaur gameplay wholesale, so this sheet
matches that layout exactly: 72x60 frames, two step rows by three facings
(down, up, left). It is drawn in the dinosaur's idiom too -- chunky
masses, a pale belly, pale planted paws -- because that is what reads at
native scale. Where the dinosaur is a towering animal and the horned
devil a towering soldier, this is a towering *predator*: a six-legged
blue-black panther whose two barbed tentacles rise over its shoulders.
"""

from pathlib import Path

from PIL import Image, ImageDraw

FRAME_W, FRAME_H = 72, 60
CLEAR = (0, 0, 0, 0)

SHADOW = (10, 18, 26, 170)
FUR_DARK = (18, 22, 42, 255)     # far legs and the shaded mass
FUR = (40, 48, 82, 255)
FUR_LIGHT = (68, 82, 124, 255)
BELLY = (92, 104, 142, 255)
PAW = (206, 202, 186, 255)
TENTACLE = (30, 26, 56, 255)
TENTACLE_LIT = (62, 56, 100, 255)
BARB = (198, 206, 232, 255)
EYE = (138, 252, 186, 255)
MAW = (172, 54, 78, 255)
GHOST = (98, 122, 198, 80)       # the after-image its name promises


def _leg(draw, x, top, step, *, near):
    """One thick planted leg. Far legs sit darker and a little higher."""
    body = FUR if near else FUR_DARK
    drop = 10 if step == near else 8
    width = 4 if near else 3
    draw.rectangle((x - width, top, x + width, top + drop), fill=body)
    draw.rectangle((x - width - 1, top + drop, x + width + 1, top + drop + 3),
                   fill=PAW if near else (150, 148, 136, 255))


def _tentacle(draw, base, tip, step):
    """A thick barbed tentacle: chunky enough to read at native scale."""
    sway = 3 if step else -3
    mid = ((base[0] + tip[0]) // 2 - sway, (base[1] + tip[1]) // 2 - 4)
    draw.line((*base, *mid), fill=TENTACLE, width=7)
    draw.line((*mid, tip[0] + sway, tip[1]), fill=TENTACLE, width=6)
    draw.line((base[0], base[1] - 2, mid[0], mid[1] - 2), fill=TENTACLE_LIT,
              width=2)
    pad_x, pad_y = tip[0] + sway, tip[1]
    draw.ellipse((pad_x - 7, pad_y - 6, pad_x + 7, pad_y + 6), fill=TENTACLE)
    draw.ellipse((pad_x - 5, pad_y - 5, pad_x + 1, pad_y - 1),
                 fill=TENTACLE_LIT)
    for barb in (-6, -1, 4):
        draw.polygon(((pad_x + barb, pad_y - 5), (pad_x + barb + 2, pad_y - 9),
                      (pad_x + barb + 3, pad_y - 4)), fill=BARB)


def beast_frame(facing: str, step: int) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), CLEAR)
    draw = ImageDraw.Draw(image)
    cx = FRAME_W // 2
    lift = -1 if step else 0
    ground = FRAME_H - 4

    draw.ellipse((cx - 27, ground - 7, cx + 27, ground + 2), fill=SHADOW)

    if facing == "left":
        top = 22 + lift
        # Far legs first, so the near ones overlap them.
        for x in (cx - 12, cx + 2, cx + 16):
            _leg(draw, x, top + 20, step, near=False)
        draw.ellipse((cx + 2, top, cx + 30, top + 26), fill=FUR)      # haunch
        draw.rectangle((cx - 22, top + 2, cx + 16, top + 24), fill=FUR)
        draw.ellipse((cx - 26, top + 1, cx - 4, top + 21), fill=FUR_LIGHT)
        draw.ellipse((cx - 20, top + 12, cx + 14, top + 26), fill=BELLY)
        for x in (cx - 17, cx - 2, cx + 13):
            _leg(draw, x, top + 24, step, near=True)
        # Head, jaw and one bright eye.
        draw.rectangle((cx - 38, top + 4, cx - 22, top + 19), fill=FUR_LIGHT)
        draw.polygon(((cx - 39, top + 12), (cx - 31, top + 8),
                      (cx - 31, top + 18)), fill=MAW)
        draw.polygon(((cx - 33, top + 4), (cx - 30, top - 5),
                      (cx - 25, top + 4)), fill=FUR_DARK)
        draw.rectangle((cx - 33, top + 8, cx - 30, top + 11), fill=EYE)
        # Tail, then the tentacles rising off the shoulders.
        draw.line((cx + 26, top + 6, cx + 34, top - 4,
                   cx + 28 + (5 if step else -5), top - 14),
                  fill=FUR_DARK, width=5)
        _tentacle(draw, (cx - 15, top + 3), (cx - 27, top - 7), step)
        _tentacle(draw, (cx - 9, top + 2), (cx - 3, top - 11), step)
    else:
        facing_camera = facing == "down"
        top = 20 + lift
        for x in (cx - 20, cx + 20):
            _leg(draw, x, top + 18, step, near=False)
        draw.ellipse((cx - 19, top, cx + 19, top + 30), fill=FUR)
        draw.ellipse((cx - 15, top + 2, cx + 7, top + 22), fill=FUR_LIGHT)
        draw.ellipse((cx - 13, top + 16, cx + 13, top + 32), fill=BELLY)
        for x in (cx - 16, cx + 16, cx - 8, cx + 8):
            _leg(draw, x, top + 26, step, near=True)
        head_top = top + 26 if facing_camera else top - 6
        draw.ellipse((cx - 11, head_top, cx + 11, head_top + 17),
                     fill=FUR_LIGHT if facing_camera else FUR)
        for side in (-1, 1):                        # ears
            draw.polygon(((cx + side * 10, head_top + 5),
                          (cx + side * 13, head_top - 4),
                          (cx + side * 4, head_top + 3)), fill=FUR_DARK)
        if facing_camera:
            for side in (-1, 1):
                draw.rectangle((cx + side * 6 - 2, head_top + 7,
                                cx + side * 6 + 1, head_top + 10), fill=EYE)
            draw.polygon(((cx - 4, head_top + 13), (cx + 4, head_top + 13),
                          (cx, head_top + 17)), fill=MAW)
        else:
            draw.line((cx, top + 28, cx + (7 if step else -7), ground - 8),
                      fill=FUR_DARK, width=5)
        _tentacle(draw, (cx - 11, top + 4), (cx - 24, top - 6), step)
        _tentacle(draw, (cx + 11, top + 4), (cx + 24, top - 6), step)

    # A faint after-image, offset from the real body. It never lies about
    # where the hitbox is; it only makes the beast look half-elsewhere.
    ghost = Image.new("RGBA", image.size, CLEAR)
    ImageDraw.Draw(ghost).ellipse(
        (cx - 22 + (6 if step else -6), 24 + lift,
         cx + 12 + (6 if step else -6), 48 + lift), fill=GHOST)
    return Image.alpha_composite(ghost, image)


def main() -> None:
    out = (Path(__file__).resolve().parents[1] /
           "assets" / "sprites" / "hazards" / "displacer_beast.png")
    sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H * 2), CLEAR)
    for row, step in enumerate((0, 1)):
        for col, facing in enumerate(("down", "up", "left")):
            sheet.alpha_composite(beast_frame(facing, step),
                                  (col * FRAME_W, row * FRAME_H))
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
