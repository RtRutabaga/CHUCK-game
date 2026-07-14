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
TUTORIAL_MAPS = {"waterdeep_docks", "sewer"}
TUTORIAL_HINT_TOP = 8       # pixels from the top of the 320x180 view
HINT_INTERACT = "Press E to interact"
HINT_JUMP = "Press SPACE to jump"
HINT_SCRATCH = "Press F to scratch"

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
