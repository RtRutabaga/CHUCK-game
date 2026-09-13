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
    '♠'  temple spike pit    (walkable fall hazard on foot, like Astral;
                              cleared safely only by the committed jump)
    '£'  temple gate         (walkable threshold under the monumental facade)
    'Ϙ'  skull monument      (solid anchor of a 3x2 wall-cell footprint; the
                              48x64 guardian statue rises from its center)
    'Ϟ'  serpent monument    (same footprint/anchor rule; a coiled serpent
                              in the ziggurat niche instead of the skull)
    '€'  carved stone skull  (solid dressing prop over temple wall)
    'ø'  pedestal brazier    (solid; animated ceremonial fire on the floor)
    '≡'  processional path   (walkable paved slabs down the entrance aisle)
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
    # Painted lane markings: road, walkable, just with a line on it.
    "≡": TileDef(solid=False, color=(96, 100, 104)),
    "‖": TileDef(solid=False, color=(96, 100, 104)),
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
    # Phase 14 fountain-plaza scenery. Each anchor carries collision while its
    # larger sprite supplies the human-scale silhouette above the paving.
    "₣": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="waterdeep_fountain", under=","),
    # Invisible footprint tiles keep the fountain's broad bowl solid while
    # drawing the same paving as the rest of the square beneath it.
    "⊠": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER, under=","),
    # The plaza's gate towers and banners, on the paving in front of the
    # district wall and drawn up over it.
    "ꝟ": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="waterdeep_gate_tower", under=","),
    "ꝡ": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="waterdeep_banner", under=","),
    # The tavern's keg rack and notice board against its north wall, and
    # the rug under the middle table; the pantry's sacks and baskets.
    "ꝣ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="tavern_keg_rack", under="="),
    "ꝥ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="tavern_notice_board", under="="),
    "ꝧ": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="tavern_rug", under="="),
    "ꝩ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="pantry_sack_pile", under="p"),
    "ꝫ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="pantry_produce_basket", under="p"),
    "ϟ": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="waterdeep_closed_gate", under=","),
    "⚒": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="waterdeep_forge", under=","),
    "⚙": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="waterdeep_anvil", under=","),
    "⚗": TileDef(solid=True, color=config.COLOR_STONE_PLACEHOLDER,
                 prop="waterdeep_alchemist_display", under=","),
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
    # ------------------------------------------------------------------
    # Phase 13's Chult desert. Sand and ripple reuse "." and ",", and the
    # canyon walls reuse "#", because those already mean walkable ground
    # and solid wall everywhere else; only the terrain the desert alone
    # has needs a character of its own.
    # ------------------------------------------------------------------
    "⟁": TileDef(solid=False, color=(176, 138, 90)),
    # Cut stone: standing ruin is solid, the floor around it is not.
    "⌗": TileDef(solid=True, color=(162, 146, 124)),
    "⌖": TileDef(solid=False, color=(162, 146, 124)),
    # Chest-high on a one-foot rat, so a bush is a wall.
    "⍟": TileDef(solid=True, color=(128, 128, 84)),
    # Burnt ground. This was the whole fire: one solid tile with a ring
    # of stones drawn inside it, which at sixteen pixels made the stones
    # three pixels each. The ring is a prop now and this is what is left
    # underneath it -- scorched sand, walkable, spread over a patch, so
    # the fire has a footprint instead of a footprint's worth of tile.
    "⚱": TileDef(solid=False, color=(120, 100, 78)),
    # The ruins' chest: the sea captain's own, standing on buried
    # flagstones instead of on ship planking.
    "⎈": TileDef(solid=True, color=(0, 0, 0), prop="desert_ruin_chest",
                 under="⌖"),
    "⩊": TileDef(solid=False, color=(96, 130, 70)),
    # Palm shade: drawn over Chuck, so it is walkable oasis turf
    # underneath. `under` is the ground the tile paints, `overhead` the
    # art that goes on top of him -- authored with neither, the tile was
    # walkable and blank and no palm ever appeared.
    "⏦": TileDef(solid=False, color=(96, 130, 70), under="⩊",
                 overhead="palm_canopy"),
    # ...and the same shade lying on sand rather than on turf. The
    # oasis's green is a narrow ring around the water and the palms
    # stand outside it, so without this the canopy could only ever be
    # drawn over the pool itself -- which is the one place a tree
    # cannot grow.
    "⍚": TileDef(solid=False, color=(214, 178, 122), under=".",
                 overhead="palm_canopy"),
    # Fragments of Chult, east of the hub. Its own tileset spells these
    # "." and "#"; the desert already owns both, so the collided maps
    # give the same art new characters.
    "ᛗ": TileDef(solid=False, color=(37, 44, 28)),
    "ᚷ": TileDef(solid=True, color=(17, 54, 34)),
    "ᚺ": TileDef(solid=True, color=(23, 68, 67)),
    # Fragments of the Feywild. Its ground and growth need characters
    # here for the same reason Chult's did; the rest of what it brought
    # already had its own and keeps them.
    "ᛟ": TileDef(solid=False, color=(46, 74, 60)),
    "ᛇ": TileDef(solid=True, color=(28, 54, 46)),
    # A piece of the ship's deck, and a piece of a castle nobody has
    # been to. The courtyard walks like flagstone; the wall is a wall.
    "⌼": TileDef(solid=False, color=(96, 72, 46)),
    "⌽": TileDef(solid=False, color=(128, 126, 122)),
    # The castle, finished. Crenellation and drum towers are the same
    # wall they replace -- solid, on the same tiles -- so a section
    # built out of them can never be the reason a route closed.
    "ᛦ": TileDef(solid=True, color=(92, 92, 96)),
    "ᛧ": TileDef(solid=True, color=(92, 92, 96)),
    # ...and its banners, which stand on the ground in front of a wall
    # rather than on the wall itself. Props anchor to the bottom of
    # their tile and draw upward, so a banner authored on the stone
    # would rise off the battlements like a flag; authored one tile out
    # it hangs down the face instead, which is what a banner does.
    #
    # Two characters for one object because the ground differs: inside
    # the courtyard it hangs over flagstones and outside the wall it
    # hangs over sand. That is the same reason the docks has both 'o'
    # and 'O' for one barrel.
    # A banner, hanging on the wall it belongs to. It is solid because
    # the wall under it is: the cloth is two tiles of sprite drawn
    # upward, and hung on the open ground in front of a one-tile curtain
    # two thirds of it came down past the bottom of the wall and lay on
    # the courtyard floor. The placement pass widens the wall by a tile
    # under every banner so there is stone for it to hang on.
    "ᛮ": TileDef(solid=True, color=(146, 34, 46),
                 prop="castle_banner", under="⌾"),
    # The corner turret: three tiles of stone with a roof on it. The
    # prop stands on the middle of the block's bottom row and draws up
    # across the whole of it, so the corner is the tallest thing on the
    # map, which is the only reason a corner tower exists.
    "ᛪ": TileDef(solid=True, color=(92, 92, 96),
                 prop="castle_turret", under="ᛧ"),
    "⌾": TileDef(solid=True, color=(92, 92, 96)),
    # A frozen world, also unvisited. Snow and drift are both snowy
    # ground as far as the weather is concerned -- SnowFall masks to
    # both -- but a drift is piled high enough to stop a one-foot rat.
    "❄": TileDef(solid=False, color=(202, 214, 232)),
    "❅": TileDef(solid=True, color=(186, 202, 224)),
    "❆": TileDef(solid=False, color=(168, 202, 222)),
    # The orc camp's stores. Deliberately the pantry's own grain-sack
    # prop rather than a desert-styled one: the phase document asks for
    # the same asset and the same behaviour, and a player who scratched
    # one open in Waterdeep should recognise these on sight. Only the
    # ground it stands on differs, which is all `under` is for.
    "⛰": TileDef(solid=True, color=(0, 0, 0), prop="grain_sack", under="."),
    # ------------------------------------------------------------------
    # The region's standing props: the layer the tileset cannot carry.
    #
    # A ruin reads as a ruin because of what has fallen off it, and none
    # of that fits in sixteen pixels -- a column is three tiles tall, a
    # fallen one is two tiles long, and neither repeats. So they are
    # props: drawn taller than their tile, y-sorted with Chuck, solid
    # underfoot. Each has a version standing on buried flagstones and a
    # version standing on open sand, because half of what makes a ruin
    # look ruined is the pieces that ended up outside it.
    # ------------------------------------------------------------------
    "⍏": TileDef(solid=True, color=(0, 0, 0), prop="desert_column",
                 under="⌖"),
    "⍐": TileDef(solid=True, color=(0, 0, 0), prop="desert_column",
                 under="."),
    # The great pillars. Solid on their own single tile, like the
    # small columns, and the stone overhangs it by six pixels a side
    # the way the eastern castle's banners overhang theirs.
    "⍕": TileDef(solid=True, color=(0, 0, 0), prop="desert_great_pillar",
                 under="⌖"),
    "⍙": TileDef(solid=True, color=(0, 0, 0), prop="desert_great_pillar",
                 under="."),
    # The gate arch. Not solid: this is the tile Chuck walks through,
    # and the sprite is anchored on it so it sorts against him -- behind
    # him on the way up to it, in front of him once he is through. Its
    # two piers are separate tiles of standing wall either side.
    # The hub's ribcage: seven solid tiles along its spine, the middle one
    # carrying the sprite. The orc camp's tents stand on three solid
    # tiles the same way; racks and the drum on one.
    "ꞿ": TileDef(solid=True, color=(212, 198, 164),
                 prop="desert_ribcage", under="."),
    "ꟁ": TileDef(solid=True, color=(212, 198, 164), under="."),
    "ꟃ": TileDef(solid=True, color=(136, 96, 60), prop="orc_tent", under="."),
    "ꟈ": TileDef(solid=True, color=(136, 96, 60), under="."),
    "ꟊ": TileDef(solid=True, color=(78, 56, 36),
                 prop="orc_weapon_rack", under="."),
    "ꟑ": TileDef(solid=True, color=(136, 96, 60),
                 prop="orc_war_drum", under="."),
    "⍛": TileDef(solid=False, color=(162, 146, 124), prop="desert_ruin_arch",
                 under="⌖"),
    "⍖": TileDef(solid=True, color=(0, 0, 0), prop="desert_column_fallen",
                 under="⌖"),
    "⍗": TileDef(solid=True, color=(0, 0, 0), prop="desert_column_fallen",
                 under="."),
    "⍓": TileDef(solid=True, color=(0, 0, 0), prop="desert_rubble",
                 under="⌖"),
    "⍔": TileDef(solid=True, color=(0, 0, 0), prop="desert_rubble",
                 under="."),
    # The oasis's palms, at last with trunks. The canopy tile above is
    # still the shade Chuck walks under; this is the tree holding it up.
    "⍑": TileDef(solid=True, color=(0, 0, 0), prop="desert_palm",
                 under="⩊"),
    "⍒": TileDef(solid=True, color=(0, 0, 0), prop="desert_palm",
                 under="."),
    # The camp's fires, at the size a camp is built around: a pit prop
    # standing in the middle of its own patch of scorched ground. The
    # one-tile ring it replaces was smaller than the rat looking at it.
    "⍘": TileDef(solid=True, color=(0, 0, 0), prop="desert_fire_pit",
                 under="⚱"),
    # ------------------------------------------------------------------
    # Dressing for the fragments east of the hub.
    #
    # Every one of these is a prop the world it came from already owns,
    # given a character here because the collided maps had to rename the
    # *ground* it stands on: Chult spells its jungle "." and "#" at home
    # and the desert had already claimed both, so the fragment kept its
    # art and took new letters. `under` is the whole difference -- the
    # tree is the same tree, standing on the same jungle, spelled
    # differently.
    #
    # Without them a fragment is a rectangle of somebody else's ground
    # colour. What makes a piece of Chult read as Chult is the trees on
    # it, and none of that can live in a tile.
    # ------------------------------------------------------------------
    "⍮": TileDef(solid=True, color=(17, 54, 34), prop="jungle_tree",
                 under="ᚷ"),
    "⍯": TileDef(solid=True, color=(37, 44, 28), prop="jungle_shrub",
                 under="ᛗ"),
    "⍰": TileDef(solid=True, color=(28, 54, 46),
                 prop="feywild_grove_tree", under="ᛇ"),
    "⍱": TileDef(solid=True, color=(46, 74, 60), prop="feywild_shrub",
                 under="ᛟ"),
    "⍲": TileDef(solid=True, color=(46, 74, 60), prop="feywild_mushroom",
                 under="ᛟ"),
    # ...and the ship's stores, on the ship's own deck. The deck is the
    # one fragment that is furniture rather than landscape: bare, a
    # length of planking is a floor with nothing to say it was ever at
    # sea, and it is the largest single cell on the seventh map.
    "⍶": TileDef(solid=True, color=(96, 72, 46), prop="barrel",
                 under="⌼"),
    "⍷": TileDef(solid=True, color=(96, 72, 46), prop="crate",
                 under="⌼"),
    # Modern-city office masses. These are all solid building footprint,
    # separated into roof/cornice/facade materials only for three-quarter-view
    # rendering; none are short freestanding walls or playable platforms.
    # The roof volume: its parapet wall, and the plant standing on it.
    "▘": TileDef(solid=True, color=(74, 77, 85)),
    "▖": TileDef(solid=True, color=(74, 77, 85)),
    "▗": TileDef(solid=True, color=(74, 77, 85)),
    "▙": TileDef(solid=True, color=(62, 65, 72)),
    "▟": TileDef(solid=True, color=(58, 74, 84)),
    "▱": TileDef(solid=True, color=(55, 58, 67)),
    "▤": TileDef(solid=True, color=(49, 52, 61)),
    "▥": TileDef(solid=True, color=(39, 42, 51)),
    "▦": TileDef(solid=False, color=(45, 49, 56)),
    "⮝": TileDef(solid=False, color=(43, 47, 55)),
    "⮟": TileDef(solid=False, color=(43, 47, 55)),
    "⮞": TileDef(solid=False, color=(43, 47, 55)),
    "⮜": TileDef(solid=False, color=(43, 47, 55)),
    # Phase 11's streets, furnished. All three are solid: they are things
    # standing on the pavement, and the placement pass that puts them
    # there proves the walk stays open around every one of them.
    #
    # The lamp is the only one the time of day changes. Its sheet has an
    # unlit head and a lit one, and the light it *casts* is a pool on the
    # ground that only the night maps get -- see StreetLightField.
    "Ⱡ": TileDef(solid=True, color=(74, 82, 92),
                 prop="city_streetlight", under="."),
    "Ⱨ": TileDef(solid=True, color=(168, 44, 40),
                 prop="city_fire_hydrant", under="."),
    "ⱦ": TileDef(solid=True, color=(172, 38, 40),
                 prop="city_stop_sign", under="."),
    "Ƀ": TileDef(solid=False, color=(43, 47, 55),
                 prop="city_bottles", under="."),
    # An open manhole in the sidewalk, its cover levered off beside it.
    "ƺ": TileDef(solid=True, color=(24, 26, 30),
                 prop="city_sewer_entrance", under="."),
    "ƻ": TileDef(solid=False, color=(181, 142, 48)),
    # Toxic runoff: walkable, unmistakably not water, and the only sewer
    # terrain that both slows Chuck and takes Sanity.
    "ʓ": TileDef(solid=False, color=(126, 196, 44)),
    # Standing rainwater on a daytime sidewalk. Purely cosmetic: it is
    # ordinary pavement underfoot, not sludge and not a hazard.
    "ꞏ": TileDef(solid=False, color=(138, 152, 164)),
    # City Day 6: another world showing through the street. Chult ground
    # is walkable, its dense growth is not, and one solid anchor tile carries
    # the large animated planar-portal prop.
    "ᵹ": TileDef(solid=False, color=(56, 92, 58)),
    "ᵺ": TileDef(solid=True, color=(26, 60, 40)),
    "Ȣ": TileDef(solid=True, color=(98, 96, 108),
                 prop="city_planar_portal", under="."),
    # The maintenance ladder out of the sewer: one human-scale 16x32
    # structure in two cells, the same shape as the ship's ladder.
    "Ɫ": TileDef(solid=False, color=(88, 96, 104)),
    "ɬ": TileDef(solid=False, color=(72, 80, 88)),
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
    # Rubble Pass's east-facing infernal cleft: unlike the temple arches this
    # is terrain art, allowing its three visible cells to exactly match the
    # walk-transition footprint.
    "›": TileDef(solid=False, color=(12, 9, 11)),
    "♠": TileDef(solid=False, color=(20, 25, 24)),
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
    "Ϟ": TileDef(solid=True, color=(52, 62, 54),
                 prop="temple_serpent_monument", under="█"),
    # Freestanding pedestal brazier: animated tileset terrain (like the
    # wall torch 'i'), solid on the floor it stands on.
    "ø": TileDef(solid=True, color=(48, 59, 51)),
    # Processional path: walkable paved slabs down the entrance hall's
    # central aisle, from the exterior door to the deeper gate.
    "≡": TileDef(solid=False, color=(78, 82, 66)),
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
    # The temple's damage and leftovers (tools/temple_dressing.py): flat
    # floor pieces walked over, carvings set into the wall, toppled
    # pillars (three tiles, the middle one carrying the sprite) and
    # stumps, and the sanctum's grand arches -- walkable under the
    # opening, solid at the piers.
    "ꞗ": TileDef(solid=False, color=(71, 76, 61),
                 prop="temple_floor_crack", under="·"),
    "ꞙ": TileDef(solid=False, color=(71, 76, 61),
                 prop="temple_missing_slabs", under="·"),
    "ꞛ": TileDef(solid=False, color=(71, 76, 61),
                 prop="temple_moss", under="·"),
    "ꞝ": TileDef(solid=False, color=(71, 76, 61),
                 prop="temple_bones", under="·"),
    "ꞟ": TileDef(solid=True, color=(52, 62, 54),
                 prop="temple_wall_carving", under="█"),
    "ꞡ": TileDef(solid=True, color=(60, 68, 58),
                 prop="temple_toppled_pillar", under="·"),
    "ꞣ": TileDef(solid=True, color=(60, 68, 58), under="·"),
    "ꞥ": TileDef(solid=True, color=(60, 68, 58),
                 prop="temple_pillar_stump", under="·"),
    "ꞧ": TileDef(solid=False, color=(71, 76, 61),
                 prop="temple_grand_arch", under="·"),
    "ꞩ": TileDef(solid=True, color=(60, 68, 58), under="·"),
    # Big broken masonry chunk — the rubble map's dominant debris (session 142).
    "ß": TileDef(solid=True, color=(60, 68, 58),
                 prop="temple_rubble_block", under="·"),
    # A porthole in the ship's hull — solid wall, the sea drawn by the
    # animated ship tileset (session 147).
    "Ø": TileDef(solid=True, color=(96, 164, 214)),
    # Phlegethos (Phase 8): lava is a walkable, lethal fall hazard, like
    # the Astral Sea; a fissure is basalt split by a glowing lava crack.
    "≋": TileDef(solid=False, color=(178, 45, 12)),
    "♨": TileDef(solid=False, color=(58, 35, 30)),
    # The infernal fortress's outer wall and its shut gate, plus the
    # brooding idols that line its approach (Phase 8).
    "▓": TileDef(solid=True, color=(44, 40, 46)),
    "╬": TileDef(solid=True, color=(26, 24, 30)),
    "Ϥ": TileDef(solid=True, color=(58, 52, 58),
                 prop="phlegethos_statue", under="·"),
    # The east-west rubble pass uses its own near-black basalt debris instead
    # of importing the green temple collapse. The lava-fall anchor is solid
    # molten terrain beneath a tall cliff-face prop.
    "þ": TileDef(solid=True, color=(38, 32, 36),
                 prop="phlegethos_rubble", under="·"),
    # Hell's leftovers (tools/phlegethos_dressing.py): ember cracks lie
    # flat, vents are walked past, bone heaps and spikes are solid; the
    # fortress's towers and banners stand on the row under its wall.
    "Ɜ": TileDef(solid=False, color=(58, 35, 30),
                 prop="phlegethos_ember_crack", under="·"),
    "ꞵ": TileDef(solid=False, color=(58, 35, 30),
                 prop="phlegethos_vent", under="·"),
    "ꞷ": TileDef(solid=True, color=(58, 35, 30),
                 prop="phlegethos_bone_heap", under="·"),
    "ꞹ": TileDef(solid=True, color=(58, 35, 30),
                 prop="phlegethos_iron_spikes", under="·"),
    "ꞻ": TileDef(solid=True, color=(44, 40, 46),
                 prop="phlegethos_fortress_tower", under="·"),
    "ꞽ": TileDef(solid=True, color=(44, 40, 46),
                 prop="phlegethos_banner", under="·"),
    "ƒ": TileDef(solid=True, color=(178, 45, 12),
                 prop="phlegethos_lava_fall", under="≋"),
    # A whole modern bus shelter displaced into Phlegethos. Its one solid
    # anchor tile is the rear post/bench footprint; the tall transparent
    # sprite carries the human scale without blocking Chuck's approach.
    # A little more city furniture: a bench and a bin on the kerb, neon on
    # a night facade's bottom course, a steam grate on the pavement, and
    # pipes and tags on sewer brick.
    "ꟓ": TileDef(solid=True, color=(104, 76, 50), prop="city_bench",
                 under="."),
    "ꟕ": TileDef(solid=True, color=(46, 92, 64), prop="city_litter_bin",
                 under="."),
    "ꟗ": TileDef(solid=True, color=(49, 52, 61), prop="city_neon_bar",
                 under="▤"),
    "ꟙ": TileDef(solid=True, color=(49, 52, 61), prop="city_neon_open",
                 under="▤"),
    "ꜧ": TileDef(solid=True, color=(49, 52, 61), prop="city_neon_24h",
                 under="▤"),
    "ꜩ": TileDef(solid=False, color=(45, 49, 56), prop="city_steam_grate",
                 under="."),
    "ꜣ": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER,
                 prop="sewer_pipe", under="b"),
    "ꜥ": TileDef(solid=True, color=config.COLOR_SOLID_PLACEHOLDER,
                 prop="sewer_graffiti", under="b"),
    "☂": TileDef(solid=True, color=(42, 45, 50),
                 prop="city_bus_stop", under="·"),
    # Phase 9's first Feywild silhouettes: tall trees grow from the solid
    # canopy; freestanding spiral plants and mushrooms shape optional floor.
    "ł": TileDef(solid=True, color=(18, 69, 52),
                 prop="feywild_tree", under="#"),
    # The Feywild wood: Chult's rounded silhouettes with a violet sheen,
    # and one ordinary oak. All three stand ON the dense vegetation they
    # dress, so they break up its blocky mass without altering any route.
    # The great trees: a trunk three tiles wide on a three-by-two solid
    # footprint. The anchor carries the sprite, drawn up from the middle
    # of the bottom row; the other five tiles are solid ground the trunk
    # covers.
    # Chult's jungle floor (tools/chult_floor_dressing.py). Ferns and
    # litter are walked over; logs (three tiles, the middle one carrying
    # the sprite), ruin fragments, stelae and the great trees are solid.
    "ꝭ": TileDef(solid=False, color=(37, 44, 28),
                 prop="chult_fern", under="."),
    "ꝯ": TileDef(solid=False, color=(37, 44, 28),
                 prop="chult_leaf_litter", under="."),
    "ꞁ": TileDef(solid=True, color=(78, 56, 36),
                 prop="chult_fallen_log", under="."),
    "ꞃ": TileDef(solid=True, color=(78, 56, 36), under="."),
    "ꞅ": TileDef(solid=True, color=(92, 102, 84),
                 prop="chult_ruin_fragment", under="."),
    "ꞇ": TileDef(solid=True, color=(72, 62, 46),
                 prop="chult_great_tree", under="."),
    "ꞑ": TileDef(solid=True, color=(72, 62, 46), under="."),
    "ꞓ": TileDef(solid=True, color=(92, 102, 84),
                 prop="temple_stela", under="."),
    # Feywild path lanterns (in the hedge, solid), path-edge stones (flat,
    # walked over), and the fen's lily pads and reeds (on water, which
    # stays water) -- tools/feywild_path_dressing.py.
    "Ꞵ": TileDef(solid=True, color=(18, 69, 52),
                 prop="fey_lantern_teal", under="#"),
    "Ꞷ": TileDef(solid=True, color=(18, 69, 52),
                 prop="fey_lantern_violet", under="#"),
    "Ꞹ": TileDef(solid=False, color=(18, 69, 52),
                 prop="fey_path_stones", under="'"),
    "Ꞻ": TileDef(solid=True, color=config.COLOR_WATER_PLACEHOLDER,
                 prop="fen_lily_pads", under="~"),
    "Ꞽ": TileDef(solid=True, color=config.COLOR_WATER_PLACEHOLDER,
                 prop="fen_reeds", under="~"),
    "ፐ": TileDef(solid=True, color=(82, 58, 90),
                 prop="feywild_great_tree", under="."),
    "ፑ": TileDef(solid=True, color=(82, 58, 90), under="."),
    "ŧ": TileDef(solid=True, color=(24, 74, 48),
                 prop="feywild_grove_tree", under="#"),
    "Ŧ": TileDef(solid=True, color=(34, 88, 46),
                 prop="feywild_shrub", under="#"),
    "Ɓ": TileDef(solid=True, color=(44, 86, 46),
                 prop="feywild_oak", under="#"),
    "Ł": TileDef(solid=True, color=(20, 55, 52),
                 prop="feywild_spiral", under="."),
    "ŋ": TileDef(solid=True, color=(20, 55, 52),
                 prop="feywild_mushroom", under="."),
    # Phase 10 landmarks. The cloud staircase stands on dense Feywild growth;
    # the tower arch is walkable pale stone whose huge sprite frames Chuck.
    "☁": TileDef(solid=True, color=(20, 55, 52),
                 prop="cloud_staircase", under="#"),
    "Ƶ": TileDef(solid=False, color=(154, 160, 169),
                 prop="cloud_tower_arch", under="."),
    "♘": TileDef(solid=True, color=(154, 160, 169),
                 prop="griffon_nest", under="#"),
    "℞": TileDef(solid=True, color=(154, 160, 169),
                 prop="aerie_rope", under="#"),
    # The Aerie's central shaft looks into the unlit tower interior.  It is
    # solid collision like open sky, but deliberately has separate art so it
    # cannot read as another gap through the clouds.
    "●": TileDef(solid=True, color=(8, 9, 15)),
    "⇓": TileDef(solid=False, color=(154, 160, 169), under="."),
    # Feywild path thresholds retain the regional path art while keeping
    # opposite directions distinct for authored two-way transitions.
    "←": TileDef(solid=False, color=(45, 76, 59),
                 under="'", overhead="fey_opening_w"),
    "→": TileDef(solid=False, color=(45, 76, 59),
                 under="'", overhead="fey_opening_e"),
    "⇧": TileDef(solid=False, color=(45, 76, 59),
                 under="'", overhead="fey_opening_n"),
    "⇩": TileDef(solid=False, color=(45, 76, 59),
                 under="'", overhead="fey_opening_s"),
    # Luminous Feywild pollen is ordinary walkable ground. Its only gameplay
    # effect is derived from Chuck's grounded footprint each frame.
    "☼": TileDef(solid=False, color=(76, 99, 54)),
    # Rootways: solid knotted root masses divide the forest floor. The narrow
    # gap is ordinary path under an overhead root arch, traversable by Chuck.
    "※": TileDef(solid=True, color=(58, 43, 39)),
    # The root wall dressed: its front face where it stops above open
    # ground, and the knots that stand along its runs. All solid, like
    # the wall they are made of.
    "ፒ": TileDef(solid=True, color=(58, 43, 39)),
    "ፓ": TileDef(solid=True, color=(58, 43, 39), prop="fey_root_knot",
                 under="※"),
    "ፔ": TileDef(solid=True, color=(58, 43, 39), prop="fey_root_knot",
                 under="ፒ"),
    "≀": TileDef(solid=False, color=(45, 76, 59),
                 under="'", overhead="fey_root_passage"),
    # Luminous Rapids: fast bright water no one crosses, static wet
    # stones, and giant flower pads that the reactive flowers raise and
    # sink. A risen pad is standable; a furled one is water again.
    "ᚼ": TileDef(solid=True, color=(86, 190, 214)),
    "ᚹ": TileDef(solid=False, color=(104, 112, 116)),
    "ᚨ": TileDef(solid=False, color=(58, 138, 74)),
    "ᚧ": TileDef(solid=True, color=(34, 96, 108)),
    # Mushroom Underways: the shaded floor beneath a giant cap is ordinary
    # walkable ground, only darker. A luminous pool is solid -- something
    # to walk around and look at rather than through.
    "ᛥ": TileDef(solid=False, color=(18, 40, 44)),
    "ᛞ": TileDef(solid=True, color=(52, 158, 186)),
    # Redcap Warrens: bare earth the camp has trampled flat.
    "ᛜ": TileDef(solid=False, color=(66, 57, 45)),
    # Redcap Warrens: fused giant toadstools form a solid thicket, and one
    # cap arches over a gap only Chuck fits through -- the mushroom
    # counterpart to the Rootways' root passage, and just as impassable to
    # a gnome-sized redcap.
    "ᛘ": TileDef(solid=True, color=(58, 40, 62)),
    "ᚿ": TileDef(solid=False, color=(45, 76, 59),
                 under="'", overhead="fey_mushroom_passage"),
    # The camp's oversized gear. Each is solid standing dressing on the
    # forest floor, sized to dwarf a one-foot-tall rat.
    "ᚠ": TileDef(solid=True, color=(78, 52, 38),
                 prop="redcap_boot", under="."),
    "ᚢ": TileDef(solid=True, color=(72, 76, 86),
                 prop="redcap_cauldron", under="."),
    "ᚦ": TileDef(solid=True, color=(88, 64, 44),
                 prop="redcap_sickle", under="."),
    "ᚱ": TileDef(solid=True, color=(92, 74, 52),
                 prop="redcap_shelter", under="."),
    # Giant Tea Table: a solid elevated surface, its deep walkable shadow,
    # and a low apron Chuck can pass beneath. Place settings remain solid
    # tabletop dressing while the legs become human/Fey-scale columns.
    "▤": TileDef(solid=True, color=(117, 76, 65)),
    "░": TileDef(solid=False, color=(13, 38, 39)),
    "◍": TileDef(solid=True, color=(117, 76, 65)),
    "♜": TileDef(solid=True, color=(13, 38, 39),
                 prop="fey_table_leg", under="░"),
    "◉": TileDef(solid=True, color=(117, 76, 65),
                 prop="fey_plate", under="▤"),
    "☕": TileDef(solid=True, color=(117, 76, 65),
                 prop="fey_teacup", under="▤"),
    "⌁": TileDef(solid=True, color=(117, 76, 65),
                 prop="fey_napkin", under="▤"),
    "⁙": TileDef(solid=True, color=(117, 76, 65),
                 prop="fey_crumbs", under="▤"),
    # Needle Garden's dense flowering beds define projectile lanes. Orchids
    # root directly into this solid terrain and fire outward across the path.
    "✿": TileDef(solid=True, color=(42, 79, 56)),
    # Phase 7 ship interiors: dark, open human-scale doorway recesses fill
    # the west, east, and south walls. They are walkable so Chuck can enter
    # the threshold; out-of-bounds collision keeps unfinished routes contained.
    "╭": TileDef(solid=False, color=(24, 20, 19)),
    "│": TileDef(solid=False, color=(24, 20, 19)),
    "╰": TileDef(solid=False, color=(24, 20, 19)),
    "╮": TileDef(solid=False, color=(24, 20, 19)),
    "┃": TileDef(solid=False, color=(24, 20, 19)),
    "╯": TileDef(solid=False, color=(24, 20, 19)),
    "┌": TileDef(solid=False, color=(24, 20, 19)),
    "┬": TileDef(solid=False, color=(24, 20, 19)),
    "┐": TileDef(solid=False, color=(24, 20, 19)),
    "├": TileDef(solid=False, color=(24, 20, 19)),
    "┼": TileDef(solid=False, color=(24, 20, 19)),
    "┤": TileDef(solid=False, color=(24, 20, 19)),
    # Human-scale ship ladder: a continuous 16x32 two-cell structure,
    # matching the established 16x30 crew sprite scale.
    "ℓ": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER),
    "ɭ": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER),
    # Exterior deck: animated open sea surrounds a broad wooden hull. The
    # rail pieces are solid perimeter geometry; their oriented tiles keep the
    # ship silhouette readable instead of treating the edge as an indoor wall.
    "═": TileDef(solid=True, color=(82, 53, 31)),
    "║": TileDef(solid=True, color=(82, 53, 31)),
    "╔": TileDef(solid=True, color=(82, 53, 31)),
    "╗": TileDef(solid=True, color=(82, 53, 31)),
    "╚": TileDef(solid=True, color=(82, 53, 31)),
    "╝": TileDef(solid=True, color=(82, 53, 31)),
    "∥": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER),
    "ʘ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_mast_sail", under="="),
    "ɧ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_helm", under="="),
    "ƀ": TileDef(solid=True, color=(82, 53, 31),
                 prop="ship_bowsprit", under="║"),
    # Crew-quarters furniture. Both are human-scale props over ship planks;
    # their single solid anchor tile leaves overhangs Chuck can scurry under.
    "ɦ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_hammock", under="="),
    "ɱ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_round_table", under="="),
    "ȼ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_captain_chest", under="="),
    "ḅ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_captain_bed", under="="),
    "Ḅ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 under="="),
    "ṛ": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_captain_rug", under="="),
    # Below-decks dressing. The desk is three tiles wide, so it stands on
    # an anchor and two blank solid tiles either side, like the bed; the
    # rope coil lies flat and is walked over.
    "ꝑ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_bookshelf", under="="),
    "ꝓ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_writing_desk", under="="),
    "ꝕ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 under="="),
    "ꝗ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_butcher_block", under="="),
    "ꝙ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_stew_pot", under="="),
    "ꝛ": TileDef(solid=False, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_rope_coil", under="="),
    "ꝝ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="ship_cargo_stack", under="="),
    # Lower-hold reuse of the pantry's carton-filled breakable shelves/jars,
    # with ship planks beneath instead of pantry boards.
    "ƞ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="pantry_shelf", under="="),
    "ʒ": TileDef(solid=True, color=config.COLOR_PLANK_PLACEHOLDER,
                 prop="grain_sack", under="="),
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
    # Phase 12's Cabin grounds.  Dedicated terrain preserves the
    # authored real-place layout and Pacific Northwest palette.  The two
    # black doorway recesses surround one aligned walkable threshold apiece.
    # Interior materials share the same sheet so crossing a normal cabin
    # threshold does not require a second rendering vocabulary.
    "ᶠ": TileDef(solid=False, color=(27, 39, 32)),
    "♟": TileDef(solid=True, color=(10, 25, 22)),
    # The strip of fake grass laid over the dirt outside the cabin.
    "ᵿ": TileDef(solid=False, color=(36, 84, 36)),
    "⌇": TileDef(solid=False, color=(46, 49, 39)),
    "▧": TileDef(solid=True, color=(42, 55, 55)),
    "▨": TileDef(solid=True, color=(50, 69, 73)),
    "▣": TileDef(solid=False, color=(104, 74, 48)),
    "↟": TileDef(solid=False, color=(88, 62, 40)),
    "◼": TileDef(solid=True, color=(5, 8, 10)),
    "Ɛ": TileDef(solid=False, color=(5, 8, 10)),  # exterior front door
    "Ɯ": TileDef(solid=False, color=(5, 8, 10)),  # interior front door
    "Ŀ": TileDef(solid=False, color=(91, 88, 56)),
    "∎": TileDef(solid=True, color=(91, 88, 56)),
    "Ƃ": TileDef(solid=False, color=(157, 145, 107)),
    "▰": TileDef(solid=True, color=(157, 145, 107)),
    "Ħ": TileDef(solid=False, color=(105, 61, 39)),
    "ħ": TileDef(solid=True, color=(105, 61, 39)),
    "ć": TileDef(solid=True, color=(72, 43, 31)),
    "♣": TileDef(solid=True, color=(10, 25, 22),
                 prop="tahuya_fir", under="♟"),
    # Evergreen huckleberry and salal: the understory a Douglas-fir
    # stand in Washington actually has under it. Both are scenery Chuck
    # walks through rather than around -- he is a foot tall and these
    # are shrubs, so blocking on them would fence off the whole wood.
    "ᶲ": TileDef(solid=False, color=(32, 80, 50),
                 prop="tahuya_salal", under="ᶠ"),
    "ᶳ": TileDef(solid=False, color=(28, 70, 44),
                 prop="tahuya_huckleberry", under="ᶠ"),
    "✦": TileDef(solid=True, color=(27, 39, 32),
                 prop="tahuya_mushroom_light", under="ᶠ"),
    "⚉": TileDef(solid=True, color=(27, 39, 32),
                 prop="tahuya_firepit", under="ᶠ"),
    "◌": TileDef(solid=True, color=(27, 39, 32),
                 prop="tahuya_ufo", under="ᶠ"),
    "⌘": TileDef(solid=True, color=(27, 39, 32),
                 prop="tahuya_firewood_shed", under="ᶠ"),
    "ℂ": TileDef(solid=True, color=(10, 25, 22),
                 prop="tahuya_cabin", under="♟"),
    # Human-scale cabin furnishings. Their larger visible sprites are backed
    # by solid carpet/linoleum footprint tiles authored in the map.
    "Ƈ": TileDef(solid=True, color=(91, 88, 56),
                 prop="cabin_big_couch", under="∎"),
    "Ƭ": TileDef(solid=True, color=(91, 88, 56),
                 prop="cabin_couch", under="∎"),
    "ƭ": TileDef(solid=True, color=(91, 88, 56),
                 prop="cabin_chair", under="∎"),
    "Ƒ": TileDef(solid=True, color=(91, 88, 56),
                  prop="cabin_table", under="∎"),
    "ƛ": TileDef(solid=True, color=(91, 88, 56),
                  prop="cabin_connector_shelf", under="∎"),
    "Ɩ": TileDef(solid=True, color=(91, 88, 56),
                  prop="cabin_mini_fridge", under="∎"),
    "ƚ": TileDef(solid=True, color=(72, 43, 31),
                  prop="cabin_closed_door_west", under="ć"),
    "ƕ": TileDef(solid=True, color=(157, 145, 107),
                 prop="cabin_kitchen", under="ħ"),
    "Ʒ": TileDef(solid=True, color=(91, 88, 56),
                  prop="cabin_woodstove", under="∎"),
    "Ə": TileDef(solid=True, color=(91, 88, 56),
                 prop="cabin_wood_storage", under="∎"),
    # A lava lamp on a pale blue side table, the closed door in the north
    # wall, and the drawn curtains behind the two couches.
    "Ɔ": TileDef(solid=True, color=(156, 186, 206),
                 prop="cabin_lava_lamp", under="Ŀ"),
    "Ɖ": TileDef(solid=True, color=(112, 74, 46),
                 prop="cabin_closed_door_north", under="Ŀ"),
    "Ɏ": TileDef(solid=True, color=(132, 108, 84),
                 prop="cabin_curtain_window", under="∎"),
    "Ɱ": TileDef(solid=True, color=(176, 138, 92),
                 prop="cabin_macrame", under="ć"),
    "Ʇ": TileDef(solid=True, color=(104, 66, 42),
                 prop="cabin_side_table", under="Ŀ"),
    "Ɵ": TileDef(solid=True, color=(152, 114, 64),
                 prop="cabin_goose_mount", under="Ŀ"),
}

