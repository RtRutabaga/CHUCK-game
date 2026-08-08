"""Generate the urban sewer crocodile sheet (Phase 11).

The crocodile is an UndeadEnemy kind, so this sheet matches that layout
exactly: three facings (down, up, left) on one row of 16x30 frames. That
frame is upright and narrow, which suits a person -- and suits a
top-down crocodile even better, since a croc really is long and thin
seen from above. At native scale it runs the full 30px against Chuck's
14, which is the whole point of the encounter.
"""

from pathlib import Path

from PIL import Image, ImageDraw

FRAME_W, FRAME_H = 16, 30
CLEAR = (0, 0, 0, 0)

HIDE_DARK = (32, 46, 34, 255)
HIDE = (58, 78, 52, 255)
HIDE_LIGHT = (86, 112, 70, 255)
BELLY = (146, 152, 108, 255)
SCUTE = (24, 34, 26, 255)
EYE = (232, 198, 78, 255)
TOOTH = (238, 240, 226, 255)
MAW = (128, 44, 52, 255)


def _legs(draw, top, splay):
    """Four squat legs, splayed out either side of the body."""
    for row in (top, top + 11):
        for side in (-1, 1):
            x = 8 + side * 5
            draw.rectangle((x - 1, row, x + 1, row + 3), fill=HIDE_DARK)
            foot = x + side * splay
            draw.rectangle((min(x, foot) - 1, row + 3,
                            max(x, foot) + 1, row + 4), fill=HIDE_DARK)


def crocodile_frame(facing: str) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), CLEAR)
    draw = ImageDraw.Draw(image)

    if facing == "left":
        # A 16-wide frame cannot hold a 30-long animal broadside, so the
        # turning croc is drawn curved: head out to the left, body
        # sweeping back and down, tail trailing. That keeps its mass the
        # same as the head-on frames instead of shrinking it by half.
        draw.polygon(((3, 6), (11, 9), (13, 17), (10, 25), (7, 29),
                      (5, 24), (5, 16), (2, 10)), fill=HIDE)
        draw.polygon(((5, 8), (10, 11), (11, 17), (9, 24), (7, 26),
                      (6, 18), (5, 12)), fill=HIDE_LIGHT)
        for y in range(11, 25, 4):                 # scutes along the spine
            draw.rectangle((7, y, 9, y + 1), fill=SCUTE)
        # The head, jaws open toward the left edge.
        draw.polygon(((0, 5), (7, 4), (8, 11), (1, 10)), fill=HIDE)
        draw.polygon(((0, 7), (6, 6), (6, 9), (1, 9)), fill=MAW)
        for x in range(1, 7, 2):
            draw.point((x, 6), fill=TOOTH)
            draw.point((x, 9), fill=TOOTH)
        draw.point((7, 3), fill=EYE)
        draw.point((4, 3), fill=EYE)
        # Legs splayed off the outside of the curve.
        for x, y in ((11, 13), (12, 20)):
            draw.rectangle((x, y, x + 2, y + 2), fill=HIDE_DARK)
        for x, y in ((3, 14), (4, 21)):
            draw.rectangle((x - 1, y, x + 1, y + 2), fill=HIDE_DARK)
        return image

    head_first = facing == "down"
    # The body: a long tapered slab, widest at the shoulders.
    draw.polygon(((4, 4), (11, 4), (13, 14), (11, 22), (8, 29), (5, 22),
                  (2, 14)), fill=HIDE)
    draw.polygon(((5, 6), (10, 6), (11, 14), (9, 21), (6, 21), (4, 14)),
                 fill=HIDE_LIGHT if head_first else HIDE)
    _legs(draw, 8, 3)
    # Scutes down the spine, and the tail tapering off the far end.
    for y in range(7, 22, 4):
        draw.rectangle((6, y, 9, y + 1), fill=SCUTE)
    draw.polygon(((7, 22), (8, 22), (8, 29), (7, 29)), fill=HIDE_DARK)

    if head_first:
        draw.ellipse((3, 0, 12, 9), fill=HIDE)
        draw.ellipse((5, 1, 10, 7), fill=HIDE_LIGHT)
        draw.rectangle((4, 6, 11, 8), fill=MAW)     # the open mouth
        for x in range(4, 12, 2):
            draw.point((x, 6), fill=TOOTH)
            draw.point((x + 1, 8), fill=TOOTH)
        draw.point((4, 2), fill=EYE)                # eyes set high and wide
        draw.point((11, 2), fill=EYE)
    else:
        draw.ellipse((3, 0, 12, 9), fill=HIDE_DARK)
        draw.ellipse((5, 1, 10, 6), fill=HIDE)
        for x in (5, 10):                           # the back of the skull
            draw.point((x, 3), fill=SCUTE)
    return image


def main() -> None:
    out = (Path(__file__).resolve().parents[1] /
           "assets" / "sprites" / "hazards" / "crocodile.png")
    sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H), CLEAR)
    for col, facing in enumerate(("down", "up", "left")):
        sheet.alpha_composite(crocodile_frame(facing), (col * FRAME_W, 0))
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
