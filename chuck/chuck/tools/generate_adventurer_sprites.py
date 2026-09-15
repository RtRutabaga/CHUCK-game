"""Generate the final chamber's battle actors (session 131).

Three adventurers at the established 16x30 human-NPC scale — a male
fighter, a wizard, and a clearly female ranger — plus the beholder, a
40x40 floating orb tyrant. Static single-facing sprites for the tableau
slice: the adventurers face west toward the beholder over the dais; the
beholder faces east toward them. Battle animation is a later slice.
"""

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "npcs"

TRANSPARENT = (0, 0, 0, 0)
OUTLINE = (34, 28, 32, 255)
SKIN = (218, 176, 138, 255)
SKIN_SHADE = (186, 142, 106, 255)

# Fighter: dented plate and a shield that has seen three campaigns.
STEEL = (154, 158, 168, 255)
STEEL_DARK = (108, 112, 124, 255)
STEEL_LIGHT = (196, 200, 210, 255)
LEATHER = (110, 78, 48, 255)

# Wizard: deep blue robes, grey beard, a crooked staff.
ROBE = (62, 76, 142, 255)
ROBE_DARK = (44, 54, 104, 255)
BEARD = (206, 206, 210, 255)
STAFF = (124, 92, 56, 255)
STAFF_GEM = (118, 214, 190, 255)

# Ranger: forest greens, auburn hair in a long ponytail, a longbow.
TUNIC = (74, 108, 62, 255)
TUNIC_DARK = (54, 82, 46, 255)
HAIR = (146, 84, 44, 255)
BOW = (112, 80, 46, 255)
STRING = (226, 222, 210, 255)

# Beholder: sickly mauve hide, one vast eye, a crescent of fangs.
HIDE = (128, 84, 118, 255)
HIDE_DARK = (96, 60, 90, 255)
HIDE_LIGHT = (156, 110, 144, 255)
EYE_WHITE = (232, 230, 224, 255)
IRIS = (170, 48, 42, 255)
PUPIL = (26, 18, 22, 255)
FANG = (230, 226, 212, 255)


def fighter() -> Image.Image:
    image = Image.new("RGBA", (16, 30), TRANSPARENT)
    d = ImageDraw.Draw(image)
    d.rectangle((5, 0, 10, 5), fill=STEEL)          # helm
    d.line((5, 0, 10, 0), fill=STEEL_LIGHT)
    d.rectangle((5, 4, 9, 7), fill=SKIN)            # face below the brim
    d.point((6, 5), fill=OUTLINE)                   # eye (facing west)
    d.rectangle((4, 8, 11, 19), fill=STEEL)         # cuirass
    d.line((4, 8, 11, 8), fill=STEEL_LIGHT)
    d.line((4, 14, 11, 14), fill=STEEL_DARK)
    d.rectangle((0, 9, 3, 17), fill=STEEL_DARK)     # the shield, held west
    d.rectangle((1, 10, 2, 16), fill=STEEL)
    # The sword arm's gauntlet. The sword itself is drawn at runtime
    # (src/entities/sword.py) so that it can swing: painted into the
    # sprite it was a pale bar pointing one way for ever.
    d.rectangle((12, 13, 13, 16), fill=STEEL_DARK)
    d.point((12, 13), fill=STEEL_LIGHT)
    d.rectangle((5, 20, 10, 25), fill=LEATHER)      # skirt
    d.rectangle((5, 26, 6, 29), fill=STEEL_DARK)    # greaves
    d.rectangle((9, 26, 10, 29), fill=STEEL_DARK)
    return image


