"""Generate Phase 14's shared Waterdeep fountain plaza and its props.

The map is deliberately built from the docks terrain vocabulary.  Opening and
returned Waterdeep therefore share geometry; runtime state chooses the older
or midday docks sheet and adds only the busier crowd.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
MAP_OUT = ROOT / "assets" / "maps" / "waterdeep_plaza.txt"
SPRITE_OUT = ROOT / "assets" / "sprites" / "objects"
WIDTH = 48
HEIGHT = 34
# Battlements plus three courses: the closed gate is three tiles and a
# bit tall, and a wall shorter than the gate is not a wall it is in.
NORTH_WALL_ROWS = 4


def fountain(frame: int) -> Image.Image:
    image = Image.new("RGBA", (72, 56), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    outline = (48, 51, 52, 255)
    stone_dark = (83, 88, 87, 255)
    stone = (126, 132, 128, 255)
    stone_light = (166, 169, 158, 255)
    water_dark = (31, 111, 126, 255)
    water = (57, 168, 176, 255)
    water_light = (138, 223, 212, 255)

    draw.ellipse((4, 45, 68, 55), fill=(33, 38, 39, 150))
    draw.ellipse((2, 34, 70, 53), fill=outline)
    draw.ellipse((6, 35, 66, 49), fill=stone_light)
    draw.ellipse((9, 37, 63, 47), fill=water_dark)
    draw.ellipse((12, 38, 60, 45), fill=water)
    draw.rectangle((7, 41, 65, 48), fill=stone)
    draw.line((8, 47, 64, 47), fill=stone_dark, width=3)
    draw.ellipse((7, 43, 65, 52), outline=outline, width=2)

    draw.polygon(((31, 38), (41, 38), (39, 20), (33, 20)), fill=outline)
    draw.polygon(((34, 37), (39, 37), (38, 21), (34, 21)), fill=stone)
    draw.ellipse((23, 16, 49, 25), fill=outline)
    draw.ellipse((26, 17, 46, 22), fill=water)
    draw.rectangle((25, 20, 47, 23), fill=stone)
    draw.line((27, 22, 45, 22), fill=stone_dark)

    # Four restrained frame states: the jets trade one pixel of height and
    # their falling beads move, which reads at native resolution without foam.
    lift = (1, 0, 2, 0)[frame]
    draw.line((36, 17, 36, 4 + lift), fill=water_dark, width=2)
    draw.line((37, 16, 37, 3 + lift), fill=water_light)
    for x, direction in ((30, -1), (42, 1)):
        top = 9 + ((frame + (0 if direction < 0 else 2)) % 3)
        draw.arc((min(x, 36), top, max(x, 36), 20), 190 if direction < 0 else 270,
                 350 if direction < 0 else 90, fill=water_light, width=1)
    bead_y = 12 + frame
    draw.point((28, bead_y), fill=water_light)
    draw.point((44, 15 + ((frame + 2) % 4)), fill=water_light)
    return image


def closed_gate() -> Image.Image:
    image = Image.new("RGBA", (64, 52), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    outline = (43, 45, 44, 255)
    stone_dark = (82, 84, 80, 255)
    stone = (124, 124, 113, 255)
    stone_light = (163, 157, 137, 255)
    iron = (46, 49, 51, 255)
    iron_light = (91, 94, 92, 255)
    draw.rectangle((9, 8, 54, 51), fill=outline)
    draw.rectangle((13, 12, 50, 51), fill=(24, 27, 28, 255))
    draw.pieslice((9, 0, 54, 35), 180, 360, fill=outline)
    draw.pieslice((13, 4, 50, 31), 180, 360, fill=stone_dark)
    draw.rectangle((3, 13, 13, 51), fill=outline)
    draw.rectangle((51, 13, 61, 51), fill=outline)
    draw.rectangle((5, 15, 11, 49), fill=stone)
    draw.rectangle((53, 15, 59, 49), fill=stone)
    draw.line((6, 16, 10, 16), fill=stone_light, width=2)
    draw.line((54, 16, 58, 16), fill=stone_light, width=2)
    for x in range(17, 49, 6):
        draw.rectangle((x, 15, x + 2, 49), fill=iron)
        draw.line((x + 1, 16, x + 1, 45), fill=iron_light)
        draw.polygon(((x, 49), (x + 2, 49), (x + 1, 52)), fill=iron)
    draw.rectangle((14, 26, 50, 29), fill=iron)
    return image


def forge() -> Image.Image:
    image = Image.new("RGBA", (40, 34), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    dark = (48, 45, 42, 255)
    stone_dark = (84, 78, 69, 255)
    stone = (126, 112, 91, 255)
    ember = (187, 60, 30, 255)
    flame = (247, 153, 48, 255)
    draw.ellipse((2, 28, 38, 33), fill=(35, 36, 35, 150))
    draw.rectangle((4, 10, 35, 31), fill=dark)
    for y in (11, 19, 27):
        draw.line((5, y, 34, y), fill=stone_dark, width=2)
    for x, y in ((12, 11), (26, 11), (19, 20), (30, 20)):
        draw.line((x, y, x, y + 7), fill=stone_dark)
    draw.rectangle((7, 13, 32, 29), outline=stone, width=2)
    draw.rectangle((11, 18, 28, 28), fill=(23, 23, 22, 255))
    draw.rectangle((13, 25, 26, 28), fill=ember)
    draw.polygon(((17, 25), (20, 17), (22, 25)), fill=flame)
    draw.rectangle((8, 6, 14, 11), fill=dark)
    draw.rectangle((9, 0, 13, 7), fill=stone_dark)
    return image


def anvil() -> Image.Image:
    image = Image.new("RGBA", (28, 18), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    outline = (42, 45, 47, 255)
    iron = (79, 86, 89, 255)
    light = (137, 143, 140, 255)
    draw.ellipse((2, 14, 25, 17), fill=(28, 31, 31, 150))
    draw.polygon(((2, 3), (20, 3), (26, 6), (19, 9), (7, 9), (4, 7)),
                 fill=outline)
    draw.polygon(((4, 3), (19, 3), (23, 5), (18, 6), (6, 6)), fill=light)
    draw.polygon(((9, 7), (18, 7), (17, 14), (8, 14)), fill=iron)
    draw.rectangle((5, 13, 21, 16), fill=outline)
    return image


def alchemist_display() -> Image.Image:
    image = Image.new("RGBA", (42, 34), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    wood_dark = (65, 48, 34, 255)
    wood = (117, 78, 45, 255)
    trim = (171, 126, 68, 255)
    draw.ellipse((1, 29, 40, 33), fill=(31, 32, 31, 145))
    draw.rectangle((3, 7, 38, 30), fill=wood_dark)
    draw.rectangle((6, 9, 35, 27), fill=(38, 35, 31, 255))
    draw.line((6, 18, 35, 18), fill=trim, width=2)
    draw.rectangle((1, 27, 40, 31), fill=wood)
    draw.line((2, 27, 39, 27), fill=trim)
    bottles = (
        (8, 11, (76, 174, 158, 255)),
        (15, 10, (151, 91, 177, 255)),
        (23, 12, (211, 126, 58, 255)),
        (30, 9, (98, 145, 201, 255)),
        (10, 21, (196, 66, 98, 255)),
        (19, 20, (91, 179, 104, 255)),
        (28, 22, (215, 186, 72, 255)),
    )
    for x, y, color in bottles:
        draw.rectangle((x + 1, y - 2, x + 3, y), fill=trim)
        draw.rectangle((x, y, x + 4, y + 5), fill=color)
        draw.point((x + 1, y + 1), fill=(224, 232, 218, 255))
    return image


def _building(grid: list[list[str]], left: int, right: int,
              roof_row: int, door_col: int) -> None:
    for row in range(roof_row, roof_row + 3):
        for col in range(left, right + 1):
            grid[row][col] = "r"
    for col in range(left, right + 1):
        grid[roof_row + 3][col] = "e"
    for row in range(roof_row + 4, roof_row + 8):
        for col in range(left, right + 1):
            grid[row][col] = "t"
    for col in (left + 2, right - 2):
        grid[roof_row + 6][col] = "W"
    grid[roof_row + 7][door_col] = "h"


# ----------------------------------------------------------------------
# Dressing
# ----------------------------------------------------------------------
# The square came out of its first pass correct and empty: two shops, a
# gate, a fountain and a stall, all of them pressed to an edge, and
# forty-two tiles by seven of unbroken paving between them. That is more
# than two screens wide and most of a screen tall, and the docks -- the
# map this is supposed to feel like -- never gives you more than three
# rows of nothing in a row.
#
# So this is a furnishing pass rather than a layout change. Everything
# in it is existing Waterdeep vocabulary: the barrels and crates that
# stand outside every building in the port, the weeds that come up
# between paving stones, and one more stall in the market's own awning
# grammar. Nothing here moves a wall or a route.
#
# The rule the clusters are laid to: no stack wider than three tiles,
# and at least four tiles of open paving between one stack and the next.
# A plaza has to stay a plaza -- what it must not be is a room you can
# cross without noticing anything.

# Barrels: singly or in twos, the way a working square accumulates them.
PLAZA_BARRELS = (
    (17, 4), (31, 4),                       # either side of the gate
    (4, 14), (34, 15),                      # the two shop yards
    (18, 15), (30, 14),
    (14, 18), (34, 18),                     # out beyond the fountain ring
    (17, 21), (31, 21),
    (20, 32), (21, 32), (27, 31),           # along the south
    (44, 24),
)

# Crates: stacked in twos and threes against walls and shop fronts.
PLAZA_CRATES = (
    (6, 4), (7, 4),                         # west of the gate
    (40, 4), (41, 4),                       # east of it
    (5, 14), (5, 15),                       # the smithy's yard
    (42, 14), (43, 14), (43, 15),           # the alchemist's
    (36, 22), (37, 22), (37, 23),           # the east flank
    (8, 31), (9, 31), (9, 32),              # the south wall
    (38, 31), (39, 31), (39, 32),
    (13, 19), (14, 19),
)

# Weeds between the paving stones. Non-solid, so they dress without ever
# narrowing a route -- and each one has a cigarette under it, which is
# the other thing this square was missing: every other map in the city
# has something in it worth scratching at.
PLAZA_WEEDS = (
    (12, 4), (35, 4),
    (14, 15), (36, 15),
    (19, 16), (29, 19),
    (21, 24), (27, 24),
    (33, 25), (15, 25),
    (14, 31), (26, 32), (33, 30), (44, 30),
)

# ...and three lying loose, the way they do everywhere else.
PLAZA_CIGARETTES = ((3, 25), (45, 20), (24, 32))

# One more stall on the west flank. The market's own grammar -- checkered
# canopy, scalloped front, posts, goods in the open -- because the plaza
# is part of the same district and should furnish itself out of the same
# cupboard.
WEST_STALL_ROWS = (22, 23)
WEST_STALL_COLS = (4, 11)
WEST_STALL_GOODS = ((5, "3"), (7, "1"), (9, "5"), (10, "2"))


def _dress(grid: list[list[str]]) -> None:
    """Furnish the square, and never over anything already authored.

    Every target is asserted to be plain paving first. Dressing that can
    silently land on a shop front, a stall post or a transition tile is
    dressing that will one day delete a route, and the failure would be
    a plaza that looks fine and cannot be walked across.
    """
    def place(col: int, row: int, char: str) -> None:
        assert grid[row][col] == ",", (col, row, grid[row][col])
        grid[row][col] = char

    for col, row in PLAZA_BARRELS:
        place(col, row, "O")
    for col, row in PLAZA_CRATES:
        place(col, row, "X")
    for col, row in PLAZA_WEEDS:
        place(col, row, "{")
    for col, row in PLAZA_CIGARETTES:
        place(col, row, "c")

    left, right = WEST_STALL_COLS
    for row in WEST_STALL_ROWS:
        for col in range(left, right + 1):
            place(col, row, "a")
    post_row = WEST_STALL_ROWS[-1] + 1
    place(left, post_row, "P")
    place(right, post_row, "P")
    for col in range(left + 1, right):
        place(col, post_row, "u")
    for col, char in WEST_STALL_GOODS:
        place(col, post_row + 1, char)


def build_map() -> list[str]:
    grid = [["," for _ in range(WIDTH)] for _ in range(HEIGHT)]
    # The north wall is the district wall, and it is as tall as the gate
    # set into it. Two tiles of it -- battlements and one course of brick
    # -- left the gate standing on the paving in front of the wall like a
    # freestanding door frame.
    grid[0] = ["w"] * WIDTH
    for row in range(1, NORTH_WALL_ROWS):
        grid[row] = ["b"] * WIDTH
    grid[-1] = ["b"] * WIDTH
    for row in range(NORTH_WALL_ROWS, HEIGHT - 1):
        grid[row][-1] = "b"

    # There is no west wall. The plaza is the far end of the docks' own
    # eastern street, so its whole west side is the way back, two columns
    # deep so a fast-moving Chuck cannot slip past the edge.
    for row in range(NORTH_WALL_ROWS, HEIGHT - 1):
        grid[row][0] = "⮜"
        grid[row][1] = "⮜"
    grid[20][2] = "ɸ"       # arrival:from_docks
    grid[20][4] = "Ʀ"       # safe direct-load spawn

    _building(grid, 3, 14, 5, 7)
    _building(grid, 33, 44, 5, 40)

    # Guarded gate, set into the bottom course of the wall, smithy yard,
    # alchemist display.
    grid[NORTH_WALL_ROWS - 1][24] = "ϟ"
    grid[14][8] = "⚒"
    grid[15][12] = "⚙"
    grid[14][38] = "⚗"

    # A broad raised fountain plinth makes the large animated bowl's collision
    # agree with its visible footprint.
    for row in range(16, 19):
        for col in range(22, 27):
            grid[row][col] = "⊠"
    grid[18][24] = "₣"

    # A small existing-language market anchors the south side without turning
    # the courtyard into a second, more elaborate docks map.
    for row in (26, 27):
        for col in range(17, 31):
            grid[row][col] = "a"
    grid[28][17] = "P"
    grid[28][30] = "P"
    for col in range(18, 30):
        grid[28][col] = "u"
    for col, char in zip((19, 21, 24, 27, 29), "12534"):
        grid[29][col] = char

    _dress(grid)

    rows = ["".join(row) for row in grid]
    assert len(rows) == HEIGHT and {len(row) for row in rows} == {WIDTH}
    return rows


def _assert_connected(rows: list[str]) -> None:
    # Marker under-terrain and every ordinary non-solid docks tile.
    # Weeds and loose cigarettes are walkable; barrels, crates and stall
    # posts are not, which is the whole reason this check exists.
    walkable = {",", "a", "u", "⮜", "ɸ", "Ʀ", "{", "c"}
    start = (2, 20)
    queue = deque([start])
    seen = {start}
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nxt = (col + dc, row + dr)
            if not (0 <= nxt[0] < WIDTH and 0 <= nxt[1] < HEIGHT):
                continue
            if nxt in seen or rows[nxt[1]][nxt[0]] not in walkable:
                continue
            seen.add(nxt)
            queue.append(nxt)
    required = {(22, 4), (26, 4), (9, 13), (38, 13), (16, 30),
                (21, 20), (28, 20), (24, 31),
                # ...and the corners, because a furnishing pass is
                # exactly the kind of change that walls one off.
                (2, 4), (45, 4), (2, 32), (45, 32),
                (3, 20), (45, 20), (24, 13), (24, 21)}
    assert required <= seen, sorted(required - seen)
    _assert_nowhere_is_empty(rows)


def largest_bare_patch(rows: list[str]) -> tuple[int, int, int, int]:
    """The biggest all-paving rectangle: (area, col, row, w, h) minus area.

    Returned rather than asserted so a test can report where the hole is
    rather than only that there is one.
    """
    height, width = len(rows), len(rows[0])
    best = (0, 0, 0, 0, 0)
    for top in range(height):
        for left in range(width):
            if rows[top][left] != ",":
                continue
            widest = width
            for bottom in range(top, height):
                run = 0
                while left + run < widest and rows[bottom][left + run] == ",":
                    run += 1
                widest = min(widest, run)
                if widest == 0:
                    break
                area = widest * (bottom - top + 1)
                if area > best[0]:
                    best = (area, left, top, widest, bottom - top + 1)
    return best


def _assert_nowhere_is_empty(rows: list[str]) -> None:
    """No stretch of bare paving as big as half a screen.

    The complaint this pass answers, stated as a number rather than as a
    feeling. Before it, the largest all-paving rectangle here was 42x7 --
    over two screens wide and most of one tall. The docks, the map this
    square is meant to feel like, never manages worse than 49 tiles and
    its worst case is one row deep.

    A plaza is allowed to be open; that is what a plaza is. What it is
    not allowed to be is a room you can cross without noticing anything.
    """
    area, col, row, wide, tall = largest_bare_patch(rows)
    assert area < 110, (area, col, row, wide, tall)


def main() -> None:
    SPRITE_OUT.mkdir(parents=True, exist_ok=True)
    for frame in range(4):
        fountain(frame).save(
            SPRITE_OUT / f"waterdeep_fountain_{frame + 1}.png"
        )
    closed_gate().save(SPRITE_OUT / "waterdeep_closed_gate.png")
    forge().save(SPRITE_OUT / "waterdeep_forge.png")
    anvil().save(SPRITE_OUT / "waterdeep_anvil.png")
    alchemist_display().save(
        SPRITE_OUT / "waterdeep_alchemist_display.png"
    )

    rows = build_map()
    _assert_connected(rows)
    header = (
        "; WATERDEEP FOUNTAIN PLAZA — shared opening/finale geometry (48x34)\n"
        "; West returns to the docks. North gate is guarded and closed.\n"
        "; West shop is the smithy; east shop is the alchemist.\n"
    )
    MAP_OUT.write_text(header + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"Wrote {MAP_OUT}")


if __name__ == "__main__":
    main()
