"""Generate Phase 10's giant-scale staircase and tower arch props."""

from pathlib import Path
import math

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"
TRANSPARENT = (0, 0, 0, 0)


def cloud_staircase() -> Image.Image:
    """A towering switchback of solid-looking cloud steps."""
    image = Image.new("RGBA", (112, 152), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    cloud_dark = (142, 151, 184, 255)
    cloud = (205, 214, 233, 255)
    cloud_light = (244, 244, 238, 255)
    violet = (142, 118, 188, 255)
    gold = (221, 188, 98, 255)

    # A broad cloud plinth makes the base impossible to mistake for foliage.
    for box in ((5, 127, 61, 151), (39, 123, 104, 151),
                (18, 116, 83, 148)):
        draw.ellipse(box, fill=cloud_dark)
    for box in ((4, 122, 59, 146), (43, 118, 107, 146),
                (18, 112, 85, 143)):
        draw.ellipse(box, fill=cloud)
    draw.arc((13, 118, 98, 151), 185, 350, fill=cloud_light, width=3)

    # Eleven ascending treads zigzag into the sky, each much wider than Chuck.
    for index in range(11):
        y = 120 - index * 10
        x = 18 + (index % 2) * 24 + index * 3
        width = 43 - index
        draw.ellipse((x - 5, y - 5, x + width + 5, y + 9), fill=cloud_dark)
        draw.rectangle((x, y, x + width, y + 6), fill=cloud)
        draw.line((x + 3, y, x + width - 2, y), fill=cloud_light, width=2)
        draw.point((x + 7 + index * 2, y + 3), fill=violet)

    # A small gold-violet crown suggests ancient construction without rails.
    draw.line((75, 13, 75, 3), fill=gold, width=2)
    draw.polygon(((70, 8), (75, 1), (80, 8)), fill=violet)
    for x, y in ((13, 111), (94, 130), (56, 84), (89, 48), (46, 24)):
        draw.point((x, y), fill=(247, 236, 184, 220))
    return image


def tower_arch() -> Image.Image:
    """A giant arch embedded in the tower's broad curved outer wall."""
    image = Image.new("RGBA", (192, 128), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    shadow = (72, 71, 94, 225)
    stone_dark = (119, 126, 149, 255)
    stone = (192, 197, 207, 255)
    light = (235, 232, 220, 255)
    gold = (210, 176, 82, 255)

    # The wall continues beyond the north edge and widens toward its base.
    # That mass is the important perspective cue: this is a tower entrance,
    # never a freestanding portal with open sky immediately behind it.
    draw.polygon(
        ((18, 0), (173, 0), (191, 119), (184, 127), (8, 127), (0, 119)),
        fill=shadow,
    )
    draw.polygon(
        ((23, 0), (168, 0), (184, 116), (177, 123), (15, 123), (7, 116)),
        fill=stone,
    )
    draw.polygon(((23, 0), (49, 0), (41, 116), (15, 123), (7, 116)),
                 fill=light)
    draw.polygon(((151, 0), (168, 0), (184, 116), (177, 123), (160, 116)),
                 fill=stone_dark)

    # Broad masonry courses curve around the cylindrical tower body.
    for y in range(15, 108, 16):
        inset = max(0, (105 - y) // 18)
        draw.line((16 + inset, y, 176 - inset, y), fill=stone_dark, width=2)
    for y, offsets in ((15, (64, 121)), (31, (46, 101, 148)),
                       (47, (70, 130)), (63, (45, 151))):
        for x in offsets:
            draw.line((x, y, x - 1, y + 15), fill=stone_dark)

    # The black opening is cut into the wall and framed by massive piers.
    doorway = (65, 43, 127, 122)
    draw.ellipse((doorway[0], doorway[1], doorway[2], 105),
                 fill=(7, 9, 17, 255))
    draw.rectangle((doorway[0], 74, doorway[2], doorway[3]),
                   fill=(7, 9, 17, 255))
    draw.rectangle((56, 79, 68, 123), fill=stone_dark)
    draw.rectangle((124, 79, 136, 123), fill=stone_dark)
    draw.arc((56, 39, 136, 112), 180, 360, fill=stone_dark, width=12)
    draw.rectangle((59, 82, 65, 123), fill=light)
    draw.rectangle((127, 82, 133, 123), fill=stone)
    draw.arc((60, 43, 132, 108), 185, 355, fill=light, width=3)
    draw.line((15, 122, 177, 122), fill=light, width=2)

    # A restrained giant-scale crest centers the entrance in the facade.
    draw.ellipse((91, 44, 101, 54), fill=gold)
    draw.point((96, 48), fill=(255, 242, 172, 255))
    return image


def griffon_nest() -> Image.Image:
    """A cloud-giant aerie nest broad enough to dwarf Chuck."""
    image = Image.new("RGBA", (112, 68), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    shadow = (55, 54, 70, 165)
    hollow = (61, 48, 39, 255)
    reed_dark = (104, 78, 48, 255)
    reed = (164, 126, 67, 255)
    reed_light = (220, 183, 104, 255)

    draw.ellipse((3, 49, 109, 67), fill=shadow)
    draw.ellipse((7, 12, 105, 63), fill=reed_dark)
    draw.ellipse((16, 18, 96, 56), fill=reed)
    draw.ellipse((25, 24, 87, 51), fill=hollow)
    for inset, color in ((3, reed_light), (8, reed), (13, reed_dark)):
        draw.arc((inset, 9 + inset // 2, 111 - inset, 65 - inset // 3),
                 5, 175, fill=color, width=3)
        draw.arc((inset, 7 + inset // 2, 111 - inset, 63 - inset // 3),
                 185, 355, fill=color, width=3)
    # Short tangential sticks build a ragged rim without turning the hollow
    # into a uniform grate. Every fifth stick juts farther out.
    colors = (reed_dark, reed, reed_light)
    for index in range(30):
        angle = math.tau * index / 30
        cx = 56 + math.cos(angle) * 46
        cy = 36 + math.sin(angle) * 22
        length = 15 + (7 if index % 5 == 0 else 0)
        tx = -math.sin(angle) * length / 2
        ty = math.cos(angle) * length / 4
        draw.line((round(cx - tx), round(cy - ty),
                   round(cx + tx), round(cy + ty)),
                  fill=colors[index % len(colors)], width=2)
    for x, y in ((31, 29), (43, 24), (67, 25), (79, 32)):
        draw.line((x - 8, y + 5, x + 9, y - 4), fill=reed_light, width=2)
    return image


def aerie_rope() -> Image.Image:
    """A giant rope lashed to a cleat on the shaft's southern stone lip."""
    image = Image.new("RGBA", (48, 80), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    dark = (91, 65, 42, 255)
    rope = (185, 139, 75, 255)
    light = (232, 194, 116, 255)
    iron_dark = (50, 52, 65, 255)
    iron = (112, 116, 132, 255)

    # The free length recedes northward into the black shaft.
    draw.ellipse((16, 1, 30, 8), fill=dark)
    draw.ellipse((18, 1, 28, 6), fill=rope)
    for y in range(6, 62, 6):
        sway = 1 if (y // 6) % 2 else -1
        draw.line((22 + sway, y, 23 - sway, y + 7), fill=dark, width=7)
        draw.line((23 + sway, y, 24 - sway, y + 7), fill=rope, width=4)
        draw.point((23 + sway, y + 1), fill=light)

    # A huge iron cleat and rope turns occupy the bottom stone tile.  This is
    # the unambiguous attachment point the player sees at the lip of the hole.
    draw.ellipse((7, 67, 41, 78), fill=iron_dark)
    draw.rectangle((11, 66, 37, 74), fill=iron)
    draw.rectangle((20, 59, 28, 78), fill=iron_dark)
    draw.rectangle((22, 59, 26, 76), fill=iron)
    draw.arc((12, 58, 36, 78), 175, 355, fill=dark, width=5)
    draw.arc((13, 57, 35, 76), 175, 355, fill=rope, width=3)
    draw.line((8, 72, 3, 77), fill=iron, width=3)
    draw.line((40, 72, 45, 77), fill=iron_dark, width=3)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cloud_staircase().save(OUT / "cloud_staircase.png")
    tower_arch().save(OUT / "cloud_tower_arch.png")
    griffon_nest().save(OUT / "griffon_nest.png")
    aerie_rope().save(OUT / "aerie_rope.png")
    print("Generated Zephyros staircase, tower, and Aerie props")


if __name__ == "__main__":
    main()
