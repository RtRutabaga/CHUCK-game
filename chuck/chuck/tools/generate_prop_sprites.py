"""Generate standing-prop sprites (barrel, crate) from text grids.

Run from the project root (requires Pillow, dev-only):

    python tools/generate_prop_sprites.py

Writes to assets/sprites/objects/: barrel.png (14x19), crate.png
(16x20), bobert_barrel.png (16x24 — the landlord, asleep; Game Bible:
present, never named, never interactable), cigarette.png (7x5, with a
wisp of smoke), and astral_anchor.png (a 2-frame ashtray
sheet: cold and empty | cigarette burning, ember lit).
Props render TALLER than their 16px tile and are y-sorted with the
characters, so Chuck (14px, one foot tall) visibly walks behind them —
the scale pillar's payoff. Anchored at the tile's bottom edge.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spritegen import render_sheet

PALETTE = {
    ".": (0, 0, 0, 0),
    "B": (146, 98, 56, 255),   # barrel stave brown
    "b": (104, 68, 38, 255),   # stave shadow
    "L": (176, 130, 78, 255),  # lid / lit top
    "K": (72, 64, 58, 255),    # iron band
    "C": (150, 112, 66, 255),  # crate plank
    "c": (112, 82, 48, 255),   # crate plank shadow
    "T": (182, 142, 88, 255),  # crate top face
    "n": (60, 52, 46, 255),    # nail / seam
    # Bobert
    "F": (216, 172, 134, 255), # skin
    "e": (66, 54, 48, 255),    # closed eyes
    "D": (152, 146, 142, 255), # gray beard
    "A": (198, 154, 118, 255), # forearms over the rim
    # cigarette
    "W": (236, 236, 228, 255), # paper
    "O": (242, 146, 66, 255),  # ember
    "u": (198, 198, 188, 255), # paper underside
    "f": (150, 150, 162, 255), # smoke wisp
    # astral anchor (an ashtray; the ember is the light)
    "S": (128, 126, 130, 255), # dish rim / grate stone frame
    "E": (94, 92, 96, 255),    # dish shadow / frame inner edge
    "k": (58, 56, 68, 255),    # cold ash well
    # HEROD sign
    "Q": (222, 206, 170, 255), # parchment
    "z": (92, 74, 58, 255),    # ink (illegible at rat scale; correct)
    "G": (168, 112, 52, 255),  # the guitar
    # tavern door
    "Y": (104, 72, 44, 255),   # door planks
    "y": (78, 52, 32, 255),    # plank seams / crossbeams
    "M": (176, 156, 116, 255), # handles
    "J": (54, 50, 48, 255),    # lantern iron
    "q": (240, 180, 80, 255),  # lantern glow
    "x": (252, 214, 120, 255), # flame
    # chimney
    "V": (128, 92, 64, 255),   # chimney brick
    "v": (100, 70, 48, 255),   # chimney mortar
    # sewer grate
    "I": (104, 106, 112, 255), # iron bar
    "i": (74, 76, 82, 255),    # iron shadow
    "_": (28, 26, 30, 255),    # the dark below
    # market stall produce + table
    "a": (118, 168, 60, 255),  # green produce
    "g": (88, 128, 44, 255),   # green shade
    "r": (196, 64, 52, 255),   # red produce
    "R": (150, 44, 38, 255),   # red shade
    "o": (224, 132, 40, 255),  # orange produce
    "0": (178, 100, 30, 255),  # orange shade
    "u": (52, 86, 128, 255),   # table cloth
    "U": (40, 66, 100, 255),   # cloth folds
}

BARREL = """
....LLLLLL....
..LLLLLLLLLL..
.LLLLLLLLLLLL.
.KKKKKKKKKKKK.
.BBbBBBBbBBBB.
BBBbBBBBbBBBBB
BBBbBBBBbBBBBB
BBBbBBBBbBBBBB
KKKKKKKKKKKKKK
BBBbBBBBbBBBBB
BBBbBBBBbBBBBB
BBBbBBBBbBBBBB
BBBbBBBBbBBBBB
KKKKKKKKKKKKKK
BBBbBBBBbBBBBB
.BBbBBBBbBBBB.
.BBbBBBBbBBBB.
..bbBBBBbBBb..
....bbbbbb....
"""

CRATE = """
TTTTTTTTTTTTTTTT
TnTTTTTTTTTTTTnT
TTTTTTTTTTTTTTTT
TTTTTTTTTTTTTTTT
TnTTTTTTTTTTTTnT
cccccccccccccccc
CCCCCCCCCCCCCCCC
CCCCCCCCCCCCCCCC
CCCCCCCCCCCCCCCC
cccccccccccccccc
CCCCCCCCCCCCCCCC
CCCCCCCCCCCCCCCC
CCCCCCCCCCCCCCCC
cccccccccccccccc
CCCCCCCCCCCCCCCC
CCCCCCCCCCCCCCCC
CCCCCCCCCCCCCCCC
cccccccccccccccc
CnCCCCCCCCCCCCnC
cccccccccccccccc
"""


BOBERT_BARREL = """
......FFFF......
.....FFFFFF.....
....FFFFFFFF....
....FFFFFFFF....
....FeeFFeeF....
....DFFFFFFD....
.LLLDDFFFFDDLLL.
.KKKDDDDDDDDKKK.
.BBAADDDDDDAABB.
.BBbBBBBBBBBbBB.
.BBbBBBBBBBBbBB.
.KKKKKKKKKKKKKK.
.BBbBBBBBBBBbBB.
.BBbBBBBBBBBbBB.
.BBbBBBBBBBBbBB.
.BBbBBBBBBBBbBB.
.KKKKKKKKKKKKKK.
.BBbBBBBBBBBbBB.
.BBbBBBBBBBBbBB.
.BBbBBBBBBBBbBB.
.BBbBBBBBBBBbBB.
.BBbBBBBBBBBbBB.
..bbBBBBBBBBbb..
....bbbbbbbb....
"""

HOUSE_DOOR = """
.nnnnnnnnnnnn.
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnyyyyyyyyyynn
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnYYYyYYyYMYnn
nnYYYyYYyYMYnn
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnyyyyyyyyyynn
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnYYYyYYyYYYnn
nnnnnnnnnnnnnn
"""

SEWER_GRATE = """
SSSSSSSSSSSSSSSS
SEEEEEEEEEEEEEES
SE__________EE_S
SEIIIIIIIIIIiE_S
SE_iiiiiiiiiiE_S
SEIIIIIIIIIIiE_S
SE_iiiiiiiiiiE_S
SEIIIIIIIIIIiE_S
SE_iiiiiiiiiiE_S
SEIIIIIIIIIIiE_S
SE__________EE_S
SEEEEEEEEEEEEEES
SSSSSSSSSSSSSSSS
"""

CHIMNEY = """
kkkkkkkkkkkk
kkkkkkkkkkkk
.VVvVVVvVVV.
.VVvVVVvVVV.
.vvvvvvvvvv.
.VVVVvVVVVV.
.VVVVvVVVVV.
.vvvvvvvvvv.
.VVvVVVvVVV.
.VVvVVVvVVV.
.vvvvvvvvvv.
.VVVVvVVVVV.
.VVVVvVVVVV.
.vvvvvvvvvv.
.VVvVVVvVVV.
.VVvVVVvVVV.
.vvvvvvvvvv.
.VVVVvVVVVV.
.VVVVvVVVVV.
.vvvvvvvvvv.
.VVvVVVvVVV.
.VVvVVVvVVV.
"""

CIGARETTE = """
.....f.
....f..
.......
WWWWWWO
uuuuuu.
"""

HEROD_SIGN = """
.nnnnnnnnnnnnnn.
.nQQQQQQQQQQQQn.
.nQzzQzQQzzQzQn.
.nQzQzQzQzQQzQn.
.nQQQQQQQQQQQQn.
.nQzzzQQzQzzQQn.
.nQQQQQQQQQQQQn.
.nQQQQQzQQQQQQn.
.nQQQQQzQQQQQQn.
.nQQQQGGGQQQQQn.
.nQQQQGGGQQQQQn.
.nQQQQQGQQQQQQn.
.nQQQQQQQQQQQQn.
.nnnnnnnnnnnnnn.
..bb........bb..
..bb........bb..
..bb........bb..
..bb........bb..
..bb........bb..
..bb........bb..
..bb........bb..
..bb........bb..
..bb........bb..
..bb........bb..
"""

ANCHOR_DIM = """
............
............
............
..SSSSSSSS..
.SSSSSSSSSS.
.SSkkkkkkSS.
.SSkkkkkkSS.
.SSSSSSSSSS.
.EEEEEEEEEE.
..EEEEEEEE..
"""

ANCHOR_LIT = """
.....f......
......f.....
............
..SSSSSSSS..
.SSSSSSSSSS.
.SSkWWWWOSS.
.SSkkkOxkSS.
.SSSSSSSSSS.
.EEEEEEEEEE.
..EEEEEEEE..
"""


STALL_POST = """
nnnnnn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nyyyyn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nyyyyn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nYYYYn
nyyyyn
nYYYYn
nnnnnn
"""

STALL_TABLE = """
........WW..........
........WW....qq.qq.
.......nWWn...qq.qq.
uuuuuuuuuuuuuuuuuuuu
uuuuUuuuuuuuuUuuuuuu
uuuuUuuuuuuuuUuuuuuu
uuuuuuuuuuuuuuuuuuuu
UuuUuuUuuUuuUuuUuuUu
.U.U.U.U.U.U.U.U.U.U
....................
..CC............CC..
..CC............CC..
..CC............CC..
..CC............CC..
..cc............cc..
....................
"""


def _produce_crate(main: str, dark: str) -> str:
    """A crate heaped with produce: rounds over the crate body."""
    top = [
        ".{m}{m}.{m}{m}..{m}{m}.{m}{m}..",
        "{m}{m}{m}{d}{m}{m}{d}.{m}{m}{d}{m}{m}{d}..",
        ".{m}{m}{d}{m}{m}{m}{m}{d}{m}{m}{m}{m}{d}{m}{m}",
        "{m}{m}{m}{m}{d}{m}{m}{m}{m}{d}{m}{m}{m}{m}{d}{m}",
        ".{d}{m}{m}{m}{d}.{d}{m}{m}{d}.{d}{m}{m}{d}",
    ]
    top = [row.format(m=main, d=dark).ljust(16, ".")[:16] for row in top]
    crate_body = CRATE.strip("\n").split("\n")[5:]  # keep from the seam down
    return "\n".join(top + crate_body)


def _build_tavern_door() -> str:
    """A 48x34 sprite: the human-scale double door with a hanging iron
    lantern on each side (glowing, per the facade reference).

    The door leaves occupy the center 32px; lanterns hang in the outer
    8px margins so the whole entrance reads as one warm unit.
    """
    W, H, OX = 48, 34, 8  # door offset into the wider canvas
    g = [["." for _ in range(W)] for _ in range(H)]
    for y in range(H):
        for x in range(32):
            if x in (0, 1, 30, 31) or y in (0, 1, 32, 33):
                g[y][x + OX] = "n"
    for x, y in ((0, 0), (1, 0), (0, 1), (30, 0), (31, 0), (31, 1)):
        g[y][x + OX] = "."  # softened arch corners
    for y in range(2, 32):
        for x in range(2, 30):
            g[y][x + OX] = "Y"
        for x in (6, 10, 15, 16, 21, 25):  # plank seams + center meet
            g[y][x + OX] = "y"
    for x in range(2, 30):  # crossbeams
        g[8][x + OX] = "y"
        g[24][x + OX] = "y"
    for y in (17, 18, 19):  # handles
        g[y][13 + OX] = "M"
        g[y][18 + OX] = "M"
    for lx in (2, 41):  # hanging lanterns, both sides
        g[10][lx + 1], g[10][lx + 2] = "J", "J"  # bracket
        g[11][lx + 2] = "J"                      # hook
        for y in range(12, 21):                  # body frame
            for x in range(lx, lx + 5):
                g[y][x] = "J"
        for y in range(14, 19):                  # glass glow
            for x in range(lx + 1, lx + 4):
                g[y][x] = "q"
        g[16][lx + 2] = "x"                      # the flame
    return "\n".join("".join(row) for row in g)


def _build_tavern_open() -> str:
    """The same human-scale entrance after the sewer: doors gone, dark within."""
    width, height, offset = 48, 34, 8
    grid = [["." for _ in range(width)] for _ in range(height)]
    # A heavy two-pixel frame around a black, readable opening. The bottom
    # stays open except for a pale stone sill, so it reads as a threshold.
    for y in range(height):
        for x in range(32):
            world_x = x + offset
            if x in (0, 1, 30, 31) or y in (0, 1):
                grid[y][world_x] = "n"
            elif y < 32:
                grid[y][world_x] = "_"
    for x, y in ((0, 0), (1, 0), (0, 1), (30, 0), (31, 0), (31, 1)):
        grid[y][x + offset] = "."
    for x in range(2, 30):
        grid[32][x + offset] = "S"
        grid[33][x + offset] = "E"
    # Keep the familiar lanterns lit on either side of the changed doorway.
    for lantern_x in (2, 41):
        grid[10][lantern_x + 1] = "J"
        grid[10][lantern_x + 2] = "J"
        grid[11][lantern_x + 2] = "J"
        for y in range(12, 21):
            for x in range(lantern_x, lantern_x + 5):
                grid[y][x] = "J"
        for y in range(14, 19):
            for x in range(lantern_x + 1, lantern_x + 4):
                grid[y][x] = "q"
        grid[16][lantern_x + 2] = "x"
    return "\n".join("".join(row) for row in grid)


def _build_tavern_table() -> str:
    """A broad human table whose underside is a room at Chuck's scale."""
    width, height = 24, 16
    grid = [["." for _ in range(width)] for _ in range(height)]
    for y in range(2, 10):
        for x in range(1, width - 1):
            grid[y][x] = "C"
    for x in range(width):
        grid[1][x] = "T"
        grid[9][x] = "c"
    for leg_x in (3, 4, 19, 20):
        for y in range(10, height):
            grid[y][leg_x] = "c"
    return "\n".join("".join(row) for row in grid)


