"""Generate Waterdeep's harbour dressing, drawn to the game's vantage.

The camera in this game hangs south of everything, above it, looking
north and down. That one fact decides what every piece here shows and,
more importantly, what it must never show:

* **Tops are seen.** A bollard's cap, the inside of a rowboat, the soil
  in a window box: all of them read from above first.
* **South faces are seen; north faces never are.** A pier stands above
  the water, so wherever water lies *south* of the planks we see the
  pier's front: the ends of the deck planks, the dark gap under the
  deck, and the pilings going down to the waterline. Wherever water
  lies *north* of the planks we see nothing at all -- that face points
  away from us. The same goes for a boat: its near side is a band of
  hull under the gunwale, its far side is hidden behind what is inside.
* **East and west faces are edges, not surfaces.** Looking straight
  north, a side face is seen end-on. What an east edge does show is the
  shadow the deck throws onto the water beside it, because the light in
  Waterdeep comes from the upper left, like everywhere else in the game.
* **Anything flat against a wall faces us.** A shop sign is hung
  parallel to the facade on a short bracket: a board sticking straight
  out of a wall is seen edge-on from here, which is to say as a line.
  Window boxes sit under the sill on the same plane.
* **Things strung between two points sag toward the viewer's bottom of
  the screen,** because down is down the screen too. A mooring line
  dips below the straight line from post to bow; a washing line bellies
  between its two walls.

Two sheets, like the tileset: evening for the opening and midday for the
return, so the wood of a pier face is the wood of the planks above it.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
CLEAR = (0, 0, 0, 0)

ERAS = {
    # Sampled from docks.png and docks_midday.png: plank light/dark, and
    # the tavern facade's stone for the lamps' plinths.
    "": {
        "plank": (150, 112, 74), "plank_dark": (108, 76, 46),
        "plank_deep": (70, 52, 36), "piling": (84, 62, 42),
        "piling_lit": (122, 92, 60), "under": (10, 14, 26, 190),
        "ripple": (118, 140, 176, 200), "shadow": (0, 0, 10, 90),
    },
    "_midday": {
        "plank": (174, 132, 82), "plank_dark": (126, 88, 50),
        "plank_deep": (84, 60, 38), "piling": (98, 72, 46),
        "piling_lit": (146, 108, 68), "under": (6, 34, 42, 170),
        "ripple": (116, 190, 184, 210), "shadow": (0, 20, 26, 80),
    },
}

OUTLINE = (40, 30, 24, 255)
IRON = (58, 58, 66, 255)
IRON_LIT = (110, 112, 122, 255)
ROPE = (184, 149, 91, 255)
ROPE_DARK = (130, 102, 62, 255)
WOOD_DARK = (74, 52, 34, 255)
WOOD = (118, 84, 52, 255)
WOOD_LIT = (158, 116, 72, 255)
HULL_PAINT = (62, 92, 110, 255)
HULL_PAINT_DARK = (40, 62, 76, 255)
LAMP_GLASS_LIT = (255, 214, 120, 255)
LAMP_GLOW = (255, 190, 90)
LAMP_GLASS_DARK = (86, 96, 104, 255)


def _rgba(colour):
    return colour if len(colour) == 4 else colour + (255,)


# ----------------------------------------------------------------------
# The pier's edges.
# ----------------------------------------------------------------------
def pier_face(era: str, with_shadow: bool = False) -> Image.Image:
    """The front of the pier, drawn on the water tile south of the deck.

    Top to bottom: the ends of the deck planks (three pixels of deck
    thickness, lit along the top where the deck surface turns the
    corner), the dark water in the shade under the deck, one piling
    going down through it, and the ripple where the piling meets the
    surface. Below the ripple the tile is left clear so the water's own
    animation carries on.
    """
    p = ERAS[era]
    image = Image.new("RGBA", (16, 16), CLEAR)
    draw = ImageDraw.Draw(image)
    # Deck thickness: plank ends.
    draw.rectangle((0, 0, 15, 3), fill=_rgba(p["plank_dark"]))
    draw.line((0, 0, 15, 0), fill=_rgba(p["plank"]))
    for x in (4, 11):
        draw.line((x, 1, x, 3), fill=_rgba(p["plank_deep"]))
    # The shade under the deck.
    draw.rectangle((0, 4, 15, 9), fill=p["under"])
    # One piling per tile, off-centre so a row of them is not a comb.
    draw.rectangle((9, 4, 12, 11), fill=_rgba(p["piling"]))
    draw.line((9, 4, 9, 11), fill=_rgba(p["piling_lit"]))
    draw.line((12, 4, 12, 11), fill=_rgba(p["plank_deep"]))
    # Waterline: the ripple round the piling and a line of it along the
    # face.
    draw.line((0, 10, 15, 10), fill=p["ripple"])
    draw.line((7, 12, 14, 12), fill=p["ripple"])
    if with_shadow:
        _shadow_column(image, p)
    return image


def _shadow_column(image, p) -> None:
    layer = Image.new("RGBA", image.size, CLEAR)
    draw = ImageDraw.Draw(layer)
    r, g, b, a = p["shadow"]
    for x, alpha in ((0, a), (1, a * 2 // 3), (2, a // 3)):
        draw.line((x, 0, x, 15), fill=(r, g, b, alpha))
    image.alpha_composite(layer)


def pier_shadow(era: str) -> Image.Image:
    """The deck's shadow on the water east of it. There is no face to
    see on that side: it points along our line of sight."""
    image = Image.new("RGBA", (16, 16), CLEAR)
    _shadow_column(image, ERAS[era])
    return image


def pier_corner(era: str) -> Image.Image:
    """Water diagonally south-east of a deck corner: where the face's
    shade and the east shadow meet, a small corner of dark."""
    p = ERAS[era]
    image = Image.new("RGBA", (16, 16), CLEAR)
    layer = Image.new("RGBA", (16, 16), CLEAR)
    draw = ImageDraw.Draw(layer)
    r, g, b, a = p["shadow"]
    draw.rectangle((0, 0, 1, 9), fill=(r, g, b, a))
    draw.point((2, 0), fill=(r, g, b, a // 2))
    image.alpha_composite(layer)
    return image


# ----------------------------------------------------------------------
# Mooring posts.
# ----------------------------------------------------------------------
def bollard(offset_x: int) -> Image.Image:
    """A mooring post: a stout wooden post, iron-banded, rope round it.

    Seen from above and in front, so the cap is an ellipse on top of a
    cylinder, lit from the west. Knee-high to a docker, which is taller
    than Chuck. `offset_x` moves the post off the tile's centre toward
    the water on edges that are not the south one.
    """
    image = Image.new("RGBA", (16, 18), CLEAR)
    draw = ImageDraw.Draw(image)
    cx = 7 + offset_x
    # A contact shadow on the deck, falling down and right.
    draw.ellipse((cx - 3, 14, cx + 6, 17), fill=(20, 14, 10, 90))
    # The post.
    draw.rectangle((cx - 3, 4, cx + 3, 15), fill=OUTLINE)
    draw.rectangle((cx - 2, 4, cx + 2, 15), fill=WOOD)
    draw.line((cx - 2, 5, cx - 2, 15), fill=WOOD_LIT)
    draw.line((cx + 2, 5, cx + 2, 15), fill=WOOD_DARK)
    # Its top, seen from above: a paler end grain ellipse.
    draw.ellipse((cx - 3, 1, cx + 3, 6), fill=OUTLINE)
    draw.ellipse((cx - 2, 2, cx + 2, 5), fill=WOOD_LIT)
    draw.point((cx, 3), fill=WOOD)
    # An iron band, and a few turns of rope under it.
    draw.line((cx - 3, 7, cx + 3, 7), fill=IRON)
    draw.point((cx - 2, 7), fill=IRON_LIT)
    for y in (10, 12):
        draw.line((cx - 3, y, cx + 3, y), fill=ROPE)
        draw.point((cx + 3, y), fill=ROPE_DARK)
    return image


# ----------------------------------------------------------------------
# A rowboat, moored.
# ----------------------------------------------------------------------
BOAT_W, BOAT_H = 56, 44


def rowboat(era: str, line: bool = True) -> Image.Image:
    """A rowboat lying east-west on the water, tied up to the post above.

    We look down into it: the inside planking and the thwarts are the
    boat. Its near (south) side shows as a band of painted hull under
    the gunwale; its far (north) side is only the gunwale's rim, because
    the outside of that planking faces away from us. The waterline runs
    along the near hull. The line from the bow ring runs up the screen
    to the post, sagging below the straight line between them.
    """
    p = ERAS[era]
    image = Image.new("RGBA", (BOAT_W, BOAT_H), CLEAR)
    draw = ImageDraw.Draw(image)
    top, bottom = 22, 38
    left, right = 4, 52
    # The hull's outline, pointed at the bow (west), a transom astern.
    hull = [(left, 30), (12, top), (right - 2, top + 1), (right, 26),
            (right, 34), (right - 2, bottom), (12, bottom), (left, 30)]
    draw.polygon(hull, fill=OUTLINE)
    # The near side of the hull: painted planks, visible below the rim.
    near = [(left + 2, 31), (12, 35), (right - 2, 35), (right - 1, 33),
            (right - 1, 37), (13, 37)]
    draw.polygon(near, fill=HULL_PAINT)
    draw.line((12, 36, right - 3, 36), fill=HULL_PAINT_DARK)
    # The inside, seen from above.
    inside = [(left + 3, 30), (13, top + 3), (right - 3, top + 3),
              (right - 3, 32), (13, 33)]
    draw.polygon(inside, fill=WOOD)
    for y in (26, 29):
        draw.line((14, y, right - 4, y), fill=WOOD_DARK)
    # The gunwale rim all the way round, lit on its far edge.
    draw.line((12, top + 1, right - 2, top + 1), fill=WOOD_LIT)
    draw.line((left + 1, 30, 12, top + 1), fill=WOOD_LIT)
    draw.line((12, 34, right - 2, 34), fill=WOOD_DARK)
    draw.line((left + 1, 30, 12, 34), fill=WOOD_DARK)
    # Two thwarts across, and the oars shipped along the inside.
    for x in (22, 38):
        draw.rectangle((x, top + 2, x + 3, 33), fill=WOOD_LIT)
        draw.line((x + 3, top + 2, x + 3, 33), fill=WOOD_DARK)
    draw.line((16, 27, 48, 25), fill=(196, 160, 104, 255))
    draw.line((44, 24, 50, 23), fill=(196, 160, 104, 255))
    # Waterline: ripples along the near hull and off the stern.
    ripple = p["ripple"]
    draw.line((10, 39, right - 1, 39), fill=ripple)
    draw.line((right + 1, 32, right + 2, 36), fill=ripple)
    draw.line((2, 32, 6, 36), fill=ripple)
    if not line:
        return image
    # The mooring line: from the bow ring up to the post's foot above,
    # dipping below the straight line between them.
    bow = (9, 27)
    # Where the post's foot lands when the boat is anchored two tiles
    # south of the post's tile (see tools/waterdeep_harbour_dressing.py).
    post = (27, 8)
    for step in range(21):
        t = step / 20
        x = bow[0] + (post[0] - bow[0]) * t
        y = bow[1] + (post[1] - bow[1]) * t + math.sin(t * math.pi) * 4
        draw.point((round(x), round(y)), fill=ROPE)
        if step % 4 == 0:
            draw.point((round(x) + 1, round(y)), fill=ROPE_DARK)
    draw.ellipse((bow[0] - 1, bow[1] - 1, bow[0] + 1, bow[1] + 1),
                 outline=IRON_LIT)
    return image


WEST_BOAT_W, WEST_BOAT_H = 24, 52


def rowboat_west(era: str) -> Image.Image:
    """The rowboat lying alongside a pier's west edge, bow to the north.

    A boat tied up to a pier lies along it, which is what the opening
    cutscene shows -- the boat parallel to the quay by the posts where
    Chuck wakes. Along a west edge that means north-south, and the vantage
    changes what of it we see. We still look down into it: the inside
    planking, the thwarts across, the oars shipped along it. Its bow
    points away up the screen, so it narrows to a point with nothing
    below it. Its stern faces us, so the transom is the one outside face
    on show, a band of paint across the bottom. Its long sides point along
    our line of sight and show only as the gunwale's rims, the west one
    lit. The bow line runs from the ring down the pier side to the post's
    foot. Drawn to be anchored on the water a tile west and a row south of
    the post (see tools/waterdeep_harbour_dressing.py).
    """
    p = ERAS[era]
    image = Image.new("RGBA", (WEST_BOAT_W, WEST_BOAT_H), CLEAR)
    draw = ImageDraw.Draw(image)
    # The hull's outline: pointed bow at the top, square transom below.
    outline = [(12, 3), (19, 13), (20, 16), (20, 44), (19, 47), (5, 47),
               (4, 44), (4, 16), (5, 13)]
    draw.polygon(outline, fill=OUTLINE)
    # The transom, the stern's outside face, toward us.
    draw.rectangle((5, 41, 19, 46), fill=HULL_PAINT)
    draw.line((5, 46, 19, 46), fill=HULL_PAINT_DARK)
    draw.line((6, 41, 18, 41), fill=WOOD_DARK)
    # The inside, seen from above.
    inside = [(12, 6), (17, 14), (18, 17), (18, 40), (6, 40), (6, 17),
              (7, 14)]
    draw.polygon(inside, fill=WOOD)
    for x in (9, 15):
        draw.line((x, 15, x, 39), fill=WOOD_DARK)
    # Gunwale rims: lit on the west, in shade on the east.
    draw.line((5, 16, 5, 40), fill=WOOD_LIT)
    draw.line((5, 14, 11, 4), fill=WOOD_LIT)
    draw.line((19, 16, 19, 40), fill=WOOD_DARK)
    draw.line((13, 4, 19, 14), fill=WOOD_DARK)
    # Two thwarts across, and the oars shipped along the inside.
    for y in (20, 31):
        draw.rectangle((6, y, 18, y + 2), fill=WOOD_LIT)
        draw.line((6, y + 2, 18, y + 2), fill=WOOD_DARK)
    draw.line((8, 17, 8, 38), fill=(196, 160, 104, 255))
    draw.line((10, 36, 10, 39), fill=(196, 160, 104, 255))
    # Waterline: ripples off the stern and down the open-water side.
    ripple = p["ripple"]
    draw.line((5, 49, 19, 49), fill=ripple)
    for y in (18, 27, 36):
        draw.line((2, y, 2, y + 3), fill=ripple)
    # The bow line: from the ring down the pier side to the post's foot.
    bow = (14, 9)
    post = (23, 33)
    for step in range(17):
        t = step / 16
        x = bow[0] + (post[0] - bow[0]) * t + math.sin(t * math.pi) * 1.5
        y = bow[1] + (post[1] - bow[1]) * t
        draw.point((round(x), round(y)), fill=ROPE)
        if step % 4 == 0:
            draw.point((round(x), round(y) + 1), fill=ROPE_DARK)
    draw.ellipse((bow[0] - 1, bow[1] - 1, bow[0] + 1, bow[1] + 1),
                 outline=IRON_LIT)
    return image


# ----------------------------------------------------------------------
# Street and shopfront.
# ----------------------------------------------------------------------
def lamp_post(lit: bool) -> Image.Image:
    """An iron street lamp: a stone foot, a tall post, a glass lantern.

    The lantern is a box seen from the front with its roof seen from
    above. Lit for the opening's evening, with a warm glow drawn round
    the glass; dark glass at midday.
    """
    width, height = 18, 46
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    cx = 8
    if lit:
        halo = Image.new("RGBA", (width, height), CLEAR)
        hd = ImageDraw.Draw(halo)
        for radius, alpha in ((8, 36), (6, 60), (4, 90)):
            hd.ellipse((cx - radius, 11 - radius, cx + radius + 1,
                        11 + radius), fill=LAMP_GLOW + (alpha,))
        image.alpha_composite(halo)
    # Stone foot, seen from above and in front.
    draw.rectangle((cx - 4, 40, cx + 4, 45), fill=(70, 68, 76, 255))
    draw.rectangle((cx - 4, 40, cx + 4, 41), fill=(118, 116, 124, 255))
    draw.ellipse((cx - 5, 43, cx + 7, 46), fill=(10, 10, 16, 70))
    # The post.
    draw.rectangle((cx - 1, 17, cx + 1, 40), fill=IRON)
    draw.line((cx - 1, 17, cx - 1, 40), fill=IRON_LIT)
    draw.rectangle((cx - 2, 28, cx + 2, 29), fill=IRON)
    # The lantern: roof, glass, base.
    draw.polygon(((cx - 5, 5), (cx, 1), (cx + 5, 5)), fill=IRON)
    draw.line((cx - 5, 5, cx, 1), fill=IRON_LIT)
    draw.rectangle((cx - 4, 5, cx + 4, 15), fill=(30, 30, 36, 255))
    glass = LAMP_GLASS_LIT if lit else LAMP_GLASS_DARK
    draw.rectangle((cx - 3, 6, cx + 3, 14), fill=glass)
    draw.line((cx, 6, cx, 14), fill=(30, 30, 36, 255))
    if lit:
        draw.point((cx - 2, 8), fill=(255, 250, 220, 255))
    else:
        draw.point((cx - 2, 7), fill=(160, 170, 178, 255))
    draw.rectangle((cx - 3, 15, cx + 3, 17), fill=IRON)
    return image


SIGNS = ("bread", "fish", "barrel", "anvil", "potion")


def shop_sign(kind: str) -> Image.Image:
    """A board hung flat against the facade from a short bracket.

    Parallel to the wall, because that is the only way a hanging sign
    can be read from where we stand; the bracket that holds it out from
    the stone is seen almost end-on, as a stub.
    """
    image = Image.new("RGBA", (16, 16), CLEAR)
    draw = ImageDraw.Draw(image)
    # Bracket stub and the two chains.
    draw.rectangle((1, 1, 14, 2), fill=IRON)
    draw.point((1, 1), fill=IRON_LIT)
    draw.line((3, 3, 3, 4), fill=IRON_LIT)
    draw.line((12, 3, 12, 4), fill=IRON_LIT)
    # The board, with a shadow on the wall below and right of it.
    draw.rectangle((2, 6, 14, 15), fill=(30, 22, 16, 110))
    draw.rectangle((1, 5, 13, 14), fill=OUTLINE)
    draw.rectangle((2, 6, 12, 13), fill=WOOD_LIT)
    draw.line((2, 13, 12, 13), fill=WOOD)
    if kind == "bread":
        draw.ellipse((3, 7, 11, 12), fill=(196, 138, 70, 255))
        draw.line((5, 8, 6, 10), fill=(150, 96, 46, 255))
        draw.line((8, 8, 9, 10), fill=(150, 96, 46, 255))
    elif kind == "fish":
        draw.ellipse((3, 8, 9, 11), fill=(96, 136, 158, 255))
        draw.polygon(((9, 9), (12, 7), (12, 12)), fill=(96, 136, 158, 255))
        draw.point((4, 9), fill=OUTLINE)
    elif kind == "barrel":
        draw.ellipse((4, 7, 10, 13), fill=(128, 88, 50, 255))
        draw.line((4, 9, 10, 9), fill=IRON)
        draw.line((4, 11, 10, 11), fill=IRON)
    elif kind == "anvil":
        draw.rectangle((3, 8, 11, 9), fill=IRON)
        draw.polygon(((3, 8), (1, 8), (3, 10)), fill=IRON)
        draw.rectangle((6, 10, 8, 12), fill=IRON)
        draw.rectangle((4, 12, 10, 12), fill=IRON)
    else:  # potion
        draw.rectangle((6, 7, 8, 8), fill=(200, 200, 210, 255))
        draw.ellipse((4, 8, 10, 13), fill=(140, 70, 170, 255))
        draw.point((5, 9), fill=(230, 200, 240, 255))
    return image


def window_box(variant: int) -> Image.Image:
    """A planter under a window sill, flowers up out of it.

    Sits on the facade's plane: its front face is a plank box, its top
    is soil with the plants growing out of it toward us and up.
    """
    image = Image.new("RGBA", (16, 16), CLEAR)
    draw = ImageDraw.Draw(image)
    blooms = (((230, 76, 96), (255, 170, 184)),
              ((236, 196, 64), (255, 236, 150)),
              ((170, 110, 220), (220, 190, 250)))[variant % 3]
    # Leaves and flowers first; the box's lip goes over their stems.
    for index, x in enumerate(range(3, 14, 2)):
        top = 6 + (index * 5 + variant) % 3
        draw.line((x, top + 2, x, 11), fill=(58, 110, 58, 255))
        draw.point((x - 1, top + 3), fill=(80, 140, 70, 255))
        colour, lit = blooms
        draw.point((x, top), fill=colour + (255,))
        draw.point((x, top + 1), fill=colour + (255,))
        draw.point((x + 1, top), fill=lit + (255,))
    # The box.
    draw.rectangle((1, 11, 14, 15), fill=OUTLINE)
    draw.rectangle((2, 12, 13, 14), fill=WOOD)
    draw.line((2, 12, 13, 12), fill=WOOD_LIT)
    draw.line((2, 11, 13, 11), fill=(60, 40, 28, 255))   # soil seen above
    return image


def washing_line(width_tiles: int) -> Image.Image:
    """A line strung across an alley between two eaves, washing on it.

    Seen from the front, so the line sags down the screen between its
    two walls, and the washing hangs from it facing us. Drawn at eave
    height: it is overhead, and fades like an awning when anyone walks
    under it.
    """
    width, height = width_tiles * 16, 44
    image = Image.new("RGBA", (width, height), CLEAR)
    draw = ImageDraw.Draw(image)
    # Iron hooks in the two walls.
    draw.rectangle((0, 5, 2, 7), fill=IRON)
    draw.rectangle((width - 3, 5, width - 1, 7), fill=IRON)

    def line_y(x):
        t = x / (width - 1)
        return 6 + math.sin(t * math.pi) * 7

    for x in range(1, width - 1):
        draw.point((x, round(line_y(x))), fill=(200, 196, 180, 255))
    colours = ((196, 62, 62), (222, 216, 196), (72, 104, 160),
               (210, 180, 90), (236, 232, 222), (120, 150, 90))
    x = 8
    index = 0
    while x < width - 14:
        colour = colours[index % len(colours)]
        wide = 8 + (index * 3) % 5
        tall = 10 + (index * 7) % 8
        y = round(line_y(x + wide // 2))
        draw.rectangle((x, y, x + wide, y + tall), fill=colour + (255,))
        draw.line((x, y + tall, x + wide, y + tall),
                  fill=tuple(max(0, c - 50) for c in colour) + (255,))
        draw.line((x + wide, y, x + wide, y + tall),
                  fill=tuple(max(0, c - 34) for c in colour) + (255,))
        # Pegs.
        draw.point((x + 1, y - 1), fill=(150, 120, 80, 255))
        draw.point((x + wide - 1, y - 1), fill=(150, 120, 80, 255))
        if index % 3 == 1:      # a shirt: sleeves
            draw.rectangle((x - 2, y + 1, x, y + 5), fill=colour + (255,))
            draw.rectangle((x + wide, y + 1, x + wide + 2, y + 5),
                           fill=colour + (255,))
        x += wide + 6 + (index * 5) % 4
        index += 1
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for era in ERAS:
        pier_face(era).save(OUT / f"pier_face{era}.png")
        pier_face(era, with_shadow=True).save(OUT / f"pier_face_shadow{era}.png")
        pier_shadow(era).save(OUT / f"pier_shadow{era}.png")
        pier_corner(era).save(OUT / f"pier_corner{era}.png")
        rowboat(era).save(OUT / f"harbour_rowboat{era}.png")
        rowboat_west(era).save(OUT / f"harbour_rowboat_west{era}.png")
    bollard(0).save(OUT / "harbour_bollard.png")
    bollard(-4).save(OUT / "harbour_bollard_west.png")
    lamp_post(True).save(OUT / "waterdeep_lamp.png")
    lamp_post(False).save(OUT / "waterdeep_lamp_midday.png")
    for kind in SIGNS:
        shop_sign(kind).save(OUT / f"shop_sign_{kind}.png")
    for variant in range(3):
        window_box(variant).save(OUT / f"window_box_{variant + 1}.png")
    washing_line(6).save(OUT / "washing_line_6.png")
    washing_line(4).save(OUT / "washing_line_4.png")
    print(f"Wrote Waterdeep's harbour dressing to {OUT}")


if __name__ == "__main__":
    main()
