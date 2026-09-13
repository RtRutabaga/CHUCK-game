"""Generate Chuck's sprite sheet from text-grid pixel art.

Run from the project root (requires Pillow, a dev-only dependency):

    python tools/generate_chuck_sprites.py

Writes assets/sprites/chuck/chuck.png -- a 3x3 grid of 12x14 frames:

    row 0: down  (idle, walk1, walk2)
    row 1: up    (idle, walk1, walk2)
    row 2: left  (idle, walk1, walk2)   [right is flipped at runtime]

Why text grids: the art stays human-readable and diff-able, tweaking a
pixel is editing a character, and no binary assets need hand-editing.
Unknown characters or wrong grid sizes fail loudly.

Character notes (Game Bible): gray fur, oversized open purple jacket
showing a lighter belly, permanent thousand-yard stare (half-lidded,
never wide-eyed), a cigarette in the profile view, visible tail.
Chuck is one foot tall: the sprite (12x14) is smaller than one 16px
tile, and that is the point.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spritegen import render_sheet

FRAME_W, FRAME_H = 12, 14

# Palette: char -> RGBA. '.' is transparent.
PALETTE = {
    ".": (0, 0, 0, 0),
    "G": (140, 138, 150, 255),  # fur
    "D": (90, 88, 102, 255),    # dark fur (ears, feet)
    "B": (182, 180, 190, 255),  # belly (shows through the open jacket)
    "P": (112, 62, 160, 255),   # jacket purple
    "p": (78, 42, 116, 255),    # jacket shadow
    "E": (28, 26, 34, 255),     # eyes (half-lidded)
    "N": (222, 142, 152, 255),  # nose
    "T": (198, 146, 150, 255),  # tail
    "W": (236, 236, 228, 255),  # cigarette paper
    "O": (242, 146, 66, 255),   # cigarette ember
}

# --------------------------------------------------------------------------
# Frames. Each is 14 rows of 12 characters.
# --------------------------------------------------------------------------

DOWN_IDLE = """
.DD......DD.
.DGD....DGD.
..GGGGGGGG..
.GGGGGGGGGG.
.GGEEGGEEGG.
.GGGGGGGGGG.
..GGGNNGGG..
.PPPBBBBPPP.
.PPPBBBBPPP.
.PPpBBBBpPP.
.PPpBBBBpPP.
..GGG..GGG..
..DDD..DDD..
............
"""

DOWN_WALK1 = """
.DD......DD.
.DGD....DGD.
..GGGGGGGG..
.GGGGGGGGGG.
.GGEEGGEEGG.
.GGGGGGGGGG.
..GGGNNGGG..
.PPPBBBBPPP.
.PPPBBBBPPP.
.PPpBBBBpPP.
.PPpBBBBpPP.
.GGG....GG..
.DDD....DD..
............
"""

DOWN_WALK2 = """
.DD......DD.
.DGD....DGD.
..GGGGGGGG..
.GGGGGGGGGG.
.GGEEGGEEGG.
.GGGGGGGGGG.
..GGGNNGGG..
.PPPBBBBPPP.
.PPPBBBBPPP.
.PPpBBBBpPP.
.PPpBBBBpPP.
..GG....GGG.
..DD....DDD.
............
"""

UP_IDLE = """
.DD......DD.
.DGD....DGD.
..GGGGGGGG..
.GGGGGGGGGG.
.GGGGGGGGGG.
.GGGGGGGGGG.
.PPPPPPPPPP.
.PPPPPPPPPP.
.PPPPPPPPPP.
.PPpPPPPpPP.
.PPpPPPPpPP.
..GGG..GGG..
..DDD..DDD..
....TTT.....
"""

UP_WALK1 = """
.DD......DD.
.DGD....DGD.
..GGGGGGGG..
.GGGGGGGGGG.
.GGGGGGGGGG.
.GGGGGGGGGG.
.PPPPPPPPPP.
.PPPPPPPPPP.
.PPPPPPPPPP.
.PPpPPPPpPP.
.PPpPPPPpPP.
.GGG....GG..
.DDD....DD..
.....TTT....
"""

UP_WALK2 = """
.DD......DD.
.DGD....DGD.
..GGGGGGGG..
.GGGGGGGGGG.
.GGGGGGGGGG.
.GGGGGGGGGG.
.PPPPPPPPPP.
.PPPPPPPPPP.
.PPPPPPPPPP.
.PPpPPPPpPP.
.PPpPPPPpPP.
..GG....GGG.
..DD....DDG.
...TTT......
"""

LEFT_IDLE = """
............
....DD......
...DGGD.....
..GGGGGGG...
..GEEGGGGG..
.GGGGGGGGG..
.NGGGGGGGG..
OWPPPPPPPP..
..PBPPPPPPT.
..PBPPPPPPTT
..PpPPPPpP.T
..GGG..GGG..
..DDD..DDD..
............
"""

LEFT_WALK1 = """
............
....DD......
...DGGD.....
..GGGGGGG...
..GEEGGGGG..
.GGGGGGGGG..
.NGGGGGGGG..
OWPPPPPPPP..
..PBPPPPPPT.
..PBPPPPPPTT
..PpPPPPpP.T
.GGG....GG..
.DDD....DD..
............
"""

LEFT_WALK2 = """
............
....DD......
...DGGD.....
..GGGGGGG...
..GEEGGGGG..
.GGGGGGGGG..
.NGGGGGGGG..
OWPPPPPPPP..
..PBPPPPPPT.
..PBPPPPPPTT
..PpPPPPpP.T
...GG....GG.
...DD....DD.
............
"""

# Sheet layout: rows are directions, columns are frames.
SHEET = [
    [DOWN_IDLE, DOWN_WALK1, DOWN_WALK2],
    [UP_IDLE, UP_WALK1, UP_WALK2],
    [LEFT_IDLE, LEFT_WALK1, LEFT_WALK2],
]

NAMES = [
    ["down_idle", "down_walk1", "down_walk2"],
    ["up_idle", "up_walk1", "up_walk2"],
    ["left_idle", "left_walk1", "left_walk2"],
]


# Asleep, for the opening cutscene: curled on his side against Bobert's
# barrel, head to the left, eyes shut, jacket rucked up, tail wrapped
# round under him. Two frames of breathing -- the jacket rises and falls.
ASLEEP_W, ASLEEP_H = 16, 9

ASLEEP_IN = """
................
.DD.............
.DGGG..PPPPP....
GGGGGGPPPPPPPP..
NGEEGGPPBBBPPPP.
.GGGGPPPBBBBPPP.
..DDPPPpppppPPT.
...TTTTTTTTTTT..
................
"""

ASLEEP_OUT = """
................
.DD.............
.DGGG...........
GGGGGGPPPPPPPP..
NGEEGGPPBBBPPPP.
.GGGGPPPBBBBPPP.
..DDPPPpppppPPT.
...TTTTTTTTTTT..
................
"""


def main() -> None:
    out = (
        Path(__file__).resolve().parents[1]
        / "assets" / "sprites" / "chuck" / "chuck.png"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    render_sheet(SHEET, NAMES, FRAME_W, FRAME_H, PALETTE).save(out)
    print(f"Wrote {out}")
    asleep = out.with_name("chuck_asleep.png")
    render_sheet([[ASLEEP_IN, ASLEEP_OUT]], [["asleep_in", "asleep_out"]],
                 ASLEEP_W, ASLEEP_H, PALETTE).save(asleep)
    print(f"Wrote {asleep}")


if __name__ == "__main__":
    main()
