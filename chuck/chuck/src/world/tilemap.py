"""Tile-based maps.

Responsibilities:
    * Load a map from a text file in assets/maps/ (one character per
      tile — see the legends below).
    * Answer collision queries: is_solid(col, row).
    * Expose named spawn points and object spawns for the WorldScene.
    * Draw the ground layer (placeholder colored rects for now).

Text map format:
    * One character per tile; ragged lines are padded solid.
    * Lines starting with ';' are comments and are ignored, so maps
      can document themselves.
    * Unknown characters are a loud error — a typo in a map file
      should never silently become a walkable hole.

Terrain legend:
    '#'  building wall       (solid, flat)
    '~'  water               (solid — Chuck is one foot tall; the
                              harbor might as well be an ocean trench)
    '.'  generic floor       (walkable)
    ','  stone street/quay   (walkable)
    '='  wooden dock planks  (walkable)
    'o'  barrel on planks    (solid standing prop, y-sorted)
    'O'  barrel on stone     (solid standing prop, y-sorted)
    'x'  crate on planks     (solid standing prop, y-sorted)
    'X'  crate on stone      (solid standing prop, y-sorted)
    'B'  Bobert's barrel     (solid standing prop; the sleeping man
                              beside Chuck's spawn — snores if asked)
    'H'  HEROD sign          (solid standing prop, y-sorted)
    'D'  tavern door         (solid prop; big enough for humans)
    'v'  open tavern threshold (walkable exterior state after sewer)
    '>'  tavern interior exit (walkable open threshold)
    'a'  market awning       (walkable; canvas drawn OVER entities)
    't'  tavern facade       (solid tan brick)
    'W'  tavern window       (solid; warm lit panes)
    'r'  tavern roof         (solid slate)
    'e'  tavern eave         (solid; slate meets wood trim and brick)
    'm'  tavern chimney      (solid roof + standing chimney prop)
    'w'  wall battlements    (solid; the district wall's crenel top)
    'b'  wall body           (solid gold-brown brick)
    'F'  wall banner         (solid; gray banner, gold emblem)
    'i'  wall torch          (solid; flickers, 2 frames)
    'g'  gate opening        (walkable; portcullis drawn OVER Chuck)
    'h'  house door          (solid facade + decorative door prop)
    'u'  awning front edge   (walkable; scalloped canvas overhead)
    'P'  stall post          (solid; timber holding the canopy corner)
    '1'-'5' stall goods      (solid props in the open stall front:
                              green/red/orange produce, barrel, table)
    '6'  tavern table        (solid standing prop on planks)
    '7'  tavern chair        (solid standing prop on planks)
    '8'  tavern bar counter  (solid standing prop on planks)
    '9'  tavern hearth       (solid standing prop on planks)
    '+'  tavern stage top    (walkable raised boards)
    '-'  tavern stage front  (solid raised fascia)
    '!'  cheese              (walkable environmental hook on pantry boards)
    '?'  open pantry door    (walkable tavern threshold)
    'p'  pantry floor        (walkable worn boards)
    's'  teal sky/cloud      (walkable successful-fall trigger)
    '^'  pantry return exit  (walkable open threshold)
    'n'  pantry shelf        (solid standing prop on pantry boards)
    'z'  grain sack          (solid standing prop on pantry boards)
    '['  pantry crate        (solid standing prop on pantry boards)
    ']'  pantry barrel       (solid standing prop on pantry boards)
    'S'  sewer grate         (solid prop; asks to be jumped into)
    'R'  ruin wall           (solid; crumbling tan foundation blocks)
    'f'  ruin floor          (solid; the rubble inside the ruin)
    'd'  sewer dirt          (walkable; packed-earth sewer floor)
    'M'  sewer mud           (walkable; wet muck, darker than dirt)
    '%'  drainage channel    (solid; murky sewer water Chuck can't cross)
    'V'  Astral wrong-map    (walkable fall hazard; never a portal)
    '_'  beneath fallen log  (walkable jungle ground, log drawn overhead)
    '|'  thorny undergrowth  (walkable Chult Sanity hazard)
    '≈'  jungle stream      (solid on foot; one tile can be jumped)
    'π'  temple masonry     (solid weathered stepped stone)
    'τ'  temple stair       (walkable broad stone stair)
    'Ω'  temple entrance    (walkable dark phase boundary)
    'ψ'  skull stake        (solid prop over jungle ground)
    '█'  temple wall         (solid interior stone)
    '·'  temple floor        (walkable interior stone)
    'Δ'  temple doorway      (walkable dark threshold)
    '∇'  deeper doorway      (walkable inert phase boundary)
    '♠'  temple spike pit    (solid on foot, jumpable)
    '£'  temple gate         (walkable threshold under the monumental facade)
    'Ϙ'  skull monument      (solid anchor of a 3x2 wall-cell footprint; the
                              48x64 guardian statue rises from its center)
    '€'  carved stone skull  (solid dressing prop over temple wall)
    'ø'  pedestal brazier    (solid; animated ceremonial fire on the floor)
    '†'  serpent idol        (solid dressing prop over temple wall)
    '‡'  glyph stela         (solid dressing prop over temple wall)
    '¦'  cracked urn         (solid dressing prop over temple wall base)
    '¢'  cracked urn         (solid dressing prop on temple floor)
    '¬'  fallen column       (solid dressing prop on temple floor)
    'W'  temple dart aperture (solid wall in temple maps)
    ';'  sailing cog         (solid landmark over dense jungle footprint)
    "'"  beaten jungle trail (walkable route toward the next Chult area)
    '"'  jungle trailhead    (walkable trail, canopy drawn overhead)
    'ð'  Chult area exit     (walkable trail, canopy drawn overhead)
    '/'  dense jungle tree   (solid tall prop over dense vegetation)
    '\\' jungle shrub        (solid broad-leaf prop over dense vegetation)

Marker legend (things ON a tile, not the tile itself — each marker
declares the terrain underneath it, so no seams appear in the ground):
    'C'  Chuck's spawn point   (on planks '=')
    'E'  Chuck's spawn point   (on stone ',' — the sewer entrance landing)
    'c'  cigarette pickup      (on stone ',')
    'j'  cigarette pickup      (on planks '=')
    'K'  patrolling cat        (on stone ',')
    'A'  Astral Anchor         (on stone ',')
    'Y'  Astral Anchor         (on sewer dirt 'd')
    'N'  dock worker NPC       (on stone ',')
    'I'  market woman NPC      (on stone ',')
    'q'  ordinary sewer rat    (on dirt 'd')
    'Z'  sewer exit choice     (on outflow 'Q')
    'J'  Chuck tavern spawn    (on planks '=')
    'T'  tavern return arrival (on stone ',')
    'U'  tavern entry arrival  (on planks '=')
    'k'  tavern bartender NPC  (on planks '=')
    'l'  tavern patron NPC     (on planks '=')
    'y'  tavern musician NPC   (on stage '+')
    ':'  tavern pantry arrival (on planks '=')
    '*'  Chuck pantry spawn    (on pantry floor 'p')
    '0'  pantry entry arrival  (on pantry floor 'p')
    '('  Chult zombie           (on jungle ground '.')
    ')'  Chult skeleton         (on jungle ground '.')
    '$'  Chult deeper boundary  (on jungle trailhead '"')
    '{'  breakable grass        (on stone ',', conceals a cigarette)
    '}'  breakable grass        (on sewer dirt 'd', conceals a cigarette)
    '<'  breakable grass        (on jungle ground '.', conceals a cigarette)
    'α/Α' Map 3 wave 1 zombie/skeleton (under a jungle opening '"')
    'β/Β' Map 3 wave 2 zombie/skeleton (under a jungle opening '"')
    'γ/Γ' Map 3 wave 3 zombie/skeleton (under a jungle opening '"')
    '↓/↑' temple dart launcher (solid wall aperture, fires into corridor)

Design notes:
    * TILE_SIZE (config) is the world grid; entity positions are in
      pixels but level geometry snaps to tiles.
    * Out-of-bounds tiles report solid, so nothing can leave the map.
    * A marker whose under-tile is solid is a loud error (a cigarette
      inside a wall is always a map mistake).
    * pygame is imported only inside draw methods, so parsing and
      collision are unit-testable without pygame installed.
    * TODO: This text format may be replaced by Tiled (.tmx via pytmx)
      when real art arrives; keep is_solid/spawn_points/object_spawns/
      draw_* as the stable interface.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from src.core import config
from src.world.tileset_layout import DOCKS, TILE_PX, art_index


class TileDef(NamedTuple):
    """Static properties of one terrain type.

    Prop tiles (barrels, crates) are solid terrain for collision, but
    are DRAWN as standing objects y-sorted with the characters: the
    ground pass paints their `under` terrain, and the WorldScene draws
    the prop sprite on top in depth order. That's how Chuck walks
    behind things.
    """

    solid: bool
    color: tuple[int, int, int]        # ground color (non-prop tiles)
    prop: str | None = None            # "barrel" | "crate" | None
    under: str | None = None           # terrain drawn beneath prop/overhead
    overhead: str | None = None        # art drawn ABOVE entities (awnings)


class MarkerDef(NamedTuple):
    """A thing placed on the map: spawn point or object."""

    kind: str        # "player" | "cigarette" | (more later: NPCs, anchors)
    under: str       # terrain char drawn/collided beneath the marker
    allow_solid: bool = False  # elevated scenery occupants keep solid footing


TILE_DEFS: dict[str, TileDef] = {
    "#": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER),
    "~": TileDef(solid=True, color=config.COLOR_WATER_PLACEHOLDER),
    ".": TileDef(solid=False, color=config.COLOR_FLOOR_PLACEHOLDER),
    ",": TileDef(solid=False, color=config.COLOR_STONE_PLACEHOLDER),
    "=": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER),
    # Standing props (solid; drawn y-sorted by the WorldScene):
    "o": TileDef(solid=True, color=(0, 0, 0), prop="barrel", under="="),
    "O": TileDef(solid=True, color=(0, 0, 0), prop="barrel", under=","),
    "x": TileDef(solid=True, color=(0, 0, 0), prop="crate", under="="),
    "X": TileDef(solid=True, color=(0, 0, 0), prop="crate", under=","),
    # Bobert's barrel: Chuck's landlord, asleep. Present, never named
    # on screen; interacting yields only a snore. He does not wake.
    "B": TileDef(solid=True, color=(0, 0, 0), prop="bobert_barrel",
                 under="="),
    # HEROD COVER BAND. TONIGHT ONLY. (It is always tonight.)
    "H": TileDef(solid=True, color=(0, 0, 0), prop="herod_sign",
                 under=","),
    # Tavern door: a human-scale double door prop over the wall. It remains
    # solid until the established post-sewer state swaps in the threshold.
    "D": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER,
                 prop="tavern_door", under="#"),
    # Phase 2 return state: the doors are gone and a dark threshold remains.
    # It becomes the walk-over entrance to the Phase 3 tavern interior.
    "v": TileDef(solid=False, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="tavern_open", under=","),
    ">": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="tavern_open", under="="),
    # Market awning: walkable stone with red canvas drawn OVERHEAD —
    # Chuck passes underneath and the canvas covers him.
    "a": TileDef(solid=False, color=config.COLOR_STONE_PLACEHOLDER,
                 under=",", overhead="awning"),
    # The tavern (facade reference: big medieval dockside tavern).
    # All solid; purely a reskin of the building mass.
    "t": TileDef(solid=True, color=config.COLOR_TAVERN_WALL),
    "W": TileDef(solid=True, color=config.COLOR_TAVERN_WALL),  # lit window
    "r": TileDef(solid=True, color=config.COLOR_TAVERN_ROOF),
    "e": TileDef(solid=True, color=config.COLOR_TAVERN_ROOF),  # eave trim
    "m": TileDef(solid=True, color=config.COLOR_TAVERN_ROOF,
                 prop="chimney", under="r"),
    # The district wall (facade reference: crenellated defensive wall).
    # A battlement row over a body row; banners and torches are
    # deliberate tiles, not random variants. All solid.
    "w": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER),
    "b": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER),
    "F": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER),
    "i": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER),
    # Gate opening: walkable street with the portcullis drawn OVERHEAD
    # — Chuck passes beneath the iron teeth, visible between them.
    "g": TileDef(solid=False, color=config.COLOR_STONE_PLACEHOLDER,
                 under=",", overhead="gate"),
    # House door: decorative entrance on district buildings. Solid;
    # these houses are never accessible — style only.
    "h": TileDef(solid=True, color=config.COLOR_TAVERN_WALL,
                 prop="house_door", under="t"),
    # The market stall, cutaway style (reference): the canopy covers
    # only the back rows and ends in a scalloped edge ('u') held by
    # posts; the goods stand in the open in front of it, visible.
    "u": TileDef(solid=False, color=config.COLOR_STONE_PLACEHOLDER,
                 under=",", overhead="awning_edge"),
    "P": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="stall_post", under=",", overhead="awning_edge"),
    "1": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="crate_green", under=","),
    "2": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="crate_red", under=","),
    "3": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="crate_orange", under=","),
    "4": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="barrel", under=","),
    "5": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="stall_table", under=","),
    "6": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="tavern_table", under="="),
    "7": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="tavern_chair", under="="),
    "8": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="bar_counter", under="="),
    "9": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="tavern_hearth", under="="),
    "+": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER),
    "-": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER),
    "!": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="cheese", under="p"),
    "?": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="pantry_open", under="="),
    "p": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER),
    "s": TileDef(solid=False, color=(32, 146, 156)),
    "^": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="pantry_open", under="p"),
    "n": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="pantry_shelf", under="p"),
    "z": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="grain_sack", under="p"),
    "[": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="crate", under="p"),
    "]": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="barrel", under="p"),
    # The sewer grate: iron set in the street near the guard. Solid;
    # Chuck interacts with it (it asks a question — see PROP_CHOICE).
    "S": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="sewer_grate", under=","),
    # The ruined foundation: crumbling block perimeter around a rubble
    # interior. All solid — stylistic only, nothing walks through it.
    "R": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER),
    "f": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER),
    # The sewer (placeholder terrain; a tileset art pass comes later).
    # Dirt and mud are the walkable floor; the drainage channel is solid
    # water — Chuck is one foot tall, so it may as well be a canal.
    "d": TileDef(solid=False, color=config.COLOR_SEWER_DIRT),
    "M": TileDef(solid=False, color=config.COLOR_SEWER_MUD),
    "%": TileDef(solid=True, color=config.COLOR_SEWER_CHANNEL),
    "V": TileDef(solid=False, color=config.COLOR_ASTRAL),
    # Rat-scale drainage gate: dirt beneath, iron bars overhead. Walking
    # through it is resolved by the area's transition configuration.
    "Q": TileDef(solid=False, color=config.COLOR_SEWER_DIRT,
                 under="d", overhead="sewer_outflow"),
    # Chuck-sized jungle passage. The ground remains ordinary jungle floor;
    # a human-scale fallen trunk is drawn above Chuck as he passes beneath it.
    "_": TileDef(solid=False, color=config.COLOR_FLOOR_PLACEHOLDER,
                 under=".", overhead="fallen_log"),
    "|": TileDef(solid=False, color=(48, 84, 39)),
    "≈": TileDef(solid=True, color=(25, 74, 69)),
    "π": TileDef(solid=True, color=(77, 87, 67)),
    "τ": TileDef(solid=False, color=(91, 96, 72)),
    "Ω": TileDef(solid=False, color=(12, 20, 18)),
    "ψ": TileDef(solid=True, color=config.COLOR_FLOOR_PLACEHOLDER,
                 prop="skull_stake", under="."),
    "█": TileDef(solid=True, color=(52, 62, 54)),
    "·": TileDef(solid=False, color=(71, 76, 61)),
    "Δ": TileDef(solid=False, color=(10, 16, 15)),
    "∇": TileDef(solid=False, color=(10, 16, 15)),
    # Human-scale temple arches. The walkable transition terrain remains
    # underneath; the spanning prop supplies a clear architectural silhouette.
    "⌂": TileDef(solid=False, color=(10, 16, 15),
                 prop="temple_arch_ns", under="∇"),
    "⌄": TileDef(solid=False, color=(10, 16, 15),
                 prop="temple_arch_ns", under="Δ"),
    "«": TileDef(solid=False, color=(10, 16, 15),
                 prop="temple_arch_ew", under="∇"),
    "»": TileDef(solid=False, color=(10, 16, 15),
                 prop="temple_arch_ew", under="Δ"),
    "♠": TileDef(solid=True, color=(20, 25, 24)),
    # Temple interior dressing — the temple's style add-ons, matching the
    # docks' stall/walls and the jungle's trees. Wall pieces keep the
    # wall's solidity and draw y-sorted against its face; floor pieces
    # occupy one floor tile each (broad rooms only, never on a route).
    # The entrance hall's monumental deeper-door facade and its flanking
    # carved skulls (reference-directed showcase; session 114). The gate
    # spans the walkable threshold like the arches; skulls dress walls.
    "£": TileDef(solid=False, color=(10, 16, 15),
                 prop="temple_gate", under="∇"),
    "€": TileDef(solid=True, color=(52, 62, 54),
                 prop="temple_skull", under="█"),
    # Guardian monument anchor: bottom-center of a 3x2 block of temple
    # wall cells; the statue sprite spans the block and rises above it.
    "Ϙ": TileDef(solid=True, color=(52, 62, 54),
                 prop="temple_monument", under="█"),
    # Freestanding pedestal brazier: animated tileset terrain (like the
    # wall torch 'i'), solid on the floor it stands on.
    "ø": TileDef(solid=True, color=(48, 59, 51)),
    "†": TileDef(solid=True, color=(52, 62, 54),
                 prop="temple_idol", under="█"),
    "‡": TileDef(solid=True, color=(52, 62, 54),
                 prop="temple_stela", under="█"),
    "¦": TileDef(solid=True, color=(52, 62, 54),
                 prop="temple_urn", under="█"),
    "¢": TileDef(solid=True, color=(71, 76, 61),
                 prop="temple_urn", under="·"),
    "¬": TileDef(solid=True, color=(71, 76, 61),
                 prop="temple_column", under="·"),
    ";": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER,
                 prop="sailing_cog", under="#"),
    "'": TileDef(solid=False, color=(44, 45, 29)),
    '"': TileDef(solid=False, color=(44, 45, 29),
                 under="'", overhead="jungle_exit"),
    "ð": TileDef(solid=False, color=(44, 45, 29),
                 under="'", overhead="jungle_exit"),
    "/": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER,
                 prop="jungle_tree", under="#"),
    "\\": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER,
                  prop="jungle_shrub", under="#"),
}

MARKER_DEFS: dict[str, MarkerDef] = {
    "C": MarkerDef(kind="player", under="="),
    "E": MarkerDef(kind="player", under=","),
    "c": MarkerDef(kind="cigarette", under=","),
    "j": MarkerDef(kind="cigarette", under="="),
    "K": MarkerDef(kind="cat", under=","),
    "A": MarkerDef(kind="anchor:waterdeep_anchor", under=","),
    "Y": MarkerDef(kind="anchor:sewer_anchor", under="d"),
    "N": MarkerDef(kind="npc:dock_worker", under=","),
    "G": MarkerDef(kind="npc:guard", under=","),
    "I": MarkerDef(kind="npc:market_woman", under=","),
    "q": MarkerDef(kind="rat", under="d"),
    "Z": MarkerDef(kind="choice:sewer_exit", under="Q"),
    "L": MarkerDef(kind="arrival:sewer_outflow", under="="),
    "J": MarkerDef(kind="player", under="="),
    "T": MarkerDef(kind="arrival:tavern_return", under=","),
    "U": MarkerDef(kind="arrival:front_entrance", under="="),
    "k": MarkerDef(kind="npc:bartender", under="="),
    "l": MarkerDef(kind="npc:patron", under="="),
    "y": MarkerDef(kind="npc:musician", under="+"),
    ":": MarkerDef(kind="arrival:pantry_return", under="="),
    "*": MarkerDef(kind="player", under="p"),
    "0": MarkerDef(kind="arrival:pantry_entry", under="p"),
    "@": MarkerDef(kind="player", under="."),
    "`": MarkerDef(kind="arrival:from_chult_1", under="."),
    "&": MarkerDef(kind="anchor:chult_anchor", under="."),
    "(": MarkerDef(kind="zombie", under="."),
    ")": MarkerDef(kind="skeleton", under="."),
    "$": MarkerDef(kind="boundary:chult_deeper", under='"'),
    "{": MarkerDef(kind="breakable_grass", under=","),
    "}": MarkerDef(kind="breakable_grass", under="d"),
    "<": MarkerDef(kind="breakable_grass", under="."),
    "¿": MarkerDef(kind="elevated_npc:sailor", under="#", allow_solid=True),
    "¡": MarkerDef(kind="raptor", under="."),
    "§": MarkerDef(kind="anchor:chult_2_anchor", under="."),
    "¶": MarkerDef(kind="massive_dinosaur", under="."),
    "¤": MarkerDef(kind="boundary:chult_run", under='"'),
    "µ": MarkerDef(kind="arrival:from_chult_2", under="."),
    "¥": MarkerDef(kind="anchor:chult_3_anchor", under="."),
    "α": MarkerDef(kind="staged_undead:1:zombie", under='"'),
    "Α": MarkerDef(kind="staged_undead:1:skeleton", under='"'),
    "β": MarkerDef(kind="staged_undead:2:zombie", under='"'),
    "Β": MarkerDef(kind="staged_undead:2:skeleton", under='"'),
    "γ": MarkerDef(kind="staged_undead:3:zombie", under='"'),
    "Γ": MarkerDef(kind="staged_undead:3:skeleton", under='"'),
    "δ": MarkerDef(kind="boundary:chult_respite", under="ð"),
    "ε": MarkerDef(kind="arrival:from_chult_3", under="."),
    "ζ": MarkerDef(kind="anchor:chult_4_anchor", under="."),
    "η": MarkerDef(kind="boundary:chult_temple", under="ð"),
    "θ": MarkerDef(kind="arrival:from_chult_4", under="."),
    "λ": MarkerDef(kind="anchor:chult_5_anchor", under="."),
    "ξ": MarkerDef(kind="boundary:temple_interior", under="Ω"),
    "ν": MarkerDef(kind="arrival:from_temple_interior", under="τ"),
    "κ": MarkerDef(kind="arrival:from_temple_exterior", under="·"),
    "ρ": MarkerDef(kind="anchor:temple_1_anchor", under="·"),
    "σ": MarkerDef(kind="boundary:temple_deeper", under="∇"),
    "υ": MarkerDef(kind="arrival:from_temple_2", under="·"),
    "φ": MarkerDef(kind="arrival:from_temple_1", under="·"),
    "χ": MarkerDef(kind="anchor:temple_2_anchor", under="·"),
    "ω": MarkerDef(kind="boundary:temple_3", under="∇"),
    "Ι": MarkerDef(kind="arrival:from_temple_3", under="·"),
    "Λ": MarkerDef(kind="arrival:from_temple_2", under="·"),
    "Φ": MarkerDef(kind="anchor:temple_3_anchor", under="·"),
    "Ψ": MarkerDef(kind="skeleton", under="·"),
    "Π": MarkerDef(kind="boundary:temple_4", under="∇"),
    "Σ": MarkerDef(kind="arrival:from_temple_4", under="·"),
    "Ρ": MarkerDef(kind="arrival:from_temple_3", under="·"),
    "Τ": MarkerDef(kind="anchor:temple_4_anchor", under="·"),
    "Υ": MarkerDef(kind="boundary:temple_5", under="∇"),
    "Ξ": MarkerDef(kind="arrival:from_temple_5", under="·"),
    "Η": MarkerDef(kind="arrival:from_temple_4", under="·"),
    "Θ": MarkerDef(kind="anchor:temple_5_anchor", under="·"),
    "Ο": MarkerDef(kind="boundary:temple_6", under="∇"),
    "ς": MarkerDef(kind="snake", under="·"),
    "Μ": MarkerDef(kind="arrival:from_temple_6", under="·"),
    "Ζ": MarkerDef(kind="arrival:from_temple_5", under="·"),
    "ϑ": MarkerDef(kind="anchor:temple_6_anchor", under="·"),
    "ϖ": MarkerDef(kind="boundary:temple_7", under="∇"),
    "↓": MarkerDef(kind="dart_trap:down", under="W", allow_solid=True),
    "↑": MarkerDef(kind="dart_trap:up", under="W", allow_solid=True),
}

_COMMENT_PREFIX = ";"
_PAD_CHAR = "#"  # ragged short lines are padded solid


class TileMap:
    """One loaded map: a terrain grid plus collision and spawn data."""

    def __init__(self, map_path: str | Path) -> None:
        """Load and parse the text map at map_path.

        Raises ValueError (with file/row/column) on unknown characters
        or markers placed over solid terrain.
        """
        self.map_path = Path(map_path)
        raw_rows = [
            line.rstrip("\n")
            for line in self.map_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith(_COMMENT_PREFIX)
        ]
        self.height_tiles = len(raw_rows)
        self.width_tiles = max(len(r) for r in raw_rows)
        raw_rows = [r.ljust(self.width_tiles, _PAD_CHAR) for r in raw_rows]

        # Named single spawn points, e.g. {"player": (152.0, 88.0)}.
        self.spawn_points: dict[str, tuple[float, float]] = {}
        # Repeatable object spawns: [("cigarette", (x, y)), ...] where
        # (x, y) is the tile center in world pixels.
        self.object_spawns: list[tuple[str, tuple[float, float]]] = []
        # Standing props: [("barrel", col, row), ...] for y-sorted draw.
        self.prop_tiles: list[tuple[str, int, int]] = []

        # Separate markers from terrain; fail loudly on anything else.
        grid: list[str] = []
        ts = config.TILE_SIZE
        for row_i, row in enumerate(raw_rows):
            terrain_row = []
            for col_i, char in enumerate(row):
                if char in TILE_DEFS:
                    terrain_row.append(char)
                    tile = TILE_DEFS[char]
                    if tile.prop is not None:
                        self.prop_tiles.append((tile.prop, col_i, row_i))
                elif char in MARKER_DEFS:
                    marker = MARKER_DEFS[char]
                    if TILE_DEFS[marker.under].solid and not marker.allow_solid:
                        raise ValueError(
                            f"Marker {char!r} ({marker.kind}) sits on solid "
                            f"terrain {marker.under!r} at row {row_i}, "
                            f"col {col_i} in {self.map_path.name}"
                        )
                    terrain_row.append(marker.under)
                    center = (col_i * ts + ts / 2, row_i * ts + ts / 2)
                    if marker.kind == "player":
                        self.spawn_points["player"] = center
                    else:
                        self.object_spawns.append((marker.kind, center))
                else:
                    raise ValueError(
                        f"Unknown tile character {char!r} at row {row_i}, "
                        f"col {col_i} in {self.map_path.name}"
                    )
            grid.append("".join(terrain_row))
        self._grid = grid
        # char -> list of tile Surfaces (variants*frames), set by
        # load_tileset(). Without it, draw_ground falls back to flat
        # colors (headless tests, missing assets). The active Tileset
        # (which char maps to which sheet row) is chosen per map.
        self._tileset = DOCKS
        self._tileset_info = DOCKS.info()
        self._tile_art: dict[str, list] = {}
        self._overhead_art: dict[str, list] = {}

    def open_tavern_entrance(self) -> None:
        """Swap the authored tavern door to its post-sewer exterior state."""
        door_tiles = [
            (col, row)
            for row, terrain_row in enumerate(self._grid)
            for col, char in enumerate(terrain_row)
            if char == "D"
        ]
        if len(door_tiles) != 1:
            raise ValueError(
                f"Expected one tavern door in {self.map_path.name}, "
                f"found {len(door_tiles)}"
            )
        col, row = door_tiles[0]
        terrain_row = self._grid[row]
        self._grid[row] = terrain_row[:col] + "v" + terrain_row[col + 1:]
        self.prop_tiles = [
            ("tavern_open" if kind == "tavern_door" else kind, pcol, prow)
            for kind, pcol, prow in self.prop_tiles
        ]

    # ------------------------------------------------------------------
    # Collision interface (used by src/world/collision.py)
    # ------------------------------------------------------------------
    def is_solid(self, col: int, row: int) -> bool:
        """True if the tile at (col, row) blocks movement.

        Out-of-bounds tiles are solid so entities can never leave.
        """
        if col < 0 or row < 0 or col >= self.width_tiles or row >= self.height_tiles:
            return True
        return TILE_DEFS[self._grid[row][col]].solid

    def terrain_at(self, col: int, row: int) -> str:
        """The terrain character at (col, row); '#' out of bounds.
        Used for surface-dependent effects (footstep sounds)."""
        if col < 0 or row < 0 or col >= self.width_tiles or row >= self.height_tiles:
            return "#"
        return self._grid[row][col]

    def clear_tile(self, col: int, row: int) -> None:
        """Replace a prop tile with its declared under-terrain.

        Used when a breakable prop (a temple urn) is destroyed at
        runtime: a floor urn's tile opens for walking, a wall-base urn's
        tile stays the wall it always was. Loud error if the tile has no
        under-terrain — clearing a plain tile is always a logic mistake.
        Map reload re-parses the file, so cleared tiles reset naturally.
        """
        char = self._grid[row][col]
        under = TILE_DEFS[char].under
        if under is None:
            raise ValueError(
                f"Tile {char!r} at col {col}, row {row} has no "
                f"under-terrain to clear to in {self.map_path.name}"
            )
        line = self._grid[row]
        self._grid[row] = line[:col] + under + line[col + 1:]

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def load_tileset(self, assets, tileset=DOCKS) -> None:
        """Slice an area's tileset for drawing (called by WorldScene).

        Rows follow the Tileset's `order`; each terrain char maps to its
        row's cells. Pass the tileset the current map should use
        (tileset_layout.tileset_for(map_name)); defaults to the docks.
        """
        self._tileset = tileset
        self._tileset_info = tileset.info()
        rows = assets.tileset(tileset.sheet, TILE_PX)
        by_name = {name: rows[i][: v * f]
                   for i, (name, v, f) in enumerate(tileset.order)}
        self._tile_art = {char: by_name[name]
                          for char, name in tileset.char_to_terrain.items()}
        self._overhead_art = {char: by_name[name]
                              for char, name in
                              tileset.overhead_char_to_terrain.items()}

    def visible_range(self, camera_offset: tuple[int, int],
                      view_w: int, view_h: int
                      ) -> tuple[int, int, int, int]:
        """(col0, col1, row0, row1) of tiles intersecting the view
        (half-open). Pure math — culling is unit-tested headless."""
        ts = config.TILE_SIZE
        ox, oy = camera_offset
        col1 = min(self.width_tiles, (ox + view_w - 1) // ts + 1)
        row1 = min(self.height_tiles, (oy + view_h - 1) // ts + 1)
        col0 = min(max(0, ox // ts), col1)   # never inverted, even if
        row0 = min(max(0, oy // ts), row1)   # the camera is off-map
        return col0, col1, row0, row1

    def draw_ground(self, surface, camera_offset: tuple[int, int],
                    time_s: float = 0.0) -> None:
        """Draw the ground layer: tileset art (flat colors as the
        headless/missing-asset fallback), culled to the view. Prop
        tiles draw their under-terrain; the prop sprite itself is
        y-sorted by the WorldScene. Water shimmers on time_s.
        """
        import pygame  # local: keeps parsing/collision pygame-free

        ts = config.TILE_SIZE
        ox, oy = camera_offset
        view_w, view_h = surface.get_size()
        col0, col1, row0, row1 = self.visible_range(
            camera_offset, view_w, view_h
        )
        char_to_terrain = self._tileset.char_to_terrain
        lookup = self._tileset_info  # (variants, frames) per terrain name
        for row_i in range(row0, row1):
            grid_row = self._grid[row_i]
            for col_i in range(col0, col1):
                char = grid_row[col_i]
                tile = TILE_DEFS[char]
                ground_char = tile.under if tile.under else char
                art = self._tile_art.get(ground_char)
                if art is not None:
                    variants, frames = lookup[char_to_terrain[ground_char]]
                    idx = art_index(col_i, row_i, variants, frames, time_s)
                    surface.blit(art[idx],
                                 (col_i * ts - ox, row_i * ts - oy))
                else:
                    pygame.draw.rect(
                        surface,
                        TILE_DEFS[ground_char].color,
                        pygame.Rect(col_i * ts - ox, row_i * ts - oy,
                                    ts, ts),
                    )

    def draw_overhead(self, surface, camera_offset: tuple[int, int],
                      time_s: float = 0.0) -> None:
        """Draw tiles that appear ABOVE entities (the market awning).

        Important for scale: Chuck walking under things is a core
        visual beat (Game Bible: "Tables feel enormous"). Culled to
        the view like the ground; silently draws nothing if the
        tileset isn't loaded (headless runs).
        """
        if not self._overhead_art:
            return
        ts = config.TILE_SIZE
        ox, oy = camera_offset
        view_w, view_h = surface.get_size()
        col0, col1, row0, row1 = self.visible_range(
            camera_offset, view_w, view_h
        )
        overhead_to_terrain = self._tileset.overhead_char_to_terrain
        for row_i in range(row0, row1):
            grid_row = self._grid[row_i]
            for col_i in range(col0, col1):
                char = grid_row[col_i]
                art = self._overhead_art.get(char)
                if art is not None:
                    name = overhead_to_terrain[char]
                    variants, frames = self._tileset_info[name]
                    idx = art_index(col_i, row_i, variants, frames, time_s)
                    surface.blit(art[idx],
                                 (col_i * ts - ox, row_i * ts - oy))
