"""Phase 11 City Sewer 2: the vertical descent and its rat pressure.

Sewer 1 is a wide map read as one long horizontal run, so this one is
deliberately its opposite -- tall and narrow, three shafts stepping down
and back west. These tests hold the region to the phase document's
instruction that the sewer maps turn rather than becoming four parallel
corridors, and that this slice adds no sludge and no jump sequence.
"""

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
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "modern_city_sewer_2"
SEWER_1 = "modern_city_sewer_1"


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


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_city_sewer_2_descends_instead_of_repeating_sewer_1() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    other = TileMap(config.MAPS_DIR / f"{SEWER_1}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (46, 62)
    # The region must turn: Sewer 1 reads wide, this one reads tall.
    assert tilemap.height_tiles > tilemap.width_tiles
    assert other.width_tiles > other.height_tiles
    assert MAP_TILESET[MAP_NAME] == "city_sewer"
    assert tileset_for(MAP_NAME).sheet == "city_sewer.png"
    assert tileset_for(MAP_NAME).sheet != tileset_for("sewer").sheet

    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["arrival:from_city_sewer_1_culvert"] == 1
    assert kinds["anchor:modern_city_sewer_2_anchor"] == 1
    assert kinds["boundary:modern_city_sewer_1"] == 1
    assert kinds["rat"] == 6
    assert kinds["cigarette"] == 3

    used = Counter(char for row in tilemap._grid for char in row)
    for material in ("#", "b", "R", "i", "d", ",", "M", "%", "ƻ", "V"):
        assert used[material] > 0, material

    # Three shafts joined by two jogs: the route turns four times.
    for point in ((10, 12), (10, 22), (24, 23), (34, 30),
                  (34, 42), (16, 42), (16, 52)):
        assert not tilemap.is_solid(*point), point


def test_everything_authored_is_reachable_and_nothing_waits_on_the_ashtray() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_city_sewer_1_culvert"][0]
    reached = _reachable(tilemap, start)
    anchor = markers["anchor:modern_city_sewer_2_anchor"][0]

    assert {anchor, markers["boundary:modern_city_sewer_1"][0],
            *markers["rat"], *markers["cigarette"]} <= reached
    # Respawning must never drop Chuck onto a rat.
    assert anchor not in set(markers["rat"])

    # The southern continuation stays collided rather than pretending
    # Sewer 3 already exists.
    assert all(tilemap.terrain_at(col, row) == "V"
               for row in range(59, 62) for col in range(12, 18))
    # Sludge and the harder Astral jump sequence belong to a later pass.
    assert not any(tilemap.terrain_at(col, row) == "≈"
                   for row in range(tilemap.height_tiles)
                   for col in range(tilemap.width_tiles))


def test_the_culvert_joins_the_two_sewer_maps_both_ways() -> None:
    onward = AREA_WALK_EXITS[(SEWER_1, "⮞")]
    assert (onward.destination, onward.arrival, onward.facing) == (
        MAP_NAME, "from_city_sewer_1_culvert", "right"
    )
    back = AREA_WALK_EXITS[(MAP_NAME, "⮜")]
    assert (back.destination, back.arrival, back.facing) == (
        SEWER_1, "from_city_sewer_2", "left"
    )
    # Sewer 1's own way back up to the night city is untouched.
    assert AREA_WALK_EXITS[(SEWER_1, "⮟")].destination == "modern_city_night_6"
    assert AREA_MUSIC[MAP_NAME] is None  # the sewer theme is a later pass

    directory, game, world = _game_and_world("modern_city_sewer_1")
    try:
        world._arrival_fade_t = None
        onward_tile = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮞"
        )
        world.player.x = onward_tile[0] * config.TILE_SIZE
        world.player.y = onward_tile[1] * config.TILE_SIZE + 4
        world.update(0.0)
        assert world.map_name == MAP_NAME
        assert game.active_checkpoint_id == MAP_NAME
        world.update(0.0)
        assert world.map_name == MAP_NAME  # no bounce

        back_tile = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮜"
        )
        world.player.x = back_tile[0] * config.TILE_SIZE
        world.player.y = back_tile[1] * config.TILE_SIZE + 4
        world.update(0.0)
        assert world.map_name == SEWER_1
        assert game.active_checkpoint_id == "modern_city_sewer_1_return"
    finally:
        game._shutdown()
        directory.cleanup()


def test_sewer_2_checkpoints_use_the_shared_loader() -> None:
    entry = CHECKPOINT_BY_ID[MAP_NAME]
    anchor = CHECKPOINT_BY_ID["modern_city_sewer_2_anchor"]
    back = CHECKPOINT_BY_ID["modern_city_sewer_1_return"]
    assert (entry.display_name, entry.map_name, entry.arrival) == (
        "City Sewer 2", MAP_NAME, "from_city_sewer_1_culvert"
    )
    assert entry.runtime_entry
    assert anchor.saveable and not anchor.development_visible
    assert (back.map_name, back.arrival) == (SEWER_1, "from_city_sewer_2")


def test_rats_pursue_here_exactly_as_they_do_in_sewer_1() -> None:
    directory, game, world = _game_and_world("modern_city_sewer_2_anchor")
    try:
        assert len(world.rats) == 6
        assert all(rat.attack_chase_enabled for rat in world.rats)
        assert all(not rat.patrolling and rat.tilemap is world.tilemap
                   for rat in world.rats)

        # Pursuit stops at walls rather than walking through a shaft edge.
        rat = world.rats[0]
        rat.x = 10 * config.TILE_SIZE
        rat.y = 12 * config.TILE_SIZE
        world.player.x = 2 * config.TILE_SIZE
        world.player.y = 12 * config.TILE_SIZE
        for _ in range(40):
            rat.update(0.05, world.player)
        rat_tile = (
            int((rat.x + rat.width / 2) // config.TILE_SIZE),
            int((rat.y + rat.height / 2) // config.TILE_SIZE),
        )
        assert not world.tilemap.is_solid(*rat_tile)

        world.rats[0].alive = False
        world.rats = [enemy for enemy in world.rats if enemy.alive]
        world._reset_enemies()
        assert len(world.rats) == 6
        assert all(enemy.attack_chase_enabled for enemy in world.rats)
    finally:
        game._shutdown()
        directory.cleanup()


def test_sewer_2_draws_without_rain_and_respawns_at_its_own_ashtray() -> None:
    directory, game, world = _game_and_world("modern_city_sewer_2_anchor")
    try:
        assert world.city_rain is None   # underground: no exterior weather
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        world._arrival_fade_t = None
        world.rats[0].alive = False
        world.rats = [rat for rat in world.rats if rat.alive]
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
        assert len(world.rats) == 6
    finally:
        game._shutdown()
        directory.cleanup()


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
    print("All City Sewer 2 tests passed.")


if __name__ == "__main__":
    _run_all()
