"""Generate human-scale crew-quarter furniture in native pixel art."""

from pathlib import Path

from PIL import Image, ImageDraw


OUT = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "objects"
TRANSPARENT = (0, 0, 0, 0)
WOOD_DARK = (63, 42, 29, 255)
WOOD = (112, 74, 43, 255)
WOOD_LIGHT = (151, 102, 57, 255)
CANVAS_DARK = (95, 75, 62, 255)
CANVAS = (151, 126, 96, 255)
CANVAS_LIGHT = (184, 158, 119, 255)
ROPE = (184, 149, 91, 255)
BRASS = (183, 142, 58, 255)
BRASS_LIGHT = (225, 190, 91, 255)
DARK = (31, 24, 22, 255)
LEAF = (91, 105, 55, 255)
SAIL_DARK = (161, 145, 102, 255)
SAIL = (218, 202, 151, 255)
SAIL_LIGHT = (239, 225, 174, 255)


def hammock() -> Image.Image:
    """A broad hanging human bunk looming over Chuck."""
    image = Image.new("RGBA", (30, 44), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.line((2, 0, 7, 14), fill=ROPE, width=2)
    draw.line((27, 0, 22, 14), fill=ROPE, width=2)
    draw.line((2, 0, 2, 36), fill=WOOD_DARK, width=3)
    draw.line((27, 0, 27, 36), fill=WOOD_DARK, width=3)
    draw.line((6, 13, 23, 13), fill=ROPE, width=2)
    # Deep curved canvas belly; Chuck can visibly pass under its overhang.
    for y, inset in ((14, 0), (15, 0), (16, 1), (17, 1), (18, 2),
                     (19, 2), (20, 3), (21, 4), (22, 5), (23, 7),
                     (24, 9)):
        draw.line((6 + inset, y, 23 - inset, y), fill=CANVAS, width=1)
    draw.line((7, 14, 22, 14), fill=CANVAS_LIGHT, width=2)
    draw.line((13, 16, 17, 23), fill=CANVAS_DARK, width=2)
    draw.rectangle((0, 35, 6, 41), fill=WOOD)
    draw.rectangle((23, 35, 29, 41), fill=WOOD)
    draw.line((0, 41, 6, 41), fill=WOOD_LIGHT, width=2)
    draw.line((23, 41, 29, 41), fill=WOOD_LIGHT, width=2)
    return image


def captain_bed() -> Image.Image:
    """An oversized human bed, nearly architectural beside Chuck. Long from
    head (top) to foot (bottom) so it reads as a proper north-south berth."""
    image = Image.new("RGBA", (72, 64), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Heavy raised frame and tall headboard at the top (the head).
    draw.rectangle((1, 3, 70, 12), fill=WOOD_DARK)
    draw.rectangle((4, 5, 67, 10), fill=WOOD)
    draw.line((5, 6, 66, 6), fill=WOOD_LIGHT, width=2)
    # The long mattress runs down to the foot.
    draw.rectangle((4, 10, 67, 59), fill=DARK)
    draw.rectangle((6, 11, 65, 56), fill=CANVAS_LIGHT)
    # Two pale pillows at the head and a deep captain-red cover down the berth.
    draw.rounded_rectangle((9, 13, 29, 23), radius=3, fill=(211, 194, 157))
    draw.rounded_rectangle((42, 13, 62, 23), radius=3, fill=(211, 194, 157))
    draw.rectangle((6, 25, 65, 56), fill=(113, 45, 42))
    draw.line((7, 26, 64, 26), fill=(174, 78, 55), width=2)
    draw.line((35, 26, 35, 54), fill=(78, 32, 31), width=1)
    draw.line((6, 40, 65, 40), fill=(90, 36, 34), width=1)  # a fold across it
    # Brass corners running the full length, and stout feet at the foot.
    for x in (4, 64):
        draw.rectangle((x, 9, x + 3, 59), fill=BRASS)
        draw.line((x + 1, 10, x + 1, 58), fill=BRASS_LIGHT, width=1)
    draw.rectangle((2, 57, 10, 63), fill=WOOD_DARK)
    draw.rectangle((61, 57, 69, 63), fill=WOOD_DARK)
    return image


def captain_rug() -> Image.Image:
    """A broad woven rug drawn flat beneath every standing object."""
    image = Image.new("RGBA", (80, 48), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    dark_red = (75, 35, 37, 255)
    red = (126, 53, 48, 255)
    gold = (183, 142, 58, 255)
    draw.rounded_rectangle((2, 3, 77, 44), radius=5, fill=DARK)
    draw.rounded_rectangle((4, 4, 75, 42), radius=4, fill=dark_red)
    draw.rectangle((8, 8, 71, 38), fill=red)
    draw.rectangle((11, 11, 68, 35), outline=gold, width=2)
    draw.polygon(((40, 13), (54, 23), (40, 33), (26, 23)),
                 fill=dark_red)
    draw.polygon(((40, 16), (49, 23), (40, 30), (31, 23)),
                 outline=gold)
    for x in range(7, 75, 6):
        draw.line((x, 1, x, 4), fill=ROPE, width=1)
        draw.line((x, 42, x, 46), fill=ROPE, width=1)
    return image


def round_table() -> Image.Image:
    """An enormous round mess table, architectural at Chuck's scale."""
    image = Image.new("RGBA", (34, 25), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.ellipse((1, 1, 32, 17), fill=WOOD_DARK)
    draw.ellipse((2, 1, 31, 15), fill=WOOD)
    draw.arc((3, 2, 30, 14), 195, 345, fill=WOOD_LIGHT, width=2)
    draw.line((6, 8, 27, 8), fill=WOOD_DARK, width=1)
    draw.line((17, 2, 17, 15), fill=WOOD_DARK, width=1)
    draw.rectangle((7, 14, 11, 23), fill=WOOD_DARK)
    draw.rectangle((23, 14, 27, 23), fill=WOOD_DARK)
    draw.line((6, 23, 12, 23), fill=WOOD_LIGHT, width=1)
    draw.line((22, 23, 28, 23), fill=WOOD_LIGHT, width=1)
    return image


def captain_chest(stage: int) -> Image.Image:
    """A broad brass-bound sea chest across four opening stages."""
    image = Image.new("RGBA", (32, 24), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    if stage == 3:
        draw.rectangle((2, 0, 29, 7), fill=WOOD_DARK)
        draw.rectangle((3, 1, 28, 5), fill=WOOD)
        draw.line((3, 6, 28, 6), fill=WOOD_LIGHT, width=1)
        draw.rectangle((2, 7, 29, 12), fill=DARK)
    elif stage == 2:
        draw.polygon(((2, 2), (29, 2), (27, 9), (4, 9)),
                     fill=WOOD_DARK)
        draw.polygon(((4, 3), (27, 3), (25, 7), (6, 7)), fill=WOOD)
        draw.line((5, 3, 26, 3), fill=WOOD_LIGHT, width=1)
        draw.rectangle((2, 8, 29, 12), fill=DARK)
    elif stage == 1:
        draw.polygon(((2, 3), (29, 3), (28, 9), (3, 9)),
                     fill=WOOD_DARK)
        draw.polygon(((3, 4), (28, 4), (27, 7), (4, 7)), fill=WOOD)
        draw.line((4, 4, 27, 4), fill=WOOD_LIGHT, width=1)
        draw.rectangle((2, 8, 29, 12), fill=DARK)
    else:
        draw.rounded_rectangle((1, 3, 30, 11), radius=4, fill=WOOD_DARK)
        draw.rounded_rectangle((2, 3, 29, 9), radius=3, fill=WOOD)
        draw.line((4, 4, 27, 4), fill=WOOD_LIGHT, width=1)
    draw.rectangle((1, 11, 30, 22), fill=WOOD)
    draw.rectangle((1, 19, 30, 22), fill=WOOD_DARK)
    draw.line((2, 12, 29, 12), fill=WOOD_LIGHT, width=1)
    for x in (5, 25):
        lid_top = 3 if stage == 0 else (7 if stage == 3 else 8)
        draw.rectangle((x, lid_top, x + 2, 22), fill=BRASS)
        draw.line((x + 1, lid_top + 1, x + 1, 21),
                  fill=BRASS_LIGHT, width=1)
    draw.rectangle((14, 11, 18, 16), fill=BRASS)
    draw.rectangle((15, 12, 17, 14), fill=DARK)
    return image


def mast_sail() -> Image.Image:
    """A mast under square rig: three yards of sail, stacked up the spar.

    One enormous sheet of canvas per mast reads as a sail, but not as a
    sailing ship. A square rigger carries a course, a topsail and a
    topgallant on separate yards up the same mast, each smaller than
    the one below it, and from above that stack of three shrinking
    rectangles is the whole silhouette of the thing.

    They are drawn square on the mast and tilted a few pixels, the way
    a set of yards braced round to the same wind reads from overhead.
    """
    image = Image.new("RGBA", (224, 240), TRANSPARENT)
    draw = ImageDraw.Draw(image)

    # The canvas first: the mast stands in front of its own sails, and
    # it is one unbroken spar all the way up. Drawn the other way round
    # it survives only in the gaps between the yards, and a mast that
    # comes and goes behind the cloth reads as three separate boards
    # rather than as one pole with sails hung off it.

    # (centre y of the yard, half-width, depth). Biggest at the foot of
    # the mast, smallest at the head. The whole rig sits high enough
    # that its lowest yard clears both the crew working at the mast's
    # foot and the helm standing forward of it: a course whose foot
    # comes down level with a man's head is canvas lying on the deck
    # party, and the bare stretch of mast under it is most of what makes
    # the rig read as tall rather than as bunting.
    yards = ((134, 98, 50), (76, 78, 42), (26, 60, 34))
    for centre_y, half, depth in yards:
        lift = half // 8          # the tilt, proportional to the spread
        left, right = 112 - half, 112 + half
        top, bottom = centre_y - depth // 2, centre_y + depth // 2
        canvas = [(left, top + lift), (right, top),
                  (right, bottom), (left, bottom + lift)]
        draw.polygon(canvas, fill=DARK)
        inset = [(left + 4, top + lift + 4), (right - 4, top + 4),
                 (right - 4, bottom - 4), (left + 4, bottom + lift - 4)]
        draw.polygon(inset, fill=SAIL)
        # The belly of it catches the light along the top and falls into
        # shadow at the foot, so the canvas is not a flat card.
        draw.line((left + 6, top + lift + 7, right - 6, top + 7),
                  fill=SAIL_LIGHT, width=5)
        draw.line((left + 6, bottom + lift - 7, right - 6, bottom - 7),
                  fill=SAIL_DARK, width=4)
        # Two seams down the cloth, following its tilt.
        for fraction in (0.34, 0.67):
            x = round(left + (right - left) * fraction)
            drop = round(lift * (1 - fraction))
            draw.line((x, top + drop + 5, x, bottom + drop - 5),
                      fill=SAIL_DARK, width=2)
        # The yard itself: a spar across the head of the sail, out past
        # the cloth at both ends.
        draw.line((left - 7, top + lift + 1, right + 7, top - 1),
                  fill=WOOD_DARK, width=5)
        draw.line((left - 7, top + lift, right + 7, top - 2),
                  fill=WOOD, width=2)

    # ...and the mast over all of it, head to deck.
    draw.rectangle((105, 0, 119, 230), fill=WOOD_DARK)
    draw.rectangle((107, 0, 113, 230), fill=WOOD)
    draw.line((108, 0, 108, 230), fill=WOOD_LIGHT, width=2)

    # The mast's foot, planted in the deck below the rig.
    draw.rectangle((95, 226, 132, 237), fill=DARK)
    draw.rectangle((100, 223, 127, 232), fill=WOOD)
    draw.line((100, 224, 127, 224), fill=WOOD_LIGHT, width=2)
    return image


# The helm, traced pixel for pixel off the reference rather than
# constructed out of ellipses. The wheel is seen from above and a little
# to starboard: an upright ellipse with the handles swung round it, the
# spokes foreshortened across it, and the pedestal standing behind and
# to one side. That particular angle is the whole character of the
# thing, and it is not what a circle-and-spokes routine arrives at.
HELM_PALETTE = {
    "#": (34, 27, 24, 255),     # the deepest shadow, behind the wheel
    "k": (48, 35, 27, 255),
    "d": (62, 43, 31, 255),
    "b": (79, 55, 37, 255),
    "w": (100, 68, 42, 255),
    "W": (133, 89, 51, 255),
    "L": (158, 106, 58, 255),   # the lit face of the rim and handles
    "G": (193, 151, 69, 255),   # the brass hub
    "g": (233, 196, 99, 255),   # ...and the light on it
}
HELM = """
....................wddd......................
...................bWGLwbw....................
...................dLLLLwb....................
...................dLLLWwb....................
...................dWLLWbddbbbb...............
...................bdWWwdbd###k...............
..............ww....dWLbddkk###kd.............
..............wb....dLLwbbbbk####d............
..............wb....dWLwbbwwd#####bw..........
.......bbw....wb...ddwwdddbwd#######w.........
.....w.LLww...wbbdbLLLLLWWwdd#######kbdb......
......WGLLw...wwWLLLLLLLLLWwwdk#####kWLW......
.....wWLLLwb.bwWLLLLLLLLLLLWwwbd####WGLLbw....
.....Ww.LLWwwwWLLLWwwwwwLLLLWwwbk##wLLLLbw....
.........WLWwWLLLwbddwwwwWLLLWwwd#wLLLLwbw....
........bLLLWLLWwddddLLwdwWLLWWwwbLLLwww......
.........wLLLLWwdddbdLLWbdwWLLWWWLLWbkdw......
..........bLLLwdddbbdLLWbddwWLLWWLWbk#d.......
.........bwLLWbdb...dLLWbdddWLLWwwd####b......
.........wLLLwdd....bLLWbddddLLLWww####w......
........dWLLWbwwb...dLLWwwwbbwLLWww####kw.....
........dLLWwbLLwb..dLLWwwwbbWLLWwwk####b.....
........dLLWddwLLwwddLLWwwbwLwLLWwwwk###b.....
.......dLLLwbkbLLLbddLLWwbWLLwwLLLwwk###b.....
........LLWwb##wLLwLLLLLwWLWwkwLLLwwk###d.....
.......dLLWww##kwLLGGGGGLLWwk#wLLLwwk###b.....
.wbbb.wbLLWww###kLGGGGGGGWwd##kwLLwwbd##b.....
wwGLLddbLLWww##kwGGGGGGGGLwd##kwLLwwwd##bwbbw.
bWLLLLWbLLWwwwwwWGGGgggGGGWb##kwLLwwwbkkdwWww.
bwLLWLWdLLwWLLLWLGGggggGGGWwbbdWLLwwwwwwwLLLWd
wwLLwbbbLLWWLLLWLGGggggGGGWWLLwWLLwWLLLLLGLLLd
..dbdbbbLLW..kkkLGGGgggGGGWWLLwWLLWWLLLLLLLLWd
.......dLLW..###kGGGGGGGGGWWbbdwLLWwwwbbbWLLwb
.......dLLWww###kLGGGGGGGLwb##kwLLwwwbkkbwbbw.
.......bLLWww###dWLGGGGGGWwd###wLLwwwd##bwww..
.......dLLLww##bLLwLGGGGWwwb###wLLwwwd##b.....
.......bLLLWwdbLLLwdwwwbbWLwd#wLLLwwk###b.....
........dLLWwwLLLwwdWLWbdWLLwkWLLLwbk###b.....
........dLLLWwLWb#ddWLWwwwLLWWWLWwwkk###......
........dwLLLbbb##WbWLWwbkbwWWLLWww####W......
........bdLLLWbk##wdWLWwbdkbwLLLWww####w......
.........bwLLLwdk#kdWLWwbdddwLLWwwd####w......
.........wWLLLLbdk#dWLWwbddbLLLLww####w.......
.......bdWLWLLLWbdddWLWwbddwLLLWww####........
.......WLLLLLLLLWwddWLWbddwLLLWWLLb##k........
.....wWLLLWddwLLLWWbbbbbWWLLLWWWLLWb#b........
.....wwLLWbbwwwLLLLLWWWLLLLLWwwwWLLWbb........
......wWWwww..wwWLLLLLLLLLLWwwbkbLLLWww.......
.......bdd.....wdLWLLLLLLLWbddk##bWGGWwb......
.................dkbLLLWwwk##kk##kwGLLwd......
..................wdwWwdkkkkkdk###bLLWbd......
...................dWLwkkdbbddk###kbW.bw......
...................dWLwkkdbbddk####k..........
..................wwLLWbkbwwddk####b..........
..................dLGLWwdbwwddk####d..........
..................dLLLLwdbwwdddk###d..........
..................dWLLLbdbwwbdddk##d..........
...................bWLbbdbwwbdddk##d..........
....................ddddbwwwbdddk##k..........
.............bw....d#dbbwwwwbdddk###w.........
.............bw...wk#kwwwwwwddddk####b........
.............bw..b###kddddddkkkkk####kbw......
.............bwwdkkkkkkkkkkkkkkkkkk####b......
.............bwb#dddddddddddddddddd####kw.....
.............b.b#kkkkkkkkkkkkkkkkkk#####d.....
................dbbbbbbbbbbbbbbbbbbbbbbbb.....
"""


# The traced grid is 46x66, which stood a little tall against the rail
# and the captain beside it. The trace stays the source of truth and the
# wheel is brought down from it, rather than being redrawn smaller and
# losing the angle that was the point of tracing it.
HELM_SCALE = 0.85


def helm_grid() -> Image.Image:
    """The wheel exactly as traced: 46x66, one pixel per character."""
    rows = HELM.strip().splitlines()
    image = Image.new("RGBA", (len(rows[0]), len(rows)), TRANSPARENT)
    pixels = image.load()
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            colour = HELM_PALETTE.get(char)
            if colour is not None:
                pixels[x, y] = colour
    return image


def _snap_to_palette(image: Image.Image) -> Image.Image:
    """Put every pixel back on the palette after a resample.

    A smooth resize is what keeps the spokes and the handles readable at
    a smaller size -- nearest-neighbour drops whole one-pixel spokes --
    but it invents colours between the nine the wheel is made of. So the
    shape comes from the resample and the colours come back from the
    grid, which is what keeps it pixel art rather than a shrunk photo.
    """
    palette = list(HELM_PALETTE.values())
    out = Image.new("RGBA", image.size, TRANSPARENT)
    source, target = image.load(), out.load()
    for y in range(image.height):
        for x in range(image.width):
            red, green, blue, alpha = source[x, y]
            if alpha < 128:
                continue
            target[x, y] = min(
                palette,
                key=lambda c: (c[0] - red) ** 2 + (c[1] - green) ** 2
                + (c[2] - blue) ** 2)
    return out


def helm() -> Image.Image:
    """The ship's wheel, traced and then brought down to size."""
    grid = helm_grid()
    size = (round(grid.width * HELM_SCALE), round(grid.height * HELM_SCALE))
    return _snap_to_palette(grid.resize(size, Image.LANCZOS))


def bowsprit() -> Image.Image:
    """A massive timber spar projecting east from the actual bow edge."""
    image = Image.new("RGBA", (400, 96), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # The generic prop anchor sits at x=200: art begins there, exactly on the
    # rail tile, then runs more than twelve tiles east across open water.
    draw.polygon([(194, 47), (395, 19), (399, 39), (196, 88)], fill=DARK)
    draw.polygon([(198, 50), (393, 23), (395, 36), (200, 82)], fill=WOOD)
    draw.line((200, 52, 392, 25), fill=WOOD_LIGHT, width=4)
    draw.line((199, 80, 393, 35), fill=WOOD_DARK, width=5)
    # A wide reinforced heel makes the spar read as structural, not a rope.
    draw.rectangle((190, 44, 205, 91), fill=WOOD_DARK)
    draw.rectangle((194, 47, 201, 87), fill=WOOD)
    draw.line((195, 48, 200, 48), fill=WOOD_LIGHT, width=2)
    draw.line((395, 20, 399, 38), fill=BRASS, width=3)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("ship_hammock", hammock()),
        ("ship_captain_bed", captain_bed()),
        ("ship_captain_rug", captain_rug()),
        ("ship_round_table", round_table()),
        ("ship_mast_sail", mast_sail()),
        ("ship_helm", helm()),
        ("ship_bowsprit", bowsprit()),
    ):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")
    frames = [captain_chest(stage) for stage in range(4)]
    sheet = Image.new("RGBA", (32 * len(frames), 24), TRANSPARENT)
    for index, frame in enumerate(frames):
        sheet.paste(frame, (index * 32, 0))
    path = OUT / "ship_captain_chest.png"
    sheet.save(path)
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
