"""Generate the game's pixel font sheet from text-grid glyph art.

Run from the project root (requires Pillow, dev-only):

    python tools/generate_font.py

Writes assets/fonts/pixel_font.png: one row of 5x9 glyph cells in
GLYPH_ORDER (defined in src/ui/bitmap_font.py — the single source of
truth shared with the runtime). Glyphs are baked in the dialogue text
color; rendering never tints or anti-aliases, so text stays crisp at
native resolution.

Every glyph is validated (5 wide, 9 tall, only 'X'/'.') and the set is
checked against GLYPH_ORDER in both directions — a missing or extra
glyph is a loud error.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from PIL import Image

from src.core import config
from src.ui.bitmap_font import GLYPH_H, GLYPH_ORDER, GLYPH_W

# Rows 0-6: body (caps and ascenders use all 7; lowercase x-height is
# rows 2-6). Rows 7-8: descenders (g j p q y , ;).
GLYPHS: dict[str, list[str]] = {
"A": ["..X..",".X.X.","X...X","X...X","XXXXX","X...X","X...X",".....","....."],
"B": ["XXXX.","X...X","X...X","XXXX.","X...X","X...X","XXXX.",".....","....."],
"C": [".XXX.","X...X","X....","X....","X....","X...X",".XXX.",".....","....."],
"D": ["XXXX.","X...X","X...X","X...X","X...X","X...X","XXXX.",".....","....."],
"E": ["XXXXX","X....","X....","XXXX.","X....","X....","XXXXX",".....","....."],
"F": ["XXXXX","X....","X....","XXXX.","X....","X....","X....",".....","....."],
"G": [".XXX.","X...X","X....","X.XXX","X...X","X...X",".XXX.",".....","....."],
"H": ["X...X","X...X","X...X","XXXXX","X...X","X...X","X...X",".....","....."],
"I": [".XXX.","..X..","..X..","..X..","..X..","..X..",".XXX.",".....","....."],
"J": ["..XXX","...X.","...X.","...X.","...X.","X..X.",".XX..",".....","....."],
"K": ["X...X","X..X.","X.X..","XX...","X.X..","X..X.","X...X",".....","....."],
"L": ["X....","X....","X....","X....","X....","X....","XXXXX",".....","....."],
"M": ["X...X","XX.XX","X.X.X","X.X.X","X...X","X...X","X...X",".....","....."],
"N": ["X...X","XX..X","X.X.X","X..XX","X...X","X...X","X...X",".....","....."],
"O": [".XXX.","X...X","X...X","X...X","X...X","X...X",".XXX.",".....","....."],
"P": ["XXXX.","X...X","X...X","XXXX.","X....","X....","X....",".....","....."],
"Q": [".XXX.","X...X","X...X","X...X","X.X.X","X..X.",".XX.X",".....","....."],
"R": ["XXXX.","X...X","X...X","XXXX.","X.X..","X..X.","X...X",".....","....."],
"S": [".XXXX","X....","X....",".XXX.","....X","....X","XXXX.",".....","....."],
"T": ["XXXXX","..X..","..X..","..X..","..X..","..X..","..X..",".....","....."],
"U": ["X...X","X...X","X...X","X...X","X...X","X...X",".XXX.",".....","....."],
"V": ["X...X","X...X","X...X","X...X","X...X",".X.X.","..X..",".....","....."],
"W": ["X...X","X...X","X...X","X.X.X","X.X.X","XX.XX","X...X",".....","....."],
"X": ["X...X","X...X",".X.X.","..X..",".X.X.","X...X","X...X",".....","....."],
"Y": ["X...X","X...X",".X.X.","..X..","..X..","..X..","..X..",".....","....."],
"Z": ["XXXXX","....X","...X.","..X..",".X...","X....","XXXXX",".....","....."],
"a": [".....",".....",".XXX.","....X",".XXXX","X...X",".XXXX",".....","....."],
"b": ["X....","X....","XXXX.","X...X","X...X","X...X","XXXX.",".....","....."],
"c": [".....",".....",".XXX.","X....","X....","X....",".XXX.",".....","....."],
"d": ["....X","....X",".XXXX","X...X","X...X","X...X",".XXXX",".....","....."],
"e": [".....",".....",".XXX.","X...X","XXXXX","X....",".XXX.",".....","....."],
"f": ["..XX.",".X...","XXXX.",".X...",".X...",".X...",".X...",".....","....."],
"g": [".....",".....",".XXXX","X...X","X...X",".XXXX","....X","X...X",".XXX."],
"h": ["X....","X....","XXXX.","X...X","X...X","X...X","X...X",".....","....."],
"i": ["..X..",".....",".XX..","..X..","..X..","..X..",".XXX.",".....","....."],
"j": ["...X.",".....","..XX.","...X.","...X.","...X.","...X.","X..X.",".XX.."],
"k": ["X....","X....","X..X.","X.X..","XX...","X.X..","X..X.",".....","....."],
"l": [".XX..","..X..","..X..","..X..","..X..","..X..",".XXX.",".....","....."],
"m": [".....",".....","XX.X.","X.X.X","X.X.X","X.X.X","X.X.X",".....","....."],
"n": [".....",".....","XXXX.","X...X","X...X","X...X","X...X",".....","....."],
"o": [".....",".....",".XXX.","X...X","X...X","X...X",".XXX.",".....","....."],
"p": [".....",".....","XXXX.","X...X","X...X","XXXX.","X....","X....","X...."],
"q": [".....",".....",".XXXX","X...X","X...X",".XXXX","....X","....X","....X"],
"r": [".....",".....","X.XX.","XX..X","X....","X....","X....",".....","....."],
"s": [".....",".....",".XXXX","X....",".XXX.","....X","XXXX.",".....","....."],
"t": [".X...",".X...","XXXX.",".X...",".X...",".X..X","..XX.",".....","....."],
"u": [".....",".....","X...X","X...X","X...X","X...X",".XXXX",".....","....."],
"v": [".....",".....","X...X","X...X","X...X",".X.X.","..X..",".....","....."],
"w": [".....",".....","X...X","X.X.X","X.X.X","X.X.X",".X.X.",".....","....."],
"x": [".....",".....","X...X",".X.X.","..X..",".X.X.","X...X",".....","....."],
"y": [".....",".....","X...X","X...X","X...X",".XXXX","....X","X...X",".XXX."],
"z": [".....",".....","XXXXX","...X.","..X..",".X...","XXXXX",".....","....."],
"0": [".XXX.","X..XX","X.X.X","X.X.X","XX..X","X...X",".XXX.",".....","....."],
"1": ["..X..",".XX..","..X..","..X..","..X..","..X..",".XXX.",".....","....."],
"2": [".XXX.","X...X","....X","..XX.",".X...","X....","XXXXX",".....","....."],
"3": [".XXX.","X...X","....X","..XX.","....X","X...X",".XXX.",".....","....."],
"4": ["...X.","..XX.",".X.X.","X..X.","XXXXX","...X.","...X.",".....","....."],
"5": ["XXXXX","X....","XXXX.","....X","....X","X...X",".XXX.",".....","....."],
"6": [".XXX.","X....","X....","XXXX.","X...X","X...X",".XXX.",".....","....."],
"7": ["XXXXX","....X","...X.","..X..","..X..","..X..","..X..",".....","....."],
"8": [".XXX.","X...X","X...X",".XXX.","X...X","X...X",".XXX.",".....","....."],
"9": [".XXX.","X...X","X...X",".XXXX","....X","....X",".XXX.",".....","....."],
".": [".....",".....",".....",".....",".....",".XX..",".XX..",".....","....."],
",": [".....",".....",".....",".....",".....",".XX..",".XX..","..X..",".X..."],
"!": ["..X..","..X..","..X..","..X..","..X..",".....","..X..",".....","....."],
"?": [".XXX.","X...X","....X","..XX.","..X..",".....","..X..",".....","....."],
"'": ["..X..","..X..",".....",".....",".....",".....",".....",".....","....."],
"\"": [".X.X.",".X.X.",".....",".....",".....",".....",".....",".....","....."],
"-": [".....",".....",".....",".XXX.",".....",".....",".....",".....","....."],
":": [".....",".....",".XX..",".XX..",".....",".XX..",".XX..",".....","....."],
";": [".....",".....",".XX..",".XX..",".....",".XX..",".XX..","..X..",".X..."],
"(": ["...X.","..X..",".X...",".X...",".X...","..X..","...X.",".....","....."],
")": [".X...","..X..","...X.","...X.","...X.","..X..",".X...",".....","....."],
"/": ["....X","...X.","...X.","..X..",".X...",".X...","X....",".....","....."],
" ": [".....",".....",".....",".....",".....",".....",".....",".....","....."],
">": ["X....",".X...","..X..","...X.","..X..",".X...","X....",".....","....."],
}


def main() -> None:
    # Two-way check against the runtime's glyph order.
    missing = [c for c in GLYPH_ORDER if c not in GLYPHS]
    extra = [c for c in GLYPHS if c not in GLYPH_ORDER]
    if missing or extra:
        raise ValueError(f"Glyph set mismatch. Missing: {missing} Extra: {extra}")

    color = (*config.COLOR_DIALOGUE_TEXT, 255)
    sheet = Image.new("RGBA", (GLYPH_W * len(GLYPH_ORDER), GLYPH_H), (0, 0, 0, 0))
    for i, char in enumerate(GLYPH_ORDER):
        rows = GLYPHS[char]
        if len(rows) != GLYPH_H or any(len(r) != GLYPH_W for r in rows):
            raise ValueError(f"Glyph {char!r} is not {GLYPH_W}x{GLYPH_H}")
        for y, row in enumerate(rows):
            for x, px in enumerate(row):
                if px == "X":
                    sheet.putpixel((i * GLYPH_W + x, y), color)
                elif px != ".":
                    raise ValueError(f"Glyph {char!r}: bad pixel char {px!r}")
    out = ROOT / "assets" / "fonts" / "pixel_font.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"Wrote {out} ({len(GLYPH_ORDER)} glyphs)")


if __name__ == "__main__":
    main()
