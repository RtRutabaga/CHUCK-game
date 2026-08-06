"""Generate Phase 10's giant-scale staircase and tower arch props."""

from pathlib import Path

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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cloud_staircase().save(OUT / "cloud_staircase.png")
    tower_arch().save(OUT / "cloud_tower_arch.png")
    print("Generated Zephyros staircase and tower arch props")


if __name__ == "__main__":
    main()
