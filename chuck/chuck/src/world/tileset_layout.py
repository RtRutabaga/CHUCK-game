"""Tileset sheet layout — single source of truth.

The generators (tools/generate_*_tileset.py) and the runtime (TileMap)
both import this, so a sheet and its reader can never disagree.

Each area has its own Tileset: a sheet PNG, an ordered list of terrain
rows, and the maps from terrain char -> row name (ground, and the
overhead layer Chuck walks under). A row holds `variants * frames`
16x16 cells, ordered [v0f0, v0f1, v1f0, ...]. Variants break up ground
repetition (picked deterministically per tile position); frames animate
(water shimmer, the sewer's flowing channel).

    docks.png  — the daylit port (planks, quay stone, harbor, tavern...)
    sewer.png  — the tunnel below (brick, stone, dirt, mud, channel)
    tavern.png — warm timber floor and interior walls
    pantry.png — worn storage boards, Astral substitutions, and teal sky

Which map uses which tileset is MAP_TILESET / tileset_for(). No pygame
here: pure data + the index math, unit-testable anywhere.
"""

from __future__ import annotations

from typing import NamedTuple

TILE_PX = 16
ANIM_FPS = 1.25  # animated-frame swaps per second: slow, breathing


class Tileset(NamedTuple):
    """One area's sheet and how its terrain chars map onto it."""

    sheet: str                              # filename in assets/tilesets/
    order: list[tuple[str, int, int]]       # (row name, variants, frames)
    char_to_terrain: dict[str, str]         # ground char -> row name
    overhead_char_to_terrain: dict[str, str]  # char -> row (drawn over Chuck)

    def info(self) -> dict[str, tuple[int, int]]:
        """(variants, frames) per row name."""
        return {name: (v, f) for name, v, f in self.order}

    @property
    def cols(self) -> int:
        """Widest row in cells — the sheet's column count."""
        return max(v * f for _, v, f in self.order)

    @property
    def rows(self) -> int:
        return len(self.order)


# --------------------------------------------------------------------------
# The docks (assets/tilesets/docks.png)
# --------------------------------------------------------------------------
DOCKS = Tileset(
    sheet="docks.png",
    order=[
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
    ],
    char_to_terrain={
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
    },
    overhead_char_to_terrain={
        "a": "awning",
        "g": "gate",
        "u": "awning_edge",   # the canopy's scalloped front
        "P": "awning_edge",   # support posts rise behind the scallops
    },
)

# --------------------------------------------------------------------------
# The sewer (assets/tilesets/sewer.png). Its own art pass: brick tunnel
# walls, a stone entrance landing, packed dirt and wet mud underfoot, and
# a murky drainage channel that flows across three frames.
# --------------------------------------------------------------------------
SEWER = Tileset(
    sheet="sewer.png",
    order=[
        ("sewer_wall", 2, 1),
        ("sewer_stone", 2, 1),
        ("sewer_dirt", 3, 1),
        ("sewer_mud", 2, 1),
        ("sewer_channel", 1, 3),
        ("astral_void", 2, 3),
        ("sewer_outflow", 1, 1),
    ],
    char_to_terrain={
        "#": "sewer_wall",
        ",": "sewer_stone",
        "d": "sewer_dirt",
        "M": "sewer_mud",
        "%": "sewer_channel",
        "V": "astral_void",
    },
    overhead_char_to_terrain={"Q": "sewer_outflow"},
)

TAVERN = Tileset(
    sheet="tavern.png",
    order=[
        ("tavern_floor", 3, 1),
        ("tavern_interior_wall", 2, 1),
        ("tavern_stage_top", 2, 1),
        ("tavern_stage_front", 2, 1),
    ],
    char_to_terrain={
        "=": "tavern_floor",
        "#": "tavern_interior_wall",
        "+": "tavern_stage_top",
        "-": "tavern_stage_front",
    },
    overhead_char_to_terrain={},
)

