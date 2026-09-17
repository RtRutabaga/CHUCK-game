"""Phase 8 --- Phlegethos, the Nine Hells overworld (arrival slice).

Chuck lands from the Nine Hells fall onto a cracked-basalt clearing
scarred by lava. Lava is a walkable, lethal fall hazard (like the Astral
Sea); a worn stone path winds from his landing past the Ashtray toward
the way onward. The infernal enemies, lava-island jumps, the fortress
climax, the dedicated soundtrack, and the Feywild-river ending are later
slices; here we just get Chuck onto the ground.
"""

from collections import deque
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.breakable_urn import BreakableUrn
from src.entities.pickup import CigaretteCarton
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.fall import fall_zone_kind
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC

MAP_NAME = "phlegethos_arrival"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_arrival_is_a_basalt_clearing_scarred_by_lava() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (44, 30)
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("arrival:from_hell") == 1
    assert kinds.count("anchor:phlegethos_anchor") == 1
    assert kinds.count("arrival:from_phlegethos_2") == 1  # returning south
    lava = sum(row.count("≋") for row in tilemap._grid)
    path = sum(row.count("≡") for row in tilemap._grid)
    assert lava >= 40, lava
    assert path >= 60, path
    # No enemies yet (they are later slices).
    assert not any(k in {"rat", "zombie", "skeleton", "raptor",
                         "massive_dinosaur", "snake"} for k in kinds)


def test_lava_is_a_lethal_walkable_fall_hazard() -> None:
    import pygame

    # Lava underfoot triggers the (shared) Astral fall; airborne is safe.
    ts = config.TILE_SIZE
    box = pygame.Rect(5 * ts, 5 * ts, 8, 8)

    class _Lava:
        def terrain_at(self, c, r):
            return "≋"

    assert fall_zone_kind(_Lava(), box, airborne=False) == "astral"
    assert fall_zone_kind(_Lava(), box, airborne=True) is None
    # Lava is not solid (Chuck can walk onto it and fall in)...
    assert not TILE_DEFS["≋"].solid
    # ...but enemies treat it as a wall, like every other fall hazard.
    assert "≋" in collision.FALL_HAZARD_TERRAIN


