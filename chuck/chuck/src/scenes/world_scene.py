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
from src.entities.choice_trigger import ChoiceTrigger
from src.entities.hazard import Cat
from src.entities.npc import NPC
from src.entities.pickup import Cigarette
from src.entities.player import Player
from src.entities.prop import Prop
from src.entities.rat import SewerRat
from src.scenes.dialogue_scene import DialogueScene
from src.scenes.scene import Scene
from src.systems.astral_anchor import AstralAnchorSystem
from src.systems.choice import ChoiceSystem
from src.systems.combat import scratch_first_target
from src.systems.dialogue import DialogueSystem
from src.systems.fall import fall_zone_kind
from src.systems.interaction import find_target
from src.ui.tutorial_hint import TutorialHint
from src.systems.sanity import SanitySystem
from src.ui.hud import HUD
from src.world.camera import Camera
from src.world.collision import overlaps
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


class WorldScene(Scene):
    """The explorable world. Starts at the docks; a dialogue choice can
    carry Chuck to another map (the sewer) via load_map()."""

    def __init__(self, game, map_name: str = "waterdeep_docks") -> None:
        super().__init__(game)
        self._initial_map = map_name
        # Set by a transition choice; applied once the conversation that
        # triggered it has closed (see update()).
        self._pending_map: str | None = None
        self._pending_arrival: str | None = None
        self._pending_climb_from_water = False
        self._sewer_completed = False

    def on_enter(self) -> None:
        """Build the starting area when this scene becomes active."""
        self.load_map(self._initial_map)

    def load_map(
        self,
        map_name: str,
        arrival: str | None = None,
        climb_from_water: bool = False,
        facing: str | None = None,
    ) -> None:
        """(Re)build the map and all entities for an area. Used both on
        first entry and when a transition carries Chuck somewhere new."""
        self.map_name = map_name
        if map_name == "waterdeep_docks" and arrival == "sewer_outflow":
            self._sewer_completed = True
        self._pending_map = None
        self._pending_arrival = None
        self._pending_climb_from_water = False
        self.tilemap = TileMap(config.MAPS_DIR / f"{self.map_name}.txt")
        if self.map_name == "waterdeep_docks" and self._sewer_completed:
            self.tilemap.open_tavern_entrance()
        self.tilemap.load_tileset(self.game.assets, tileset_for(self.map_name))
        self._world_time = 0.0  # drives water shimmer

        arrivals = {
            kind.split(":", 1)[1]: position
            for kind, position in self.tilemap.object_spawns
            if kind.startswith("arrival:")
        }
        if arrival is not None:
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
        self.sanity = SanitySystem(on_depleted=self._begin_respawn)
        self.hud = HUD(self.sanity)
        self._hint = (
            TutorialHint(self.game.assets)
            if self.map_name in config.TUTORIAL_MAPS
            else None
        )
        self._jump_tutorial_complete = False

        # Respawn: where Chuck returns (defaults to where he woke up),
        # and the transition state (None = living normally).
        self.anchors_system = AstralAnchorSystem(
            default_position=(self.player.x, self.player.y)
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
        self.props = [
            Prop(kind, col, row, self.game.assets)
            for kind, col, row in self.tilemap.prop_tiles
        ]
        self.pickups: list[Cigarette] = []
        self.hazards: list[Cat] = []
        self.anchors: list[AstralAnchor] = []
        self.npcs: list[NPC] = []
        self.choice_triggers: list[ChoiceTrigger] = []
        self._enemy_spawns = [
            (kind, position)
            for kind, position in self.tilemap.object_spawns
            if kind in {"cat", "rat"}
        ]
        for kind, (cx, cy) in self.tilemap.object_spawns:
            if kind == "cigarette":
                cig = Cigarette(cx, cy)
                cig.load_sprite(self.game.assets)
                self.pickups.append(cig)
            elif kind == "cat":
                continue  # rebuilt with all enemies below
            elif kind == "anchor":
                anchor = AstralAnchor(cx, cy)
                anchor.load_sprites(self.game.assets)
                self.anchors.append(anchor)
            elif kind.startswith("npc:"):
                npc_id = kind.split(":", 1)[1]
                npc = NPC(cx, cy, npc_id=npc_id, dialogue_id=npc_id)
                npc.load_sprites(self.game.assets)
                self.npcs.append(npc)
            elif kind == "rat":
                continue  # rebuilt with all enemies below
            elif kind.startswith("choice:"):
                choice_id = kind.split(":", 1)[1]
                self.choice_triggers.append(ChoiceTrigger(cx, cy, choice_id))
            elif kind.startswith("arrival:"):
                continue  # named map metadata, not a runtime entity
            else:
                raise ValueError(f"No spawner for object kind {kind!r}")
        self._reset_enemies()


    def handle_event(self, event: pygame.event.Event) -> None:
        """Temporary: ESC quits until a pause menu exists."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.quit()

    def update(self, dt: float) -> None:
        """Advance the world simulation."""
        # A transition chosen during a conversation waits until that
        # conversation has closed and control returns here — only then
        # is this scene the top of the stack again — so the descent
        # lines finish over the old world before the new one loads.
        if self._pending_map is not None:
            destination = self._pending_map
            arrival = self._pending_arrival
            climb_from_water = self._pending_climb_from_water
            self.load_map(
                destination,
                arrival=arrival,
                climb_from_water=climb_from_water,
            )
            return

        # The world keeps moving whether or not Chuck is in it.
        self._world_time += dt
        for cat in self.hazards:
            cat.update(dt)
        for rat in self.rats:
            rat.update(dt)

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
        fall_kind = fall_zone_kind(
            self.tilemap, self.player.hitbox, self.player.jumping
        )
        if fall_kind is not None:
            self._begin_fall(fall_kind)
            self.camera.update(dt)
            return
        if (
            self.map_name == "sewer"
            and self._player_tile()[1] > config.SEWER_JUMP_ROW
        ):
            self._jump_tutorial_complete = True

        exit_config = AREA_WALK_EXITS.get(
            (self.map_name, self.tilemap.terrain_at(*self._player_tile()))
        )
        if exit_config is not None:
            self.load_map(
                exit_config.destination,
                arrival=exit_config.arrival,
                facing=exit_config.facing,
            )
            return

        # One committed scratch resolves against at most one rat. Rat bodies
        # block the one-tile choke, so the group must be cleared to continue.
        if self.player.scratch_just_started:
            self.game.audio.play_sfx("scratch")
            scratch_first_target(self.player.scratch_hitbox(), self.rats)
        self.rats = [rat for rat in self.rats if rat.alive]

        blocking_rat = next(
            (rat for rat in self.rats if overlaps(self.player.hitbox, rat.hitbox)),
            None,
        )
        if blocking_rat is not None:
            if self.sanity.damage(blocking_rat.damage):
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
                dialogue_id = (
                    target.interact(self.player)
                    if isinstance(target, NPC)
                    else target.dialogue_id
                )
                self.game.scenes.push(
                    DialogueScene(self.game, self.dialogue.get(dialogue_id))
                )
                return  # the world holds its breath

        player_box = self.player.hitbox

        # Pickups: collect on overlap, then drop dead ones.
        for pickup in self.pickups:
            if pickup.alive and overlaps(player_box, pickup.hitbox):
                pickup.on_collect(self.sanity)
                self.game.audio.play_sfx("pickup")
        self.pickups = [p for p in self.pickups if p.alive]

        self._update_footsteps(dt)

        # Anchors: touching one attunes it (and un-lights the rest).
        for anchor in self.anchors:
            if not anchor.lit and overlaps(player_box, anchor.hitbox):
                for other in self.anchors:
                    other.lit = False
                anchor.lit = True
                self.anchors_system.activate((anchor.x, anchor.y))
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
        self.tilemap.draw_ground(surface, offset, self._world_time)
        for pickup in self.pickups:  # flat ground litter, under everyone
            pickup.draw(surface, offset)
        for drawable in self._sorted_drawables():
            drawable.draw(surface, offset)
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

    def _sorted_drawables(self):
        """Everything that stands in the world, painter-ordered by feet.

        Lower on screen draws later, so characters correctly pass in
        front of and behind props, anchors, and each other. Chuck is
        one foot tall; this is where that finally SHOWS.
        """
        drawables = [*self.props, *self.anchors, *self.hazards, *self.rats,
                     *self.npcs, self.player]
        return sorted(drawables, key=lambda d: d.sort_y)

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

    def _interactable_in_range(self):
        """The NPC or prop Chuck could talk to right now, or None.

        The interact key and the tutorial hint both read this, so the
        hint can never promise something E won't deliver.
        """
        return find_target(
            self.player.interaction_probe(),
            self.player.hitbox,
            self.npcs,
            [*self.props, *self.choice_triggers],
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
        if self.map_name != "sewer" or self._jump_tutorial_complete:
            return False
        col, row = self._player_tile()
        left, right, top, bottom = config.SEWER_JUMP_HINT_BOUNDS
        return left <= col <= right and top <= row <= bottom

    def _scratch_hint_visible(self) -> bool:
        """Prompt only at the post-gap rat choke, until all rats are gone."""
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
        surface = "wood" if terrain == "=" else "stone"
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
        self._scratch_tutorial_rats = []
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
                rat.configure_patrol(
                    self.tilemap,
                    blocked_spawn_tiles=rat_spawn_tiles - {rat_tile},
                )
                self.rats.append(rat)
                if self.map_name == "sewer" and rat_tile in tutorial_tiles:
                    self._scratch_tutorial_rats.append(rat)

    # ------------------------------------------------------------------
    # Astral fall hazard
    # ------------------------------------------------------------------
    def _begin_fall(self, kind: str) -> None:
        """Lock control and let Chuck quietly drop into the wrong map."""
        self._fall_kind = kind
        self._fall_t = 0.0
        self.player.fall_progress = 0.0
        self.player.moving = False
        self.player.scratch_remaining = 0.0
        self.player.hurt_blink = 0.0
        self._step_timer = 0.0

    def _update_fall(self, dt: float) -> None:
        """Shrink and sink Chuck, then hand off to ordinary respawn."""
        assert self._fall_t is not None
        self._fall_t += dt
        self.player.fall_progress = min(1.0, self._fall_t / config.FALL_DURATION)
        if self._fall_t >= config.FALL_DURATION:
            kind = self._fall_kind
            self._fall_t = None
            self._fall_kind = None
            self.player.fall_progress = None
            if kind == "sky":
                from src.scenes.falling_cutscene_scene import FallingCutsceneScene
                self.game.scenes.replace(FallingCutsceneScene(self.game))
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
