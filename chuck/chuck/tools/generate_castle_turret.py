"""Generate the corner turret for the collided desert's castle.

The curtain got crenellated and the corners got a drum tile, and at one
tile each the corners came out reading as a slightly different piece of
wall rather than as the thing a wall turns around. A castle's corner is
its tallest point -- that is the entire reason a corner tower exists --
and nothing on this map was taller than anything else.

So the corner is an object rather than a tile: a round tower three tiles
across with a slate cone on it, standing high enough that the wall runs
into its base. It is the only thing in the fragment that rises, which is
what makes the walls beside it read as walls of something.

The pennant is the same red and gold as the banners hanging on the
faces below it. The castle already says whose it is down at eye level;
saying it again on the roofline is what a real one does, and it ties
the two objects together as one house rather than two ideas.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"

# Three tiles across and four and a half tall. The bottom forty-eight
# pixels stand on the turret's own three-by-three of solid stone; the
# rest is the height, which is the whole point of the object.
W, H = 48, 72
FOOT = 48                       # where the three-by-three block begins

# The fragment's own ashlar, so the turret is the same building as the
# wall it stands on rather than a visitor.
STONE = (92, 92, 96, 255)
STONE_LIT = (122, 122, 126, 255)
STONE_DARK = (58, 58, 62, 255)
MORTAR = (74, 74, 78, 255)
SLIT = (44, 44, 50, 255)
MOSS = (74, 96, 68, 255)

# Slate, cold and blue against grey stone so the roof is a different
# material and not just a darker wall.
SLATE = (68, 74, 92, 255)
SLATE_LIT = (96, 104, 126, 255)
SLATE_DARK = (46, 50, 64, 255)

CLOTH = (146, 34, 46, 255)
TRIM = (196, 162, 78, 255)


def turret() -> Image.Image:
    """One corner turret, lit from the west like everything else here."""
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # ------------------------------------------------------------------
    # The drum, from its base up to the corbels.
    # ------------------------------------------------------------------
    body_top, body_bottom = 34, H - 1
    left, right = 5, W - 6
    span = right - left
    for x in range(left, right + 1):
        # A cylinder is a gradient, not an outline. Drawn with a couple
        # of shadow columns down each edge it stayed a rectangle with
        # dark sides; shaded across its whole width, with the light
        # about a third of the way in, it turns.
        across = (x - left) / span
        light = math.sin(across * math.pi) ** 0.6
        light *= 1.0 - abs(across - 0.35) * 0.55
        if light > 0.86:
            colour = STONE_LIT
        elif light > 0.5:
            colour = STONE
        elif light > 0.28:
            colour = MORTAR
        else:
            colour = STONE_DARK
        draw.line((x, body_top, x, body_bottom), fill=colour)
    # Courses, bowing downward toward the middle -- the second half of
    # what makes this something you are looking around.
    for y in range(body_top + 5, body_bottom, 6):
        for x in range(left + 1, right):
            across = (x - left) / span
            drop = round(math.sin(across * math.pi) * 1.5)
            image.putpixel((x, min(body_bottom, y + drop)), STONE_DARK)

    # An arrow loop on the face that shows, cross-shaped because a bare
    # vertical line at this width reads as a joint in the stonework.
    draw.rectangle((23, 45, 24, 55), fill=SLIT)
    draw.rectangle((21, 48, 26, 49), fill=SLIT)
    draw.line((23, 44, 24, 44), fill=STONE_LIT)

    # ------------------------------------------------------------------
    # The corbelled parapet the roof sits on. It is wider than the drum
    # and wider than the eave above it, so the turret reads as stepping
    # out at the top the way a machicolated one does.
    # ------------------------------------------------------------------
    for x in range(1, W - 1):
        across = (x - 1) / (W - 3)
        light = math.sin(across * math.pi) ** 0.5
        colour = STONE_LIT if light > 0.88 else (
            STONE if light > 0.45 else MORTAR)
        draw.line((x, 29, x, 35), fill=colour)
    draw.line((1, 29, W - 2, 29), fill=STONE_LIT)
    draw.line((1, 35, W - 2, 35), fill=STONE_DARK)
    # The corbels themselves: the brackets the parapet is carried on,
    # hanging under its lip where anybody can see them.
    for x in range(2, W - 2, 4):
        draw.rectangle((x, 36, x + 1, 38), fill=STONE_DARK)
        draw.point((x, 36), fill=MORTAR)

    # ------------------------------------------------------------------
    # The cone.
    # ------------------------------------------------------------------
    apex_x, apex_y = 24, 4
    eave_y, eave_spread = 28, 17
    for y in range(apex_y, eave_y + 1):
        spread = round((y - apex_y) / (eave_y - apex_y) * eave_spread) + 1
        draw.line((apex_x - spread, y, apex_x + spread, y), fill=SLATE)
        draw.line((apex_x + spread - 2, y, apex_x + spread, y),
                  fill=SLATE_DARK)
        draw.line((apex_x - spread, y, apex_x - spread + 1, y),
                  fill=SLATE_DARK)
        lit = apex_x - max(1, round(spread * 0.45))
        image.putpixel((max(0, lit), y), SLATE_LIT)
        image.putpixel((max(0, lit + 1), y), SLATE_LIT)
    # Slate courses, tighter toward the apex.
    for y in (9, 14, 19, 24):
        spread = round((y - apex_y) / (eave_y - apex_y) * eave_spread) + 1
        draw.line((apex_x - spread + 2, y, apex_x + spread - 2, y),
                  fill=SLATE_DARK)
    # The eave line, and its shadow on the parapet under it.
    draw.line((apex_x - eave_spread - 1, eave_y,
               apex_x + eave_spread + 1, eave_y), fill=SLATE_DARK)
    draw.line((apex_x - eave_spread - 1, eave_y + 1,
               apex_x + eave_spread + 1, eave_y + 1), fill=STONE_DARK)

    # ------------------------------------------------------------------
    # The finial and its pennant: the same house as the banners below.
    # ------------------------------------------------------------------
    draw.line((apex_x, 0, apex_x, 6), fill=STONE_DARK)
    draw.point((apex_x, 0), fill=TRIM)
    draw.polygon(((apex_x + 1, 1), (apex_x + 9, 3), (apex_x + 1, 5)),
                 fill=CLOTH)
    draw.line((apex_x + 1, 3, apex_x + 7, 3), fill=TRIM)

    # Two pieces of moss, low down where the rain runs off.
    image.putpixel((7, 62), MOSS)
    image.putpixel((W - 9, 55), MOSS)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    turret().save(OUT / "castle_turret.png")
    print(f"Wrote {W}x{H} to {OUT / 'castle_turret.png'}")


if __name__ == "__main__":
    main()
