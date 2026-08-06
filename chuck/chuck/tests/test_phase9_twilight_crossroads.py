"""Phase 9 Map 13 -- the Twilight Crossroads culmination."""

from collections import Counter, deque
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world import collision
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "feywild_twilight_crossroads"
RAPIDS = "feywild_luminous_rapids"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _tile(position):
    size = config.TILE_SIZE
    return (int(position[0] // size), int(position[1] // size))


def _points(tilemap):
    return {
        kind: _tile(position)
        for kind, position in tilemap.object_spawns
        if kind.startswith(("arrival:", "anchor:", "boundary:"))
    }


def _reachable(tilemap, start, *, large_actor=False):
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            terrain = tilemap.terrain_at(*point)
            if point in reached or tilemap.is_solid(*point):
                continue
            if large_actor and terrain in collision.LARGE_ACTOR_PASSAGE_TERRAIN:
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def _settle(scene, seconds):
    while seconds > 0.0:
        scene.update(0.05)
        seconds -= 0.05


def test_crossroads_is_a_broad_twilight_culmination_not_a_boss_map() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (76, 52)
    assert MAP_TILESET[MAP_NAME] == "feywild"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"

    kinds = Counter(kind for kind, _position in tilemap.object_spawns)
    assert kinds["arrival:from_feywild_12"] == 1
    assert kinds["anchor:feywild_13_anchor"] == 1
    assert kinds["boundary:feywild_tower"] == 1
    assert kinds["thorn_mite"] == 5
    assert kinds["redcap"] == 1
    assert kinds["breakable_grass"] == 3
    assert not any(
        kind in kinds for kind in (
            "displacer_beast", "massive_dinosaur", "pit_fiend",
            "horned_devil", "zombie", "skeleton",
        )
    )
    assert sum(row.count("☼") for row in tilemap._grid) >= 50


def test_geography_is_wrong_but_both_connected_edges_are_readable() -> None:
    forward = AREA_WALK_EXITS[(RAPIDS, "→")]
    backward = AREA_WALK_EXITS[(MAP_NAME, "⇩")]
    assert forward.destination == MAP_NAME
    assert forward.arrival == "from_feywild_12" and forward.facing == "up"
    assert backward.destination == RAPIDS
    assert backward.arrival == "from_feywild_13"

    tilemap = _map()
    # The eastward Rapids connection arriving at a south edge is the spatial
    # impossibility; each local opening still uses the three-cell wilderness
    # language established in Chult.
    south = [tilemap.terrain_at(col, tilemap.height_tiles - 1)
             for col in range(tilemap.width_tiles)]
    west = [tilemap.terrain_at(0, row)
            for row in range(tilemap.height_tiles)]
    assert south.count("⇩") == 3
    assert west.count("←") == 3


def test_one_reciprocal_flower_opens_the_final_route_without_a_softlock() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_13")
        scene._arrival_fade_t = None
        points = _points(scene.tilemap)
        arrival = points["arrival:from_feywild_12"]
        tower = points["boundary:feywild_tower"]
        assert tower not in _reachable(scene.tilemap, arrival)

        group = scene.reactive_flowers.groups["twilight"]
        assert len(group.opens) == 3 and len(group.closes) == 3
        assert scene.reactive_flowers.trigger("twilight")
        _settle(scene, config.REACTIVE_FLOWER_CHANGE_DELAY + 0.2)
        reached = _reachable(scene.tilemap, arrival)
        assert tower in reached

        # The switch itself remains reachable from both sides of the opened
        # gate, and a second scratch restores the authored state exactly.
        flower = scene.reactive_flowers.flowers[0]
        assert _tile((flower.x + 7, flower.y + 6)) in reached
        assert scene.reactive_flowers.trigger("twilight")
        _settle(scene, config.REACTIVE_FLOWER_CHANGE_DELAY + 0.2)
        assert tower not in _reachable(scene.tilemap, arrival)
    finally:
        game._shutdown()


def test_root_pocket_is_a_chuck_only_optional_refuge() -> None:
    tilemap = _map()
    points = _points(tilemap)
    start = points["arrival:from_feywild_12"]
    chuck = _reachable(tilemap, start)
    large = _reachable(tilemap, start, large_actor=True)
    passages = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "≀"
    }
    caches = {
        _tile(position) for kind, position in tilemap.object_spawns
        if kind == "breakable_grass"
    }
    assert len(passages) == 2
    assert passages <= chuck and not (passages & large)
    assert caches <= chuck
    assert caches - large, "large enemies can reach every optional cache"


def test_arrival_anchor_and_main_route_do_not_force_the_redcap() -> None:
    tilemap = _map()
    points = _points(tilemap)
    start = points["arrival:from_feywild_12"]
    anchor = points["anchor:feywild_13_anchor"]
    redcap = next(_tile(position) for kind, position in tilemap.object_spawns
                  if kind == "redcap")
    assert anchor in _reachable(tilemap, start)
    distance = math.dist(start, redcap) * config.TILE_SIZE
    assert distance > config.REDCAP_NOTICE_RANGE * 2

    # The tower remains an inert promise: it has no walk-exit configured, and
    # Phase 9 therefore cannot silently begin the later tower phase.
    assert (MAP_NAME, "←") not in AREA_WALK_EXITS


def test_shared_checkpoint_save_continue_respawn_and_round_trip() -> None:
    entry = CHECKPOINT_BY_ID["feywild_13"]
    anchor_cp = CHECKPOINT_BY_ID["feywild_13_anchor"]
    assert entry.display_name == "Feywild 13" and entry.runtime_entry
    assert anchor_cp.saveable and not anchor_cp.development_visible

    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            scene = game.checkpoints.load_checkpoint("feywild_12")
            scene._arrival_fade_t = None
            east = next((col, row)
                        for row in range(scene.tilemap.height_tiles)
                        for col in range(scene.tilemap.width_tiles)
                        if scene.tilemap.terrain_at(col, row) == "→")
            scene.player.x = east[0] * config.TILE_SIZE + 3
            scene.player.y = east[1] * config.TILE_SIZE + 4
            scene.update(0.0)
            assert scene.map_name == MAP_NAME
            assert game.active_checkpoint_id == "feywild_13"

            anchor = scene.anchors[0]
            scene.player.x, scene.player.y = anchor.x, anchor.y
            scene.update(0.0)
            assert anchor.lit
            assert game.active_checkpoint_id == "feywild_13_anchor"

            scene.rats.clear()
            scene.sanity.deplete()
            scene.update(config.RESPAWN_FADE_OUT)
            scene.update(config.RESPAWN_HOLD)
            scene.update(config.RESPAWN_FADE_IN)
            assert len(scene.rats) == 5
            assert all(rat.variant == "thorn_mite" for rat in scene.rats)
            assert all(rat.attack_chase_enabled for rat in scene.rats)
            assert (scene.player.x, scene.player.y) == (anchor.x, anchor.y)

            south = next((col, row)
                         for row in range(scene.tilemap.height_tiles)
                         for col in range(scene.tilemap.width_tiles)
                         if scene.tilemap.terrain_at(col, row) == "⇩")
            scene.player.x = south[0] * config.TILE_SIZE + 3
            scene.player.y = south[1] * config.TILE_SIZE + 4
            scene.update(0.0)
            assert scene.map_name == RAPIDS
            assert game.active_checkpoint_id == "feywild_12_return"

            # Continue still restores the persisted physical Ashtray, not the
            # unsaved map edge visited afterward.
            resumed = game.checkpoints.continue_game()
            assert resumed is not None and resumed.map_name == MAP_NAME
            assert resumed.anchors[0].lit
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
    print("All Twilight Crossroads tests passed.")


if __name__ == "__main__":
    _run_all()
