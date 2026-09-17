"""Phase 11 City Sewer 1 modern-tunnel foundation and rat pressure."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.choice import ChoiceSystem
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_sewer_1"


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


def _game_and_world(checkpoint="modern_city_sewer_1"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_city_sewer_1_is_long_narrow_modern_and_three_legged() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert (tilemap.width_tiles, tilemap.height_tiles) == (92, 38)
    assert tilemap.width_tiles > tilemap.height_tiles * 2
    assert MAP_TILESET[MAP_NAME] == "city_sewer"
    assert tileset_for(MAP_NAME).sheet == "city_sewer.png"
    assert tileset_for(MAP_NAME).sheet != tileset_for("sewer").sheet
    assert kinds["arrival:from_city_night_6"] == 1
    assert kinds["boundary:modern_city_night_6"] == 1
    assert kinds["rat"] == 5
    assert kinds["cigarette"] == 3

    used = Counter(char for row in tilemap._grid for char in row)
    for material in ("#", "b", "R", "i", "d", ",", "M", "%", "ƻ", "V"):
        assert used[material] > 0, material
    # Entry, long cross-run, and southern collided end establish three legs.
    assert not tilemap.is_solid(11, 34)
    assert not tilemap.is_solid(45, 20)
    assert not tilemap.is_solid(80, 29)


def test_all_authored_content_is_reachable_before_the_astral_end() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    reached = _reachable(tilemap, markers["arrival:from_city_night_6"][0])
    required = {
        markers["boundary:modern_city_night_6"][0],
        *markers["rat"],
        *markers["cigarette"],
    }
    assert required <= reached
    assert all(tilemap.terrain_at(col, row) == "V"
               for row in range(35, 38) for col in range(76, 81))
    exit_def = AREA_WALK_EXITS[(MAP_NAME, "⮟")]
    assert (exit_def.destination, exit_def.arrival, exit_def.facing) == (
        "modern_city_night_6", "from_city_sewer_1", "down"
    )


def test_city_entrance_yes_loads_sewer_and_no_remains_silent() -> None:
    choice = ChoiceSystem().get("city_sewer_entrance")
    yes, no = choice.options
    assert yes.goto == MAP_NAME and yes.arrival == "from_city_night_6"
    assert no.goto is None and no.dialogue is None and no.action is None

    directory, game, city = _game_and_world("modern_city_6")
    try:
        city._on_choice(yes)
        city.update(0.0)
        sewer = game.scenes.current
        assert sewer.map_name == MAP_NAME
        assert sewer._player_tile() == (11, 34)
        assert sewer.player.facing == "up"
    finally:
        game._shutdown()
        directory.cleanup()


def test_city_sewer_checkpoint_and_return_arrival_use_shared_loader() -> None:
    entry = CHECKPOINT_BY_ID["modern_city_sewer_1"]
    return_cp = CHECKPOINT_BY_ID["modern_city_6_return"]
    assert (entry.display_name, entry.map_name, entry.arrival) == (
        "City Sewer 1", MAP_NAME, "from_city_night_6"
    )
    assert (return_cp.map_name, return_cp.arrival) == (
        "modern_city_night_6", "from_city_sewer_1"
    )


def test_rats_use_ship_hold_pursuit_and_respect_astral_collision() -> None:
    directory, game, world = _game_and_world("modern_city_sewer_1")
    try:
        assert len(world.rats) == 5
        assert all(rat.attack_chase_enabled for rat in world.rats)
        assert all(not rat.patrolling and rat.tilemap is world.tilemap
                   for rat in world.rats)

        rat = world.rats[0]
        rat.x = 78 * config.TILE_SIZE + 4
        rat.y = 34 * config.TILE_SIZE + 5
        world.player.x = 78 * config.TILE_SIZE + 4
        world.player.y = 37 * config.TILE_SIZE + 5
        rat.update(1.0, world.player)
        rat_tile = (
            int((rat.x + rat.width / 2) // config.TILE_SIZE),
            int((rat.y + rat.height / 2) // config.TILE_SIZE),
        )
        assert world.tilemap.terrain_at(*rat_tile) != "V"

        world.rats[0].alive = False
        world.rats = [enemy for enemy in world.rats if enemy.alive]
        world._reset_enemies()
        assert len(world.rats) == 5
        assert all(enemy.attack_chase_enabled for enemy in world.rats)
    finally:
        game._shutdown()
        directory.cleanup()


def test_city_sewer_draws_without_city_rain_and_respawns_at_its_anchor() -> None:
    directory, game, world = _game_and_world("modern_city_sewer_1")
    try:
        assert world.city_rain is None
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        world._arrival_fade_t = None
        world.rats[0].alive = False
        world.rats = [rat for rat in world.rats if rat.alive]
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert len(world.rats) == 5
        assert all(rat.attack_chase_enabled for rat in world.rats)
    finally:
        game._shutdown()
        directory.cleanup()
