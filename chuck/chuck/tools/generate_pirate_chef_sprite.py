"""Generate the galley chef's six-frame procedural pixel-art sheet.

The 16x30 human scale matches established NPCs. Two frames per facing add a
heavy running bob and cleaver swing without changing the native art language.
"""

from pathlib import Path

from PIL import Image, ImageDraw


FRAME_W = 16
FRAME_H = 30
TRANSPARENT = (0, 0, 0, 0)
OUTLINE = (43, 35, 34, 255)
SKIN = (205, 151, 105, 255)
SKIN_SHADOW = (157, 105, 78, 255)
WHITE = (205, 196, 166, 255)
WHITE_SHADOW = (151, 145, 127, 255)
RED = (137, 45, 44, 255)
RED_DARK = (88, 31, 35, 255)
TROUSERS = (55, 61, 68, 255)
BOOT = (43, 31, 27, 255)
STEEL = (178, 188, 186, 255)
STEEL_LIGHT = (220, 224, 211, 255)
HANDLE = (91, 58, 38, 255)


def _rect(draw: ImageDraw.ImageDraw, box, color) -> None:
    draw.rectangle(box, fill=color)


def chef_frame(facing: str, step: int) -> Image.Image:
    image = Image.new("RGBA", (FRAME_W, FRAME_H), TRANSPARENT)
    draw = ImageDraw.Draw(image)
    bob = step

    # Tall cook's toque, bandana, head and jacket.
    _rect(draw, (5, 1 + bob, 10, 2 + bob), WHITE_SHADOW)
    _rect(draw, (3, 3 + bob, 12, 6 + bob), WHITE)
    _rect(draw, (4, 2 + bob, 7, 5 + bob), WHITE)
    _rect(draw, (8, 2 + bob, 11, 5 + bob), WHITE)
    _rect(draw, (4, 7 + bob, 11, 8 + bob), RED)
    _rect(draw, (5, 9 + bob, 10, 12 + bob), SKIN)
    if facing == "down":
        _rect(draw, (6, 10 + bob, 6, 10 + bob), OUTLINE)
        _rect(draw, (9, 10 + bob, 9, 10 + bob), OUTLINE)
        _rect(draw, (7, 12 + bob, 9, 12 + bob), RED_DARK)
    elif facing == "up":
        # The whole head shadows over from behind (a pale strip below the
        # shadow read as a mouth), with the bandana knot at the nape.
        _rect(draw, (5, 9 + bob, 10, 12 + bob), SKIN_SHADOW)
        _rect(draw, (7, 9 + bob, 8, 11 + bob), RED_DARK)
    else:
        _rect(draw, (5, 10 + bob, 5, 10 + bob), OUTLINE)
        _rect(draw, (4, 11 + bob, 4, 11 + bob), SKIN)
    _rect(draw, (3, 13 + bob, 12, 20 + bob), WHITE)
    _rect(draw, (3, 18 + bob, 12, 20 + bob), WHITE_SHADOW)
    _rect(draw, (2, 14 + bob, 3, 18 + bob), SKIN)

    # A broad cleaver moves opposite the stride and stays unmistakable.
    if facing == "left":
        blade_y = 14 + (0 if step else 2)
        _rect(draw, (0, blade_y, 4, blade_y + 4), STEEL)
        _rect(draw, (0, blade_y, 3, blade_y), STEEL_LIGHT)
        _rect(draw, (4, blade_y + 2, 6, blade_y + 3), HANDLE)
        _rect(draw, (5, blade_y + 1, 7, blade_y + 2), SKIN)
    else:
        blade_y = 14 + (2 if step else 0)
        _rect(draw, (12, blade_y, 15, blade_y + 4), STEEL)
        _rect(draw, (13, blade_y, 15, blade_y), STEEL_LIGHT)
        _rect(draw, (10, blade_y + 2, 12, blade_y + 3), HANDLE)
        _rect(draw, (9, blade_y + 1, 11, blade_y + 2), SKIN)

    # Alternating legs make the pursuit visibly more animated than ordinary
    # stationary NPCs while retaining their exact overall height.
    _rect(draw, (4, 21 + bob, 7, 25 + bob), TROUSERS)
    _rect(draw, (9, 21 + bob, 12, 25 + bob), TROUSERS)
    if step:
        _rect(draw, (3, 25 + bob, 6, 28 + bob), BOOT)
        _rect(draw, (10, 25 + bob, 13, 27 + bob), BOOT)
    else:
        _rect(draw, (4, 25 + bob, 7, 27 + bob), BOOT)
        _rect(draw, (9, 25 + bob, 12, 28 + bob), BOOT)
    return image


def main() -> None:
    frames = [
        chef_frame("down", 0), chef_frame("down", 1),
        chef_frame("up", 0), chef_frame("up", 1),
        chef_frame("left", 0), chef_frame("left", 1),
    ]
    sheet = Image.new("RGBA", (FRAME_W * len(frames), FRAME_H), TRANSPARENT)
    for index, frame in enumerate(frames):
        sheet.paste(frame, (index * FRAME_W, 0))
    out = (Path(__file__).resolve().parents[1] / "assets" / "sprites"
           / "hazards" / "pirate_chef.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
