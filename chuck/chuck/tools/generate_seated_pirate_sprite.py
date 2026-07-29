"""Generate the crew-quarter pirate's six-frame seated animation."""

from pathlib import Path

from PIL import Image, ImageDraw


W, H = 16, 30
CLEAR = (0, 0, 0, 0)
OUTLINE = (39, 31, 30, 255)
SKIN = (194, 143, 103, 255)
SKIN_DARK = (139, 91, 71, 255)
HAIR = (78, 49, 34, 255)
RED = (139, 45, 45, 255)
RED_DARK = (86, 31, 34, 255)
COAT = (49, 73, 94, 255)
COAT_LIGHT = (67, 96, 119, 255)
SHIRT = (190, 181, 148, 255)
TROUSER = (68, 57, 49, 255)
BOOT = (42, 31, 27, 255)
PEWTER = (148, 154, 151, 255)
ALE = (186, 126, 49, 255)
CHAIR = (103, 67, 40, 255)
CHAIR_LIGHT = (139, 92, 51, 255)


def rect(draw, box, color) -> None:
    draw.rectangle(box, fill=color)


def frame(facing: str, beat: int) -> Image.Image:
    image = Image.new("RGBA", (W, H), CLEAR)
    draw = ImageDraw.Draw(image)
    bob = beat

    # The chair is part of the character silhouette, so "seated" remains
    # legible even when the table is partly off-camera.
    rect(draw, (2, 13, 3, 28), CHAIR)
    rect(draw, (12, 13, 13, 28), CHAIR)
    rect(draw, (2, 13, 13, 15), CHAIR_LIGHT)
    rect(draw, (1, 21, 14, 23), CHAIR)

    # Battered tricorn and red head scarf.
    if facing == "up":
        # Break up the rear silhouette so the hat does not become a pasted-on
        # dark rectangle when this separate interior pirate turns away.
        rect(draw, (4, 5 + bob, 11, 6 + bob), OUTLINE)
        rect(draw, (6, 2 + bob, 9, 5 + bob), HAIR)
        rect(draw, (5, 4 + bob, 10, 5 + bob), HAIR)
    else:
        rect(draw, (3, 3 + bob, 12, 4 + bob), OUTLINE)
        rect(draw, (5, 1 + bob, 10, 4 + bob), HAIR)
        rect(draw, (2, 4 + bob, 13, 6 + bob), HAIR)
    rect(draw, (4, 6 + bob, 11, 7 + bob), RED)
    rect(draw, (5, 8 + bob, 10, 12 + bob), SKIN)
    if facing == "down":
        rect(draw, (6, 9 + bob, 6, 9 + bob), OUTLINE)
        rect(draw, (9, 9 + bob, 9, 9 + bob), OUTLINE)
        rect(draw, (5, 12 + bob, 10, 13 + bob), HAIR)
    elif facing == "up":
        # Back of the head: uniform shadowed skull with one narrow scarf
        # tail hanging CONNECTED to the wrap-around band (a detached lower
        # band over pale skin read as an open mouth from behind).
        rect(draw, (5, 8 + bob, 10, 12 + bob), SKIN_DARK)
        rect(draw, (7, 8 + bob, 7, 10 + bob), RED_DARK)
    else:
        rect(draw, (5, 9 + bob, 5, 9 + bob), OUTLINE)
        rect(draw, (4, 10 + bob, 4, 10 + bob), SKIN_DARK)
        rect(draw, (5, 12 + bob, 9, 13 + bob), HAIR)

    # Loose coat over a pale shirt, compressed into a seated silhouette.
    rect(draw, (3, 14 + bob, 12, 20 + bob), COAT)
    rect(draw, (6, 14 + bob, 9, 20 + bob), SHIRT)
    rect(draw, (3, 18 + bob, 4, 20 + bob), COAT_LIGHT)
    rect(draw, (11, 18 + bob, 12, 20 + bob), COAT_LIGHT)
    rect(draw, (3, 21 + bob, 7, 24 + bob), TROUSER)
    rect(draw, (9, 21 + bob, 13, 24 + bob), TROUSER)
    rect(draw, (2, 24 + bob, 6, 27 + bob), BOOT)
    rect(draw, (10, 24 + bob, 14, 27 + bob), BOOT)

    # His pewter mug rises on the offbeat, giving the seated NPC a relaxed
    # soundtrack-like pulse without turning him into a broad gag.
    mug_y = 15 + (0 if beat else 3)
    if facing == "left":
        rect(draw, (0, mug_y, 3, mug_y + 4), PEWTER)
        rect(draw, (1, mug_y, 2, mug_y), ALE)
        rect(draw, (3, mug_y + 1, 5, mug_y + 2), SKIN)
    else:
        rect(draw, (12, mug_y, 15, mug_y + 4), PEWTER)
        rect(draw, (13, mug_y, 14, mug_y), ALE)
        rect(draw, (10, mug_y + 1, 12, mug_y + 2), SKIN)
    return image


def main() -> None:
    frames = [
        frame("down", 0), frame("down", 1),
        frame("up", 0), frame("up", 1),
        frame("left", 0), frame("left", 1),
    ]
    sheet = Image.new("RGBA", (W * len(frames), H), CLEAR)
    for index, cell in enumerate(frames):
        sheet.paste(cell, (index * W, 0))
    out = (Path(__file__).resolve().parents[1] / "assets" / "sprites"
           / "npcs" / "seated_pirate.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
