"""Generate Waterdeep's added dressing: the gate towers and banners on the
plaza's north wall, the tavern's keg rack, notice board and rug, and the
pantry's sack piles and produce baskets.

Every piece takes its colours from what is already on screen beside it:
the towers are the district wall's own brick with the gate's grey stone
at the corners, the banners are the watch's blue, the tavern pieces are
the tavern's planks.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

import generate_castle_banner


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
CLEAR = (0, 0, 0, 0)

# The district wall's brick, and the gate's stone.
BRICK = (138, 106, 58, 255)
BRICK_LIT = (158, 124, 70, 255)
BRICK_DARK = (108, 80, 44, 255)
BRICK_SHADOW = (84, 62, 36, 255)
STONE = (124, 124, 113, 255)
STONE_LIT = (163, 157, 137, 255)
STONE_DARK = (91, 94, 92, 255)
SLIT = (30, 32, 34, 255)
OUTLINE = (46, 36, 26, 255)

WOOD_DARK = (63, 42, 29, 255)
WOOD = (112, 74, 43, 255)
WOOD_LIGHT = (151, 102, 57, 255)
WOOD_PALE = (176, 128, 78, 255)
IRON = (54, 56, 60, 255)
BRASS = (183, 142, 58, 255)
BRASS_LIGHT = (225, 190, 91, 255)
PAPER = (222, 210, 176, 255)
PAPER_DARK = (180, 166, 128, 255)
BURLAP = (160, 136, 94, 255)
BURLAP_LIT = (190, 166, 120, 255)
BURLAP_DARK = (116, 96, 64, 255)
TWINE = (94, 74, 46, 255)

# The watch's blue and silver.
WATCH_BANNER = {
    "cloth_dark": (46, 60, 94, 255),
    "cloth": (66, 86, 128, 255),
    "cloth_lit": (92, 114, 156, 255),
    "trim": (196, 200, 208, 255),
    "trim_dark": (140, 144, 154, 255),
    "device": (226, 230, 236, 255),
}

TOWER_W, TOWER_H = 36, 80


def gate_tower() -> Image.Image:
    """A square wall tower standing a tile proud of the district wall.

    Its foot is on the paving in front of the wall, and it runs the full
    height of the wall behind it, crenellated at the top: the wall is as
    tall as the map lets anything be, so the tower says it is a tower by
    standing forward and by its stone corners, not by rising.
    """
    image = Image.new("RGBA", (TOWER_W, TOWER_H), CLEAR)
    draw = ImageDraw.Draw(image)
    left, right = 1, TOWER_W - 2
    top = 8
    # The body, brick in running bond, lit from the west.
    draw.rectangle((left - 1, top - 1, right + 1, TOWER_H - 1), fill=OUTLINE)
    draw.rectangle((left, top, right, TOWER_H - 3), fill=BRICK)
    for course, y in enumerate(range(top + 2, TOWER_H - 3, 4)):
        draw.line((left, y, right, y), fill=BRICK_DARK)
        shift = 0 if course % 2 else 4
        for x in range(left + shift, right, 8):
            draw.line((x, y - 3, x, y - 1), fill=BRICK_DARK)
        draw.line((left, y - 3, left + 6, y - 3), fill=BRICK_LIT)
    # The shaded east face of the projection.
    draw.rectangle((right - 4, top, right, TOWER_H - 3), fill=BRICK_SHADOW)
    for y in range(top + 2, TOWER_H - 3, 4):
        draw.line((right - 4, y, right, y), fill=OUTLINE)
    # Stone quoins up both corners, alternating long and short.
    for index, y in enumerate(range(top, TOWER_H - 6, 6)):
        long = index % 2 == 0
        width = 6 if long else 4
        draw.rectangle((left, y, left + width, y + 4), fill=STONE)
        draw.line((left, y, left + width, y), fill=STONE_LIT)
        draw.rectangle((right - width, y, right, y + 4), fill=STONE_DARK)
        draw.line((right - width, y, right, y), fill=STONE)
    # A string course of stone under the parapet.
    draw.rectangle((left - 1, top + 6, right + 1, top + 9), fill=STONE)
    draw.line((left - 1, top + 6, right + 1, top + 6), fill=STONE_LIT)
    draw.line((left - 1, top + 9, right + 1, top + 9), fill=STONE_DARK)
    # Crenellations: merlons of stone on top of the parapet.
    for x in range(left - 1, right + 1, 8):
        draw.rectangle((x, 0, x + 4, top + 5), fill=OUTLINE)
        draw.rectangle((x + 1, 1, x + 3, top + 5), fill=STONE)
        draw.line((x + 1, 1, x + 3, 1), fill=STONE_LIT)
    draw.rectangle((left, top, right, top + 5), fill=BRICK_DARK)
    draw.line((left, top, right, top), fill=BRICK_SHADOW)
    # Two arrow slits, one above the other.
    for y in (26, 50):
        draw.rectangle((16, y, 19, y + 11), fill=STONE_DARK)
        draw.rectangle((17, y + 1, 18, y + 10), fill=SLIT)
        draw.line((15, y + 12, 20, y + 12), fill=STONE_LIT)
    # A plinth where it meets the paving.
    draw.rectangle((left - 1, TOWER_H - 7, right + 1, TOWER_H - 1),
                   fill=STONE_DARK)
    draw.line((left - 1, TOWER_H - 7, right + 1, TOWER_H - 7), fill=STONE)
    draw.rectangle((right - 4, TOWER_H - 6, right + 1, TOWER_H - 1),
                   fill=(70, 72, 70, 255))
    return image


def keg_rack() -> Image.Image:
    """Three kegs on their sides in a timber cradle, taps facing the room."""
    image = Image.new("RGBA", (44, 34), CLEAR)
    draw = ImageDraw.Draw(image)
    # The cradle.
    draw.rectangle((1, 12, 42, 33), fill=WOOD_DARK)
    draw.rectangle((2, 30, 41, 32), fill=WOOD)
    for x in (2, 21, 40):
        draw.rectangle((x - 1, 12, x + 1, 33), fill=WOOD)
        draw.line((x - 1, 12, x - 1, 33), fill=WOOD_LIGHT)

    def keg(cx, cy):
        draw.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=OUTLINE)
        draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=WOOD)
        draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=WOOD_LIGHT)
        draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=WOOD)
        draw.arc((cx - 8, cy - 8, cx + 8, cy + 8), 200, 300, fill=WOOD_PALE)
        draw.arc((cx - 8, cy - 8, cx + 8, cy + 8), 0, 360, fill=IRON)
        draw.line((cx - 3, cy, cx + 3, cy), fill=WOOD_DARK)
        # The tap.
        draw.rectangle((cx - 1, cy + 1, cx + 1, cy + 5), fill=BRASS)
        draw.point((cx - 1, cy + 1), fill=BRASS_LIGHT)
        draw.rectangle((cx - 2, cy + 5, cx + 2, cy + 6), fill=BRASS)

    keg(11, 21)
    keg(32, 21)
    keg(22, 9)
    return image


def notice_board() -> Image.Image:
    """A board on two posts with the town's notices pinned to it."""
    image = Image.new("RGBA", (30, 36), CLEAR)
    draw = ImageDraw.Draw(image)
    for x in (4, 25):
        draw.rectangle((x - 1, 10, x + 1, 35), fill=WOOD_DARK)
        draw.line((x - 1, 10, x - 1, 35), fill=WOOD)
    draw.rectangle((0, 2, 29, 24), fill=OUTLINE)
    draw.rectangle((1, 3, 28, 23), fill=WOOD_LIGHT)
    draw.rectangle((3, 5, 26, 21), fill=(128, 92, 58, 255))
    # A little roof over it against the weather, even indoors: it came
    # off the dock wall.
    draw.polygon(((-1, 3), (14, -1), (30, 3)), fill=WOOD_DARK)
    draw.line((0, 2, 14, -1), fill=WOOD)
    notices = ((5, 6, 12, 14), (14, 7, 24, 12), (16, 14, 25, 20),
               (6, 15, 13, 20))
    for index, (x0, y0, x1, y1) in enumerate(notices):
        draw.rectangle((x0, y0, x1, y1), fill=PAPER)
        draw.line((x0, y1, x1, y1), fill=PAPER_DARK)
        for y in range(y0 + 2, y1 - 1, 2):
            draw.line((x0 + 1, y, x1 - 1 - (y + index) % 3, y),
                      fill=(120, 108, 90, 255))
        draw.point(((x0 + x1) // 2, y0), fill=(160, 40, 40, 255))
    # One wanted poster with a face on it.
    draw.rectangle((15, 8, 17, 10), fill=(150, 120, 96, 255))
    return image


def tavern_rug() -> Image.Image:
    """A long worn rug under the middle table, flat on the boards."""
    image = Image.new("RGBA", (80, 56), CLEAR)
    draw = ImageDraw.Draw(image)
    green_dark = (46, 62, 44, 255)
    green = (72, 94, 62, 255)
    ochre = (176, 136, 66, 255)
    ochre_dark = (130, 98, 48, 255)
    draw.rounded_rectangle((2, 3, 77, 52), radius=4, fill=(34, 30, 24, 255))
    draw.rounded_rectangle((3, 4, 76, 50), radius=3, fill=green_dark)
    draw.rectangle((7, 8, 72, 46), fill=green)
    draw.rectangle((10, 11, 69, 43), outline=ochre, width=1)
    draw.rectangle((13, 14, 66, 40), outline=ochre_dark, width=1)
    for step in range(9):
        spread = 12 - abs(step - 4) * 3
        draw.line((40 - spread, 23 + step, 40 + spread, 23 + step),
                  fill=ochre_dark if step % 2 else ochre)
    # Wear: a paler patch where the chairs scrape.
    for x, y in ((24, 30), (26, 31), (55, 18), (57, 17), (58, 19)):
        draw.point((x, y), fill=(96, 116, 80, 255))
    for x in range(6, 76, 5):
        draw.line((x, 1, x, 4), fill=ochre_dark)
        draw.line((x, 50, x, 54), fill=ochre_dark)
    return image


def sack_pile() -> Image.Image:
    """Three flour sacks slumped together, tied at the neck."""
    image = Image.new("RGBA", (30, 24), CLEAR)
    draw = ImageDraw.Draw(image)

    def sack(x0, y0, x1, y1):
        draw.ellipse((x0, y0, x1, y1), fill=BURLAP_DARK)
        draw.ellipse((x0 + 1, y0 + 1, x1 - 2, y1 - 2), fill=BURLAP)
        draw.arc((x0 + 2, y0 + 2, x1 - 3, y1 - 3), 190, 260, fill=BURLAP_LIT)
        neck = (x0 + x1) // 2
        draw.rectangle((neck - 2, y0 - 3, neck + 1, y0 + 1), fill=BURLAP)
        draw.line((neck - 3, y0 + 1, neck + 2, y0 + 1), fill=TWINE)
        draw.point((neck - 2, y0 - 3), fill=BURLAP_LIT)

    sack(1, 10, 15, 23)
    sack(14, 9, 29, 23)
    sack(7, 4, 21, 16)
    for x, y in ((6, 17), (21, 16), (13, 10)):
        draw.point((x, y), fill=(236, 230, 214, 255))   # a dusting of flour
    return image


def produce_basket() -> Image.Image:
    """A wicker basket heaped with onions and apples."""
    image = Image.new("RGBA", (22, 18), CLEAR)
    draw = ImageDraw.Draw(image)
    fruit = ((5, 6, (196, 160, 92, 255)), (10, 4, (170, 52, 40, 255)),
             (15, 6, (196, 160, 92, 255)), (8, 8, (150, 44, 36, 255)),
             (13, 8, (206, 172, 104, 255)))
    for cx, cy, colour in fruit:
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=colour)
        draw.point((cx - 1, cy - 2), fill=(236, 220, 170, 255))
    draw.polygon(((1, 9), (20, 9), (18, 17), (3, 17)), fill=WOOD_DARK)
    draw.polygon(((2, 10), (19, 10), (17, 16), (4, 16)), fill=WOOD_LIGHT)
    for y in (12, 14):
        draw.line((3, y, 18, y), fill=WOOD)
    for x in range(4, 18, 3):
        draw.line((x, 10, x + 1, 16), fill=WOOD)
    draw.line((1, 9, 20, 9), fill=WOOD_PALE)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gate_tower().save(OUT / "waterdeep_gate_tower.png")
    for frame in range(generate_castle_banner.FRAMES):
        generate_castle_banner.banner(frame, WATCH_BANNER).save(
            OUT / f"waterdeep_banner_{frame + 1}.png")
    keg_rack().save(OUT / "tavern_keg_rack.png")
    notice_board().save(OUT / "tavern_notice_board.png")
    tavern_rug().save(OUT / "tavern_rug.png")
    sack_pile().save(OUT / "pantry_sack_pile.png")
    produce_basket().save(OUT / "pantry_produce_basket.png")
    print(f"Wrote Waterdeep dressing to {OUT}")


if __name__ == "__main__":
    main()
