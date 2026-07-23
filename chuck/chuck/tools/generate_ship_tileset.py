"""Generate the shared ship interior and exterior tileset.

An internal wooden hull: plank floor, timber wall, north-wall portholes,
human-scale side doors, floor ladders, open-sea waves, and exterior rails. The
porthole's
sky/sea/wave palette is the escape cutscene's exact palette
(escape_cutscene_scene.py), and its four frames roll the wave crests
sideways, so the playable compartment and the cutscene read as the same
place.
"""

import math
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame

from src.world.tileset_layout import SHIP, TILE_PX

# The cutscene palette, shared so the two match exactly.
SKY = (196, 224, 240)
SEA = (96, 164, 214)
SEA_DEEP = (66, 138, 196)
CREST = (214, 236, 250)
WOOD = (120, 84, 52)        # plank floor
WALL = (92, 64, 40)         # hull timber
LINE = (78, 54, 34)
HL_FLOOR = (140, 100, 64)
HL_WALL = (110, 78, 48)
RIM = (150, 120, 66)        # brass
RIM_DARK = (96, 74, 38)
DOOR_HL = (126, 82, 45)
DARK = (24, 20, 19)


def draw_ship_floor(surface, variant: int, _frame: int) -> None:
    surface.fill(WOOD)
    for y in (4, 9, 14):
        pygame.draw.line(surface, LINE, (0, y), (15, y), 1)
        pygame.draw.line(surface, HL_FLOOR, (0, y + 1), (15, y + 1), 1)
    # A staggered plank butt-join so the boards don't line up.
    bx = (variant * 6 + 3) % 14
    pygame.draw.line(surface, LINE, (bx, 0), (bx, 4), 1)
    pygame.draw.line(surface, LINE, ((bx + 8) % 15, 10), ((bx + 8) % 15, 14), 1)
    surface.set_at((2 + variant * 3, 2), HL_FLOOR)


def draw_ship_wall(surface, variant: int, _frame: int) -> None:
    surface.fill(WALL)
    pygame.draw.line(surface, HL_WALL, (0, 0), (15, 0), 1)
    for y in (5, 11):
        pygame.draw.line(surface, LINE, (0, y), (15, y), 1)
    sx = 3 + variant * 5
    pygame.draw.line(surface, LINE, (sx, 0), (sx, 15), 1)
    # A bolt head or two in the timber.
    surface.set_at((sx - 2, 8), RIM_DARK)


def draw_porthole(surface, _variant: int, frame: int) -> None:
    """A brass porthole onto the sea, its wave crests rolled by `frame`."""
    draw_ship_wall(surface, 0, 0)  # timber background around the glass
    cx, cy, r = 8, 8, 6
    # Sky above, sea below, darker toward the bottom of the glass.
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy > r * r:
                continue
            if dy <= -2:
                col = SKY
            elif dy < 3:
                col = SEA
            else:
                col = SEA_DEEP
            surface.set_at((cx + dx, cy + dy), col)
    # Two rolling wave crests; the frame shifts their phase.
    for row, wy0 in enumerate((cy, cy + 3)):
        for dx in range(-r, r + 1):
            wy = wy0 + round(math.sin(dx * 0.9 + frame * 1.57 + row * 1.6) * 0.9)
            if dx * dx + (wy - cy) ** 2 <= r * r and (wy - cy) >= -1:
                surface.set_at((cx + dx, wy), CREST)
    # Brass rim and rivets, proud of the hull.
    pygame.draw.circle(surface, RIM, (cx, cy), r + 1, 2)
    pygame.draw.circle(surface, RIM_DARK, (cx, cy), r + 1, 1)
    for angle in (0, 90, 180, 270):
        rx = cx + round(math.cos(math.radians(angle)) * (r + 1))
        ry = cy + round(math.sin(math.radians(angle)) * (r + 1))
        surface.set_at((rx, ry), RIM_DARK)


def _draw_side_door(surface, side: str, section: str) -> None:
    """One third of a dark, open human-scale side doorway."""
    surface.fill(DARK)
    if side == "west":
        jamb_x = 13
    else:
        jamb_x = 1
    pygame.draw.line(surface, DOOR_HL, (jamb_x, 0), (jamb_x, 15), 2)
    if section == "top":
        pygame.draw.line(surface, DOOR_HL, (0, 2), (15, 2), 2)
    elif section == "middle":
        # A single highlight on the jamb keeps the opening readable against
        # the black future-map boundary without implying a door panel.
        surface.set_at((jamb_x, 8), RIM)
    else:
        pygame.draw.line(surface, DOOR_HL, (0, 13), (15, 13), 2)