MARKER_DEFS: dict[str, MarkerDef] = {
    "C": MarkerDef(kind="player", under="="),
    "E": MarkerDef(kind="player", under=","),
    "c": MarkerDef(kind="cigarette", under=","),
    "j": MarkerDef(kind="cigarette", under="="),
    "K": MarkerDef(kind="cat", under=","),
    "A": MarkerDef(kind="anchor:waterdeep_anchor", under=","),
    # Phase 13. The desert hub's ashtray stands on the middle ruin's
    # buried floor: the one place a player can see from a distance.
    "⨀": MarkerDef(kind="anchor:desert_central_anchor", under="⌖"),
    "⨁": MarkerDef(kind="anchor:desert_orc_camp_anchor", under="."),
    "☉": MarkerDef(kind="anchor:desert_oasis_anchor", under="⩊"),
    # Cigarette grass on the oasis turf: the established scratchable,
    # standing on the only green ground in the region.
    "⩏": MarkerDef(kind="breakable_grass", under="⩊"),
    "♆": MarkerDef(kind="arrival:from_oasis", under="."),
    "♁": MarkerDef(kind="arrival:from_undead_ruins", under="."),
    "☽": MarkerDef(kind="anchor:desert_ruins_anchor", under="⌖"),
    # Skeletons patrolling the ruins: the Chult implementation exactly,
    # standing on sand outside the walls and on flagstones within.
    "ᛊ": MarkerDef(kind="skeleton", under="."),
    "ᛏ": MarkerDef(kind="skeleton", under="⌖"),
    # Phase 13's eastward traversal.
    "⌦": MarkerDef(kind="arrival:from_desert_central", under="."),
    "⌸": MarkerDef(kind="anchor:desert_east_1_anchor", under="."),
    "⌱": MarkerDef(kind="arrival:from_east_1", under="."),
    "⌲": MarkerDef(kind="arrival:from_east_2", under="."),
    "⌳": MarkerDef(kind="anchor:desert_east_2_anchor", under="."),
    # Snakes, in the jungle that fell in with them.
    "⌴": MarkerDef(kind="snake", under="ᛗ"),
    "⌵": MarkerDef(kind="arrival:from_east_3", under="."),
    "⌶": MarkerDef(kind="anchor:desert_east_3_anchor", under="."),
    "⌷": MarkerDef(kind="arrival:from_east_4", under="."),
    "⌹": MarkerDef(kind="anchor:desert_east_4_anchor", under="."),
    # Redcaps came through with the Feywild. Hell's devils needed no
    # marker of their own: Phlegethos already authored one per facing,
    # each standing on basalt, which is exactly what its fragment is.
    "⌺": MarkerDef(kind="redcap", under="ᛟ"),
    "⍀": MarkerDef(kind="arrival:from_east_5", under="."),
    "⍁": MarkerDef(kind="anchor:desert_east_5_anchor", under="."),
    # Armoured knights, on the courtyard they came in on.
    "⍂": MarkerDef(kind="knight", under="⌽"),
    "⍃": MarkerDef(kind="arrival:from_east_6", under="."),
    "⍄": MarkerDef(kind="anchor:desert_east_6_anchor", under="."),
    # The seventh map east, and the way back out of it. Nine worlds on
    # one map: its arrival and its Ashtray both stand on the sliver of
    # desert by the west gap, which is the last ordinary ground on it.
    "⍳": MarkerDef(kind="arrival:from_east_6", under="."),
    "⍴": MarkerDef(kind="anchor:desert_east_7_anchor", under="."),
    # Coming back out of the seventh map, and going into the eighth.
    # One character for both: an arrival is named for where you came
    # *from*, so the sixth map's return and the eighth map's entrance
    # are the same marker standing on two different maps -- the same
    # way the hub's three neighbours all share one.
    "⍵": MarkerDef(kind="arrival:from_east_7", under="."),
    # The eighth map east, where the ground has mostly gone. Its
    # Ashtray is on the desert island by the west rim -- the last thing
    # on the traversal wide enough to stand on and think about.
    "⍹": MarkerDef(kind="anchor:desert_east_8_anchor", under="."),
    "⍺": MarkerDef(kind="arrival:from_east_8", under="."),
    # ------------------------------------------------------------------
    # The final trio encounter. The three of them stand on plain desert
    # sand: they are the one thing on the map that is not a fragment of
    # somewhere else, and the ground under them is the ground this whole
    # phase has been about.
    #
    # Reusing the established battle actors rather than authoring new
    # ones is the point. A player has met these three twice and is meant
    # to recognise them, which a bespoke third pair of sprites would
    # quietly cost.
    # ------------------------------------------------------------------
    "⍻": MarkerDef(kind="battle:fighter", under="."),
    "⍼": MarkerDef(kind="battle:wizard", under="."),
    "⍽": MarkerDef(kind="battle:ranger", under="."),
    "⍾": MarkerDef(kind="arrival:from_east_8", under="."),
    "⍿": MarkerDef(kind="anchor:desert_trio_anchor", under="."),
    "⎀": MarkerDef(kind="arrival:from_trio", under="."),
    # The blue dragon, facing the way its breath goes. It cannot be
    # fought, so it has no facing variants for pursuit -- only the two
    # a lane of lightning can point along.
    "⍅": MarkerDef(kind="blue_dragon:left", under="❄"),
    "⍆": MarkerDef(kind="blue_dragon:right", under="❄"),
    # Desert orcs, on the sand and inside the camp's beaten ground.
    "❂": MarkerDef(kind="orc", under="."),
    "⟠": MarkerDef(kind="orc", under=","),
    # The one road between the hub and the camp, walked both ways.
    "⛲": MarkerDef(kind="arrival:from_orc_camp", under="."),
    "⌬": MarkerDef(kind="arrival:from_desert_central", under="."),
    "Y": MarkerDef(kind="anchor:sewer_anchor", under="d"),
    "N": MarkerDef(kind="npc:dock_worker", under=","),
    "G": MarkerDef(kind="npc:guard", under=","),
    "I": MarkerDef(kind="npc:market_woman", under=","),
    # Phase 14's shared street between the docks and fountain plaza.
    "Ƥ": MarkerDef(kind="arrival:from_plaza", under=","),
    "ɸ": MarkerDef(kind="arrival:from_docks", under=","),
    "Ʀ": MarkerDef(kind="player", under=","),
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
    "ʛ": MarkerDef(kind="breakable_grass", under="ᶠ"),
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
    # The entrance hall's three center-aisle markers sit ON the
    # processional path, so their under-terrain matches it (no seams).
    "κ": MarkerDef(kind="arrival:from_temple_exterior", under="≡"),
    "ρ": MarkerDef(kind="anchor:temple_1_anchor", under="≡"),
    "σ": MarkerDef(kind="boundary:temple_deeper", under="∇"),
    "υ": MarkerDef(kind="arrival:from_temple_2", under="≡"),
    "φ": MarkerDef(kind="arrival:from_temple_1", under="≡"),
    "χ": MarkerDef(kind="anchor:temple_2_anchor", under="·"),
    "ω": MarkerDef(kind="boundary:temple_3", under="∇"),
    "Ι": MarkerDef(kind="arrival:from_temple_3", under="≡"),
    "Λ": MarkerDef(kind="arrival:from_temple_2", under="≡"),
    "Φ": MarkerDef(kind="anchor:temple_3_anchor", under="·"),
    "Ψ": MarkerDef(kind="skeleton", under="·"),
    "Π": MarkerDef(kind="boundary:temple_4", under="∇"),
    "Σ": MarkerDef(kind="arrival:from_temple_4", under="≡"),
    "Ρ": MarkerDef(kind="arrival:from_temple_3", under="≡"),
    "Τ": MarkerDef(kind="anchor:temple_4_anchor", under="·"),
    "Υ": MarkerDef(kind="boundary:temple_5", under="∇"),
    "Ξ": MarkerDef(kind="arrival:from_temple_5", under="≡"),
    "Η": MarkerDef(kind="arrival:from_temple_4", under="≡"),
    "Θ": MarkerDef(kind="anchor:temple_5_anchor", under="·"),
    "Ο": MarkerDef(kind="boundary:temple_6", under="∇"),
    "ς": MarkerDef(kind="snake", under="·"),
    "Μ": MarkerDef(kind="arrival:from_temple_6", under="≡"),
    "Ζ": MarkerDef(kind="arrival:from_temple_5", under="≡"),
    "ϑ": MarkerDef(kind="anchor:temple_6_anchor", under="·"),
    "ϖ": MarkerDef(kind="boundary:temple_7", under="∇"),
    # Temple Map 7, the shrine hall (session 121).
    "ϒ": MarkerDef(kind="arrival:from_temple_6", under="≡"),
    "ϰ": MarkerDef(kind="anchor:temple_7_anchor", under="·"),
    "ϱ": MarkerDef(kind="boundary:temple_8", under="∇"),
    "ϵ": MarkerDef(kind="arrival:from_temple_7", under="≡"),
    # Temple Map 9, the final chamber (session 130).
    "ϻ": MarkerDef(kind="arrival:from_temple_8", under="≡"),
    "ϼ": MarkerDef(kind="anchor:temple_9_anchor", under="·"),
    "Ͻ": MarkerDef(kind="arrival:from_temple_9", under="≡"),
    # The final chamber's battle tableau (session 131).
    "Ͼ": MarkerDef(kind="battle:fighter", under="≡"),
    "Ͽ": MarkerDef(kind="battle:wizard", under="·"),
    "Ѐ": MarkerDef(kind="battle:ranger", under="·"),
    "Ё": MarkerDef(kind="battle:beholder", under="·"),
    # Temple Map 8, the gauntlet (session 122).
    "ϴ": MarkerDef(kind="arrival:from_temple_7", under="≡"),
    "Ϲ": MarkerDef(kind="anchor:temple_8_anchor", under="·"),
    "Ϸ": MarkerDef(kind="boundary:temple_9", under="∇"),
    "Ϻ": MarkerDef(kind="arrival:from_temple_8", under="≡"),
    "↓": MarkerDef(kind="dart_trap:down", under="W", allow_solid=True),
    "↑": MarkerDef(kind="dart_trap:up", under="W", allow_solid=True),
    # The rubble map — where the scripted Fireball throws Chuck (session 135).
    # Its arrival and ashtray sit on the one intact paved lane (session 139).
    "Ѣ": MarkerDef(kind="arrival:from_fireball", under="≡"),
    "Ѥ": MarkerDef(kind="anchor:temple_rubble_anchor", under="≡"),
    # The ship deck — where the crawlspace leads out (session 138).
    "Ҋ": MarkerDef(kind="arrival:from_crawlspace", under="="),
    "Ҍ": MarkerDef(kind="anchor:ship_deck_anchor", under="="),
    "Ҝ": MarkerDef(kind="arrival:from_lower_hold", under="="),
    "Ҟ": MarkerDef(kind="arrival:from_ship_room", under="="),
    "Ҡ": MarkerDef(kind="anchor:ship_lower_hold_anchor", under="="),
    "Ң": MarkerDef(kind="rat", under="="),
    "Ҥ": MarkerDef(kind="pirate_chef", under="="),
    "Ҧ": MarkerDef(kind="arrival:from_ship_room", under="="),
    "Ҩ": MarkerDef(kind="anchor:ship_galley_anchor", under="="),
    "Ҫ": MarkerDef(kind="arrival:from_galley", under="="),
    "Ҭ": MarkerDef(kind="arrival:from_ship_room", under="="),
    "Ұ": MarkerDef(kind="anchor:ship_crew_anchor", under="="),
    "Ү": MarkerDef(
        kind="pirate_npc:seated_pirate:crew_pirate_met", under="="
    ),
    "Ҳ": MarkerDef(kind="boundary:captain_cabin", under="┃"),
    "Һ": MarkerDef(kind="boundary:ship_deck", under="="),
    "Ҵ": MarkerDef(kind="arrival:from_crew_quarters", under="="),
    "Ӏ": MarkerDef(kind="arrival:from_captain_cabin", under="="),
    "Ӂ": MarkerDef(kind="arrival:from_crew_quarters", under="="),
    "ӂ": MarkerDef(kind="anchor:ship_captain_anchor", under="="),
    "Ӄ": MarkerDef(kind="arrival:from_crew_quarters", under="="),
    "ӄ": MarkerDef(kind="anchor:ship_exterior_anchor", under="="),
    "Ӆ": MarkerDef(kind="arrival:from_exterior_deck", under="="),
    "ӆ": MarkerDef(
        kind="deck_pirate:concertina_pirate:deck_concertina_met:concertina",
        under="=",
    ),
    "Ӈ": MarkerDef(
        kind="deck_pirate:cheering_pirate:deck_cheering_met:cheer", under="=",
    ),
    "ӈ": MarkerDef(
        kind="deck_pirate:dancing_pirate:deck_dancer_met:dance", under="=",
    ),
    "Ӊ": MarkerDef(
        kind="deck_pirate:jeffries:deck_jeffries_met:struggle", under="=",
    ),
    "ӊ": MarkerDef(kind="sword_fighter:a", under="="),
    "Ӌ": MarkerDef(kind="sword_fighter:b", under="="),
    "ӌ": MarkerDef(
        kind="deck_captain:captain_pirate:captain_confronted:captain",
        under="=",
    ),
    "Ӎ": MarkerDef(
        kind="deck_plank_origin", under="═", allow_solid=True,
    ),
    # The rubble crawlspace's "Enter crevice?" prompt (session 141).
    "Ҏ": MarkerDef(kind="choice:crevice", under="≡"),
    # Phlegethos arrival map — where the Nine Hells fall drops Chuck.
    "Ѩ": MarkerDef(kind="arrival:from_hell", under="≡"),
    "Ѫ": MarkerDef(kind="anchor:phlegethos_anchor", under="·"),
    "Ѭ": MarkerDef(kind="arrival:from_phlegethos_2", under="≡"),
    # Phlegethos map 2, the lava road, and its infernal enemies. Lemures
    # are a third undead kind and fire snakes a temple-snake variant, so
    # both spawn through the existing enemy paths.
    "Ѯ": MarkerDef(kind="lemure", under="·"),
    "Ԁ": MarkerDef(kind="fire_snake", under="·"),
    "Ԃ": MarkerDef(kind="arrival:from_phlegethos_1", under="≡"),
    "Ԅ": MarkerDef(kind="anchor:phlegethos_road_anchor", under="·"),
    "Ԇ": MarkerDef(kind="arrival:from_phlegethos_3", under="≡"),
    # Phlegethos map 3, the lava lake crossed by stepping-stone islands.
    "Ԉ": MarkerDef(kind="arrival:from_phlegethos_2", under="≡"),
    "Ԋ": MarkerDef(kind="anchor:phlegethos_lake_anchor", under="≡"),
    "Ԍ": MarkerDef(kind="arrival:from_phlegethos_4", under="≡"),
    # Spined devils perch and throw down an authored lane; flameskulls
    # weave along a horizontal or vertical haunt.
    "Ԏ": MarkerDef(kind="spined_devil:down", under="·"),
    "Ԑ": MarkerDef(kind="spined_devil:up", under="·"),
    "Ԓ": MarkerDef(kind="spined_devil:left", under="·"),
    "Ԕ": MarkerDef(kind="spined_devil:right", under="·"),
    "Ԗ": MarkerDef(kind="flameskull:h", under="·"),
    "Ԙ": MarkerDef(kind="flameskull:v", under="·"),
    # Flameskulls float, so they may also haunt open lava. These place
    # the same hazard while leaving the molten tile beneath untouched.
    "Ԛ": MarkerDef(kind="flameskull:h", under="≋"),
    "Ԝ": MarkerDef(kind="flameskull:v", under="≋"),
    # Phlegethos map 5, the fortress approach, its infernal garrison,
    # and the trio's battle with the Pit Fiend.
    "Ԟ": MarkerDef(kind="horned_devil", under="·"),
    "Ԡ": MarkerDef(kind="arrival:from_phlegethos_rubble", under="≡"),
    "Ԣ": MarkerDef(kind="anchor:phlegethos_4_anchor", under="≡"),
    "Ԥ": MarkerDef(kind="boundary:phlegethos_fortress", under="≡"),
    "Ԧ": MarkerDef(kind="battle:fighter", under="≡"),
    "Ԩ": MarkerDef(kind="battle:wizard", under="≡"),
    "Ԫ": MarkerDef(kind="battle:ranger", under="≡"),
    "Ԭ": MarkerDef(kind="battle:pit_fiend", under="≡"),
    # Phlegethos's east-west rubble pass, inserted between the lava lake and
    # fortress. Its internal checkpoint IDs remain independent of display
    # numbering so existing fortress saves stay valid.
    "Ԯ": MarkerDef(kind="arrival:from_phlegethos_3", under="≡"),
    "԰": MarkerDef(kind="anchor:phlegethos_rubble_anchor", under="≡"),
    "Բ": MarkerDef(kind="arrival:from_phlegethos_fortress", under="≡"),
    # The fractured way inserted before the fortress battle. Existing
    # fortress marker IDs remain untouched so old saves stay valid.
    "ዐ": MarkerDef(kind="arrival:from_phlegethos_rubble", under="≡"),
    "ዑ": MarkerDef(kind="anchor:phlegethos_fractured_anchor", under="≡"),
    "ዒ": MarkerDef(kind="arrival:from_phlegethos_fortress", under="≡"),
    "ዓ": MarkerDef(kind="pit_fiend", under="·"),
    "ዕ": MarkerDef(kind="npc:businessman", under="≡"),
    # Phase 9 opens on the bank reached by the river cutscene.
    "Գ": MarkerDef(kind="arrival:from_river", under=","),
    "Դ": MarkerDef(kind="anchor:feywild_anchor", under="'"),
    "Ե": MarkerDef(kind="boundary:feywild_deeper", under="→"),
    "Խ": MarkerDef(kind="arrival:from_feywild_2", under="'"),
    # Blooming Path: one reversible flower exchanges the upper and lower
    # authored vegetation gates. Solid target markers explicitly opt in.
    "Զ": MarkerDef(kind="arrival:from_feywild_1", under="'"),
    "Է": MarkerDef(kind="anchor:feywild_2_anchor", under="'"),
    "Ը": MarkerDef(kind="boundary:feywild_3", under="→"),
    "Թ": MarkerDef(kind="flower_switch:intro", under="."),
    "Ժ": MarkerDef(
        kind="flower_open:intro", under="#", allow_solid=True
    ),
    "Ի": MarkerDef(kind="flower_close:intro", under="'"),
    # Pollen Orchard arrivals, checkpoint, later boundary, and its optional
    # route-exchange flower.
    "Լ": MarkerDef(kind="arrival:from_feywild_2", under="'"),
    "Ծ": MarkerDef(kind="anchor:feywild_3_anchor", under="'"),
    "Կ": MarkerDef(kind="boundary:feywild_4", under="⇧"),
    "Հ": MarkerDef(kind="arrival:from_feywild_4", under="'"),
    "Ձ": MarkerDef(kind="flower_switch:orchard", under="."),
    "Ղ": MarkerDef(
        kind="flower_open:orchard", under="#", allow_solid=True
    ),
    "Ճ": MarkerDef(kind="flower_close:orchard", under="'"),
    "Մ": MarkerDef(kind="arrival:from_feywild_3", under="'"),
    # Rootways: first redcap pursuit and Chuck-scale protected passages.
    "Յ": MarkerDef(kind="arrival:from_feywild_3", under="'"),
    "Ն": MarkerDef(kind="anchor:feywild_4_anchor", under="'"),
    "Շ": MarkerDef(kind="redcap", under="."),
    "Ո": MarkerDef(kind="boundary:feywild_5", under="→"),
    "Չ": MarkerDef(kind="arrival:from_feywild_5", under="'"),
    # Giant Tea Table: quiet Map 5 respite and future Needle Garden edge.
    "Պ": MarkerDef(kind="arrival:from_feywild_4", under="."),
    "Ջ": MarkerDef(kind="anchor:feywild_5_anchor", under="."),
    "Ռ": MarkerDef(kind="boundary:feywild_6", under="⇩"),
    "Ս": MarkerDef(kind="arrival:from_feywild_6", under="."),
    # Luminous Rapids: two flower groups that raise and sink pads, the
    # moths and orchids that watch the lanes, and the map's own points.
    "წ": MarkerDef(kind="flower_switch:rapids_upper", under="."),
    "ჭ": MarkerDef(
        kind="flower_open:rapids_upper", under="ᚧ", allow_solid=True
    ),
    "ხ": MarkerDef(kind="flower_close:rapids_upper", under="ᚨ"),
    "ჯ": MarkerDef(kind="flower_switch:rapids_lower", under="."),
    "ჰ": MarkerDef(
        kind="flower_open:rapids_lower", under="ᚧ", allow_solid=True
    ),
    "ჱ": MarkerDef(kind="flower_close:rapids_lower", under="ᚨ"),
    "ჲ": MarkerDef(kind="arrival:from_feywild_11", under="'"),
    "ჳ": MarkerDef(kind="anchor:feywild_12_anchor", under="."),
    "ჴ": MarkerDef(kind="boundary:feywild_13", under="→"),
    "ჵ": MarkerDef(kind="arrival:from_feywild_13", under="'"),
    # Moths fly the lanes, so they sit over the rapids themselves.
    "ჶ": MarkerDef(kind="lantern_moth:h", under="ᚼ", allow_solid=True),
    "ჷ": MarkerDef(kind="lantern_moth:v", under="ᚼ", allow_solid=True),
    "ჸ": MarkerDef(kind="spitting_orchid:left", under="#", allow_solid=True),
    "ჹ": MarkerDef(kind="spitting_orchid:down", under="#", allow_solid=True),
    # Twilight Crossroads: one reciprocal route exchange, a southern return
    # from the geographically wrong Rapids connection, and an intentionally
    # inert western boundary reserved for the later floating wizard tower.
    "Ꭰ": MarkerDef(kind="flower_switch:twilight", under="."),
    "Ꭱ": MarkerDef(
        kind="flower_open:twilight", under="#", allow_solid=True
    ),
    "Ꭲ": MarkerDef(kind="flower_close:twilight", under="'"),
    "Ꭳ": MarkerDef(kind="arrival:from_feywild_12", under="'"),
    "Ꭴ": MarkerDef(kind="anchor:feywild_13_anchor", under="."),
    "Ꭵ": MarkerDef(kind="boundary:feywild_tower", under="←"),
    "Ꭶ": MarkerDef(kind="arrival:from_feywild_tower", under="'"),
    # Phase 10 Cloud Staircase and first tower platform.
    "ሀ": MarkerDef(kind="arrival:from_feywild_13", under="'"),
    "ሁ": MarkerDef(kind="anchor:zephyros_staircase_anchor", under="'"),
    "ሂ": MarkerDef(kind="choice:cloud_staircase", under="'"),
    "ሃ": MarkerDef(kind="arrival:from_staircase", under="."),
    "ሄ": MarkerDef(kind="anchor:zephyros_exterior_anchor", under="."),
    "ህ": MarkerDef(kind="boundary:zephyros_aerie", under="Ƶ"),
    "ሆ": MarkerDef(kind="arrival:from_aerie", under="."),
    # The Aerie: exterior return, local anchor, one colossal griffon, and
    # the stable rope boundary for Zephyros' introduction slice.
    "ሇ": MarkerDef(kind="arrival:from_exterior", under="."),
    "ለ": MarkerDef(kind="anchor:zephyros_aerie_anchor", under="."),
    "ሉ": MarkerDef(kind="griffon", under="."),
    "ሊ": MarkerDef(kind="choice:zephyros_rope", under="."),
    "ላ": MarkerDef(kind="arrival:from_flight", under="."),
    "ሌ": MarkerDef(kind="anchor:modern_city_anchor", under="."),
    # Phase 11 City Night 1: ordinary loose cigarettes on wet sidewalk.
    "ል": MarkerDef(kind="cigarette", under="."),
    "ሎ": MarkerDef(kind="traffic_lane:right:0", under="="),
    "ሏ": MarkerDef(kind="traffic_lane:left:1", under="="),
    # City Night 1/2 handoff, local checkpoint, pedestrians, and raccoon.
    "ሐ": MarkerDef(kind="boundary:modern_city_night_2", under="⮝"),
    "ሑ": MarkerDef(kind="arrival:from_city_night_2", under="."),
    "ሒ": MarkerDef(kind="arrival:from_city_night_1", under="."),
    "ሓ": MarkerDef(kind="anchor:modern_city_2_anchor", under="."),
    "ሔ": MarkerDef(kind="boundary:modern_city_night_1", under="⮟"),
    "ሕ": MarkerDef(kind="npc:businessman", under="."),
    "ሖ": MarkerDef(kind="patrol_npc:businessman:h", under="."),
    "ሗ": MarkerDef(kind="raccoon", under="."),
    # City Night 2/3 east-west handoff and Map 3's authored scene.
    "መ": MarkerDef(kind="boundary:modern_city_night_3", under="⮞"),
    "ሙ": MarkerDef(kind="arrival:from_city_night_3", under="."),
    "ሚ": MarkerDef(kind="arrival:from_city_night_2", under="."),
    "ማ": MarkerDef(kind="anchor:modern_city_3_anchor", under="."),
    "ሜ": MarkerDef(kind="boundary:modern_city_night_2", under="⮜"),
    "ም": MarkerDef(kind="npc:homeless_man", under="."),
    "ሞ": MarkerDef(kind="patrol_npc:businessman:v", under="."),
    "ሟ": MarkerDef(kind="traffic_lane:down:0", under="="),
    "ሠ": MarkerDef(kind="traffic_lane:up:1", under="="),
    # City Night 3/4 north-south handoff and Map 4's local checkpoint.
    "ሡ": MarkerDef(kind="boundary:modern_city_night_4", under="⮝"),
    "ሢ": MarkerDef(kind="arrival:from_city_night_4", under="."),
    "ሣ": MarkerDef(kind="arrival:from_city_night_3", under="."),
    "ሤ": MarkerDef(kind="anchor:modern_city_4_anchor", under="."),
    "ሥ": MarkerDef(kind="boundary:modern_city_night_3", under="⮟"),
    # City Night 4/5 west-east handoff and the highway lane field.
    "ሦ": MarkerDef(kind="boundary:modern_city_night_5", under="⮜"),
    "ሧ": MarkerDef(kind="arrival:from_city_night_5", under="."),
    "ረ": MarkerDef(kind="arrival:from_city_night_4", under="."),
    "ሩ": MarkerDef(kind="anchor:modern_city_5_anchor", under="."),
    "ሪ": MarkerDef(kind="boundary:modern_city_night_4", under="⮞"),
    "ራ": MarkerDef(kind="traffic_lane:up:0", under="="),
    "ሬ": MarkerDef(kind="traffic_lane:down:1", under="="),
    "ር": MarkerDef(kind="traffic_lane:up:2", under="="),
    "ሮ": MarkerDef(kind="traffic_lane:down:3", under="="),
    "ሯ": MarkerDef(kind="traffic_lane:down:0", under="="),
    "ሰ": MarkerDef(kind="traffic_lane:up:1", under="="),
    "ሱ": MarkerDef(kind="traffic_lane:down:2", under="="),
    "ሲ": MarkerDef(kind="traffic_lane:up:3", under="="),
    # City Night 5/6 handoff and the final night-city sewer threshold.
    "ሳ": MarkerDef(kind="boundary:modern_city_night_6", under="⮜"),
    "ሴ": MarkerDef(kind="arrival:from_city_night_6", under="."),
    "ስ": MarkerDef(kind="arrival:from_city_night_5", under="."),
    "ሶ": MarkerDef(kind="anchor:modern_city_6_anchor", under="."),
    "ሷ": MarkerDef(kind="boundary:modern_city_night_5", under="⮞"),
    "ሸ": MarkerDef(kind="choice:city_sewer_entrance", under="."),
    "ቓ": MarkerDef(kind="choice:city_sewer_ladder", under="d"),
    # City Sewer 1 arrival, local Ashtray, return, and city-side return point.
    "ሹ": MarkerDef(kind="arrival:from_city_night_6", under="d"),
    "ሺ": MarkerDef(kind="anchor:modern_city_sewer_1_anchor", under="d"),
    "ሻ": MarkerDef(kind="boundary:modern_city_night_6", under="⮟"),
    "ሼ": MarkerDef(kind="arrival:from_city_sewer_1", under="."),
    # City Sewer 2: the culvert on from Sewer 1, its own arrival,
    # Ashtray, and the reciprocal way back.
    "ሽ": MarkerDef(kind="boundary:modern_city_sewer_2", under="⮞"),
    "ሾ": MarkerDef(kind="boundary:modern_city_sewer_1", under="⮜"),
    "ሿ": MarkerDef(kind="arrival:from_city_sewer_1_culvert", under="d"),
    "ቀ": MarkerDef(kind="anchor:modern_city_sewer_2_anchor", under="d"),
    "ቁ": MarkerDef(kind="arrival:from_city_sewer_2", under="d"),
    # City Sewer 3: the flooded hall, its crocodile, and the reserved
    # way on to Sewer 4.
    "ቂ": MarkerDef(kind="arrival:from_city_sewer_2_drop", under="d"),
    "ቃ": MarkerDef(kind="anchor:modern_city_sewer_3_anchor", under="d"),
    "ቄ": MarkerDef(kind="boundary:modern_city_sewer_2", under="⮞"),
    "ቅ": MarkerDef(kind="boundary:modern_city_sewer_4", under="⮜"),
    "ቆ": MarkerDef(kind="crocodile", under="ʓ", allow_solid=False),
    "ቇ": MarkerDef(kind="arrival:from_city_sewer_3", under="d"),
    # City Sewer 4: the last tunnel, and the ladder up into daylight.
    "ቈ": MarkerDef(kind="arrival:from_city_sewer_3_west", under="d"),
    "ቊ": MarkerDef(kind="anchor:modern_city_sewer_4_anchor", under="d"),
    "ቋ": MarkerDef(kind="boundary:modern_city_sewer_3", under="⮞"),
    "ቌ": MarkerDef(kind="arrival:from_city_sewer_4", under="d"),
    # City Day 1: the first daylight map, its Ashtray, the woman in the
    # red dress on her long patrol, and the reserved way on to Day 2.
    "ቍ": MarkerDef(kind="arrival:from_city_sewer_4_ladder", under="."),
    "ቐ": MarkerDef(kind="anchor:modern_city_day_1_anchor", under="."),
    "ቑ": MarkerDef(kind="boundary:modern_city_day_2", under="⮞"),
    "ቒ": MarkerDef(kind="patrol_npc:red_dress_woman:h", under="."),
    # City Day 2: the crossroads, and the reserved way on to Day 3.
    "ቔ": MarkerDef(kind="boundary:modern_city_day_1", under="⮜"),
    "ቕ": MarkerDef(kind="boundary:modern_city_day_3", under="⮟"),
    "ቖ": MarkerDef(kind="arrival:from_city_day_1", under="."),
    "ቘ": MarkerDef(kind="anchor:modern_city_day_2_anchor", under="."),
    "ቚ": MarkerDef(kind="arrival:from_city_day_2", under="."),
    "ቛ": MarkerDef(kind="animal_control", under="."),
    # Police officers hold a fixed post and fire down one authored lane.
    "ቜ": MarkerDef(kind="police:left", under="."),
    "ቝ": MarkerDef(kind="police:right", under="."),
    "በ": MarkerDef(kind="police:up", under="."),
    "ቡ": MarkerDef(kind="police:down", under="."),
    # City Day 3: the street that runs along the open edge.
    "ቢ": MarkerDef(kind="boundary:modern_city_day_2", under="⮝"),
    "ባ": MarkerDef(kind="boundary:modern_city_day_4", under="⮟"),
    "ቤ": MarkerDef(kind="arrival:from_city_day_2", under="."),
    "ብ": MarkerDef(kind="anchor:modern_city_day_3_anchor", under="."),
    "ቦ": MarkerDef(kind="arrival:from_city_day_3", under="."),
    # City Day 4: the square whose floor gave way.
    "ቨ": MarkerDef(kind="boundary:modern_city_day_3", under="⮝"),
    "ቩ": MarkerDef(kind="boundary:modern_city_day_5", under="⮞"),
    "ቪ": MarkerDef(kind="arrival:from_city_day_3", under="."),
    "ቫ": MarkerDef(kind="anchor:modern_city_day_4_anchor", under="."),
    "ቬ": MarkerDef(kind="arrival:from_city_day_4", under="."),
    # City Day 5: the overpass, and the two spans that dropped out.
    "ቭ": MarkerDef(kind="boundary:modern_city_day_4", under="⮝"),
    "ቮ": MarkerDef(kind="boundary:modern_city_day_6", under="⮟"),
    "ቯ": MarkerDef(kind="arrival:from_city_day_4", under="."),
    "ተ": MarkerDef(kind="anchor:modern_city_day_5_anchor", under="."),
    "ቱ": MarkerDef(kind="arrival:from_city_day_5", under="."),
    # City Day 6: the collision. Its cast stands in the Chult patch, and
    # the portal trigger sits at the far-southwest oval's threshold.
    "ቲ": MarkerDef(kind="boundary:modern_city_day_5", under="⮝"),
    "ታ": MarkerDef(kind="arrival:from_city_day_5", under="."),
    "ቴ": MarkerDef(kind="anchor:modern_city_day_6_anchor", under="."),
    "ት": MarkerDef(kind="choice:doug_fir_portal", under="."),
    "ቶ": MarkerDef(kind="massive_dinosaur", under="ᵹ"),
    "ቷ": MarkerDef(kind="npc:prone_businessman", under="ᵹ"),
    "ቸ": MarkerDef(kind="raptor", under="ᵹ"),
    "ቹ": MarkerDef(kind="arrival:from_city_day_6", under="."),
    "ቺ": MarkerDef(kind="police:spin", under="."),
    "ች": MarkerDef(kind="raptor:chasing", under="."),
    "ቻ": MarkerDef(kind="patrol_npc:businessman:h:flee", under="."),
    "ቼ": MarkerDef(kind="patrol_npc:businessman:v:flee", under="ᵹ"),
    # Mushroom Underways: a quiet map, so only a checkpoint, the two
    # arrivals, and the reserved Map 12 edge.
    "შ": MarkerDef(kind="arrival:from_feywild_10", under="'"),
    "ჩ": MarkerDef(kind="anchor:feywild_11_anchor", under="'"),
    "ც": MarkerDef(kind="boundary:feywild_12", under="→"),
    "ძ": MarkerDef(kind="arrival:from_feywild_12", under="'"),
    # Displacer Meadow: one massive stalker, the meadow's checkpoint, and
    # the reserved Map 11 edge.
    "ს": MarkerDef(kind="arrival:from_feywild_9", under="'"),
    "ტ": MarkerDef(kind="anchor:feywild_10_anchor", under="'"),
    "უ": MarkerDef(kind="boundary:feywild_11", under="→"),
    "ფ": MarkerDef(kind="arrival:from_feywild_11", under="'"),
    "ქ": MarkerDef(kind="displacer_beast", under="."),
    "ღ": MarkerDef(kind="thorn_mite", under="."),
    # Shifting Hedge: four reciprocal flower groups. Each opens one
    # hedge doorway and closes another, so every scratch is a trade
    # rather than a one-way unlock, and scratching again undoes it.
    "ა": MarkerDef(kind="flower_switch:hedge_west", under="."),
    "ბ": MarkerDef(
        kind="flower_open:hedge_west", under="#", allow_solid=True
    ),
    "გ": MarkerDef(kind="flower_close:hedge_west", under="'"),
    "დ": MarkerDef(kind="flower_switch:hedge_north", under="."),
    "ე": MarkerDef(
        kind="flower_open:hedge_north", under="#", allow_solid=True
    ),
    "ვ": MarkerDef(kind="flower_close:hedge_north", under="'"),
    "ზ": MarkerDef(kind="flower_switch:hedge_east", under="."),
    "თ": MarkerDef(
        kind="flower_open:hedge_east", under="#", allow_solid=True
    ),
    "ი": MarkerDef(kind="flower_close:hedge_east", under="'"),
    "კ": MarkerDef(kind="flower_switch:hedge_south", under="."),
    "ლ": MarkerDef(
        kind="flower_open:hedge_south", under="#", allow_solid=True
    ),
    "მ": MarkerDef(kind="flower_close:hedge_south", under="'"),
    # Shifting Hedge arrival, Ashtray, and the reserved Map 10 edge.
    "ნ": MarkerDef(kind="arrival:from_feywild_8", under="'"),
    "ო": MarkerDef(kind="anchor:feywild_9_anchor", under="."),
    "პ": MarkerDef(kind="boundary:feywild_10", under="→"),
    "ჟ": MarkerDef(kind="arrival:from_feywild_10", under="'"),
    "რ": MarkerDef(kind="thorn_mite", under="."),
    # Redcap Warrens: the camp's pursuers, its mite nests, one checkpoint,
    # and the future Shifting Hedge edge.
    "բ": MarkerDef(kind="arrival:from_feywild_7", under="'"),
    "գ": MarkerDef(kind="anchor:feywild_8_anchor", under="."),
    "դ": MarkerDef(kind="boundary:feywild_9", under="→"),
    "ե": MarkerDef(kind="arrival:from_feywild_9", under="'"),
    "զ": MarkerDef(kind="redcap", under="."),
    "է": MarkerDef(kind="thorn_mite", under="."),
    # Needle Garden: rooted cardinal launchers, one checkpoint, and the
    # future Moonmoth Fen handoff.
    "Վ": MarkerDef(
        kind="spitting_orchid:down", under="✿", allow_solid=True
    ),
    "Տ": MarkerDef(
        kind="spitting_orchid:up", under="✿", allow_solid=True
    ),
    "Ր": MarkerDef(
        kind="spitting_orchid:left", under="✿", allow_solid=True
    ),
    "Ց": MarkerDef(
        kind="spitting_orchid:right", under="✿", allow_solid=True
    ),
    "Ւ": MarkerDef(kind="arrival:from_feywild_5", under="."),
    "Փ": MarkerDef(kind="anchor:feywild_6_anchor", under="."),
    "Ք": MarkerDef(kind="boundary:feywild_7", under="→"),
    "Օ": MarkerDef(kind="arrival:from_feywild_7", under="."),
    # Feywild map 7, the Moonmoth Fen, and its lantern moths.
    "Ֆ": MarkerDef(kind="arrival:from_feywild_6", under="'"),
    "ՙ": MarkerDef(kind="anchor:feywild_7_anchor", under="."),
    "ֈ": MarkerDef(kind="boundary:feywild_8", under="→"),
    "ֆ": MarkerDef(kind="arrival:from_feywild_8", under=","),
    # Moths fly, so they haunt the open water itself: allow_solid keeps
    # the deep channel beneath them untouched.
    "֊": MarkerDef(kind="lantern_moth:h", under="~", allow_solid=True),
    "Ա": MarkerDef(kind="lantern_moth:v", under="~", allow_solid=True),
    # Phase 12: cutscene arrival and the exterior's one physical Ashtray.
    "ኀ": MarkerDef(kind="arrival:from_doug_fir", under="⌇"),
    "ኁ": MarkerDef(kind="anchor:tahuya_exterior_anchor", under="ᶠ"),
    # The sole cabin threshold stays spatially reversible. Runtime arrivals
    # sit one tile clear of each door so entering never immediately bounces
    # Chuck back across the same threshold.
    "ኂ": MarkerDef(kind="arrival:from_cabin_front", under="▣"),
    "ኄ": MarkerDef(kind="arrival:from_front_door", under="Ŀ"),
    "ኅ": MarkerDef(kind="choice:cabin_table_portal", under="Ŀ"),
    # The same question asked from the hardwood on the table's south
    # side. A separate glyph only because the floor differs there.
    "ኇ": MarkerDef(kind="choice:cabin_table_portal", under="Ħ"),
    "ኆ": MarkerDef(kind="anchor:tahuya_interior_anchor", under="Ŀ"),
    # Four seated Phase 12 light entities. Their markers sit inside the
    # furniture footprints; solid under-tiles preserve the authored collision.
    "₁": MarkerDef(
        kind="cabin_light:cabin_entity_big_couch:"
             "cabin_entity_big_couch_spoken:0",
        under="∎", allow_solid=True,
    ),
    "₂": MarkerDef(
        kind="cabin_light:cabin_entity_couch:"
             "cabin_entity_couch_spoken:2",
        under="∎", allow_solid=True,
    ),
    "₃": MarkerDef(
        kind="cabin_light:cabin_entity_chair_north:"
             "cabin_entity_chair_north_spoken:4:west",
        under="∎", allow_solid=True,
    ),
    "₄": MarkerDef(
        kind="cabin_light:cabin_entity_chair_south:"
             "cabin_entity_chair_south_spoken:6:west",
        under="∎", allow_solid=True,
    ),
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
        # Connected pieces of overhead art (one market awning, one palm
        # canopy), built on first use; and faded copies of overhead tiles.
        self._overhead_regions: dict[tuple[int, int], int] | None = None
        self._thinned_overhead: dict[tuple[str, int, int], object] = {}

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

    def has_terrain(self, wanted) -> bool:
        """True if any tile on the map uses one of these characters.

        Lets a scene ask what a map is made of rather than being told:
        the snow weather turns itself on for any map with snow in it,
        so a new frozen fragment needs no entry in any list.
        """
        return any(char in wanted for row in self._grid for char in row)

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

    def set_terrain(self, col: int, row: int, char: str) -> str:
        """Swap one tile's terrain at runtime, returning the old char.

        Used by scripted world changes (the sanctum's Astral breach):
        the caller keeps the returned char to restore the tile when the
        room resets. Only known terrain may be written — an unknown
        char here is always a logic mistake, same as in a map file.
        Map reload re-parses the file, so mutations reset naturally.
        """
        if char not in TILE_DEFS:
            raise ValueError(f"Unknown terrain {char!r} for set_terrain")
        line = self._grid[row]
        old = line[col]
        self._grid[row] = line[:col] + char + line[col + 1:]
        return old

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
                    time_s: float = 0.0, *,
                    include_chars: frozenset[str] | None = None,
                    exclude_chars: frozenset[str] | None = None) -> None:
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
                if (include_chars is not None
                        and ground_char not in include_chars):
                    continue
                if exclude_chars is not None and ground_char in exclude_chars:
                    continue
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

    def overhead_regions(self) -> dict[tuple[int, int], int]:
        """Label every overhead tile with the connected canopy it is part of.

        An awning fades as one piece of canvas. Fading only the tiles
        Chuck is touching drew a hole the shape of a rat in the middle of
        it, which reads as a cloth with a rat-shaped tear rather than as
        a thing he is underneath.
        """
        if self._overhead_regions is None:
            from collections import deque

            cells = {
                (col, row)
                for row, line in enumerate(self._grid)
                for col, char in enumerate(line)
                if char in TILE_DEFS and TILE_DEFS[char].overhead
            }
            labels: dict[tuple[int, int], int] = {}
            label = 0
            for cell in sorted(cells, key=lambda c: (c[1], c[0])):
                if cell in labels:
                    continue
                labels[cell] = label
                queue = deque([cell])
                while queue:
                    col, row = queue.popleft()
                    for spot in ((col + 1, row), (col - 1, row),
                                 (col, row + 1), (col, row - 1)):
                        if spot in cells and spot not in labels:
                            labels[spot] = label
                            queue.append(spot)
                label += 1
            self._overhead_regions = labels
        return self._overhead_regions

    def overhead_regions_over(self, rect) -> set[int]:
        """Which canopies cover any part of a world-space rectangle."""
        regions = self.overhead_regions()
        if not regions:
            return set()
        ts = config.TILE_SIZE
        found = set()
        for row in range(int(rect.top // ts), int((rect.bottom - 1) // ts) + 1):
            for col in range(int(rect.left // ts),
                             int((rect.right - 1) // ts) + 1):
                label = regions.get((col, row))
                if label is not None:
                    found.add(label)
        return found

    def _thinned_overhead_tile(self, char: str, index: int, level: int,
                               art) -> object:
        key = (char, index, level)
        tile = self._thinned_overhead.get(key)
        if tile is None:
            import pygame  # local: keeps parsing/collision pygame-free

            from src.entities.prop import SEE_THROUGH_ALPHA, SEE_THROUGH_STEPS

            tile = pygame.Surface(art.get_size(), pygame.SRCALPHA)
            tile.blit(art, (0, 0))
            keep = round(255 - (255 - SEE_THROUGH_ALPHA) * level
                         / SEE_THROUGH_STEPS)
            tile.fill((255, 255, 255, keep),
                      special_flags=pygame.BLEND_RGBA_MULT)
            self._thinned_overhead[key] = tile
        return tile

    def draw_overhead(self, surface, camera_offset: tuple[int, int],
                      time_s: float = 0.0,
                      veils: dict[int, float] | None = None) -> None:
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
        regions = self.overhead_regions() if veils else None
        if veils:
            from src.entities.prop import SEE_THROUGH_STEPS
        for row_i in range(row0, row1):
            grid_row = self._grid[row_i]
            for col_i in range(col0, col1):
                char = grid_row[col_i]
                art = self._overhead_art.get(char)
                if art is not None:
                    name = overhead_to_terrain[char]
                    variants, frames = self._tileset_info[name]
                    idx = art_index(col_i, row_i, variants, frames, time_s)
                    tile = art[idx]
                    if regions is not None:
                        veil = veils.get(regions.get((col_i, row_i)), 0.0)
                        if veil > 0.0:
                            tile = self._thinned_overhead_tile(
                                char, idx,
                                max(1, round(veil * SEE_THROUGH_STEPS)),
                                art[idx])
                    surface.blit(tile, (col_i * ts - ox, row_i * ts - oy))
