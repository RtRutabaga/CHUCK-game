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
FEYWILD_POLLEN_SPEED_MULTIPLIER = 0.48
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

# Feywild reactive flowers visibly pulse before atomically exchanging one
# authored vegetation route for another. The short aftermath flash makes the
# changed tiles legible without a tutorial panel.
REACTIVE_FLOWER_CHANGE_DELAY = 0.45
REACTIVE_FLOWER_FLASH_DURATION = 0.48

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
HALFLING_LEAF_CIGARETTES = 40

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
# Hold rats use the temple snakes' notice-and-pursue pressure while retaining
# their ordinary one-scratch durability and contact damage.
HOLD_RAT_CHASE_SPEED = 32.0
HOLD_RAT_NOTICE_RANGE = 96.0

# City raccoons occupy the middle ground between one-hit rats and durable
# Chultan undead: quick enough to pressure Chuck, but still a brief fight.
RACCOON_FRAME_W = 20
RACCOON_FRAME_H = 14
RACCOON_HITBOX_W = 14
RACCOON_HITBOX_H = 8
RACCOON_SPEED = 30.0
RACCOON_SANITY_DAMAGE = 15
RACCOON_SCRATCHES = 3
RACCOON_NOTICE_RANGE = 104.0

# A walking businessperson moves slowly along one authored sidewalk segment.
CITY_PEDESTRIAN_SPEED = 12.0
CITY_PEDESTRIAN_RANGE = 42.0
# Pedestrians who walk further than the default beat. The woman in the
# red dress covers most of a block, which -- with the dress -- is what
# makes her readable as a distinct figure rather than another commuter.
PEDESTRIAN_PATROL_RANGES = {
    "red_dress_woman": 168.0,
}

# Animal Control officers. Durability and contact match a Chult zombie --
# they are the same role -- and the net is what makes them their own
# thing: a close-range hold that drains Sanity to zero over four seconds
# and then hands off to the ordinary depletion the whole game uses.
ANIMAL_CONTROL_SPEED = 21.0
ANIMAL_CONTROL_SANITY_DAMAGE = 20
ANIMAL_CONTROL_SCRATCHES = 8
NET_RANGE = 26.0
NET_WIND_UP_SECONDS = 0.55
NET_CAPTURE_SECONDS = 4.0

# Police officers: stationary ranged hazards to route around, never a
# cover-shooter. They reuse the spined devil's projectile wholesale --
# bullets simply travel faster and are stopped by the same solid
# geometry -- and add the one thing the devil lacks: a visible aim
# before every shot, so a lane can always be read before it is fired.
POLICE_HITBOX_W = 12
POLICE_HITBOX_H = 10
POLICE_FRAME_W = 16
POLICE_FRAME_H = 30
POLICE_INTERVAL = 2.4
POLICE_AIM_SECONDS = 0.7
POLICE_CONTACT_DAMAGE = 15
BULLET_SPEED = 210.0
BULLET_SANITY_DAMAGE = 18
BULLET_HITBOX_LONG = 6
BULLET_HITBOX_SHORT = 3

# Chult undead share the established human footprint and sprite scale. Both
# are deliberately durable; their low speeds leave room to evade them.
UNDEAD_FRAME_W = 16
UNDEAD_FRAME_H = 30
ZOMBIE_SPEED = 18.0
ZOMBIE_SANITY_DAMAGE = 20
ZOMBIE_SCRATCHES = 8

# The urban sewer's one large predator. It fills the zombie's role -- as
# durable, as dangerous on contact -- but it is markedly faster, because a
# crocodile in a straight tunnel should be something Chuck runs from rather
# than something he backs away from.
CROCODILE_SPEED = 27.0
CROCODILE_SANITY_DAMAGE = 22
CROCODILE_SCRATCHES = 9
SKELETON_SPEED = 25.0
SKELETON_SANITY_DAMAGE = 15
SKELETON_SCRATCHES = 6
# Phlegethos lemures (Phase 8) reuse the undead lifecycle exactly: the
# slowest, most durable shamblers yet -- a wall of wretched flesh that is
# far better walked around than fought.
LEMURE_SPEED = 15.0
LEMURE_SANITY_DAMAGE = 18
LEMURE_SCRATCHES = 10

