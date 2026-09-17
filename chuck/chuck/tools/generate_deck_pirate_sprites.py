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
ROPE_DARK = (124, 96, 54, 255)
ROPE_LIGHT = (214, 185, 128, 255)
PEWTER = (151, 157, 154, 255)
ALE = (190, 128, 49, 255)
WOOD = (109, 70, 39, 255)
GOLD = (205, 154, 56, 255)
RED = (145, 48, 44, 255)
BLUE = (49, 77, 103, 255)
GREEN = (50, 94, 61, 255)
PURPLE = (92, 54, 103, 255)
STEEL = (176, 182, 188, 255)
STEEL_LIGHT = (214, 219, 222, 255)


def rect(draw: ImageDraw.ImageDraw, box, color) -> None:
    draw.rectangle(box, fill=color)


def _draw_cutlass(draw: ImageDraw.ImageDraw, cx: int, bob: int,
                  side: int) -> None:
    """A cutlass held out at guard, matching the deck fencers' language:
    an extended hand, a gold crossguard, and an angled steel blade with a
    bright edge rising up and away from the body (`side`: +1 right, -1
    left). Kept below hat height so it never crosses his face."""
    hilt_x = cx + 6 * side
    hilt_y = 17 + bob
    tip_x = 15 if side > 0 else 0
    tip_y = 9 + bob
    arm = sorted((cx + 3 * side, cx + 5 * side))
    rect(draw, (arm[0], 15 + bob, arm[1], 17 + bob), SKIN)   # extended hand
    draw.line((hilt_x, hilt_y, tip_x, tip_y), fill=STEEL, width=2)
    draw.line((hilt_x, hilt_y - 1, tip_x, tip_y - 1), fill=STEEL_LIGHT,
              width=1)
    rect(draw, (hilt_x - 1, hilt_y - 1, hilt_x + 1, hilt_y + 1), GOLD)


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

    # Loose coat, pale shirt, head, scarf, and battered tricorn. Seen
    # from behind (facing up) the shirt front and the pale face are
    # hidden: plain coat back and a fully shadowed skull instead.
    rect(draw, (cx - 5, 13 + bob, cx + 5, 22 + bob), coat)
    if facing != "up":
        rect(draw, (cx - 1, 13 + bob, cx + 2, 21 + bob), WHITE)
        rect(draw, (cx - 4, 7 + bob, cx + 4, 13 + bob), SKIN)
    else:
        rect(draw, (cx - 4, 7 + bob, cx + 4, 13 + bob), SKIN_DARK)
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
        # The back of the head is now the uniform shadowed skull painted
        # above; only the scarf's knot and hanging tails interrupt it,
        # CONNECTED to the wrap-around band so they read as cloth. (The
        # old pale ring + a second detached red band read as a huge open
        # mouth whenever a pirate looked north.)
        rect(draw, (cx - 1, 8 + bob, cx + 1, 9 + bob), RED)      # knot
        rect(draw, (cx, 9 + bob, cx + 1, 12 + bob), RED)          # tail
        rect(draw, (cx - 1, 9 + bob, cx - 1, 10 + bob), RED)      # tail
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
        # Jeffries, lashed to the mast. His arms are pinned to his sides
        # rather than held out -- a man waving his elbows about is not
        # tied to anything -- and the turns of rope run out past his
        # shoulders to the edge of the frame, because he stands in front
        # of the spar and the rope carries on round it.
        #
        # Three turns, one pixel each. A fourth, or a second pixel on
        # any of them, buries the coat and the shirt under it and stops
        # reading as a man tied up at all: it becomes a length of fence.
        tug = (-1, 0, -1, 0)[phase]
        rect(draw, (cx - 6 + tug, 14, cx - 5 + tug, 22), SKIN)
        rect(draw, (cx + 5 - tug, 14, cx + 6 - tug, 22), SKIN)
        rect(draw, (cx - 6 + tug, 21, cx - 5 + tug, 22), SKIN_DARK)
        rect(draw, (cx + 5 - tug, 21, cx + 6 - tug, 22), SKIN_DARK)
        for y in (14, 18, 22):
            rect(draw, (1, y, W - 2, y), ROPE)
            for x in range(2, W - 2, 3):
                rect(draw, (x, y, x, y), ROPE_DARK)
            rect(draw, (1, y, 1, y), ROPE_LIGHT)
            rect(draw, (W - 2, y, W - 2, y), ROPE_LIGHT)
        # The knot pulled tight over his chest, and the tail of the line
        # hanging off it.
        rect(draw, (cx - 1, 16, cx + 1, 18), ROPE_DARK)
        rect(draw, (cx, 17, cx, 17), ROPE_LIGHT)
        rect(draw, (cx + 2, 23, cx + 2, 25 + tug), ROPE)
    elif action == "captain_walk":
        # A restrained opposite arm swing, distinct from his later pointing
        # performance so the entrance reads as a walk rather than a slide.
        swing = (-1, 0, 1, 0)[phase]
        rect(draw, (cx - 7, 15 + swing, cx - 5, 21 + swing), coat)
        rect(draw, (cx + 5, 15 - swing, cx + 7, 21 - swing), coat)
        rect(draw, (cx - 7, 21 + swing, cx - 6, 22 + swing), SKIN)
        rect(draw, (cx + 6, 21 - swing, cx + 7, 22 - swing), SKIN)
        _draw_cutlass(draw, cx, bob, 1)  # cutlass in hand as he enters
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
        trim_x = sorted((cx + 2 * hip_direction, cx + 5 * hip_direction))
        rect(draw, (trim_x[0], 21, trim_x[1], 22), GOLD)
        # The cutlass rides at guard in his free hand, opposite the point
        # (the cutlass helper draws the extended arm itself).
        _draw_cutlass(draw, cx, bob, hip_direction)
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
