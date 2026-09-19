"""Phase 9's Blooming Path and reusable reactive-flower introduction."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.reactive_flowers import ReactiveFlowerController
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "feywild_blooming_path"


def _marker_positions(tilemap: TileMap, prefix: str = ""):
    size = config.TILE_SIZE
    return [
        (kind, (int(x // size), int(y // size)))
        for kind, (x, y) in tilemap.object_spawns
        if kind.startswith(prefix)
    ]


def _reachable(tilemap: TileMap, start: tuple[int, int]):
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            if point in reached or tilemap.is_solid(*point):
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_blooming_path_is_a_large_peaceful_two_route_map() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (60, 42)
    assert MAP_TILESET[MAP_NAME] == "feywild"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"

    kinds = Counter(kind for kind, _position in tilemap.object_spawns)
    assert kinds["arrival:from_feywild_1"] == 1
    assert kinds["boundary:feywild_3"] == 1
    assert kinds["flower_switch:intro"] == 1
    assert kinds["flower_open:intro"] == 3
    assert kinds["flower_close:intro"] == 3
    assert kinds["breakable_grass"] == 2
    assert not any(
        kind in {
            "rat", "snake", "zombie", "skeleton", "lemure", "raptor",
            "massive_dinosaur", "horned_devil", "fire_snake",
        }
        for kind in kinds
    )

    props = Counter(kind for kind, _col, _row in tilemap.prop_tiles)
    assert props["feywild_tree"] >= 4
    assert props["feywild_spiral"] >= 2
    assert props["feywild_mushroom"] >= 2


def test_both_authored_flower_states_remain_navigable() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = dict(_marker_positions(tilemap))
    controller = ReactiveFlowerController(tilemap, tilemap.object_spawns)
    arrival = markers["arrival:from_feywild_1"]
    required = {
        markers["boundary:feywild_3"],
        markers["flower_switch:intro"],
    }

    assert required <= _reachable(tilemap, arrival)
    group = controller.groups["intro"]
    assert all(tilemap.is_solid(target.col, target.row)
               for target in group.opens)
    assert all(not tilemap.is_solid(target.col, target.row)
               for target in group.closes)

    assert controller.trigger("intro")
    controller.update(
        config.REACTIVE_FLOWER_CHANGE_DELAY,
        pygame.Rect(-100, -100, 1, 1),
    )
    assert group.active
    assert required <= _reachable(tilemap, arrival)
    assert all(not tilemap.is_solid(target.col, target.row)
               for target in group.opens)
    assert all(tilemap.is_solid(target.col, target.row)
               for target in group.closes)

    assert controller.trigger("intro")
    controller.update(
        config.REACTIVE_FLOWER_CHANGE_DELAY,
        pygame.Rect(-100, -100, 1, 1),
    )
    assert not group.active
    assert required <= _reachable(tilemap, arrival)


def test_flower_waits_until_chuck_is_clear_and_resets_after_death() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    controller = ReactiveFlowerController(tilemap, tilemap.object_spawns)
    target = controller.groups["intro"].opens[0]
    blocking_player = pygame.Rect(
        target.col * config.TILE_SIZE,
        target.row * config.TILE_SIZE,
        config.PLAYER_HITBOX_W,
        config.PLAYER_HITBOX_H,
    )

    controller.trigger("intro")
    controller.update(config.REACTIVE_FLOWER_CHANGE_DELAY, blocking_player)
    assert not controller.groups["intro"].active
    assert tilemap.is_solid(target.col, target.row)

    controller.update(0.0, pygame.Rect(-100, -100, 1, 1))
    assert controller.groups["intro"].active
    assert not tilemap.is_solid(target.col, target.row)

    controller.reset()
    assert not controller.groups["intro"].active
    assert tilemap.is_solid(target.col, target.row)


def test_world_scratch_activates_the_flower_through_normal_combat() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_2")
        flower = scene.reactive_flowers.flowers[0]
        scene.player.x = flower.x - scene.player.width - 2
        scene.player.y = flower.y + (flower.height - scene.player.height) / 2
        scene.player.facing = "right"
        game.input._actions_just_pressed.add("scratch")

        scene.update(0.0)
        assert scene.reactive_flowers._pending_group == "intro"
        assert not scene.reactive_flowers.groups["intro"].active

        scene.update(config.REACTIVE_FLOWER_CHANGE_DELAY)
        assert scene.reactive_flowers.groups["intro"].active
    finally:
        game._shutdown()


def test_grass_beside_first_flower_can_accidentally_trigger_it() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_2")
        flower = scene.reactive_flowers.flowers[0]
        grass = min(
            scene.breakables,
            key=lambda item: abs(item.x - flower.x) + abs(item.y - flower.y),
        )
        assert abs(grass.x - flower.x) <= config.TILE_SIZE
        assert abs(grass.y - flower.y) <= 1

        # Approach between the adjacent targets while apparently scratching
        # upward at the grass. Flower targeting is intentionally first.
        scene.player.x = flower.x - 7
        scene.player.y = flower.y + flower.height + 3
        scene.player.facing = "up"
        assert scene.player.scratch_hitbox().colliderect(grass.hitbox)
        assert scene.player.scratch_hitbox().colliderect(flower.hitbox)
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.0)

        assert scene.reactive_flowers._pending_group == "intro"
        assert grass.alive
    finally:
        game._shutdown()


def test_feywild_boundaries_use_cardinal_vegetation_openings() -> None:
    """Every overhead in the Feywild is a lid over ground somebody stands on.

    Stated as a rule rather than as an inventory. The list here was exact
    until the tea table's lip needed a west and an east tile of its own --
    a beam has a direction, and the horizontal art repeated down the side
    of the table drew a ladder bolted to the furniture -- and an inventory
    fails on the day a new overhead is added whether or not the new one is
    right.
    """
    tileset = tileset_for(MAP_NAME)
    overheads = tileset.overhead_char_to_terrain
    # The four cardinal cuts are still the whole boundary vocabulary...
    assert {
        "\u2190": "fey_opening_w",
        "\u2192": "fey_opening_e",
        "\u21e7": "fey_opening_n",
        "\u21e9": "fey_opening_s",
    }.items() <= overheads.items()
    # ...the two crawl-throughs are still overheads rather than floors...
    assert overheads["\u2240"] == "fey_root_passage"
    assert overheads["\u16bf"] == "fey_mushroom_passage"
    # ...and so is the giant tea table's underside, which is the one
    # overhead out here that is a thing rather than a gap: Chuck walks
    # beneath the boards, and they thin out over him while he is under
    # them the way the market's awning does.
    assert overheads["\u2592"] == "fey_table_under"

    for char, art_name in overheads.items():
        # An overhead is never also a floor: it draws over whatever the
        # tile it is written on resolves to.
        assert char not in tileset.char_to_terrain
        assert TILE_DEFS[char].overhead == art_name
        assert not TILE_DEFS[char].solid, char
        # ...and what it resolves to is ground, so Chuck fits under it.
        assert TILE_DEFS[char].under, char
        assert not TILE_DEFS[TILE_DEFS[char].under].solid, char


def test_feywild_handoffs_are_three_tile_openings_on_outer_edges() -> None:
    """Match Chult's broad boundary cut, never a portal inside the map."""
    expected_edges = {
        "feywild_riverbank": (("east", "→"),),
        "feywild_blooming_path": (("west", "←"), ("east", "→")),
        "feywild_pollen_orchard": (("north", "⇧"), ("south", "⇩")),
        "feywild_rootways": (("west", "←"), ("east", "→")),
        "feywild_needle_garden": (("north", "⇧"), ("east", "→")),
        "feywild_twilight_crossroads": (
            ("south", "⇩"), ("west", "←")
        ),
    }
    for map_name, edges in expected_edges.items():
        tilemap = TileMap(config.MAPS_DIR / f"{map_name}.txt")
        for side, terrain in edges:
            if side == "west":
                cells = [
                    tilemap.terrain_at(0, row)
                    for row in range(tilemap.height_tiles)
                ]
            elif side == "east":
                cells = [
                    tilemap.terrain_at(tilemap.width_tiles - 1, row)
                    for row in range(tilemap.height_tiles)
                ]
            elif side == "north":
                cells = [
                    tilemap.terrain_at(col, 0)
                    for col in range(tilemap.width_tiles)
                ]
            else:
                cells = [
                    tilemap.terrain_at(col, tilemap.height_tiles - 1)
                    for col in range(tilemap.width_tiles)
                ]
            indices = [index for index, char in enumerate(cells)
                       if char == terrain]
            assert len(indices) == 3
            assert indices == list(range(indices[0], indices[0] + 3))


