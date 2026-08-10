"""Phase 11 City Night 6 and its bounded modern-sewer threshold."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.pedestrian import PedestrianNPC
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_night_6"
# The manhole used to be counted as masonry because it was cut into a
# building. It is a hole in the sidewalk now, so it is not an office.
# The roof volume: field, parapets on three edges, and the vents and
# skylights standing on it. All of it is one solid office mass.
OFFICE = frozenset("#▘▖▗▙▟▱▤▥w")


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


def _game_and_world(checkpoint="modern_city_6"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_city_night_6_is_a_full_scale_final_night_block() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert (tilemap.width_tiles, tilemap.height_tiles) == (88, 60)
    assert MAP_TILESET[MAP_NAME] == "city"
    assert kinds["arrival:from_city_night_5"] == 1
    assert kinds["anchor:modern_city_6_anchor"] == 1
    assert kinds["boundary:modern_city_night_5"] == 1
    assert kinds["choice:city_sewer_entrance"] == 1
    assert kinds["arrival:from_city_sewer_1"] == 1
    assert kinds["npc:businessman"] == 2
    assert kinds["patrol_npc:businessman:v"] == 1
    assert kinds["npc:homeless_man"] == 0
    assert kinds["raccoon"] == 1
    assert kinds["cigarette"] == 4
    assert kinds["traffic_lane:down:0"] == 1
    assert kinds["traffic_lane:up:1"] == 1
    assert Counter(kind for kind, _col, _row in tilemap.prop_tiles) == {
        "city_sewer_entrance": 1
    }

    components = _office_components(tilemap)
    assert len(components) == 4
    for component in components:
        cols = [point[0] for point in component]
        rows = [point[1] for point in component]
        assert max(cols) - min(cols) + 1 >= 32
        assert max(rows) - min(rows) + 1 >= 20


def test_route_turns_from_east_entry_to_the_sewer_threshold() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    reached = _reachable(tilemap, markers["arrival:from_city_night_5"][0])
    required = {
        markers["anchor:modern_city_6_anchor"][0],
        markers["boundary:modern_city_night_5"][0],
        markers["choice:city_sewer_entrance"][0],
        markers["arrival:from_city_sewer_1"][0],
        *markers["npc:businessman"],
        *markers["patrol_npc:businessman:v"],
        *markers["raccoon"],
        *markers["cigarette"],
    }
    assert required <= reached
    assert markers["choice:city_sewer_entrance"] == [(20, 24)]
    assert markers["arrival:from_city_night_5"] == [(83, 24)]
    assert markers["arrival:from_city_sewer_1"] == [(20, 26)]
    exits = [exit_def for (source, _), exit_def in AREA_WALK_EXITS.items()
             if source == MAP_NAME]
    assert len(exits) == 1
    assert (exits[0].destination, exits[0].arrival) == (
        "modern_city_night_5", "from_city_night_6"
    )


def test_city_5_and_6_openings_align_with_named_arrivals() -> None:
    map_5 = TileMap(config.MAPS_DIR / "modern_city_night_5.txt")
    map_6 = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers_5 = _markers(map_5)
    markers_6 = _markers(map_6)
    assert markers_5["boundary:modern_city_night_6"] == [(0, 24)]
    assert markers_5["arrival:from_city_night_6"] == [(4, 24)]
    assert markers_6["boundary:modern_city_night_5"] == [(87, 24)]
    assert markers_6["arrival:from_city_night_5"] == [(83, 24)]


def test_the_sewer_entrance_is_an_open_manhole_in_the_pavement() -> None:
    """A hole in the street with its cover beside it, not a portal.

    The first attempt was a human-sized concrete opening cut into the
    building behind, which read as the mouth of a subway. A sewer is
    reached through the street, so the geometry is checked here: the
    hole is over the solid tile, the cover is off to one side of it,
    and the tile underneath is sidewalk rather than masonry.
    """
    image = pygame.image.load(str(
        config.SPRITES_DIR / "objects" / "city_sewer_entrance.png"
    ))
    width, height = image.get_size()
    # Props draw centred on their tile, so the hole -- not the sprite --
    # has to sit over the middle of the tile that is actually solid.
    assert image.get_at((width // 2, height - 12))[:3] == (6, 7, 9)
    # ...and the cover is beside it rather than behind it, so it never
    # reads as a second, closed hole.
    cover = [x for x in range(width)
             if image.get_at((x, 22))[:3][0] > image.get_at((x, 22))[:3][2]
             and image.get_at((x, 22))[3] > 0]
    assert cover and min(cover) > width // 2, (min(cover) if cover else None)

    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert tilemap.is_solid(20, 22), "the open hole is not walked over"
    assert TILE_DEFS["ƺ"].under == ".", "the manhole is in the sidewalk"
    assert TILE_DEFS["ƺ"].prop == "city_sewer_entrance"

    directory, game, world = _game_and_world()
    try:
        assert len(world.choice_triggers) == 1
        trigger = world.choice_triggers[0]
        assert trigger.choice_id == "city_sewer_entrance"
        assert trigger.walk_triggered
        world._arrival_fade_t = None
        world.player.x = trigger.x + trigger.width / 2 - world.player.width / 2
        world.player.y = trigger.y + trigger.height / 2 - world.player.height / 2
        world.update(0.0)
        prompt = game.scenes.current
        assert isinstance(prompt, DialogueScene)
        assert prompt._choice.prompt == "Enter the sewer?"
        assert [option.label for option in prompt._choice.options] == [
            "YES", "NO"
        ]
    finally:
        game._shutdown()
        directory.cleanup()


def test_checkpoint_world_and_death_reset_use_shared_systems() -> None:
    entry = CHECKPOINT_BY_ID["modern_city_6"]
    anchor = CHECKPOINT_BY_ID["modern_city_6_anchor"]
    assert (entry.display_name, entry.map_name, entry.arrival) == (
        "City Night 6", MAP_NAME, "from_city_night_5"
    )
    assert anchor.position == (1284.0, 389.0)
    assert anchor.saveable

    directory, game, world = _game_and_world("modern_city_6_anchor")
    try:
        assert world.city_rain is not None
        assert len(world.npcs) == 3
        assert sum(isinstance(npc, PedestrianNPC)
                   for npc in world.npcs) == 1
        assert len(world.raccoons) == 1
        assert len(world.traffic_lanes) == 2
        initial_centers = [
            [vehicle.center for vehicle in lane.vehicles]
            for lane in world.traffic_lanes
        ]
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        world._arrival_fade_t = None
        world.traffic_lanes[0].update(0.25)
        world.raccoons[0].on_scratched()
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
        assert [
            [vehicle.center for vehicle in lane.vehicles]
            for lane in world.traffic_lanes
        ] == initial_centers
        assert world.raccoons[0].scratches_remaining == (
            config.RACCOON_SCRATCHES
        )
    finally:
        game._shutdown()
        directory.cleanup()
