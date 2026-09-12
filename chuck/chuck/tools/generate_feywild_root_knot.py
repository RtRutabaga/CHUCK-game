"""Generate the knots that break up the Feywild's root walls.

A root wall made only of its tile is still a surface, however well the
tile tangles: the eye finds the repeat within a screen. What an actual
wall of roots has that a surface does not is places where the roots
gather -- a boss where several of them have grown round each other and
swollen, with the smaller ones spilling out of it along the run.

Three variants, each two tiles wide and not quite two tall. They stand
on a wall tile with wall either side, so the knot's overhang lands on
more roots rather than on the floor. One of the three carries a cluster
of the Feywild's little glowing caps.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_title_art import Piece, _hash, _outline  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "objects"

W, H = 32, 28
VARIANTS = 3

# The root wall tile's own browns, as a ramp.
BARK = ((20, 14, 18), (56, 38, 36), (82, 55, 45), (106, 70, 50),
        (125, 83, 55))
CAP = ((40, 60, 90), (68, 150, 190), (120, 210, 230), (170, 240, 244),
       (220, 252, 250))


def _curve(piece, a, b, c, r0, r1, steps=10):
    previous = None
    for step in range(steps + 1):
        t = step / steps
        x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t * t * c[0]
        y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t * t * c[1]
        radius = r0 + (r1 - r0) * t
        if previous is not None:
            piece.capsule(previous[0], (x, y), previous[1], radius)
        previous = ((x, y), radius)


def root_knot(variant: int) -> Image.Image:
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lean = (-2, 0, 2)[variant]

    # Roots running out of it along the wall, drawn first so the boss
    # swells over their ends.
    spill = (
        ((14, 20), (6, 22), (0, 25), 3.2, 2.0),
        ((18, 20), (26, 22), (32, 24), 3.2, 2.0),
        ((13, 16), (5, 12), (1, 17), 2.4, 1.4),
        ((19, 15), (27, 11), (31, 16), 2.4, 1.4),
    )
    for index, (a, b, c, r0, r1) in enumerate(spill):
        root = Piece(BARK, fur=True, salt=20 + variant * 5 + index,
                     ambient=0.2)
        _curve(root, a, b, (c[0], c[1] + (variant + index) % 3 - 1), r0, r1)
        root.paint(image)

    boss = Piece(BARK, fur=True, salt=40 + variant, ambient=0.22)
    boss.ellipse((16 + lean, 17), 9.5, 8.5)
    boss.ellipse((13 + lean, 13), 6, 5.5)
    boss.ellipse((20 + lean, 12), 5.5, 5)
    boss.paint(image)

    pixels = image.load()
    # Twisted grain round the boss: the roots it is made of.
    for turn in range(3):
        for step in range(40):
            angle = step / 40 * math.tau * 0.8 + turn * 2.1 + variant
            radius = 3 + step * 0.16
            x = round(16 + lean + math.cos(angle) * radius)
            y = round(16 + math.sin(angle) * radius * 0.8)
            if 0 <= x < W and 0 <= y < H and pixels[x, y][3]:
                pixels[x, y] = BARK[1] + (255,)

    if variant == 1:
        for cx, cy, r in ((24, 9, 2.6), (27, 11, 1.9), (22, 7, 1.6)):
            cap = Piece(CAP, ambient=0.5, salt=90)
            cap.ellipse((cx, cy), r, r * 0.7)
            cap.paint(image)
            if 0 <= cy + 2 < H:
                pixels[cx, cy + 2] = (200, 196, 176, 255)

    return _outline(image)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for variant in range(VARIANTS):
        root_knot(variant).save(OUT / f"fey_root_knot_{variant + 1}.png")
    print(f"Wrote {VARIANTS} root knots ({W}x{H}) to {OUT}")


if __name__ == "__main__":
    main()
