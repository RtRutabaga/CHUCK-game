"""Phase 11's first explorable rainy-city map."""

from collections import Counter, deque

from src.core import config
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_arrival"


def _markers(tilemap: TileMap) -> dict[str, list[tuple[int, int]]]:
    points: dict[str, list[tuple[int, int]]] = {}
    for kind, (x, y) in tilemap.object_spawns:
        points.setdefault(kind, []).append((
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)
        ))
    return points


def _reachable_without_falling(
    tilemap: TileMap, start: tuple[int, int]
) -> set[tuple[int, int]]:
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in (
            (col - 1, row), (col + 1, row),
            (col, row - 1), (col, row + 1),
        ):
            pcol, prow = point
            if point in reached or tilemap.is_solid(pcol, prow):
                continue
            if tilemap.terrain_at(pcol, prow) == "V":
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_city_night_1_establishes_the_region_without_future_encounters() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _position in tilemap.object_spawns)

    assert (tilemap.width_tiles, tilemap.height_tiles) == (56, 36)
    assert MAP_TILESET[MAP_NAME] == "city"
    assert kinds["arrival:from_flight"] == 1
    assert kinds["anchor:modern_city_anchor"] == 1
    assert kinds["cigarette"] == 4
    assert not any(kind.startswith("boundary:") for kind in kinds)
    assert not any(key[0] == MAP_NAME for key in AREA_WALK_EXITS)
    assert not any(
        kind.startswith(("npc:", "rat", "raccoon", "traffic:"))
        for kind in kinds
    )

    terrain = "".join(tilemap._grid)
    assert terrain.count("V") >= 150
    assert terrain.count("=") >= 400
    assert terrain.count("w") >= 25
    assert not tilemap.is_solid(21, 31)
    assert not tilemap.is_solid(21, 28)


def test_every_city_night_1_discovery_is_reachable_without_astral_fall() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_flight"][0]
    required = {
        markers["anchor:modern_city_anchor"][0],
        *markers["cigarette"],
    }
    assert required <= _reachable_without_falling(tilemap, start)


def test_city_checkpoint_registry_preserves_phase10_save_compatibility() -> None:
    entry = CHECKPOINT_BY_ID["modern_city_1"]
    anchor = CHECKPOINT_BY_ID["modern_city_anchor"]
    assert entry.display_name == "City Night 1"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_flight"
    assert anchor.display_name == "City Night 1 Ashtray"
    assert anchor.map_name == MAP_NAME
    assert anchor.position == (340.0, 453.0)
    assert anchor.saveable


def test_city_tileset_uses_the_shared_animated_astral_hazard() -> None:
    tileset = tileset_for(MAP_NAME)
    assert tileset.char_to_terrain["V"] == "astral_void"
    assert tileset.info()["astral_void"] == (2, 3)