# Spined devils never move: they perch and flick burning tail spines down
# an authored lane, exactly as the temple's wall launchers throw darts.
# Closing to melee is fatal, so they are a pure ranged dodge problem.
SPINED_DEVIL_FRAME_W = 16
SPINED_DEVIL_FRAME_H = 22
SPINED_DEVIL_HITBOX_W = 12
SPINED_DEVIL_HITBOX_H = 10
SPINED_DEVIL_INTERVAL = 2.0
SPINED_DEVIL_CONTACT_DAMAGE = 15
SPINE_SPEED = 96.0
SPINE_SANITY_DAMAGE = 18
SPINE_HITBOX_LONG = 8
SPINE_HITBOX_SHORT = 3

# Flameskulls weave fast and erratically around a fixed haunt, like bees.
# They cannot be cleared -- they are moving hazards to be timed, and they
# drift over lava as happily as over stone.
FLAMESKULL_FRAME_W = 14
FLAMESKULL_FRAME_H = 14
FLAMESKULL_HITBOX_W = 10
FLAMESKULL_HITBOX_H = 10
FLAMESKULL_SPEED = 62.0
FLAMESKULL_RANGE = 40.0
FLAMESKULL_WEAVE = 18.0
FLAMESKULL_SANITY_DAMAGE = 16
UNDEAD_NOTICE_RANGE = 112.0
THORN_SANITY_DAMAGE = 10

# Toxic sewer sludge is the modern city's single new terrain hazard. It is
# deliberately built from two effects the game already has -- Chult's thorn
# damage and the Feywild pollen slowdown -- rather than a sewer-only rule.
# It bites harder than thorns and drags harder than pollen, so a sludge
# channel reads as something to cross deliberately, never to stand in.
SLUDGE_SANITY_DAMAGE = 14
SLUDGE_SPEED_MULTIPLIER = 0.42

# Feywild redcaps are gnome-sized pursuit enemies: sturdier than Chuck and
# quick enough to pressure an exposed route, but unable to enter his narrow
# root passages.
REDCAP_FRAME_W = 20
REDCAP_FRAME_H = 24
REDCAP_HITBOX_W = 14
REDCAP_HITBOX_H = 9
REDCAP_SPEED = 27.0
REDCAP_NOTICE_RANGE = 112.0
REDCAP_SANITY_DAMAGE = 18
REDCAP_SCRATCHES = 6
REDCAP_FRAME_DURATION = 0.22

# Feywild spitting orchids are rooted cardinal launchers. Their slower seeds
# and pronounced wind-up leave a deliberate timing window in authored lanes.
ORCHID_FRAME_W = 20
ORCHID_FRAME_H = 24
ORCHID_HITBOX_W = 12
ORCHID_HITBOX_H = 8
ORCHID_SHOT_INTERVAL = 2.4
ORCHID_WINDUP_TIME = 0.55
ORCHID_FLASH_TIME = 0.16
ORCHID_SEED_SPEED = 84.0
ORCHID_SEED_SANITY_DAMAGE = 14
ORCHID_SEED_HITBOX_LONG = 7
ORCHID_SEED_HITBOX_SHORT = 3

# Temple wall launchers fire narrow, readable projectiles across trap corridors.
# Darts outrun Chuck but their authored spacing and cadence leave timing windows.
DART_SPEED = 112.0
DART_SANITY_DAMAGE = 15
DART_INTERVAL = 1.75
DART_HITBOX_SHORT = 2
DART_HITBOX_LONG = 7

# The sanctum battle in motion: a desperate, overwhelming fight Chuck
# only has to survive. Rays sweep the adventurers' lanes; the ranger
# spins loosing a rotating spray of arrows in every direction; the
# wizard hurls fans of bolts; and the beholder occasionally charges a
# screen-shaking cone of force east across the hall. None of it is
# aimed at Chuck, but the air is thick with stray death.
BATTLE_RAY_SPEED = 92.0
BATTLE_RAY_SANITY_DAMAGE = 20
BATTLE_RAY_INTERVAL = 1.4
BATTLE_RAY_RANGE = 320.0
BATTLE_RAY_HITBOX_LONG = 12
BATTLE_RAY_HITBOX_SHORT = 3

# The spinning archer: a fan of arrows per beat, the aim whirling around
# the compass so arrows spray the whole room over a couple of seconds.
BATTLE_ARROW_SPEED = 150.0
BATTLE_ARROW_SANITY_DAMAGE = 10
BATTLE_ARROW_INTERVAL = 0.3
BATTLE_ARROW_FAN = 2               # arrows loosed per beat
BATTLE_ARROW_FAN_SPREAD = 0.42     # radians between fan arrows
BATTLE_ARROW_SPIN_STEP = 0.85      # radians the aim whirls each beat
BATTLE_RANGER_SPIN_SPEED = 8.0     # visual body spin, rad/s

