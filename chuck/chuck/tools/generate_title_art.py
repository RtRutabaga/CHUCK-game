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
    points = [(84, 106), (104, 118), (114, 136),
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

    He is leaning back on the C: shoulders over towards the stone, hips
    and feet out away from it, ankles crossed. The far arm goes up and
    over the top of the letter and hangs down its face, which is what
    makes it a lean rather than a rat standing next to a word.
    """
    image = _blank()

    # --- the far arm, over the top of the C ---------------------------
    sleeve = Piece(JACKET, salt=11)
    sleeve.capsule((88, 60), (110, 40), 9.5, 8.2)
    sleeve.capsule((110, 40), (127, 46), 8.2, 6.4)
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

    # --- legs, crossed at the ankle ---------------------------------
    far_leg = Piece(FUR, fur=True, salt=21)
    far_leg.capsule((76, 104), (79, 124), 13, 8)
    far_leg.capsule((79, 124), (62, 142), 8, 4)
    far_leg.paint(image)
    far_foot = Piece(PINK, salt=22, ambient=0.3)
    far_foot.capsule((63, 143), (47, 146), 4, 2.6)
    for toe in range(3):
        far_foot.capsule((48 - toe, 145 + toe * 0.6), (44 - toe, 147), 1.4,
                         1.0)
    far_foot.paint(image)

    # --- the jacket, two sizes too big --------------------------------
    jacket = Piece(JACKET, salt=31)
    jacket.capsule((84, 62), (70, 104), 18, 19)
    jacket.polygon([(60, 54), (100, 52), (96, 112), (52, 114)], bulge=0.5)
    jacket.paint(image)

    belly = Piece(BELLY, fur=True, salt=32, ambient=0.3)
    belly.ellipse((62, 86), 10.5, 23)
    belly.paint(image)

    near_panel = Piece(JACKET, salt=33)
    near_panel.polygon([(50, 60), (58, 62), (54, 114), (45, 112)], bulge=0.6)
    near_panel.paint(image)

    # Folds, a seam and a pocket: the jacket is cloth, and cloth that
    # has no creases in it is plastic.
    for (a, b) in (((84, 70), (88, 98)), ((75, 86), (78, 106)),
                   ((93, 60), (95, 78))):
        _line(image, a, b, JACKET[1])
    _line(image, (72, 94), (86, 92), JACKET[0])
    _line(image, (72, 95), (86, 93), JACKET[3])
    for y in range(66, 110, 4):
        image.load()[90, y] = JACKET[1] + (255,)

    collar = Piece(JACKET, salt=34, ambient=0.3)
    collar.capsule((58, 54), (72, 58), 5, 4)
    collar.capsule((72, 58), (94, 50), 4, 6)
    collar.paint(image)
    pixels = image.load()
    for x, y, c in ((65, 63, PIN), (66, 63, PIN), (65, 64, (180, 142, 60))):
        pixels[x, y] = c + (255,)

    near_leg = Piece(FUR, fur=True, salt=41)
    near_leg.capsule((60, 106), (56, 126), 13, 8)
    near_leg.capsule((56, 126), (72, 142), 8, 4)
    near_leg.paint(image)
    near_foot = Piece(PINK, salt=42, ambient=0.3)
    near_foot.capsule((72, 143), (89, 146), 4, 2.6)
    for toe in range(3):
        near_foot.capsule((88 + toe, 145 + toe * 0.6), (92 + toe, 147), 1.4,
                          1.0)
    near_foot.paint(image)

    # --- head ---------------------------------------------------------
    far_ear = Piece(FUR, salt=51)
    far_ear.ellipse((90, 17), 12, 14)
    far_ear.paint(image)
    far_inner = Piece(PINK, rim=False, ambient=0.35)
    far_inner.ellipse((88, 19), 7.5, 9.5)
    far_inner.paint(image)

    skull = Piece(FUR, fur=True, salt=52)
    skull.ellipse((74, 34), 19, 16)
    skull.ellipse((58, 40), 13, 10.5)
    skull.ellipse((47, 43), 9, 7.5)
    skull.ellipse((40, 45), 5.5, 4.5)
    skull.paint(image)

    # The cheek, a shade paler than the head and no more. In belly-white
    # it came out as a moustache.
    cheek = Piece(FUR[1:] + (BELLY[2],), fur=True, rim=False, salt=53,
                  ambient=0.3)
    cheek.ellipse((63, 46), 8, 4.5)
    cheek.paint(image)

    near_ear = Piece(FUR, salt=54)
    near_ear.ellipse((70, 13), 10, 12)
    near_ear.paint(image)
    near_inner = Piece(PINK, rim=False, ambient=0.35)
    near_inner.ellipse((68, 15), 6, 8)
    near_inner.paint(image)

    pixels = image.load()

    # The eye. Half-lidded, always: the heavy upper lid is most of the
    # expression, and a wide round eye on this face would be somebody
    # else's rat. The lid is fur rather than a black band -- drawn dark
    # all the way across, it came out as a pair of sunglasses.
    ex, ey = 56.5, 33.0
    if blink:
        for x in range(52, 62):
            pixels[x, 33] = FUR[0] + (255,)
        for x in range(53, 61):
            pixels[x, 32] = FUR[3] + (255,)
    else:
        for y in range(30, 37):
            for x in range(51, 63):
                ox = (x + 0.5 - ex) / 4.6
                oy = (y + 0.5 - ey) / 2.9
                if ox * ox + oy * oy <= 1.0:
                    pixels[x, y] = EYE[0] + (255,)
        for x in range(51, 63):
            if pixels[x, 32][:3] == EYE[0]:
                pixels[x, 31] = FUR[3] + (255,)          # the lid
                pixels[x, 32] = FUR[0] + (255,)          # its edge
        pixels[55, 33] = (210, 214, 230, 255)            # the catchlight
        for x in range(53, 60):
            pixels[x, 36] = FUR[1] + (255,)
    # Brow, heavy and flat.
    _line(image, (50, 29), (61, 28), FUR[1])

    # Nose, mouth and the two incisors.
    nose = Piece(PINK, ambient=0.4)
    nose.ellipse((35, 45), 3.2, 2.6)
    nose.paint(image)
    pixels[34, 44] = PINK[4] + (255,)
    _line(image, (38, 49), (49, 51), FUR[0])
    for x in (39, 40):
        pixels[x, 50] = TOOTH + (255,)
        pixels[x, 51] = TOOTH + (255,)
    pixels[39, 52] = (196, 170, 104, 255)

    # Whiskers, fanned forward off the snout.
    for end in ((22, 39), (20, 45), (23, 51)):
        _line(image, (41, 46), end, (196, 194, 206))
    for end in ((27, 36), (28, 55)):
        _line(image, (43, 48), end, (140, 138, 152))

    return _outline(image)


def _arm_pose(amount: float):
    """Elbow, hand and cigarette for a raise between 0 (rest) and 1."""
    ease = amount * amount * (3 - 2 * amount)

    def mix(a, b):
        return (a[0] + (b[0] - a[0]) * ease, a[1] + (b[1] - a[1]) * ease)

    elbow = mix((54, 94), (52, 80))
    hand = mix((46, 80), (41, 54))
    angle = math.radians(-148 + (-176 + 148) * ease)
    filter_end = mix((44, 78), (38, 50))
    return elbow, hand, angle, filter_end


def chuck_arm(amount: float) -> tuple[Image.Image, dict]:
    """The near arm and the cigarette, somewhere between rest and a drag."""
    image = _blank()
    shoulder = (64, 62)
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

    mouth = (38, 50)
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
