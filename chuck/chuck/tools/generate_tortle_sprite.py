"""Generate the Chult Falls tortle: npcs/tortle.png.

Run from the project root (requires Pillow, dev-only):

    python tools/generate_tortle_sprite.py

Three frames (down, up, left; right is the left one flipped at runtime),
like every standing NPC -- but 24 pixels wide instead of 16, because a
tortle is a person with a house on his back and the house is wider than
the person. Human height: he towers over Chuck the same as anybody.

After the reference: an old, hunched turtle-man, beaked and heavy-browed,
green-skinned with a pale plastron, a brown plated shell with moss
growing on the top of it, a blue vest, brown trousers, and a knobbly
walking stick in his right hand.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sprites" / "npcs" / "tortle.png"
FRAME_W, FRAME_H = 24, 30

SKIN = (132, 164, 104)
SKIN_DARK = (94, 124, 78)
SKIN_LIT = (168, 192, 128)
EYE = (26, 24, 28)
BROW = (80, 106, 70)
PALE = (198, 184, 128)
PALE_DARK = (160, 146, 98)
SHELL = (146, 106, 62)
SHELL_DARK = (102, 72, 42)
SHELL_RIM = (182, 140, 86)
MOSS = (106, 152, 56)
MOSS_LIT = (158, 196, 84)
VEST = (52, 80, 114)
VEST_DARK = (36, 56, 82)
CLOTH = (120, 96, 64)
CLOTH_DARK = (84, 66, 44)
STICK = (118, 76, 46)
STICK_DARK = (76, 48, 30)


class Frame:
    def __init__(self) -> None:
        self.image = Image.new("RGBA", (FRAME_W, FRAME_H), (0, 0, 0, 0))

    def px(self, x: int, y: int, colour) -> None:
        if 0 <= x < FRAME_W and 0 <= y < FRAME_H:
            self.image.putpixel((x, y), (*colour, 255))

    def rect(self, x0: int, y0: int, x1: int, y1: int, colour) -> None:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, colour)

    def ellipse(self, x0, y0, x1, y1, paint) -> None:
        """paint(x, y, edge) for every pixel inside; edge = on the rim."""
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = (x1 - x0) / 2 + 0.5, (y1 - y0) / 2 + 0.5

        def inside(x, y):
            return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1

        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if inside(x, y):
                    edge = not all(inside(x + dx, y + dy) for dx, dy in
                                   ((1, 0), (-1, 0), (0, 1), (0, -1)))
                    paint(x, y, edge)

    def stick(self, x: int, top: int) -> None:
        for y in range(top, FRAME_H):
            self.px(x, y, STICK_DARK if (y * 5) % 7 < 2 else STICK)
        # A crook and a knot or two: it is a branch, not a staff.
        self.px(x + 1, top, STICK)
        self.px(x + 1, top + 1, STICK_DARK)
        self.px(x - 1, top + 9, STICK_DARK)
        self.px(x + 1, top + 16, STICK_DARK)


def shell(frame: Frame, x0, y0, x1, y1, rim_side: str | None) -> None:
    def paint(x, y, edge):
        if edge:
            colour = SHELL_RIM if rim_side is None or (
                (rim_side == "left" and x < (x0 + x1) / 2)
                or y > (y0 + y1) / 2) else SHELL_DARK
        else:
            row = (y - y0) // 5
            seam_x = (x - x0 + (3 if row % 2 else 0)) % 6 == 0
            seam_y = (y - y0) % 5 == 0
            colour = SHELL_DARK if seam_x or seam_y else SHELL
        frame.px(x, y, colour)

    frame.ellipse(x0, y0, x1, y1, paint)


def moss(frame: Frame, points) -> None:
    for index, (x, y) in enumerate(points):
        frame.px(x, y, MOSS_LIT if index % 3 == 0 else MOSS)


def down() -> Image.Image:
    f = Frame()
    # The shell behind him shows round his shoulders and hips.
    shell(f, 3, 5, 20, 23, None)
    moss(f, [(5, 5), (6, 4), (7, 5), (6, 6), (16, 5), (17, 4), (18, 5),
             (17, 6), (15, 6)])
    # Head: heavy brow, eyes to the sides, pale beak and jaw.
    f.rect(9, 1, 14, 6, SKIN)
    f.rect(10, 0, 13, 0, SKIN)
    f.rect(10, 1, 11, 1, SKIN_LIT)
    f.rect(9, 3, 14, 3, BROW)
    f.px(10, 4, EYE)
    f.px(13, 4, EYE)
    f.rect(10, 5, 13, 6, PALE)
    f.px(11, 7, PALE_DARK)
    f.px(12, 7, PALE_DARK)
    f.rect(10, 7, 10, 7, SKIN_DARK)
    f.rect(13, 7, 13, 7, SKIN_DARK)
    # Body: plastron down the middle, the vest open over it.
    f.rect(7, 8, 16, 20, VEST)
    f.rect(10, 8, 13, 19, PALE)
    for y in (11, 14, 17):
        f.rect(10, y, 13, y, PALE_DARK)
    f.rect(7, 9, 7, 20, VEST_DARK)
    f.rect(16, 9, 16, 20, VEST_DARK)
    # Arms: his right (our left) out to the stick, his left hanging.
    f.rect(5, 8, 6, 14, SKIN)
    f.rect(5, 12, 5, 14, SKIN_DARK)
    f.rect(17, 8, 18, 16, SKIN)
    f.rect(18, 11, 18, 16, SKIN_DARK)
    f.rect(17, 17, 18, 17, SKIN_DARK)
    f.stick(3, 6)
    f.rect(3, 14, 5, 16, SKIN)
    f.px(3, 16, SKIN_DARK)
    # Trousers and feet.
    f.rect(8, 20, 15, 25, CLOTH)
    f.rect(8, 20, 15, 20, CLOTH_DARK)
    f.rect(11, 23, 12, 25, CLOTH_DARK)
    f.rect(8, 26, 10, 27, SKIN_DARK)
    f.rect(13, 26, 15, 27, SKIN_DARK)
    f.rect(7, 28, 10, 29, SKIN)
    f.rect(13, 28, 16, 29, SKIN)
    return f.image


def up() -> Image.Image:
    f = Frame()
    # The back of his head over the top of the shell.
    f.rect(9, 0, 14, 5, SKIN)
    f.rect(10, 0, 12, 1, SKIN_LIT)
    f.rect(9, 4, 14, 5, SKIN_DARK)
    # Arms at his sides; the stick is in his right, our right from behind.
    f.rect(3, 8, 4, 16, SKIN)
    f.rect(3, 13, 3, 16, SKIN_DARK)
    f.rect(19, 8, 20, 14, SKIN)
    f.stick(20, 6)
    f.rect(19, 14, 21, 16, SKIN)
    # Trousers and heels under the shell.
    f.rect(8, 21, 15, 25, CLOTH)
    f.rect(11, 23, 12, 25, CLOTH_DARK)
    f.rect(8, 26, 10, 27, SKIN_DARK)
    f.rect(13, 26, 15, 27, SKIN_DARK)
    f.rect(7, 28, 10, 29, SKIN)
    f.rect(13, 28, 16, 29, SKIN)
    # The shell, which is most of him from here, and its moss.
    shell(f, 4, 4, 19, 24, "bottom")
    f.rect(8, 23, 15, 24, VEST)  # the vest's hem below the shell
    moss(f, [(8, 4), (9, 3), (10, 4), (11, 3), (12, 4), (13, 3), (14, 4),
             (15, 5), (10, 5), (13, 5), (7, 5), (11, 2), (12, 5)])
    return f.image


def left() -> Image.Image:
    f = Frame()
    # Shell on his back, hunched high, moss on the crown of it.
    shell(f, 9, 5, 21, 23, "left")
    moss(f, [(12, 5), (13, 4), (14, 4), (15, 3), (16, 4), (17, 4),
             (18, 5), (14, 5), (16, 5), (15, 2), (19, 6)])
    # Legs, bent: trousers, then green shins and feet.
    f.rect(8, 21, 15, 24, CLOTH)
    f.rect(12, 22, 15, 24, CLOTH_DARK)
    f.rect(7, 25, 9, 27, SKIN)
    f.rect(12, 25, 14, 27, SKIN_DARK)
    f.rect(5, 28, 9, 29, SKIN)
    f.rect(11, 28, 15, 29, SKIN_DARK)
    # Body, between the stick and the shell: vest over a pale front.
    f.rect(7, 11, 11, 21, VEST)
    f.rect(6, 12, 7, 20, PALE)
    f.rect(6, 15, 7, 15, PALE_DARK)
    f.rect(6, 18, 7, 18, PALE_DARK)
    f.rect(10, 12, 11, 21, VEST_DARK)
    # Neck forward and down, the head thrust out ahead of him.
    f.rect(6, 9, 9, 11, SKIN)
    f.rect(7, 11, 9, 11, SKIN_DARK)
    f.rect(2, 5, 7, 9, SKIN)
    f.rect(3, 4, 6, 4, SKIN)
    f.rect(4, 4, 6, 5, SKIN_LIT)
    f.rect(2, 6, 6, 6, BROW)
    f.px(4, 7, EYE)
    f.px(1, 8, PALE)   # the beak
    f.rect(2, 8, 5, 9, PALE)
    f.rect(3, 10, 5, 10, PALE_DARK)
    # The stick out in front, and the arm reaching down to it.
    f.stick(2, 11)
    f.rect(7, 12, 9, 14, SKIN)
    f.rect(5, 14, 7, 16, SKIN)
    f.rect(5, 16, 7, 16, SKIN_DARK)
    f.rect(1, 16, 4, 18, SKIN)
    f.px(1, 18, SKIN_DARK)
    return f.image


def main() -> None:
    sheet = Image.new("RGBA", (FRAME_W * 3, FRAME_H), (0, 0, 0, 0))
    for index, frame in enumerate((down(), up(), left())):
        sheet.alpha_composite(frame, (index * FRAME_W, 0))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
