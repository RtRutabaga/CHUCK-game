"""Phase 9 Rootways, redcap pursuit, and Chuck-scale passage regression."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.redcap import Redcap
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world import collision
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "feywild_rootways"


def _markers(tilemap: TileMap) -> dict[str, tuple[int, int]]:
    size = config.TILE_SIZE
    return {
        kind: (int(x // size), int(y // size))
        for kind, (x, y) in tilemap.object_spawns
    }


def _reachable(
    tilemap: TileMap,
    start: tuple[int, int],
    *,
    large_actor: bool = False,
) -> set[tuple[int, int]]:
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            terrain = tilemap.terrain_at(*point)
            if point in reached or tilemap.is_solid(*point):
                continue
            if large_actor and terrain in collision.LARGE_ACTOR_PASSAGE_TERRAIN:
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_rootways_is_a_large_two_redcap_pursuit_map() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (68, 46)
    assert MAP_TILESET[MAP_NAME] == "feywild"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"

    kinds = Counter(kind for kind, _position in tilemap.object_spawns)
    assert kinds["arrival:from_feywild_3"] == 1
    assert kinds["redcap"] == 2
    assert kinds["boundary:feywild_5"] == 1
    assert kinds["arrival:from_feywild_5"] == 1
    assert kinds["breakable_grass"] == 1
    assert sum(
        tilemap.terrain_at(col, row) == "≀"
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
    ) == 2


def test_root_passages_protect_a_refuge_and_optional_cache() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    arrival = markers["arrival:from_feywild_3"]
    cache = markers["breakable_grass"]
    chuck_reach = _reachable(tilemap, arrival)
    large_reach = _reachable(tilemap, arrival, large_actor=True)

    assert cache in chuck_reach
    assert cache not in large_reach
    assert (30, 35) in chuck_reach
    assert (30, 35) not in large_reach
    assert markers["boundary:feywild_5"] in chuck_reach


def test_redcap_is_durable_and_visibly_stops_at_a_root_gap() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    redcap = Redcap(26 * config.TILE_SIZE + 8, 35 * config.TILE_SIZE + 8)
    redcap.tilemap = tilemap

    class Target:
        x = 30 * config.TILE_SIZE + 3
        y = 35 * config.TILE_SIZE + 4
        width = config.PLAYER_HITBOX_W
        height = config.PLAYER_HITBOX_H

    for _ in range(80):
        redcap.update(0.05, Target())
    passage_left = 27 * config.TILE_SIZE
    assert redcap.x + redcap.width <= passage_left
    assert redcap.alive

    for _ in range(config.REDCAP_SCRATCHES - 1):
        redcap.on_scratched()
        assert redcap.alive
    redcap.on_scratched()
    assert not redcap.alive


def test_orchard_and_rootways_transition_both_ways() -> None:
    forward = AREA_WALK_EXITS[("feywild_pollen_orchard", "⇧")]
    backward = AREA_WALK_EXITS[(MAP_NAME, "←")]
    onward = AREA_WALK_EXITS[(MAP_NAME, "→")]
    assert forward.destination == MAP_NAME
    assert forward.arrival == "from_feywild_3"
    assert backward.destination == "feywild_pollen_orchard"
    assert backward.arrival == "from_feywild_4"
    assert onward.destination == "feywild_needle_garden"
    assert onward.arrival == "from_feywild_5"

    entry = CHECKPOINT_BY_ID["feywild_4"]
    assert entry.display_name == "Feywild 4" and entry.runtime_entry


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
    print("All Phase 9 Rootways tests passed.")


if __name__ == "__main__":
    _run_all()
