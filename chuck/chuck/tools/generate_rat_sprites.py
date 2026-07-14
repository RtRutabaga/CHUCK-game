"""Generate the two-frame ordinary sewer-rat sprite sheet."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spritegen import render_sheet

FRAME_W, FRAME_H = 10, 8

PALETTE = {
    ".": (0, 0, 0, 0),
    "g": (122, 116, 110, 255),
    "d": (82, 78, 76, 255),
    "p": (184, 128, 132, 255),
    "e": (224, 214, 190, 255),
}

RAT_IDLE = """
..........
.p...p....
.ggggg....
.gegggg...
.ggggggdp.
..d..d....
..........
..........
"""

RAT_TWITCH = """
..........
.p...p....
.ggggg....
.gegggg...
.ggggggd..
..d..d.dp.
..........
..........
"""


def main() -> None:
    out = (Path(__file__).resolve().parents[1]
           / "assets" / "sprites" / "hazards" / "rat.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    render_sheet([[RAT_IDLE, RAT_TWITCH]], [["rat_idle", "rat_twitch"]],
                 FRAME_W, FRAME_H, PALETTE).save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