def _build_tavern_chair() -> str:
    width, height = 12, 14
    grid = [["." for _ in range(width)] for _ in range(height)]
    for y in range(0, 7):
        for x in range(2, 10):
            grid[y][x] = "C" if x not in (3, 8) else "c"
    for x in range(1, 11):
        grid[7][x] = "T"
        grid[8][x] = "C"
    for leg_x in (2, 3, 8, 9):
        for y in range(9, height):
            grid[y][leg_x] = "c"
    return "\n".join("".join(row) for row in grid)


def _build_bar_counter() -> str:
    width, height = 16, 20
    grid = [["." for _ in range(width)] for _ in range(height)]
    for y in range(3, height):
        for x in range(width):
            grid[y][x] = "C"
    for y in (2, 8, 15, 19):
        for x in range(width):
            grid[y][x] = "c" if y != 2 else "T"
    for x in (0, 7, 8, 15):
        for y in range(3, height):
            grid[y][x] = "c"
    return "\n".join("".join(row) for row in grid)


def _build_tavern_hearth() -> str:
    width, height = 28, 26
    grid = [["." for _ in range(width)] for _ in range(height)]
    for y in range(3, height):
        for x in range(2, width - 2):
            grid[y][x] = "S"
    for y in range(8, 24):
        for x in range(7, 21):
            grid[y][x] = "_"
    for x in range(5, 23):
        grid[2][x] = "E"
        grid[3][x] = "S"
    for x in range(4, 24):
        grid[24][x] = "E"
        grid[25][x] = "S"
    # One restrained, readable flame in the dark firebox.
    for x, y, char in (
        (13, 14, "O"), (14, 14, "O"), (12, 15, "q"), (13, 15, "x"),
        (14, 15, "x"), (15, 15, "q"), (11, 16, "O"), (12, 16, "x"),
        (13, 16, "x"), (14, 16, "x"), (15, 16, "x"), (16, 16, "O"),
        (10, 17, "q"), (11, 17, "O"), (12, 17, "O"), (13, 17, "x"),
        (14, 17, "x"), (15, 17, "O"), (16, 17, "O"), (17, 17, "q"),
        (10, 18, "O"), (11, 18, "O"), (12, 18, "O"), (13, 18, "O"),
        (14, 18, "O"), (15, 18, "O"), (16, 18, "O"), (17, 18, "O"),
    ):
        grid[y][x] = char
    return "\n".join("".join(row) for row in grid)