def test_arrival_reaches_the_ashtray_and_the_way_onward_on_foot() -> None:
    tilemap = _map()
    ts = config.TILE_SIZE
    pts = {kind.split(":", 1)[1]: (int(x // ts), int(y // ts))
           for kind, (x, y) in tilemap.object_spawns}
    start = pts["from_hell"]
    reached = {start}
    frontier = deque([start])
    while frontier:
        c, r = frontier.popleft()
        for nc, nr in ((c - 1, r), (c + 1, r), (c, r - 1), (c, r + 1)):
            if (nc, nr) in reached:
                continue
            # On foot the lava is impassable (a lethal fall).
            if tilemap.is_solid(nc, nr) or tilemap.terrain_at(nc, nr) == "≋":
                continue
            reached.add((nc, nr))
            frontier.append((nc, nr))
    assert pts["phlegethos_anchor"] in reached
    # ...and so is the ash-choked pass onward to the lava road.
    onward = next((c, r) for r in range(tilemap.height_tiles)
                  for c in range(tilemap.width_tiles)
                  if tilemap.terrain_at(c, r) == "∇")
    assert onward in reached


def test_phlegethos_uses_its_own_tileset_and_infernal_theme() -> None:
    tileset = tileset_for(MAP_NAME)
    assert tileset.sheet == "phlegethos.png"
    assert tileset.info()["lava"][1] >= 2  # lava is animated
    assert tileset.char_to_terrain["V"] == "astral_void"
    assert tileset.info()["astral_void"] == (2, 3)
    # Every Phlegethos map plays the realm's own driving infernal theme.
    for name in (
        MAP_NAME,
        "phlegethos_road",
        "phlegethos_lake",
        "phlegethos_rubble_pass",
        "phlegethos_fractured_way",
        "phlegethos_fortress_approach",
    ):
        assert AREA_MUSIC[name] == "phlegethos.wav", name


def test_phlegethos_checkpoints_are_registered() -> None:
    entry = CHECKPOINT_BY_ID["phlegethos_arrival"]
    assert entry.display_name == "Phlegethos 1"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_hell"
    assert entry.runtime_entry and entry.fade_in
    anchor = CHECKPOINT_BY_ID["phlegethos_anchor"]
    assert anchor.map_name == MAP_NAME
    assert anchor.saveable and not anchor.development_visible


def test_phlegethos_loads_and_places_chuck_on_the_landing() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("phlegethos_arrival")
        assert scene.map_name == MAP_NAME
        assert len(scene.anchors) == 1
        assert scene._player_tile() == (22, 27)  # the from_hell landing
    finally:
        game._shutdown()


ROAD = "phlegethos_road"


def test_the_lava_road_pinches_to_a_ledge_and_is_walkable_end_to_end() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{ROAD}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (48, 32)
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("arrival:from_phlegethos_1") == 1
    assert kinds.count("anchor:phlegethos_road_anchor") == 1
    assert kinds.count("arrival:from_phlegethos_3") == 1  # back from the lake
    # Far more lava than the arrival: the road is the first real gauntlet.
    assert sum(row.count("≋") for row in tilemap._grid) >= 150
    # Its waist is a single-tile stone ledge with lava on both sides.
    ledge = [c for c in range(48) if tilemap.terrain_at(c, 16) == "≡"
             and tilemap.terrain_at(c, 15) == "≋"
             and tilemap.terrain_at(c, 17) == "≋"]
    assert len(ledge) >= 4, ledge
    # Entry, Ashtray, both passes and the onward boundary all connect on
    # foot (lava is lethal, so it may never be routed through).
    ts = config.TILE_SIZE
    pts = {kind.split(":", 1)[1]: (int(x // ts), int(y // ts))
           for kind, (x, y) in tilemap.object_spawns
           if kind.startswith(("arrival:", "anchor:", "boundary:"))}
    start = pts["from_phlegethos_1"]
    reached = {start}
    frontier = deque([start])
    while frontier:
        c, r = frontier.popleft()
        for nxt in ((c - 1, r), (c + 1, r), (c, r - 1), (c, r + 1)):
            if nxt in reached or tilemap.is_solid(*nxt):
                continue
            if tilemap.terrain_at(*nxt) == "≋":
                continue
            reached.add(nxt)
            frontier.append(nxt)
    assert pts["phlegethos_road_anchor"] in reached
    for char in ("∇", "Δ"):
        gap = next((c, r) for r in range(tilemap.height_tiles)
                   for c in range(tilemap.width_tiles)
                   if tilemap.terrain_at(c, r) == char)
        assert gap in reached, char


def test_lemures_and_fire_snakes_reuse_the_established_enemies() -> None:
    from src.entities.snake import TempleSnake
    from src.entities.undead import UndeadEnemy

    tilemap = TileMap(config.MAPS_DIR / f"{ROAD}.txt")
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("lemure") >= 5
    assert kinds.count("fire_snake") >= 5

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("phlegethos_road")
        # Lemures ARE undead: the zombie/skeleton lifecycle, third kind.
        assert scene.undead and all(isinstance(e, UndeadEnemy)
                                    and e.kind == "lemure"
                                    for e in scene.undead)
        lemure = scene.undead[0]
        assert lemure.speed == config.LEMURE_SPEED
        assert lemure.damage == config.LEMURE_SANITY_DAMAGE
        assert lemure.max_scratches == config.LEMURE_SCRATCHES
        # Slower and more durable than the Chultan undead it reuses.
        assert lemure.speed < config.ZOMBIE_SPEED
        assert lemure.max_scratches > config.ZOMBIE_SCRATCHES
        # Fire snakes ARE temple snakes: same class, molten sprite only.
        assert scene.snakes and all(isinstance(s, TempleSnake)
                                    and s.variant == "fire_snake"
                                    for s in scene.snakes)
        snake = scene.snakes[0]
        assert snake.speed == config.SNAKE_SPEED
        assert snake.max_scratches == 1  # still one scratch to clear
    finally:
        game._shutdown()


def test_the_two_phlegethos_maps_connect_both_ways() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("phlegethos_arrival")
        scene._arrival_fade_t = None
        onward = next((c, r) for r in range(scene.tilemap.height_tiles)
                      for c in range(scene.tilemap.width_tiles)
                      if scene.tilemap.terrain_at(c, r) == "∇")
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == ROAD
        assert game.active_checkpoint_id == "phlegethos_road"
        scene.update(0.0)
        assert scene.map_name == ROAD  # no transition bounce

        back = next((c, r) for r in range(scene.tilemap.height_tiles)
                    for c in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(c, r) == "Δ")
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "phlegethos_1_return"
    finally:
        game._shutdown()


LAKE = "phlegethos_lake"


def test_the_lava_lake_is_crossed_by_single_hop_stepping_stones() -> None:
    """The phase's set piece: islands over a lava lake, every gap exactly
    one tile so each crossing is one committed jump (the temple Astral
    connector's rule). Nothing safe may be stranded."""
    tilemap = TileMap(config.MAPS_DIR / f"{LAKE}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (44, 34)
    # It really is a lake: lava dominates the map.
    lava = {(c, r) for r in range(tilemap.height_tiles)
            for c in range(tilemap.width_tiles)
            if tilemap.terrain_at(c, r) == "≋"}
    assert len(lava) >= 400, len(lava)
    safe = {(c, r) for r in range(tilemap.height_tiles)
            for c in range(tilemap.width_tiles)
            if not tilemap.is_solid(c, r) and (c, r) not in lava}

    ts = config.TILE_SIZE
    pts = {kind.split(":", 1)[1]: (int(x // ts), int(y // ts))
           for kind, (x, y) in tilemap.object_spawns
           if kind.startswith(("arrival:", "anchor:", "boundary:"))}
    start = pts["from_phlegethos_2"]

    # Walk on safe cells; jump clears EXACTLY one lava cell onto safe floor.
    reached = {start}
    frontier = deque([start])
    while frontier:
        c, r = frontier.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            walk = (c + dc, r + dr)
            if walk in safe and walk not in reached:
                reached.add(walk)
                frontier.append(walk)
            over = (c + dc, r + dr)
            land = (c + 2 * dc, r + 2 * dr)
            if over in lava and land in safe and land not in reached:
                reached.add(land)
                frontier.append(land)
    assert reached == safe, sorted(safe - reached)[:8]
    assert pts["phlegethos_lake_anchor"] in reached
    assert pts["from_phlegethos_4"] in reached  # the far shore, onward

    # The crossing genuinely requires hops: the far shore is NOT reachable
    # by walking alone.
    walk_only = {start}
    frontier = deque([start])
    while frontier:
        c, r = frontier.popleft()
        for nxt in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
            if nxt in safe and nxt not in walk_only:
                walk_only.add(nxt)
                frontier.append(nxt)
    assert pts["from_phlegethos_4"] not in walk_only, "the lake can be walked!"
    # And a good number of separate islands stand in the lava.
    islands = []
    seen: set = set()
    for cell in sorted(safe):
        if cell in seen:
            continue
        blob = {cell}
        stack = [cell]
        while stack:
            c, r = stack.pop()
            for nxt in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
                if nxt in safe and nxt not in blob:
                    blob.add(nxt)
                    stack.append(nxt)
        seen |= blob
        islands.append(blob)
    # Two shores plus the stepping stones, each its own disconnected blob.
    assert len(islands) >= 8, len(islands)


def test_the_road_and_lake_connect_both_ways() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("phlegethos_road")
        scene._arrival_fade_t = None
        onward = next((c, r) for r in range(scene.tilemap.height_tiles)
                      for c in range(scene.tilemap.width_tiles)
                      if scene.tilemap.terrain_at(c, r) == "∇")
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == LAKE
        assert game.active_checkpoint_id == "phlegethos_lake"
        scene.update(0.0)
        assert scene.map_name == LAKE  # no bounce

        back = next((c, r) for r in range(scene.tilemap.height_tiles)
                    for c in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(c, r) == "Δ")
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == ROAD
        assert game.active_checkpoint_id == "phlegethos_2_return"
    finally:
        game._shutdown()


def test_spined_devils_are_stationary_throwers_and_fatal_in_melee() -> None:
    from src.entities.spined_devil import FlamingSpine, SpinedDevil

    tilemap = TileMap(config.MAPS_DIR / f"{ROAD}.txt")
    perches = [kind for kind, _pos in tilemap.object_spawns
               if kind.startswith("spined_devil:")]
    assert len(perches) >= 3
    assert all(k.split(":", 1)[1] in {"up", "down", "left", "right"}
               for k in perches)

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("phlegethos_road")
        scene._arrival_fade_t = None
        devils = scene.spined_devils
        assert devils and all(isinstance(d, SpinedDevil) for d in devils)
        # They never move: a perch is a fixed lane problem.
        home = [(d.x, d.y) for d in devils]
        for _ in range(40):
            scene.update(0.05)
        assert [(d.x, d.y) for d in devils] == home
        # ...but they throw burning spines on a cadence.
        assert scene.spines and all(isinstance(s, FlamingSpine)
                                    for s in scene.spines)
        # A spine costs Sanity and is spent on impact.
        scene.spines = []
        spine = FlamingSpine(scene.player.hitbox.centerx,
                             scene.player.hitbox.centery, "down")
        scene.spines.append(spine)
        before = scene.sanity.current
        scene.update(0.01)
        assert scene.sanity.current == before - config.SPINE_SANITY_DAMAGE
        assert spine not in scene.spines

        # Closing to melee is simply fatal, however much Sanity remains.
        devil = devils[0]
        scene.sanity.current = scene.sanity.maximum
        scene.player.x = devil.x - 4
        scene.player.y = devil.y
        scene.player.facing = "right"
        game.input.begin_frame()
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.02)
        assert scene.sanity.current == 0, "scratching a spined devil must kill"
    finally:
        game._shutdown()


def test_flameskulls_weave_as_unkillable_hazards_over_the_lava() -> None:
    from src.entities.flameskull import Flameskull

    tilemap = TileMap(config.MAPS_DIR / f"{LAKE}.txt")
    haunts = [kind for kind, _pos in tilemap.object_spawns
              if kind.startswith("flameskull:")]
    assert len(haunts) >= 3
    # They float, so their markers leave the molten tile beneath intact.
    ts = config.TILE_SIZE
    for kind, (x, y) in tilemap.object_spawns:
        if kind.startswith("flameskull:"):
            assert tilemap.terrain_at(int(x // ts), int(y // ts)) == "≋"

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(LAKE)
        scene._arrival_fade_t = None
        skulls = scene.flameskulls
        assert skulls and all(isinstance(s, Flameskull) for s in skulls)
        # They weave: fast movement that returns around a fixed haunt.
        skull = skulls[0]
        seen = set()
        for _ in range(120):
            scene.update(0.05)
            seen.add((round(skull.x), round(skull.y)))
        assert len(seen) > 20, "a flameskull should weave, not sit"
        spread = max(abs(x - skull.home[0]) for x, _y in seen)
        assert spread <= config.FLAMESKULL_RANGE + config.FLAMESKULL_WEAVE + 8

        # Put one exactly where Chuck stands on the safe shore (he cannot
        # stand in the lava they haunt), so contact is judged on its own.
        haunt = Flameskull(scene.player.hitbox.centerx,
                           scene.player.hitbox.centery, "h")
        haunt._t = 0.0  # at rest on its haunt, i.e. right on top of him
        haunt.load_sprites(game.assets)
        scene.flameskulls.append(haunt)
        before_count = len(scene.flameskulls)

        # Touching one costs Chuck Sanity...
        scene.sanity.current = scene.sanity.maximum
        scene.update(0.001)
        assert scene.sanity.current == (
            scene.sanity.maximum - config.FLAMESKULL_SANITY_DAMAGE)

        # ...and it cannot be cleared: scratching one changes nothing.
        game.input.begin_frame()
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.001)
        assert len(scene.flameskulls) == before_count
    finally:
        game._shutdown()


APPROACH = "phlegethos_fortress_approach"

PHLEGETHOS_URN_COUNTS = {
    MAP_NAME: 3,
    ROAD: 3,
    LAKE: 4,
    "phlegethos_rubble_pass": 3,
    APPROACH: 4,
}


def test_all_phlegethos_maps_reuse_carton_filled_temple_urns() -> None:
    game = Game()
    try:
        for map_name, expected_count in PHLEGETHOS_URN_COUNTS.items():
            tilemap = TileMap(config.MAPS_DIR / f"{map_name}.txt")
            authored = [
                (col, row) for kind, col, row in tilemap.prop_tiles
                if kind == "temple_urn"
            ]
            assert len(authored) == expected_count, (map_name, authored)
            assert all(
                tilemap.terrain_at(col, row) == chr(0xA2)
                for col, row in authored
            )

            scene = game.checkpoints.load_checkpoint(map_name)
            scene._pending_entrance_dialogue = None
            scene._arrival_fade_t = None
            urns = [
                item for item in scene.breakables
                if isinstance(item, BreakableUrn)
            ]
            assert len(urns) == expected_count
            urn = urns[0]
            col = int(urn._center_x // config.TILE_SIZE)
            row = int(urn._bottom // config.TILE_SIZE) - 1
            urn.on_scratched()
            scene.update(0.0)
            assert scene.tilemap.terrain_at(col, row) == chr(0xB7)
            assert isinstance(scene.pickups[-1], CigaretteCarton)
            assert scene.pickups[-1].cigarette_count == 20
    finally:
        game._shutdown()


def test_the_fortress_approach_establishes_the_wall_gate_and_idols() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{APPROACH}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (48, 34)
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("arrival:from_phlegethos_rubble") == 1
    assert kinds.count("anchor:phlegethos_4_anchor") == 1
    assert kinds.count("boundary:phlegethos_fortress") == 1  # the climax
    for actor in ("fighter", "wizard", "ranger", "pit_fiend"):
        assert kinds.count(f"battle:{actor}") == 1
    battle_positions = {
        kind.split(":", 1)[1]: position
        for kind, position in tilemap.object_spawns
        if kind.startswith("battle:")
    }
    # The 128px Pit Fiend must not cover the wizard's complete silhouette.
    assert (
        battle_positions["wizard"][0]
        > battle_positions["pit_fiend"][0] + 128
    )
    # The setting's remaining visual beats: an iron-black fortress wall
    # closing off the north, its shut gate, and brooding infernal idols.
    fortress = sum(row.count("▓") for row in tilemap._grid)
    gate = sum(row.count("╬") for row in tilemap._grid)
    statues = [(c, r) for kind, c, r in tilemap.prop_tiles
               if kind == "phlegethos_statue"]
    assert fortress >= 150, fortress
    assert gate >= 6, gate
    assert len(statues) >= 6, len(statues)
    # Wall, gate and idols are all solid: the fortress interior is not
    # this phase, and the idols are scenery to walk around.
    assert TILE_DEFS["▓"].solid and TILE_DEFS["╬"].solid
    assert all(tilemap.is_solid(c, r) for c, r in statues)
    # The gate sits inside the wall band, not out in the open.
    gate_rows = {r for r in range(tilemap.height_tiles)
                 for c in range(tilemap.width_tiles)
                 if tilemap.terrain_at(c, r) == "╬"}
    assert max(gate_rows) <= 8, gate_rows

    # Entry, Ashtray, the gate approach and the pass back all connect on
    # foot without routing through lava.
    ts = config.TILE_SIZE
    pts = {kind.split(":", 1)[1]: (int(x // ts), int(y // ts))
           for kind, (x, y) in tilemap.object_spawns
           if kind.startswith(("arrival:", "anchor:", "boundary:"))}
    start = pts["from_phlegethos_rubble"]
    reached = {start}
    frontier = deque([start])
    while frontier:
        c, r = frontier.popleft()
        for nxt in ((c - 1, r), (c + 1, r), (c, r - 1), (c, r + 1)):
            if nxt in reached or tilemap.is_solid(*nxt):
                continue
            if tilemap.terrain_at(*nxt) == "≋":
                continue
            reached.add(nxt)
            frontier.append(nxt)
    assert pts["phlegethos_4_anchor"] in reached
    assert pts["phlegethos_fortress"] in reached
    back = next((c, r) for r in range(tilemap.height_tiles)
                for c in range(tilemap.width_tiles)
                if tilemap.terrain_at(c, r) == "Δ")
    assert back in reached


def test_horned_devils_reuse_the_massive_dinosaur_wholesale() -> None:
    from src.entities.massive_dinosaur import MassiveDinosaur

    tilemap = TileMap(config.MAPS_DIR / f"{APPROACH}.txt")
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("horned_devil") >= 1
    # The garrison mixes every lesser devil the realm has introduced.
    assert kinds.count("lemure") >= 2
    assert kinds.count("fire_snake") >= 2
    assert sum(1 for k in kinds if k.startswith("spined_devil:")) >= 1

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(APPROACH)
        devils = scene.dinosaurs
        assert devils and all(isinstance(d, MassiveDinosaur) for d in devils)
        devil = devils[0]
        # It IS the Chult colossus: identical stats, infernal art only.
        assert devil.variant == "horned_devil"
        assert devil.speed == config.DINOSAUR_SPEED
        assert devil.damage == config.DINOSAUR_SANITY_DAMAGE
        assert devil.max_scratches == config.DINOSAUR_SCRATCHES
        # It towers: the frame is far larger than a human NPC's.
        frame = devil._frames["down"][0]
        assert frame.get_width() == config.DINOSAUR_FRAME_W
        assert frame.get_height() == config.DINOSAUR_FRAME_H
        assert frame.get_height() > config.UNDEAD_FRAME_H
    finally:
        game._shutdown()


def test_phlegethos_ashtray_markers_resolve_to_saveable_definitions() -> None:
    """Every authored Phase 8 Ashtray must activate through the registry."""
    for map_name in (
        "phlegethos_arrival",
        ROAD,
        LAKE,
        "phlegethos_rubble_pass",
        "phlegethos_fractured_way",
        APPROACH,
    ):
        tilemap = TileMap(config.MAPS_DIR / f"{map_name}.txt")
        anchor_ids = [
            kind.split(":", 1)[1]
            for kind, _position in tilemap.object_spawns
            if kind.startswith("anchor:")
        ]
        assert len(anchor_ids) == 1, (map_name, anchor_ids)
        definition = CHECKPOINT_BY_ID[anchor_ids[0]]
        assert definition.map_name == map_name
        assert definition.saveable


def test_the_trio_battles_the_pit_fiend_through_shared_choreography() -> None:
    from src.entities.battle_hazards import InfernalBattleChoreographer

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(APPROACH)
        by_kind = {actor.kind: actor for actor in scene.battle_actors}
        assert set(by_kind) == {"fighter", "wizard", "ranger", "pit_fiend"}
        assert isinstance(scene.battle, InfernalBattleChoreographer)
        assert scene.breach is None  # the temple's scripted seal stays there

        # A short deterministic window produces direct trio attacks and a
        # Pit Fiend answer without starting the later reality-break climax.
        tick = scene.battle.update(2.0)
        kinds = {shot.kind for shot in tick.projectiles}
        assert {"arrow", "bolt", "ray"} <= kinds
        fiend = by_kind["pit_fiend"]
        assert fiend._image.get_size() == (128, 128)
        assert (fiend.width, fiend.height) == (64, 32)
        assert fiend._image.get_height() >= config.UNDEAD_FRAME_H * 4
        wizard = by_kind["wizard"]
        fiend_left = fiend.center_x - fiend._image.get_width() / 2
        fiend_right = fiend.center_x + fiend._image.get_width() / 2
        wizard_left = wizard.center_x - wizard._image.get_width() / 2
        wizard_right = wizard.center_x + wizard._image.get_width() / 2
        assert wizard_left > fiend_right or wizard_right < fiend_left
    finally:
        game._shutdown()


def test_astral_corruption_seals_retreat_then_constricts_the_arena() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(APPROACH)
        corruption = scene.infernal_corruption
        assert corruption is not None and not corruption.triggered

        # The WorldScene owns the trigger: the lower approach stays intact,
        # then crossing into the upper yard starts the corruption.
        scene._pending_entrance_dialogue = None
        scene.player.x = 24 * config.TILE_SIZE
        scene.player.y = (
            config.INFERNAL_CORRUPTION_TRIGGER_ROW + 1
        ) * config.TILE_SIZE
        scene.update(0.01)
        assert not corruption.triggered
        scene.player.y = (
            config.INFERNAL_CORRUPTION_TRIGGER_ROW
        ) * config.TILE_SIZE
        scene.update(0.01)
        assert corruption.triggered

        # The first event is a two-row, unjumpable seal behind Chuck. Give
        # its center-out cascade time to finish.
        corruption.update(2.0, scene.player.hitbox)
        for row in config.INFERNAL_CORRUPTION_SEAL_ROWS:
            original_safe = [
                col for col in range(scene.tilemap.width_tiles)
                if scene.tilemap.terrain_at(col, row) == "V"
            ]
            assert len(original_safe) >= 10, (row, original_safe)

        # Three later incursions eat inward from both sides, but the authored
        # central spine remains safe until the later Feywild-river slice.
        corruption.update(12.0, scene.player.hitbox)
        astral = {
            (col, row)
            for row in range(scene.tilemap.height_tiles)
            for col in range(scene.tilemap.width_tiles)
            if scene.tilemap.terrain_at(col, row) == "V"
        }
        assert len(astral) >= 70, len(astral)
        assert corruption.wave_index == 3
        assert all(
            scene.tilemap.terrain_at(col, row) != "V"
            for row in range(10, 21)
            for col in range(21, 28)
        )

        # Ordinary death/reset restores the authored basalt and re-arms the
        # complete sequence rather than saving a corrupted runtime map.
        scene._reset_enemies()
        assert scene.infernal_corruption is not corruption
        assert not scene.infernal_corruption.triggered
        assert not any(
            scene.tilemap.terrain_at(col, row) == "V"
            for row in range(scene.tilemap.height_tiles)
            for col in range(scene.tilemap.width_tiles)
        )
    finally:
        game._shutdown()


def test_astral_corruption_never_opens_directly_beneath_chuck() -> None:
    import pygame

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(APPROACH)
        corruption = scene.infernal_corruption
        corruption.trigger((24, config.INFERNAL_CORRUPTION_TRIGGER_ROW))
        row = config.INFERNAL_CORRUPTION_SEAL_ROWS[0]
        chuck_tile = pygame.Rect(24 * config.TILE_SIZE,
                                 row * config.TILE_SIZE,
                                 config.TILE_SIZE, config.TILE_SIZE)
        corruption.update(2.0, chuck_tile)
        assert scene.tilemap.terrain_at(24, row) != "V"
        corruption.update(0.1, None)
        assert scene.tilemap.terrain_at(24, row) == "V"
    finally:
        game._shutdown()


def test_river_builds_to_an_unavoidable_surge_while_astral_stays_open() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(APPROACH)
        scene._pending_entrance_dialogue = None
        corruption = scene.infernal_corruption
        corruption.trigger((24, config.INFERNAL_CORRUPTION_TRIGGER_ROW))

        corruption.update(config.FEYWILD_RIVER_START_TIME - 0.1, None)
        scene.update(0.0)
        assert not scene.feywild_river.active

        corruption.update(0.1, None)
        scene.update(0.0)
        river = scene.feywild_river
        assert river.active and len(river.blocks) == 10
        before = [block.x for block in river.blocks]
        river.update(1.0)
        assert all(
            after < prior
            for after, prior in zip(
                (block.x for block in river.blocks), before,
            )
        )

        # All Astral waves have landed, but the broad central refuge remains
        # readable and safe. Purple pressure is avoidable at the climax.
        corruption.update(
            config.INFERNAL_CORRUPTION_WAVE_TIMES[-1]
            - corruption.elapsed + 1.0,
            None,
        )
        assert corruption.wave_index == 3
        center_astral = sum(
            scene.tilemap.terrain_at(col, row) == "V"
            for row in range(10, 23)
            for col in range(21, 28)
        )
        assert center_astral == 0, center_astral

        # Six seconds after the river begins, eighteen additional blocks
        # arrive aligned as a complete arena-height wall. Every playable row
        # from the fortress gate to the retreat seal is covered at the same x,
        # so this late river surge cannot be avoided or outlasted.
        river.update(config.FEYWILD_RIVER_SURGE_TIME)
        surge = [block for block in river.blocks if block.surge]
        assert river.surge_spawned and len(river.blocks) == 28
        assert {int(block.y // config.TILE_SIZE) for block in surge} == set(
            range(7, 25)
        )
        assert len({block.x for block in surge}) == 1

        old_river = river
        scene._reset_enemies()
        assert scene.feywild_river is not old_river
        assert not scene.feywild_river.active
        assert not any(
            scene.tilemap.terrain_at(col, row) == "V"
            for row in range(scene.tilemap.height_tiles)
            for col in range(scene.tilemap.width_tiles)
        )
    finally:
        game._shutdown()


def test_walking_or_jumping_into_river_falls_then_starts_cutscene() -> None:
    game = Game()
    try:
        for jumping in (False, True):
            scene = game.checkpoints.load_checkpoint(APPROACH)
            scene._pending_entrance_dialogue = None
            scene._arrival_fade_t = None
            scene.feywild_river.activate()
            block = scene.feywild_river.blocks[0]
            scene.player.x = block.x + 8
            scene.player.y = block.y + 4
            scene.player.jump_remaining = (
                config.JUMP_DURATION / 2 if jumping else 0.0
            )

            scene.update(0.0)
            assert scene._fall_kind == "river"
            assert scene._fall_t == 0.0
            assert scene.player.fall_progress == 0.0
            assert scene.player.visible
            assert not scene.player.jumping

            # The complete shared shrink/sink animation plays before the
            # success handoff. Unlike Astral/lava falls, Sanity is untouched.
            sanity = scene.sanity.current
            scene.update(config.FALL_DURATION)
            assert scene._fall_t is None
            assert scene._river_escape_t == 0.0
            assert not scene.player.visible
            assert scene.sanity.current == sanity
    finally:
        game._shutdown()


def test_the_lake_and_rubble_pass_connect_both_ways() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(LAKE)
        scene._arrival_fade_t = None
        onward = next((c, r) for r in range(scene.tilemap.height_tiles)
                      for c in range(scene.tilemap.width_tiles)
                      if scene.tilemap.terrain_at(c, r) == "∇")
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "phlegethos_rubble_pass"
        assert game.active_checkpoint_id == "phlegethos_rubble_pass"
        scene.update(0.0)
        assert scene.map_name == "phlegethos_rubble_pass"  # no bounce

        # He came out at the pass's south gate, walking north, rather
        # than against its west wall facing east.
        arrival = scene._player_tile()
        assert arrival[1] > scene.tilemap.height_tiles - 6, arrival
        assert scene.player.facing == "up"

        back = next((c, r) for r in range(scene.tilemap.height_tiles)
                    for c in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(c, r) == "⌄")
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == LAKE
        assert game.active_checkpoint_id == "phlegethos_3_return"
    finally:
        game._shutdown()


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All Phlegethos arrival tests passed.")


if __name__ == "__main__":
    _run_all()


def test_the_seal_hands_the_realms_theme_over_to_its_fight_version() -> None:
    """Walking up to the wall is exploring; the seal is the fight.

    The approach keeps the realm's own theme while Chuck is still
    walking it, and swaps to the fight arrangement at the moment the
    Astral closes behind him. Dying puts it back, because the respawn
    rebuilds the approach in place rather than reloading the scene.
    """
    from src.world.transitions import AREA_MUSIC, FORTRESS_BATTLE_MUSIC

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(APPROACH)
        scene._pending_entrance_dialogue = None
        played = []
        game.audio.play_music = lambda name, loop=True: played.append(name)

        scene.player.x = 24 * config.TILE_SIZE
        scene.player.y = (
            config.INFERNAL_CORRUPTION_TRIGGER_ROW + 1
        ) * config.TILE_SIZE
        scene.update(0.01)
        assert played == []

        scene.player.y = (
            config.INFERNAL_CORRUPTION_TRIGGER_ROW
        ) * config.TILE_SIZE
        scene.update(0.01)
        assert played == [FORTRESS_BATTLE_MUSIC]

        scene._reset_enemies()
        assert played[-1] == AREA_MUSIC[APPROACH]
    finally:
        game._shutdown()