def wizard() -> Image.Image:
    image = Image.new("RGBA", (16, 30), TRANSPARENT)
    d = ImageDraw.Draw(image)
    d.polygon(((7, 0), (11, 6), (3, 6)), fill=ROBE_DARK)  # pointed hat
    d.rectangle((2, 6, 12, 7), fill=ROBE_DARK)            # brim
    d.rectangle((5, 8, 9, 11), fill=SKIN)                 # face
    d.point((6, 9), fill=OUTLINE)
    d.rectangle((4, 12, 10, 16), fill=BEARD)              # the beard
    d.rectangle((5, 15, 9, 17), fill=BEARD)
    d.rectangle((3, 13, 11, 26), fill=ROBE)               # robes
    d.line((3, 13, 3, 26), fill=ROBE_DARK)
    d.line((11, 13, 11, 26), fill=ROBE_DARK)
    d.rectangle((3, 27, 11, 29), fill=ROBE_DARK)          # hem
    d.rectangle((0, 4, 1, 27), fill=STAFF)                # staff, west
    d.rectangle((0, 2, 1, 3), fill=STAFF_GEM)             # its stone
    return image


def ranger() -> Image.Image:
    image = Image.new("RGBA", (16, 30), TRANSPARENT)
    d = ImageDraw.Draw(image)
    d.rectangle((5, 0, 10, 2), fill=HAIR)           # hair over the brow
    d.rectangle((5, 2, 9, 6), fill=SKIN)            # face
    d.point((6, 4), fill=OUTLINE)
    d.rectangle((10, 1, 12, 4), fill=HAIR)          # gathered ponytail...
    d.rectangle((11, 5, 12, 15), fill=HAIR)         # ...falling long
    d.rectangle((4, 7, 10, 17), fill=TUNIC)         # tunic, cinched
    d.line((4, 12, 10, 12), fill=TUNIC_DARK)        # belt
    d.rectangle((4, 13, 10, 14), fill=TUNIC)
    d.rectangle((5, 18, 9, 23), fill=TUNIC_DARK)    # skirted hem
    d.rectangle((5, 24, 6, 29), fill=LEATHER)       # boots
    d.rectangle((8, 24, 9, 29), fill=LEATHER)
    # The longbow, held out west toward the beholder: the wood bows out
    # away from her, and the string runs tip to tip on her side of it.
    for y, xs in ((4, (2, 3)), (5, (2,)), (6, (1, 2)), (7, (1,)), (8, (1,))):
        for x in xs:
            d.point((x, y), fill=BOW)
            d.point((x, 28 - y), fill=BOW)
    d.rectangle((0, 9, 1, 19), fill=BOW)
    d.line((3, 5, 3, 23), fill=STRING)                  # string
    return image


def beholder() -> Image.Image:
    image = Image.new("RGBA", (40, 40), TRANSPARENT)
    d = ImageDraw.Draw(image)
    # Eye stalks first, writhing over the crown.
    for tip_x, tip_y, base_x in ((3, 4, 12), (11, 1, 16), (20, 0, 20),
                                 (29, 1, 24), (37, 4, 28)):
        d.line((base_x, 12, tip_x, tip_y), fill=HIDE_DARK, width=2)
        d.rectangle((tip_x - 1, tip_y - 1, tip_x + 1, tip_y + 1),
                    fill=EYE_WHITE)
        d.point((tip_x, tip_y), fill=IRIS)
    # The orb body.
    d.ellipse((4, 8, 36, 38), fill=HIDE)
    d.ellipse((6, 10, 34, 24), fill=HIDE_LIGHT)
    d.ellipse((4, 8, 36, 38), outline=HIDE_DARK)
    # The vast central eye, glaring east toward the adventurers.
    d.ellipse((12, 13, 32, 27), fill=EYE_WHITE)
    d.ellipse((21, 16, 30, 25), fill=IRIS)
    d.ellipse((24, 18, 28, 23), fill=PUPIL)
    # A crescent maw of fangs.
    d.arc((10, 22, 32, 36), 20, 160, fill=HIDE_DARK, width=3)
    for x in range(13, 30, 4):
        d.polygon(((x, 31), (x + 1, 34), (x + 2, 31)), fill=FANG)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, image in (("fighter", fighter()), ("wizard", wizard()),
                        ("ranger", ranger()), ("beholder", beholder())):
        path = OUT / f"{name}.png"
        image.save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
