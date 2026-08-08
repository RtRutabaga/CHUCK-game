"""Phase 11 City Sewer 3: the flooded hall and its crocodile.

The region doubles back here -- Sewer 1 ran east, Sewer 2 dropped south,
this one runs west -- and its middle is a wide hall with a sludge channel
and one crocodile living in it.

The phase document is explicit that the crocodile must stay escapable or
avoidable rather than becoming a mandatory combat gate, so the test that
matters proves a route across the hall exists that never enters its
notice range, while the channel itself stays genuinely contested.
"""

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
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_sewer_3"
SEWER_2 = "modern_city_sewer_2"
SLUDGE = "ʓ"


def _markers(tilemap):
    result = {}
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)
        ))
    return result


def _flood(tilemap, start, *, avoid=None):
    notice = config.UNDEAD_NOTICE_RANGE / config.TILE_SIZE
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < tilemap.width_tiles
                    and 0 <= y < tilemap.height_tiles):
                continue
            if point in found or tilemap.is_solid(x, y):
                continue
            if avoid is not None and math.dist(point, avoid) <= notice:
                continue
            found.add(point)
            queue.append(point)
    return found


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_the_region_doubles_back_instead_of_running_on() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (84, 40)
    assert MAP_TILESET[MAP_NAME] == "city_sewer"
    assert tileset_for(MAP_NAME).sheet != tileset_for("sewer").sheet

    markers = _markers(tilemap)
    # Chuck drops in at the east edge and leaves at the west: the three
    # sewer maps so far run east, then south, then back west.
    arrival = markers["arrival:from_city_sewer_2_drop"][0]
    onward = markers["boundary:modern_city_sewer_4"][0]
    assert arrival[0] > tilemap.width_tiles * 0.8, arrival
    assert onward[0] < tilemap.width_tiles * 0.1, onward

    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["crocodile"] == 1
    assert kinds["anchor:modern_city_sewer_3_anchor"] == 1
    assert kinds["rat"] == 4
    assert kinds["cigarette"] == 3

    used = Counter(char for row in tilemap._grid for char in row)
    for material in ("#", "b", "R", "i", "d", ",", "M", "%", SLUDGE):
        assert used[material] > 0, material


def test_the_crocodile_can_always_be_walked_around() -> None:
    """The phase document's hard requirement for this encounter."""
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_city_sewer_2_drop"][0]
    croc = markers["crocodile"][0]
    onward = markers["boundary:modern_city_sewer_4"][0]
    anchor = markers["anchor:modern_city_sewer_3_anchor"][0]

    reachable = _flood(tilemap, start)
    assert {onward, anchor, croc} <= reachable

    clear = _flood(tilemap, start, avoid=croc)
    assert onward in clear, "the crocodile blocks the only way through"
    assert anchor in clear, "the Ashtray sits inside its notice range"
    # ...but it does hold the channel it lives in.
    assert not any(math.dist(point, croc) <= 3 for point in clear)

    # It lies in the sludge, which is what makes it dangerous: slowed,
    # Chuck is still quicker, but not by much.
    assert tilemap.terrain_at(*croc) == SLUDGE
    slowed = config.PLAYER_SPEED * config.SLUDGE_SPEED_MULTIPLIER
    assert slowed > config.CROCODILE_SPEED, (slowed, config.CROCODILE_SPEED)


def test_a_crocodile_is_the_zombie_role_moving_faster() -> None:
    from src.entities.undead import UndeadEnemy

    assert config.CROCODILE_SPEED > config.ZOMBIE_SPEED
    assert config.CROCODILE_SCRATCHES >= config.ZOMBIE_SCRATCHES
    assert config.CROCODILE_SANITY_DAMAGE >= config.ZOMBIE_SANITY_DAMAGE

    directory, game, world = _game_and_world("modern_city_sewer_3_anchor")
    try:
        assert len(world.undead) == 1
        croc = world.undead[0]
        assert isinstance(croc, UndeadEnemy) and croc.kind == "crocodile"
        assert croc.speed == config.CROCODILE_SPEED
        assert croc.max_scratches == config.CROCODILE_SCRATCHES

        # It ignores Chuck beyond its notice range, then comes straight on.
        home = (croc.x, croc.y)
        world.player.x = croc.x + config.UNDEAD_NOTICE_RANGE * 2
        world.player.y = croc.y
        for _ in range(20):
            croc.update(0.05, world.player)
        assert (croc.x, croc.y) == home, "it noticed Chuck from too far"

        world.player.x = croc.x + config.UNDEAD_NOTICE_RANGE / 3
        world.player.y = croc.y
        for _ in range(20):
            croc.update(0.05, world.player)
        assert croc.x > home[0], "it should pursue once it notices"

        # It can be fought, but it takes a while -- it is not a rat.
        for _ in range(config.CROCODILE_SCRATCHES - 1):
            croc.on_scratched()
        assert croc.alive
        croc.on_scratched()
        assert not croc.alive
    finally:
        game._shutdown()
        directory.cleanup()


def test_sewer_2_drops_into_sewer_3_and_back() -> None:
    down = AREA_WALK_EXITS[(SEWER_2, "⮟")]
    assert (down.destination, down.arrival) == (
        MAP_NAME, "from_city_sewer_2_drop")
    back = AREA_WALK_EXITS[(MAP_NAME, "⮞")]
    assert (back.destination, back.arrival) == (SEWER_2, "from_city_sewer_3")

    entry = CHECKPOINT_BY_ID[MAP_NAME]
    assert (entry.display_name, entry.map_name) == ("City Sewer 3", MAP_NAME)
    assert entry.runtime_entry
    assert CHECKPOINT_BY_ID["modern_city_sewer_3_anchor"].saveable

    directory, game, world = _game_and_world(SEWER_2)
    try:
        world._arrival_fade_t = None
        drop = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮟"
        )
        world.player.x = drop[0] * config.TILE_SIZE
        world.player.y = drop[1] * config.TILE_SIZE
        world.update(0.0)
        assert world.map_name == MAP_NAME
        assert game.active_checkpoint_id == MAP_NAME
        world.update(0.0)
        assert world.map_name == MAP_NAME  # no bounce

        back_tile = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮞"
        )
        world.player.x = back_tile[0] * config.TILE_SIZE
        world.player.y = back_tile[1] * config.TILE_SIZE + 4
        world.update(0.0)
        assert world.map_name == SEWER_2
        assert game.active_checkpoint_id == "modern_city_sewer_2_return"
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_hall_draws_and_respawn_restores_the_crocodile() -> None:
    directory, game, world = _game_and_world("modern_city_sewer_3_anchor")
    try:
        assert world.city_rain is None
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        world._arrival_fade_t = None
        world.undead[0].alive = False
        world.undead = [enemy for enemy in world.undead if enemy.alive]
        world.rats[0].alive = False
        world.rats = [rat for rat in world.rats if rat.alive]
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert (world.player.x, world.player.y) == (
            world.anchors[0].x, world.anchors[0].y
        )
        assert len(world.undead) == 1 and len(world.rats) == 4
        assert world.undead[0].scratches_remaining == (
            config.CROCODILE_SCRATCHES)
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
    print("All City Sewer 3 tests passed.")


if __name__ == "__main__":
    _run_all()
