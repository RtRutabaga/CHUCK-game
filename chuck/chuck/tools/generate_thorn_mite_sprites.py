"""Generate the two-frame thorn-mite sprite sheet.

A thorn mite is the Feywild's rat: tiny, quick, and gone in one scratch.
It reads as a walking burr -- a dark seed-body bristling with pale
thorns, carried on thin legs -- so at native scale it is unmistakably
smaller than Chuck and unmistakably not a rodent.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spritegen import render_sheet

FRAME_W, FRAME_H = 10, 8

PALETTE = {
    ".": (0, 0, 0, 0),
    "b": (58, 44, 66, 255),    # the seed-body's shadowed mass
    "h": (92, 72, 104, 255),   # its lit violet upper curve
    "t": (176, 198, 148, 255), # thorns, pale enough to read at 10px
    "e": (240, 226, 132, 255), # a glinting eye
    "l": (40, 32, 46, 255),    # legs
}

MITE_STEP = """
..........
...t..t...
..thhhht..
.tbbbheet.
..tbbbbt..
...t..t...
..l....l..
..........
"""

MITE_SCUTTLE = """
..........
..t...t...
..thhhht..
.tbbbheet.
..tbbbbt..
...t..t...
...l..l...
..........
"""


def main() -> None:
    out = (Path(__file__).resolve().parents[1]
           / "assets" / "sprites" / "hazards" / "thorn_mite.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    render_sheet([[MITE_STEP, MITE_SCUTTLE]],
                 [["mite_step", "mite_scuttle"]],
                 FRAME_W, FRAME_H, PALETTE).save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
