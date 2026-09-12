"""Generate the title screen: the Astral sky, the stone name, and Chuck.

Everything in the game is drawn at 320x180 and scaled up four times.
The title is the one place that gets twice that -- a 640x360 canvas
scaled up twice -- because it is the one place Chuck is shown large
enough for his face to be a face. In play he is twelve pixels wide and
reads as a grey shape in a purple jacket; here he is a hundred and
thirty pixels tall, and the half-lidded stare, the pink ears, the long
snout with its whiskers and its two incisors, the fur, the jacket
two sizes too big and the cigarette are all things a player can
actually see.

It is still pixel art, made the same way as every other asset in the
project: drawn by code, no anti-aliasing, a fixed ramp per material,
dithered between tones rather than blended. What changes is only the
density. The shapes are built from shaded primitives -- capsules for
limbs and tail, ellipsoids for skull and snout -- lit from the upper
left like the rest of the game, and each part gets its own dark rim so
an arm in front of a jacket reads as an arm in front of a jacket.

Chuck is split into layers so he can move without every combination
of pose being baked: the tail behind him (four sway phases), his body
(eyes open and blinking), and the near arm with the cigarette (five
positions from resting to at the mouth). A metadata file records where
the ember and the mouth are in every frame, so the title scene can put
smoke exactly where it comes from.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "title"

CANVAS = (640, 360)

# Where things stand on the canvas. The scene reads these back out of
# the metadata rather than restating them.
LOGO_ORIGIN = (214, 110)
LOGO_CELL = 8
LOGO_GAP = 6
LOGO_DEPTH = 9
CHUCK_ORIGIN = (118, 62)
CHUCK_SIZE = (140, 152)
# How far the head sits down into the collar from where it is drawn.
HEAD_DROP = 7

LIGHT = (-0.52, -0.62, 0.59)            # upper left, towards the viewer
_LEN = math.sqrt(sum(c * c for c in LIGHT))
LIGHT = tuple(c / _LEN for c in LIGHT)

BAYER = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)

# ---------------------------------------------------------------------
# Ramps: deepest shadow first, highlight last.
# ---------------------------------------------------------------------
FUR = ((58, 56, 70), (92, 90, 104), (128, 126, 140), (158, 156, 170),
       (192, 190, 202))
BELLY = ((112, 108, 120), (150, 146, 156), (184, 180, 188),
         (208, 204, 210), (230, 228, 232))
PINK = ((120, 64, 80), (170, 98, 114), (212, 136, 148), (232, 164, 172),
        (246, 196, 198))
JACKET = ((40, 20, 66), (70, 36, 108), (106, 58, 156), (136, 84, 190),
          (170, 124, 218))
EYE = ((14, 12, 18), (30, 26, 36))
OUTLINE = (18, 14, 26)
WHISKER = (214, 212, 222)
TOOTH = (236, 214, 150)
PAPER = (240, 238, 228)
PAPER_SHADE = (196, 192, 186)
FILTER = (214, 150, 78)
FILTER_DARK = (164, 104, 52)
ASH = (150, 146, 144)
EMBER = (255, 140, 52)
PIN = (232, 196, 88)


def _hash(x: int, y: int, salt: int = 0) -> int:
    value = (x * 374761393 + y * 668265263 + salt * 2147483647) & 0xFFFFFFFF
    value = (value ^ (value >> 13)) * 1274126177 & 0xFFFFFFFF
    return value ^ (value >> 16)


def _tone(ramp, intensity: float, x: int, y: int):
    """Pick a ramp colour, dithered between the two nearest tones."""
    scaled = max(0.0, min(0.999, intensity)) * (len(ramp) - 1)
    low = int(scaled)
    frac = scaled - low
    threshold = (BAYER[y % 4][x % 4] + 0.5) / 16.0
    index = low + 1 if frac > threshold else low
    return ramp[min(index, len(ramp) - 1)]


class Piece:
    """One shaded, rimmed shape built from overlapping primitives.

    Primitives in a piece are unioned: where two cover the same pixel,
    the one whose surface is nearer the viewer supplies the normal. So
    a snout made of three ellipsoids reads as one snout, and the rim is
    drawn round the outside of the union rather than round every blob.
    """

    def __init__(self, ramp, *, fur: bool = False, rim: bool = True,
                 ambient: float = 0.22, salt: int = 0) -> None:
        self.ramp = ramp
        self.fur = fur
        self.rim = rim
        self.ambient = ambient
        self.salt = salt
        self.pixels: dict[tuple[int, int], tuple[float, float, float]] = {}

    def _offer(self, x: int, y: int, normal) -> None:
        current = self.pixels.get((x, y))
        if current is None or normal[2] > current[2]:
            self.pixels[(x, y)] = normal

    def capsule(self, p0, p1, r0: float, r1: float) -> "Piece":
        (x0, y0), (x1, y1) = p0, p1
        big = max(r0, r1)
        left, right = int(min(x0, x1) - big) - 1, int(max(x0, x1) + big) + 2
        top, bottom = int(min(y0, y1) - big) - 1, int(max(y0, y1) + big) + 2
        dx, dy = x1 - x0, y1 - y0
        length_sq = dx * dx + dy * dy or 1e-6
        for y in range(top, bottom):
            for x in range(left, right):
                px, py = x + 0.5, y + 0.5
                t = max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy)
                                 / length_sq))
                cx, cy = x0 + dx * t, y0 + dy * t
                r = r0 + (r1 - r0) * t
                ox, oy = (px - cx) / r, (py - cy) / r
                d = ox * ox + oy * oy
                if d <= 1.0:
                    self._offer(x, y, (ox, oy, math.sqrt(1.0 - d)))
        return self

    def ellipse(self, centre, rx: float, ry: float) -> "Piece":
        cx, cy = centre
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                ox = (x + 0.5 - cx) / rx
                oy = (y + 0.5 - cy) / ry
                d = ox * ox + oy * oy
                if d <= 1.0:
                    self._offer(x, y, (ox, oy, math.sqrt(1.0 - d)))
        return self

    def polygon(self, points, bulge: float = 0.35) -> "Piece":
        """A flat panel, shaded as a gently curved sheet."""
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        half_w = (max(xs) - min(xs)) / 2 or 1
        half_h = (max(ys) - min(ys)) / 2 or 1
        for y in range(int(min(ys)), int(max(ys)) + 1):
            for x in range(int(min(xs)), int(max(xs)) + 1):
                if _inside(points, x + 0.5, y + 0.5):
                    ox = (x + 0.5 - cx) / half_w * bulge
                    oy = (y + 0.5 - cy) / half_h * bulge
                    z = math.sqrt(max(0.0, 1.0 - ox * ox - oy * oy))
                    self._offer(x, y, (ox, oy, z))
        return self

    def paint(self, image: Image.Image) -> None:
        width, height = image.size
        pixels = image.load()
        for (x, y), (nx, ny, nz) in self.pixels.items():
            if not (0 <= x < width and 0 <= y < height):
                continue
            light = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
            intensity = self.ambient + (1.0 - self.ambient) * max(0.0, light)
            if self.fur:
                h = _hash(x, y, self.salt)
                # Grain: short dark strokes and the odd lit hair. Taken
                # off the intensity rather than painted on top, so it
                # follows the form instead of sitting on it.
                if h % 11 == 0:
                    intensity -= 0.22
                elif h % 17 == 0:
                    intensity += 0.18
                elif _hash(x - 1, y - 1, self.salt) % 11 == 0:
                    intensity -= 0.14
            colour = _tone(self.ramp, intensity, x, y)
            if self.rim and any((x + ox, y + oy) not in self.pixels
                                for ox, oy in ((1, 0), (-1, 0), (0, 1),
                                               (0, -1))):
                colour = self.ramp[0]
            pixels[x, y] = colour + (255,)


def _inside(points, x: float, y: float) -> bool:
    inside = False
    j = len(points) - 1
    for i in range(len(points)):
        xi, yi = points[i]
        xj, yj = points[j]
        if (yi > y) != (yj > y):
            if x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
                inside = not inside
        j = i
    return inside


def _line(image: Image.Image, p0, p1, colour) -> None:
    (x0, y0), (x1, y1) = p0, p1
    steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    pixels = image.load()
    for step in range(steps + 1):
        t = step / steps
        x = round(x0 + (x1 - x0) * t)
        y = round(y0 + (y1 - y0) * t)
        if 0 <= x < image.width and 0 <= y < image.height:
            pixels[x, y] = colour + (255,) if len(colour) == 3 else colour


def _outline(image: Image.Image) -> Image.Image:
    """A one-pixel dark silhouette round everything opaque."""
    result = image.copy()
    src = image.load()
    dst = result.load()
    for y in range(image.height):
        for x in range(image.width):
            if src[x, y][3]:
                continue
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + ox, y + oy
                if 0 <= nx < image.width and 0 <= ny < image.height \
                        and src[nx, ny][3]:
                    dst[x, y] = OUTLINE + (255,)
                    break
    return result


# ---------------------------------------------------------------------
# Chuck
# ---------------------------------------------------------------------
def _blank():
    return Image.new("RGBA", CHUCK_SIZE, (0, 0, 0, 0))


def chuck_tail(phase: int) -> Image.Image:
    """The tail, behind everything, curling round onto the ground.

    Four phases of a lazy sway at the tip. The root never moves: it is
    hidden behind his hip, and a tail that swings from the base is a
    rope somebody is pulling.
    """
    image = _blank()
    sway = math.sin(phase / 4 * math.tau)
    points = [(76, 110), (100, 122), (112, 140),
              (126 + 5 * sway, 143 - 2 * sway)]
    piece = Piece(PINK, salt=3, ambient=0.3)
    segments = 22
    previous = None
    for index in range(segments + 1):
        t = index / segments
        a, b, c, d = points
        x = ((1 - t) ** 3 * a[0] + 3 * (1 - t) ** 2 * t * b[0]
             + 3 * (1 - t) * t * t * c[0] + t ** 3 * d[0])
        y = ((1 - t) ** 3 * a[1] + 3 * (1 - t) ** 2 * t * b[1]
             + 3 * (1 - t) * t * t * c[1] + t ** 3 * d[1])
        radius = 5.2 - 3.8 * t
        if previous is not None:
            piece.capsule(previous[0], (x, y), previous[1], radius)
        previous = ((x, y), radius)
    piece.paint(image)
    # Rings: a rat's tail is scaled, and at this size the scales are the
    # difference between a tail and a worm.
    pixels = image.load()
    for index in range(2, segments, 2):
        t = index / segments
        a, b, c, d = points
        x = ((1 - t) ** 3 * a[0] + 3 * (1 - t) ** 2 * t * b[0]
             + 3 * (1 - t) * t * t * c[0] + t ** 3 * d[0])
        y = ((1 - t) ** 3 * a[1] + 3 * (1 - t) ** 2 * t * b[1]
             + 3 * (1 - t) * t * t * c[1] + t ** 3 * d[1])
        px, py = round(x), round(y)
        if 0 <= px < image.width and 0 <= py < image.height \
                and pixels[px, py][3]:
            pixels[px, py] = PINK[1] + (255,)
    return _outline(image)


def chuck_body(blink: bool) -> Image.Image:
    """Everything but the tail and the arm with the cigarette.

    He faces the viewer. The first version drew him side-on, turned
    away towards his cigarette, and what showed was the back of the
    jacket and a pair of legs coming out from under it at angles that
    only work on something facing the other way. Front-on, the jacket
    hangs open over his chest, both lapels stand up either side of his
    neck, and only the head turns -- three-quarters, towards the hand
    with the cigarette in it.

    He is leaning back on the C: shoulders over towards the stone, hips
    forward, long legs crossed out in front. The far arm goes back over
    the top of the letter and hangs down its face, which is what makes
    it a lean rather than a rat standing next to a word.
    """
    image = _blank()

    # --- the far arm, back over the top of the C ----------------------
    sleeve = Piece(JACKET, salt=11, ambient=0.16)
    sleeve.capsule((94, 64), (110, 42), 9.0, 8.0)
    sleeve.capsule((110, 42), (127, 46), 8.0, 6.4)
    sleeve.paint(image)
    cuff = Piece(JACKET, ambient=0.08)
    cuff.capsule((126, 46), (130, 48), 5.8, 5.4)
    cuff.paint(image)
    hand = Piece(PINK, salt=12, ambient=0.3)
    hand.capsule((131, 48), (134, 55), 4.4, 3.8)
    for finger in range(4):
        base = (130.5 + finger * 2.1, 55)
        hand.capsule(base, (base[0] + 0.4, 61 + (finger % 2)), 1.6, 1.2)
    hand.paint(image)

    # --- legs: long, crossed, stretched out away from the stone --------
    # The first pass put both legs down the same line and they merged
    # into one thick one. Knees apart, shins crossing, feet pointing
    # opposite ways: that is what reads as crossed ankles.
    far_leg = Piece(FUR, fur=True, salt=21, ambient=0.16)
    far_leg.capsule((74, 108), (70, 127), 11, 7)
    far_leg.capsule((70, 127), (52, 144), 7, 4)
    far_leg.paint(image)
    far_foot = Piece(PINK, salt=22, ambient=0.3)
    far_foot.capsule((52, 145), (36, 147), 4, 2.6)
    for toe in range(3):
        far_foot.capsule((37 - toe, 146 + toe * 0.6), (33 - toe, 148), 1.4,
                         1.0)
    far_foot.paint(image)

    # --- the body under the jacket ------------------------------------
    torso = Piece(FUR, fur=True, salt=30)
    torso.capsule((64, 106), (80, 64), 17, 17)
    torso.paint(image)

    chest = Piece(BELLY, fur=True, salt=32, ambient=0.3)
    chest.capsule((66, 106), (76, 62), 9.5, 9)
    chest.paint(image)


    # --- the jacket, open, two sizes too big ---------------------------
    # The panel on his right (the viewer's left) faces the light; the
    # other one turns away from it, towards the stone.
    near_panel = Piece(JACKET, salt=33)
    near_panel.polygon([(50, 58), (66, 56), (60, 88), (58, 116), (44, 114),
                        (46, 84)], bulge=0.45)
    near_panel.paint(image)
    far_panel = Piece(JACKET, salt=34, ambient=0.14)
    far_panel.polygon([(84, 56), (102, 58), (98, 88), (90, 114), (74, 116),
                       (80, 86)], bulge=0.45)
    far_panel.paint(image)

    pixels = image.load()
    # Folds and seams: cloth that has no creases in it is plastic.
    for (a, b) in (((52, 70), (50, 100)), ((57, 96), (54, 112)),
                   ((95, 66), (92, 96)), ((86, 96), (82, 112))):
        _line(image, a, b, JACKET[1])
    # A pocket flap on each side.
    _line(image, (47, 98), (57, 97), JACKET[0])
    _line(image, (47, 99), (57, 98), JACKET[3])
    _line(image, (80, 98), (92, 98), JACKET[0])
    _line(image, (80, 99), (92, 99), JACKET[2])
    # The open edges, lit where they fold back.
    _line(image, (66, 58), (59, 114), JACKET[4])
    _line(image, (83, 58), (76, 114), JACKET[1])
    # The hem, a darker band.
    _line(image, (45, 114), (58, 116), JACKET[0])
    _line(image, (75, 116), (90, 114), JACKET[0])

    near_leg = Piece(FUR, fur=True, salt=41)
    near_leg.capsule((58, 110), (46, 126), 11, 7)
    near_leg.capsule((46, 126), (64, 143), 7, 4)
    near_leg.paint(image)
    near_foot = Piece(PINK, salt=42, ambient=0.3)
    near_foot.capsule((64, 144), (80, 148), 4, 2.6)
    for toe in range(3):
        near_foot.capsule((79 + toe, 147 + toe * 0.5), (83 + toe, 149), 1.4,
                          1.0)
    near_foot.paint(image)

    # Popped collar, both sides of the neck.
    neck = Piece(FUR, fur=True, salt=35)
    neck.capsule((72, 50), (76, 58), 8, 9)
    neck.paint(image)
    lapel_near = Piece(JACKET, salt=36, ambient=0.3)
    lapel_near.polygon([(56, 48), (68, 56), (64, 72), (54, 60)], bulge=0.5)
    lapel_near.paint(image)
    lapel_far = Piece(JACKET, salt=37, ambient=0.2)
    lapel_far.polygon([(92, 46), (82, 56), (86, 72), (96, 58)], bulge=0.5)
    lapel_far.paint(image)
    for x, y, c in ((60, 60, PIN), (61, 60, PIN), (60, 61, (180, 142, 60))):
        pixels[x, y] = c + (255,)

    # --- head, three-quarters towards the cigarette --------------------
    # Drawn on its own sheet and set down onto the collar. At first it
    # sat where the design put it and a rat grew a neck, which rats do
    # not have: the head goes straight into the shoulders.
    body = image
    image = _blank()
    far_ear = Piece(FUR, salt=51)
    far_ear.ellipse((70, 12), 8, 10)
    far_ear.paint(image)
    far_inner = Piece(PINK, rim=False, ambient=0.35)
    far_inner.ellipse((70, 13), 4.5, 6.5)
    far_inner.paint(image)

    skull = Piece(FUR, fur=True, salt=52)
    skull.ellipse((76, 32), 17, 15)
    skull.ellipse((61, 33), 12, 9.5)
    skull.ellipse((51, 32), 8.5, 7)
    skull.ellipse((44, 31), 5, 4.2)
    skull.paint(image)

    cheek = Piece(FUR[1:] + (BELLY[2],), fur=True, rim=False, salt=53,
                  ambient=0.3)
    cheek.ellipse((68, 39), 9, 5)
    cheek.paint(image)

    near_ear = Piece(FUR, salt=54)
    near_ear.ellipse((90, 18), 11, 13)
    near_ear.paint(image)
    near_inner = Piece(PINK, rim=False, ambient=0.35)
    near_inner.ellipse((89, 19), 7, 9)
    near_inner.paint(image)

    pixels = image.load()

    # The eye: half-lidded, always. The lid is fur with a dark edge; drawn
    # as a black band it came out as sunglasses.
    ex, ey = 64.5, 27.5
    if blink:
        for x in range(60, 70):
            pixels[x, 28] = FUR[0] + (255,)
        for x in range(61, 69):
            pixels[x, 27] = FUR[3] + (255,)
    else:
        for y in range(24, 32):
            for x in range(59, 71):
                ox = (x + 0.5 - ex) / 4.6
                oy = (y + 0.5 - ey) / 2.9
                if ox * ox + oy * oy <= 1.0:
                    pixels[x, y] = EYE[0] + (255,)
        for x in range(59, 71):
            if pixels[x, 26][:3] == EYE[0]:
                pixels[x, 25] = FUR[3] + (255,)
                pixels[x, 26] = FUR[0] + (255,)
        pixels[63, 27] = (210, 214, 230, 255)
        for x in range(61, 68):
            pixels[x, 31] = FUR[1] + (255,)
    _line(image, (58, 23), (69, 22), FUR[1])

    # Nose, mouth, incisors.
    nose = Piece(PINK, ambient=0.4)
    nose.ellipse((40, 30), 3.2, 2.6)
    nose.paint(image)
    pixels[39, 29] = PINK[4] + (255,)
    _line(image, (43, 35), (55, 38), FUR[0])
    for x in (44, 45):
        pixels[x, 36] = TOOTH + (255,)
        pixels[x, 37] = TOOTH + (255,)
    pixels[44, 38] = (196, 170, 104, 255)

    for end in ((26, 23), (24, 30), (27, 37)):
        _line(image, (46, 31), end, (196, 194, 206))
    for end in ((31, 20), (32, 40)):
        _line(image, (48, 33), end, (140, 138, 152))

    body.alpha_composite(image, (0, HEAD_DROP))
    return _outline(body)


def _arm_pose(amount: float):
    """Elbow, hand and cigarette for a raise between 0 (rest) and 1."""
    ease = amount * amount * (3 - 2 * amount)

    def mix(a, b):
        return (a[0] + (b[0] - a[0]) * ease, a[1] + (b[1] - a[1]) * ease)

    elbow = mix((44, 94), (40, 76))
    hand = mix((38, 78), (46, 44 + HEAD_DROP))
    angle = math.radians(-140 + (176 + 140) * ease)
    filter_end = mix((36, 75), (44, 37 + HEAD_DROP))
    return elbow, hand, angle, filter_end


def chuck_arm(amount: float) -> tuple[Image.Image, dict]:
    """The near arm and the cigarette, somewhere between rest and a drag."""
    image = _blank()
    shoulder = (56, 64)
    elbow, hand, angle, filter_end = _arm_pose(amount)
    wrist = (elbow[0] + (hand[0] - elbow[0]) * 0.78,
             elbow[1] + (hand[1] - elbow[1]) * 0.78)

    sleeve = Piece(JACKET, salt=61)
    sleeve.capsule(shoulder, elbow, 9.5, 8)
    sleeve.capsule(elbow, wrist, 8, 6.4)
    sleeve.paint(image)
    cuff = Piece(JACKET, ambient=0.1)
    cuff.capsule(wrist, (wrist[0] + (hand[0] - wrist[0]) * 0.3,
                         wrist[1] + (hand[1] - wrist[1]) * 0.3), 5.8, 5.4)
    cuff.paint(image)

    # The cigarette, drawn before the fingers so they close round it.
    direction = (math.cos(angle), math.sin(angle))
    length = 15
    ember_point = (filter_end[0] + direction[0] * length,
                   filter_end[1] + direction[1] * length)
    pixels = image.load()
    for step in range(length + 1):
        t = step / length
        x = filter_end[0] + direction[0] * length * t
        y = filter_end[1] + direction[1] * length * t
        for thickness in (0, 1):
            px, py = round(x), round(y + thickness)
            if not (0 <= px < image.width and 0 <= py < image.height):
                continue
            if step <= 4:
                colour = FILTER if (step + thickness) % 3 else FILTER_DARK
            elif step >= length - 1:
                colour = ASH
            else:
                colour = PAPER if thickness == 0 else PAPER_SHADE
            pixels[px, py] = colour + (255,)
    tip = (round(ember_point[0]), round(ember_point[1]))
    for ox, oy in ((0, 0), (0, 1)):
        pixels[tip[0] + ox, tip[1] + oy] = EMBER + (255,)

    fingers = Piece(PINK, salt=62, ambient=0.32)
    fingers.capsule(wrist, hand, 4.6, 4.0)
    for index in range(3):
        base = (hand[0] - 2 + index * 2.2, hand[1] - 2 + index * 1.2)
        fingers.capsule(base, (base[0] - 3.2, base[1] + 1.4), 1.7, 1.3)
    fingers.capsule((hand[0] + 1, hand[1] - 3), (hand[0] - 2, hand[1] - 5),
                    1.6, 1.2)                               # thumb
    fingers.paint(image)

    mouth = (43, 37 + HEAD_DROP)
    return _outline(image), {
        "ember": [round(ember_point[0], 1), round(ember_point[1], 1)],
        "mouth": list(mouth),
    }


# ---------------------------------------------------------------------
# The name
# ---------------------------------------------------------------------
LETTERS = {
    "C": (
        ".######",
        "#######",
        "###....",
        "##.....",
        "##.....",
        "##.....",
        "###....",
        "#######",
        ".######",
    ),
    "H": (
        "##...##",
        "##...##",
        "##...##",
        "#######",
        "#######",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
    ),
    "U": (
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        "##...##",
        "###.###",
        "#######",
        ".#####.",
    ),
    "K": (
        "##...##",
        "##..###",
        "##.###.",
        "#####..",
        "####...",
        "#####..",
        "##.###.",
        "##..###",
        "##...##",
    ),
}

STONE_TOP = (238, 228, 208)
STONE_MID = (214, 206, 206)
STONE_LOW = (184, 186, 222)
STONE_SPECK = (158, 148, 160)
STONE_RUST = (196, 158, 120)
STONE_CRACK = (104, 96, 124)
STONE_EDGE_LIT = (252, 248, 236)
STONE_EDGE_DARK = (150, 150, 190)
SIDE_RAMP = ((34, 30, 88), (48, 44, 124), (70, 62, 160), (98, 88, 188))


def logo() -> tuple[Image.Image, dict]:
    """CHUCK in cracked stone blocks, with depth going down and right."""
    word = "CHUCK"
    letter_w = 7 * LOGO_CELL
    letter_h = 9 * LOGO_CELL
    width = len(word) * letter_w + (len(word) - 1) * LOGO_GAP + LOGO_DEPTH + 2
    height = letter_h + LOGO_DEPTH + 2
    face = set()
    for index, char in enumerate(word):
        left = index * (letter_w + LOGO_GAP)
        rows = LETTERS[char]
        for row, line in enumerate(rows):
            for col, cell in enumerate(line):
                if cell != "#":
                    continue
                for y in range(LOGO_CELL):
                    for x in range(LOGO_CELL):
                        face.add((left + col * LOGO_CELL + x,
                                  row * LOGO_CELL + y))

    # Chips: corners knocked off, and the odd bite out of an edge. Taken
    # out of the face before the depth is built, so the dark side shows
    # through where the stone broke.
    def edge(x, y):
        return any((x + ox, y + oy) not in face
                   for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)))

    for (x, y) in list(face):
        if (x, y) not in face:
            continue
        neighbours = sum((x + ox, y + oy) in face
                         for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if neighbours == 2 and _hash(x, y, 7) % 3 == 0:
            for oy in range(3):
                for ox in range(3 - oy):
                    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                        face.discard((x + ox * sx, y + oy * sy))
    for (x, y) in list(face):
        if edge(x, y) and _hash(x, y, 9) % 97 == 0:
            for ox in range(-2, 3):
                for oy in range(-2, 3):
                    if abs(ox) + abs(oy) <= 2:
                        face.discard((x + ox, y + oy))

    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = image.load()

    # Depth, back to front.
    for depth in range(LOGO_DEPTH, 0, -1):
        colour = SIDE_RAMP[min(len(SIDE_RAMP) - 1,
                               (LOGO_DEPTH - depth) * len(SIDE_RAMP)
                               // LOGO_DEPTH)]
        for (x, y) in face:
            px, py = x + depth, y + depth
            if 0 <= px < width and 0 <= py < height:
                shade = colour
                if _hash(px, py, 13) % 9 == 0:
                    shade = SIDE_RAMP[0]
                pixels[px, py] = shade + (255,)

    # The face.
    for (x, y) in face:
        t = y / letter_h
        if t < 0.5:
            base = [STONE_TOP[i] + (STONE_MID[i] - STONE_TOP[i]) * t * 2
                    for i in range(3)]
        else:
            base = [STONE_MID[i] + (STONE_LOW[i] - STONE_MID[i]) * (t - 0.5) * 2
                    for i in range(3)]
        colour = tuple(round(c) for c in base)
        h = _hash(x, y, 17)
        if h % 7 == 0:
            colour = STONE_SPECK
        elif h % 23 == 0:
            colour = STONE_RUST
        elif h % 5 == 0:
            colour = tuple(min(255, c + 12) for c in colour)
        # A two-pixel bevel: lit along the top and left of each block,
        # dark along the bottom and right.
        if (x, y - 1) not in face or (x - 1, y) not in face:
            colour = STONE_EDGE_LIT
        elif (x, y + 1) not in face or (x + 1, y) not in face:
            colour = STONE_EDGE_DARK
        elif (x, y - 2) not in face or (x - 2, y) not in face:
            colour = tuple(min(255, c + 10) for c in colour)
        elif (x, y + 2) not in face or (x + 2, y) not in face:
            colour = tuple(max(0, c - 22) for c in colour)
        pixels[x, y] = colour + (255,)

    # Cracks: short random walks in from the edges, each with a lit lip
    # on one side so it reads as a split rather than a pencil line.
    starts = sorted((x, y) for (x, y) in face
                    if edge(x, y) and _hash(x, y, 29) % 61 == 0)
    for sx, sy in starts:
        x, y = sx, sy
        direction = _hash(sx, sy, 31) % 4
        for step in range(8 + _hash(sx, sy, 37) % 14):
            if (x, y) not in face:
                break
            pixels[x, y] = STONE_CRACK + (255,)
            if (x + 1, y + 1) in face:
                pixels[x + 1, y + 1] = STONE_EDGE_LIT + (255,)
            turn = _hash(x, y, 41) % 5
            if turn == 0:
                direction = (direction + 1) % 4
            elif turn == 1:
                direction = (direction + 3) % 4
            dx, dy = ((1, 1), (-1, 1), (1, 0), (0, 1))[direction]
            x, y = x + dx, y + dy

    top_of_c = LOGO_ORIGIN[1]
    return _outline(image), {
        "origin": list(LOGO_ORIGIN),
        "size": [width, height],
        "top_of_c": top_of_c,
    }


# ---------------------------------------------------------------------
# The sky
# ---------------------------------------------------------------------
def background() -> tuple[Image.Image, dict]:
    """The Astral sky: two ribbons of nebula and a great many stars.

    The first version thresholded a busy grain field into hard tone
    bands and the ribbons came back spotted like a leopard. Now the
    density is one smooth value, pushed through a five-tone ramp with
    ordered dithering between neighbours -- the same way every lit
    surface in the game is shaded -- and the grain only nudges it.
    """
    width, height = CANVAS
    image = Image.new("RGBA", CANVAS, (0, 0, 0, 255))
    pixels = image.load()
    ramp = ((5, 6, 18), (12, 16, 50), (28, 40, 116), (70, 44, 142),
            (116, 98, 204))

    for y in range(height):
        for x in range(width):
            u = x / width
            v = y / height
            ribbon_a = math.exp(-((v - (0.16 + 0.5 * u * u
                                        + 0.05 * math.sin(u * 8.0))) ** 2)
                                / 0.014)
            ribbon_b = math.exp(-((v - (0.97 - 0.58 * (1 - u) ** 2
                                        + 0.05 * math.sin(u * 6.0 + 1.3))) ** 2)
                                / 0.022)
            # Summed sines at two scales: the long wisps and the fine
            # tangle inside them. Anything modular draws stripes.
            wisp = (math.sin(x * 0.021 + y * 0.034)
                    + math.sin(x * 0.013 - y * 0.027 + 1.9)) / 2.0
            tangle = (math.sin(x * 0.083 + y * 0.051 + 0.4)
                      + math.sin(x * 0.047 - y * 0.091 + 2.2)) / 2.0
            density = max(ribbon_a * (1.0 - 0.55 * u), ribbon_b)
            density *= 0.72 + 0.22 * wisp + 0.12 * tangle
            centre = math.exp(-(((u - 0.5) / 0.3) ** 2
                                + ((v - 0.56) / 0.34) ** 2))
            density *= 1.0 - 0.8 * centre
            colour = _tone(ramp, density * 1.15, x, y)
            # Dust: the nebula is made of stars, too small to be stars.
            if density > 0.3 and _hash(x, y, 71) % 13 == 0:
                colour = (150, 162, 236)
            pixels[x, y] = colour + (255,)

    sparkles = []
    for index in range(620):
        h = _hash(index, 3, 101)
        x, y = h % width, (h >> 11) % height
        level = (h >> 20) % 100
        if level < 70:
            colour = (120, 130, 190)
        elif level < 92:
            colour = (200, 206, 250)
        else:
            colour = (255, 255, 255)
        pixels[x, y] = colour + (255,)
    for index in range(46):
        h = _hash(index, 5, 211)
        x, y = 2 + h % (width - 4), 2 + (h >> 11) % (height - 4)
        for ox, oy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            pixels[x + ox, y + oy] = (230, 234, 255, 255)
    for index in range(16):
        h = _hash(index, 7, 307)
        x, y = 10 + h % (width - 20), 10 + (h >> 11) % (height - 20)
        arm = 3 + (h >> 22) % 5
        sparkles.append([x, y, arm,
                         round(((h >> 5) % 100) / 100 * math.tau, 3)])
        _sparkle(pixels, x, y, arm, 255)
    return image, {"sparkles": sparkles}


def _sparkle(pixels, x: int, y: int, arm: int, alpha: int) -> None:
    pixels[x, y] = (255, 255, 255, alpha)
    for step in range(1, arm + 1):
        fade = 1.0 - step / (arm + 1)
        colour = (round(170 + 85 * fade), round(190 + 65 * fade), 255)
        for sx, sy in ((step, 0), (-step, 0), (0, step), (0, -step)):
            pixels[x + sx, y + sy] = colour + (alpha,)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        pixels[x + sx, y + sy] = (160, 180, 250, alpha)


ARM_FRAMES = 5
TAIL_FRAMES = 4


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sky, sky_meta = background()
    sky.save(OUT / "background.png")
    name, name_meta = logo()
    name.save(OUT / "logo.png")
    for phase in range(TAIL_FRAMES):
        chuck_tail(phase).save(OUT / f"chuck_tail_{phase}.png")
    chuck_body(False).save(OUT / "chuck_body.png")
    chuck_body(True).save(OUT / "chuck_body_blink.png")
    arms = []
    for index in range(ARM_FRAMES):
        image, meta = chuck_arm(index / (ARM_FRAMES - 1))
        image.save(OUT / f"chuck_arm_{index}.png")
        arms.append(meta)
    meta = {
        "canvas": list(CANVAS),
        "logo": name_meta,
        "chuck_origin": list(CHUCK_ORIGIN),
        "arm_frames": arms,
        "tail_frames": TAIL_FRAMES,
        **sky_meta,
    }
    (OUT / "title.json").write_text(json.dumps(meta, indent=2) + "\n",
                                    encoding="utf-8")
    print(f"Wrote title art to {OUT}")


if __name__ == "__main__":
    main()
