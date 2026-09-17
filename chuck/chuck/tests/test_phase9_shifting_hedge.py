"""Phase 9 Map 9 --- the Shifting Hedge.

The phase's main navigation puzzle: one ring corridor gated at four
corners, two gates open and two shut, and four flowers that each trade
one doorway for another. The hedge is deterministic and inspectable --
never randomised -- so these tests reason about it exactly as the player
is meant to.

The important test is the last one. It walks the entire state space (every
tile in every combination of the four groups) and proves that from every
state Chuck can reach, the exit is still reachable: no sequence of
scratches, in any order, can strand him.
"""

from collections import deque
from itertools import product
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

MAP_NAME = "feywild_shifting_hedge"
WARRENS = "feywild_redcap_warrens"
GROUP_IDS = ("hedge_east", "hedge_north", "hedge_south", "hedge_west")


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _tile(position):
    ts = config.TILE_SIZE
    return (int(position[0] // ts), int(position[1] // ts))


def _points(tilemap):
    return {kind.split(":", 1)[1]: _tile(pos)
            for kind, pos in tilemap.object_spawns
            if kind.startswith(("arrival:", "boundary:"))}


def _new_scene(game):
    scene = game.checkpoints.load_checkpoint("feywild_9")
    scene._arrival_fade_t = None
    return scene


def _settle(scene, seconds=1.0):
    remaining = seconds
    while remaining > 0.0:
        scene.update(0.05)
        remaining -= 0.05


def test_the_hedge_is_a_deterministic_ring_with_four_flower_groups() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (68, 44)
    game = Game()
    try:
        scene = _new_scene(game)
        controller = scene.reactive_flowers
        assert sorted(controller.groups) == list(GROUP_IDS)
        assert len(controller.flowers) == len(GROUP_IDS)
        # Every group trades: it opens hedge and closes open ground. The
        # controller refuses to build a group that only gives.
        for group_id, group in controller.groups.items():
            assert group.opens and group.closes, group_id
            assert not group.active
            for target in group.opens:
                assert scene.tilemap.is_solid(target.col, target.row)
            for target in group.closes:
                assert not scene.tilemap.is_solid(target.col, target.row)
    finally:
        game._shutdown()


def test_a_scratched_flower_trades_one_doorway_for_another() -> None:
    game = Game()
    try:
        scene = _new_scene(game)
        controller = scene.reactive_flowers
        group = controller.groups["hedge_north"]
        shut = group.opens[0]
        open_ground = group.closes[0]

        flower = next(f for f in controller.flowers
                      if f.group_id == "hedge_north")
        scene.player.x = flower.x - 10
        scene.player.y = flower.y
        scene.player.facing = "right"
        game.input.begin_frame()
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.001)
        # The flower pulses first; terrain must not snap instantly.
        assert scene.tilemap.is_solid(shut.col, shut.row)
        _settle(scene, config.REACTIVE_FLOWER_CHANGE_DELAY + 0.2)

        assert group.active
        assert not scene.tilemap.is_solid(shut.col, shut.row)
        assert scene.tilemap.is_solid(open_ground.col, open_ground.row)
        assert flower._active

        # A second scratch is the reciprocal: the hedge trades back.
        game.input.begin_frame()
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.001)
        _settle(scene, config.REACTIVE_FLOWER_CHANGE_DELAY + 0.2)
        assert not group.active
        assert scene.tilemap.is_solid(shut.col, shut.row)
        assert not scene.tilemap.is_solid(open_ground.col, open_ground.row)
    finally:
        game._shutdown()


def test_the_hedge_never_changes_under_chuck_and_resets_on_respawn() -> None:
    game = Game()
    try:
        scene = _new_scene(game)
        controller = scene.reactive_flowers
        group = controller.groups["hedge_north"]
        closing = group.closes[0]

        # Standing on the tile the flower wants to fill: the change waits.
        scene.player.x = closing.col * config.TILE_SIZE + 1
        scene.player.y = closing.row * config.TILE_SIZE + 1
        assert controller.trigger("hedge_north")
        _settle(scene, config.REACTIVE_FLOWER_CHANGE_DELAY + 0.5)
        assert not group.active
        assert not scene.tilemap.is_solid(closing.col, closing.row)

        # Step off and it lands.
        scene.player.x = (closing.col + 3) * config.TILE_SIZE
        _settle(scene, 0.3)
        assert group.active

        # Sanity zero must restore the authored opening state exactly.
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT)
        scene.update(config.RESPAWN_HOLD)
        assert not group.active
        assert scene.tilemap.is_solid(group.opens[0].col, group.opens[0].row)
        assert not scene.tilemap.is_solid(closing.col, closing.row)
        assert not any(f._active for f in controller.flowers)
    finally:
        game._shutdown()


