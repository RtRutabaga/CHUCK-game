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
    FeywildRiverField, InfernalAstralCorruption,
    InfernalBattleChoreographer,
)
from src.entities.dart_trap import DartTrap, TempleDart
from src.entities.deck_pirate import DeckPirateNPC
from src.entities.hazard import Cat
from src.entities.massive_dinosaur import MassiveDinosaur
from src.entities.npc import NPC
from src.entities.pickup import Cigarette
from src.entities.pirate_chef import PirateChef
from src.entities.pirate_npc import PirateNPC
from src.entities.player import Player
from src.entities.prop import Prop
from src.entities.rat import SewerRat
from src.entities.raptor import Raptor
from src.entities.reality_blocks import RealityBlockField
from src.entities.snake import TempleSnake
from src.entities.flameskull import Flameskull
from src.entities.spined_devil import FlamingSpine, SpinedDevil
from src.entities.sword_fighter import SwordFighter
from src.entities.undead import UndeadEnemy
from src.scenes.dialogue_scene import DialogueScene
from src.scenes.scene import Scene
from src.systems.astral_anchor import AstralAnchorSystem
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
from src.systems.terrain_hazard import touching_terrain_hazard
from src.systems.undead_release import (
    UndeadReleaseController, is_staged_undead,
)
from src.ui.tutorial_hint import TutorialHint
from src.systems.sanity import SanitySystem
from src.systems.ship_motion import deck_rock_offset
from src.ui.hud import HUD
from src.world.camera import Camera
from src.world.collision import overlaps
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