# The wizard's magic: a westward fan of bolts at the beholder, often.
BATTLE_BOLT_SPEED = 76.0
BATTLE_BOLT_SANITY_DAMAGE = 15
BATTLE_BOLT_INTERVAL = 1.05
BATTLE_BOLT_FAN = 3
BATTLE_BOLT_FAN_SPREAD = 0.34      # radians between fan bolts

# The beholder's cone: an occasional charged blast of force east across
# the hall — a bright telegraph, then a wide lethal wedge that shakes
# the screen and booms. Chuck must be clear of the wedge when it fires.
BATTLE_CONE_INTERVAL = 6.0
BATTLE_CONE_CHARGE = 0.9           # telegraph before the blast lands
BATTLE_CONE_ACTIVE = 0.4           # the dangerous window
BATTLE_CONE_HALF_ANGLE = 0.5       # ~29 degrees to each side
BATTLE_CONE_RANGE = 216.0          # leaves an eastern refuge to flee to
BATTLE_CONE_SANITY_DAMAGE = 30
BATTLE_CONE_SHAKE = 6.0            # screen-shake impulse on detonation
BATTLE_CONE_SOUND = "beholder_blast"

BATTLE_SLASH_INTERVAL = 1.5
BATTLE_SLASH_ACTIVE = 0.22
BATTLE_SLASH_SANITY_DAMAGE = 12
BATTLE_ATTACK_FLASH = 0.18

# Screen shake decays exponentially; the offset jitters within ±amount.
CAMERA_SHAKE_DECAY = 9.0

# The scripted Fireball ends the sanctum fight. Once Chuck has been
# sealed in the battle (the breach triggered) and survived this long,
# the wizard casts it: a flash and a heavy shake, Chuck cut to roughly
# half Sanity, and then he is thrown into the collapsed rubble map. The
# outcome is scripted — the player cannot prevent or hasten it.
BATTLE_FIREBALL_DELAY = 24.0       # seconds of survival before it lands
FIREBALL_FLASH_PEAK = 0.4          # the blast lands; Sanity is halved
FIREBALL_DURATION = 1.2            # flash length before the rubble loads
FIREBALL_SHAKE = 11.0
FIREBALL_SANITY_FRACTION = 0.5     # cut to (at most) this fraction of max
FIREBALL_SOUND = "fireball"

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

# The fortress battle's Phase 8 corruption. Crossing into the upper yard
# seals the two rows behind Chuck, then three timed incursions eat inward from
# the arena's sides while leaving a readable central route. The river—not an
# unavoidable Astral conversion—supplies the forced final escape.
INFERNAL_CORRUPTION_TRIGGER_ROW = 23
INFERNAL_CORRUPTION_SEAL_ROWS = (25, 26)
INFERNAL_CORRUPTION_WAVE_TIMES = (4.0, 8.0, 12.0)
FEYWILD_RIVER_START_TIME = 15.0
FEYWILD_RIVER_SPEED = 64.0
FEYWILD_RIVER_BLOCK_W = 64
FEYWILD_RIVER_BLOCK_H = 16
FEYWILD_RIVER_SURGE_TIME = 6.0
FEYWILD_RIVER_ESCAPE_FADE = 0.65

# The entrance establishing shot cuts the camera to the battle so the
# trio's heroic lines land on the trio, not the empty aisle Chuck
# walked in by. The group's feet sit this far below screen-center, so
# the actors ride in the upper frame clear of the dialogue panel.
SANCTUM_ESTABLISH_LIFT = 30

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

# Modern-city traffic. Cars are environmental timing hazards rather than
# enemies: two impacts deplete full Sanity, and fixed spacing keeps every
# crossing observable and deterministic.
TRAFFIC_SPEED = 150.0
TRAFFIC_SPACING = 256.0
TRAFFIC_MARGIN = 48.0
TRAFFIC_SANITY_DAMAGE = 50
TRAFFIC_HITBOX_LONG = 34
TRAFFIC_HITBOX_SHORT = 14
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
PIRATE_CHEF_SPEED = 58.0
PIRATE_CHEF_NOTICE_RANGE = 96.0
PIRATE_CHEF_SANITY_DAMAGE = 20
SWORD_FIGHTER_SPEED = 38.0
SWORD_FIGHTER_SANITY_DAMAGE = 15

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
