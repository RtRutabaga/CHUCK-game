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


def build_map() -> list[str]:
    grid = [["," for _ in range(WIDTH)] for _ in range(HEIGHT)]
    grid[0] = ["w"] * WIDTH
    grid[1] = ["b"] * WIDTH
    grid[-1] = ["b"] * WIDTH
    for row in range(2, HEIGHT - 1):
        grid[row][0] = "b"
        grid[row][-1] = "b"

    # The west street is the same broad opening visible southeast of the
    # tavern. Two transition columns prevent a fast-moving Chuck slipping by.
    for row in range(19, 22):
        grid[row][0] = "⮜"
        grid[row][1] = "⮜"
    grid[20][2] = "ɸ"       # arrival:from_docks
    grid[20][4] = "Ʀ"       # safe direct-load spawn

    _building(grid, 3, 14, 5, 7)
    _building(grid, 33, 44, 5, 40)

    # Guarded gate, smithy yard, alchemist display.
    grid[3][24] = "ϟ"
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

    rows = ["".join(row) for row in grid]
    assert len(rows) == HEIGHT and {len(row) for row in rows} == {WIDTH}
    return rows


def _assert_connected(rows: list[str]) -> None:
    # Marker under-terrain and every ordinary non-solid docks tile.
    walkable = {",", "a", "u", "⮜", "ɸ", "Ʀ"}
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
                (21, 20), (28, 20), (24, 31)}
    assert required <= seen, sorted(required - seen)


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
