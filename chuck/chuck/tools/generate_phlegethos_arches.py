"""Generate Phlegethos's threshold arches.

Run from the project root (requires Pillow, dev-only):

    python tools/generate_phlegethos_arches.py

Writes assets/sprites/objects/phlegethos_arch_ns.png (48x38) and
phlegethos_arch_ew.png (38x48).

The same openings as the temple's arches, tile for tile -- the doorways
of this region are built at that scale on purpose, and a devil-sized
door has to stay devil-sized. Everything else about them is different.
The temple's are old green stone, block-seamed, with moss in the joints.
These are the fortress's iron-strapped basalt: darker, banded with iron
and studded with rivets, cracked through with ember light, and lit from
the doorway itself rather than from the sky. Nothing grows on them.

The palette is taken from the Phlegethos tileset and the fortress wall
(tools/generate_phlegethos_tileset.py), so a gate reads as part of the
wall it is cut into.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "objects"

TRANSPARENT = (0, 0, 0, 0)
# The dark of the opening, and the fortress stone around it.
VOID = (9, 7, 9, 255)
STONE = (44, 40, 46, 255)
STONE_DARK = (26, 24, 30, 255)
STONE_LIGHT = (70, 64, 72, 255)
IRON = (96, 92, 100, 255)
IRON_DARK = (60, 58, 66, 255)
# Ember light: in the cracks, under the keystone, and out of the doorway.
EMBER_DEEP = (112, 28, 13, 255)
EMBER = (178, 45, 12, 255)
EMBER_HOT = (235, 83, 15, 255)
EMBER_BRIGHT = (255, 157, 31, 255)


def _rivets(draw: ImageDraw.ImageDraw, box, horizontal: bool) -> None:
    """Iron studs along a strap: what holds this thing together."""
    x0, y0, x1, y1 = box
    if horizontal:
        for x in range(x0 + 2, x1 - 1, 5):
            draw.point((x, y0 + 1), fill=IRON)
            draw.point((x, y1 - 1), fill=IRON_DARK)
    else:
        for y in range(y0 + 2, y1 - 1, 5):
            draw.point((x0 + 1, y), fill=IRON)
            draw.point((x1 - 1, y), fill=IRON_DARK)


def _cracks(draw: ImageDraw.ImageDraw, seams) -> None:
    """Ember light in the joints: the heat is inside the stone."""
    for (x0, y0), (x1, y1) in seams:
        draw.line((x0, y0, x1, y1), fill=EMBER_DEEP)
        draw.point((x0, y0), fill=EMBER)


def north_south_arch() -> Image.Image:
    """The frontal gate: the same 48x38 opening as the temple's."""
    image = Image.new("RGBA", (48, 38), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # The opening, and the glow standing in it.
    draw.rectangle((13, 11, 34, 37), fill=VOID)
    for index, y in enumerate(range(37, 30, -1)):
        shade = (EMBER_DEEP if index > 3 else (60, 20, 14, 255))
        draw.line((14 + index, y, 33 - index, y), fill=shade)
    # Jambs and the stepped head, in fortress basalt.
    draw.rectangle((5, 15, 12, 37), fill=STONE)
    draw.rectangle((35, 15, 42, 37), fill=STONE)
    draw.rectangle((9, 8, 38, 15), fill=STONE)
    draw.rectangle((13, 4, 34, 9), fill=STONE)
    draw.rectangle((17, 1, 30, 5), fill=STONE)
    # Iron straps across the jambs rather than the temple's block seams.
    for y in (19, 27, 34):
        draw.rectangle((5, y, 12, y + 2), fill=IRON_DARK)
        draw.rectangle((35, y, 42, y + 2), fill=IRON_DARK)
        _rivets(draw, (5, y, 12, y + 2), horizontal=True)
        _rivets(draw, (35, y, 42, y + 2), horizontal=True)
    draw.rectangle((9, 9, 38, 11), fill=IRON_DARK)
    _rivets(draw, (9, 9, 38, 11), horizontal=True)
    # The lit edge, and the keystone burning in the crown.
    draw.line((9, 15, 13, 10, 17, 6, 30, 6, 34, 10, 38, 15),
              fill=STONE_LIGHT, width=2)
    draw.rectangle((21, 1, 26, 6), fill=STONE_DARK)
    draw.rectangle((22, 2, 25, 5), fill=EMBER_DEEP)
    draw.rectangle((23, 3, 24, 4), fill=EMBER_HOT)
    draw.point((23, 3), fill=EMBER_BRIGHT)
    _cracks(draw, ((((7, 21), (7, 26))), ((40, 30), (40, 36)),
                   ((11, 33), (11, 37)), ((37, 17), (37, 22))))
    draw.line((12, 37, 35, 37), fill=STONE_DARK, width=2)
    return image


def east_west_arch() -> Image.Image:
    """The side-wall gate: the same 38x48 opening as the temple's."""
    image = Image.new("RGBA", (38, 48), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 13, 37, 34), fill=VOID)
    for index, x in enumerate(range(37, 30, -1)):
        shade = (EMBER_DEEP if index > 3 else (60, 20, 14, 255))
        draw.line((x, 14 + index, x, 33 - index), fill=shade)
    draw.rectangle((10, 5, 37, 12), fill=STONE)
    draw.rectangle((10, 35, 37, 42), fill=STONE)
    draw.rectangle((5, 9, 12, 38), fill=STONE)
    draw.rectangle((1, 13, 6, 34), fill=STONE)
    for x in (16, 24, 32):
        draw.rectangle((x, 5, x + 2, 12), fill=IRON_DARK)
        draw.rectangle((x, 35, x + 2, 42), fill=IRON_DARK)
        _rivets(draw, (x, 5, x + 2, 12), horizontal=False)
        _rivets(draw, (x, 35, x + 2, 42), horizontal=False)
    draw.rectangle((9, 9, 11, 38), fill=IRON_DARK)
    _rivets(draw, (9, 9, 11, 38), horizontal=False)
    draw.line((12, 9, 7, 13, 7, 34, 12, 38), fill=STONE_LIGHT, width=2)
    draw.rectangle((1, 21, 6, 26), fill=STONE_DARK)
    draw.rectangle((2, 22, 5, 25), fill=EMBER_DEEP)
    draw.rectangle((3, 23, 4, 24), fill=EMBER_HOT)
    draw.point((3, 23), fill=EMBER_BRIGHT)
    _cracks(draw, (((14, 7), (19, 7)), ((28, 40), (33, 40)),
                   ((21, 41), (25, 41)), ((12, 11), (16, 11))))
    draw.line((37, 12, 37, 35), fill=STONE_DARK, width=2)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (("phlegethos_arch_ns", north_south_arch()),
                        ("phlegethos_arch_ew", east_west_arch()),
                        # Mirrored, for a door in an east wall: the
                        # reveal is on the far side of the passage.
                        ("phlegethos_arch_ew_east",
                         east_west_arch().transpose(
                             Image.FLIP_LEFT_RIGHT))):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
