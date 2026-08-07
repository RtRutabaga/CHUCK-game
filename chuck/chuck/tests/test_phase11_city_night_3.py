"""Phase 11 City Night 3 and its restrained sidewalk encounter."""

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
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.dialogue import DialogueSystem
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_night_3"
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


def _game_and_world(checkpoint="modern_city_3"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_city_night_3_has_large_blocks_and_one_homeless_scene() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert (tilemap.width_tiles, tilemap.height_tiles) == (80, 56)
    assert MAP_TILESET[MAP_NAME] == "city"
    assert kinds["arrival:from_city_night_2"] == 1
    assert kinds["anchor:modern_city_3_anchor"] == 1
    assert kinds["boundary:modern_city_night_2"] == 1
    assert kinds["npc:homeless_man"] == 1
    assert kinds["npc:businessman"] == 1
    assert kinds["patrol_npc:businessman:v"] == 1
    assert kinds["raccoon"] == 2
    assert kinds["cigarette"] == 4
    assert kinds["traffic_lane:down:0"] == 1
    assert kinds["traffic_lane:up:1"] == 1
    assert Counter(kind for kind, _col, _row in tilemap.prop_tiles) == {
        "city_bottles": 2
    }
    assert not any(kind == "boundary:modern_city_night_4" for kind in kinds)

    components = _office_components(tilemap)
    assert len(components) == 4
    for component in components:
        cols = [point[0] for point in component]
        rows = [point[1] for point in component]
        assert max(cols) - min(cols) + 1 >= 29
        assert max(rows) - min(rows) + 1 >= 19


def test_every_map_3_discovery_is_reachable_without_astral_fall() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    reached = _reachable(tilemap, markers["arrival:from_city_night_2"][0])
    required = {
        markers["anchor:modern_city_3_anchor"][0],
        markers["boundary:modern_city_night_2"][0],
        *markers["npc:homeless_man"],
        *markers["npc:businessman"],
        *markers["patrol_npc:businessman:v"],
        *markers["raccoon"],
        *markers["cigarette"],
    }
    assert required <= reached
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].destination == (
        "modern_city_night_2"
    )
    assert not any(
        source == MAP_NAME and terrain != "⮜"
        for source, terrain in AREA_WALK_EXITS
    )


def test_map_2_and_3_visual_openings_match_their_named_arrivals() -> None:
    map_2 = TileMap(config.MAPS_DIR / "modern_city_night_2.txt")
    map_3 = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers_2 = _markers(map_2)
    markers_3 = _markers(map_3)
    assert markers_2["boundary:modern_city_night_3"] == [(75, 35)]
    assert markers_2["arrival:from_city_night_3"] == [(71, 35)]
    assert markers_3["boundary:modern_city_night_2"] == [(0, 33)]
    assert markers_3["arrival:from_city_night_2"] == [(4, 33)]
    assert AREA_WALK_EXITS[("modern_city_night_2", "⮞")].arrival == (
        "from_city_night_2"
    )
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].arrival == "from_city_night_3"


def test_checkpoint_dialogue_and_scene_entities_are_shared_systems() -> None:
    entry = CHECKPOINT_BY_ID["modern_city_3"]
    anchor = CHECKPOINT_BY_ID["modern_city_3_anchor"]
    assert (entry.display_name, entry.map_name, entry.arrival) == (
        "City Night 3", MAP_NAME, "from_city_night_2"
    )
    assert anchor.position == (116.0, 533.0)
    assert anchor.saveable
    dialogue = DialogueSystem()
    assert dialogue.get("homeless_man") == ["Hey there buddy!"]
    assert dialogue.get("businessman") == ["Ah! A rat!"]

    directory, game, world = _game_and_world()
    try:
        assert world.city_rain is not None
        assert len(world.npcs) == 3
        homeless = [npc for npc in world.npcs
                    if npc.npc_id == "homeless_man"]
        assert len(homeless) == 1
        assert not isinstance(homeless[0], PedestrianNPC)
        assert sum(isinstance(npc, PedestrianNPC)
                   for npc in world.npcs) == 1
        assert len(world.raccoons) == 2
        assert {lane.direction for lane in world.traffic_lanes} == {"up", "down"}
        assert [prop.kind for prop in world.props].count("city_bottles") == 2
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)
    finally:
        game._shutdown()
        directory.cleanup()


def test_homeless_and_bottle_sprites_keep_human_scale() -> None:
    homeless = pygame.image.load(
        str(config.SPRITES_DIR / "npcs" / "homeless_man.png")
    )
    assert homeless.get_size() == (config.NPC_FRAME_W * 3, config.NPC_FRAME_H)
    for index in (1, 2):
        bottles = pygame.image.load(str(
            config.SPRITES_DIR / "objects" / f"city_bottles_{index}.png"
        ))
        assert bottles.get_size() == (16, 16)
        assert sum(
            bottles.get_at((x, y)).a > 0
            for y in range(16) for x in range(16)
        ) >= 45


def test_city_night_3_sanity_return_uses_its_anchor_and_resets_raccoons() -> None:
    directory, game, world = _game_and_world("modern_city_3_anchor")
    try:
        world._arrival_fade_t = None
        world.raccoons[0].on_scratched()
        assert world.raccoons[0].scratches_remaining == (
            config.RACCOON_SCRATCHES - 1
        )
        world.sanity.deplete()
        assert world._respawn_phase == "out"
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert world._respawn_phase == "in"
        assert world.sanity.current == config.SANITY_MAX
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
        assert len(world.raccoons) == 2
        assert all(
            enemy.scratches_remaining == config.RACCOON_SCRATCHES
            for enemy in world.raccoons
        )
    finally:
        game._shutdown()
        directory.cleanup()
