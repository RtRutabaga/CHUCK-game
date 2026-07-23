"""Generate the paired deck fencers' four-beat action sheets."""

from pathlib import Path

from PIL import Image, ImageDraw


W, H = 24, 30
CLEAR = (0, 0, 0, 0)
OUTLINE = (38, 29, 28, 255)
SKIN = (194, 143, 103, 255)
SHIRT = (203, 194, 158, 255)
BOOT = (43, 31, 27, 255)
TROUSER = (62, 53, 48, 255)
STEEL = (203, 211, 207, 255)
STEEL_DARK = (103, 116, 117, 255)
GOLD = (202, 151, 54, 255)
RED = (143, 48, 45, 255)
BLUE = (45, 76, 108, 255)


def rect(draw, box, color) -> None:
    draw.rectangle(box, fill=color)


def frame(facing: str, phase: int, coat) -> Image.Image:
    image = Image.new("RGBA", (W, H), CLEAR)
    draw = ImageDraw.Draw(image)
    # Source side frames face left; the runtime mirrors them for fighter A.
    lunge = -2 if facing == "left" and phase == 1 else 0
    cx = 14 + lunge
    bob = (0, 1, 0, 0)[phase]

    rect(draw, (cx - 4, 22, cx - 1, 27), TROUSER)
    rect(draw, (cx + 1, 22, cx + 4, 27), TROUSER)
    rect(draw, (cx - 5, 27, cx - 1, 29), BOOT)
    rect(draw, (cx + 1, 27, cx + 5, 29), BOOT)
    rect(draw, (cx - 5, 13 + bob, cx + 5, 22 + bob), coat)
    rect(draw, (cx - 1, 13 + bob, cx + 2, 21 + bob), SHIRT)
    rect(draw, (cx - 4, 7 + bob, cx + 4, 13 + bob), SKIN)
    rect(draw, (cx - 5, 6 + bob, cx + 5, 8 + bob), RED)
    rect(draw, (cx - 6, 3 + bob, cx + 6, 6 + bob), OUTLINE)
    rect(draw, (cx - 3, 1 + bob, cx + 3, 4 + bob), OUTLINE)
    if facing == "down":
        rect(draw, (cx - 2, 9 + bob, cx - 2, 9 + bob), OUTLINE)
        rect(draw, (cx + 2, 9 + bob, cx + 2, 9 + bob), OUTLINE)
    elif facing == "up":
        rect(draw, (cx - 3, 8 + bob, cx + 3, 12 + bob), OUTLINE)
    else:
        rect(draw, (cx - 3, 9 + bob, cx - 3, 9 + bob), OUTLINE)

    # Four readable fencing beats: guard, lunge, high parry, low recovery.
    if facing == "left":
        hilt = (cx - 4, 17 + bob)
        tips = ((2, 16), (0, 16), (3, 7), (4, 24))
    elif facing == "up":
        hilt = (cx - 4, 16 + bob)
        tips = ((5, 10), (3, 7), (9, 3), (2, 17))
    else:
        hilt = (cx - 4, 17 + bob)
        tips = ((4, 19), (2, 22), (6, 8), (3, 25))
    tip = tips[phase]
    draw.line((hilt[0], hilt[1], tip[0], tip[1]), fill=STEEL_DARK, width=3)
    draw.line((hilt[0], hilt[1] - 1, tip[0], tip[1] - 1), fill=STEEL, width=1)
    rect(draw, (hilt[0] - 1, hilt[1] - 2,
                hilt[0] + 2, hilt[1] + 1), GOLD)
    rect(draw, (cx - 6, 16 + bob, cx - 4, 19 + bob), SKIN)
    return image


def sheet(coat) -> Image.Image:
    frames = [
        frame(facing, phase, coat)
        for facing in ("down", "up", "left")
        for phase in range(4)
    ]
    image = Image.new("RGBA", (W * len(frames), H), CLEAR)
    for index, cell in enumerate(frames):
        image.paste(cell, (index * W, 0))
    return image


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "hazards"
    out.mkdir(parents=True, exist_ok=True)
    for role, coat in (("a", BLUE), ("b", RED)):
        path = out / f"sword_fighter_{role}.png"
        sheet(coat).save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