def draw_ship_door_w_top(surface, _variant: int, _frame: int) -> None:
    _draw_side_door(surface, "west", "top")


def draw_ship_door_w_middle(surface, _variant: int, _frame: int) -> None:
    _draw_side_door(surface, "west", "middle")


def draw_ship_door_w_bottom(surface, _variant: int, _frame: int) -> None:
    _draw_side_door(surface, "west", "bottom")


def draw_ship_door_e_top(surface, _variant: int, _frame: int) -> None:
    _draw_side_door(surface, "east", "top")


def draw_ship_door_e_middle(surface, _variant: int, _frame: int) -> None:
    _draw_side_door(surface, "east", "middle")


def draw_ship_door_e_bottom(surface, _variant: int, _frame: int) -> None:
    _draw_side_door(surface, "east", "bottom")


def _draw_south_door(surface, column: str, row: str) -> None:
    """One cell of the 3x2 dark opening in the compartment's south wall."""
    surface.fill(DARK)
    if row == "top":
        pygame.draw.line(surface, DOOR_HL, (0, 1), (15, 1), 2)
    else:
        pygame.draw.line(surface, DOOR_HL, (0, 14), (15, 14), 2)
    if column == "left":
        pygame.draw.line(surface, DOOR_HL, (1, 0), (1, 15), 2)
    elif column == "right":
        pygame.draw.line(surface, DOOR_HL, (14, 0), (14, 15), 2)


def draw_ship_door_s_top_left(surface, _variant: int, _frame: int) -> None:
    _draw_south_door(surface, "left", "top")


def draw_ship_door_s_top_middle(surface, _variant: int, _frame: int) -> None:
    _draw_south_door(surface, "middle", "top")


def draw_ship_door_s_top_right(surface, _variant: int, _frame: int) -> None:
    _draw_south_door(surface, "right", "top")


def draw_ship_door_s_bottom_left(surface, _variant: int, _frame: int) -> None:
    _draw_south_door(surface, "left", "bottom")


def draw_ship_door_s_bottom_middle(surface, _variant: int, _frame: int) -> None:
    _draw_south_door(surface, "middle", "bottom")


def draw_ship_door_s_bottom_right(surface, _variant: int, _frame: int) -> None:
    _draw_south_door(surface, "right", "bottom")


def draw_ship_ladder(surface, _variant: int, _frame: int) -> None:
    """A dark deck hatch with brass-edged wooden ladder rungs."""
    draw_ship_floor(surface, 1, 0)
    pygame.draw.rect(surface, DARK, pygame.Rect(2, 1, 12, 14))
    pygame.draw.line(surface, RIM_DARK, (3, 1), (3, 14), 2)
    pygame.draw.line(surface, RIM_DARK, (12, 1), (12, 14), 2)
    for y in (3, 7, 11):
        pygame.draw.line(surface, RIM, (4, y), (11, y), 2)


def draw_ship_ocean(surface, variant: int, frame: int) -> None:
    """Bright open water with rolling line crests, never particle dots."""
    surface.fill(SEA_DEEP)
    phase = frame * 1.35 + variant * 0.8
    for x in range(16):
        upper = 3 + round(math.sin(x * 0.55 + phase) * 1.2)
        lower = 11 + round(math.sin(x * 0.48 + phase + 2.1) * 1.1)
        surface.set_at((x, upper), SEA)
        surface.set_at((x, lower), CREST)
        if upper + 1 < 16:
            surface.set_at((x, upper + 1), SEA)


def draw_ship_plank(surface, variant: int, _frame: int) -> None:
    """One narrow north-south board, transparent over the animated sea."""
    pygame.draw.rect(surface, DARK, pygame.Rect(2, 0, 12, 16))
    pygame.draw.rect(surface, WOOD, pygame.Rect(3, 0, 10, 16))
    pygame.draw.line(surface, HL_FLOOR, (4, 0), (4, 15), 1)
    pygame.draw.line(surface, LINE, (11, 0), (11, 15), 1)
    brace_y = 4 + variant * 7
    pygame.draw.line(surface, LINE, (3, brace_y), (12, brace_y), 2)
    surface.set_at((9 - variant * 3, 8 + variant * 4), HL_FLOOR)


