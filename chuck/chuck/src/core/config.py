"""Central configuration for CHUCK.

Every tunable constant lives here so future sessions never hunt through
gameplay code to change a number. Group related constants together and
keep this file free of logic.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = PROJECT_ROOT / "data"

SPRITES_DIR = ASSETS_DIR / "sprites"
TILESETS_DIR = ASSETS_DIR / "tilesets"
MAPS_DIR = ASSETS_DIR / "maps"
MUSIC_DIR = ASSETS_DIR / "audio" / "music"
SFX_DIR = ASSETS_DIR / "audio" / "sfx"
FONTS_DIR = ASSETS_DIR / "fonts"
CHOICE_DIR = DATA_DIR / "choices"
DIALOGUE_DIR = DATA_DIR / "dialogue"

# ---------------------------------------------------------------------------
# Window / rendering
# ---------------------------------------------------------------------------
GAME_TITLE = "CHUCK"

# Temporary development menu. Set False for a player-facing final build; the
# checkpoint registry and real save system remain unchanged.
ENABLE_DEV_CHECKPOINT_SELECTOR = True

# Native (internal) resolution. All pixel art is authored at this size and
# then integer-scaled up to the window, keeping the 16-bit look crisp.
NATIVE_WIDTH = 320
NATIVE_HEIGHT = 180

# How many times the native surface is scaled for the actual window.
WINDOW_SCALE = 4
# Delta-time ceiling: vsync misses, window drags, or tab-outs produce
# dt spikes; clamping keeps one bad frame from lurching the simulation
# (most visibly the camera's settle after Chuck stops).
MAX_DT = 1.0 / 30.0
WINDOW_WIDTH = NATIVE_WIDTH * WINDOW_SCALE
WINDOW_HEIGHT = NATIVE_HEIGHT * WINDOW_SCALE

FPS = 60

# ---------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------
TILE_SIZE = 16  # pixels; the world grid everything snaps to

# ---------------------------------------------------------------------------
# Colors (RGB)
# ---------------------------------------------------------------------------
COLOR_BLACK = (0, 0, 0)

# Placeholder colors used until real art exists.
COLOR_FLOOR_PLACEHOLDER = (52, 46, 52)    # dark generic floor
COLOR_SOLID_PLACEHOLDER = (108, 88, 68)   # crate/wall brown
COLOR_CHUCK_PLACEHOLDER = (128, 80, 168)  # jacket purple
COLOR_TAVERN_WALL = (166, 132, 86)   # tan brick fallback
COLOR_TAVERN_ROOF = (62, 60, 70)     # slate fallback
COLOR_STONE_PLACEHOLDER = (88, 84, 88)    # quay stone
COLOR_PLANK_PLACEHOLDER = (150, 112, 74)  # dock planks
COLOR_WATER_PLACEHOLDER = (36, 52, 84)    # harbor water
COLOR_BARREL_PLACEHOLDER = (134, 88, 50)  # barrels (incl. Bobert's)

# The sewer: placeholder terrain colors (a tileset art pass comes later,
# just as the docks layout in session 3 preceded the docks tileset in
# session 12). Damp, colorless, a step down out of the daylit docks.
COLOR_SEWER_DIRT = (74, 62, 48)      # packed earth floor
COLOR_SEWER_MUD = (58, 50, 38)       # wet muck (walkable, darker dirt)
COLOR_SEWER_CHANNEL = (46, 56, 46)   # murky drainage water (solid)

# TODO: Define the warm Waterdeep-at-sunset palette once art direction
#       work begins (Game Bible: ALttP / Link's Awakening / Chrono Trigger).

# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
PLAYER_SPEED = 80.0  # pixels/second — tune until walking feels good
# Hitbox in pixels; deliberately smaller than a 16px tile because Chuck
# is one foot tall and should slip through rat-sized gaps. The hitbox is
# his footprint; the sprite is taller and anchored to its bottom edge.
PLAYER_HITBOX_W = 10
PLAYER_HITBOX_H = 8
JUMP_DURATION = 0.36
JUMP_SPEED = 104.0
JUMP_HEIGHT = 6
FALL_DURATION = 0.65
CLIMB_OUT_DURATION = 0.65
CLIMB_OUT_LIFT = 2
AREA_FADE_DURATION = 0.75

# Sewer layout landmarks shared by scene tutorials and map tests. Keeping
# these beside the movement rules makes geometry changes fail loudly instead
# of leaving prompts behind at obsolete coordinates.
SEWER_JUMP_ROW = 30
SEWER_RAT_COL = 32
SEWER_RAT_ROWS = (34, 35, 36)
SEWER_JUMP_HINT_BOUNDS = (24, 39, 27, 30)  # left, right, top, bottom
SEWER_SCRATCH_HINT_BOUNDS = (24, 39, 31, 36)

# Scratch: deliberately brief and simple. The forward box extends a little
# beyond Chuck's footprint so attacking never demands pixel-perfect contact.
SCRATCH_DURATION = 0.18
SCRATCH_REACH = 14
BREAKABLE_GRASS_DURATION = 0.42
GRASS_SCRATCH_HINT_MAPS = {"waterdeep_docks", "sewer"}
GRASS_SCRATCH_HINT_REACH = TILE_SIZE * 2

# Chuck's sprite sheet (see tools/generate_chuck_sprites.py).
CHUCK_SHEET = "chuck/chuck.png"
CHUCK_FRAME_W = 12
CHUCK_FRAME_H = 14
# Seconds per walk-cycle frame.
ANIM_WALK_FRAME_TIME = 0.12

# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------
# Higher = snappier follow; lower = floatier. Frame-rate independent.
CAMERA_LERP_RATE = 6.0

# ---------------------------------------------------------------------------
# Sanity (Chuck's "health" — see Game Bible)
# ---------------------------------------------------------------------------
SANITY_MAX = 100
# Chuck wakes up at 60%. He is not a morning rat. (Also makes cigarette
# pickups visible on the meter before hazards exist to drain it.)
SANITY_START = 60
CIGARETTE_SANITY_RESTORE = 25  # TODO: tune during Phase One playtesting
# A carton (found by breaking a temple urn or pantry jar) counts as
# exactly this many cigarettes: sanity clamps at full, and the
# overall-game cigarette ledger (session 128) banks the full 20.
CARTON_CIGARETTE_COUNT = 20

# Seconds of invulnerability after taking a hit, so one cat brush
# doesn't drain everything in a single overlap.
HURT_COOLDOWN = 0.8

# ---------------------------------------------------------------------------
# Hazards
# ---------------------------------------------------------------------------
CAT_SHEET = "hazards/cat.png"
CAT_FRAME_W = 18
CAT_FRAME_H = 12
CAT_SPEED = 40.0            # slower than Chuck; menace, not a chase
CAT_SANITY_DAMAGE = 20
# Cat footprint (16x8): wide, low, and much bigger than Chuck's 10x8.
CAT_HITBOX_W = 16
CAT_HITBOX_H = 8

# Ordinary sewer rats are visibly smaller than Chuck's 12x14 sprite.
RAT_SHEET = "hazards/rat.png"
RAT_FRAME_W = 10
RAT_FRAME_H = 8
RAT_HITBOX_W = 8
RAT_HITBOX_H = 6
RAT_SANITY_DAMAGE = 10
RAT_PATROL_SPEED = 12.0
RAT_PATROL_RANGE = 6.0

# Chult undead share the established human footprint and sprite scale. Both
# are deliberately durable; their low speeds leave room to evade them.
UNDEAD_FRAME_W = 16
UNDEAD_FRAME_H = 30
ZOMBIE_SPEED = 18.0
ZOMBIE_SANITY_DAMAGE = 20
ZOMBIE_SCRATCHES = 8
SKELETON_SPEED = 25.0
SKELETON_SANITY_DAMAGE = 15
SKELETON_SCRATCHES = 6
UNDEAD_NOTICE_RANGE = 112.0
THORN_SANITY_DAMAGE = 10

# Temple wall launchers fire narrow, readable projectiles across trap corridors.
# Darts outrun Chuck but their authored spacing and cadence leave timing windows.
DART_SPEED = 112.0
DART_SANITY_DAMAGE = 15
DART_INTERVAL = 1.75
DART_HITBOX_SHORT = 2
DART_HITBOX_LONG = 7

# The sanctum battle in motion: the combatants' attacks are timed hazards
# Chuck must dodge, not aimed at him. Rays sweep the three adventurers'
# lanes in a fixed cycle and dissipate at range, so the east half of the
# hall stays survivable; arrows and bolts fly west at the beholder; the
# fighter's slash pulses where the skeletons press him.
BATTLE_RAY_SPEED = 88.0
BATTLE_RAY_SANITY_DAMAGE = 20
BATTLE_RAY_INTERVAL = 2.1
BATTLE_RAY_RANGE = 320.0
BATTLE_RAY_HITBOX_LONG = 12
BATTLE_RAY_HITBOX_SHORT = 3
BATTLE_ARROW_SPEED = 168.0
BATTLE_ARROW_SANITY_DAMAGE = 10
BATTLE_ARROW_INTERVAL = 1.9
BATTLE_BOLT_SPEED = 72.0
BATTLE_BOLT_SANITY_DAMAGE = 15
BATTLE_BOLT_INTERVAL = 2.6
BATTLE_SLASH_INTERVAL = 1.5
BATTLE_SLASH_ACTIVE = 0.22
BATTLE_SLASH_SANITY_DAMAGE = 12
BATTLE_ATTACK_FLASH = 0.18

# The Astral breach: once Chuck walks into sight of the battle, the
# Astral Sea breaks through the floor behind him in a two-tile-thick
# north-south band — unjumpable, uncrossable by enemies, lethal to walk
# into — sealing the hall so the battle cannot be walked away from.
# Death resets the room, so the seal restores with everything else.
BREACH_TRIGGER_COL = 28
BREACH_COLS = (32, 33)
BREACH_INSTANT_RADIUS = 7
BREACH_STEP = 0.06
BREACH_FLASH = 0.35

# Temple snakes are a brief pressure-release encounter: quick enough to make
# the open chamber lively, but deliberately defeated by a single scratch.
SNAKE_FRAME_W = 18
SNAKE_FRAME_H = 10
SNAKE_HITBOX_W = 14
SNAKE_HITBOX_H = 6
SNAKE_SPEED = 32.0
SNAKE_NOTICE_RANGE = 96.0
SNAKE_SANITY_DAMAGE = 10

# Chult raptors are visibly larger and more immediately dangerous than the
# undead, but remain slower than Chuck so open-space evasion is reliable.
RAPTOR_FRAME_W = 44
RAPTOR_FRAME_H = 30
RAPTOR_HITBOX_W = 30
RAPTOR_HITBOX_H = 15
RAPTOR_SPEED = 68.0
RAPTOR_NOTICE_RANGE = 152.0
RAPTOR_SANITY_DAMAGE = 25
RAPTOR_SCRATCHES = 10
RAPTOR_FRAME_DURATION = 0.13

# One enormous dinosaur occupies the northern Map 2 clearing. It is slower
# than even a zombie; its danger is its screen presence and heavy contact.
DINOSAUR_FRAME_W = 72
DINOSAUR_FRAME_H = 60
DINOSAUR_HITBOX_W = 48
DINOSAUR_HITBOX_H = 24
DINOSAUR_SPEED = 14.0
DINOSAUR_NOTICE_RANGE = 128.0
DINOSAUR_SANITY_DAMAGE = 40
DINOSAUR_SCRATCHES = 20
DINOSAUR_FRAME_DURATION = 0.30

# ---------------------------------------------------------------------------
# Astral Anchor respawn (Game Bible: quiet, quick, never punishing)
# ---------------------------------------------------------------------------
RESPAWN_FADE_OUT = 0.5   # world dims to the Astral dark
RESPAWN_HOLD = 0.7       # a breath among the stars
RESPAWN_FADE_IN = 0.5    # and back
COLOR_ASTRAL = (14, 16, 38)
COLOR_STAR = (228, 232, 248)
COLOR_ANCHOR_DIM = (96, 110, 150)
COLOR_ANCHOR_LIT = (170, 200, 255)

# ---------------------------------------------------------------------------
# NPCs
# ---------------------------------------------------------------------------
NPC_FRAME_W = 16
NPC_FRAME_H = 30   # humans tower over a one-foot rat; that's the point
NPC_HITBOX_W = 12
NPC_HITBOX_H = 8
UNDEAD_HITBOX_W = NPC_HITBOX_W
UNDEAD_HITBOX_H = NPC_HITBOX_H

# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------
AUDIO_MUSIC_VOLUME = 0.6   # ambience / music stream
AUDIO_SFX_VOLUME = 0.8
MUSIC_FILE = "waterdeep_docks.wav"
FOOTSTEP_INTERVAL = 0.28   # seconds between steps while walking

# ---------------------------------------------------------------------------
# Dialogue
# ---------------------------------------------------------------------------
DIALOGUE_CPS = 40           # typewriter speed, characters per second
# Text renders with the hand-drawn pixel font (assets/fonts/, built by
# tools/generate_font.py); its glyphs are baked in COLOR_DIALOGUE_TEXT.
# ---------------------------------------------------------------------------
# Tutorial hints (TEMPORARY — Waterdeep and the sewer only; see
# src/ui/tutorial_hint.py. Not instructional UI for the whole game.)
# ---------------------------------------------------------------------------
TUTORIAL_MAPS = {"waterdeep_docks", "sewer", "waterdeep_pantry"}
TUTORIAL_HINT_TOP = 8       # pixels from the top of the 320x180 view
HINT_INTERACT = "Press E to interact"
HINT_JUMP = "Press SPACE to jump"
HINT_SCRATCH = "Press F to scratch"
HINT_ANCHOR = "Ashtrays save your progress"

# Choice options drawn inside the dialogue panel.
CHOICE_LEFT = 8             # px indent inside the panel's text area
CHOICE_TOP_OFFSET = 18      # px below the panel's top edge
CHOICE_LINE_GAP = 3

COLOR_DIALOGUE_PANEL = (24, 22, 30)
COLOR_DIALOGUE_BORDER = (120, 116, 130)
COLOR_DIALOGUE_TEXT = (232, 230, 236)

# The HUD sanity meter is a lit cigarette burning down (see src/ui/hud.py).
COLOR_CIG_PAPER = (236, 236, 228)
COLOR_CIG_EMBER = (242, 146, 66)
COLOR_CIG_FILTER = (214, 168, 110)
COLOR_CIG_ASH = (104, 102, 110)

# TODO: Add input binding constants when the input system is implemented.
# TODO: Add audio volume defaults when the audio system is implemented.
