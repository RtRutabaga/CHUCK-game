"""Generate the orc catapult for the final encounter.

Run from the project root (requires Pillow, dev-only):

    python tools/generate_orc_catapult.py

Writes assets/sprites/hazards/orc_catapult.png: four 56x44 frames,

    0  cocked    the arm hauled back, a rock in the bucket
    1  loosing   the arm upright, mid-swing
    2  loosed    the arm against its stop, the bucket empty
    3  wreck     what the dragon leaves: burnt timbers, a snapped arm

Side-on, facing east, which is where it shoots: at the three heroes
holding the rift. Crude, lashed-together orc work -- raw timber,
rope bindings, iron-shod wheels -- at the same human scale as the orcs
pushing it, so it towers over Chuck like everything else in this room.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = (Path(__file__).resolve().parents[1] / "assets" / "sprites"
       / "hazards" / "orc_catapult.png")
FRAME_W, FRAME_H = 56, 44

OUTLINE = (30, 22, 18, 255)
WOOD = (122, 86, 50, 255)
WOOD_LIT = (158, 116, 70, 255)
WOOD_DARK = (84, 58, 34, 255)
ROPE = (196, 172, 118, 255)
IRON = (70, 70, 76, 255)
IRON_LIT = (118, 118, 126, 255)
ROCK = (132, 124, 112, 255)
ROCK_LIT = (176, 168, 150, 255)
CHAR = (38, 30, 28, 255)
CHAR_LIT = (72, 56, 46, 255)
EMBER = (232, 110, 40, 255)
EMBER_HOT = (255, 196, 96, 255)
PIVOT = (30, 25)            # where the arm turns, in frame pixels


def _plank(draw, a, b, width, colour, lit=None):
    draw.line((*a, *b), fill=OUTLINE, width=width + 2)
    draw.line((*a, *b), fill=colour, width=width)
    if lit is not None:
        draw.line((a[0], a[1] - 1, b[0], b[1] - 1), fill=lit, width=1)


def _wheel(draw, cx, cy, charred=False):
    rim = CHAR if charred else IRON
    hub = CHAR_LIT if charred else WOOD_DARK
    draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=OUTLINE)
    draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=rim)
    draw.ellipse((cx - 4, cy - 4, cx + 4, cy + 4),
                 fill=CHAR if charred else WOOD)
    for angle in (0.3, 1.87, 3.44, 5.01):
        draw.line((cx, cy, cx + round(math.cos(angle) * 4),
                   cy + round(math.sin(angle) * 4)), fill=hub, width=1)
    draw.ellipse((cx - 1, cy - 1, cx + 1, cy + 1),
                 fill=CHAR_LIT if charred else IRON_LIT)


def _frame_body(draw) -> None:
    """The carriage: base rails, uprights, the stop, and the wheels."""
    # Base rails, one behind the other, running the length of it.
    _plank(draw, (6, 34), (50, 34), 3, WOOD_DARK)
    _plank(draw, (4, 36), (52, 36), 3, WOOD, WOOD_LIT)
    # The A-frame the arm turns in.
    _plank(draw, (20, 35), (PIVOT[0], PIVOT[1]), 3, WOOD, WOOD_LIT)
    _plank(draw, (40, 35), (PIVOT[0], PIVOT[1]), 3, WOOD, WOOD_LIT)
    # The crossbar the arm slams into.
    _plank(draw, (40, 35), (44, 12), 2, WOOD_DARK)
    _plank(draw, (36, 12), (48, 12), 2, WOOD, WOOD_LIT)
    # Rope lashing at the joints: this was not built, it was tied.
    for x, y in ((PIVOT[0] - 1, PIVOT[1] - 1), (43, 11), (21, 33), (39, 33)):
        draw.line((x - 2, y, x + 2, y + 2), fill=ROPE, width=1)
        draw.line((x - 2, y + 2, x + 2, y), fill=ROPE, width=1)
    _wheel(draw, 13, 37)
    _wheel(draw, 43, 37)


def _arm(draw, angle: float, loaded: bool) -> None:
    """The throwing arm at `angle` (radians, 0 = pointing east)."""
    length = 19
    tail = 6
    ex = PIVOT[0] + math.cos(angle) * length
    ey = PIVOT[1] - math.sin(angle) * length
    tx = PIVOT[0] - math.cos(angle) * tail
    ty = PIVOT[1] + math.sin(angle) * tail
    _plank(draw, (round(tx), round(ty)), (round(ex), round(ey)), 3,
           WOOD, WOOD_LIT)
    # The bucket, a cupped block at the end of the arm.
    draw.ellipse((round(ex) - 5, round(ey) - 4, round(ex) + 5,
                  round(ey) + 4), fill=OUTLINE)
    draw.ellipse((round(ex) - 4, round(ey) - 3, round(ex) + 4,
                  round(ey) + 3), fill=WOOD_DARK)
    if loaded:
        draw.ellipse((round(ex) - 4, round(ey) - 6, round(ex) + 4,
                      round(ey) + 1), fill=OUTLINE)
        draw.ellipse((round(ex) - 3, round(ey) - 5, round(ex) + 3,
                      round(ey)), fill=ROCK)
        draw.point((round(ex) - 1, round(ey) - 4), fill=ROCK_LIT)
    # The pivot pin.
    draw.ellipse((PIVOT[0] - 2, PIVOT[1] - 2, PIVOT[0] + 2, PIVOT[1] + 2),
                 fill=IRON)


def cocked() -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    _frame_body(draw)
    # Hauled back and down behind it, the bucket low at the west end.
    _arm(draw, math.radians(200), loaded=True)
    # The winch rope, taut from the arm down to the rail.
    draw.line((10, 28, 16, 35), fill=ROPE, width=1)
    return image


def loosing() -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    _frame_body(draw)
    _arm(draw, math.radians(100), loaded=True)
    return image


def loosed() -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    _frame_body(draw)
    _arm(draw, math.radians(28), loaded=False)
    return image


def wreck() -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    # The carriage burnt down to its rails, one end collapsed.
    _plank(draw, (4, 37), (52, 36), 3, CHAR, CHAR_LIT)
    _plank(draw, (8, 34), (30, 30), 3, CHAR, CHAR_LIT)
    _plank(draw, (20, 36), (28, 24), 2, CHAR)
    _plank(draw, (42, 36), (36, 26), 2, CHAR)
    # The arm snapped off and lying across the rails.
    _plank(draw, (26, 33), (50, 28), 2, CHAR, CHAR_LIT)
    _wheel(draw, 13, 38, charred=True)
    _wheel(draw, 44, 39, charred=True)
    # Embers still in it.
    for x, y in ((12, 35), (24, 31), (33, 36), (46, 31), (29, 26)):
        draw.point((x, y), fill=EMBER)
        draw.point((x + 1, y), fill=EMBER_HOT)
    return image


def main() -> None:
    sheet = Image.new("RGBA", (FRAME_W * 4, FRAME_H), (0, 0, 0, 0))
    for index, frame in enumerate((cocked(), loosing(), loosed(), wreck())):
        sheet.alpha_composite(frame, (index * FRAME_W, 0))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
