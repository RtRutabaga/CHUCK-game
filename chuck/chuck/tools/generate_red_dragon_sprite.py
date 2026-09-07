"""Generate Phase 13's red dragon: the one that does not stand still.

The blue dragon on the frozen map is a fixed thing that breathes down a
lane. This one is the same animal built for the opposite job -- it
crosses the final encounter in the air, from one side of the arena to
the other, laying a line of fire on the ground under itself. Same
proportions, same construction, same palette discipline; every
difference between the two sheets is a consequence of it flying.

The biggest of those differences is the camera. The blue dragon is
drawn from the side, like every other creature in this game, because
that is what you see when a thing is standing on the same floor you
are. This one is a long way above that floor, and the honest view of
something overhead is from above: back, both wings spread, tail
trailing.

Drawing it in profile was tried first, and it fails for a reason worth
writing down. In profile the wing sweeps through exactly the space the
body and the tail occupy, so the bottom of every wingbeat came back as
one flat red mass with a plank sticking out of it -- tail behind the
membrane, legs behind the tail, nothing readable. From above nothing
overlaps anything: the wings go out to either side, and the beat is
carried by how far out they reach.

    both wings spread, sweeping back from the shoulder
    a long tail behind, longer than the body, finned
    a wedge head with horns raked back off it
    legs folded along the flanks

Twelve frames: six of a wingbeat, then the same six again with the jaw
open and a plume out of it. Making the breath its own separate pose,
the way the blue dragon's is, would have stopped the wings mid-air for
as long as it was breathing -- the exact moment a flying thing must not
look like it has been paused.

Only the left-travelling view is drawn; a pass the other way is this
mirrored. There is no shadow in the frame: this one's shadow falls on
ground it is nowhere near, so the entity draws it separately, and it is
also the clearest thing on screen telling a player where the fire is
about to be.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "hazards"

FRAME_W, FRAME_H = 128, 96
FLY_FRAMES = 6
BREATH_FRAMES = 6

# Red, and hot -- but the animal has to stay darker than what comes out
# of it. The fire is nearly white at the core, so the scales sit well
# below that; a dragon as bright as its own breath is a dragon you
# cannot see the breath of.
SCALE_DARK = (92, 24, 22, 255)
SCALE = (154, 44, 34, 255)
SCALE_LIT = (198, 76, 48, 255)
SCALE_PALE = (232, 132, 80, 255)
MEMBRANE = (124, 34, 34, 255)
MEMBRANE_UP = (176, 62, 46, 255)
MEMBRANE_DOWN = (86, 24, 26, 255)
BONE = (214, 148, 104, 255)
BONE_DIM = (152, 96, 68, 255)
# Horn and claw stay neutral. Warm ones disappeared into the animal;
# these are the only cool colour on it, and they are what keeps the
# silhouette legible against its own fire.
HORN = (226, 214, 200, 255)
HORN_DARK = (138, 126, 116, 255)
# Claws are bone rather than white. At full white there are ten of
# them on this animal and they read as a scatter of loose sparks
# sitting in front of it rather than as parts of it.
CLAW = (214, 196, 172, 255)
EYE = (255, 242, 180, 255)
EYE_DARK = (128, 74, 18, 255)
MOUTH = (54, 20, 18, 255)
# The furnace: what the throat and the plume are made of.
FIRE_DEEP = (206, 62, 22, 255)
FIRE = (255, 148, 40, 255)
FIRE_CORE = (255, 240, 176, 255)

# The centre line the whole animal is built on, and where along it each
# part sits. Travelling left, so the head is at the low end.
SPINE_Y = 48
SNOUT_X = 4
SKULL_X = 28
SHOULDER_X = 60
HAUNCH_X = 86
TAIL_TIP_X = 126


def _beat(step: int) -> float:
    """Where in the wingbeat this frame is: -1 fully up, +1 fully down."""
    return -math.cos(step / FLY_FRAMES * math.tau)


def _wing(draw, beat: float, side: int) -> None:
    """One wing, spread out to `side` (-1 north, +1 south), seen from above.

    From overhead a beating wing does not sweep across the animal, it
    *shortens*: level with the back it is at full span, and at the top
    and bottom of the stroke it is foreshortened in toward the body. So
    the whole beat is carried by reach, which is why this reads at
    sixteen pixels a tile when the profile version did not.

    Reach alone would make the recovery and the power stroke identical,
    though, and a wing that looks the same going both ways looks like a
    loop rather than like work. Two things separate them: the membrane
    is lit on the way up and in shadow on the way down, and the tips
    rake forward on the recovery and back on the power stroke.
    """
    span = 0.42 + 0.58 * math.sqrt(max(0.0, 1.0 - beat * beat))
    rake = -beat * 7.0
    membrane = MEMBRANE_UP if beat < 0 else MEMBRANE_DOWN
    bone = BONE if beat < 0 else BONE_DIM

    def out(distance: float) -> float:
        return SPINE_Y + side * distance * span

    root_front = (SHOULDER_X - 8, out(6))
    root_back = (SHOULDER_X + 14, out(9))
    wrist = (SHOULDER_X + 6 + rake, out(28))
    tips = (
        (SHOULDER_X + 26 + rake, out(41)),
        (SHOULDER_X + 40 + rake * 0.6, out(34)),
        (SHOULDER_X + 44 + rake * 0.3, out(18)),
    )
    draw.polygon((root_front, wrist) + tips + (root_back,), fill=membrane)
    # The leading half a shade up from the trailing, so the wing has a
    # front edge instead of being one flat panel.
    draw.polygon((root_front, wrist, tips[0], tips[1]),
                 fill=MEMBRANE_UP if beat < 0 else MEMBRANE)
    # The arm bone runs shoulder to wrist to the leading tip in one
    # unbroken line. That line is the front edge of the wing and it is
    # most of what stops the shape reading as a leaf.
    draw.line((root_front, wrist), fill=bone, width=4)
    draw.line((wrist, tips[0]), fill=bone, width=3)
    for tip in tips[1:]:
        draw.line((wrist, tip), fill=bone, width=2)
    # A claw at the leading tip: the one detail that says wing and not
    # fin. On the leading finger only, so it does not become a comb.
    draw.polygon((tips[0], (tips[0][0] + 4, tips[0][1] - side * 2),
                  (tips[0][0] + 1, tips[0][1] + side * 3)), fill=HORN_DARK)
    # Scalloped trailing edge between the fingers.
    for index in range(len(tips) - 1):
        first, second = tips[index], tips[index + 1]
        mid = ((first[0] + second[0]) / 2 - 2,
               (first[1] + second[1]) / 2 - side * 2)
        draw.polygon((first, mid, second), fill=(0, 0, 0, 0))


def _leg(draw, hip, knee, foot, side: int, thickness: int, colour) -> None:
    """A leg folded along the flank, seen from above."""
    draw.line((hip, knee), fill=colour, width=thickness)
    draw.line((knee, foot), fill=colour, width=max(3, thickness - 3))
    for toe in range(3):
        angle = math.radians(-40 + toe * 40)
        tip = (foot[0] - 5 * math.cos(angle),
               foot[1] + side * 4 * math.sin(angle))
        draw.line((foot, tip), fill=CLAW, width=1)


def _head(draw, open_jaw: bool) -> None:
    """The skull, from above: a wedge, with the horns doing the work.

    Seen from overhead a dragon's head is nearly all snout, and what
    separates it from a lizard's is the pair of horns raked back off
    the skull and the brow ridges over the eyes. Without them it came
    back as an arrowhead.
    """
    y = SPINE_Y
    draw.polygon(((SNOUT_X, y), (SNOUT_X + 8, y - 6), (SKULL_X, y - 11),
                  (SKULL_X + 6, y), (SKULL_X, y + 11), (SNOUT_X + 8, y + 6)),
                 fill=SCALE)
    draw.polygon(((SNOUT_X + 3, y), (SNOUT_X + 10, y - 4),
                  (SKULL_X - 2, y - 7), (SKULL_X + 2, y),
                  (SKULL_X - 2, y + 7), (SNOUT_X + 10, y + 4)),
                 fill=SCALE_LIT)

    if open_jaw:
        # The jaw hinges open, so from above the mouth is a bright
        # wedge opening forward out of the snout.
        draw.polygon(((SNOUT_X - 2, y), (SNOUT_X + 16, y - 9),
                      (SNOUT_X + 20, y), (SNOUT_X + 16, y + 9)),
                     fill=MOUTH)
        draw.polygon(((SNOUT_X + 2, y), (SNOUT_X + 16, y - 6),
                      (SNOUT_X + 18, y), (SNOUT_X + 16, y + 6)),
                     fill=FIRE_DEEP)
        draw.polygon(((SNOUT_X + 6, y), (SNOUT_X + 15, y - 3),
                      (SNOUT_X + 16, y), (SNOUT_X + 15, y + 3)), fill=FIRE)
        # Teeth along both jaw edges, and they must not meet across the
        # gap: what says "open" is the dark between the two rows.
        for tooth in range(4):
            tx = SNOUT_X + 3 + tooth * 4
            for side in (-1, 1):
                ty = y + side * (2 + tooth * 1.6)
                draw.polygon(((tx, ty), (tx + 3, ty),
                              (tx + 1, ty + side * 3)), fill=HORN)
    else:
        draw.line((SNOUT_X, y, SKULL_X, y), fill=MOUTH, width=1)
        for tooth in (5, 10, 15):
            for side in (-1, 1):
                tx = SNOUT_X + tooth
                draw.polygon(((tx, y + side), (tx + 2, y + side),
                              (tx + 1, y + side * 4)), fill=HORN)

    # The nose horn, standing up off the snout: from above it is a
    # short spike on the centre line, which is all it can be.
    draw.polygon(((SNOUT_X + 6, y - 3), (SNOUT_X + 13, y),
                  (SNOUT_X + 6, y + 3)), fill=HORN)
    draw.polygon(((SNOUT_X + 8, y - 1), (SNOUT_X + 12, y),
                  (SNOUT_X + 8, y + 1)), fill=HORN_DARK)
    # ...and the pair raked back off the skull, one each side. Drawn as
    # tapering blades rather than as lines with a darker line over
    # them: at this size that treatment came back as white hatching,
    # and the head looked like it was wearing a comb.
    for side in (-1, 1):
        for index, (dx, dy, reach, width) in enumerate(
                ((22, 7, 15, 4), (25, 3, 11, 3))):
            base = (SNOUT_X + dx, y + side * dy)
            tip = (base[0] + reach,
                   base[1] + side * (reach * 0.55 + index * 4))
            draw.polygon((
                (base[0], base[1] - side * width / 2),
                (base[0], base[1] + side * width / 2),
                tip,
            ), fill=HORN if index == 0 else HORN_DARK)

    # Brow and eye, each side. The brow is what makes it look like it
    # is looking somewhere.
    for side in (-1, 1):
        ex, ey = SNOUT_X + 18, y + side * 6
        draw.polygon(((ex - 4, ey), (ex + 4, ey - side),
                      (ex + 3, ey + side * 4), (ex - 3, ey + side * 4)),
                     fill=SCALE_DARK)
        box = (ex - 2, ey, ex + 2, ey + side * 3)
        draw.ellipse(box if side > 0 else (box[0], box[3], box[2], box[1]),
                     fill=EYE)
        draw.point((ex, ey + side * 2), fill=EYE_DARK)


def _plume(draw, step: int) -> None:
    """The breath leaving the mouth: forward, and falling as it goes.

    Short on purpose. What burns Chuck is the stripe the entity lays on
    the floor; this is the join between the animal and that stripe, and
    a plume long enough to be a hazard of its own would be a second
    hazard nobody could tell apart from the first.

    Forward rather than straight down, because from directly overhead a
    downward jet is a blob under the chin. Forward and spreading is
    what a jet angled at the ground looks like from up here, and it is
    also what puts the glow on the floor ahead of the animal -- which
    is the warning the whole hazard is built around.
    """
    for index in range(8):
        along = index / 7.0
        px = SNOUT_X + 2 - along * 22
        radius = 4.0 + along * 11.0
        wobble = math.sin(along * 5.0 + step * 1.9) * 2.2
        draw.ellipse((px - radius, SPINE_Y - radius + wobble,
                      px + radius, SPINE_Y + radius + wobble), fill=FIRE_DEEP)
    for index in range(7):
        along = index / 6.0
        px = SNOUT_X + 2 - along * 19
        radius = 2.6 + along * 7.4
        wobble = math.sin(along * 5.0 + step * 1.9) * 1.8
        draw.ellipse((px - radius, SPINE_Y - radius + wobble,
                      px + radius, SPINE_Y + radius + wobble), fill=FIRE)
    for index in range(5):
        along = index / 4.0
        px = SNOUT_X + 1 - along * 13
        radius = 1.6 + along * 3.6
        draw.ellipse((px - radius, SPINE_Y - radius,
                      px + radius, SPINE_Y + radius), fill=FIRE_CORE)


def _spine_ridge(draw, points) -> None:
    """The ridge down the back, as small notches on the centre line.

    From above, spines point at whoever is looking, so they cannot be
    silhouetted -- all that is left of them is a line of pale notches
    down the middle. Drawn any larger than this they stop being scales
    and become chevrons, and what came back was a dragon with arrows
    printed along it.
    """
    for index in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[index], points[index + 1]
        draw.line((x0, y0, x1, y1), fill=SCALE_DARK, width=2)
        if index % 2:
            continue
        size = max(1, 3 - index // 3)
        mid = ((x0 + x1) / 2, (y0 + y1) / 2)
        draw.polygon(((mid[0] - size - 1, mid[1]),
                      (mid[0] + size, mid[1] - size),
                      (mid[0] + size, mid[1] + size)), fill=SCALE_PALE)


def dragon_frame(step: int, breathing: bool) -> Image.Image:
    """One frame, travelling left. A pass the other way is this mirrored."""
    image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    beat = _beat(step)

    # The tail: longer than the body, and the reason this is not a
    # bird. It sweeps to one side and back with the beat, so the animal
    # is steering rather than gliding on rails.
    sweep = beat * 5.0
    tail = [(HAUNCH_X - 2, SPINE_Y), (HAUNCH_X + 10, SPINE_Y + sweep * 0.4),
            (HAUNCH_X + 20, SPINE_Y + sweep * 0.8),
            (HAUNCH_X + 30, SPINE_Y + sweep),
            (TAIL_TIP_X - 6, SPINE_Y + sweep * 1.2)]
    for index in range(len(tail) - 1):
        width = max(3, 15 - index * 3)
        draw.line((tail[index], tail[index + 1]), fill=SCALE_DARK, width=width)
        draw.line((tail[index], tail[index + 1]), fill=SCALE,
                  width=max(1, width - 5))
    # The fin, a flat blade lying along the last of it.
    tip = (TAIL_TIP_X, SPINE_Y + sweep * 1.3)
    draw.polygon(((tip[0] - 18, tip[1]), (tip[0] - 6, tip[1] - 7),
                  (tip[0], tip[1]), (tip[0] - 6, tip[1] + 7)),
                 fill=SCALE_DARK)
    draw.polygon(((tip[0] - 13, tip[1]), (tip[0] - 7, tip[1] - 3),
                  (tip[0] - 3, tip[1]), (tip[0] - 7, tip[1] + 3)), fill=SCALE)

    # Wings under the body on the power stroke, over it on the
    # recovery. One frame's worth of depth, and it costs nothing.
    if beat > 0:
        for side in (-1, 1):
            _wing(draw, beat, side)

    # Legs, folded along the flanks.
    for side in (-1, 1):
        _leg(draw, (HAUNCH_X - 2, SPINE_Y + side * 8),
             (HAUNCH_X + 4, SPINE_Y + side * 17),
             (HAUNCH_X - 6, SPINE_Y + side * 20), side, 7, SCALE_DARK)
        _leg(draw, (SHOULDER_X - 6, SPINE_Y + side * 7),
             (SHOULDER_X - 2, SPINE_Y + side * 14),
             (SHOULDER_X - 12, SPINE_Y + side * 16), side, 6, SCALE_DARK)

    # The body: one mass from the shoulders to the haunch, with the
    # neck tapering out of the front of it.
    draw.ellipse((SHOULDER_X - 14, SPINE_Y - 15, HAUNCH_X + 4, SPINE_Y + 15),
                 fill=SCALE)
    draw.ellipse((SHOULDER_X - 10, SPINE_Y - 11, HAUNCH_X - 2, SPINE_Y + 11),
                 fill=SCALE_LIT)
    draw.line((SHOULDER_X - 6, SPINE_Y, SKULL_X + 6, SPINE_Y),
              fill=SCALE, width=17)
    draw.line((SHOULDER_X - 6, SPINE_Y, SKULL_X + 6, SPINE_Y),
              fill=SCALE_LIT, width=10)

    _head(draw, breathing)

    if beat <= 0:
        for side in (-1, 1):
            _wing(draw, beat, side)

    _spine_ridge(draw, [(SKULL_X + 8, SPINE_Y), (SHOULDER_X - 8, SPINE_Y),
                        (SHOULDER_X + 6, SPINE_Y), (SHOULDER_X + 20, SPINE_Y),
                        (HAUNCH_X - 2, SPINE_Y)] + tail[1:4])

    if breathing:
        _plume(draw, step)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [dragon_frame(step, False) for step in range(FLY_FRAMES)]
    frames += [dragon_frame(step, True) for step in range(BREATH_FRAMES)]
    sheet = Image.new("RGBA", (FRAME_W * len(frames), FRAME_H), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.alpha_composite(frame, (index * FRAME_W, 0))
    path = OUT / "red_dragon.png"
    sheet.save(path)
    print(f"Wrote {path} ({sheet.width}x{sheet.height}, "
          f"{len(frames)} frames of {FRAME_W}x{FRAME_H})")


if __name__ == "__main__":
    main()
