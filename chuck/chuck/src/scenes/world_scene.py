"""World scene: where the game is actually played.

Responsibilities (current):
    * Own the current TileMap and the Player.
    * Update order: entities -> camera (so it tracks the new position).
    * Draw order: ground tiles -> entities -> (future: overhead, HUD).
    * ESC quits (temporary, until a pause menu exists).

Responsibilities (future):
    * Y-sorted entity drawing (Chuck behind crates and chair legs).
    * Sanity system + quiet Astral Anchor respawn on depletion.
    * Ambient audio (ocean, gulls) via the audio system.
"""

from __future__ import annotations

import math

import pygame

from src.core import config
from src.entities.anchor import AstralAnchor
from src.entities.battle_actor import BattleActor
from src.entities.captain_chest import CaptainChest
from src.entities.breakable_grass import BreakableGrass
from src.entities.breakable_urn import BreakableUrn
from src.entities.jar_shelf import PantryJar, PantryJarShelf
from src.entities.choice_trigger import ChoiceTrigger
from src.entities.battle_hazards import (
    AstralBreach, BattleChoreographer, BattleProjectile,
    CollisionBattleChoreographer, FeywildRiverField,
    InfernalAstralCorruption, InfernalBattleChoreographer,
)
from src.systems.orc_horde import OrcHorde
from src.systems.orc_siege import OrcSiege
from src.systems.trio_encounter import TrioEncounter, WorldChurn
from src.entities.dart_trap import DartTrap, TempleDart
from src.entities.deck_pirate import DeckPirateNPC
from src.entities.hazard import Cat
from src.entities.massive_dinosaur import MassiveDinosaur
from src.entities.npc import NPC
from src.entities.cabin_light_entity import CabinLightEntity
from src.entities.pedestrian import PedestrianNPC
from src.entities.pickup import Cigarette
from src.entities.pirate_chef import PirateChef
from src.entities.pirate_npc import PirateNPC
from src.entities.player import Player
from src.entities.prop import Prop, midday_variant
from src.entities.rat import SewerRat
from src.entities.raccoon import Raccoon
from src.entities.raptor import Raptor
from src.entities.redcap import Redcap
from src.entities.reality_blocks import RealityBlockField
from src.entities.aurora_light import AuroraLight, MAP_SPRITE_REGION
from src.entities.street_light import StreetLightField
from src.entities.blue_dragon import BlueDragon
from src.entities import red_dragon
from src.entities.red_dragon import RedDragonFlyby
from src.entities.city_rain import CityRain
from src.entities.snow_fall import SNOW_TERRAIN, SnowFall
from src.entities.snake import TempleSnake
from src.entities.flameskull import Flameskull
from src.entities.fisherman import FishermanNPC
from src.entities.spitting_orchid import OrchidSeed, SpittingOrchid
from src.entities.police import (
    Bullet, PoliceOfficer, SpinningPoliceOfficer,
)
from src.entities.spined_devil import FlamingSpine, SpinedDevil
from src.entities.sword_fighter import SwordFighter
from src.entities.traffic import ROAD_TERRAIN, TrafficLane
from src.entities.animal_control import AnimalControlOfficer
from src.entities.undead import UndeadEnemy
from src.scenes.dialogue_scene import DialogueScene
from src.scenes.scene import Scene
from src.systems.astral_anchor import AstralAnchorSystem
from src.systems.cabin_progress import (
    COUNTER_MAP_AWAKENED_FLAG, apply_cabin_door_crossing,
    awakened_music_for,
)
from src.systems.checkpoints import WATERDEEP_RETURN_FLAG
from src.systems.captain_confrontation import (
    CAPTAIN_ARRIVAL_SPEED,
    CAPTAIN_CONFRONTED_FLAG,
    DECK_PLANK_LENGTH,
    DECK_PLANK_WIDTH,
    PLANK_KICK_APPROACH_SPEED,
    PLANK_KICK_FALL_DURATION,
    PLANK_KICK_WINDUP,
    PLANK_PROCESSION_SPEED,
    captain_confrontation_ready,
    stage_deck_plank,
)
from src.systems.choice import Choice, ChoiceSystem, Option
from src.systems.combat import scratch_first_target
from src.systems.dialogue import DialogueSystem
from src.systems.fall import fall_zone_kind
from src.systems.interaction import find_target
from src.systems.reactive_flowers import ReactiveFlowerController
from src.systems.terrain_effect import ground_speed_multiplier
from src.systems.terrain_hazard import touching_terrain_hazard
from src.systems.undead_release import (
    UndeadReleaseController, is_staged_undead,
)
from src.systems.waterdeep_finale import (
    DOCKED_SHIP_TILE, FISHERMAN_TILE, PLAZA_TOWNSFOLK,
    RETURN_PLAZA_TOWNSFOLK, RETURN_TOWNSFOLK,
)
from src.ui.tutorial_hint import TutorialHint
from src.systems.net_capture import NetCapture
from src.systems.sanity import SanitySystem
from src.systems.ship_motion import deck_rock_offset
from src.ui.hud import HUD

BOBERT_AWAKE_LINE = "bobert_awake"
PANTRY_CHEESE_HINT = "pantry_cheese_hint"

# Ground with a line of its own, keyed by map character the way the fall
# zones are. The Astral Sea is terrain and not a prop -- seventeen
# thousand tiles of it across thirty-nine maps -- so it has nowhere to
# keep a line except here.
TERRAIN_DIALOGUE = {"V": "examine_astral_void"}


class _TerrainTarget:
    """A stand-in, so ground can be examined like anything else.

    It carries the one attribute the interact path reads off a prop and
    nothing else: no choice, no interact(), no hitbox, no place in any
    of the scene's lists. It never outlives the key press that made it.
    """

    __slots__ = ("dialogue_id",)

    def __init__(self, dialogue_id: str) -> None:
        self.dialogue_id = dialogue_id
BOBERT_CARTONS_LINE = "bobert_awake_cartons"
from src.world.camera import Camera
from src.world.collision import overlaps
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import (
    AREA_MUSIC, AREA_WALK_EXITS, DRAGON_MUSIC, FORTRESS_BATTLE_MUSIC,
)