def _build_cheese() -> str:
    """A bright floor-level wedge, readable without becoming a pickup."""
    return "\n".join((
        "..........",
        "......q...",
        "....qqqq..",
        "..qqxqqq..",
        ".qqqqOqqq.",
        "qqxqqqqqqq",
        "OOOOOOOOOO",
    ))


def _build_pantry_door() -> str:
    """A human-scale rear door that frames the next Phase 3 route."""
    width, height = 24, 30
    grid = [["." for _ in range(width)] for _ in range(height)]
    for y in range(2, height):
        for x in range(2, width - 2):
            grid[y][x] = "Y"
    for x in range(2, width - 2):
        grid[2][x] = "L"
        grid[3][x] = "y"
        grid[height - 1][x] = "y"
    for y in range(2, height):
        for x in (2, 3, width - 4, width - 3, width // 2):
            grid[y][x] = "y"
    for y in (10, 20):
        for x in range(4, width - 3):
            grid[y][x] = "y"
    grid[16][width // 2 - 3] = "M"
    return "\n".join("".join(row) for row in grid)


def _build_pantry_open() -> str:
    """A dark human doorway with a restrained timber frame."""
    width, height = 24, 30
    grid = [["." for _ in range(width)] for _ in range(height)]
    for y in range(3, height):
        for x in range(4, width - 4):
            grid[y][x] = "_"
    for y in range(2, height):
        for x in (2, 3, width - 4, width - 3):
            grid[y][x] = "y"
    for x in range(2, width - 2):
        grid[2][x] = "L"
        grid[3][x] = "y"
    return "\n".join("".join(row) for row in grid)


def _build_pantry_shelf() -> str:
    """Human storage shelves with jars looming above Chuck."""
    width, height = 28, 24
    grid = [["." for _ in range(width)] for _ in range(height)]
    for y in range(2, height):
        for x in (1, 2, width - 3, width - 2):
            grid[y][x] = "c"
    for shelf_y in (3, 11, 19):
        for x in range(1, width - 1):
            grid[shelf_y][x] = "T" if shelf_y == 3 else "C"
            grid[shelf_y + 1][x] = "c"
    for base_x, jar in ((5, "q"), (10, "S"), (16, "O"), (21, "q")):
        for y in range(6, 11):
            for x in range(base_x, base_x + 4):
                grid[y][x] = jar
        grid[5][base_x + 1] = "M"
        grid[5][base_x + 2] = "M"
    for base_x, jar in ((7, "S"), (14, "q"), (20, "O")):
        for y in range(14, 19):
            for x in range(base_x, base_x + 4):
                grid[y][x] = jar
        grid[13][base_x + 1] = "M"
        grid[13][base_x + 2] = "M"
    return "\n".join("".join(row) for row in grid)


def _build_grain_sack() -> str:
    """A tied food sack, slightly taller than Chuck."""
    return "\n".join((
        ".....cc.....",
        "....cTTc....",
        ".....cc.....",
        "...TTTTTT...",
        "..TTTTTTTT..",
        ".TTTTTTTTTT.",
        ".TTTTCTTTTT.",
        "TTTTTCTTTTTT",
        "TTTTTTTTTTTT",
        "TTTTTTTTTTTT",
        "TTTTTCTTTTTT",
        ".TTTTCTTTTT.",
        ".TTTTTTTTTT.",
        "..CCCCCCCC..",
        "...cccccc...",
        "............",
    ))


def _write(name: str, grid: str, w: int, h: int) -> None:
    out = (Path(__file__).resolve().parents[1]
           / "assets" / "sprites" / "objects" / f"{name}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    render_sheet([[grid]], [[name]], w, h, PALETTE).save(out)
    print(f"Wrote {out}")


def _write_sheet(name: str, grids: list[str], names: list[str],
                 w: int, h: int) -> None:
    out = (Path(__file__).resolve().parents[1]
           / "assets" / "sprites" / "objects" / f"{name}.png")
    render_sheet([grids], [names], w, h, PALETTE).save(out)
    print(f"Wrote {out}")


def main() -> None:
    _write("barrel", BARREL, 14, 19)
    _write("crate", CRATE, 16, 20)
    _write("bobert_barrel", BOBERT_BARREL, 16, 24)
    _write("herod_sign", HEROD_SIGN, 16, 24)
    _write("tavern_door", _build_tavern_door(), 48, 34)
    _write("tavern_open", _build_tavern_open(), 48, 34)
    _write("tavern_table", _build_tavern_table(), 24, 16)
    _write("tavern_chair", _build_tavern_chair(), 12, 14)
    _write("bar_counter", _build_bar_counter(), 16, 20)
    _write("tavern_hearth", _build_tavern_hearth(), 28, 26)
    _write("cheese", _build_cheese(), 10, 7)
    _write("pantry_door", _build_pantry_door(), 24, 30)
    _write("pantry_open", _build_pantry_open(), 24, 30)
    _write("pantry_shelf", _build_pantry_shelf(), 28, 24)
    _write("grain_sack", _build_grain_sack(), 12, 16)
    _write("chimney", CHIMNEY, 12, 22)
    _write("sewer_grate", SEWER_GRATE, 16, 13)
    _write("house_door", HOUSE_DOOR, 14, 20)
    _write("stall_post", STALL_POST, 6, 26)
    _write("stall_table", STALL_TABLE, 20, 16)
    _write("crate_green", _produce_crate("a", "g"), 16, 20)
    _write("crate_red", _produce_crate("r", "R"), 16, 20)
    _write("crate_orange", _produce_crate("o", "0"), 16, 20)
    _write("cigarette", CIGARETTE, 7, 5)
    # The Astral Anchor presents as an ashtray: cold ash when
    # dormant, a live ember when attuned. Of course it does.
    _write_sheet("astral_anchor", [ANCHOR_DIM, ANCHOR_LIT],
                 ["anchor_dim", "anchor_lit"], 12, 10)


if __name__ == "__main__":
    main()