def test_the_hedge_can_be_solved_and_can_never_strand_chuck() -> None:
    """The whole state space, walked: every reachable state still exits."""
    tilemap = _map()
    points = _points(tilemap)
    start, goal = points["from_feywild_8"], points["feywild_10"]

    game = Game()
    try:
        scene = _new_scene(game)
        groups = {
            group_id: (
                tuple((t.col, t.row) for t in group.opens),
                tuple((t.col, t.row) for t in group.closes),
                _tile((next(f for f in scene.reactive_flowers.flowers
                            if f.group_id == group_id).x + 7,
                       next(f for f in scene.reactive_flowers.flowers
                            if f.group_id == group_id).y + 6)),
            )
            for group_id, group in scene.reactive_flowers.groups.items()
        }
        base_open = {
            (col, row)
            for row in range(tilemap.height_tiles)
            for col in range(tilemap.width_tiles)
            if not scene.tilemap.is_solid(col, row)
        }
    finally:
        game._shutdown()

    def walkable(state):
        tiles = set(base_open)
        for group_id in state:
            opens, closes, _switch = groups[group_id]
            tiles |= set(opens)
            tiles -= set(closes)
        return tiles

    open_by_state = {
        tuple(sorted(combo)): walkable(combo)
        for size in range(len(GROUP_IDS) + 1)
        for combo in product(GROUP_IDS, repeat=size)
    }

    origin = (start, ())
    nodes = {origin}
    backward = {}
    frontier = deque([origin])
    while frontier:
        tile, state = frontier.popleft()
        col, row = tile
        for step in ((col - 1, row), (col + 1, row),
                     (col, row - 1), (col, row + 1)):
            if step not in open_by_state[state]:
                continue
            node = (step, state)
            backward.setdefault(node, []).append((tile, state))
            if node not in nodes:
                nodes.add(node)
                frontier.append(node)
        for group_id, (opens, closes, switch) in groups.items():
            reach = abs(col - switch[0]) + abs(row - switch[1])
            if reach > 1 or tile in set(opens) | set(closes):
                continue
            active = set(state)
            active.symmetric_difference_update({group_id})
            node = (tile, tuple(sorted(active)))
            if tile not in open_by_state[node[1]]:
                continue
            backward.setdefault(node, []).append((tile, state))
            if node not in nodes:
                nodes.add(node)
                frontier.append(node)

    reached = {tile for tile, _state in nodes}
    assert goal in reached, "the hedge cannot be solved"
    caches = {_tile(pos) for kind, pos in tilemap.object_spawns
              if kind == "breakable_grass"}
    assert caches and caches <= reached

    # Standing still solves nothing: the hedge is a real puzzle.
    idle = open_by_state[()]
    walked = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for step in ((col - 1, row), (col + 1, row),
                     (col, row - 1), (col, row + 1)):
            if step in idle and step not in walked:
                walked.add(step)
                frontier.append(step)
    assert goal not in walked, "the hedge can be walked straight through"
    assert not (caches & walked)

    # The safety proof: every reachable state can still reach the exit.
    finishers = {node for node in nodes if node[0] == goal}
    can_finish = set(finishers)
    frontier = deque(finishers)
    while frontier:
        node = frontier.popleft()
        for source in backward.get(node, ()):
            if source not in can_finish:
                can_finish.add(source)
                frontier.append(source)
    assert nodes == can_finish, sorted(nodes - can_finish)[:6]


def test_hedge_checkpoints_music_and_the_warrens_connection() -> None:
    entry = CHECKPOINT_BY_ID["feywild_9"]
    assert entry.display_name == "Feywild 9" and entry.runtime_entry
    assert entry.map_name == MAP_NAME and entry.arrival == "from_feywild_8"
    assert tileset_for(MAP_NAME).sheet == "feywild.png"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"
    assert AREA_WALK_EXITS[(WARRENS, "→")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "←")].destination == WARRENS

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_8")
        scene._arrival_fade_t = None
        onward = next((c, r) for r in range(scene.tilemap.height_tiles)
                      for c in range(scene.tilemap.width_tiles)
                      if scene.tilemap.terrain_at(c, r) == "→")
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_9"
        scene.update(0.0)
        assert scene.map_name == MAP_NAME  # no bounce

        back = next((c, r) for r in range(scene.tilemap.height_tiles)
                    for c in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(c, r) == "←")
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == WARRENS
        assert game.active_checkpoint_id == "feywild_8_return"
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
    print("All Shifting Hedge tests passed.")


if __name__ == "__main__":
    _run_all()
