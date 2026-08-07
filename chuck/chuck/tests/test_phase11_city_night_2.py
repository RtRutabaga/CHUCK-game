"""Phase 11 City Night 2 map, people, and raccoon encounter."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.pedestrian import PedestrianNPC
from src.entities.raccoon import Raccoon
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.dialogue import DialogueSystem
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_night_2"
OFFICE = frozenset("#▱▤▥w")


def _markers(tilemap):
    result = {}
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)
        ))
    return result


def _reachable(tilemap, start):
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in found or tilemap.is_solid(*point):
                continue
            if tilemap.terrain_at(*point) == "V":
                continue
            found.add(point)
            queue.append(point)
    return found


def _office_components(tilemap):
    remaining = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) in OFFICE
    }
    components = []
    while remaining:
        component = {remaining.pop()}
        queue = list(component)
        while queue:
            col, row = queue.pop()
            for point in ((col - 1, row), (col + 1, row),
                          (col, row - 1), (col, row + 1)):
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    queue.append(point)
        components.append(component)
    return components


def _game_and_world(checkpoint="modern_city_2"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_city_night_2_is_a_large_city_grid_with_authored_content() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert (tilemap.width_tiles, tilemap.height_tiles) == (76, 56)
    assert MAP_TILESET[MAP_NAME] == "city"
    assert kinds["arrival:from_city_night_1"] == 1
    assert kinds["anchor:modern_city_2_anchor"] == 1
    assert kinds["boundary:modern_city_night_1"] == 1
    assert kinds["boundary:modern_city_night_3"] == 1
    assert kinds["arrival:from_city_night_3"] == 1
    assert kinds["npc:businessman"] == 2
    assert kinds["patrol_npc:businessman:h"] == 1
    assert kinds["raccoon"] == 1
    assert kinds["cigarette"] == 4
    assert kinds["traffic_lane:right:0"] == 1
    assert kinds["traffic_lane:left:1"] == 1

    components = _office_components(tilemap)
    assert len(components) == 4
    for component in components:
        cols = [point[0] for point in component]
        rows = [point[1] for point in component]
        assert max(cols) - min(cols) + 1 >= 28
        assert max(rows) - min(rows) + 1 >= 18


def test_city_night_2_content_and_return_are_reachable_without_falling() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    reached = _reachable(tilemap, markers["arrival:from_city_night_1"][0])
    required = {
        markers["anchor:modern_city_2_anchor"][0],
        markers["boundary:modern_city_night_1"][0],
        markers["boundary:modern_city_night_3"][0],
        *markers["npc:businessman"],
        *markers["patrol_npc:businessman:h"],
        *markers["raccoon"],
        *markers["cigarette"],
    }
    assert required <= reached

    outward = AREA_WALK_EXITS[("modern_city_arrival", "⮝")]
    backward = AREA_WALK_EXITS[(MAP_NAME, "⮟")]
    assert outward.destination == MAP_NAME
    assert outward.arrival == "from_city_night_1"
    assert backward.destination == "modern_city_arrival"
    assert backward.arrival == "from_city_night_2"
    onward = AREA_WALK_EXITS[(MAP_NAME, "⮞")]
    assert onward.destination == "modern_city_night_3"
    assert onward.arrival == "from_city_night_2"


def test_city_night_2_checkpoint_and_dialogue_are_registered() -> None:
    entry = CHECKPOINT_BY_ID["modern_city_2"]
    anchor = CHECKPOINT_BY_ID["modern_city_2_anchor"]
    assert (entry.display_name, entry.map_name, entry.arrival) == (
        "City Night 2", MAP_NAME, "from_city_night_1"
    )
    assert anchor.position == (484.0, 757.0)
    assert anchor.saveable
    assert DialogueSystem().get("businessman") == ["Ah! A rat!"]


def test_world_builds_rain_people_raccoon_and_traffic() -> None:
    directory, game, world = _game_and_world()
    try:
        assert world.city_rain is not None
        assert len(world.npcs) == 3
        assert sum(isinstance(npc, PedestrianNPC) for npc in world.npcs) == 1
        assert len(world.raccoons) == 1
        assert len(world.traffic_lanes) == 2

        walker = next(npc for npc in world.npcs
                      if isinstance(npc, PedestrianNPC))
        start = walker.x
        walker.update(0.5)
        assert walker.x > start

        raccoon = world.raccoons[0]
        assert config.RAT_SANITY_DAMAGE < raccoon.damage < config.ZOMBIE_SANITY_DAMAGE
        assert 1 < raccoon.max_scratches < config.ZOMBIE_SCRATCHES
        world.player.x = raccoon.x - 40
        world.player.y = raccoon.y
        start = raccoon.x
        raccoon.update(0.5, world.player)
        assert raccoon.x < start
    finally:
        game._shutdown()
        directory.cleanup()


def test_raccoon_defeat_and_death_reset_use_normal_enemy_lifecycle() -> None:
    directory, game, world = _game_and_world("modern_city_2_anchor")
    try:
        raccoon = world.raccoons[0]
        for _ in range(config.RACCOON_SCRATCHES):
            raccoon.on_scratched()
        assert not raccoon.alive
        world.raccoons = [enemy for enemy in world.raccoons if enemy.alive]
        assert not world.raccoons
        world._reset_enemies()
        assert len(world.raccoons) == 1
        assert world.raccoons[0].scratches_remaining == config.RACCOON_SCRATCHES
    finally:
        game._shutdown()
        directory.cleanup()
