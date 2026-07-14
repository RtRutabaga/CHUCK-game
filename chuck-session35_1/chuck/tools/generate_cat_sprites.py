"""Generate the dock cat's sprite sheet from text-grid pixel art.

Run from the project root (requires Pillow, dev-only):

    python tools/generate_cat_sprites.py

Writes assets/sprites/hazards/cat.png — 3 frames of 18x12, all facing
left (stand, walk1, walk2); right-facing is flipped at runtime.

Design notes (Game Bible: scale is a pillar): the cat is 18px long to
Chuck's 12px, and it reads as a slab of muscle next to him. To a
one-foot-tall rat, a dockside tabby is a dragon with a collar.
The cat is not evil. It is a cat. This is worse.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spritegen import render_sheet

FRAME_W, FRAME_H = 18, 12

PALETTE = {
    ".": (0, 0, 0, 0),
    "R": (204, 126, 58, 255),   # tabby orange
    "r": (158, 90, 40, 255),    # stripes
    "q": (128, 74, 34, 255),    # ears / paws / shading
    "E": (70, 160, 90, 255),    # eye (green, unblinking)
    "T": (204, 126, 58, 255),   # tail (same orange; separate for editing)
}

CAT_STAND = """
.qq...qq..........
.RRRRRRR..........
.RERRRRR.........T
.RRRRRRR........TT
..RRRRRRRRRRRRRT..
..RRRrRRRrRRRRRT..
..RRRRRRRRRRRRR...
..RRRrRRRrRRRRR...
..RRRRRRRRRRRRR...
..RRR.......RRR...
..qqq.......qqq...
..................
"""

CAT_WALK1 = """
.qq...qq..........
.RRRRRRR..........
.RERRRRR.........T
.RRRRRRR........TT
..RRRRRRRRRRRRRT..
..RRRrRRRrRRRRRT..
..RRRRRRRRRRRRR...
..RRRrRRRrRRRRR...
..RRRRRRRRRRRRR...
.RRR.........RR...
.qqq.........qq...
..................
"""

CAT_WALK2 = """
.qq...qq..........
.RRRRRRR..........
.RERRRRR.........T
.RRRRRRR........TT
..RRRRRRRRRRRRRT..
..RRRrRRRrRRRRRT..
..RRRRRRRRRRRRR...
..RRRrRRRrRRRRR...
..RRRRRRRRRRRRR...
...RRR......RRRR..
...qqq......qqqq..
..................
"""

SHEET = [[CAT_STAND, CAT_WALK1, CAT_WALK2]]
NAMES = [["cat_stand", "cat_walk1", "cat_walk2"]]


def main() -> None:
    out = (
        Path(__file__).resolve().parents[1]
        / "assets" / "sprites" / "hazards" / "cat.png"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    render_sheet(SHEET, NAMES, FRAME_W, FRAME_H, PALETTE).save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