def test_blooming_path_uses_shared_transitions_and_checkpoints() -> None:
    forward = AREA_WALK_EXITS[("feywild_riverbank", "→")]
    backward = AREA_WALK_EXITS[(MAP_NAME, "←")]
    assert forward.destination == MAP_NAME
    assert forward.arrival == "from_feywild_1"
    assert backward.destination == "feywild_riverbank"
    assert backward.arrival == "from_feywild_2"

    entry = CHECKPOINT_BY_ID["feywild_2"]
    return_entry = CHECKPOINT_BY_ID["feywild_1_return"]
    assert entry.display_name == "Feywild 2"
    assert entry.map_name == MAP_NAME and entry.runtime_entry
    assert return_entry.arrival == "from_feywild_2"

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_2")
        assert scene.map_name == MAP_NAME
        assert game.progress.has("feywild_reached")
        assert len(scene.reactive_flowers.flowers) == 1
        assert scene.undead == []
        assert scene.raptors == []
        assert scene.dinosaurs == []
    finally:
        game._shutdown()


def test_riverbank_and_blooming_path_transition_both_ways() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_riverbank")
        # The river-cutscene entry deliberately fades in before control.
        scene.update(config.AREA_FADE_DURATION)
        forward_tile = next(
            (col, row)
            for row, terrain_row in enumerate(scene.tilemap._grid)
            for col, char in enumerate(terrain_row)
            if char == "→"
        )
        scene.player.x = forward_tile[0] * config.TILE_SIZE + 3
        scene.player.y = forward_tile[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_2"

        return_tile = next(
            (col, row)
            for row, terrain_row in enumerate(scene.tilemap._grid)
            for col, char in enumerate(terrain_row)
            if char == "←"
        )
        scene.player.x = return_tile[0] * config.TILE_SIZE + 3
        scene.player.y = return_tile[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "feywild_riverbank"
        assert game.active_checkpoint_id == "feywild_1_return"
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
    print("All Phase 9 Blooming Path tests passed.")


if __name__ == "__main__":
    _run_all()
