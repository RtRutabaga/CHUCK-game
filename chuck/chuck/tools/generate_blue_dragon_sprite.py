"""Generate Phase 13's blue dragon: the biggest thing in the game.

The dragon used to be drawn in code, out of about a dozen polygons in a
48x34 box. That was the right size for a hazard marker and the wrong
size for a dragon: at three tiles across, the wing was a triangle, the
head was an eight-pixel rectangle, and the thing a player actually read
was "a blue shape that hurts". There is only one of these in the game
and it is the one thing on the map that cannot be fought, so it has to
be worth walking up to look at.

So it is a sprite now, at 128x96 -- eight tiles by six, nearly twice the
size of the massive Chult dinosaur, and about nine times Chuck's own
height. That is roughly the real ratio between a one-foot rat and a
dragon, and getting it right is most of why the thing reads.

What makes a silhouette read as a dragon, in rough order of how much
each one carries at this scale:

    the wing, spread and boned, above the shoulder
    the long neck, and a head with a jaw rather than a face
    the tail, longer than the body, tapering to a fin
    spines down the whole length of it
    four legs with claws on the ground

Only the left-facing view is drawn. The dragon never moves and never
turns, so the right-facing one is this flipped -- which is also why the
head is drawn in profile rather than three-quarters: a three-quarter
head mirrors into a dragon looking over its own shoulder.

Six frames. Four of them are a slow wing beat for the long stretches
when it is doing nothing, and two are the breath: head down, jaw open,
throat lit. The breath frames are separate poses rather than the idle
with a mouth pasted on, because a creature that is about to do
something does it with its whole body.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "hazards"

FRAME_W, FRAME_H = 128, 96
IDLE_FRAMES = 4
BREATH_FRAMES = 2

# Blue, and cold. The lightning it breathes is nearly white, so the
# animal itself has to stay well below that or the bolt stops reading
# as the bright thing in the picture.
SCALE_DARK = (26, 52, 96, 255)
SCALE = (48, 92, 158, 255)
SCALE_LIT = (86, 142, 204, 255)
SCALE_PALE = (140, 190, 236, 255)
BELLY = (170, 200, 228, 255)
BELLY_DARK = (116, 152, 190, 255)
MEMBRANE = (62, 100, 158, 255)
MEMBRANE_LIT = (94, 138, 196, 255)
BONE = (150, 186, 224, 255)
HORN = (224, 230, 240, 255)
HORN_DARK = (142, 154, 176, 255)
CLAW = (236, 240, 248, 255)
EYE = (250, 236, 120, 255)
EYE_DARK = (120, 96, 20, 255)
MOUTH = (58, 30, 46, 255)
THROAT = (206, 232, 255, 255)
SHADOW = (24, 40, 62, 110)

GROUND = 90         # where the feet and the cast shadow sit


def _spines(draw, points, size: int, colour=HORN) -> None:
    """A row of spines along a line. The single cheapest dragon tell.

    Drawn as triangles standing off the back rather than as a comb of
    equal teeth: a dragon's spines get shorter toward the tail, and a
    line of identical ones reads as a garden rake.
    """
    for index in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[index], points[index + 1]
        height = max(2, size - index)
        # Perpendicular to the run, so the spines lean the way the
        # back does instead of all standing straight up.
        dx, dy = x1 - x0, y1 - y0
        length = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / length, dx / length
        tip = (x0 + (x1 - x0) * 0.4 + nx * height,
               y0 + (y1 - y0) * 0.4 + ny * height)
        draw.polygon(((x0, y0), tip, (x1, y1)), fill=colour)


def _wing(draw, lift: float) -> None:
    """One big spread wing, above and behind the shoulder.

    This is the shape doing most of the work, so it gets most of the
    frame: root at the shoulder, a wrist up and to the right, and four
    fingers fanning out from it with membrane stretched between them.

    The membrane is drawn as one polygon and the finger bones over it,
    rather than as four separate panels. Panelled, the gaps between
    them showed the sky through the middle of the wing and it came
    apart into four flags on a pole.
    """
    root = (62, 52)
    wrist = (86, 16 - lift)
    tips = (
        (118, 4 - lift * 1.4),
        (126, 26 - lift),
        (116, 46 - lift * 0.6),
        (96, 58 - lift * 0.3),
    )
    # The membrane: shoulder, wrist, round the finger tips, back home.
    draw.polygon((root, wrist) + tips, fill=MEMBRANE)
    # A lighter wash on the upper half, so the wing has a near edge and
    # a far one instead of being a flat blue kite.
    draw.polygon((root, wrist, tips[0], tips[1]), fill=MEMBRANE_LIT)
    # The arm bone, thicker than the fingers, and the fingers off it.
    draw.line((root, wrist), fill=BONE, width=4)
    for index, tip in enumerate(tips):
        draw.line((wrist, tip), fill=BONE, width=3 if index < 2 else 2)
        # A claw at the leading tip: the one detail that says wing and
        # not fin.
        if index == 0:
            draw.polygon((tip, (tip[0] + 5, tip[1] - 2),
                          (tip[0] + 1, tip[1] + 4)), fill=CLAW)
    # The trailing edge scalloped between the fingers, which is the
    # other half of reading as a wing rather than as a sail.
    for index in range(len(tips) - 1):
        near, far = tips[index], tips[index + 1]
        mid = ((near[0] + far[0]) / 2 - 5, (near[1] + far[1]) / 2)
        draw.polygon((near, mid, far), fill=(0, 0, 0, 0))


def _leg(draw, hip, knee, foot, thickness: int, colour) -> None:
    draw.line((hip, knee), fill=colour, width=thickness)
    draw.line((knee, foot), fill=colour, width=max(3, thickness - 3))
    draw.ellipse((foot[0] - 7, foot[1] - 4, foot[0] + 7, foot[1] + 4),
                 fill=colour)
    for toe in range(3):
        tx = foot[0] - 8 + toe * 4
        draw.polygon(((tx, foot[1] + 1), (tx - 4, foot[1] + 4),
                      (tx + 1, foot[1] + 4)), fill=CLAW)


def _head(draw, anchor, open_jaw: bool, glow: float) -> None:
    """The head, in profile, snout to the left.

    A dragon's head at this size is a wedge with a jaw hinge behind it,
    a brow over the eye and horns swept back off the skull. Drawn as an
    oval with a dot for an eye it came out as a horse.
    """
    hx, hy = anchor
    # Skull: a wedge, deeper at the back where the jaw hinges.
    draw.polygon(((hx, hy + 8), (hx + 12, hy + 1), (hx + 28, hy),
                  (hx + 34, hy + 10), (hx + 26, hy + 16), (hx + 6, hy + 14)),
                 fill=SCALE)
    draw.polygon(((hx, hy + 8), (hx + 12, hy + 1), (hx + 24, hy + 2),
                  (hx + 20, hy + 7), (hx + 4, hy + 9)), fill=SCALE_LIT)

    if open_jaw:
        # Hinged down and back, with the inside of the mouth showing.
        draw.polygon(((hx + 4, hy + 13), (hx + 26, hy + 14),
                      (hx + 24, hy + 28), (hx + 2, hy + 20)), fill=MOUTH)
        draw.polygon(((hx + 3, hy + 16), (hx + 24, hy + 17),
                      (hx + 22, hy + 27), (hx + 3, hy + 22)), fill=SCALE_DARK)
        draw.polygon(((hx + 5, hy + 21), (hx + 22, hy + 22),
                      (hx + 21, hy + 26), (hx + 6, hy + 24)), fill=SCALE_DARK)
        # Teeth, top and bottom, and they must not meet. Drawn to the
        # same line from both jaws they closed the gap between them and
        # the open mouth came back as a zip fastener -- what says "open"
        # is the dark between the two rows, not the teeth themselves.
        for tooth in range(4):
            tx = hx + 5 + tooth * 5
            draw.polygon(((tx, hy + 13), (tx + 2, hy + 13), (tx + 1, hy + 16)),
                         fill=HORN)
        for tooth in range(3):
            tx = hx + 8 + tooth * 5
            draw.polygon(((tx, hy + 22), (tx + 2, hy + 22), (tx + 1, hy + 19)),
                         fill=HORN)
        # The charge in its throat, which is the only warm colour on it.
        if glow > 0:
            # Small and deep in the throat. Filling the mouth with it,
            # the dragon came back holding a bright ball in its teeth.
            radius = 1.5 + 2.0 * glow
            draw.ellipse((hx + 19 - radius, hy + 19 - radius,
                          hx + 19 + radius, hy + 19 + radius), fill=THROAT)
    else:
        draw.polygon(((hx + 2, hy + 12), (hx + 26, hy + 14),
                      (hx + 24, hy + 18), (hx + 4, hy + 15)),
                     fill=SCALE_DARK)
        # The line of the closed mouth, with two teeth showing over it.
        draw.line((hx + 3, hy + 13, hx + 24, hy + 15), fill=MOUTH, width=1)
        for tooth in (6, 11):
            draw.polygon(((hx + tooth, hy + 14), (hx + tooth + 2, hy + 14),
                          (hx + tooth + 1, hy + 18)), fill=HORN)

    # The nose horn: a blue dragon's one unmistakable feature, and the
    # reason this is not a wyvern.
    draw.polygon(((hx + 2, hy + 7), (hx - 6, hy - 6), (hx + 8, hy + 4)),
                 fill=HORN)
    draw.polygon(((hx + 2, hy + 7), (hx - 3, hy - 2), (hx + 5, hy + 5)),
                 fill=HORN_DARK)
    # ...and the pair swept back off the skull.
    for index, (dx, dy, reach) in enumerate(((22, 2, 16), (26, 6, 13))):
        base = (hx + dx, hy + dy)
        tip = (base[0] + reach, base[1] - reach * 0.55 - index * 2)
        draw.line((base, tip), fill=HORN, width=4 - index)
        draw.line((base, tip), fill=HORN_DARK, width=1)

    # Brow and eye. The brow is what makes it look at you.
    draw.polygon(((hx + 8, hy + 4), (hx + 18, hy + 2), (hx + 17, hy + 6),
                  (hx + 9, hy + 8)), fill=SCALE_DARK)
    draw.ellipse((hx + 10, hy + 5, hx + 15, hy + 9), fill=EYE)
    draw.line((hx + 12, hy + 5, hx + 12, hy + 9), fill=EYE_DARK)
    # A frill of small spines along the jaw line, back toward the neck.
    for index in range(3):
        bx = hx + 24 + index * 3
        draw.polygon(((bx, hy + 12 + index), (bx + 5, hy + 10 + index * 2),
                      (bx + 1, hy + 16 + index)), fill=SCALE_DARK)


def dragon_frame(step: int, breathing: bool, glow: float = 0.0) -> Image.Image:
    """One frame, facing left. The right-facing view is this mirrored."""
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    lift = (0.0, 3.0, 5.0, 2.0)[step % 4] if not breathing else 1.0
    # Breathing, it drops its shoulders and drives the head forward and
    # down. Standing straight with the jaw open it looked like a yawn.
    crouch = 6 if breathing else 0

    draw.ellipse((14, GROUND - 5, 116, GROUND + 6), fill=SHADOW)

    # The tail first, so the body overlaps its root rather than the
    # other way round. It is longer than the body on purpose: the tail
    # is what stops a winged thing reading as a bird.
    tail = [(78, 56 + crouch), (96, 62 + crouch), (108, 70),
            (116, 78), (121, 85)]
    for index in range(len(tail) - 1):
        draw.line((tail[index], tail[index + 1]), fill=SCALE_DARK,
                  width=max(3, 14 - index * 3))
        # A lit edge along the top of it. One flat dark colour the
        # whole way, the tail read as a shadow cast by the haunch
        # rather than as part of the animal.
        draw.line((tail[index][0], tail[index][1] - 2,
                   tail[index + 1][0], tail[index + 1][1] - 2),
                  fill=SCALE, width=max(1, 5 - index))
    # The fin at the end of it, standing up off the tip.
    draw.polygon(((118, 84), (127, 74), (127, 92), (114, 90)),
                 fill=SCALE_DARK)
    draw.polygon(((119, 84), (125, 78), (125, 89), (117, 88)), fill=SCALE)
    _spines(draw, tail, 8, SCALE_DARK)

    # Far legs, in shadow, before the body.
    _leg(draw, (74, 62 + crouch), (84, 76 + crouch), (86, GROUND - 2),
         9, SCALE_DARK)
    _leg(draw, (46, 60 + crouch), (40, 74 + crouch), (38, GROUND - 2),
         7, SCALE_DARK)

    _wing(draw, lift)

    # The body: one heavy mass, chest deeper than haunch.
    draw.ellipse((38, 42 + crouch, 92, 80 + crouch), fill=SCALE)
    draw.ellipse((36, 44 + crouch, 74, 80 + crouch), fill=SCALE_LIT)
    # Belly plates. Horizontal bands under the body, which is the
    # detail that says reptile at any distance.
    draw.ellipse((42, 62 + crouch, 88, 82 + crouch), fill=BELLY)
    for band in range(5):
        by = 64 + crouch + band * 4
        draw.line((46 + band, by, 84 - band, by), fill=BELLY_DARK, width=1)

    # Near legs, over the body, so it has depth.
    _leg(draw, (78, 64 + crouch), (90, 78 + crouch), (94, GROUND), 11, SCALE)
    _leg(draw, (50, 64 + crouch), (44, 78 + crouch), (44, GROUND), 9, SCALE)

    # Neck, drawn as a taper from the shoulders. Breathing, it comes
    # forward and down; idle, it stands up.
    if breathing:
        neck = [(56, 48 + crouch), (44, 40), (30, 36), (20, 34)]
    else:
        neck = [(56, 46), (44, 34), (32, 24), (24, 18)]
    for index in range(len(neck) - 1):
        draw.line((neck[index], neck[index + 1]), fill=SCALE,
                  width=max(6, 18 - index * 4))
    for index in range(len(neck) - 1):
        draw.line((neck[index], neck[index + 1]), fill=SCALE_LIT,
                  width=max(3, 12 - index * 4))
    # Throat plates up the underside of the neck.
    for index in range(4):
        along = index / 4.0
        px = neck[0][0] + (neck[-1][0] - neck[0][0]) * along
        py = neck[0][1] + (neck[-1][1] - neck[0][1]) * along + 5
        draw.line((px - 4, py, px + 4, py - 2), fill=BELLY_DARK, width=2)

    # Spines: neck, back, and on down the tail, all one run.
    _spines(draw, list(reversed(neck)) + [(70, 44 + crouch),
                                          (84, 52 + crouch)], 9, SCALE_PALE)

    _head(draw, (neck[-1][0] - 16, neck[-1][1] - 12), breathing, glow)

    if breathing:
        # A few sparks at the mouth, so the frame before the bolt is
        # already crackling. The bolt itself is drawn by the entity.
        for index in range(4):
            sx = 4 + (index * 5 + step * 3) % 14
            sy = neck[-1][1] - 2 + ((index * 7) % 9)
            draw.point((sx, sy), fill=THROAT)
            draw.point((sx + 1, sy + 1), fill=BONE)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [dragon_frame(step, False) for step in range(IDLE_FRAMES)]
    frames += [dragon_frame(step, True, glow=0.4 + 0.6 * step)
               for step in range(BREATH_FRAMES)]
    sheet = Image.new("RGBA", (FRAME_W * len(frames), FRAME_H), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, (index * FRAME_W, 0))
    path = OUT / "blue_dragon.png"
    sheet.save(path)
    print(f"Wrote {path} ({sheet.width}x{sheet.height}, "
          f"{len(frames)} frames of {FRAME_W}x{FRAME_H})")


if __name__ == "__main__":
    main()
