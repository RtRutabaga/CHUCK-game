"""Phase 9 Map 12 --- the Luminous Rapids.

The region's traversal systems, added up: one-tile jumps over an
impassable river, reactive flowers deciding which pads are safe, pollen
on the approaches, moths in the lanes, and one orchid kept off the
required route.

The heavy test is the last one. It walks the whole (tile, group-state)
space with the jump rule built in and proves four things: the crossing
can be made, it cannot be walked, it cannot be jumped without a flower
either, and from every state Chuck can reach the exit is still
reachable -- so no scratch can ever strand him mid-river.
"""

from collections import deque
from itertools import product
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.reactive_flowers import GROUP_TERRAIN
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import FEYWILD, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

MAP_NAME = "feywild_luminous_rapids"
UNDERWAYS = "feywild_mushroom_underways"
GROUP_IDS = ("rapids_lower", "rapids_upper")

RIVER, STONE, PAD_UP, PAD_DOWN, CHANNEL = "ᚼ", "ᚹ", "ᚨ", "ᚧ", "≈"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _tile(position):
    ts = config.TILE_SIZE
    return (int(position[0] // ts), int(position[1] // ts))


def _points(tilemap):
    return {kind.split(":", 1)[1]: _tile(pos)
            for kind, pos in tilemap.object_spawns
            if kind.startswith(("arrival:", "boundary:"))}


def _settle(scene, seconds):
    remaining = seconds
    while remaining > 0.0:
        scene.update(0.05)
        remaining -= 0.05


def test_the_river_stones_and_pads_are_built_from_the_right_pieces() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (78, 44)
    # Fast water and a furled pad are walls; a stone and a risen pad are
    # floor; the channel keeps the jumpable semantics the Fen established.
    assert TILE_DEFS[RIVER].solid and TILE_DEFS[PAD_DOWN].solid
    assert not TILE_DEFS[STONE].solid and not TILE_DEFS[PAD_UP].solid
    assert TILE_DEFS[CHANNEL].solid
    for char, art in ((RIVER, "fey_rapids"), (STONE, "fey_stepping_stone"),
                      (PAD_UP, "fey_pad_open"), (PAD_DOWN, "fey_pad_closed")):
        assert FEYWILD.char_to_terrain[char] == art

    # Both flower groups declare that their change raises and sinks pads
    # rather than paving the river with the default path tile.
    for group_id in GROUP_IDS:
        assert GROUP_TERRAIN[group_id] == (PAD_UP, PAD_DOWN)

    assert sum(row.count(RIVER) for row in tilemap._grid) >= 500


def test_a_flower_raises_one_pad_chain_and_sinks_the_other() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_12")
        scene._arrival_fade_t = None
        group = scene.reactive_flowers.groups["rapids_lower"]
        furled, risen = group.opens[0], group.closes[0]
        assert scene.tilemap.terrain_at(furled.col, furled.row) == PAD_DOWN
        assert scene.tilemap.terrain_at(risen.col, risen.row) == PAD_UP

        assert scene.reactive_flowers.trigger("rapids_lower")
        _settle(scene, config.REACTIVE_FLOWER_CHANGE_DELAY + 0.2)

        # The chain swaps, and it swaps into pad art -- not into a path
        # tile laid across a river.
        assert scene.tilemap.terrain_at(furled.col, furled.row) == PAD_UP
        assert scene.tilemap.terrain_at(risen.col, risen.row) == PAD_DOWN
        assert not scene.tilemap.is_solid(furled.col, furled.row)
        assert scene.tilemap.is_solid(risen.col, risen.row)

        # Scratching again puts the river back exactly as authored.
        assert scene.reactive_flowers.trigger("rapids_lower")
        _settle(scene, config.REACTIVE_FLOWER_CHANGE_DELAY + 0.2)
        assert scene.tilemap.terrain_at(furled.col, furled.row) == PAD_DOWN
        assert scene.tilemap.terrain_at(risen.col, risen.row) == PAD_UP
    finally:
        game._shutdown()


def test_pollen_slows_approaches_and_never_a_landing_or_a_gap() -> None:
    tilemap = _map()
    pollen = [(col, row)
              for row in range(tilemap.height_tiles)
              for col in range(tilemap.width_tiles)
              if tilemap.terrain_at(col, row) == "☼"]
    assert len(pollen) >= 60, len(pollen)
    for col, row in pollen:
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbour = tilemap.terrain_at(col + dc, row + dr)
            assert neighbour != CHANNEL, (col, row)
            assert neighbour not in {STONE, PAD_UP, PAD_DOWN}, (col, row)

    # Moths patrol over the water itself; the one orchid is a late
    # flourish on the optional ledge, never a gate on the route.
    moths = [pos for kind, pos in tilemap.object_spawns
             if kind.startswith("lantern_moth:")]
    assert len(moths) == 3
    for position in moths:
        assert tilemap.terrain_at(*_tile(position)) == RIVER
    orchids = [kind for kind, _pos in tilemap.object_spawns
               if kind.startswith("spitting_orchid:")]
    assert len(orchids) == 1


def test_the_rapids_need_the_flowers_and_never_strand_chuck() -> None:
    tilemap = _map()
    points = _points(tilemap)
    start, goal = points["from_feywild_11"], points["feywild_13"]

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_12")
        scene._arrival_fade_t = None
        groups = {}
        for group_id, group in scene.reactive_flowers.groups.items():
            flower = next(f for f in scene.reactive_flowers.flowers
                          if f.group_id == group_id)
            groups[group_id] = (
                tuple((t.col, t.row) for t in group.opens),
                tuple((t.col, t.row) for t in group.closes),
                _tile((flower.x + 7, flower.y + 6)),
            )
        base_open = {(col, row)
                     for row in range(tilemap.height_tiles)
                     for col in range(tilemap.width_tiles)
                     if not scene.tilemap.is_solid(col, row)}
    finally:
        game._shutdown()

    def walkable(state):
        tiles = set(base_open)
        for group_id in state:
            opens, closes, _switch = groups[group_id]
            tiles |= set(opens)
            tiles -= set(closes)
        return tiles

    open_by_state = {tuple(sorted(combo)): walkable(combo)
                     for size in range(len(GROUP_IDS) + 1)
                     for combo in product(GROUP_IDS, repeat=size)}

    def travel(tile, state, opens):
        """Where one move can go: a step, or one committed hop."""
        col, row = tile
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            step, land = (col + dc, row + dr), (col + 2 * dc, row + 2 * dr)
            if step in opens:
                yield step
            elif (0 <= land[0] < tilemap.width_tiles
                    and 0 <= land[1] < tilemap.height_tiles
                    and tilemap.terrain_at(*step) == CHANNEL
                    and land in opens):
                yield land

    origin = (start, ())
    nodes = {origin}
    backward = {}
    frontier = deque([origin])
    while frontier:
        tile, state = frontier.popleft()
        for destination in travel(tile, state, open_by_state[state]):
            node = (destination, state)
            backward.setdefault(node, []).append((tile, state))
            if node not in nodes:
                nodes.add(node)
                frontier.append(node)
        col, row = tile
        for group_id, (opens, closes, switch) in groups.items():
            if abs(col - switch[0]) + abs(row - switch[1]) > 1:
                continue
            if tile in set(opens) | set(closes):
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
    assert goal in reached, "the rapids cannot be crossed"
    caches = {_tile(pos) for kind, pos in tilemap.object_spawns
              if kind == "breakable_grass"}
    assert caches and caches <= reached

    # Walking gets nowhere; jumping alone gets nowhere either. The lower
    # flower is genuinely the crossing.
    idle = open_by_state[()]
    walked, hopped = {start}, {start}
    for allow_hops, seen in ((False, walked), (True, hopped)):
        frontier = deque([start])
        while frontier:
            tile = frontier.popleft()
            col, row = tile
            for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                step = (col + dc, row + dr)
                land = (col + 2 * dc, row + 2 * dr)
                nxt = None
                if step in idle:
                    nxt = step
                elif (allow_hops
                        and 0 <= land[0] < tilemap.width_tiles
                        and 0 <= land[1] < tilemap.height_tiles
                        and tilemap.terrain_at(*step) == CHANNEL
                        and land in idle):
                    nxt = land
                if nxt is not None and nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
    assert goal not in walked, "the rapids can be walked"
    assert goal not in hopped, "the rapids need no flower"

    # And no order of scratches strands him out on the water.
    goals = {node for node in nodes if node[0] == goal}
    can_finish = set(goals)
    frontier = deque(goals)
    while frontier:
        node = frontier.popleft()
        for source in backward.get(node, ()):
            if source not in can_finish:
                can_finish.add(source)
                frontier.append(source)
    assert nodes == can_finish, sorted(nodes - can_finish)[:6]


def test_rapids_checkpoints_music_and_the_underways_connection() -> None:
    entry = CHECKPOINT_BY_ID["feywild_12"]
    assert entry.display_name == "Feywild 12" and entry.runtime_entry
    assert entry.map_name == MAP_NAME and entry.arrival == "from_feywild_11"
    assert tileset_for(MAP_NAME).sheet == "feywild.png"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"
    assert AREA_WALK_EXITS[(UNDERWAYS, "→")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "←")].destination == UNDERWAYS

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_11")
        scene._arrival_fade_t = None
        onward = next((c, r) for r in range(scene.tilemap.height_tiles)
                      for c in range(scene.tilemap.width_tiles)
                      if scene.tilemap.terrain_at(c, r) == "→")
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_12"
        scene.update(0.0)
        assert scene.map_name == MAP_NAME  # no bounce

        back = next((c, r) for r in range(scene.tilemap.height_tiles)
                    for c in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(c, r) == "←")
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == UNDERWAYS
        assert game.active_checkpoint_id == "feywild_11_return"
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
    print("All Luminous Rapids tests passed.")


if __name__ == "__main__":
    _run_all()
