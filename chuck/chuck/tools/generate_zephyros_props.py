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
    """A cloud-giant-scale pale stone arch around a black threshold."""
    image = Image.new("RGBA", (96, 78), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    shadow = (81, 78, 103, 210)
    stone_dark = (116, 122, 145, 255)
    stone = (189, 194, 205, 255)
    light = (232, 229, 218, 255)
    gold = (210, 176, 82, 255)

    draw.ellipse((2, 69, 94, 77), fill=shadow)
    draw.rectangle((8, 27, 29, 72), fill=stone_dark)
    draw.rectangle((67, 27, 88, 72), fill=stone_dark)
    draw.pieslice((8, 0, 88, 69), 180, 360, fill=stone_dark)
    draw.rectangle((15, 29, 81, 72), fill=(8, 10, 18, 255))
    draw.pieslice((15, 7, 81, 72), 180, 360, fill=(8, 10, 18, 255))
    draw.rectangle((8, 27, 16, 72), fill=stone)
    draw.rectangle((80, 27, 88, 72), fill=stone)
    draw.arc((8, 0, 88, 70), 180, 360, fill=stone, width=8)
    draw.arc((12, 4, 84, 68), 190, 350, fill=light, width=2)
    draw.line((8, 71, 88, 71), fill=light, width=2)
    for x in (13, 83):
        for y in (36, 52, 66):
            draw.line((x - 4, y, x + 4, y), fill=stone_dark)
    draw.ellipse((44, 7, 52, 15), fill=gold)
    draw.point((48, 10), fill=(255, 242, 172, 255))
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cloud_staircase().save(OUT / "cloud_staircase.png")
    tower_arch().save(OUT / "cloud_tower_arch.png")
    print("Generated Zephyros staircase and tower arch props")


if __name__ == "__main__":
    main()
