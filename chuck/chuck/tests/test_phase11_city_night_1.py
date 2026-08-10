"""Phase 11's first explorable rainy-city map."""

from collections import Counter, deque

from src.core import config
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_arrival"
# The roof volume: field, parapets on three edges, and the vents and
# skylights standing on it. All of it is one solid office mass.
OFFICE_TERRAIN = frozenset("#▘▖▗▙▟▱▤▥w")
NIGHT_MAPS = (
    "modern_city_arrival", "modern_city_night_2", "modern_city_night_3",
    "modern_city_night_4", "modern_city_night_5", "modern_city_night_6",
)


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


def _office_components(tilemap: TileMap) -> list[set[tuple[int, int]]]:
    remaining = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) in OFFICE_TERRAIN
    }
    components = []
    while remaining:
        component = {remaining.pop()}
        frontier = list(component)
        while frontier:
            col, row = frontier.pop()
            for point in (
                (col - 1, row), (col + 1, row),
                (col, row - 1), (col, row + 1),
            ):
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    frontier.append(point)
        components.append(component)
    return components


def test_city_night_1_establishes_the_region_and_opens_city_night_2() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _position in tilemap.object_spawns)

    assert (tilemap.width_tiles, tilemap.height_tiles) == (72, 54)
    assert MAP_TILESET[MAP_NAME] == "city"
    assert kinds["arrival:from_flight"] == 1
    assert kinds["anchor:modern_city_anchor"] == 1
    assert kinds["cigarette"] == 4
    assert kinds["boundary:modern_city_night_2"] == 1
    assert kinds["arrival:from_city_night_2"] == 1
    exit_config = AREA_WALK_EXITS[(MAP_NAME, "⮝")]
    assert exit_config.destination == "modern_city_night_2"
    assert exit_config.arrival == "from_city_night_1"
    assert not any(
        kind.startswith(("npc:", "rat", "raccoon"))
        for kind in kinds
    )

    terrain = "".join(tilemap._grid)
    assert terrain.count("V") >= 240
    assert terrain.count("=") >= 650
    assert terrain.count("w") >= 250
    assert not tilemap.is_solid(27, 47)
    assert not tilemap.is_solid(27, 43)


def test_offices_are_four_large_inaccessible_city_blocks() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    components = _office_components(tilemap)
    assert len(components) == 4
    assert sum(map(len, components)) >= 1500
    for component in components:
        cols = [point[0] for point in component]
        rows = [point[1] for point in component]
        assert max(cols) - min(cols) + 1 >= 21
        assert max(rows) - min(rows) + 1 >= 18
        assert all(tilemap.is_solid(*point) for point in component)


def test_every_city_night_1_discovery_is_reachable_without_astral_fall() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_flight"][0]
    required = {
        markers["anchor:modern_city_anchor"][0],
        markers["boundary:modern_city_night_2"][0],
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
    assert anchor.position == (436.0, 693.0)
    assert anchor.saveable


def test_city_tileset_uses_the_shared_animated_astral_hazard() -> None:
    tileset = tileset_for(MAP_NAME)
    assert tileset.char_to_terrain["V"] == "astral_void"
    assert tileset.info()["astral_void"] == (2, 3)
    assert tileset.char_to_terrain["#"] == "city_roof"
    assert tileset.char_to_terrain["▱"] == "city_cornice"
    assert tileset.char_to_terrain["▤"] == "city_facade"
    assert tileset.char_to_terrain["▥"] == "city_side_facade"
    assert tileset.info()["city_window"] == (4, 3)
    assert tileset.char_to_terrain["▦"] == "city_crosswalk"


def test_night_blocks_are_terraces_of_buildings_not_slabs_of_stone() -> None:
    """A block has to read as several buildings seen from above.

    It used to be painted as one mass: an unbroken field of roof with a
    strip of windows along the bottom. That is a slab of plain stone
    across half the screen, because a roof with no edge and nothing
    standing on it is only a colour. What is checked here is the shape
    that fixes it -- a parapet around every roof, plant on top of it, a
    stepped roofline, and side walls turning away from the camera.
    """
    for name in NIGHT_MAPS:
        tilemap = TileMap(config.MAPS_DIR / f"{name}.txt")
        grid = tilemap._grid
        used = Counter(char for row in grid for char in row)

        # Every roof is walled: back parapet, and one down each side.
        for char in "▘▖▗":
            assert used[char] > 0, (name, char)
        # ...and has plant standing on it, not just texture.
        assert used["▙"] + used["▟"] >= 12, (name, used)

        # The roofline steps: cornices sit at more than one height in a
        # block, which is what makes a terrace rather than one building.
        cornice_rows = {row for row, line in enumerate(grid)
                        if "▱" in line}
        assert len(cornice_rows) >= 4, (name, sorted(cornice_rows))

        # Side walls turn away from the camera on every block, and there
        # are now more of them than there were flat masses.
        assert used["▥"] >= 40, (name, used["▥"])

        # No unbroken field of bare roof is left anywhere: the widest
        # run of plain roof tiles in a row is bounded by the buildings
        # the block is divided into.
        widest = 0
        for line in grid:
            run = 0
            for char in line:
                run = run + 1 if char == "#" else 0
                widest = max(widest, run)
        assert widest <= 24, (name, widest)