def _rail_base(surface) -> None:
    draw_ship_floor(surface, 0, 0)


def draw_ship_rail_h(surface, _variant: int, _frame: int) -> None:
    _rail_base(surface)
    pygame.draw.rect(surface, DARK, pygame.Rect(0, 5, 16, 6))
    pygame.draw.line(surface, HL_FLOOR, (0, 5), (15, 5), 1)
    pygame.draw.line(surface, WALL, (0, 10), (15, 10), 2)
    for x in (1, 8, 14):
        pygame.draw.rect(surface, WALL, pygame.Rect(x, 1, 2, 14))


def draw_ship_rail_v(surface, _variant: int, _frame: int) -> None:
    _rail_base(surface)
    pygame.draw.rect(surface, DARK, pygame.Rect(5, 0, 6, 16))
    pygame.draw.line(surface, HL_FLOOR, (5, 0), (5, 15), 1)
    pygame.draw.line(surface, WALL, (10, 0), (10, 15), 2)
    for y in (1, 8, 14):
        pygame.draw.rect(surface, WALL, pygame.Rect(1, y, 14, 2))


def _draw_ship_rail_corner(surface, left: bool, top: bool) -> None:
    _rail_base(surface)
    hx0, hx1 = (5, 15) if left else (0, 10)
    vy0, vy1 = (5, 15) if top else (0, 10)
    pygame.draw.line(surface, DARK, (hx0, 8), (hx1, 8), 5)
    pygame.draw.line(surface, DARK, (8, vy0), (8, vy1), 5)
    pygame.draw.circle(surface, WALL, (8, 8), 4)
    surface.set_at((8, 8), HL_FLOOR)


def draw_ship_rail_nw(surface, _variant: int, _frame: int) -> None:
    _draw_ship_rail_corner(surface, True, True)


def draw_ship_rail_ne(surface, _variant: int, _frame: int) -> None:
    _draw_ship_rail_corner(surface, False, True)


def draw_ship_rail_sw(surface, _variant: int, _frame: int) -> None:
    _draw_ship_rail_corner(surface, True, False)


def draw_ship_rail_se(surface, _variant: int, _frame: int) -> None:
    _draw_ship_rail_corner(surface, False, False)


DRAW = {
    "ship_floor": draw_ship_floor,
    "ship_wall": draw_ship_wall,
    "porthole": draw_porthole,
    "ship_door_w_top": draw_ship_door_w_top,
    "ship_door_w_middle": draw_ship_door_w_middle,
    "ship_door_w_bottom": draw_ship_door_w_bottom,
    "ship_door_e_top": draw_ship_door_e_top,
    "ship_door_e_middle": draw_ship_door_e_middle,
    "ship_door_e_bottom": draw_ship_door_e_bottom,
    "ship_door_s_top_left": draw_ship_door_s_top_left,
    "ship_door_s_top_middle": draw_ship_door_s_top_middle,
    "ship_door_s_top_right": draw_ship_door_s_top_right,
    "ship_door_s_bottom_left": draw_ship_door_s_bottom_left,
    "ship_door_s_bottom_middle": draw_ship_door_s_bottom_middle,
    "ship_door_s_bottom_right": draw_ship_door_s_bottom_right,
    "ship_ladder": draw_ship_ladder,
    "ship_ocean": draw_ship_ocean,
    "ship_plank": draw_ship_plank,
    "ship_rail_h": draw_ship_rail_h,
    "ship_rail_v": draw_ship_rail_v,
    "ship_rail_nw": draw_ship_rail_nw,
    "ship_rail_ne": draw_ship_rail_ne,
    "ship_rail_sw": draw_ship_rail_sw,
    "ship_rail_se": draw_ship_rail_se,
}


def main() -> None:
    pygame.init()
    sheet = pygame.Surface((SHIP.cols * TILE_PX, SHIP.rows * TILE_PX),
                           pygame.SRCALPHA)
    for row_i, (name, variants, frames) in enumerate(SHIP.order):
        for variant in range(variants):
            for frame in range(frames):
                cell = pygame.Surface((TILE_PX, TILE_PX), pygame.SRCALPHA)
                DRAW[name](cell, variant, frame)
                sheet.blit(cell, ((variant * frames + frame) * TILE_PX,
                                  row_i * TILE_PX))
    out = ROOT / "assets" / "tilesets" / SHIP.sheet
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