class WorldScene(Scene):
    """The explorable world. Starts at the docks; a dialogue choice can
    carry Chuck to another map (the sewer) via load_map()."""

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
        # Set by a transition choice; applied once the conversation that
        # triggered it has closed (see update()).
        self._pending_map: str | None = None
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
        self._pending_arrival = None
        self._pending_climb_from_water = False
        self._pending_facing = None
        self._pending_fade_in = False
        self._walk_choice_armed = True  # crevice-style walk-in prompts
        self._ladder_choice_armed = True
        self.tilemap = TileMap(config.MAPS_DIR / f"{self.map_name}.txt")
        if self.map_name == "waterdeep_docks" and self._sewer_completed:
            self.tilemap.open_tavern_entrance()
        self.tilemap.load_tileset(self.game.assets, tileset_for(self.map_name))
        self._world_time = 0.0  # drives water shimmer
        self._arrival_fade_t: float | None = 0.0 if fade_in else None

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
        # The adventurers' entrance lines (session 131): entering the
        # final chamber from the gauntlet, each delivers one heroic,
        # non-interactive line before control returns.
        self._pending_entrance_dialogue = (
            "sanctum_entrance"
            if map_name == "temple_sanctum" and arrival == "from_temple_8"
            else "phlegethos_battle_entrance"
            if (
                map_name == "phlegethos_fortress_approach"
                and arrival == "from_phlegethos_3"
            )
            else None
        )
        self._restore_camera_to_player = False
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
               self.game.cigarettes)
        self._hint = (
            TutorialHint(self.game.assets)
            if self.map_name in config.TUTORIAL_MAPS
            else None
        )
        self._jump_tutorial_complete = False

        # Respawn: where Chuck returns (defaults to where he woke up),
        # and the transition state (None = living normally).
        self.anchors_system = AstralAnchorSystem(
            default_position=(self.player.x, self.player.y),
            default_checkpoint_id=checkpoint_id,
        )
        self._respawn_phase: str | None = None  # "out" | "hold" | "in"
        self._respawn_t = 0.0
        self._fall_t: float | None = None
        self._fall_kind: str | None = None

        # Area music, looping — or silence where an area has no theme yet
        # (the sewer's track is a later Phase 2 session). Footsteps
        # alternate variants and pick wood/stone from the tile underfoot.
        music = AREA_MUSIC.get(self.map_name, config.MUSIC_FILE)
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
        self._plank_procession_target: tuple[float, float] | None = None
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
            if kind == "ship_captain_chest":
                prop = CaptainChest(
                    col, row, self.game.assets,
                    self.game.progress,
                )
            else:
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
        self.choice_triggers: list[ChoiceTrigger] = []
        self.battle_actors: list[BattleActor] = []
        self._dart_trap_spawns = [
            (kind.split(":", 1)[1], position)
            for kind, position in self.tilemap.object_spawns
            if kind.startswith("dart_trap:")
        ]
        self._enemy_spawns = [
            (kind, position)
            for kind, position in self.tilemap.object_spawns
            if kind in {
                "cat", "rat", "zombie", "skeleton", "lemure", "raptor",
                "massive_dinosaur", "horned_devil", "snake", "fire_snake",
                "pirate_chef",
            } or kind.startswith(("sword_fighter:", "spined_devil:",
                                  "flameskull:"))
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
                "rat", "zombie", "skeleton", "lemure", "raptor",
                "massive_dinosaur", "horned_devil", "snake", "fire_snake",
                "pirate_chef",
            }:
                continue  # rebuilt with all enemies below
            elif kind.startswith(("sword_fighter:", "spined_devil:",
                                  "flameskull:")):
                continue  # rebuilt with all hazards below
            elif kind.startswith("battle:"):
                actor = BattleActor(cx, cy, kind.split(":", 1)[1])
                actor.load_sprite(self.game.assets)
                self.battle_actors.append(actor)
            elif kind.startswith("choice:"):
                choice_id = kind.split(":", 1)[1]
                self.choice_triggers.append(ChoiceTrigger(cx, cy, choice_id))
            elif kind.startswith("arrival:"):
                continue  # named map metadata, not a runtime entity
            elif kind.startswith("boundary:"):
                # Authored handoff metadata for a future destination.  It is
                # deliberately inert until that destination map exists.
                continue
            elif kind.startswith("dart_trap:"):
                continue  # rebuilt with projectiles by _reset_enemies()
            elif is_staged_undead(kind):
                continue  # released in finite groups as Chuck advances
            else:
                raise ValueError(f"No spawner for object kind {kind!r}")
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


    def handle_event(self, event: pygame.event.Event) -> None:
        """Temporary: ESC quits until a pause menu exists."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

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

        # The argument has closed on "FIREBALL!!": now it lands.
        if self._fireball_after_dialogue and self._fireball_t is None:
            self._fireball_after_dialogue = False
            self._begin_fireball()
            return

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
        for rat in self.rats:
            rat.update(dt, self.player)
        for kind, position in self.undead_release.release_for_row(
            self._player_tile()[1]
        ):
            self._spawn_undead(kind, position)
        for undead in self.undead:
            undead.update(dt, self.player)
        for raptor in self.raptors:
            raptor.update(dt, self.player)
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
        for spine in self.spines:
            spine.update(dt, self.tilemap)
        self.spines = [spine for spine in self.spines if spine.alive]
        for skull in self.flameskulls:
            skull.update(dt)
        for actor in self.battle_actors:
            actor.update(dt)
        if self.battle is not None:
            tick = self.battle.update(dt)
            self.battle_projectiles.extend(tick.projectiles)
            self.battle_cones.extend(tick.cones)
            for shot in self.battle_projectiles:
                shot.update(dt, self.tilemap)
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
            self.infernal_corruption.update(dt, self.player.hitbox)
            if (
                self.infernal_corruption.triggered
                and self.infernal_corruption.elapsed
                >= config.FEYWILD_RIVER_START_TIME
            ):
                self.feywild_river.activate()
        self.feywild_river.update(dt)
        for breakable in self.breakables:
            breakable.update(dt)
        self.breakables = [item for item in self.breakables if item.alive]
        for prop in self.props:
            update = getattr(prop, "update", None)
            if callable(update):
                update(dt)
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

        self.sanity.update(dt)
        old_player_position = (self.player.x, self.player.y)
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
            self.load_map(
                exit_config.destination,
                arrival=exit_config.arrival,
                facing=exit_config.facing,
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
            scratch_first_target(
                self.player.scratch_hitbox(),
                [*(prop for prop in self.props
                   if callable(getattr(prop, "on_scratched", None))),
                 *self.breakables, *self.rats, *self.undead, *self.raptors,
                 *self.dinosaurs, *self.snakes],
            )
            self._collect_pending_drops()
        self.rats = [rat for rat in self.rats if rat.alive]
        self.undead = [enemy for enemy in self.undead if enemy.alive]
        self.raptors = [raptor for raptor in self.raptors if raptor.alive]
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
                self.game.scenes.push(
                    DialogueScene(self.game, self.dialogue.get(dialogue_id))
                )
                return  # the world holds its breath

        player_box = self.player.hitbox

        for dart in self.darts:
            if dart.alive and overlaps(player_box, dart.hitbox):
                dart.alive = False
                if self.sanity.damage(dart.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
        self.darts = [dart for dart in self.darts if dart.alive]

        for spine in self.spines:
            if spine.alive and overlaps(player_box, spine.hitbox):
                spine.alive = False
                if self.sanity.damage(spine.damage):
                    self.player.hurt_blink = config.HURT_COOLDOWN
                    self.game.audio.play_sfx("hurt")
        self.spines = [spine for spine in self.spines if spine.alive]

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

        # Anchors: touching one attunes it (and un-lights the rest).
        for anchor in self.anchors:
            if not anchor.lit and overlaps(player_box, anchor.hitbox):
                for other in self.anchors:
                    other.lit = False
                anchor.lit = True
                self.anchors_system.activate(
                    (anchor.x, anchor.y), anchor.checkpoint_id
                )
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
        for prop in self.props:
            if getattr(prop, "floor_layer", False):
                prop.draw(surface, offset)
        for pickup in self.pickups:  # flat ground litter, under everyone
            pickup.draw(surface, offset)
        for drawable in self._sorted_drawables():
            drawable.draw(surface, offset)
        if self.breach is not None:
            self.breach.draw(surface, offset)
        if self.infernal_corruption is not None:
            self.infernal_corruption.draw(surface, offset)
        for cone in self.battle_cones:
            cone.draw(surface, offset)
        self.tilemap.draw_overhead(surface, offset, self._world_time)
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
                     *self.battle_actors,
                     *self.hazards, *self.rats,
                     *self.undead, *self.raptors, *self.dinosaurs,
                     *self.snakes, *self.chefs, *self.fencers,
                     *self.spined_devils, *self.flameskulls,
                     *self.darts, *self.spines, *self.battle_projectiles,
                     *self.npcs, self.player]
        return sorted(drawables, key=lambda d: d.sort_y)

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
        """Cut to the starboard approach, then let Chuck walk to the rail."""
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
            (rail_row - 1) * ts + (ts - self.player.height) / 2,
        )
        self._plank_procession_active = True
        self.camera.follow(self.player)

    def _on_choice(self, option) -> None:
        """What a decision means. The scene reports; the world acts.

        A `goto` option carries Chuck to another map. It may also name an
        arrival marker and restrained arrival choreography. We only record
        the transition here; DialogueScene closes itself, and the actual
        load happens back in update() once it has.
        """
        self.last_choice = option.dialogue or option.goto
        if option.goto is not None:
            self._pending_map = option.goto
            self._pending_arrival = option.arrival
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

        field.activate()
        self._reality_warning_shown = True
        self.game.scenes.push(DialogueScene(
            self.game,
            self.dialogue.get("jeffries_reality_warning"),
        ))
        return True

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

    def _interactable_in_range(self):
        """The NPC or prop Chuck could talk to right now, or None.

        The interact key and the tutorial hint both read this, so the
        hint can never promise something E won't deliver.
        """
        return find_target(
            self.player.interaction_probe(),
            self.player.hitbox,
            self.npcs,
            [*self.props,
             *(t for t in self.choice_triggers if not t.walk_triggered)],
        )

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
        self.undead = []
        self.raptors = []
        self.dinosaurs = []
        self.snakes = []
        self.chefs = []
        self.fencers = []
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
        self.flameskulls: list[Flameskull] = []
        # The sanctum battle restarts its cadences whenever the room does,
        # and the Astral breach heals shut and re-arms with it.
        if self.map_name == "temple_sanctum":
            self.battle = BattleChoreographer(self.battle_actors)
        elif self.map_name == "phlegethos_fortress_approach":
            self.battle = InfernalBattleChoreographer(self.battle_actors)
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
        self.infernal_corruption = (
            InfernalAstralCorruption(self.tilemap)
            if self.map_name == "phlegethos_fortress_approach" else None
        )
        if getattr(self, "feywild_river", None) is not None:
            self.feywild_river.reset()
        self.feywild_river = FeywildRiverField(
            self.tilemap.width_tiles * config.TILE_SIZE
        )
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
            if kind == "rat"
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
            elif kind == "rat":
                rat = SewerRat(cx, cy)
                rat.load_sprites(self.game.assets)
                rat_tile = (
                    int(cx // config.TILE_SIZE),
                    int(cy // config.TILE_SIZE),
                )
                if self.map_name == "ship_lower_hold":
                    rat.configure_attack_chase(self.tilemap)
                else:
                    rat.configure_patrol(
                        self.tilemap,
                        blocked_spawn_tiles=rat_spawn_tiles - {rat_tile},
                    )
                self.rats.append(rat)
                if self.map_name == "sewer" and rat_tile in tutorial_tiles:
                    self._scratch_tutorial_rats.append(rat)
            elif kind in {"zombie", "skeleton", "lemure"}:
                self._spawn_undead(kind, (cx, cy))
            elif kind == "raptor":
                raptor = Raptor(cx, cy)
                raptor.tilemap = self.tilemap
                raptor.load_sprites(self.game.assets)
                self.raptors.append(raptor)
            elif kind in {"massive_dinosaur", "horned_devil"}:
                # A horned devil is the Chultan colossus in infernal art.
                dinosaur = MassiveDinosaur(
                    cx, cy,
                    variant=("horned_devil" if kind == "horned_devil"
                             else "massive_dinosaur"),
                )
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
            elif kind.startswith("flameskull:"):
                skull = Flameskull(cx, cy, kind.split(":", 1)[1])
                skull.load_sprites(self.game.assets)
                self.flameskulls.append(skull)
        if self.fencers:
            if len(self.fencers) != 2:
                raise ValueError("Exterior fencing encounter needs two pirates")
            self.fencers[0].bind_pair(self.fencers[1])

    def _spawn_undead(
        self, kind: str, position: tuple[float, float]
    ) -> None:
        enemy = UndeadEnemy(*position, kind)
        enemy.tilemap = self.tilemap
        enemy.load_sprites(self.game.assets)
        self.undead.append(enemy)

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
            # The return: at the attuned anchor (or where he woke up).
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
        """Fade from black only for checkpoints that author an arrival fade."""
        if self._arrival_fade_t is None:
            return
        progress = min(1.0, self._arrival_fade_t / config.AREA_FADE_DURATION)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, round(255 * (1.0 - progress))))
        surface.blit(overlay, (0, 0))
