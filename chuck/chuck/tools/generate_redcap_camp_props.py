"""Generate the redcap camp's oversized gear.

Everything here belongs to gnome-sized fey, so every piece is drawn to
dwarf one-foot-tall Chuck: a boot stands as tall as he does, a cooking
pot is a building, and a planted sickle is a gate he walks under. The
camp sells the phase's scale premise before a single redcap notices him.
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
TRANSPARENT = (0, 0, 0, 0)

LEATHER_DARK = (48, 32, 26, 255)
LEATHER = (78, 52, 38, 255)
LEATHER_LIT = (106, 74, 52, 255)
IRON_DARK = (38, 40, 47, 255)
IRON = (72, 76, 86, 255)
IRON_LIT = (124, 130, 142, 255)
RED_CLOTH = (128, 34, 38, 255)
RED_LIT = (170, 56, 54, 255)
WOOD_DARK = (52, 38, 30, 255)
WOOD = (88, 64, 44, 255)
SHADOW = (10, 26, 24, 150)


def _shadow(draw, box):
    """Every camp piece gets a planted ellipse so it sits on the ground."""
    draw.ellipse(box, fill=SHADOW)


def boot(variant: int) -> Image.Image:
    """A kicked-off redcap boot, as tall as Chuck and twice as wide."""
    image = Image.new("RGBA", (24, 20), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    lean = (0, 1, -1)[variant]
    _shadow(draw, (2, 15, 22, 19))
    # Sole, then the slumped leather shaft leaning as it fell.
    draw.rectangle((3, 14, 21, 17), fill=IRON_DARK)
    draw.polygon(((4, 15), (20, 15), (18 + lean, 4), (9 + lean, 4)),
                 fill=LEATHER)
    draw.polygon(((4, 15), (9, 15), (9 + lean, 4), (9 + lean, 4)),
                 fill=LEATHER_DARK)
    draw.line((11 + lean, 5, 18, 14), fill=LEATHER_LIT)
    # The cuff flops open; the buckle catches the light.
    draw.ellipse((8 + lean, 2, 19 + lean, 7), fill=LEATHER_DARK)
    draw.ellipse((10 + lean, 3, 17 + lean, 6), fill=(24, 16, 14, 255))
    draw.rectangle((6, 10, 9, 12), fill=IRON_LIT)
    return image


def cauldron() -> Image.Image:
    """The camp pot: a black iron belly on stones, still steaming."""
    image = Image.new("RGBA", (28, 26), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    _shadow(draw, (2, 21, 26, 25))
    for x in (3, 12, 20):                       # the fire stones
        draw.ellipse((x, 19, x + 6, 24), fill=(58, 56, 52, 255))
    draw.ellipse((4, 6, 24, 23), fill=IRON_DARK)
    draw.ellipse((6, 7, 22, 20), fill=IRON)
    draw.ellipse((4, 4, 24, 10), fill=IRON_DARK)   # the rim
    draw.ellipse((6, 5, 22, 9), fill=(28, 22, 20, 255))
    draw.arc((7, 5, 21, 9), 200, 340, fill=IRON_LIT)
    draw.arc((2, 1, 26, 12), 200, 340, fill=IRON)  # the swinging handle
    # A little green broth showing over the rim, because they are cooking.
    draw.ellipse((9, 6, 19, 8), fill=(84, 112, 56, 255))
    return image


def sickle() -> Image.Image:
    """A sickle driven into the earth --- a doorway at Chuck's scale."""
    image = Image.new("RGBA", (22, 34), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    _shadow(draw, (4, 29, 18, 33))
    draw.rectangle((9, 11, 12, 31), fill=WOOD)
    draw.line((9, 12, 9, 30), fill=WOOD_DARK)
    draw.rectangle((8, 22, 13, 26), fill=LEATHER)   # the grip binding
    # The blade is a crescent: one filled disc with a second punched out
    # of it, leaving a hook that is thick at the heel and tapers to a
    # point. It sweeps left over the handle, high above Chuck's head.
    blade = Image.new("RGBA", image.size, TRANSPARENT)
    edge = ImageDraw.Draw(blade)
    edge.ellipse((0, 0, 20, 18), fill=IRON)
    edge.ellipse((3, -5, 25, 14), fill=TRANSPARENT)
    # Hone the cutting edge, then punch the hollow again so no highlight
    # survives inside it and the blade stays an open hook.
    edge.arc((1, 1, 19, 17), 20, 200, fill=IRON_LIT)
    edge.ellipse((3, -5, 25, 14), fill=TRANSPARENT)
    image.alpha_composite(blade)
    draw.rectangle((8, 11, 13, 14), fill=IRON_DARK)  # socket, blade to haft
    return image


def shelter(variant: int) -> Image.Image:
    """A crude hide lean-to: poles, a stretched skin, a red rag on top."""
    image = Image.new("RGBA", (40, 36), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    _shadow(draw, (2, 30, 38, 35))
    hide = ((92, 74, 52, 255), (78, 66, 50, 255))[variant]
    draw.polygon(((3, 32), (20, 3), (37, 32)), fill=hide)
    draw.polygon(((3, 32), (20, 3), (20, 32)), fill=(58, 46, 34, 255))
    for x in (10, 20, 30):                      # lashed support poles
        draw.line((x, 32, 20, 4), fill=WOOD_DARK)
    draw.polygon(((14, 32), (20, 18), (26, 32)), fill=(22, 18, 16, 255))
    # The red cap rag they fly over every shelter.
    draw.polygon(((17, 5), (26, 2), (24, 8)), fill=RED_CLOTH)
    draw.line((17, 5, 26, 2), fill=RED_LIT)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for index in range(3):
        path = OUT / f"redcap_boot_{index + 1}.png"
        boot(index).save(path)
        written.append(path)
    for index in range(2):
        path = OUT / f"redcap_shelter_{index + 1}.png"
        shelter(index).save(path)
        written.append(path)
    for name, image in (("redcap_cauldron", cauldron()),
                        ("redcap_sickle", sickle())):
        path = OUT / f"{name}.png"
        image.save(path)
        written.append(path)
    for path in written:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
