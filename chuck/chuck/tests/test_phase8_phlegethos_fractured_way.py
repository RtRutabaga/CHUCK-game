"""The collided bus-stop route inserted before the Pit Fiend battle."""

from collections import Counter, deque
import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "phlegethos_fractured_way"
RUBBLE = "phlegethos_rubble_pass"
FORTRESS = "phlegethos_fortress_approach"
ASTRAL = "V"
LAVA = "≋"


def _markers(tilemap):
    result = {}
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE),
        ))
    return result


def _reachable(tilemap, start, *, astral_hops=False):
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            step = (col + dc, row + dr)
            if not (0 <= step[0] < tilemap.width_tiles
                    and 0 <= step[1] < tilemap.height_tiles):
                continue
            destination = step
            terrain = tilemap.terrain_at(*step)
            if terrain == ASTRAL and astral_hops:
                destination = (col + dc * 2, row + dr * 2)
                if not (0 <= destination[0] < tilemap.width_tiles
                        and 0 <= destination[1] < tilemap.height_tiles):
                    continue
                if (tilemap.is_solid(*destination)
                        or tilemap.terrain_at(*destination) in {ASTRAL, LAVA}):
                    continue
            elif tilemap.is_solid(*step) or terrain in {ASTRAL, LAVA}:
                continue
            if destination not in found:
                found.add(destination)
                queue.append(destination)
    return found


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_map_is_one_ashtray_route_with_only_the_avoidable_pit_fiend() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    counts = Counter(kind for kind, _ in tilemap.object_spawns)
    props = Counter(kind for kind, _col, _row in tilemap.prop_tiles)

    assert (tilemap.width_tiles, tilemap.height_tiles) == (76, 48)
    assert MAP_TILESET[MAP_NAME] == "phlegethos"
    assert AREA_MUSIC[MAP_NAME] == "phlegethos.wav"
    assert counts["anchor:phlegethos_fractured_anchor"] == 1
    assert counts["arrival:from_phlegethos_rubble"] == 1
    assert counts["arrival:from_phlegethos_fortress"] == 1
    assert counts["pit_fiend"] == 1
    assert counts["flameskull:h"] == 3
    assert counts["npc:businessman"] == 1
    assert props["city_bus_stop"] == 1
    assert props["phlegethos_rubble"] >= 250

    enemy_kinds = {
        "rat", "raccoon", "zombie", "skeleton", "lemure", "crocodile",
        "animal_control", "raptor", "massive_dinosaur", "horned_devil",
        "pit_fiend", "displacer_beast", "griffon", "snake", "fire_snake",
        "redcap", "thorn_mite",
    }
    assert {kind for kind in counts if kind in enemy_kinds} == {"pit_fiend"}

    # The huge fiend starts more than its full notice radius from every paved
    # route tile, so simply staying on the road avoids the encounter.
    pit = markers["pit_fiend"][0]
    path = [
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "≡"
    ]
    assert min(math.dist(pit, point) for point in path) > (
        config.DINOSAUR_NOTICE_RANGE / config.TILE_SIZE
    )


def test_astral_course_is_the_only_mandatory_hazard() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    arrival = markers["arrival:from_phlegethos_rubble"][0]
    onward = markers["arrival:from_phlegethos_fortress"][0]
    anchor = markers["anchor:phlegethos_fractured_anchor"][0]
    businessman = markers["npc:businessman"][0]

    walking = _reachable(tilemap, arrival)
    hopping = _reachable(tilemap, arrival, astral_hops=True)
    assert anchor in walking and businessman in walking
    assert onward not in walking, "the Astral course can be walked around"
    assert onward in hopping

    # Four full cross-bands require four separate committed jumps. The side
    # fields are three tiles thick, so none can be used as a one-hop bypass.
    for row in (15, 12, 9, 6):
        assert all(tilemap.terrain_at(col, row) == ASTRAL
                   for col in range(57, 64))
    for row in range(3, 18):
        assert all(tilemap.terrain_at(col, row) == ASTRAL
                   for col in (*range(54, 57), *range(64, 67)))

    # Lava and its skulls are off the required paved route, never a crossing.
    for point in markers["flameskull:h"]:
        assert tilemap.terrain_at(*point) == LAVA
        assert min(math.dist(point, path_point) for path_point in walking
                   if tilemap.terrain_at(*path_point) == "≡") > 5.0


def test_bus_stop_is_a_close_reachable_city_tableau() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    arrival = markers["arrival:from_phlegethos_rubble"][0]
    businessman = markers["npc:businessman"][0]
    bus_stop = next(
        (col, row) for kind, col, row in tilemap.prop_tiles
        if kind == "city_bus_stop"
    )
    walking = _reachable(tilemap, arrival)
    assert businessman in walking
    assert math.dist(bus_stop, businessman) < 4.0

    nearby_astral = [
        (col, row)
        for row in range(bus_stop[1] - 6, bus_stop[1] + 7)
        for col in range(bus_stop[0] - 8, bus_stop[0] + 9)
        if tilemap.terrain_at(col, row) == ASTRAL
    ]
    assert 4 <= len(nearby_astral) <= 8

    image = pygame.image.load(str(
        config.SPRITES_DIR / "objects" / "city_bus_stop.png"
    ))
    assert image.get_width() >= config.NPC_FRAME_W * 4
    assert image.get_height() >= config.NPC_FRAME_H * 2

    directory, game, world = _game_and_world()
    try:
        assert len(world.npcs) == 1
        npc = world.npcs[0]
        assert npc.npc_id == npc.dialogue_id == "businessman"
        assert world.dialogue.get(npc.interact(world.player)) == ["Ah! A rat!"]
        assert len(world.dinosaurs) == 1
        fiend = world.dinosaurs[0]
        assert fiend.variant == "pit_fiend"
        assert fiend.speed == config.DINOSAUR_SPEED
        assert fiend._frames["down"][0].get_size() == (128, 128)
        assert len(world.flameskulls) == 3
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0.0)
        world.draw(surface)
    finally:
        game._shutdown()
        directory.cleanup()


def test_new_map_sits_between_rubble_and_the_unchanged_fight() -> None:
    assert AREA_WALK_EXITS[(RUBBLE, "›")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "«")].destination == RUBBLE
    onward = AREA_WALK_EXITS[(MAP_NAME, "∇")]
    assert (onward.destination, onward.arrival) == (
        FORTRESS, "from_phlegethos_rubble"
    )
    back = AREA_WALK_EXITS[(FORTRESS, "Δ")]
    assert (back.destination, back.arrival) == (
        MAP_NAME, "from_phlegethos_fortress"
    )

    entry = CHECKPOINT_BY_ID[MAP_NAME]
    anchor = CHECKPOINT_BY_ID["phlegethos_fractured_anchor"]
    fortress = CHECKPOINT_BY_ID[FORTRESS]
    assert (entry.display_name, entry.arrival) == (
        "Phlegethos 5", "from_phlegethos_rubble"
    )
    assert anchor.display_name == "Phlegethos 5 Ashtray" and anchor.saveable
    assert fortress.display_name == "Phlegethos 6"


def _run_all() -> None:
    for name, function in sorted(globals().items()):
        if name.startswith("test_") and callable(function):
            function()
            print("  PASS ", name)
    print("All fractured-way tests passed.")


if __name__ == "__main__":
    _run_all()
