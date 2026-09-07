"""Generate the docks tileset from text-grid tile art.

Run from the project root (requires Pillow, dev-only):

    python tools/generate_tileset.py

Writes assets/tilesets/docks.png laid out per src/world/tileset_layout
(the shared contract with the runtime). Water's second animation frame
is derived by rotating the authored frame one row down — a slow
shimmer, not a light show.

Art direction (Game Bible): warm, worn, late-afternoon port. Texture
should read at a glance and disappear at a stare — the ground is a
stage, not the show.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from PIL import Image
from spritegen import parse_frame

from src.world.tileset_layout import (
    SHEET_COLS, SHEET_ROWS, TILE_PX, TILESET_ORDER,
)

PALETTE = {
    ".": (0, 0, 0, 0),  # transparent (overhead tiles: gate teeth gaps)
    # planks
    "P": (150, 112, 74, 255), "p": (132, 96, 60, 255),
    "s": (108, 76, 46, 255), "n": (70, 58, 44, 255),
    # stone
    "S": (90, 86, 92, 255), "j": (72, 68, 76, 255), "h": (104, 100, 108, 255),
    # water
    "W": (36, 52, 84, 255), "w": (52, 72, 110, 255), "f": (118, 140, 176, 255),
    # interior floor
    "F": (52, 46, 52, 255), "g": (42, 37, 43, 255),
    # wall
    "B": (112, 92, 68, 255), "m": (88, 72, 54, 255), "l": (126, 105, 80, 255),
    # awning canvas
    "R": (168, 58, 52, 255), "r": (140, 46, 42, 255), "y": (188, 76, 66, 255),
    # tavern: tan brick facade
    "T": (166, 132, 86, 255), "t": (132, 102, 64, 255),
    "u": (186, 152, 102, 255),
    # tavern: glowing window
    "d": (66, 52, 38, 255), "q": (236, 172, 68, 255),
    "Q": (248, 204, 112, 255),
    # tavern: slate roof + wood eave
    "V": (62, 60, 70, 255), "v": (44, 42, 50, 255), "U": (80, 78, 90, 255),
    "e": (108, 78, 48, 255), "E": (84, 60, 38, 255),
    # castle wall: gold-brown brick, merlons, banner, torch, portcullis
    "G": (138, 106, 58, 255), "z": (108, 80, 44, 255),
    "H": (158, 124, 70, 255), "I": (170, 138, 82, 255),
    "k": (52, 48, 46, 255),
    "N": (96, 94, 100, 255), "M": (74, 72, 78, 255),
    "O": (204, 162, 74, 255),
    "x": (244, 166, 60, 255), "X": (252, 214, 120, 255),
    "Z": (58, 56, 60, 255),
    # ruined foundation
    "D": (64, 58, 60, 255),    # rubble earth
    "A": (50, 45, 47, 255),    # dark patches
}

# The finale is the same city under a higher, clearer sun.  Teal water is the
# strongest read; stone, timber, canvas, and masonry lift together so this is
# a time-of-day change rather than one conspicuously recoloured material.
MIDDAY_PALETTE = {
    **PALETTE,
    "P": (174, 132, 82, 255), "p": (154, 112, 68, 255),
    "s": (126, 88, 50, 255), "n": (66, 62, 56, 255),
    "S": (120, 118, 124, 255), "j": (94, 92, 100, 255),
    "h": (136, 134, 140, 255),
    "W": (22, 94, 106, 255), "w": (38, 124, 132, 255),
    "f": (116, 190, 184, 255),
    "B": (138, 112, 78, 255), "m": (108, 86, 60, 255),
    "l": (154, 128, 92, 255),
    "R": (190, 68, 58, 255), "r": (160, 54, 48, 255),
    "y": (214, 92, 74, 255),
    "T": (194, 158, 104, 255), "t": (158, 124, 78, 255),
    "u": (214, 180, 124, 255),
    # Daylight windows reflect the sky instead of glowing from within.
    "d": (82, 78, 72, 255), "q": (122, 158, 164, 255),
    "Q": (170, 202, 202, 255),
    "V": (78, 78, 88, 255), "v": (56, 56, 64, 255),
    "U": (98, 98, 108, 255),
    "e": (128, 94, 56, 255), "E": (102, 74, 44, 255),
    "G": (166, 130, 72, 255), "z": (132, 98, 52, 255),
    "H": (188, 150, 88, 255), "I": (200, 164, 100, 255),
}

PLANKS_1 = """
PPPPpPPPPPPPpPPP
PPPPPPPPpPPPPPPP
nPPPPPPPPPPPPPPn
ssssssssssssssss
PPpPPPPPPPPpPPPP
PPPPPPpPPPPPPPPP
PPPPPPPPPPPPPPPP
ssssssssssssssss
PPPPPPPPpPPPPPPP
pPPPPPPPPPPPpPPP
nPPPPPPPPPPPPPPn
ssssssssssssssss
PPPPPpPPPPPPPPPP
PPPPPPPPPPpPPPPP
PPpPPPPPPPPPPPPP
ssssssssssssssss
"""

PLANKS_2 = """
PPpPPPPPPPPPPPPP
PPPPPPPPPPPPpPPP
PPPPPPPnPPPPPPPP
ssssssssssssssss
PPPPPPPPPPPPPPpP
pPPPPPpPPPPPPPPP
nPPPPPPPPPPPPPPn
ssssssssssssssss
PPPPPpPPPPPPPPPP
PPPPPPPPPPPpPPPP
PPPPPPPPnPPPPPPP
ssssssssssssssss
PpPPPPPPPPPPPpPP
PPPPPPPPpPPPPPPP
nPPPPPPPPPPPPPPn
ssssssssssssssss
"""

STONE_1 = """
SSSSSSSjSSSSSSSS
ShSSSSSjSSSShSSS
SSSSSSSjSSSSSSSS
jjjjjjjjjjjjjjjj
SSSjSSSSSSSjSSSS
SSSjSShSSSSjSSSS
SSSjSSSSSSSjSSSS
jjjjjjjjjjjjjjjj
SSSSSSSSjSSSSSSS
ShSSSSSSjSSSSShS
SSSSSSSSjSSSSSSS
jjjjjjjjjjjjjjjj
SSSSSjSSSSSSjSSS
SSSSSjSSShSSjSSS
SSSSSjSSSSSSjSSS
jjjjjjjjjjjjjjjj
"""

STONE_2 = """
SSSjSSSSSSSSjSSS
SSSjSShSSSSSjSSS
SSSjSSSSSSSSjSSS
jjjjjjjjjjjjjjjj
SSSSSSSSjSSSSSSS
ShSSSSSSjSSSShSS
SSSSSSSSjSSSSSSS
jjjjjjjjjjjjjjjj
SSSSjSSSSSSjSSSS
SSSSjSSSSSSjSSSS
SSSSjSShSSSjSSSS
jjjjjjjjjjjjjjjj
SjSSSSSSSSSSSSjS
SjSSSShSSSSSSSjS
SjSSSSSSSSSSSSjS
jjjjjjjjjjjjjjjj
"""

STONE_3 = """
SSSSSSjSSSSSSSSS
SShSSSjSSSSShSSS
SSSSSSjSSSSSSSSS
jjjjjjjjjjjjjjjj
SjSSSSSSSSjSSSSS
SjSSShSSSSjSSSSS
SjSSSSSSSSjSSSSS
jjjjjjjjjjjjjjjj
SSSSSSSSSSSSjSSS
SSShSSSSSSSSjSSS
SSSSSSSSSSSSjSSS
jjjjjjjjjjjjjjjj
SSSSjSSSSSSSSSSS
SSSSjSSSSShSSSSS
SSSSjSSSSSSSSSSS
jjjjjjjjjjjjjjjj
"""

WATER_1 = """
WWWWWWWWWWWWWWWW
WWwwWWWWWWWWWWWW
WWWWWWWWWWwwwWWW
WWWWWWWWWWWWWWWW
WWWWWfWWWWWWWWWW
WwwWWWWWWWWWWwwW
WWWWWWWWWWWWWWWW
WWWWWWWwwWWWWWWW
WWWWWWWWWWWWWWWW
WwWWWWWWWWWWfWWW
WWWWWWwwwWWWWWWW
WWWWWWWWWWWWWWWW
WWwwWWWWWWWwWWWW
WWWWWWWWWWWWWWWW
WWWWWWWWwwWWWWWW
WWWWWWWWWWWWWWWW
"""

WATER_2 = """
WWWWWWWWWWWWWWWW
WWWWWWWwwWWWWWWW
WwWWWWWWWWWWWWWW
WWWWWWWWWWWWwwWW
WWWWWWWWWWWWWWWW
WWWwwWWWfWWWWWWW
WWWWWWWWWWWWWWWW
WWWWWWWWWWwwWWWW
WwwWWWWWWWWWWWWW
WWWWWWWWWWWWWWWW
WWWWfWWWWwWWWWWW
WWWWWWWWWWWWWWWW
WWWWWWwwWWWWWwwW
WWWWWWWWWWWWWWWW
WWwWWWWWWWWWWWWW
WWWWWWWWWWWWWWWW
"""

FLOOR = """
FFFFFFFFFFFFFFFF
FFFFgFFFFFFFFFFF
FFFFFFFFFFFgFFFF
gggggggggggggggg
FFFFFFFFgFFFFFFF
FFgFFFFFFFFFFFFF
FFFFFFFFFFFFFgFF
gggggggggggggggg
FFFFFgFFFFFFFFFF
FFFFFFFFFFgFFFFF
FgFFFFFFFFFFFFFF
gggggggggggggggg
FFFFFFFFFFFFgFFF
FFFgFFFFFFFFFFFF
FFFFFFFFgFFFFFFF
gggggggggggggggg
"""

WALL = """
BBBBBBBmBBBBBBBB
BlBBBBBmBBBBlBBB
BBBBBBBmBBBBBBBB
mmmmmmmmmmmmmmmm
BBBmBBBBBBBBmBBB
BBBmBBBlBBBBmBBB
BBBmBBBBBBBBmBBB
mmmmmmmmmmmmmmmm
BBBBBBBBBmBBBBBB
BlBBBBBBBmBBBlBB
BBBBBBBBBmBBBBBB
mmmmmmmmmmmmmmmm
BBBBmBBBBBBBmBBB
BBBBmBBlBBBBmBBB
BBBBmBBBBBBBmBBB
mmmmmmmmmmmmmmmm
"""


AWNING_1 = """
yyyyyyyyyyyyyyyy
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
"""

AWNING_2 = """
yyyyyyyyyyyyyyyy
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
"""

AWNING_EDGE = """
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
RRRRRRRRrrrrrrrr
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
rrrrrrrrRRRRRRRR
RRRRRRRRrrrrrrrr
.RRRRRR..rrrrrr.
..RRRR....rrrr..
...RR......rr...
................
................
"""



TAVERN_WALL_1 = """
TTTTTTTtTTTTTTTT
TuTTTTTtTTTTuTTT
TTTTTTTtTTTTTTTT
tttttttttttttttt
TTTtTTTTTTTTtTTT
TTTtTTTuTTTTtTTT
TTTtTTTTTTTTtTTT
tttttttttttttttt
TTTTTTTTTtTTTTTT
TuTTTTTTTtTTTuTT
TTTTTTTTTtTTTTTT
tttttttttttttttt
TTTTtTTTTTTTtTTT
TTTTtTTuTTTTtTTT
TTTTtTTTTTTTtTTT
tttttttttttttttt
"""

TAVERN_WALL_2 = """
TTTTtTTTTTTtTTTT
TTTTtTTuTTTtTTTT
TTTTtTTTTTTtTTTT
tttttttttttttttt
TTTTTTTTtTTTTTTT
TuTTTTTTtTTTTuTT
TTTTTTTTtTTTTTTT
tttttttttttttttt
TTTtTTTTTTTTTtTT
TTTtTTTuTTTTTtTT
TTTtTTTTTTTTTtTT
tttttttttttttttt
TTTTTTTTTtTTTTTT
TuTTTTTTTtTTTTTT
TTTTTTTTTtTTTTTT
tttttttttttttttt
"""

TAVERN_WINDOW = """
TTTTTTTtTTTTTTTT
TTTTTTTTTTTTTTTT
TTTddddddddddTTT
TTTdQQQddQQQdTTT
TTTdQQQddQQQdTTT
TTTdQQQddQQQdTTT
TTTddddddddddTTT
TTTdqqqddqqqdTTT
TTTdqqqddqqqdTTT
TTTdqqqddqqqdTTT
TTTdqqqddqqqdTTT
TTTddddddddddTTT
TTttttttttttttTT
tttttttttttttttt
TTTTtTTTTTTTtTTT
tttttttttttttttt
"""

TAVERN_ROOF_1 = """
VVVVVVVVvVVVVVVV
VUVVVVVVvVVVVUVV
vvvvvvvvvvvvvvvv
VVVvVVVVVVVVvVVV
VVVvVVUVVVVVvVVV
vvvvvvvvvvvvvvvv
VVVVVVvVVVVVVVVV
VVUVVVvVVVVVVUVV
vvvvvvvvvvvvvvvv
VVVVvVVVVVVvVVVV
VVVVvVVUVVVvVVVV
vvvvvvvvvvvvvvvv
VVVVVVVVvVVVVVVV
VUVVVVVVvVVVVVVV
vvvvvvvvvvvvvvvv
VVVvVVVVVVVVvVVV
"""

TAVERN_ROOF_2 = """
VVVvVVVVVVVVvVVV
VVVvVVUVVVVVvVVV
vvvvvvvvvvvvvvvv
VVVVVVVVvVVVVVVV
VUVVVVVVvVVVVUVV
vvvvvvvvvvvvvvvv
VVVVvVVVVVVvVVVV
VVVVvVVUVVVvVVVV
vvvvvvvvvvvvvvvv
VVVVVVvVVVVVVVVV
VVUVVVvVVVVVVUVV
vvvvvvvvvvvvvvvv
VVVvVVVVVVVVVvVV
VVVvVVUVVVVVVvVV
vvvvvvvvvvvvvvvv
VVVVVVVVvVVVVVVV
"""

TAVERN_EAVE = """
VVVVVVvVVVVVVVVV
VVUVVVvVVVVVUVVV
vvvvvvvvvvvvvvvv
VVVVvVVVVVVvVVVV
VVVVvVVUVVVvVVVV
vvvvvvvvvvvvvvvv
VVVVVVVVVVVVVVVV
vvvvvvvvvvvvvvvv
eeeeeeeeeeeeeeee
eeEeeeeEeeeeEeee
eeeeeeeeeeeeeeee
EEEEEEEEEEEEEEEE
TTTTTTTTTTTTTTTT
TTTTTTTtTTTTTTTT
TuTTTTTtTTTTTTTT
tttttttttttttttt
"""


CASTLE_TOP_1 = """
IIIIIkkkIIIIIkkk
GGGGGkkkGGGGGkkk
GGGGGkkkGGGGGkkk
HGGGGkkkHGGGGkkk
GGGGGGGGGGGGGGGG
zzzzzzzzzzzzzzzz
GGGzGGGGGGGGzGGG
GGGzGGHGGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGzGGGGGGG
GHGGGGGGzGGGGHGG
zzzzzzzzzzzzzzzz
GGGGzGGGGGGGzGGG
GGGGzGGGGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGzGGGGGGG
"""

CASTLE_TOP_2 = """
IIIIIkkkIIIIIkkk
GGGGGkkkGGGGGkkk
GGGGGkkkGGGGGkkk
GGGGHkkkGGGGHkkk
GGGGGGGGGGGGGGGG
zzzzzzzzzzzzzzzz
GGGGGGGGzGGGGGGG
GGHGGGGGzGGGGGGG
zzzzzzzzzzzzzzzz
GGGzGGGGGGGGzGGG
GGGzGGGHGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGGzGGGGGG
GHGGGGGGGzGGGGGG
zzzzzzzzzzzzzzzz
GGGzGGGGGGGGzGGG
"""

CASTLE_WALL_1 = """
GGGzGGGGGGGGzGGG
GGGzGGHGGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGzGGGGGGG
GHGGGGGGzGGGGHGG
zzzzzzzzzzzzzzzz
GGGGzGGGGGGGzGGG
GGGGzGGHGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGGzGGGGGG
GGHGGGGGGzGGGGGG
zzzzzzzzzzzzzzzz
GGGzGGGGGGGGzGGG
GGGzGGGGGHGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGzGGGGGGG
"""

CASTLE_WALL_2 = """
GGGGGGGGzGGGGGGG
GGHGGGGGzGGGGGGG
zzzzzzzzzzzzzzzz
GGGGzGGGGGGGzGGG
GGGGzGGHGGGGzGGG
zzzzzzzzzzzzzzzz
GGGzGGGGGGGGzGGG
GGGzGGGGGHGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGzGGGGGGGGG
GHGGGGzGGGGGHGGG
zzzzzzzzzzzzzzzz
GGGGGGGGGzGGGGGG
GGGGHGGGGzGGGGGG
zzzzzzzzzzzzzzzz
GGGzGGGGGGGGzGGG
"""

CASTLE_BANNER = """
GGGzGGGGGGGGzGGG
GGGzGGGGGGGGzGGG
zzzzzNNNNNNzzzzz
GGGGGNNNNNNGGGGG
GGGGGNNONNNGGGGG
GGGGGNOOONNGGGGG
GGGGGNNONNNGGGGG
GGGGGNNONNNGGGGG
zzzzzNNONNNzzzzz
GGGGGNNONNNGGGGG
GGGGGNNNNNNGGGGG
GGGGGMNNNNMGGGGG
zzzzzGMNNMGzzzzz
GGGGGGGMMGGGGGGG
GGGGGGGGGGGGGGGG
zzzzzzzzzzzzzzzz
"""

CASTLE_TORCH_A = """
GGGzGGGGGGGGzGGG
GGGzGGGGGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGXGGGGGGGG
GGGGGGxXGGGGGGGG
GGGGGGxxXGGGGGGG
GGGGGGGxxGGGGGGG
zzzzzzznnzzzzzzz
GGGGGGGnnGGGGGGG
GGGGGGGnnGGGGGGG
zzzzzzzzzzzzzzzz
GGGGzGGGGGGGzGGG
GGGGzGGHGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGzGGGGGGG
GGHGGGGGzGGGGGGG
"""

CASTLE_TORCH_B = """
GGGzGGGGGGGGzGGG
GGGzGGGGGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGXGGGGGGG
GGGGGGGGXxGGGGGG
GGGGGGGXxxGGGGGG
GGGGGGGxxGGGGGGG
zzzzzzznnzzzzzzz
GGGGGGGnnGGGGGGG
GGGGGGGnnGGGGGGG
zzzzzzzzzzzzzzzz
GGGGzGGGGGGGzGGG
GGGGzGGHGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGzGGGGGGG
GGHGGGGGzGGGGGGG
"""

CASTLE_TORCH_OUT = """
GGGzGGGGGGGGzGGG
GGGzGGGGGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGNNGGGGGGG
GGGGGGGNNGGGGGGG
GGGGGGGMNGGGGGGG
GGGGGGGMNGGGGGGG
zzzzzzznnzzzzzzz
GGGGGGGnnGGGGGGG
GGGGGGGnnGGGGGGG
zzzzzzzzzzzzzzzz
GGGGzGGGGGGGzGGG
GGGGzGGHGGGGzGGG
zzzzzzzzzzzzzzzz
GGGGGGGGzGGGGGGG
GGHGGGGGzGGGGGGG
"""

RUIN_WALL_1 = """
GGGGGGGzGGGGGGGH
GHGGGGGzGGGGGGGG
GGGGGGGzGGGGGkGG
GGGGGGGzGGGGGGGG
zzzzzzzzzzzzzDzz
GGGkGGGGGGGGGDDG
GGGGGGGGGGGzGGGG
GHGGGGGGGGGzGGGG
DGGGGGGGGGGzGGGH
zzDzzzzzzzzzzzzz
GGGGGGGzGGGGGGGG
GGGGkGGzGGGHGGGG
GGGGGGGzGGGGGGGG
GGGGGGGzGGGGGGGk
zzzzzzzzzzzzzzzz
GGGHGGGGGGGGkGGG
"""

RUIN_WALL_2 = """
GGGzGGGGGGGGzGGG
GGGzGGGGGkGGzGGG
GHGzGGGGGGGGzGGH
DGGzGGGGGGGGzGGG
zzzzzzzzDDzzzzzz
GGGGGGGGGDGGGGGG
GGGGGGkGGGGGGGGG
GGzGGGGGGGGGHGGG
GGzGGGGGGGGGGGGD
zzzzzzzzzzzzzzDD
GGGGGGGGzGGGGGGG
GHGGGGGGzGGkGGGG
GGGGGGGGzGGGGGGG
GGGGkGGGzGGGGGGG
zzzzzzzzzzzzzzzz
GGGGGGGHGGGGGGGG
"""

RUIN_FLOOR_1 = """
DDDDDDDDDDDDDDDD
DDADDDDDDDDDADDD
DDDDDDDHDDDDDDDD
DDDDDDDDDDDDDDDD
DADDDDDDDDDDDDAD
DDDDDDDDDAADDDDD
DDDDDkDDDAADDDDD
DDDDDDDDDDDDDDDD
DDDDDDDDDDDDHDDD
DDADDDDDDDDDDDDD
DDDDDDDDDDDDDDDD
DDDDDDHHDDDDDADD
DDDDDDDHDDDDDDDD
DADDDDDDDDDDDDDD
DDDDDDDDDDkDDDDD
DDDDDDDDDDDDDDDD
"""

RUIN_FLOOR_2 = """
DDDDDDDDDDDDDDDD
DDDDDADDDDDDDDDD
DDDDDDDDDDDHHDDD
DDkDDDDDDDDDHDDD
DDDDDDDDDDDDDDDD
DDDDDDDDADDDDDDD
DDDADDDDDDDDDDDD
DDDDDDDDDDDDDADD
DDDDDDHDDDDDDDDD
DDDDDDDDDDDDDDDD
DADDDDDDDDkDDDDD
DDDDDDDDDDDDDDDD
DDDDDDDDDDDDDDDD
DDDDDAADDDDDDHDD
DDDDDAADDDDDDDDD
DDDDDDDDDDDDDDDD
"""

GATE = """
SSSjSSSSSSSjSSSS
jjjjjjjjjjjjjjjj
ZZZZZZZZZZZZZZZZ
.Z..Z..Z..Z..Z..
.Z..Z..Z..Z..Z..
ZZZZZZZZZZZZZZZZ
.Z..Z..Z..Z..Z..
.Z..Z..Z..Z..Z..
.Z..Z..Z..Z..Z..
.Z..Z..Z..Z..Z..
................
................
................
................
................
................
"""


def _rows(grid: str, name: str, palette=PALETTE) -> list[str]:
    return parse_frame(grid, name, TILE_PX, TILE_PX, palette)


def _shift_down(rows: list[str]) -> list[str]:
    """Derive an animation frame: rotate the tile one row down."""
    return [rows[-1]] + rows[:-1]


def _build_sheet(palette, *, torches_lit: bool) -> Image.Image:
    rows = lambda grid, name: _rows(grid, name, palette)
    torch_a = CASTLE_TORCH_A if torches_lit else CASTLE_TORCH_OUT
    torch_b = CASTLE_TORCH_B if torches_lit else CASTLE_TORCH_OUT
    art: dict[str, list[list[str]]] = {
        "planks": [rows(PLANKS_1, "planks_1"), rows(PLANKS_2, "planks_2")],
        "stone": [rows(STONE_1, "stone_1"), rows(STONE_2, "stone_2"),
                  rows(STONE_3, "stone_3")],
        # water: [v0f0, v0f1, v1f0, v1f1] — frame 1 derived by rotation.
        "water": [rows(WATER_1, "water_1"),
                  _shift_down(rows(WATER_1, "water_1")),
                  rows(WATER_2, "water_2"),
                  _shift_down(rows(WATER_2, "water_2"))],
        "floor": [rows(FLOOR, "floor")],
        "wall": [rows(WALL, "wall")],
        "awning": [rows(AWNING_1, "awning_1"), rows(AWNING_2, "awning_2")],
        "tavern_wall": [rows(TAVERN_WALL_1, "tavern_wall_1"),
                        rows(TAVERN_WALL_2, "tavern_wall_2")],
        "tavern_window": [rows(TAVERN_WINDOW, "tavern_window")],
        "tavern_roof": [rows(TAVERN_ROOF_1, "tavern_roof_1"),
                        rows(TAVERN_ROOF_2, "tavern_roof_2")],
        "tavern_eave": [rows(TAVERN_EAVE, "tavern_eave")],
        "castle_top": [rows(CASTLE_TOP_1, "castle_top_1"),
                       rows(CASTLE_TOP_2, "castle_top_2")],
        "castle_wall": [rows(CASTLE_WALL_1, "castle_wall_1"),
                        rows(CASTLE_WALL_2, "castle_wall_2")],
        "castle_banner": [rows(CASTLE_BANNER, "castle_banner")],
        "castle_torch": [rows(torch_a, "castle_torch_a"),
                         rows(torch_b, "castle_torch_b")],
        "gate": [rows(GATE, "gate")],
        "awning_edge": [rows(AWNING_EDGE, "awning_edge")],
        "ruin_wall": [rows(RUIN_WALL_1, "ruin_wall_1"),
                      rows(RUIN_WALL_2, "ruin_wall_2")],
        "ruin_floor": [rows(RUIN_FLOOR_1, "ruin_floor_1"),
                       rows(RUIN_FLOOR_2, "ruin_floor_2")],
    }
    sheet = Image.new(
        "RGBA", (SHEET_COLS * TILE_PX, SHEET_ROWS * TILE_PX), (0, 0, 0, 0)
    )
    for row_i, (name, variants, frames) in enumerate(TILESET_ORDER):
        cells = art[name]
        if len(cells) != variants * frames:
            raise ValueError(
                f"{name}: layout says {variants * frames} cells, art has "
                f"{len(cells)}"
            )
        for col_i, rows in enumerate(cells):
            for y, row in enumerate(rows):
                for x, char in enumerate(row):
                    sheet.putpixel(
                        (col_i * TILE_PX + x, row_i * TILE_PX + y),
                        palette[char],
                    )
    return sheet


def main() -> None:
    outputs = (
        ("docks.png", PALETTE, True),
        ("docks_midday.png", MIDDAY_PALETTE, False),
    )
    for filename, palette, torches_lit in outputs:
        sheet = _build_sheet(palette, torches_lit=torches_lit)
        out = ROOT / "assets" / "tilesets" / filename
        existing = Image.open(out).convert("RGBA") if out.exists() else None
        if (
            existing is None
            or existing.size != sheet.size
            or existing.tobytes() != sheet.tobytes()
        ):
            sheet.save(out)
            action = "Wrote"
        else:
            action = "Unchanged"
        print(f"{action} {out} ({SHEET_COLS}x{SHEET_ROWS} cells)")


if __name__ == "__main__":
    main()