PANTRY = Tileset(
    sheet="pantry.png",
    order=[
        ("pantry_floor", 3, 1),
        ("pantry_wall", 2, 1),
        ("astral_void", 2, 3),
        ("sky_cloud", 12, 2),
    ],
    char_to_terrain={
        "p": "pantry_floor",
        "#": "pantry_wall",
        "V": "astral_void",
        "s": "sky_cloud",
    },
    overhead_char_to_terrain={},
)

CHULT = Tileset(
    sheet="chult.png",
    order=[
        ("jungle_ground", 4, 1),
        ("dense_jungle", 4, 1),
        ("fallen_log", 4, 1),
        ("thorn_patch", 3, 1),
        ("jungle_stream", 3, 3),
        ("jungle_trail", 3, 1),
        ("jungle_exit", 3, 1),
        ("temple_stone", 4, 1),
        ("temple_stairs", 3, 1),
        ("temple_entrance", 2, 1),
        ("astral_void", 2, 3),
    ],
    char_to_terrain={
        ".": "jungle_ground",
        "#": "dense_jungle",
        "|": "thorn_patch",
        "≈": "jungle_stream",
        "'": "jungle_trail",
        "π": "temple_stone",
        "τ": "temple_stairs",
        "Ω": "temple_entrance",
        "V": "astral_void",
    },
    overhead_char_to_terrain={
        "_": "fallen_log",
        '"': "jungle_exit",
        "ð": "jungle_exit",
    },
)

TEMPLE = Tileset(
    sheet="temple.png",
    order=[
        ("temple_floor", 4, 1),
        ("temple_wall", 4, 1),
        ("temple_doorway", 2, 1),
        ("temple_spikes", 3, 1),
        ("temple_torch", 1, 2),
        ("temple_dart_wall", 2, 1),
        ("astral_void", 2, 3),
        ("temple_brazier", 1, 2),
        ("temple_path", 2, 1),
    ],
    char_to_terrain={
        "·": "temple_floor",
        "█": "temple_wall",
        "Δ": "temple_doorway",
        "∇": "temple_doorway",
        "♠": "temple_spikes",
        "i": "temple_torch",
        "W": "temple_dart_wall",
        "V": "astral_void",
        "ø": "temple_brazier",
        "≡": "temple_path",
    },
    overhead_char_to_terrain={},
)

# --------------------------------------------------------------------------
# The ship (assets/tilesets/ship.png). An internal wooden compartment whose
# hull is set with brass portholes onto the sunlit sea — the animated wave
# crests use the escape cutscene's exact palette so the two match.
# --------------------------------------------------------------------------
SHIP = Tileset(
    sheet="ship.png",
    order=[
        ("ship_floor", 3, 1),
        ("ship_wall", 3, 1),
        ("porthole", 1, 4),   # brass window + sky + sea + rolling waves
        ("ship_door_w_top", 1, 1),
        ("ship_door_w_middle", 1, 1),
        ("ship_door_w_bottom", 1, 1),
        ("ship_door_e_top", 1, 1),
        ("ship_door_e_middle", 1, 1),
        ("ship_door_e_bottom", 1, 1),
        ("ship_door_s_top_left", 1, 1),
        ("ship_door_s_top_middle", 1, 1),
        ("ship_door_s_top_right", 1, 1),
        ("ship_door_s_bottom_left", 1, 1),
        ("ship_door_s_bottom_middle", 1, 1),
        ("ship_door_s_bottom_right", 1, 1),
        ("ship_ladder_top", 1, 1),
        ("ship_ladder_bottom", 1, 1),
        ("ship_ocean", 3, 4),
        ("ship_plank", 2, 1),
        ("ship_rail_h", 1, 1),
        ("ship_rail_v", 1, 1),
        ("ship_rail_nw", 1, 1),
        ("ship_rail_ne", 1, 1),
        ("ship_rail_sw", 1, 1),
        ("ship_rail_se", 1, 1),
    ],
    char_to_terrain={
        "=": "ship_floor",
        "#": "ship_wall",
        "Ø": "porthole",
        "╭": "ship_door_w_top",
        "│": "ship_door_w_middle",
        "╰": "ship_door_w_bottom",
        "╮": "ship_door_e_top",
        "┃": "ship_door_e_middle",
        "╯": "ship_door_e_bottom",
        "┌": "ship_door_s_top_left",
        "┬": "ship_door_s_top_middle",
        "┐": "ship_door_s_top_right",
        "├": "ship_door_s_bottom_left",
        "┼": "ship_door_s_bottom_middle",
        "┤": "ship_door_s_bottom_right",
        "ℓ": "ship_ladder_top",
        "ɭ": "ship_ladder_bottom",
        "~": "ship_ocean",
        "∥": "ship_plank",
        "═": "ship_rail_h",
        "║": "ship_rail_v",
        "╔": "ship_rail_nw",
        "╗": "ship_rail_ne",
        "╚": "ship_rail_sw",
        "╝": "ship_rail_se",
    },
    overhead_char_to_terrain={},
)

