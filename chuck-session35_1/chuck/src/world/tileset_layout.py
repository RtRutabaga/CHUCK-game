"""Tileset sheet layout — single source of truth.

The generator (tools/generate_tileset.py) and the runtime (TileMap)
both import this, so the sheet and its reader can never disagree.

Sheet: assets/tilesets/docks.png. One row per terrain; each row holds
`variants * frames` 16x16 cells, ordered [v0f0, v0f1, v1f0, ...].
Variants break up ground repetition (picked deterministically per tile
position); frames animate (currently only water shimmers).

No pygame; pure data + the index math, unit-testable anywhere.
"""

from __future__ import annotations

TILE_PX = 16

# (terrain_name, variants, frames) — row order in the sheet.
TILESET_ORDER: list[tuple[str, int, int]] = [
    ("planks", 2, 1),
    ("stone", 3, 1),
    ("water", 2, 2),
    ("floor", 1, 1),
    ("wall", 1, 1),
    ("awning", 2, 1),
    ("tavern_wall", 2, 1),
    ("tavern_window", 1, 1),
    ("tavern_roof", 2, 1),
    ("tavern_eave", 1, 1),
    ("castle_top", 2, 1),
    ("castle_wall", 2, 1),
    ("castle_banner", 1, 1),
    ("castle_torch", 1, 2),
    ("gate", 1, 1),
    ("awning_edge", 1, 1),
    ("ruin_wall", 2, 1),
    ("ruin_floor", 2, 1),
]

# Terrain char (from tilemap TILE_DEFS) -> sheet terrain name.
CHAR_TO_TERRAIN: dict[str, str] = {
    "=": "planks",
    ",": "stone",
    "~": "water",
    ".": "floor",
    "#": "wall",
    "t": "tavern_wall",
    "W": "tavern_window",
    "r": "tavern_roof",
    "e": "tavern_eave",
    "w": "castle_top",
    "b": "castle_wall",
    "F": "castle_banner",
    "i": "castle_torch",
    "R": "ruin_wall",
    "f": "ruin_floor",
}

# Overhead terrains draw ABOVE entities (Chuck walks underneath).
OVERHEAD_CHAR_TO_TERRAIN: dict[str, str] = {
    "a": "awning",
    "g": "gate",
    "u": "awning_edge",       # the canopy's scalloped front
    "P": "awning_edge",       # support posts rise behind the scallops
}

SHEET_COLS = max(v * f for _, v, f in TILESET_ORDER)
SHEET_ROWS = len(TILESET_ORDER)

ANIM_FPS = 1.25  # water frame swaps per second: slow harbor breathing


def art_index(col: int, row: int, variants: int, frames: int,
              time_s: float) -> int:
    """Column in the terrain's sheet row for this tile right now.

    Variant is a stable per-position hash (the ground never rearranges
    itself); frame advances with time.
    """
    variant = (col * 31 + row * 17) % variants
    frame = int(time_s * ANIM_FPS) % frames
    return variant * frames + frame