class WorldScene(Scene):
    """The explorable world. Starts at the docks; a dialogue choice can
    carry Chuck to another map (the sewer) via load_map()."""

    pausable = True

    def __init__(
        self,
        game,
        map_name: str = "waterdeep_docks",
        *,
        initial_arrival: str | None = None,
        initial_position: tuple[float, float] | None = None,
        initial_facing: str | None = None,
        initial_climb_from_water: bool = False,
        initial_sanity: int | None = None,
        initial_checkpoint_id: str | None = None,
        initial_fade_in: bool = False,
        initial_fade_from: tuple[int, int, int] = (0, 0, 0),
    ) -> None:
        super().__init__(game)
        self._initial_map = map_name
        self._initial_arrival = initial_arrival
        self._initial_position = initial_position
        self._initial_facing = initial_facing
        self._initial_climb_from_water = initial_climb_from_water
        self._initial_sanity = initial_sanity
        self._initial_checkpoint_id = initial_checkpoint_id
        self._initial_fade_in = initial_fade_in
        self._initial_fade_from = initial_fade_from
        # Set by a transition choice; applied once the conversation that
        # triggered it has closed (see update()).
        self._pending_map: str | None = None
        self._pending_choice_action: str | None = None
        self._pending_arrival: str | None = None
        self._pending_climb_from_water = False
        self._pending_fade_in = False
        self._sewer_completed = game.progress.has("sewer_completed")

    def on_enter(self) -> None:
        """Build the starting area when this scene becomes active."""
        self.load_map(
            self._initial_map,
            arrival=self._initial_arrival,
            climb_from_water=self._initial_climb_from_water,
            facing=self._initial_facing,
            position=self._initial_position,
            sanity=self._initial_sanity,
            checkpoint_id=self._initial_checkpoint_id,
            fade_in=self._initial_fade_in,
            fade_from=self._initial_fade_from,
        )

    def load_map(
        self,
        map_name: str,
        arrival: str | None = None,
        climb_from_water: bool = False,
        facing: str | None = None,
        position: tuple[float, float] | None = None,
        sanity: int | None = None,
        checkpoint_id: str | None = None,
        fade_in: bool = False,
        fade_from: tuple[int, int, int] = (0, 0, 0),
        arrival_row: int | None = None,
    ) -> None:
        """(Re)build the map and all entities for an area. Used both on
        first entry and when a transition carries Chuck somewhere new."""
        self.map_name = map_name
        if map_name == "waterdeep_docks" and arrival == "sewer_outflow":
            self.game.progress.enable("sewer_completed")
        if checkpoint_id is None:
            checkpoint_id = self.game.checkpoints.entry_checkpoint_id(
                map_name, arrival
            )
        self.game.checkpoints.set_runtime_checkpoint(checkpoint_id)
        self._sewer_completed = self.game.progress.has("sewer_completed")
        self._pending_map = None
        self._pending_choice_action = None
        self._pending_arrival = None
        self._pending_climb_from_water = False
        self._pending_facing = None
        self._pending_fade_in = False
        self._walk_choice_armed = True  # crevice-style walk-in prompts
        self._ladder_choice_armed = True
        self.tilemap = TileMap(config.MAPS_DIR / f"{self.map_name}.txt")
        if self.map_name == "waterdeep_docks" and self._sewer_completed:
            self.tilemap.open_tavern_entrance()
        self.tilemap.load_tileset(
            self.game.assets,
            tileset_for(
                self.map_name,
                waterdeep_returned=self.game.progress.has(
                    WATERDEEP_RETURN_FLAG
                ),
            ),
        )
        self._world_time = 0.0  # drives water shimmer
        # It is still raining in the daytime city, so both surface city
        # tilesets get weather; only the sewer below them is dry.
        self.city_rain = (
            CityRain()
            if MAP_TILESET.get(map_name) in {"city", "city_day"}
            else None
        )
        # Snow falls on any map with snow on it, rather than on a list
        # of named maps: the fragment's own tiles are the mask, so a
        # frozen piece of any shape gets the right weather for free.
        self.snow = SnowFall() if self.tilemap.has_terrain(
            SNOW_TERRAIN) else None
        # Once the table map has woken, the cabin lights go out and the
        # ...and the night city's lamps, which are the same idea at the
        # other end of the game: a fixed set of pools this map draws
        # over itself. The day blocks carry the same posts on the same
        # tiles and no field at all, which is the whole of what "the
        # lights are off" means here.
        self.street_lights = (
            StreetLightField([
                (col, row) for kind, col, row in self.tilemap.prop_tiles
                if kind == "city_streetlight"
            ])
            if self.after_dark else None
        )

        # room is lit by the aurora projector and the stove alone.
        self.aurora = (
            AuroraLight(self._prop_centre("cabin_woodstove"),
                        self._prop_centre("cabin_lava_lamp"),
                        self._prop_centre("cabin_table"))
            if (map_name == "tahuya_cabin_interior"
                and self.game.progress.has(COUNTER_MAP_AWAKENED_FLAG))
            else None
        )
        self._arrival_fade_t: float | None = 0.0 if fade_in else None
        self._arrival_fade_from = fade_from

        arrivals = {
            kind.split(":", 1)[1]: position
            for kind, position in self.tilemap.object_spawns
            if kind.startswith("arrival:")
        }
        if position is not None:
            spawn_cx = position[0] + config.PLAYER_HITBOX_W / 2
            spawn_cy = position[1] + config.PLAYER_HITBOX_H / 2
        elif arrival is not None:
            if arrival not in arrivals:
                raise ValueError(
                    f"Map {map_name!r} has no arrival marker {arrival!r}"
                )
            spawn_cx, spawn_cy = arrivals[arrival]
            if arrival_row is not None:
                spawn_cy = self._open_row_near(spawn_cx, arrival_row,
                                               spawn_cy)
        else:
            spawn_cx, spawn_cy = self.tilemap.spawn_points.get(
                "player",
                (
                    self.tilemap.width_tiles * config.TILE_SIZE / 2,
                    self.tilemap.height_tiles * config.TILE_SIZE / 2,
                ),
            )
        target_player_y = spawn_cy - config.PLAYER_HITBOX_H / 2
        self.player = Player(
            spawn_cx - config.PLAYER_HITBOX_W / 2,
            target_player_y,
            self.game.input,
        )
        if facing is not None:
            self.player.facing = facing
        if climb_from_water:
            self.player.y += config.TILE_SIZE
            self.player.facing = "up"
        self.player.tilemap = self.tilemap
        self.player.load_sprites(self.game.assets)
        self._traffic_safe_position = (self.player.x, self.player.y)
        # The adventurers' entrance lines (session 131): entering the
        # final chamber from the gauntlet, each delivers one heroic,
        # non-interactive line before control returns.
        self._pending_entrance_dialogue = (
            "sanctum_entrance"
            if map_name == "temple_sanctum" and arrival == "from_temple_8"
            else "phlegethos_battle_entrance"
            if (
                map_name == "phlegethos_fortress_approach"
                and arrival == "from_phlegethos_rubble"
            )
            # The third and last of these. Same path as the other two,
            # deliberately: a player has met the trio twice and the
            # lines landing on the tableau the same way is most of what
            # says this is the same three people.
            else "trio_opening"
            if map_name == "desert_trio" and arrival == "from_east_8"
            else None
        )
        self._restore_camera_to_player = False
        self._trio_after_dialogue = False
        self._climb_t: float | None = 0.0 if climb_from_water else None
        self._climb_from_y = self.player.y
        self._climb_target_y = target_player_y
        self.player.climb_progress = 0.0 if climb_from_water else None

        self.camera = Camera(config.NATIVE_WIDTH, config.NATIVE_HEIGHT)
        self.camera.set_bounds(
            self.tilemap.width_tiles * config.TILE_SIZE,
            self.tilemap.height_tiles * config.TILE_SIZE,
        )
        self.camera.follow(self.player)

        # Sanity + HUD. Depletion starts the quiet respawn.
        previous_sanity = getattr(getattr(self, "sanity", None), "current", None)
        sanity_start = (
            previous_sanity
            if sanity is None and previous_sanity is not None
            else sanity
        )
        self.sanity = SanitySystem(
            on_depleted=self._begin_respawn,
            start=sanity_start,
        )
        self.hud = HUD(self.sanity, self.game.assets.bitmap_font(),
               self.game.cigarettes, self.game.deaths,
               progress=self.game.progress)
        # The opening teaches; the return does not. By the time Chuck is
        # back on these docks he has pressed every key there is.
        self._hint = (
            TutorialHint(self.game.assets, self.game.input)
            if self.map_name in config.TUTORIAL_MAPS
            and not self.game.progress.has(WATERDEEP_RETURN_FLAG)
            else None
        )
        self._jump_tutorial_complete = False

        # Respawn: the door he came in by, fixed for this visit.
        #
        # Where the door is a climb out of the water, that is the top of
        # the climb and not the bottom of it. Chuck starts a tile lower
        # with the animation running, and putting him back THERE on a
        # death would drop him in the harbour.
        self.anchors_system = AstralAnchorSystem(
            default_position=(self.player.x, self._climb_target_y
                              if self._climb_t is not None
                              else self.player.y),
            default_checkpoint_id=checkpoint_id,
        )
        # Being netted holds Chuck still and drains him; it never becomes
        # a second way to die. Map reset clears it like any enemy state.
        self.net_capture = NetCapture()
        # Canopy region -> how thinned out it is, for overhead tiles that
        # somebody is standing under.
        self._overhead_veils: dict[int, float] = {}
        self._respawn_phase: str | None = None  # "out" | "hold" | "in"
        self._respawn_t = 0.0
        self._fall_t: float | None = None
        self._fall_kind: str | None = None

        # Area music, looping — or silence where an area has no theme yet
        # (the sewer's track is a later Phase 2 session). Footsteps
        # alternate variants and pick wood/stone from the tile underfoot.
        music = (
            awakened_music_for(self.map_name, self.game.progress)
            or AREA_MUSIC.get(self.map_name, config.MUSIC_FILE)
        )
        if music is not None:
            self.game.audio.play_music(music)
        else:
            self.game.audio.stop_music()
        self._step_timer = 0.0
        self._step_variant = 1

        # Object spawns from map markers.
        self.dialogue = DialogueSystem()
        self.choices = ChoiceSystem()
        self.last_choice: str | None = None  # what Chuck last decided
        self._deck_captain_spawn = None
        self._deck_plank_origin: tuple[int, int] | None = None
        self.reality_blocks: RealityBlockField | None = None
        self._reality_warning_shown = False
        self._captain_confrontation_started = False
        self._captain_arrival_active = False
        self._captain_arrival_waypoints: list[tuple[float, float]] = []
        self._captain_after_arrival_dialogue = False
        self._captain_after_dialogue = False
        self._plank_procession_active = False
        self._plank_procession_phase: str | None = None
        self._plank_procession_target: tuple[float, float] | None = None
        self._plank_after_warning_dialogue = False
        self._plank_ending_phase: str | None = None
        self._plank_ending_t = 0.0
        self._plank_ending_waypoints: list[tuple[float, float]] = []
        self._plank_ending_block = None
        self._plank_ending_start: tuple[float, float] | None = None
        self._plank_kick_sounded = False
        self._river_escape_t: float | None = None
        # Temple urns, pantry jar shelves, and pantry floor jars are
        # living breakables (see below), not static props.
        self.props = []
        for kind, col, row in self.tilemap.prop_tiles:
            if kind in ("temple_urn", "pantry_shelf", "grain_sack"):
                continue
            if kind in ("ship_captain_chest", "desert_ruin_chest",
                        "chult_falls_chest"):
                prop = CaptainChest(
                    col, row, self.game.assets,
                    self.game.progress, kind=kind,
                    progress_flag=(
                        None if kind == "ship_captain_chest"
                        else f"{kind}_opened"),
                    collected_flag=(
                        None if kind == "ship_captain_chest"
                        else f"{kind}_carton_collected"),
                )
            else:
                if (
                    kind == "cabin_table"
                    and self.game.progress.has(COUNTER_MAP_AWAKENED_FLAG)
                ):
                    kind = "cabin_table_awakened"
                elif kind == "city_streetlight" and self.after_dark:
                    # The same lamp on the same tile in both cities; only
                    # the glass differs. Swapping the sprite here rather
                    # than authoring two characters keeps the night and
                    # day maps directly comparable, tile for tile.
                    kind = "city_streetlight_lit"
                elif kind.startswith("temple_arch") and \
                        self.map_name.startswith("phlegethos"):
                    # Phlegethos's gates are the temple's doorway at the
                    # temple's scale, which is the point of them -- but
                    # they are cut into infernal basalt, not temple
                    # stone, and they should not read as the same wall.
                    kind = kind.replace("temple", "phlegethos")
                elif kind == "bobert_barrel" and self._waterdeep_midday:
                    # Chuck is home, and Bobert is up.
                    kind = "bobert_barrel_awake"
                elif self._waterdeep_midday:
                    # Waterdeep is one map in two lights, like its tileset:
                    # pier wood and water tints to match the midday sheet,
                    # and the lamps out.
                    kind = midday_variant(kind)
                prop = Prop(kind, col, row, self.game.assets)
            self.props.append(prop)
        self.pickups: list[Cigarette] = []
        self.breakables: list[BreakableGrass | BreakableUrn] = []
        # Each dressed urn becomes a scratchable entity concealing a
        # cigarette carton. Breaking clears its tile to the declared
        # under-terrain: floor urns open up, wall-base urns stay wall.
        for kind, col, row in self.tilemap.prop_tiles:
            if kind != "temple_urn":
                continue
            wall_mounted = self.tilemap.terrain_at(col, row) == "¦"
            urn = BreakableUrn(
                col, row, wall_mounted=wall_mounted,
                on_break=(lambda c=col, r=row:
                          self.tilemap.clear_tile(c, r)),
            )
            urn.load_sprite(self.game.assets)
            self.breakables.append(urn)
        # Pantry-style shelves: the furniture stands forever, but its JARS
        # are scratch-breakable and spill a carton. The scene picks the drop
        # tile because only the map knows which neighboring board is safe;
        # this supports both pantry board ('p') and ship plank ('=').
        for kind, col, row in self.tilemap.prop_tiles:
            if kind != "pantry_shelf":
                continue
            ts = config.TILE_SIZE
            drop_tile = next(
                (c, r)
                for c, r in ((col, row + 1), (col - 1, row + 1),
                             (col + 1, row + 1), (col - 1, row),
                             (col + 1, row))
                if self.tilemap.terrain_at(c, r) in {"p", "="}
                and not self.tilemap.is_solid(c, r)
            )
            shelf = PantryJarShelf(
                col, row,
                drop=(drop_tile[0] * ts + ts / 2,
                      drop_tile[1] * ts + ts / 2),
            )
            shelf.load_sprite(self.game.assets)
            self.breakables.append(shelf)
        # Pantry floor jars (the round 'z' vessels): the temple floor
        # urns' lifecycle in crockery — shatter, spill a carton in
        # place, and clear the tile to open board.
        for kind, col, row in self.tilemap.prop_tiles:
            if kind != "grain_sack":
                continue
            jar = PantryJar(
                col, row,
                on_break=(lambda c=col, r=row:
                          self.tilemap.clear_tile(c, r)),
            )
            jar.load_sprite(self.game.assets)
            self.breakables.append(jar)
        self.hazards: list[Cat] = []
        self.anchors: list[AstralAnchor] = []
        self.npcs: list[NPC] = []
        self.reactive_flowers = ReactiveFlowerController(
            self.tilemap, self.tilemap.object_spawns
        )
        self.reactive_flowers.load_sprites(self.game.assets)
        self.choice_triggers: list[ChoiceTrigger] = []
        self.battle_actors: list[BattleActor] = []
        self._dart_trap_spawns = [
            (kind.split(":", 1)[1], position)
            for kind, position in self.tilemap.object_spawns
            if kind.startswith("dart_trap:")
        ]
        self._traffic_lane_spawns = [
            (kind.split(":")[1], int(kind.split(":")[2]), position)
            for kind, position in self.tilemap.object_spawns
            if kind.startswith("traffic_lane:")
        ]
        self._enemy_spawns = [
            (kind, position)
            for kind, position in self.tilemap.object_spawns
            if kind in {
                "cat", "rat", "raccoon", "zombie", "skeleton", "lemure",
                "orc", "knight", "crocodile", "animal_control",
                "raptor",
                "massive_dinosaur", "horned_devil", "pit_fiend",
                "displacer_beast",
                "griffon",
                "snake", "fire_snake",
                "pirate_chef", "redcap", "thorn_mite",
            } or kind.startswith((
                "sword_fighter:", "spined_devil:", "police:", "flameskull:",
                "spitting_orchid:", "lantern_moth:", "raptor:",
                "blue_dragon:",
            ))
        ]
        self._staged_undead_spawns = [
            (kind, position)
            for kind, position in self.tilemap.object_spawns
            if is_staged_undead(kind)
        ]
        self.undead_release = UndeadReleaseController(
            self.map_name, self._staged_undead_spawns
        )
        for kind, (cx, cy) in self.tilemap.object_spawns:
            if kind == "cigarette":
                cig = Cigarette(cx, cy)
                cig.load_sprite(self.game.assets)
                self.pickups.append(cig)
            elif kind == "breakable_grass":
                grass = BreakableGrass(cx, cy)
                grass.load_sprite(self.game.assets)
                self.breakables.append(grass)
            elif kind == "cat":
                continue  # rebuilt with all enemies below
            elif kind.startswith("anchor:"):
                anchor_id = kind.split(":", 1)[1]
                anchor = AstralAnchor(cx, cy, anchor_id)
                anchor.load_sprites(self.game.assets)
                anchor.lit = anchor_id == checkpoint_id
                self.anchors.append(anchor)
            elif kind.startswith("npc:"):
                npc_id = kind.split(":", 1)[1]
                npc = NPC(cx, cy, npc_id=npc_id, dialogue_id=npc_id)
                npc.load_sprites(self.game.assets)
                self.npcs.append(npc)
            elif kind.startswith("cabin_light:"):
                parts = kind.split(":")
                _prefix, dialogue_id, progress_flag, phase = parts[:4]
                facing = parts[4] if len(parts) > 4 else "south"
                npc = CabinLightEntity(
                    cx, cy,
                    dialogue_id=dialogue_id,
                    progress=self.game.progress,
                    progress_flag=progress_flag,
                    phase_index=int(phase),
                    facing=facing,
                    seat_sort_y=(int(cy // config.TILE_SIZE) + 2)
                                * config.TILE_SIZE + 0.5,
                )
                npc.load_sprites(self.game.assets)
                self.npcs.append(npc)
            elif kind.startswith("patrol_npc:"):
                _prefix, npc_id, rest = kind.split(":", 2)
                # "h" or "v", optionally ":flee" for the City Day 6 chase.
                axis, _, mode = rest.partition(":")
                npc = PedestrianNPC(
                    cx, cy, npc_id=npc_id, dialogue_id=npc_id, axis=axis,
                    patrol_range=config.PEDESTRIAN_PATROL_RANGES.get(npc_id),
                    fleeing=(mode == "flee"),
                )
                npc.tilemap = self.tilemap
                npc.load_sprites(self.game.assets)
                self.npcs.append(npc)
            elif kind.startswith("elevated_npc:"):
                npc_id = kind.split(":", 1)[1]
                npc = NPC(
                    cx, cy, npc_id=npc_id, dialogue_id=npc_id,
                    interaction_extension_down=config.TILE_SIZE * 4,
                    sort_y_override=cy + config.TILE_SIZE * 5,
                )
                npc.load_sprites(self.game.assets)
                self.npcs.append(npc)
            elif kind.startswith("pirate_npc:"):
                npc_id, progress_flag = kind.split(":", 2)[1:]
                npc = PirateNPC(
                    cx, cy, npc_id=npc_id,
                    progress=self.game.progress,
                    progress_flag=progress_flag,
                )
                npc.load_sprites(self.game.assets)
                self.npcs.append(npc)
            elif kind.startswith("deck_pirate:"):
                npc_id, progress_flag, performance = kind.split(":", 3)[1:]
                npc = DeckPirateNPC(
                    cx, cy, npc_id=npc_id,
                    progress=self.game.progress,
                    progress_flag=progress_flag,
                    performance=performance,
                )
                npc.load_sprites(self.game.assets)
                self.npcs.append(npc)
            elif kind.startswith("deck_captain:"):
                npc_id, progress_flag, performance = kind.split(":", 3)[1:]
                self._deck_captain_spawn = (
                    cx, cy, npc_id, progress_flag, performance,
                )
            elif kind == "deck_plank_origin":
                self._deck_plank_origin = (
                    int(cx // config.TILE_SIZE),
                    int(cy // config.TILE_SIZE),
                )
            elif kind in {
                "rat", "raccoon", "zombie", "skeleton", "lemure", "orc",
                "knight", "crocodile",
                "animal_control", "raptor",
                "massive_dinosaur", "horned_devil", "pit_fiend",
                "displacer_beast",
                "griffon",
                "snake", "fire_snake",
                "pirate_chef", "redcap", "thorn_mite",
            } or kind.startswith("raptor:"):
                continue  # rebuilt with all enemies below
            elif kind.startswith((
                "sword_fighter:", "spined_devil:", "police:", "flameskull:",
                "spitting_orchid:", "lantern_moth:", "blue_dragon:",
            )):
                continue  # rebuilt with all hazards below
            elif kind.startswith("battle:"):
                actor = BattleActor(cx, cy, kind.split(":", 1)[1])
                actor.load_sprite(self.game.assets)
                self.battle_actors.append(actor)
            elif kind.startswith("choice:"):
                choice_id = kind.split(":", 1)[1]
                # The table only asks once its map has woken. The
                # ordinary D&D map has no planar interaction, so the
                # trigger is not built rather than being built and
                # silenced.
                if (
                    choice_id == "cabin_table_portal"
                    and not self.game.progress.has(COUNTER_MAP_AWAKENED_FLAG)
                ):
                    continue
                self.choice_triggers.append(ChoiceTrigger(cx, cy, choice_id))
            elif kind.startswith("arrival:"):
                continue  # named map metadata, not a runtime entity
            elif kind.startswith("boundary:"):
                # Authored handoff metadata for a future destination.  It is
                # deliberately inert until that destination map exists.
                continue
            elif kind.startswith("traffic_lane:"):
                continue  # rebuilt as a fixed-size lane field on reset
            elif kind.startswith(
                ("flower_switch:", "flower_open:", "flower_close:")
            ):
                continue  # owned by the map-local reactive-flower controller
            elif kind.startswith("dart_trap:"):
                continue  # rebuilt with projectiles by _reset_enemies()
            elif is_staged_undead(kind):
                continue  # released in finite groups as Chuck advances
            else:
                raise ValueError(f"No spawner for object kind {kind!r}")
        self._add_waterdeep_state_dressing()
        if self.game.progress.has(CAPTAIN_CONFRONTED_FLAG):
            self._spawn_deck_captain()
            self._stage_deck_plank()
            self._apply_post_confrontation_tableau()
        if (
            self.map_name == "ship_exterior_deck"
            and self._deck_plank_origin is not None
        ):
            self.reality_blocks = RealityBlockField(*self._deck_plank_origin)
            self.reality_blocks.load_art(self.game.assets)
        # An opened-but-uncollected captain chest reconstructs its physical
        # carton when this room is loaded.
        self._collect_pending_drops()
        self._reset_enemies()

    def _add_waterdeep_state_dressing(self) -> None:
        """Populate shared Waterdeep geometry for its current era."""
        returned = self.game.progress.has(WATERDEEP_RETURN_FLAG)
        if self.map_name == "waterdeep_docks" and returned:
            self.props.append(Prop(
                "waterdeep_docked_ship", *DOCKED_SHIP_TILE, self.game.assets
            ))
            ts = config.TILE_SIZE
            fish_col, fish_row = FISHERMAN_TILE
            fisherman = FishermanNPC(
                fish_col * ts + ts / 2,
                fish_row * ts + ts / 2,
            )
            fisherman.load_sprites(self.game.assets)
            self.npcs.append(fisherman)
            self._add_townsfolk(RETURN_TOWNSFOLK)
        elif self.map_name == "waterdeep_plaza":
            self._add_townsfolk(PLAZA_TOWNSFOLK)
            if returned:
                self._add_townsfolk(RETURN_PLAZA_TOWNSFOLK)

    def _add_townsfolk(self, spawns) -> None:
        """Build one authored group with reused human-scale sprites."""
        ts = config.TILE_SIZE
        for spawn in spawns:
            col, row = spawn.tile
            npc = NPC(
                col * ts + ts / 2,
                row * ts + ts / 2,
                npc_id=spawn.sprite_id,
                dialogue_id=spawn.dialogue_id,
            )
            npc.facing = spawn.facing
            npc.load_sprites(self.game.assets)
            self.npcs.append(npc)


    def update(self, dt: float) -> None:
        """Advance the world simulation."""
        # The authored warning freezes the room like any other dialogue. The
        # chase begins only after that overlay closes and control returns.
        if self._chef_start_after_dialogue:
            self._chef_start_after_dialogue = False
            for chef in self.chefs:
                chef.begin_pursuit()
        if self._captain_after_arrival_dialogue:
            self._captain_after_arrival_dialogue = False
            captain = self._spawn_deck_captain()
            captain.face_toward(self.player)
            self.camera.focus_on(
                captain.x + captain.width / 2,
                captain.y + captain.height / 2,
            )
            self._captain_after_dialogue = True
            self.game.scenes.push(DialogueScene(
                self.game, self.dialogue.get("captain_confrontation")
            ))
            return
        if self._captain_after_dialogue:
            self._captain_after_dialogue = False
            self.game.progress.enable(CAPTAIN_CONFRONTED_FLAG)
            self._begin_plank_procession()
        if self._plank_after_warning_dialogue:
            self._plank_after_warning_dialogue = False
            self._continue_plank_procession()
        if self._pending_entrance_dialogue is not None:
            lines = self.dialogue.get(self._pending_entrance_dialogue)
            self._pending_entrance_dialogue = None
            if self.battle_actors:
                # Cut to the battle so the heroes' lines land on them,
                # not on the empty aisle Chuck entered by. The camera
                # returns to Chuck once the conversation closes.
                cx, cy = self._battle_establishing_focus()
                self.camera.focus_on(cx, cy)
                self._restore_camera_to_player = True
            self.game.scenes.push(DialogueScene(self.game, lines))
            return
        if self._restore_camera_to_player:
            self._restore_camera_to_player = False
            self.camera.follow(self.player)

        if self._river_escape_t is not None:
            self._river_escape_t += dt
            self.camera.update(dt)
            if self._river_escape_t >= config.FEYWILD_RIVER_ESCAPE_FADE:
                from src.scenes.feywild_river_cutscene_scene import (
                    FeywildRiverCutsceneScene,
                )
                self.game.scenes.replace(
                    FeywildRiverCutsceneScene(
                        self.game, sanity=self.sanity.current
                    )
                )
            return

        # "Where he belongs!" has closed: the worlds come apart and the
        # blast puts him back on the docks. The end of Phase 13.
        if self._trio_after_dialogue:
            self._trio_after_dialogue = False
            from src.scenes.return_to_waterdeep_cutscene_scene import (
                ReturnToWaterdeepCutsceneScene,
            )
            self.game.scenes.replace(
                ReturnToWaterdeepCutsceneScene(
                    self.game, sanity=self.sanity.current
                )
            )
            return

        # The argument has closed on "FIREBALL!!": now it lands.
        if self._fireball_after_dialogue and self._fireball_t is None:
            self._fireball_after_dialogue = False
            self._begin_fireball()
            return

        # A validated cutscene action chosen in a prompt waits until the
        # overlay has closed, just like an ordinary map transition.
        if self._pending_choice_action is not None:
            action = self._pending_choice_action
            self._pending_choice_action = None
            if action == "tower_arrival":
                from src.scenes.tower_arrival_cutscene_scene import (
                    TowerArrivalCutsceneScene,
                )
                self.game.scenes.replace(
                    TowerArrivalCutsceneScene(
                        self.game, sanity=self.sanity.current
                    )
                )
                return
            if action == "desert_arrival":
                from src.scenes.desert_arrival_cutscene_scene import (
                    DesertArrivalCutsceneScene,
                )
                self.game.scenes.replace(
                    DesertArrivalCutsceneScene(
                        self.game, sanity=self.sanity.current
                    )
                )
                return
            if action == "doug_fir_portal":
                from src.scenes.doug_fir_cutscene_scene import (
                    DougFirCutsceneScene,
                )
                self.game.scenes.replace(
                    DougFirCutsceneScene(
                        self.game, sanity=self.sanity.current
                    )
                )
                return
            if action == "zephyros_intro":
                from src.scenes.zephyros_intro_cutscene_scene import (
                    ZephyrosIntroCutsceneScene,
                )
                self.game.scenes.replace(
                    ZephyrosIntroCutsceneScene(
                        self.game, sanity=self.sanity.current
                    )
                )
                return
            raise ValueError(f"Unhandled choice action {action!r}")

        # A transition chosen during a conversation waits until that
        # conversation has closed and control returns here — only then
        # is this scene the top of the stack again — so the descent
        # lines finish over the old world before the new one loads.
        if self._pending_map is not None:
            destination = self._pending_map
            arrival = self._pending_arrival
            climb_from_water = self._pending_climb_from_water
            facing = self._pending_facing
            fade_in = self._pending_fade_in
            if self.map_name == "temple_rubble" and destination == "ship_deck":
                # Saying YES to the crevice plays the escape cutscene, which
                # ends Phase 6 and hands off to the playable deck itself.
                from src.scenes.escape_cutscene_scene import EscapeCutsceneScene
                self.game.scenes.replace(
                    EscapeCutsceneScene(self.game, sanity=self.sanity.current)
                )
                return
            self.load_map(
                destination,
                arrival=arrival,
                climb_from_water=climb_from_water,
                facing=facing,
                fade_in=fade_in,
            )
            return

        # The world keeps moving whether or not Chuck is in it.
        self._world_time += dt
        if self.city_rain is not None:
            self.city_rain.update(dt)
        if self.aurora is not None:
            self.aurora.update(dt)
        if self.street_lights is not None:
            self.street_lights.update(dt)
        if self.reality_blocks is not None:
            self.reality_blocks.update(dt)
        if self._arrival_fade_t is not None:
            self._arrival_fade_t += dt
            if self._arrival_fade_t >= config.AREA_FADE_DURATION:
                self._arrival_fade_t = None
            self.camera.update(dt)
            return
        if (
            self.map_name == "ship_exterior_deck"
            and not self._captain_confrontation_started
            and captain_confrontation_ready(self.game.progress)
        ):
            self._captain_confrontation_started = True
            self._begin_captain_arrival()
            self.camera.update(dt)
            return
        if self._captain_arrival_active:
            captain = self._spawn_deck_captain()
            target_x, target_y = self._captain_arrival_waypoints[0]
            if captain.scripted_walk_toward(
                target_x, target_y, CAPTAIN_ARRIVAL_SPEED, dt
            ):
                self._captain_arrival_waypoints.pop(0)
            if not self._captain_arrival_waypoints:
                self._captain_arrival_active = False
                announcer = next(
                    (
                        npc for npc in self.npcs
                        if isinstance(npc, DeckPirateNPC)
                        and npc.npc_id == "concertina_pirate"
                    ),
                    None,
                )
                if announcer is None:
                    raise ValueError(
                        "Ship exterior deck is missing its captain announcer"
                    )
                announcer.face_toward(captain)
                self.camera.focus_on(
                    captain.x + captain.width / 2,
                    captain.y + captain.height / 2,
                )
                self._captain_after_arrival_dialogue = True
                self.game.scenes.push(DialogueScene(
                    self.game, self.dialogue.get("captain_arrival")
                ))
            self.camera.update(dt)
            return
        if self._plank_procession_active:
            assert self._plank_procession_target is not None
            reached = self.player.scripted_walk_toward(
                *self._plank_procession_target,
                PLANK_PROCESSION_SPEED,
                dt,
            )
            if reached:
                self._plank_procession_active = False
                self._plank_procession_target = None
                if self._plank_procession_phase == "to_plank":
                    self._plank_procession_phase = "warning"
                    self._show_reality_warning(resume_procession=True)
                elif self._plank_procession_phase == "to_end":
                    self._plank_procession_phase = None
                    if not self._maybe_begin_plank_ending():
                        raise ValueError(
                            "Scripted plank walk reached the endpoint "
                            "without starting its ending"
                        )
            self._update_footsteps(dt)
            self.camera.update(dt)
            return
        if self._plank_ending_phase is not None:
            self._update_plank_ending(dt)
            self.camera.update(dt)
            return

        # The Fireball has been cast: the world freezes under the blast
        # until it throws Chuck into the rubble.
        if self._fireball_t is not None:
            self._update_fireball(dt)
            self.camera.update(dt)
            return
        if not self._chef_notice_shown:
            noticing_chef = next(
                (chef for chef in self.chefs if chef.can_notice(self.player)),
                None,
            )
            if noticing_chef is not None:
                self._chef_notice_shown = True
                self.game.progress.enable("pirate_chef_met")
                self._chef_start_after_dialogue = True
                noticing_chef.face_toward(self.player)
                self.game.scenes.push(DialogueScene(
                    self.game, self.dialogue.get("pirate_chef_notice")
                ))
                return
        for cat in self.hazards:
            cat.update(dt)
        for lane in self.traffic_lanes:
            lane.update(dt)
        for rat in self.rats:
            rat.update(dt, self.player)
        for raccoon in self.raccoons:
            raccoon.update(dt, self.player)
        for kind, position in self.undead_release.release_for_row(
            self._player_tile()[1]
        ):
            self._spawn_undead(kind, position)
        for undead in self.undead:
            undead.update(dt, self.player)
        for raptor in self.raptors:
            # A raptor already chasing somebody is busy. On City Day 6
            # that is the whole tableau -- and it is also Chuck's cover,
            # so the choice has to be real rather than decorative.
            raptor.update(dt, self._raptor_quarry(raptor))
        for redcap in self.redcaps:
            redcap.update(dt, self.player)
        for dinosaur in self.dinosaurs:
            dinosaur.update(dt, self.player)
        for snake in self.snakes:
            snake.update(dt, self.player)
        for chef in self.chefs:
            chef.update(dt, self.player)
        for fencer in self.fencers:
            fencer.update(dt)
        for npc in self.npcs:
            npc.update(dt)
        for trap in self.dart_traps:
            dart = trap.update(dt)
            if dart is not None:
                self.darts.append(dart)
        for dart in self.darts:
            dart.update(dt, self.tilemap)
        self.darts = [dart for dart in self.darts if dart.alive]
        for devil in self.spined_devils:
            spine = devil.update(dt)
            if spine is not None:
                self.spines.append(spine)
        for dragon in self.blue_dragons:
            dragon.update(dt)
        if self.snow is not None:
            self.snow.update(dt)
        for spine in self.spines:
            spine.update(dt, self.tilemap)
        self.spines = [spine for spine in self.spines if spine.alive]
        for officer in self.police:
            bullet = officer.update(dt)
            if bullet is not None:
                self.bullets.append(bullet)
        for bullet in self.bullets:
            bullet.update(dt, self.tilemap)
        self.bullets = [bullet for bullet in self.bullets if bullet.alive]
        for orchid in self.spitting_orchids:
            seed = orchid.update(dt)
            if seed is not None:
                self.orchid_seeds.append(seed)
        for seed in self.orchid_seeds:
            seed.update(dt, self.tilemap)
        self.orchid_seeds = [
            seed for seed in self.orchid_seeds if seed.alive
        ]
        for skull in self.flameskulls:
            skull.update(dt)
        for actor in self.battle_actors:
            actor.update(dt)
        if self.horde is not None:
            # Before the cadences, so the ranger is aiming at where the
            # nearest orc is now rather than at where it was. Chuck's box
            # goes in so that nothing can be spawned on top of him.
            self.horde.update(dt, self.player.hitbox)
        if self.siege is not None and self.trio is not None:
            # The rest of the orc army: archers standing off, then the
            # catapult. On the encounter's clock, and pausing with it.
            self.battle_projectiles.extend(
                self.siege.update(dt, self.trio.beats_played))
        if self.battle is not None:
            tick = self.battle.update(dt)
            self.battle_projectiles.extend(tick.projectiles)
            self.battle_cones.extend(tick.cones)
            for shot in self.battle_projectiles:
                shot.update(dt, self.tilemap)
            self._resolve_horde_fire()
            self.battle_projectiles = [
                shot for shot in self.battle_projectiles if shot.alive
            ]
            for cone in self.battle_cones:
                cone.update(dt)
                if cone.just_activated:
                    # The blast lands: the hall lurches and booms.
                    self.camera.shake(config.BATTLE_CONE_SHAKE)
                    self.game.audio.play_sfx(config.BATTLE_CONE_SOUND)
            self.battle_cones = [c for c in self.battle_cones if c.alive]
        if self.trio is not None:
            # The heroes talk their way through the fight on a clock,
            # not on a trigger: Chuck is never asked to walk anywhere
            # to advance it, because walking anywhere in this room is
            # not something he can reliably do.
            beat = self.trio.update(
                dt,
                self._player_tile() if self._respawn_phase is None else None,
                self.player.hitbox,
            )
            if beat is not None:
                self.camera.focus_on(*self._battle_establishing_focus())
                self._restore_camera_to_player = True
                if self.trio.advances:
                    self.game.audio.play_sfx("vanish")
                # The last of them is the trigger. Fired here it would
                # cut the line off mid-sentence, so it waits for the
                # conversation to close -- the same way the sanctum's
                # Fireball waits for the argument that decides on it.
                self._trio_after_dialogue = self.trio.finished
                self.game.scenes.push(
                    DialogueScene(self.game, self.dialogue.get(beat)))
                return
            if self.trio.closing_in:
                # The Ashtray goes down with the ground it was standing
                # on. Left where it was it would be a save point
                # floating in the Astral Sea -- which reads as a bug
                # rather than as the west end of the arena being gone,
                # and it is the one prop in the room a player would try
                # to walk back to.
                self.anchors = [
                    anchor for anchor in self.anchors
                    if self.tilemap.terrain_at(
                        int(anchor.x) // config.TILE_SIZE,
                        int(anchor.y) // config.TILE_SIZE) != "V"
                ]
            if self.trio.collided:
                # The dragon's cue. Asked for every frame and a no-op
                # after the first, which is the same idiom the region
                # uses to carry one tune across a scene change.
                #
                # It starts here rather than on the dragon's first pass
                # because here is where the camera is: "Good enough" cuts
                # to the three of them, and a hard change of music under
                # a hard change of shot reads as one event. Two seconds
                # later, when the animal actually appears at the edge of
                # the arena, there is nothing on screen to hit.
                self.game.audio.play_music(DRAGON_MUSIC)
            if (self.trio.collided and self.red_dragon is not None
                    and self.siege is not None
                    and self.red_dragon.passes == 0
                    and self.red_dragon.aim_row is None
                    and self.siege.target_row is not None):
                # Its first pass is flown down the catapult's row: the
                # dragon's arrival is the end of the orcs' siege engine.
                self.red_dragon.aim_row = self.siege.target_row
            if self.trio.collided and self.red_dragon is not None:
                # Aimed at him, unless he is in the middle of dying --
                # the same guard the rift's advance uses, and for the
                # same reason: a pass lined up on a body is a pass
                # lined up on nothing.
                self.red_dragon.update(
                    dt,
                    self._player_tile() if self._respawn_phase is None
                    else None,
                    # ...and where he is to the pixel, for the volleys
                    # it spits while it is down. A fan aimed at the
                    # middle of his tile and a fan aimed at him are the
                    # same fan at this range; a fan aimed at nothing is
                    # the ranger's old problem again.
                    self.player.hitbox.center
                    if self._respawn_phase is None else None,
                )
                # It does not care whose side anybody is on. An orc
                # standing in the fire burns the same as Chuck would,
                # which is most of what sells the thing as weather
                # rather than as an attack aimed at the player.
                if self.horde is not None:
                    self.horde.cut_down_any(
                        self.red_dragon.lethal_rects
                        + self.red_dragon.ball_rects)
                if self.siege is not None:
                    if self.siege.burn(self.red_dragon.lethal_rects
                                       + self.red_dragon.ball_rects):
                        self.game.audio.play_sfx("fireball")
                    if (self.red_dragon.passes >= 2
                            and self.siege.catapult is not None
                            and not self.siege.catapult.wrecked):
                        # However that first pass went, the catapult
                        # does not outlast the dragon's second.
                        self.siege.catapult.wreck()
            if self.trio.collided and self.churn is not None:
                # The heroes are closing it. The desert is overwhelmed
                # by fragments of everywhere, in large sections that
                # arrive faster and faster -- and none of which can
                # hurt him, because all any of them changes is the
                # floor.
                self.churn.update(dt)
        if self.breach is not None:
            if (not self.breach.triggered
                    and self._player_tile()[0] <= config.BREACH_TRIGGER_COL):
                # Chuck is in sight of the battle: the Astral Sea breaks
                # through behind him. There is no walking away now.
                self.breach.trigger(self._player_tile())
                self.game.audio.play_sfx("vanish")
            self.breach.update(dt, self.player.hitbox)
            # Sealed in and surviving: once the clock runs out the wizard
            # resolves to cast, over his companions' protests. The camera
            # cuts to the desperate argument; the blast follows it.
            if (self.breach.triggered and not self._fireball_dialogue_shown
                    and self._fireball_t is None
                    and self._respawn_phase is None):
                self._survival_t += dt
                if self._survival_t >= config.BATTLE_FIREBALL_DELAY:
                    self._fireball_dialogue_shown = True
                    self._fireball_after_dialogue = True
                    self.camera.focus_on(*self._battle_establishing_focus())
                    self.game.scenes.push(
                        DialogueScene(self.game,
                                      self.dialogue.get("fireball_cast")))
                    return
        if self.infernal_corruption is not None:
            if (
                not self.infernal_corruption.triggered
                and self._player_tile()[1]
                <= config.INFERNAL_CORRUPTION_TRIGGER_ROW
            ):
                self.infernal_corruption.trigger(self._player_tile())
                self.game.audio.play_sfx("vanish")
                # The seal is the moment the approach stops being a walk,
                # so the realm's theme hands over to its own fight
                # arrangement here rather than at the map's edge.
                self.game.audio.play_music(FORTRESS_BATTLE_MUSIC)
            self.infernal_corruption.update(dt, self.player.hitbox)
            if (
                self.infernal_corruption.triggered
                and self.infernal_corruption.elapsed
                >= config.FEYWILD_RIVER_START_TIME
            ):
                self.feywild_river.activate()
        self.feywild_river.update(dt)
        self.reactive_flowers.update(dt, self.player.hitbox)
        for breakable in self.breakables:
            breakable.update(dt)
        self.breakables = [item for item in self.breakables if item.alive]
        for prop in self.props:
            update = getattr(prop, "update", None)
            if callable(update):
                update(dt)
        self._update_see_through_props(dt)
        self._collect_pending_drops()

        if self._climb_t is not None:
            self._update_climb(dt)
            self.camera.update(dt)
            return

        if self._respawn_phase is not None:
            self._update_respawn(dt)
            self.camera.update(dt)
            return

        if self._fall_t is not None:
            self._update_fall(dt)
            self.camera.update(dt)
            return

        if self.net_capture.active:
            self._update_net_capture(dt)
            self.camera.update(dt)
            return

        self.sanity.update(dt)
        old_player_position = (self.player.x, self.player.y)
        self.player.ground_speed_multiplier = ground_speed_multiplier(
            self.tilemap, self.player.hitbox, self.player.jumping
        )
        self.player.update(dt)
        if self.player.jump_just_started:
            self.game.audio.play_sfx("jump")
        river_block = self.feywild_river.colliding_block(
            self.player.hitbox
        )
        if river_block is not None:
            rect = river_block.rect
            self._begin_fall(
                "river",
                target=(
                    rect.centerx - self.player.width / 2,
                    rect.centery - self.player.height / 2,
                ),
            )
            self.camera.update(dt)
            return
        fall_kind = fall_zone_kind(
            self.tilemap, self.player.hitbox, self.player.jumping
        )
        if fall_kind is not None:
            self._begin_fall(fall_kind)
            self.camera.update(dt)
            return
        if self._maybe_begin_reality_breakup():
            self.camera.update(dt)
            return
        if self._maybe_begin_plank_ending():
            self.camera.update(dt)
            return
        if self._handle_traffic_contact():
            self.camera.update(dt)
            return
        if (
            self.map_name == "sewer"
            and self._player_tile()[1] > config.SEWER_JUMP_ROW
        ):
            self._jump_tutorial_complete = True

        # Walk-triggered choices (the rubble crevice): stepping into the
        # zone pops the YES/NO prompt, no interact press. It arms on entry
        # and re-arms only once Chuck has left, so a "NO" isn't re-asked
        # while he still stands there.
        player_box = self.player.hitbox
        walk_choice = next(
            (t for t in self.choice_triggers if t.walk_triggered
             and overlaps(player_box, pygame.Rect(*t.interaction_bounds()))),
            None,
        )
        if walk_choice is not None:
            if self._walk_choice_armed:
                self._walk_choice_armed = False
                choice = self.choices.get(walk_choice.choice_id)
                self.game.scenes.push(DialogueScene(
                    self.game, [choice.prompt], choice=choice,
                    dialogue=self.dialogue, on_choice=self._on_choice))
                return
        else:
            self._walk_choice_armed = True

        exit_config = AREA_WALK_EXITS.get(
            (self.map_name, self.tilemap.terrain_at(*self._player_tile()))
        )
        if exit_config is not None:
            if exit_config.confirmation is not None:
                if self._ladder_choice_armed:
                    self._ladder_choice_armed = False
                    choice = Choice(
                        prompt=exit_config.confirmation,
                        options=[
                            Option(
                                "YES",
                                goto=exit_config.destination,
                                arrival=exit_config.arrival,
                            ),
                            Option("NO"),
                        ],
                    )
                    self.game.scenes.push(DialogueScene(
                        self.game, [choice.prompt], choice=choice,
                        dialogue=self.dialogue,
                        on_choice=(
                            lambda option, exit_config=exit_config:
                            self._on_ladder_choice(option, exit_config)
                        ),
                    ))
                # NO leaves Chuck standing on the ladder without immediately
                # reopening or traversing it. Walking away rearms the prompt.
                return
            apply_cabin_door_crossing(
                self.game.progress,
                self.map_name,
                exit_config.destination,
                exit_config.arrival,
            )
            self.load_map(
                exit_config.destination,
                arrival=exit_config.arrival,
                facing=exit_config.facing,
                arrival_row=(self._player_tile()[1]
                             if exit_config.keep_row else None),
            )
            return
        self._ladder_choice_armed = True

        # One committed scratch resolves against at most one living enemy.
        if self.player.scratch_just_started:
            self.game.audio.play_sfx("scratch")
            # Closing to melee with a spined devil is simply fatal: its
            # barbs answer the scratch before Chuck's claws land.
            reach = self.player.scratch_hitbox()
            if any(overlaps(reach, devil.hitbox)
                   for devil in self.spined_devils):
                self.sanity.deplete()
                return
            enemies = [
                *self.rats, *self.raccoons, *self.undead, *self.horde_orcs,
                *self.raptors,
                *self.redcaps, *self.dinosaurs, *self.snakes,
            ]
            scratch_first_target(
                reach,
                [*self.reactive_flowers.flowers,
                 *(prop for prop in self.props
                   if callable(getattr(prop, "on_scratched", None))),
                  *self.breakables, *enemies],
                overlap_box=self.player.hitbox,
                overlap_targets=enemies,
            )
            self._collect_pending_drops()
        self.rats = [rat for rat in self.rats if rat.alive]
        self.raccoons = [enemy for enemy in self.raccoons if enemy.alive]
        self.undead = [enemy for enemy in self.undead if enemy.alive]
        self.raptors = [raptor for raptor in self.raptors if raptor.alive]
        self.redcaps = [redcap for redcap in self.redcaps if redcap.alive]
        self.dinosaurs = [dinosaur for dinosaur in self.dinosaurs
                          if dinosaur.alive]
        self.snakes = [snake for snake in self.snakes if snake.alive]

        blocking_rat = next(
            (rat for rat in self.rats if overlaps(self.player.hitbox, rat.hitbox)),
            None,
        )
        if blocking_rat is not None:
            if self.sanity.damage(blocking_rat.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position

        blocking_raccoon = next(
            (enemy for enemy in self.raccoons
             if overlaps(self.player.hitbox, enemy.hitbox)),
            None,
        )
        if blocking_raccoon is not None:
            if self.sanity.damage(blocking_raccoon.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position

        blocking_undead = next(
            (enemy for enemy in self.undead
             if overlaps(self.player.hitbox, enemy.hitbox)),
            None,
        )
        if blocking_undead is not None:
            if self.sanity.damage(blocking_undead.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position

        # The horde is not coming for him, but it is in his way. This is
        # the weave the room is made of: their paths converge on two
        # points and he has to cross them.
        blocking_orc = next(
            (orc for orc in self.horde_orcs
             if overlaps(self.player.hitbox, orc.hitbox)),
            None,
        )
        if blocking_orc is not None:
            if self.sanity.damage(blocking_orc.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position
        if self.siege is not None and self.siege.blocks(self.player.hitbox):
            # The catapult is a thing in the way, not a thing that hurts.
            self.player.x, self.player.y = old_player_position

        blocking_raptor = next(
            (raptor for raptor in self.raptors
             if overlaps(self.player.hitbox, raptor.hitbox)),
            None,
        )
        if blocking_raptor is not None:
            if self.sanity.damage(blocking_raptor.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position

        blocking_redcap = next(
            (redcap for redcap in self.redcaps
             if overlaps(self.player.hitbox, redcap.hitbox)),
            None,
        )
        if blocking_redcap is not None:
            if self.sanity.damage(blocking_redcap.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position

        blocking_dinosaur = next(
            (dinosaur for dinosaur in self.dinosaurs
             if overlaps(self.player.hitbox, dinosaur.hitbox)),
            None,
        )
        if blocking_dinosaur is not None:
            if self.sanity.damage(blocking_dinosaur.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position

        blocking_snake = next(
            (snake for snake in self.snakes
             if overlaps(self.player.hitbox, snake.hitbox)),
            None,
        )
        if blocking_snake is not None:
            if self.sanity.damage(blocking_snake.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position

        blocking_chef = next(
            (chef for chef in self.chefs
             if overlaps(self.player.hitbox, chef.hitbox)),
            None,
        )
        if blocking_chef is not None:
            if self.sanity.damage(blocking_chef.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position

        blocking_fencer = next(
            (fencer for fencer in self.fencers
             if overlaps(self.player.hitbox, fencer.hitbox)),
            None,
        )
        if blocking_fencer is not None:
            if self.sanity.damage(blocking_fencer.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
            self.player.x, self.player.y = old_player_position

        # Talking: interact probes one tile ahead of Chuck.
        if self.game.input.was_pressed("interact"):
            target = self._interactable_in_range()
            if target is not None:
                choice_id = getattr(target, "choice_id", None)
                if choice_id is not None:
                    # A question, not a statement: the grate.
                    choice = self.choices.get(choice_id)
                    self.game.scenes.push(
                        DialogueScene(
                            self.game,
                            [choice.prompt],
                            choice=choice,
                            dialogue=self.dialogue,
                            on_choice=self._on_choice,
                        )
                    )
                    return
                # NPCs turn to face Chuck; props just talk.
                interact = getattr(target, "interact", None)
                dialogue_id = (
                    interact(self.player)
                    if callable(interact)
                    else target.dialogue_id
                )
                if dialogue_id is None:
                    # Action-only interactables (the captain's chest) alter
                    # the world directly and never open a dialogue overlay.
                    self._collect_pending_drops()
                    return
                if dialogue_id == BOBERT_AWAKE_LINE:
                    self._talk_to_bobert()
                    return
                if target in self.npcs:
                    dialogue_id = self._second_word(target, dialogue_id)
                lines = list(self.dialogue.get(dialogue_id))
                if self._points_at_the_cheese(target):
                    lines += self.dialogue.get(PANTRY_CHEESE_HINT)
                self.game.scenes.push(DialogueScene(self.game, lines))
                return  # the world holds its breath

        player_box = self.player.hitbox

        for dart in self.darts:
            if dart.alive and overlaps(player_box, dart.hitbox):
                dart.alive = False
                if self.sanity.damage(dart.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
        self.darts = [dart for dart in self.darts if dart.alive]

        # The dragon's lane, while it is lit. Nothing is consumed and
        # nothing dies: the bolt simply hurts whoever is standing in it,
        # and the cooldown is what stops it emptying Sanity at once.
        for dragon in self.blue_dragons:
            if dragon.lethal and overlaps(player_box, dragon.strike):
                if self.sanity.damage(dragon.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
        # ...and the red one's trail, which is the same contract in
        # motion: nothing is consumed, nothing dies, and the cooldown is
        # what stops it emptying Sanity in one stride.
        if self.red_dragon is not None:
            # The stripe costs more than a ball: one is a wall he chose
            # to stand in, the other is one of four things that came at
            # him while he was dealing with the other three.
            burn = self.red_dragon.damage_for(player_box)
            if burn and self.sanity.damage(burn):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
        if self.siege is not None:
            # A rolling rock on its way to the heroes.
            knock = self.siege.damage_for(player_box)
            if knock and self.sanity.damage(knock):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
        for spine in self.spines:
            if spine.alive and overlaps(player_box, spine.hitbox):
                spine.alive = False
                if self.sanity.damage(spine.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
        self.spines = [spine for spine in self.spines if spine.alive]

        for seed in self.orchid_seeds:
            if seed.alive and overlaps(player_box, seed.hitbox):
                seed.alive = False
                if self.sanity.damage(seed.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
        self.orchid_seeds = [
            seed for seed in self.orchid_seeds if seed.alive
        ]

        # Flameskulls cannot be cleared: they only ever cost Sanity.
        for skull in self.flameskulls:
            if overlaps(player_box, skull.hitbox):
                if self.sanity.damage(skull.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
                break
        for devil in self.spined_devils:
            if overlaps(player_box, devil.hitbox):
                if self.sanity.damage(devil.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
                break
        for officer in self.police:
            if overlaps(player_box, officer.hitbox):
                if self.sanity.damage(officer.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
                break
        for bullet in self.bullets:
            if bullet.alive and overlaps(player_box, bullet.hitbox):
                bullet.alive = False
                if self.sanity.damage(bullet.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
                break
        # Spent rounds leave immediately, exactly as spines do, so a
        # bullet can never land twice on its way out of the list.
        self.bullets = [bullet for bullet in self.bullets if bullet.alive]

        for shot in self.battle_projectiles:
            if shot.alive and overlaps(player_box, shot.hitbox):
                shot.alive = False
                if self.sanity.damage(shot.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
        self.battle_projectiles = [
            shot for shot in self.battle_projectiles if shot.alive
        ]
        if self.battle is not None:
            slash = self.battle.slash_hitbox()
            if slash is not None and overlaps(player_box, slash):
                if self.sanity.damage(config.BATTLE_SLASH_SANITY_DAMAGE):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
        for cone in self.battle_cones:
            if cone.contains(player_box):
                if self.sanity.damage(config.BATTLE_CONE_SANITY_DAMAGE):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
                break

        self._check_net_capture()
        terrain_hazard = touching_terrain_hazard(
            self.tilemap, player_box, self.player.jumping
        )
        if terrain_hazard is not None and self.sanity.damage(
            terrain_hazard.sanity_damage
        ):
            self.player.hurt_blink = config.HURT_COOLDOWN
            self.game.audio.play_sfx("hurt")

        # Pickups: collect on overlap, then drop dead ones.
        for pickup in self.pickups:
            if pickup.alive and overlaps(player_box, pickup.hitbox):
                pickup.on_collect(self.sanity, self.game.cigarettes)
                self.game.audio.play_sfx("pickup")
        self.pickups = [p for p in self.pickups if p.alive]

        self._update_footsteps(dt)

        # Anchors: touching one still banks a save, and no longer moves
        # where Chuck comes back to. The door he walked in by is the
        # respawn point now, on every map -- measured, that costs a
        # median of 1.7 tiles of walking against coming back to the
        # Ashtray, because the fights are deep in the maps and the walk
        # was already long. The Anchor itself goes shortly.
        for anchor in self.anchors:
            if not anchor.lit and overlaps(player_box, anchor.hitbox):
                for other in self.anchors:
                    other.lit = False
                anchor.lit = True
                self.game.checkpoints.activate_checkpoint(
                    anchor.checkpoint_id, self.sanity.current
                )
                self.game.audio.play_sfx("chime")  # singular.

        # Hazards: contact costs sanity (i-frames prevent draining).
        for cat in self.hazards:
            if overlaps(player_box, cat.hitbox):
                if self.sanity.damage(cat.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")

        self.camera.update(dt)  # after movement, so it tracks this frame

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the world through the camera offset."""
        surface.fill(config.COLOR_BLACK)
        offset = self.camera.offset
        if self.map_name == "ship_exterior_deck":
            # Sea stays fixed while ship geometry and every occupant share the
            # same one-pixel, shanty-tempo bob. Physics remains unshifted.
            self.tilemap.draw_ground(
                surface, offset, self._world_time,
                include_chars=frozenset({"~"}),
            )
            if self.reality_blocks is not None:
                # Reality fragments belong to the wrong sea, not the rocking
                # ship, so they keep the ocean/camera frame beneath the hull.
                self.reality_blocks.draw(surface, offset)
            rock_x, rock_y = deck_rock_offset(self._world_time)
            offset = (offset[0] - rock_x, offset[1] - rock_y)
            self.tilemap.draw_ground(
                surface, offset, self._world_time,
                exclude_chars=frozenset({"~"}),
            )
        else:
            self.tilemap.draw_ground(surface, offset, self._world_time)
        self.feywild_river.draw(surface, offset)
        self.reactive_flowers.draw(surface, offset)
        for prop in self.props:
            if getattr(prop, "floor_layer", False):
                prop.draw(surface, offset)
        for pickup in self.pickups:  # flat ground litter, under everyone
            pickup.draw(surface, offset)
        if self.red_dragon is not None:
            # The burning ground goes under everything standing on it,
            # so a player can see their own feet in the fire.
            self.red_dragon.draw_ground(surface, offset)
        if self.siege is not None:
            # Rolling rocks and the shadows of the ones still in the air.
            self.siege.draw_ground(surface, offset)
        for drawable in self._sorted_drawables():
            drawable.draw(surface, offset)
        if self.siege is not None:
            self.siege.draw_air(surface, offset)
        if self.red_dragon is not None and not self.red_dragon.on_the_ground:
            # In the air it goes over everything, because it is not
            # standing on the floor at all. Sorting it by its feet the
            # way the rest of the room is sorted would put a flying
            # dragon behind a waist-high rock. On the ground it is in
            # the sorted pass instead -- see `_sorted_drawables`.
            self.red_dragon.draw(surface, offset)
        if self.breach is not None:
            self.breach.draw(surface, offset)
        if self.trio is not None:
            self.trio.draw(surface, offset)
        if self.churn is not None:
            self.churn.draw(surface, offset)
        if self.infernal_corruption is not None:
            self.infernal_corruption.draw(surface, offset)
        for cone in self.battle_cones:
            cone.draw(surface, offset)
        self.tilemap.draw_overhead(surface, offset, self._world_time,
                                   self._overhead_veils)
        if self.street_lights is not None:
            # After the overhead pass and before the HUD: the lamps light
            # the street, not the interface.
            self.street_lights.draw(surface, offset)
        if self.aurora is not None:
            # After the overhead pass and before the HUD: the projector
            # lights the room, not the interface.
            self.aurora.draw(surface, offset)
            # ...and the map goes back on top of it, undimmed. It is
            # the reason the lights are off; it cannot be one of the
            # things the dark falls on.
            for prop in self.props:
                if prop.kind == "cabin_table_awakened":
                    prop.draw_region(surface, offset, MAP_SPRITE_REGION)
        if self.city_rain is not None:
            self.city_rain.draw(surface)
        if self.snow is not None:
            # Over the world and under the HUD, and masked to the snow
            # it belongs to -- which is why it needs the map and the
            # camera rather than just the screen.
            self.snow.draw(surface, offset, self.tilemap)
        self.hud.draw(surface)
        # Tutorial hint (temporary; Waterdeep + sewer only). Hidden
        # while a dialogue is open — it has already been taken up on.
        if (
            self._hint is not None
            and self.game.scenes.current is self
            and self._fall_t is None
            and self._climb_t is None
        ):
            if self._jump_hint_visible():
                self._hint.draw(surface, config.HINT_JUMP)
            elif self._scratch_hint_visible():
                self._hint.draw(surface, config.HINT_SCRATCH)
            elif self._anchor_hint_visible():
                self._hint.draw(surface, config.HINT_ANCHOR)
            elif self._interactable_in_range() is not None:
                self._hint.draw(surface, config.HINT_INTERACT)
        self._draw_net_overlay(surface, offset)
        self._draw_respawn_overlay(surface)
        self._draw_arrival_fade(surface)
        self._draw_river_escape_boundary(surface)
        self._draw_fireball(surface)

    def _battle_establishing_focus(self) -> tuple[float, float]:
        """The camera center that frames the whole battle for its lines.

        Horizontally centered on the actors' span; vertically lifted so
        the group's feet clear the dialogue panel at the screen bottom.
        """
        actors = self.battle_actors
        center_x = (min(a.x for a in actors)
                    + max(a.x + a.width for a in actors)) / 2
        # Put the group's feet a little below screen-center, leaving the
        # bottom of the frame (the dialogue panel) clear of the actors.
        group_bottom = max(a.y + a.height for a in actors)
        center_y = group_bottom - config.SANCTUM_ESTABLISH_LIFT
        return center_x, center_y

    def _begin_fireball(self) -> None:
        """The wizard casts Fireball: the fight ends, scripted."""
        self._fireball_t = 0.0
        self._fireball_halved = False
        for actor in self.battle_actors:
            actor.attack_flash = config.BATTLE_ATTACK_FLASH
        self.camera.shake(config.FIREBALL_SHAKE)
        self.game.audio.play_sfx(config.FIREBALL_SOUND)

    def _update_fireball(self, dt: float) -> None:
        """Advance the scripted explosion, then throw Chuck to the rubble."""
        self._fireball_t += dt
        if (not self._fireball_halved
                and self._fireball_t >= config.FIREBALL_FLASH_PEAK):
            # The blast lands: Chuck is cut to (at most) half Sanity. It
            # never heals him — only the explosion's toll.
            self._fireball_halved = True
            capped = int(self.sanity.maximum * config.FIREBALL_SANITY_FRACTION)
            self.sanity.current = min(self.sanity.current, capped)
        if self._fireball_t >= config.FIREBALL_DURATION:
            self._fireball_t = None
            self._pending_map = "temple_rubble"
            self._pending_arrival = "from_fireball"
            self._pending_fade_in = True  # come to, dazed, in the rubble

    def _draw_fireball(self, surface) -> None:
        """The explosion: a bloom from the wizard, then a white-out."""
        t = self._fireball_t
        if t is None:
            return
        w, h = surface.get_size()
        peak = config.FIREBALL_FLASH_PEAK
        if t < peak:
            frac = t / peak
            wizard = next((a for a in self.battle_actors
                           if a.kind == "wizard"), None)
            ox, oy = self.camera.offset
            if wizard is not None:
                cx = int(wizard.center_x - ox)
                cy = int(wizard.center_y - oy)
            else:
                cx, cy = w // 2, h // 2
            radius = int(frac * max(w, h) * 1.4)
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (250, 150, 40, 230), (cx, cy), radius)
            pygame.draw.circle(overlay, (255, 236, 190, 245),
                               (cx, cy), int(radius * 0.6))
            surface.blit(overlay, (0, 0))
        else:
            # The white-out that masks the throw into the rubble.
            frac = (t - peak) / max(1e-4, config.FIREBALL_DURATION - peak)
            overlay = pygame.Surface((w, h))
            overlay.fill((255, 244, 224))
            overlay.set_alpha(int(255 * min(1.0, 0.5 + frac)))
            surface.blit(overlay, (0, 0))

    def _prop_centre(self, wanted: str) -> tuple[float, float] | None:
        """Middle of one authored prop in world pixels, if the map has it."""
        for kind, col, row in self.tilemap.prop_tiles:
            if kind == wanted:
                ts = config.TILE_SIZE
                return (col * ts + ts / 2, row * ts + ts / 2)
        return None

    def _open_row_near(self, centre_x: float, row: int,
                       fallback_y: float) -> float:
        """The centre y of the open tile nearest ``row`` in this column.

        For arrivals along a whole map edge. The row Chuck left the last
        map on may be a building on this one, so the search walks out
        from it a row at a time, nearer rows first, and falls back to the
        arrival marker itself if the whole column is closed.
        """
        ts = config.TILE_SIZE
        col = int(centre_x // ts)
        height = self.tilemap.height_tiles
        for distance in range(height):
            for candidate in (row - distance, row + distance):
                if 0 <= candidate < height \
                        and not self.tilemap.is_solid(col, candidate):
                    return candidate * ts + ts / 2
        return fallback_y

    def _update_see_through_props(self, dt: float) -> None:
        """Thin anything big enough to hide Chuck while he is under it.

        The great trees, the ship's sails, the arches and the cabin as
        props, and every canopy drawn over the world as overhead tiles --
        market awnings, the city gate, palm crowns, the jungle's exit
        canopy, the Feywild's hedge openings.

        Chuck and nobody else. This used to fade for anyone with feet, on
        the grounds that an enemy vanishing under an awning is a hit the
        player cannot see coming -- but in practice what it mostly did
        was flicker: the sails over the ship went half transparent every
        time a fencer walked his loop behind them, and Chult's dinosaur
        thinned out a tree from across the map with Chuck nowhere near
        it. A canopy that fades for things the player is not doing reads
        as a bug in the canopy. The cases it was guarding against are
        rare, and the pursuers big enough to matter are bigger than
        anything they could hide behind anyway.
        """
        from src.entities.prop import SEE_THROUGH_RATE

        walkers = [self.player]
        for prop in self.props:
            if getattr(prop, "see_through", False):
                prop.update_veil(walkers, dt)

        covered: set[int] = set()
        for walker in walkers:
            box = walker.hitbox
            # The sprite stands up above its feet: a rat whose head is
            # under the canvas is under the canvas.
            reach = pygame.Rect(box.left, box.top - 12, box.width,
                                box.height + 12)
            covered |= self.tilemap.overhead_regions_over(reach)
        step = SEE_THROUGH_RATE * dt
        for region in covered | set(self._overhead_veils):
            veil = self._overhead_veils.get(region, 0.0)
            veil = min(1.0, veil + step) if region in covered \
                else max(0.0, veil - step)
            if veil > 0.0:
                self._overhead_veils[region] = veil
            else:
                self._overhead_veils.pop(region, None)

    def _sorted_drawables(self):
        """Everything that stands in the world, painter-ordered by feet.

        Lower on screen draws later, so characters correctly pass in
        front of and behind props, anchors, and each other. Chuck is
        one foot tall; this is where that finally SHOWS.
        """
        standing_props = [
            prop for prop in self.props
            if not getattr(prop, "floor_layer", False)
        ]
        drawables = [*standing_props, *self.breakables, *self.anchors,
                     *self.reactive_flowers.flowers,
                     *self.battle_actors,
                     *self.hazards, *self.rats, *self.raccoons,
                      *self.undead, *self.horde_orcs,
                     *self.raptors, *self.dinosaurs,
                     *self.redcaps, *self.snakes, *self.chefs, *self.fencers,
                     *self.spined_devils, *self.police, *self.flameskulls,
                     *self.spitting_orchids,
                     *self.traffic_vehicles,
                     *self.darts, *self.spines, *self.bullets,
                     *self.blue_dragons,
                     *self.orchid_seeds,
                     *self.battle_projectiles,
                     *self.grounded_dragon,
                     *(self.siege.drawables if self.siege is not None
                       else ()),
                     *self.npcs, self.player]
        return sorted(drawables, key=lambda d: d.sort_y)

    @property
    def grounded_dragon(self):
        """The red dragon, but only while it is standing on the floor.

        In the air it is drawn over the whole room. Down, it has to sort
        with everything else that has feet, or eight tiles of red sit on
        top of Chuck for seven seconds -- and the one rule this arena is
        held to above every other is that he stays readable.
        """
        if self.red_dragon is None or not self.red_dragon.on_the_ground:
            return []
        return [self.red_dragon]

    @property
    def horde_orcs(self):
        """The living horde, or nothing on the maps that have none."""
        orcs = self.horde.orcs if self.horde is not None else []
        if self.siege is not None:
            # The archers and the catapult's crew are orcs in his way
            # the same as the horde is.
            orcs = [*orcs, *self.siege.bodies]
        return orcs

    def _resolve_horde_fire(self) -> None:
        """The ranger's arrows landing. One arrow, one orc.

        Only her arrows and only the horde: the garrison that has
        noticed Chuck is his problem, and a room where stray hero fire
        cleared it for him would take away the thing he is dodging.
        """
        if self.horde is None:
            return
        for shot in self.battle_projectiles:
            if not shot.alive or shot.kind != "arrow":
                continue
            hit = next((orc for orc in self.horde.orcs
                        if overlaps(shot.hitbox, orc.hitbox)), None)
            if hit is not None:
                self.horde.kill(hit)
                shot.alive = False

    @property
    def _waterdeep_midday(self) -> bool:
        return (self.map_name in {"waterdeep_docks", "waterdeep_plaza"}
                and self.game.progress.has(WATERDEEP_RETURN_FLAG))

    @property
    def after_dark(self) -> bool:
        """Is this one of the city's night blocks?

        Taken from which sheet the map draws with rather than from its
        name. The night and day cities are the same streets at different
        hours and their maps are near-identical; the tileset is the one
        place the difference is already recorded, so it is the one place
        worth asking.
        """
        return MAP_TILESET.get(self.map_name) == "city"

    @property
    def traffic_vehicles(self):
        return [
            vehicle
            for lane in self.traffic_lanes
            for vehicle in lane.vehicles
        ]

    def _handle_traffic_contact(self) -> bool:
        """Apply a severe road hit and return Chuck to his last sidewalk."""
        vehicle = next(
            (
                vehicle for vehicle in self.traffic_vehicles
                if overlaps(self.player.hitbox, vehicle.hitbox)
            ),
            None,
        )
        if vehicle is not None:
            if self.sanity.damage(vehicle.damage):
                self.player.hurt_blink = config.HURT_COOLDOWN
                self.game.audio.play_sfx("hurt")
                self.camera.shake(3.0)
            # A car never carries Chuck, embeds him, or shoves him out of the
            # map. Like a Frogger miss, the hit returns him to the last safe
            # non-road footing while normal Sanity/respawn rules continue.
            self.player.x, self.player.y = self._traffic_safe_position
            return True

        center_col, center_row = self._player_tile()
        if self.tilemap.terrain_at(center_col, center_row) not in ROAD_TERRAIN:
            self._traffic_safe_position = (self.player.x, self.player.y)
        return False

    def _spawn_deck_captain(self) -> DeckPirateNPC:
        """Materialize the authored captain once the confrontation is due."""
        existing = next(
            (
                npc for npc in self.npcs
                if isinstance(npc, DeckPirateNPC)
                and npc.npc_id == "captain_pirate"
            ),
            None,
        )
        if existing is not None:
            return existing
        if self._deck_captain_spawn is None:
            raise ValueError(
                "Ship exterior deck is missing its authored captain marker"
            )
        cx, cy, npc_id, progress_flag, performance = self._deck_captain_spawn
        captain = DeckPirateNPC(
            cx, cy, npc_id=npc_id,
            progress=self.game.progress,
            progress_flag=progress_flag,
            performance=performance,
        )
        captain.load_sprites(self.game.assets)
        self.npcs.append(captain)
        return captain

    def _begin_captain_arrival(self) -> None:
        """Bring the captain up at midship and walk him to the stern helm."""
        if self._deck_captain_spawn is None:
            raise ValueError(
                "Ship exterior deck is missing its authored captain marker"
            )
        arrival = next(
            (
                position for kind, position in self.tilemap.object_spawns
                if kind == "arrival:from_crew_quarters"
            ),
            None,
        )
        if arrival is None:
            raise ValueError(
                "Ship exterior deck is missing its crew-quarters arrival"
            )
        captain = self._spawn_deck_captain()
        captain.x = arrival[0] - captain.width / 2
        captain.y = arrival[1] - captain.height / 2
        target_cx, target_cy = self._deck_captain_spawn[:2]
        target_x = target_cx - captain.width / 2
        target_y = target_cy - captain.height / 2
        # Step clear of the ladder and Ashtray, cross the open lower deck,
        # then step north to the helm. This also avoids cutting diagonally
        # through the western mast and Jeffries.
        deck_lane_y = target_y + config.TILE_SIZE
        self._captain_arrival_waypoints = [
            (captain.x, deck_lane_y),
            (target_x, deck_lane_y),
            (target_x, target_y),
        ]
        self._captain_arrival_active = True
        self.camera.follow(captain)

    def _stage_deck_plank(self) -> None:
        if self._deck_plank_origin is None:
            raise ValueError(
                "Ship exterior deck is missing its authored plank origin"
            )
        stage_deck_plank(self.tilemap, self._deck_plank_origin)

    def _apply_post_confrontation_tableau(self) -> None:
        """Place the captain and objecting pirate around the plank approach."""
        if self._deck_plank_origin is None:
            raise ValueError(
                "Ship exterior deck is missing its authored plank origin"
            )
        captain = self._spawn_deck_captain()
        objector = next(
            (
                npc for npc in self.npcs
                if isinstance(npc, DeckPirateNPC)
                and npc.npc_id == "cheering_pirate"
            ),
            None,
        )
        if objector is None:
            raise ValueError("Ship exterior deck is missing its objecting pirate")
        col, rail_row = self._deck_plank_origin
        ts = config.TILE_SIZE

        def place(entity, tile_col: int, tile_row: int) -> None:
            entity.x = tile_col * ts + (ts - entity.width) / 2
            entity.y = tile_row * ts + (ts - entity.height) / 2

        place(captain, col - 3, rail_row - 2)
        place(objector, col + DECK_PLANK_WIDTH + 2, rail_row - 2)
        captain.facing = "right"
        objector.facing = "left"

    def _begin_plank_procession(self) -> None:
        """Begin the uninterrupted walk from the accusation to the plank."""
        self._stage_deck_plank()
        self._apply_post_confrontation_tableau()
        assert self._deck_plank_origin is not None
        col, rail_row = self._deck_plank_origin
        ts = config.TILE_SIZE
        plank_center_x = (col + DECK_PLANK_WIDTH / 2) * ts
        self.player.x = plank_center_x - self.player.width / 2
        self.player.y = (
            (rail_row - 5) * ts + (ts - self.player.height) / 2
        )
        self.player.jump_remaining = 0.0
        self.player.scratch_remaining = 0.0
        self.player.facing = "down"
        self._plank_procession_target = (
            self.player.x,
            rail_row * ts + (ts - self.player.height) / 2,
        )
        self._plank_procession_phase = "to_plank"
        self._plank_procession_active = True
        self.camera.follow(self.player)

    def _continue_plank_procession(self) -> None:
        """Walk Chuck from Jeffries' warning to the plank's outer tile."""
        if self._deck_plank_origin is None:
            raise ValueError(
                "Ship exterior deck is missing its authored plank origin"
            )
        col, first_row = self._deck_plank_origin
        last_row = first_row + DECK_PLANK_LENGTH - 1
        ts = config.TILE_SIZE
        plank_center_x = (col + DECK_PLANK_WIDTH / 2) * ts
        self.player.x = plank_center_x - self.player.width / 2
        self._plank_procession_target = (
            self.player.x,
            last_row * ts + (ts - self.player.height) / 2,
        )
        self._plank_procession_phase = "to_end"
        self._plank_procession_active = True
        self.camera.follow(self.player)

    def _on_choice(self, option) -> None:
        """What a decision means. The scene reports; the world acts.

        A `goto` option carries Chuck to another map. It may also name an
        arrival marker and restrained arrival choreography. We only record
        the transition here; DialogueScene closes itself, and the actual
        load happens back in update() once it has.
        """
        action = getattr(option, "action", None)
        self.last_choice = option.dialogue or option.goto or action
        if action is not None:
            self._pending_choice_action = action
        if option.goto is not None:
            self._pending_map = option.goto
            self._pending_arrival = option.arrival
            self._pending_facing = option.facing
            self._pending_climb_from_water = option.climb_from_water

    def _on_ladder_choice(self, option, exit_config) -> None:
        """Route a confirmed ladder through the ordinary area-exit record."""
        self._on_choice(option)
        if option.goto is not None:
            self._pending_facing = exit_config.facing

    def _maybe_begin_reality_breakup(self) -> bool:
        """Reveal wrong-map blocks when Chuck first commits to the plank."""
        field = self.reality_blocks
        origin = self._deck_plank_origin
        if (
            field is None
            or origin is None
            or field.active
            or self._reality_warning_shown
            or not self.game.progress.has(CAPTAIN_CONFRONTED_FLAG)
        ):
            return False
        col, row = self._player_tile()
        plank_col, first_row = origin
        if not (
            plank_col <= col < plank_col + DECK_PLANK_WIDTH
        ) or not (
            first_row <= row < first_row + DECK_PLANK_LENGTH
        ):
            return False

        self._show_reality_warning()
        return True

    def _show_reality_warning(self, *, resume_procession: bool = False) -> None:
        """Activate the streamed fragments and present Jeffries' warning."""
        if self.reality_blocks is None:
            raise ValueError("Ship exterior deck is missing its reality field")
        self.reality_blocks.activate()
        self._reality_warning_shown = True
        self._plank_after_warning_dialogue = resume_procession
        self.game.scenes.push(DialogueScene(
            self.game,
            self.dialogue.get("jeffries_reality_warning"),
        ))

    def _maybe_begin_plank_ending(self) -> bool:
        """Lock the endpoint once Chuck reaches the end of the live plank."""
        field = self.reality_blocks
        origin = self._deck_plank_origin
        if (
            field is None
            or origin is None
            or not field.active
            or not self._reality_warning_shown
            or self._plank_ending_phase is not None
        ):
            return False
        col, row = self._player_tile()
        plank_col, first_row = origin
        last_row = first_row + DECK_PLANK_LENGTH - 1
        if (
            not plank_col <= col < plank_col + DECK_PLANK_WIDTH
            or row != last_row
        ):
            return False

        captain = self._spawn_deck_captain()
        ts = config.TILE_SIZE
        plank_center_x = (plank_col + DECK_PLANK_WIDTH / 2) * ts
        self.player.x = plank_center_x - self.player.width / 2
        target_x = plank_center_x - captain.width / 2
        target_y = (last_row - 2) * ts + (ts - captain.height) / 2
        # First cross the deck to the plank centerline, then walk straight
        # behind Chuck. This avoids a diagonal shortcut across open sea.
        self._plank_ending_waypoints = [
            (target_x, captain.y),
            (target_x, target_y),
        ]
        self._plank_ending_phase = "approach"
        self._plank_ending_t = 0.0
        self.player.moving = False
        self.player.jump_remaining = 0.0
        self.player.scratch_remaining = 0.0
        self.player.facing = "down"
        self.camera.focus_on(
            self.player.x + self.player.width / 2,
            self.player.y + self.player.height / 2,
        )
        return True

    def _update_plank_ending(self, dt: float) -> None:
        """Walk the captain in, kick Chuck, and land in a streamed block."""
        assert self.reality_blocks is not None
        captain = self._spawn_deck_captain()
        phase = self._plank_ending_phase

        if phase == "approach":
            target = self._plank_ending_waypoints[0]
            if captain.scripted_walk_toward(
                *target, PLANK_KICK_APPROACH_SPEED, dt
            ):
                self._plank_ending_waypoints.pop(0)
            if not self._plank_ending_waypoints:
                captain.facing = "down"
                self._plank_ending_phase = "wait"
            return

        captain.update(dt)
        if phase == "wait":
            player_screen_x = (
                self.player.x + self.player.width / 2 - round(self.camera.x)
            )
            player_screen_bottom = (
                self.player.y + self.player.height - round(self.camera.y)
            )
            candidates = []
            for block in self.reality_blocks.visible_blocks:
                if block.kind != "hell" or block.screen_y < player_screen_bottom:
                    continue
                block_x, _block_y = self.reality_blocks.position(block)
                if block_x <= player_screen_x <= block_x + block.width:
                    candidates.append(block)
            if not candidates:
                return
            self._plank_ending_block = min(
                candidates, key=lambda block: block.screen_y
            )
            self._plank_ending_start = (self.player.x, self.player.y)
            self._plank_ending_phase = "kick"
            self._plank_ending_t = 0.0
            self._plank_kick_sounded = False
            captain.kick_progress = 0.0
            return

        if phase != "kick":
            return
        assert self._plank_ending_block is not None
        assert self._plank_ending_start is not None
        previous = self._plank_ending_t
        self._plank_ending_t += dt
        captain.kick_progress = min(
            1.0, self._plank_ending_t / PLANK_KICK_WINDUP
        )
        if (
            not self._plank_kick_sounded
            and previous < PLANK_KICK_WINDUP <= self._plank_ending_t
        ):
            self._plank_kick_sounded = True
            self.game.audio.play_sfx("hurt")
            self.camera.shake(2.0)

        fall_progress = min(
            1.0,
            max(0.0, self._plank_ending_t - PLANK_KICK_WINDUP)
            / PLANK_KICK_FALL_DURATION,
        )
        if fall_progress <= 0.0:
            return
        eased = fall_progress * fall_progress * (3.0 - 2.0 * fall_progress)
        block_x, block_y = self.reality_blocks.position(
            self._plank_ending_block
        )
        rock_x, rock_y = deck_rock_offset(self._world_time)
        target_x = (
            block_x + self._plank_ending_block.width / 2
            + round(self.camera.x) - rock_x - self.player.width / 2
        )
        target_y = (
            block_y + self._plank_ending_block.height / 2
            + round(self.camera.y) - rock_y - self.player.height / 2
        )
        start_x, start_y = self._plank_ending_start
        self.player.x = start_x + (target_x - start_x) * eased
        self.player.y = start_y + (target_y - start_y) * eased
        self.player.fall_progress = eased
        if fall_progress < 1.0:
            return

        captain.kick_progress = None
        self.player.visible = False
        from src.scenes.hell_falling_cutscene_scene import (
            HellFallingCutsceneScene,
        )
        self.game.scenes.replace(
            HellFallingCutsceneScene(self.game, sanity=self.sanity.current)
        )

    def _points_at_the_cheese(self, target) -> bool:
        """In the pantry, every plain object says where the cheese is.

        The way on from the pantry is a jump into the sky to the cheese in
        the middle of the room, and nothing about a hole in the floor says
        "jump in". So the things Chuck looks at while he is working it out
        -- the barrels, crates, sacks, baskets, the door -- all end on the
        same nudge. The cheese itself does not, and neither do the jars
        and shelves: they are for scratching.
        """
        return (self.map_name == "waterdeep_pantry"
                and target in self.props
                and getattr(target, "kind", None) != "cheese")

    def _talk_to_bobert(self) -> None:
        """The end of the game: Bobert asks after the smokes.

        With all three cartons of premium Buhetian halfling leaf, Chuck
        has brought back something worth coming home with and Bobert says
        so; without them the question just hangs. Either way the docks
        fade slowly to black when he is done talking.
        """
        from src.entities.captain_chest import (
            PREMIUM_CARTON_FLAGS, premium_cartons_collected)
        from src.scenes.ending_scene import EndingScene

        good = (premium_cartons_collected(self.game.progress)
                >= len(PREMIUM_CARTON_FLAGS))

        def end() -> None:
            self.game.scenes.push(EndingScene(self.game, good=good))

        def after_question() -> None:
            if not good:
                end()
                return
            self.game.scenes.push(DialogueScene(
                self.game, self.dialogue.get(BOBERT_CARTONS_LINE),
                on_close=end))

        self.game.scenes.push(DialogueScene(
            self.game, self.dialogue.get(BOBERT_AWAKE_LINE),
            on_close=after_question))

    def _second_word(self, npc, dialogue_id: str) -> str:
        """The same person, spoken to again, says something else.

        Driven entirely by the writing: a person whose line has a
        ``<line>_repeat`` sibling in data/dialogue says the first one the
        first time and the second one every time after. Anyone without a
        repeat line -- Waterdeep's guards, by design -- just says their
        one line again.

        Remembered per person, not per line, because several townsfolk
        share a line: the second browser outside the market should still
        get a first word in. And remembered for the session rather than
        the visit, so walking out of the tavern and back in does not make
        the bartender forget he already told you about the cheese.
        """
        repeat = f"{dialogue_id}_repeat"
        if not self.dialogue.has(repeat):
            return dialogue_id
        spoken = self.game.spoken_to
        key = (self.map_name, round(npc.x), round(npc.y), dialogue_id)
        if key in spoken:
            return repeat
        spoken.add(key)
        return dialogue_id

    def _interactable_in_range(self):
        """The NPC, prop or ground Chuck could talk to right now, or None.

        The interact key and the tutorial hint both read this, so the
        hint can never promise something E won't deliver.
        """
        target = find_target(
            self.player.interaction_probe(),
            self.player.hitbox,
            self.npcs,
            [*self.props,
             *self.breakables,
             *self.reactive_flowers.flowers,
             *(t for t in self.choice_triggers if not t.walk_triggered)],
        )
        if target is not None:
            return target
        return self._terrain_in_range()

    def _terrain_in_range(self):
        """Ground with something to say, one tile ahead of Chuck.

        The Astral Sea is terrain rather than a prop -- seventeen
        thousand tiles of it across thirty-nine maps -- so it cannot
        answer the way a barrel does. Anything else in reach answers
        first; this is what is left when Chuck is looking at nothing but
        the gap in the world.
        """
        probe = self.player.interaction_probe()
        ts = config.TILE_SIZE
        for col in range(probe.left // ts, probe.right // ts + 1):
            for row in range(probe.top // ts, probe.bottom // ts + 1):
                line = TERRAIN_DIALOGUE.get(self.tilemap.terrain_at(col, row))
                if line is not None:
                    return _TerrainTarget(line)
        return None

    def _collect_pending_drops(self) -> None:
        """Materialize one-shot physical rewards requested by world objects."""
        for source in [*self.props, *self.breakables]:
            take_drop = getattr(source, "take_drop_position", None)
            create_pickup = getattr(source, "create_pickup", None)
            if not callable(take_drop) or not callable(create_pickup):
                continue
            drop = take_drop()
            if drop is not None:
                self.pickups.append(
                    create_pickup(drop, self.game.assets)
                )

    def _raptor_quarry(self, raptor):
        """Who this raptor is after: a fleeing person, or failing that Chuck.

        Only raptors authored as chasers look at anybody but Chuck, which
        keeps the City Day 6 tableau put -- the jungle animals stay in
        the jungle and stay dangerous, and the two on the ring road are
        visibly after the two people running. Every other map has nobody
        to flee, so nothing outside City Day 6 changes.
        """
        if not getattr(raptor, "chases_people", False):
            return self.player
        nearest, best = None, config.RAPTOR_NOTICE_RANGE
        for npc in self.npcs:
            if not getattr(npc, "fleeing", False):
                continue
            distance = math.dist(
                (raptor.x + raptor.width / 2, raptor.y + raptor.height / 2),
                (npc.x + npc.width / 2, npc.y + npc.height / 2),
            )
            if distance < best:
                nearest, best = npc, distance
        return nearest if nearest is not None else self.player

    def _player_tile(self) -> tuple[int, int]:
        """Tile under Chuck's footprint center."""
        ts = config.TILE_SIZE
        return (
            int((self.player.x + self.player.width / 2) // ts),
            int((self.player.y + self.player.height / 2) // ts),
        )

    def _jump_hint_visible(self) -> bool:
        """Show the sewer's temporary prompt only on approach to the gap."""
        col, row = self._player_tile()
        if self.map_name == "sewer":
            if self._jump_tutorial_complete:
                return False
            left, right, top, bottom = config.SEWER_JUMP_HINT_BOUNDS
            return left <= col <= right and top <= row <= bottom
        if self.map_name == "waterdeep_pantry":
            radius = 2
            return any(
                self.tilemap.terrain_at(col + dx, row + dy) == "s"
                for dx in range(-radius, radius + 1)
                for dy in range(-radius, radius + 1)
                if abs(dx) + abs(dy) <= radius
            )
        return False

    def _scratch_hint_visible(self) -> bool:
        """Prompt near grass in opening maps, or at the sewer rat choke."""
        if self.map_name in config.GRASS_SCRATCH_HINT_MAPS:
            player_cx = self.player.x + self.player.width / 2
            player_cy = self.player.y + self.player.height / 2
            reach = config.GRASS_SCRATCH_HINT_REACH
            if any(
                grass.intact
                and abs(player_cx - (grass.x + grass.width / 2)) <= reach
                and abs(player_cy - (grass.y + grass.height / 2)) <= reach
                for grass in self.breakables
            ):
                return True
        if (
            self.map_name != "sewer"
            or not any(rat.alive for rat in self._scratch_tutorial_rats)
        ):
            return False
        col, row = self._player_tile()
        left, right, top, bottom = config.SEWER_SCRATCH_HINT_BOUNDS
        return left <= col <= right and top <= row <= bottom

    def _anchor_hint_visible(self) -> bool:
        """Introduce the maze ashtray when Chuck comes within 1.5 tiles."""
        if self.map_name != "sewer":
            return False
        player_cx = self.player.x + self.player.width / 2
        player_cy = self.player.y + self.player.height / 2
        reach = config.TILE_SIZE * 1.5
        return any(
            abs(player_cx - (anchor.x + anchor.width / 2)) <= reach
            and abs(player_cy - (anchor.y + anchor.height / 2)) <= reach
            for anchor in self.anchors
        )

    def _update_footsteps(self, dt: float) -> None:
        """A soft tap per stride; wood on the dock, stone on the street."""
        if not self.player.moving or self.player.jumping:
            self._step_timer = 0.0
            return
        self._step_timer -= dt
        if self._step_timer > 0.0:
            return
        self._step_timer = config.FOOTSTEP_INTERVAL
        ts = config.TILE_SIZE
        terrain = self.tilemap.terrain_at(
            int((self.player.x + self.player.width / 2) // ts),
            int((self.player.y + self.player.height / 2) // ts),
        )
        surface = "wood" if terrain in {"=", "∥"} else "stone"
        self.game.audio.play_sfx(f"footstep_{surface}_{self._step_variant}")
        self._step_variant = 2 if self._step_variant == 1 else 1

    def _update_climb(self, dt: float) -> None:
        """Move Chuck one tile from harbor water onto the return pier."""
        assert self._climb_t is not None
        self._climb_t += dt
        progress = min(1.0, self._climb_t / config.CLIMB_OUT_DURATION)
        eased = progress * progress * (3.0 - 2.0 * progress)
        self.player.y = (
            self._climb_from_y
            + (self._climb_target_y - self._climb_from_y) * eased
        )
        self.player.facing = "up"
        self.player.moving = progress < 1.0
        self.player.climb_progress = progress
        if progress >= 1.0:
            self.player.y = self._climb_target_y
            self.player.moving = False
            self.player.climb_progress = None
            self._climb_t = None

    def _reset_enemies(self) -> None:
        """Rebuild this area's enemies from map markers after Chuck returns."""
        self.hazards = []
        self.rats = []
        self.raccoons = []
        self.undead = []
        self.net_capture.clear()
        self.raptors = []
        self.redcaps = []
        self.dinosaurs = []
        self.snakes = []
        self.chefs = []
        self.fencers = []
        self.traffic_lanes = [
            TrafficLane(
                cx, cy, direction, phase,
                self.tilemap.width_tiles * config.TILE_SIZE,
                self.tilemap.height_tiles * config.TILE_SIZE,
            )
            for direction, phase, (cx, cy) in self._traffic_lane_spawns
        ]
        for lane in self.traffic_lanes:
            lane.load_sprites(self.game.assets)
        self._traffic_safe_position = (self.player.x, self.player.y)
        self._chef_notice_shown = False
        self._chef_start_after_dialogue = False
        self.dart_traps = [
            DartTrap(cx, cy, direction)
            for direction, (cx, cy) in self._dart_trap_spawns
        ]
        self.darts: list[TempleDart] = []
        # Phlegethos hazards: perched spine-throwers and weaving skulls.
        self.spined_devils: list[SpinedDevil] = []
        self.spines: list[FlamingSpine] = []
        self.blue_dragons: list[BlueDragon] = []
        # The daytime city's stationary shooters and their rounds.
        self.police: list[PoliceOfficer] = []
        self.bullets: list[Bullet] = []
        self.flameskulls: list[Flameskull] = []
        self.spitting_orchids: list[SpittingOrchid] = []
        self.orchid_seeds: list[OrchidSeed] = []
        # What the last two of the three are fighting. Built before the
        # cadences, because the cadences are aimed at it: the ranger has
        # no shot without a horde and the fighter has nothing to swing
        # at, which is the whole difference from the version of this
        # room where she spun on the spot.
        actors = {actor.kind: actor for actor in self.battle_actors}
        self.horde = (
            OrcHorde(self.tilemap, self.game.assets,
                     fighter=actors["fighter"], ranger=actors["ranger"])
            if self.map_name == "desert_trio"
            and {"fighter", "ranger"} <= set(actors) else None
        )
        # ...and the rest of the orc army, standing off from them.
        self.siege = (
            OrcSiege(self.tilemap, self.game.assets, self.battle_actors)
            if self.horde is not None else None
        )
        # The sanctum battle restarts its cadences whenever the room does,
        # and the Astral breach heals shut and re-arms with it.
        if self.map_name == "temple_sanctum":
            self.battle = BattleChoreographer(self.battle_actors)
        elif self.map_name == "phlegethos_fortress_approach":
            self.battle = InfernalBattleChoreographer(self.battle_actors)
        elif self.map_name == "desert_trio":
            self.battle = CollisionBattleChoreographer(
                self.battle_actors, horde=self.horde)
        else:
            self.battle = None
        self.battle_projectiles: list[BattleProjectile] = []
        self.battle_cones: list = []
        if getattr(self, "breach", None) is not None:
            self.breach.restore()
        if getattr(self, "infernal_corruption", None) is not None:
            self.infernal_corruption.restore()
        self.breach = (
            AstralBreach(self.tilemap)
            if self.map_name == "temple_sanctum" else None
        )
        # The final encounter's clock. Its footing set is the heroes'
        # own tiles: the rift takes the arena a column at a time as
        # they talk, and the three holding it must not be swallowed by
        # the thing they are closing.
        if getattr(self, "trio", None) is not None:
            self.trio.restore()
        if getattr(self, "churn", None) is not None:
            self.churn.restore()
        self.trio = (
            TrioEncounter(
                self.tilemap,
                {
                    (col, row)
                    for kind, position in self.tilemap.object_spawns
                    if kind.startswith("battle:")
                    for col, row in ((int(position[0]) // config.TILE_SIZE,
                                      int(position[1]) // config.TILE_SIZE),)
                },
            )
            if self.map_name == "desert_trio" else None
        )
        # ...and the collision itself, which starts when the last thing
        # has been said. It writes floors and nothing else, so it can
        # share the heroes' protected footing without being able to
        # hurt anybody standing on it.
        self.churn = (
            WorldChurn(self.tilemap, self.trio._protected)
            if self.trio is not None else None
        )
        # ...and the dragon, which arrives with it. Everything else in
        # this room is pressure Chuck reads around himself -- arrows
        # from a fixed point, a horde on fixed courses, a floor being
        # repainted under him. A stripe of fire crossing the arena at
        # whatever row he happens to be on is the one kind he has to
        # read about *himself*, which is why it is saved for the last
        # thirty seconds rather than running the whole encounter.
        self.red_dragon = (
            RedDragonFlyby(self.tilemap) if self.trio is not None else None
        )
        if self.red_dragon is not None:
            self.red_dragon.load_sprites(self.game.assets)
            # ...and the room goes back to its own theme when it goes
            # back to its own start. The respawn rebuilds this arena in
            # place rather than reloading the scene, so left alone a
            # player who died in the last thirty seconds would begin the
            # encounter again with the music from the end of it.
            self.game.audio.play_music(AREA_MUSIC[self.map_name])
        self.infernal_corruption = (
            InfernalAstralCorruption(self.tilemap)
            if self.map_name == "phlegethos_fortress_approach" else None
        )
        if self.infernal_corruption is not None:
            # Respawning rebuilds the approach in place rather than
            # reloading the scene, so the seal is open again and the
            # music has to go back to the walk it belongs to. Without
            # this a player who died in the fight would start it over
            # with the fight's own music already playing.
            self.game.audio.play_music(AREA_MUSIC[self.map_name])
        if getattr(self, "feywild_river", None) is not None:
            self.feywild_river.reset()
        self.feywild_river = FeywildRiverField(
            self.tilemap.width_tiles * config.TILE_SIZE
        )
        self.reactive_flowers.reset()
        # The scripted Fireball: how long Chuck has survived sealed in,
        # and the explosion once it fires. Reset with the room so death
        # restarts the survival clock.
        self._survival_t = 0.0
        self._fireball_t: float | None = None
        self._fireball_halved = False
        # The adventurers argue before the cast, then the blast.
        self._fireball_dialogue_shown = False
        self._fireball_after_dialogue = False
        self._scratch_tutorial_rats = []
        self.undead_release.reset()
        rat_spawn_tiles = {
            (int(cx // config.TILE_SIZE), int(cy // config.TILE_SIZE))
            for kind, (cx, cy) in self._enemy_spawns
            if kind in {"rat", "thorn_mite"}
        }
        tutorial_tiles = {
            (config.SEWER_RAT_COL, row) for row in config.SEWER_RAT_ROWS
        }
        for kind, (cx, cy) in self._enemy_spawns:
            if kind == "cat":
                cat = Cat(cx, cy)
                cat.tilemap = self.tilemap
                cat.load_sprites(self.game.assets)
                self.hazards.append(cat)
            elif kind in {"rat", "thorn_mite"}:
                rat = SewerRat(cx, cy, variant=kind)
                rat.load_sprites(self.game.assets)
                rat_tile = (
                    int(cx // config.TILE_SIZE),
                    int(cy // config.TILE_SIZE),
                )
                # Feywild thorn mites fill the same small aggressive role as
                # the ship-hold rats: short notice, direct pursuit, one
                # scratch. Ordinary sewer rats keep their authored patrols.
                if (
                    kind == "thorn_mite"
                    or self.map_name == "ship_lower_hold"
                    or self.map_name.startswith("modern_city_sewer_")
                ):
                    rat.configure_attack_chase(self.tilemap)
                else:
                    rat.configure_patrol(
                        self.tilemap,
                        blocked_spawn_tiles=rat_spawn_tiles - {rat_tile},
                    )
                self.rats.append(rat)
                if self.map_name == "sewer" and rat_tile in tutorial_tiles:
                    self._scratch_tutorial_rats.append(rat)
            elif kind == "raccoon":
                raccoon = Raccoon(cx, cy)
                raccoon.tilemap = self.tilemap
                raccoon.load_sprites(self.game.assets)
                self.raccoons.append(raccoon)
            elif kind in {"zombie", "skeleton", "lemure", "orc", "knight",
                          "crocodile", "animal_control"}:
                self._spawn_undead(kind, (cx, cy))
            elif kind == "raptor" or kind.startswith("raptor:"):
                raptor = Raptor(cx, cy)
                # An authored chaser is after the people, not the rat.
                raptor.chases_people = kind.endswith(":chasing")
                if raptor.chases_people:
                    raptor.standoff = config.RAPTOR_CHASE_STANDOFF
                raptor.tilemap = self.tilemap
                raptor.load_sprites(self.game.assets)
                self.raptors.append(raptor)
            elif kind.startswith("blue_dragon:"):
                dragon = BlueDragon(
                    cx, cy, facing=kind.split(":", 1)[1],
                    # Where it stands decides where in its cycle it
                    # starts, so a map with more than one of them never
                    # has them breathing in unison. In world pixels
                    # rather than tiles: this spawner is handed a
                    # centre, not a grid position.
                    phase=(cx * 0.043 + cy * 0.069),
                )
                dragon.load_sprites(self.game.assets)
                self.blue_dragons.append(dragon)
            elif kind == "redcap":
                redcap = Redcap(cx, cy)
                redcap.tilemap = self.tilemap
                redcap.load_sprites(self.game.assets)
                self.redcaps.append(redcap)
            elif kind in {"massive_dinosaur", "horned_devil", "pit_fiend",
                          "displacer_beast", "griffon"}:
                # A horned devil is the Chultan colossus in infernal art;
                # displacer beasts and griffons are the same readable massive
                # hazard behavior in their own regional art.
                dinosaur = MassiveDinosaur(cx, cy, variant=kind)
                dinosaur.tilemap = self.tilemap
                dinosaur.load_sprites(self.game.assets)
                self.dinosaurs.append(dinosaur)
            elif kind in {"snake", "fire_snake"}:
                # Phlegethos fire snakes are the temple snake exactly, in
                # molten colours (the variant selects the sprite sheet).
                snake = TempleSnake(
                    cx, cy,
                    variant="fire_snake" if kind == "fire_snake" else "snake",
                )
                snake.tilemap = self.tilemap
                snake.load_sprites(self.game.assets)
                self.snakes.append(snake)
            elif kind == "pirate_chef":
                chef = PirateChef(cx, cy)
                chef.tilemap = self.tilemap
                chef.load_sprites(self.game.assets)
                self.chefs.append(chef)
            elif kind.startswith("sword_fighter:"):
                fencer = SwordFighter(cx, cy, kind.split(":", 1)[1])
                fencer.tilemap = self.tilemap
                fencer.load_sprites(self.game.assets)
                self.fencers.append(fencer)
            elif kind.startswith("spined_devil:"):
                devil = SpinedDevil(cx, cy, kind.split(":", 1)[1])
                devil.load_sprites(self.game.assets)
                self.spined_devils.append(devil)
            elif kind.startswith("police:"):
                aim = kind.split(":", 1)[1]
                officer = (SpinningPoliceOfficer(cx, cy) if aim == "spin"
                           else PoliceOfficer(cx, cy, aim))
                officer.load_sprites(self.game.assets)
                self.police.append(officer)
            elif kind.startswith(("flameskull:", "lantern_moth:")):
                # A lantern moth is the flameskull hazard as Feywild
                # wildlife: same weave, same unclearable contact danger.
                family, axis = kind.split(":", 1)
                skull = Flameskull(
                    cx, cy, axis,
                    variant=("lantern_moth" if family == "lantern_moth"
                             else "flameskull"),
                )
                skull.load_sprites(self.game.assets)
                self.flameskulls.append(skull)
            elif kind.startswith("spitting_orchid:"):
                orchid = SpittingOrchid(cx, cy, kind.split(":", 1)[1])
                orchid.load_sprites(self.game.assets)
                self.spitting_orchids.append(orchid)
        if self.fencers:
            if len(self.fencers) != 2:
                raise ValueError("Exterior fencing encounter needs two pirates")
            self.fencers[0].bind_pair(self.fencers[1])

    def _spawn_undead(
        self, kind: str, position: tuple[float, float]
    ) -> None:
        enemy = (
            AnimalControlOfficer(*position) if kind == "animal_control"
            else UndeadEnemy(*position, kind)
        )
        enemy.tilemap = self.tilemap
        enemy.load_sprites(self.game.assets)
        self.undead.append(enemy)

    # ------------------------------------------------------------------
    # Animal Control's net
    # ------------------------------------------------------------------
    def _update_net_capture(self, dt: float) -> None:
        """Hold Chuck and drain him, then hand off to ordinary depletion.

        Nothing here respawns anybody. When the drain runs out this calls
        the same deplete() a lethal fall does, and the existing quiet
        disappearance takes over from there.
        """
        self.sanity.update(dt)
        for officer in self.undead:
            officer.update(dt, self.player)
        remaining = self.net_capture.advance(dt)
        if remaining is None:
            self.net_capture.clear()
            self.sanity.deplete()
            return
        self.sanity.current = remaining

    def _check_net_capture(self) -> None:
        """Throw the net if any officer has finished winding up on Chuck."""
        if self.net_capture.active or self._respawn_phase is not None:
            return
        for officer in self.undead:
            if not isinstance(officer, AnimalControlOfficer):
                continue
            if officer.net_ready(self.player):
                self.net_capture.begin(self.sanity.current)
                self.game.audio.play_sfx("hurt")
                return

    def _draw_net_overlay(self, surface, camera_offset) -> None:
        """The mesh over Chuck: the readable part of being caught."""
        if not self.net_capture.active:
            return
        import pygame

        ox, oy = camera_offset
        box = self.player.hitbox
        left = int(box.centerx) - 10 - ox
        top = int(box.centery) - 12 - oy
        rect = pygame.Rect(left, top, 20, 20)
        pygame.draw.ellipse(surface, (60, 66, 74), rect, 2)
        for offset in range(-8, 9, 4):
            pygame.draw.line(surface, (208, 216, 222),
                             (rect.centerx + offset, rect.top + 2),
                             (rect.centerx + offset, rect.bottom - 2))
            pygame.draw.line(surface, (208, 216, 222),
                             (rect.left + 2, rect.centery + offset),
                             (rect.right - 2, rect.centery + offset))

    # ------------------------------------------------------------------
    # Astral fall hazard
    # ------------------------------------------------------------------
    def _begin_fall(
        self,
        kind: str,
        target: tuple[float, float] | None = None,
    ) -> None:
        """Lock control and let Chuck quietly drop into the wrong map."""
        self._fall_kind = kind
        self._fall_t = 0.0
        self.player.fall_progress = 0.0
        self.player.moving = False
        if kind == "river":
            self.player.jump_remaining = 0.0
        self.player.scratch_remaining = 0.0
        self.player.hurt_blink = 0.0
        self._step_timer = 0.0
        # The fall triggers the moment Chuck's footprint center crosses
        # the hazard tile, so entering from the north or a side leaves
        # most of his sprite over the safe neighbor — sinking there reads
        # as falling into ordinary ground. Glide him onto the hazard
        # tile's center during the fall so he always visibly drops INTO
        # the hole, whichever way he stepped in.
        ts = config.TILE_SIZE
        center_x = self.player.x + self.player.width / 2
        center_y = self.player.y + self.player.height / 2
        col, row = int(center_x // ts), int(center_y // ts)
        self._fall_start = (self.player.x, self.player.y)
        self._fall_target = target or (
            col * ts + ts / 2 - self.player.width / 2,
            row * ts + ts / 2 - self.player.height / 2,
        )

    def _begin_river_escape(self) -> None:
        """Reach the stable boundary before the dedicated river cutscene."""
        self._river_escape_t = 0.0
        self.player.visible = False
        self.player.moving = False
        self.player.jump_remaining = 0.0
        self.player.scratch_remaining = 0.0
        self._step_timer = 0.0
        self.game.audio.play_sfx("vanish")

    def _draw_river_escape_boundary(self, surface) -> None:
        if self._river_escape_t is None:
            return
        progress = min(
            1.0,
            self._river_escape_t / config.FEYWILD_RIVER_ESCAPE_FADE,
        )
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        # A brief blue-green water flash gives way to the black handoff where
        # the next bounded slice will begin the rushing-river cutscene.
        color = (
            round(32 * (1.0 - progress)),
            round(112 * (1.0 - progress)),
            round(124 * (1.0 - progress)),
            255,
        )
        overlay.fill(color)
        surface.blit(overlay, (0, 0))

    def _update_fall(self, dt: float) -> None:
        """Shrink and sink Chuck, then hand off to ordinary respawn."""
        assert self._fall_t is not None
        self._fall_t += dt
        self.player.fall_progress = min(1.0, self._fall_t / config.FALL_DURATION)
        # Slide onto the hazard tile over the fall's first stretch.
        glide = min(1.0, self._fall_t / (config.FALL_DURATION * 0.4))
        start_x, start_y = self._fall_start
        target_x, target_y = self._fall_target
        self.player.x = start_x + (target_x - start_x) * glide
        self.player.y = start_y + (target_y - start_y) * glide
        if self._fall_t >= config.FALL_DURATION:
            kind = self._fall_kind
            self._fall_t = None
            self._fall_kind = None
            self.player.fall_progress = None
            if kind == "sky":
                from src.scenes.falling_cutscene_scene import FallingCutsceneScene
                self.game.scenes.replace(FallingCutsceneScene(self.game))
            elif kind == "river":
                self._begin_river_escape()
            else:
                self.sanity.deplete()

    # ------------------------------------------------------------------
    # Astral respawn (Game Bible: quiet, quick, never punishing)
    # ------------------------------------------------------------------
    def _begin_respawn(self) -> None:
        """Sanity reached zero. Chuck quietly stops being here."""
        # One death per vanish. A second depletion while he is already
        # gone -- a hit landing during the fade -- is the same death.
        if self._respawn_phase is None:
            self.game.deaths.record()
        self.player.visible = False
        self.player.hurt_blink = 0.0
        self._respawn_phase = "out"
        self._respawn_t = 0.0
        self.game.audio.play_sfx("vanish")

    def _update_respawn(self, dt: float) -> None:
        """Advance the fade-out -> hold -> fade-in sequence."""
        self._respawn_t += dt
        if self._respawn_phase == "out" and self._respawn_t >= config.RESPAWN_FADE_OUT:
            self._respawn_phase, self._respawn_t = "hold", 0.0
        elif self._respawn_phase == "hold" and self._respawn_t >= config.RESPAWN_HOLD:
            # The return: the door he came in by.
            self.player.x, self.player.y = (
                self.anchors_system.respawn_position_for_chuck()
            )
            self._reset_enemies()
            self.sanity.refill()
            # Death rewinds the cigarette count to the respawn point's
            # committed value — the run since the checkpoint is undone.
            self.game.cigarettes.rollback()
            self.camera.follow(self.player)  # snap, no cross-map pan
            self.player.visible = True
            self._respawn_phase, self._respawn_t = "in", 0.0
            self.game.audio.play_sfx("respawn")
        elif self._respawn_phase == "in" and self._respawn_t >= config.RESPAWN_FADE_IN:
            self._respawn_phase = None

    def _draw_respawn_overlay(self, surface) -> None:
        """The Astral dark: a dimming veil and a few patient stars."""
        if self._respawn_phase is None:
            return
        if self._respawn_phase == "out":
            alpha = min(1.0, self._respawn_t / config.RESPAWN_FADE_OUT)
        elif self._respawn_phase == "hold":
            alpha = 1.0
        else:
            alpha = max(0.0, 1.0 - self._respawn_t / config.RESPAWN_FADE_IN)

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*config.COLOR_ASTRAL, int(alpha * 255)))
        surface.blit(overlay, (0, 0))
        if alpha > 0.85:  # stars only in the deep dark
            for sx, sy in ((52, 30), (240, 22), (150, 90), (300, 130),
                           (28, 150), (200, 58), (90, 120)):
                pygame.draw.rect(
                    surface, config.COLOR_STAR, pygame.Rect(sx, sy, 1, 1)
                )

    def _draw_arrival_fade(self, surface) -> None:
        """Fade up, for checkpoints that author an arrival fade.

        Out of black for everything that arrived through a blackout,
        which is all of them bar one: the desert crossing whites out
        instead, and fading that back in from black puts a flash
        between the cutscene and the map it hands to.
        """
        if self._arrival_fade_t is None:
            return
        progress = min(1.0, self._arrival_fade_t / config.AREA_FADE_DURATION)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self._arrival_fade_from,
                      round(255 * (1.0 - progress))))
        surface.blit(overlay, (0, 0))