# --------------------------------------------------------------------------
# Phlegethos (assets/tilesets/phlegethos.png). The Nine Hells overworld:
# dark cracked basalt, volcanic cliffs, worn stone paths, glowing lava
# fissures, and animated lava (a walkable fall hazard, like the Astral Sea).
# --------------------------------------------------------------------------
PHLEGETHOS = Tileset(
    sheet="phlegethos.png",
    order=[
        ("basalt", 4, 1),
        ("cliff", 3, 1),
        ("path", 2, 1),
        ("lava", 2, 3),     # animated; a lethal fall hazard on foot
        ("fissure", 2, 1),  # basalt split by a glowing lava crack
        ("pass", 1, 1),     # an ash-choked gap onward to the next map
        ("side_pass", 1, 1),  # a human-height cleft through an east wall
        ("astral_void", 2, 3),  # collided reality; exact shared hazard art
        ("fortress", 3, 1),      # the infernal fortress's iron-black wall
        ("fortress_gate", 1, 1),  # its barred gate, shut for now
    ],
    char_to_terrain={
        "·": "basalt",
        "█": "cliff",
        "≡": "path",
        "≋": "lava",
        "♨": "fissure",
        "∇": "pass",
        "Δ": "pass",
        "›": "side_pass",
        "V": "astral_void",
        "▓": "fortress",
        "╬": "fortress_gate",
    },
    overhead_char_to_terrain={},
)

# --------------------------------------------------------------------------
# Feywild (assets/tilesets/feywild.png). The first playable riverbank
# continues the ending cutscene's cool teal water, saturated growth, luminous
# flowers, and enchanted paths without borrowing Chult's tropical palette.
# --------------------------------------------------------------------------
FEYWILD = Tileset(
    sheet="feywild.png",
    order=[
        ("fey_ground", 4, 1),
        ("fey_dense", 4, 1),
        ("fey_river", 3, 3),
        ("fey_bank", 3, 1),
        ("fey_path", 3, 1),
        ("fey_pollen", 3, 3),
        ("fey_opening_w", 3, 1),
        ("fey_opening_e", 3, 1),
        ("fey_opening_n", 3, 1),
        ("fey_opening_s", 3, 1),
        ("fey_root_wall", 4, 1),
        ("fey_root_passage", 3, 1),
        ("fey_tabletop", 4, 1),
        ("fey_table_shadow", 3, 1),
        ("fey_table_apron", 3, 1),
        ("fey_tea_spill", 3, 1),
        ("fey_needle_bed", 4, 1),
        ("fey_channel", 3, 3),
        ("fey_camp_dirt", 4, 1),
        ("fey_mushroom_thicket", 4, 1),
        ("fey_mushroom_passage", 3, 1),
    ],
    char_to_terrain={
        ".": "fey_ground",
        "#": "fey_dense",
        "~": "fey_river",
        ",": "fey_bank",
        "'": "fey_path",
        "☼": "fey_pollen",
        "※": "fey_root_wall",
        "▤": "fey_tabletop",
        "░": "fey_table_shadow",
        "◍": "fey_tea_spill",
        "✿": "fey_needle_bed",
        "≈": "fey_channel",
        "ᛜ": "fey_camp_dirt",
        "ᛘ": "fey_mushroom_thicket",
    },
    overhead_char_to_terrain={
        "←": "fey_opening_w",
        "→": "fey_opening_e",
        "⇧": "fey_opening_n",
        "⇩": "fey_opening_s",
        "≀": "fey_root_passage",
        "ᚿ": "fey_mushroom_passage",
        "⌑": "fey_table_apron",
    },
)

