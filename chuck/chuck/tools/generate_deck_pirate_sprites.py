"""Generate the four shanty-synchronized exterior-deck pirate sheets."""

from pathlib import Path

from PIL import Image, ImageDraw


W, H = 16, 30
CLEAR = (0, 0, 0, 0)
OUTLINE = (38, 29, 28, 255)
SKIN = (194, 143, 103, 255)
SKIN_DARK = (137, 88, 67, 255)
WHITE = (205, 198, 166, 255)
BOOT = (43, 31, 27, 255)
TROUSER = (61, 53, 49, 255)
ROPE = (184, 149, 91, 255)
PEWTER = (151, 157, 154, 255)
ALE = (190, 128, 49, 255)
WOOD = (109, 70, 39, 255)
GOLD = (205, 154, 56, 255)
RED = (145, 48, 44, 255)
BLUE = (49, 77, 103, 255)
GREEN = (50, 94, 61, 255)
PURPLE = (92, 54, 103, 255)


def rect(draw: ImageDraw.ImageDraw, box, color) -> None:
    draw.rectangle(box, fill=color)


def _person(facing: str, phase: int, coat, action: str) -> Image.Image:
    image = Image.new("RGBA", (W, H), CLEAR)
    draw = ImageDraw.Draw(image)
    sway = (-1, 0, 1, 0)[phase] if action == "dance" else 0
    bob = (0, 1, 0, 1)[phase] if action != "struggle" else (0, 0, 1, 0)[phase]
    cx = 8 + sway

    # Boots and legs establish a human-scale, readable stance.
    if action == "dance":
        left_dx, right_dx = ((-2, 1), (-1, 2), (0, 3), (-1, 2))[phase]
    elif action == "captain_walk":
        left_dx, right_dx = ((-2, 1), (-1, 2), (0, 1), (-1, 0))[phase]
    else:
        left_dx, right_dx = -1, 1
    rect(draw, (cx - 4 + left_dx, 22, cx - 1 + left_dx, 27), TROUSER)
    rect(draw, (cx + right_dx, 22, cx + 3 + right_dx, 27), TROUSER)
    rect(draw, (cx - 5 + left_dx, 27, cx - 1 + left_dx, 29), BOOT)
    rect(draw, (cx + right_dx, 27, cx + 4 + right_dx, 29), BOOT)

    # Loose coat, pale shirt, head, scarf, and battered tricorn.
    rect(draw, (cx - 5, 13 + bob, cx + 5, 22 + bob), coat)
    rect(draw, (cx - 1, 13 + bob, cx + 2, 21 + bob), WHITE)
    rect(draw, (cx - 4, 7 + bob, cx + 4, 13 + bob), SKIN)
    rect(draw, (cx - 5, 6 + bob, cx + 5, 8 + bob), RED)
    if facing == "left":
        # Side dialogue facings need a shaped tricorn silhouette. The former
        # full-width 13x4 rectangle read as a black box over the pirate's face
        # when the native image was scaled to the window.
        rect(draw, (cx - 4, 5 + bob, cx + 5, 6 + bob), OUTLINE)
        rect(draw, (cx - 1, 2 + bob, cx + 4, 5 + bob), OUTLINE)
    elif facing == "up":
        # Seen from behind, the tricorn still needs a broken silhouette. A
        # full 13x4 brim becomes a featureless black rectangle at 4x scale.
        rect(draw, (cx - 4, 5 + bob, cx + 4, 6 + bob), OUTLINE)
        rect(draw, (cx - 2, 2 + bob, cx + 2, 5 + bob), OUTLINE)
        rect(draw, (cx - 3, 4 + bob, cx + 3, 4 + bob), OUTLINE)
    else:
        rect(draw, (cx - 6, 3 + bob, cx + 6, 6 + bob), OUTLINE)
        rect(draw, (cx - 3, 1 + bob, cx + 3, 4 + bob), OUTLINE)
    if facing == "down":
        rect(draw, (cx - 2, 9 + bob, cx - 2, 9 + bob), OUTLINE)
        rect(draw, (cx + 2, 9 + bob, cx + 2, 9 + bob), OUTLINE)
    elif facing == "up":
        # The old solid 7x5 near-black patch read as a box pasted over the
        # head whenever dialogue turned a pirate away from Chuck. Shape the
        # back of the head with warm shadow, scarf, and only a narrow hairline.
        rect(draw, (cx - 3, 8 + bob, cx + 3, 11 + bob), SKIN_DARK)
        rect(draw, (cx - 2, 8 + bob, cx + 2, 8 + bob), OUTLINE)
        rect(draw, (cx - 3, 11 + bob, cx + 3, 12 + bob), RED)
        rect(draw, (cx - 3, 9 + bob, cx - 3, 10 + bob), OUTLINE)
        rect(draw, (cx + 3, 9 + bob, cx + 3, 10 + bob), OUTLINE)
    else:
        rect(draw, (cx - 3, 9 + bob, cx - 3, 9 + bob), OUTLINE)
        rect(draw, (cx - 5, 10 + bob, cx - 4, 11 + bob), SKIN_DARK)

    if action == "concertina":
        spread = (1, 3, 5, 3)[phase]
        y = 16 + bob
        rect(draw, (cx - 5 - spread, y, cx - 3, y + 5), WOOD)
        rect(draw, (cx + 3, y, cx + 5 + spread, y + 5), WOOD)
        rect(draw, (cx - 3 - spread, y + 1, cx + 3 + spread, y + 4), GOLD)
        for x in range(cx - 2 - spread, cx + 3 + spread, 2):
            rect(draw, (x, y + 1, x, y + 4), OUTLINE)
    elif action == "cheer":
        mug_y = (16, 10, 4, 10)[phase]
        rect(draw, (cx + 5, mug_y, cx + 8, mug_y + 5), PEWTER)
        rect(draw, (cx + 6, mug_y, cx + 7, mug_y), ALE)
        rect(draw, (cx + 3, mug_y + 2, cx + 5, mug_y + 3), SKIN)
    elif action == "dance":
        arm_y = (18, 13, 9, 13)[phase]
        rect(draw, (cx - 7, arm_y, cx - 5, arm_y + 5), SKIN)
        rect(draw, (cx + 5, 22 - arm_y // 2, cx + 7, 27 - arm_y // 2), SKIN)
    elif action == "struggle":
        # Jeffries: elbows strain against three visible rope bands.
        tug = (-1, 1, -1, 1)[phase]
        rect(draw, (cx - 7 + tug, 14, cx - 5 + tug, 22), SKIN)
        rect(draw, (cx + 5 - tug, 14, cx + 7 - tug, 22), SKIN)
        for y in (15, 18, 21):
            rect(draw, (cx - 7, y, cx + 7, y), ROPE)
        rect(draw, (cx - 1, 12, cx, 25), ROPE)
    elif action == "captain_walk":
        # A restrained opposite arm swing, distinct from his later pointing
        # performance so the entrance reads as a walk rather than a slide.
        swing = (-1, 0, 1, 0)[phase]
        rect(draw, (cx - 7, 15 + swing, cx - 5, 21 + swing), coat)
        rect(draw, (cx + 5, 15 - swing, cx + 7, 21 - swing), coat)
        rect(draw, (cx - 7, 21 + swing, cx - 6, 22 + swing), SKIN)
        rect(draw, (cx + 6, 21 - swing, cx + 7, 22 - swing), SKIN)
    else:  # Captain: a clipped point toward Chuck/the waiting plank.
        reach = (0, 1, 2, 1)[phase]
        direction = -1 if facing == "left" else 1
        sleeve_x = sorted((cx + 3 * direction,
                           cx + (4 + reach) * direction))
        hand_x = sorted((cx + (5 + reach) * direction,
                         cx + (6 + reach) * direction))
        rect(draw, (sleeve_x[0], 14, sleeve_x[1], 16), coat)
        rect(draw, (hand_x[0], 14, hand_x[1], 15), SKIN)
        hip_direction = -direction
        hip_x = sorted((cx + 5 * hip_direction, cx + 7 * hip_direction))
        rect(draw, (hip_x[0], 16, hip_x[1], 21), SKIN)
        trim_x = sorted((cx + 2 * hip_direction, cx + 5 * hip_direction))
        rect(draw, (trim_x[0], 21, trim_x[1], 22), GOLD)
    return image


def _sheet(action: str, coat) -> Image.Image:
    frames = [
        _person(facing, phase, coat, action)
        for facing in ("down", "up", "left")
        for phase in range(4)
    ]
    if action == "captain":
        frames.extend(
            _person(facing, phase, coat, "captain_walk")
            for facing in ("down", "up", "left")
            for phase in range(4)
        )
    sheet = Image.new("RGBA", (W * len(frames), H), CLEAR)
    for index, frame in enumerate(frames):
        sheet.paste(frame, (index * W, 0))
    return sheet


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "assets" / "sprites" / "npcs"
    out.mkdir(parents=True, exist_ok=True)
    for name, action, coat in (
        ("concertina_pirate", "concertina", BLUE),
        ("cheering_pirate", "cheer", RED),
        ("dancing_pirate", "dance", GREEN),
        ("jeffries", "struggle", PURPLE),
        ("captain_pirate", "captain", (73, 38, 43, 255)),
    ):
        path = out / f"{name}.png"
        _sheet(action, coat).save(path)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
