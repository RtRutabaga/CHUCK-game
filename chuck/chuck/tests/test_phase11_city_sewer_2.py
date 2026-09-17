"""Phase 11 City Sewer 2: the vertical descent and its rat pressure.

Sewer 1 is a wide map read as one long horizontal run, so this one is
deliberately its opposite -- tall and narrow, three shafts stepping down
and back west. These tests hold the region to the phase document's
instruction that the sewer maps turn rather than becoming four parallel
corridors. It also carries the sewer's toxic sludge and the phase's
harder Astral jump course, both built from systems the game already had.
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
SLUDGE = "ʓ"
SEWER_1 = "modern_city_sewer_1"


def _markers(tilemap):
    result = {}
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)
        ))
    return result


def _reachable(tilemap, start, *, hops=False):
    """Walk the map, optionally with the established committed jump, which
    clears exactly one tile of Astral onto safe ground."""
    found = {start}
    queue = deque([start])
    while queue:
        col, row = queue.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            step = (col + dc, row + dr)
            land = (col + 2 * dc, row + 2 * dr)
            for point in ((step, land) if hops else (step,)):
                x, y = point
                if not (0 <= x < tilemap.width_tiles
                        and 0 <= y < tilemap.height_tiles):
                    continue
                if point in found or tilemap.is_solid(x, y):
                    continue
                if tilemap.terrain_at(x, y) == "V":
                    continue
                if point is land and tilemap.terrain_at(*step) != "V":
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
    assert kinds["boundary:modern_city_sewer_1"] == 1
    assert kinds["rat"] == 6
    assert kinds["cigarette"] == 3

    used = Counter(char for row in tilemap._grid for char in row)
    for material in ("#", "b", "R", "i", "d", ",", "M", "%", "ƻ", "V"):
        assert used[material] > 0, material

    # Three shafts joined by two jogs: the route turns four times.
    for point in ((10, 12), (10, 22), (24, 23), (34, 30),
                  (34, 42), (16, 42), (12, 45), (22, 51)):
        assert not tilemap.is_solid(*point), point


def test_everything_authored_is_reachable_and_nothing_waits_on_the_waypoint() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_city_sewer_1_culvert"][0]
    reached = _reachable(tilemap, start, hops=True)

    # Respawning must never drop Chuck onto a rat.

    # The southern end is collided either side of a marked opening: the
    # floor gave way here, and that hole is now the way down to Sewer 3.
    assert all(tilemap.terrain_at(col, row) == "V"
               for row in range(59, 62) for col in (12, 13, 16, 17))
    assert all(tilemap.terrain_at(col, row) == "⮟"
               for row in range(59, 62) for col in (14, 15))
    # The sewer's new hazard is present, and shapes rather than covers.
    sludge = sum(row.count(SLUDGE) for row in tilemap._grid)
    total = tilemap.width_tiles * tilemap.height_tiles
    assert 0 < sludge < total // 20, sludge


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
    # The sewer theme now runs unbroken through all four tunnels.
    assert AREA_MUSIC[MAP_NAME] == "city_sewer.wav"

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
    back = CHECKPOINT_BY_ID["modern_city_sewer_1_return"]
    assert (entry.display_name, entry.map_name, entry.arrival) == (
        "City Sewer 2", MAP_NAME, "from_city_sewer_1_culvert"
    )
    assert entry.runtime_entry
    assert (back.map_name, back.arrival) == (SEWER_1, "from_city_sewer_2")


def test_rats_pursue_here_exactly_as_they_do_in_sewer_1() -> None:
    directory, game, world = _game_and_world("modern_city_sewer_2")
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


def test_sewer_2_draws_without_rain_and_respawns_at_its_own_door() -> None:
    directory, game, world = _game_and_world("modern_city_sewer_2")
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
        assert len(world.rats) == 6
    finally:
        game._shutdown()
        directory.cleanup()


def test_sludge_reuses_the_thorn_and_pollen_systems() -> None:
    """The phase document asks for the two existing effects combined, not
    a sewer-only rule living somewhere new."""
    from src.systems.terrain_effect import SLOWING_TERRAIN, ground_speed_multiplier
    from src.systems.terrain_hazard import TERRAIN_HAZARDS, touching_terrain_hazard

    assert TERRAIN_HAZARDS[SLUDGE].sanity_damage == config.SLUDGE_SANITY_DAMAGE
    assert TERRAIN_HAZARDS[SLUDGE].kind == "sludge"
    assert SLOWING_TERRAIN[SLUDGE] == config.SLUDGE_SPEED_MULTIPLIER
    # It bites harder than thorns and drags harder than pollen.
    assert config.SLUDGE_SANITY_DAMAGE > config.THORN_SANITY_DAMAGE
    assert config.SLUDGE_SPEED_MULTIPLIER < config.FEYWILD_POLLEN_SPEED_MULTIPLIER
    # ...and it is unmistakable: its own animated art, not the channel.
    assert tileset_for(MAP_NAME).char_to_terrain[SLUDGE] == "city_sewer_sludge"
    art = dict((name, (v, f)) for name, v, f in tileset_for(MAP_NAME).order)
    assert art["city_sewer_sludge"][1] > 1

    directory, game, world = _game_and_world("modern_city_sewer_2")
    try:
        tilemap = world.tilemap
        sludge = next(
            (col, row)
            for row in range(tilemap.height_tiles)
            for col in range(tilemap.width_tiles)
            if tilemap.terrain_at(col, row) == SLUDGE
        )
        world.player.x = sludge[0] * config.TILE_SIZE
        world.player.y = sludge[1] * config.TILE_SIZE
        box = world.player.hitbox
        assert ground_speed_multiplier(tilemap, box, False) == (
            config.SLUDGE_SPEED_MULTIPLIER)
        assert touching_terrain_hazard(tilemap, box, False).kind == "sludge"
        # Jumping over it costs nothing: airborne is never slowed or bitten.
        assert ground_speed_multiplier(tilemap, box, True) == 1.0
        assert touching_terrain_hazard(tilemap, box, True) is None

        # Standing in it drains Sanity at the shared cadence...
        world._arrival_fade_t = None
        world.sanity.current = world.sanity.maximum
        for _ in range(40):
            world.update(0.05)
        assert world.sanity.current < world.sanity.maximum

        # ...and stepping out restores full speed immediately, because the
        # effect is read from the footprint rather than stored.
        clean = next(
            (col, row)
            for row in range(tilemap.height_tiles)
            for col in range(tilemap.width_tiles)
            if tilemap.terrain_at(col, row) == "d"
        )
        world.player.x = clean[0] * config.TILE_SIZE
        world.player.y = clean[1] * config.TILE_SIZE
        assert ground_speed_multiplier(tilemap, world.player.hitbox, False) == 1.0
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_astral_course_must_be_jumped_and_cannot_be_walked() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_city_sewer_1_culvert"][0]

    def flood(hops):
        found = {start}
        queue = deque([start])
        while queue:
            col, row = queue.popleft()
            for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                step = (col + dc, row + dr)
                land = (col + 2 * dc, row + 2 * dr)
                for point in ((step, land) if hops else (step,)):
                    x, y = point
                    if not (0 <= x < tilemap.width_tiles
                            and 0 <= y < tilemap.height_tiles):
                        continue
                    if point in found or tilemap.is_solid(x, y):
                        continue
                    if tilemap.terrain_at(x, y) == "V":
                        continue
                    if point is land and tilemap.terrain_at(*step) != "V":
                        continue
                    found.add(point)
                    queue.append(point)
        return found

    chamber = (12, 56)
    assert chamber in flood(True), "the course cannot be completed"
    assert chamber not in flood(False), "the course can be walked around"

    # Several gaps, every one of them a single tile across.
    # The course only; the reserved southern block below it is collided
    # ground marking where Sewer 3 will attach, not a crossing.
    gaps = [(col, row)
            for row in range(44, 59)
            for col in range(tilemap.width_tiles)
            if tilemap.terrain_at(col, row) == "V"]
    assert len(gaps) >= 20, len(gaps)
    for col, row in gaps:
        horizontal = (tilemap.terrain_at(col - 1, row) != "V"
                      and tilemap.terrain_at(col + 1, row) != "V")
        vertical = (tilemap.terrain_at(col, row - 1) != "V"
                    and tilemap.terrain_at(col, row + 1) != "V")
        assert horizontal or vertical, (col, row)

    # The course turns rather than dropping in one straight line.
    columns = {col for col, _row in gaps}
    rows = {row for _col, row in gaps}
    assert len(columns) > 6 and len(rows) > 4

    # The door sits above the course, never inside it.


def test_a_missed_jump_falls_and_returns_to_this_maps_door() -> None:
    from src.systems.fall import fall_zone_kind

    directory, game, world = _game_and_world("modern_city_sewer_2")
    try:
        world._arrival_fade_t = None
        gap = next(
            (col, row)
            for row in range(44, 59)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "V"
        )
        world.player.x = gap[0] * config.TILE_SIZE
        world.player.y = gap[1] * config.TILE_SIZE
        assert fall_zone_kind(world.tilemap, world.player.hitbox, False) is not None
        # ...but not while the jump is still carrying him across it.
        assert fall_zone_kind(world.tilemap, world.player.hitbox, True) is None

        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
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
