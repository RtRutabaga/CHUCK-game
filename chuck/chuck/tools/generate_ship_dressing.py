"""Generate the ship's below-decks and deck dressing in native pixel art.

The captain's bookshelf and writing desk, the galley's butcher block and
stew pot, rope coils, and lashed cargo stacks for the hold and the deck.
The same wood, rope and brass as the ship's existing furniture, so the
new pieces read as fitted out by the same carpenter.
"""

from pathlib import Path

from PIL import Image, ImageDraw


OUT = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "objects"
TRANSPARENT = (0, 0, 0, 0)
DARK = (31, 24, 22, 255)
WOOD_DARK = (63, 42, 29, 255)
WOOD = (112, 74, 43, 255)
WOOD_LIGHT = (151, 102, 57, 255)
WOOD_PALE = (176, 128, 78, 255)
ROPE_DARK = (122, 94, 55, 255)
ROPE = (184, 149, 91, 255)
ROPE_LIGHT = (214, 185, 128, 255)
BRASS = (183, 142, 58, 255)
BRASS_LIGHT = (225, 190, 91, 255)
PARCHMENT = (214, 196, 150, 255)
PARCHMENT_DARK = (170, 148, 104, 255)
IRON_DARK = (28, 28, 32, 255)
IRON = (58, 58, 64, 255)
IRON_LIGHT = (96, 96, 104, 255)
STEEL = (170, 176, 184, 255)