TILESETS: dict[str, Tileset] = {
    "docks": DOCKS,
    "sewer": SEWER,
    "tavern": TAVERN,
    "pantry": PANTRY,
    "chult": CHULT,
    "temple": TEMPLE,
    "ship": SHIP,
    "phlegethos": PHLEGETHOS,
    "feywild": FEYWILD,
}

# Which map draws with which tileset (default: the docks sheet).
MAP_TILESET: dict[str, str] = {
    "waterdeep_docks": "docks",
    "sewer": "sewer",
    "waterdeep_tavern": "tavern",
    "waterdeep_pantry": "pantry",
    "chult_jungle": "chult",
    "chult_cog": "chult",
    "chult_run": "chult",
    "chult_respite": "chult",
    "chult_temple": "chult",
    "temple_entrance": "temple",
    "temple_spikes": "temple",
    "temple_skeletons": "temple",
    "temple_darts": "temple",
    "temple_snakes": "temple",
    "temple_astral_wind": "temple",
    "temple_shrine": "temple",
    "temple_gauntlet": "temple",
    "temple_sanctum": "temple",
    "temple_rubble": "temple",
    "ship_deck": "ship",
    "ship_lower_hold": "ship",
    "ship_galley": "ship",
    "ship_crew_quarters": "ship",
    "ship_captain_cabin": "ship",
    "ship_exterior_deck": "ship",
    "phlegethos_arrival": "phlegethos",
    "phlegethos_road": "phlegethos",
    "phlegethos_lake": "phlegethos",
    "phlegethos_rubble_pass": "phlegethos",
    "phlegethos_fortress_approach": "phlegethos",
    "feywild_riverbank": "feywild",
    "feywild_blooming_path": "feywild",
    "feywild_pollen_orchard": "feywild",
    "feywild_rootways": "feywild",
    "feywild_tea_table": "feywild",
    "feywild_needle_garden": "feywild",
    "feywild_moonmoth_fen": "feywild",
    "feywild_redcap_warrens": "feywild",
    "feywild_shifting_hedge": "feywild",
    "feywild_displacer_meadow": "feywild",
}


def tileset_for(map_name: str) -> Tileset:
    """The Tileset a given map should draw with."""
    return TILESETS[MAP_TILESET.get(map_name, "docks")]


# --------------------------------------------------------------------------
# Back-compat module aliases (the docks generator and older imports still
# read these names; they are simply the docks tileset's fields).
# --------------------------------------------------------------------------
TILESET_ORDER = DOCKS.order
CHAR_TO_TERRAIN = DOCKS.char_to_terrain
OVERHEAD_CHAR_TO_TERRAIN = DOCKS.overhead_char_to_terrain
SHEET_COLS = DOCKS.cols
SHEET_ROWS = DOCKS.rows


def art_index(col: int, row: int, variants: int, frames: int,
              time_s: float) -> int:
    """Column in the terrain's sheet row for this tile right now.

    Variant is a stable per-position hash (the ground never rearranges
    itself); frame advances with time.
    """
    variant = (col * 31 + row * 17) % variants
    frame = int(time_s * ANIM_FPS) % frames
    return variant * frames + frame