def bookshelf() -> Image.Image:
    """A tall captain's bookcase standing against the cabin's north wall."""
    image = Image.new("RGBA", (32, 46), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Carcass: dark outline, a cornice on top and a plinth at the foot.
    draw.rectangle((1, 3, 30, 45), fill=DARK)
    draw.rectangle((2, 4, 29, 43), fill=WOOD)
    draw.rectangle((0, 0, 31, 4), fill=WOOD_DARK)
    draw.line((1, 1, 30, 1), fill=WOOD_LIGHT)
    draw.rectangle((1, 41, 30, 45), fill=WOOD_DARK)
    draw.line((2, 41, 29, 41), fill=WOOD_LIGHT)
    # Three bays, recessed and shadowed.
    bays = ((6, 15), (18, 27), (30, 39))
    book_colours = (
        ((112, 45, 42, 255), (150, 70, 58, 255)),
        ((52, 72, 96, 255), (80, 104, 130, 255)),
        ((70, 92, 52, 255), (98, 124, 72, 255)),
        ((126, 98, 50, 255), (168, 134, 72, 255)),
        ((84, 52, 84, 255), (116, 78, 112, 255)),
    )
    for shelf, (top, bottom) in enumerate(bays):
        draw.rectangle((4, top, 27, bottom), fill=(40, 28, 22, 255))
        draw.line((4, bottom + 1, 27, bottom + 1), fill=WOOD_LIGHT)
        x = 5
        index = shelf * 2
        while x < 26:
            width = 2 + (index * 7 + shelf) % 2
            height = 6 + (index * 5 + shelf * 3) % 3
            dark, light = book_colours[index % len(book_colours)]
            if shelf == 1 and 14 <= x <= 17:
                # A leaning volume, then a rolled chart lying flat.
                draw.polygon(((x, bottom), (x + 2, bottom),
                              (x + 5, bottom - 6), (x + 3, bottom - 7)),
                             fill=dark)
                draw.line((x + 3, bottom - 6, x + 1, bottom - 1), fill=light)
                x += 6
                continue
            if shelf == 2 and x >= 19:
                draw.rectangle((x, bottom - 3, 26, bottom), fill=PARCHMENT)
                draw.line((x, bottom - 3, 26, bottom - 3),
                          fill=(236, 222, 180, 255))
                draw.rectangle((x - 1, bottom - 3, x, bottom),
                               fill=PARCHMENT_DARK)
                break
            draw.rectangle((x, bottom - height + 1, x + width - 1, bottom),
                           fill=dark)
            draw.line((x, bottom - height + 1, x, bottom), fill=light)
            draw.point((x + width - 1, bottom - height + 3), fill=BRASS)
            x += width + (1 if index % 3 == 0 else 0)
            index += 1
    # A little brass ship's lamp bracket on the cornice's end.
    draw.rectangle((25, 5, 26, 6), fill=BRASS_LIGHT)
    return image


def writing_desk() -> Image.Image:
    """The captain's broad desk, a chart open on it, seen from the front."""
    image = Image.new("RGBA", (48, 32), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Top face, receding away from the viewer.
    draw.rectangle((0, 2, 47, 15), fill=DARK)
    draw.rectangle((1, 3, 46, 13), fill=WOOD_LIGHT)
    draw.line((1, 3, 46, 3), fill=WOOD_PALE)
    for y in (7, 11):
        draw.line((3, y, 44, y), fill=WOOD)
    # Front face with two drawers and brass pulls.
    draw.rectangle((1, 14, 46, 25), fill=WOOD)
    draw.line((1, 14, 46, 14), fill=WOOD_DARK)
    for left in (4, 27):
        draw.rectangle((left, 16, left + 16, 22), fill=WOOD_DARK)
        draw.rectangle((left + 1, 17, left + 15, 21), fill=WOOD)
        draw.rectangle((left + 7, 18, left + 9, 19), fill=BRASS)
        draw.point((left + 7, 18), fill=BRASS_LIGHT)
    # Stout legs, in shadow underneath.
    draw.rectangle((1, 25, 46, 26), fill=WOOD_DARK)
    for x in (1, 42):
        draw.rectangle((x, 26, x + 4, 31), fill=WOOD_DARK)
        draw.line((x, 26, x, 31), fill=WOOD)
    # A chart spread across the top, its corners curling.
    draw.polygon(((6, 4), (27, 4), (28, 12), (5, 12)), fill=PARCHMENT)
    draw.line((6, 4, 27, 4), fill=(236, 222, 180, 255))
    draw.line((5, 12, 28, 12), fill=PARCHMENT_DARK)
    draw.line((9, 9, 13, 7), fill=(112, 84, 56, 255))
    draw.line((13, 7, 18, 8), fill=(112, 84, 56, 255))
    draw.line((18, 8, 23, 6), fill=(112, 84, 56, 255))
    draw.point((22, 10), fill=(140, 44, 40, 255))
    draw.point((21, 10), fill=(140, 44, 40, 255))
    # An inkpot with a quill, and a candle in a brass dish.
    draw.rectangle((33, 7, 36, 11), fill=IRON_DARK)
    draw.point((34, 7), fill=IRON_LIGHT)
    draw.line((35, 7, 39, 0), fill=(226, 222, 210, 255))
    draw.line((36, 7, 40, 1), fill=(190, 186, 176, 255))
    draw.ellipse((40, 9, 45, 12), fill=BRASS)
    draw.rectangle((42, 3, 43, 10), fill=(226, 214, 180, 255))
    draw.point((42, 2), fill=(250, 214, 110, 255))
    draw.point((42, 1), fill=(255, 244, 190, 255))
    return image


def butcher_block() -> Image.Image:
    """The galley's thick end-grain block, a cleaver bitten into it."""
    image = Image.new("RGBA", (26, 28), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    # Top face: end grain.
    draw.rectangle((1, 6, 24, 15), fill=DARK)
    draw.rectangle((2, 7, 23, 13), fill=WOOD_PALE)
    for x in (7, 13, 19):
        draw.arc((x - 4, 8, x + 3, 13), 0, 360, fill=WOOD_LIGHT)
    draw.line((3, 10, 22, 11), fill=WOOD_LIGHT)
    # Deep front face and short legs.
    draw.rectangle((2, 14, 23, 23), fill=WOOD)
    draw.line((2, 14, 23, 14), fill=WOOD_DARK)
    draw.line((2, 18, 23, 18), fill=WOOD_DARK)
    draw.rectangle((2, 23, 5, 27), fill=WOOD_DARK)
    draw.rectangle((20, 23, 23, 27), fill=WOOD_DARK)
    # The cleaver: blade sunk into the top, handle raised.
    draw.polygon(((9, 1), (16, 1), (16, 9), (9, 10)), fill=STEEL)
    draw.line((9, 1, 16, 1), fill=(224, 228, 232, 255))
    draw.line((9, 10, 16, 9), fill=IRON)
    draw.rectangle((16, 3, 22, 5), fill=WOOD_DARK)
    draw.line((16, 3, 22, 3), fill=WOOD)
    return image


def stew_pot() -> Image.Image:
    """A big black iron pot on three short legs, something brown in it."""
    image = Image.new("RGBA", (26, 24), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.line((5, 18, 3, 23), fill=IRON_DARK, width=2)
    draw.line((20, 18, 22, 23), fill=IRON_DARK, width=2)
    draw.line((13, 20, 13, 23), fill=IRON_DARK, width=2)
    draw.ellipse((1, 5, 24, 22), fill=IRON_DARK)
    draw.ellipse((2, 6, 23, 20), fill=IRON)
    draw.arc((4, 8, 12, 18), 120, 240, fill=IRON_LIGHT)
    draw.ellipse((2, 3, 23, 10), fill=IRON_DARK)
    draw.ellipse((4, 4, 21, 9), fill=(104, 70, 42, 255))
    draw.point((9, 6), fill=(150, 108, 64, 255))
    draw.point((15, 7), fill=(150, 108, 64, 255))
    draw.point((12, 5), fill=(172, 128, 76, 255))
    # A wooden ladle leaning out of it.
    draw.line((15, 6, 23, 0), fill=WOOD_LIGHT, width=2)
    draw.point((23, 0), fill=WOOD_PALE)
    # Iron ears.
    draw.rectangle((0, 8, 1, 10), fill=IRON_DARK)
    draw.rectangle((24, 8, 25, 10), fill=IRON_DARK)
    return image


def rope_coil() -> Image.Image:
    """A flat coil of line lying on the planks."""
    image = Image.new("RGBA", (18, 12), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 1, 17, 11), fill=ROPE_DARK)
    draw.ellipse((1, 1, 16, 10), fill=ROPE)
    draw.ellipse((3, 3, 14, 8), fill=ROPE_DARK)
    draw.ellipse((4, 3, 13, 8), fill=ROPE)
    draw.ellipse((6, 4, 11, 7), fill=ROPE_DARK)
    draw.arc((1, 1, 16, 10), 190, 330, fill=ROPE_LIGHT)
    draw.arc((4, 3, 13, 8), 190, 330, fill=ROPE_LIGHT)
    # The loose end trailing off.
    draw.line((15, 8, 17, 11), fill=ROPE)
    return image


def cargo_stack() -> Image.Image:
    """Two crates and a sack, lashed together with rope against the roll."""
    image = Image.new("RGBA", (28, 38), TRANSPARENT)
    draw = ImageDraw.Draw(image)

    def crate(left, top, right, bottom):
        draw.rectangle((left, top, right, bottom), fill=DARK)
        draw.rectangle((left + 1, top + 1, right - 1, top + 4),
                       fill=WOOD_LIGHT)
        draw.line((left + 1, top + 1, right - 1, top + 1), fill=WOOD_PALE)
        draw.rectangle((left + 1, top + 5, right - 1, bottom - 1), fill=WOOD)
        draw.line((left + 1, top + 5, right - 1, top + 5), fill=WOOD_DARK)
        middle = (top + 5 + bottom) // 2
        draw.line((left + 2, middle, right - 2, middle), fill=WOOD_DARK)
        draw.line((left + 2, top + 6, right - 2, bottom - 2),
                  fill=WOOD_DARK)

    crate(1, 17, 26, 37)     # the big one on the planks
    crate(5, 4, 22, 18)      # a smaller one on top
    # A sack slumped against the top crate's side.
    draw.ellipse((18, 7, 27, 18), fill=(122, 104, 72, 255))
    draw.ellipse((19, 8, 25, 15), fill=(160, 140, 100, 255))
    draw.line((21, 7, 23, 5), fill=ROPE_DARK, width=2)
    # Lashing: one line over the top and down both faces.
    draw.line((13, 4, 13, 37), fill=ROPE, width=1)
    draw.line((14, 4, 14, 37), fill=ROPE_DARK, width=1)
    draw.line((1, 27, 26, 27), fill=ROPE, width=1)
    draw.line((5, 12, 22, 12), fill=ROPE, width=1)
    draw.rectangle((12, 26, 15, 28), fill=ROPE_LIGHT)
    return image


def deck_grating() -> Image.Image:
    """A hatch grating let into the deck between the masts.

    A thick frame of planks round a lattice of crossed battens, with the
    dark of the hold showing through every square. Flat on the deck and
    walked over; seen at the same slight angle as the planks, so the
    frame's far edge catches the light and its near edge is in shadow.
    """
    width, height = 160, 60
    image = Image.new("RGBA", (width, height), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    hold = (26, 18, 14, 255)
    hold_deep = (14, 10, 8, 255)
    # The frame: outline, then planks, lit along the far side.
    draw.rectangle((0, 0, width - 1, height - 1), fill=DARK)
    draw.rectangle((1, 1, width - 2, height - 2), fill=WOOD)
    draw.rectangle((1, 1, width - 2, 4), fill=WOOD_LIGHT)
    draw.line((2, 1, width - 3, 1), fill=WOOD_PALE)
    draw.rectangle((1, height - 5, width - 2, height - 2), fill=WOOD_DARK)
    draw.rectangle((1, 1, 4, height - 2), fill=WOOD_LIGHT)
    draw.rectangle((width - 5, 1, width - 2, height - 2), fill=WOOD_DARK)
    # Grain along the frame.
    for x in range(8, width - 8, 13):
        draw.line((x, 2, x + 5, 2), fill=WOOD)
        draw.line((x + 4, height - 3, x + 9, height - 3), fill=DARK)
    # The lattice: square holes in a grid of battens.
    left, top = 6, 6
    right, bottom = width - 7, height - 7
    draw.rectangle((left, top, right, bottom), fill=WOOD)
    hole, batten = 4, 2
    step = hole + batten
    for y in range(top + 1, bottom - hole + 2, step):
        for x in range(left + 1, right - hole + 2, step):
            draw.rectangle((x, y, x + hole - 1, y + hole - 1), fill=hold)
            # Deeper at the bottom of each hole, where the batten above
            # shades it.
            draw.line((x, y, x + hole - 1, y), fill=hold_deep)
            # The lit top edge of the batten below the hole.
            draw.line((x, y + hole, x + hole - 1, y + hole), fill=WOOD_LIGHT)
    draw.line((left, top - 1, right, top - 1), fill=DARK)
    draw.line((left, bottom + 1, right, bottom + 1), fill=WOOD_LIGHT)
    return image


SPRITES = {
    "ship_bookshelf": bookshelf,
    "ship_writing_desk": writing_desk,
    "ship_butcher_block": butcher_block,
    "ship_stew_pot": stew_pot,
    "ship_rope_coil": rope_coil,
    "ship_cargo_stack": cargo_stack,
    "ship_deck_grating": deck_grating,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, draw in SPRITES.items():
        path = OUT / f"{name}.png"
        draw().save(path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
