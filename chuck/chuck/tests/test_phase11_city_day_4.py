"""Phase 11 City Day 4: the square whose floor gave way.

The first three daytime maps lost buildings. This one loses the ground:
a civic square broken into slabs with the Astral Sea between them, so
crossing it takes the committed jump the Fen and the sewer taught --
now on concrete, in daylight, as the ramp toward City Day 6.

The square is tempting rather than mandatory, and these tests hold both
halves of that: every cigarette on it needs a jump, and somebody who
refuses to jump at all can still finish the map.
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
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "modern_city_day_4"
DAY_3 = "modern_city_day_3"


def _markers(tilemap):
    result = {}
    ts = config.TILE_SIZE
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((int(x // ts), int(y // ts)))
    return result


def _flood(tilemap, start, *, hops):
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


def _density(tilemap):
    total = tilemap.width_tiles * tilemap.height_tiles
    return sum(row.count("V") for row in tilemap._grid) / total


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(checkpoint)
    world._arrival_fade_t = None
    return directory, game, world


def test_the_damage_ratchet_holds_across_the_daytime_run() -> None:
    """No daytime map may be less damaged than the one before it.

    Density rather than raw count: a bigger map with the same share of
    void is not a more damaged one.
    """
    names = ("modern_city_day_1", "modern_city_day_2", DAY_3, MAP_NAME)
    densities = [_density(TileMap(config.MAPS_DIR / f"{name}.txt"))
                 for name in names]
    assert densities == sorted(densities), dict(zip(names, densities))
    # ...and this map is the most damaged so far, by a clear margin.
    assert densities[-1] > 0.35, densities[-1]


def test_the_square_is_slabs_over_nothing() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (70, 52)
    assert MAP_TILESET[MAP_NAME] == "city_day"

    markers = _markers(tilemap)
    hopped = _flood(tilemap, markers["arrival:from_city_day_3"][0], hops=True)
    walked = _flood(tilemap, markers["arrival:from_city_day_3"][0], hops=False)

    # Every crack is one tile: each void tile inside the square has solid
    # footing directly opposite it on at least one axis.
    square_gaps = [
        (col, row)
        for row in range(15, 38) for col in range(18, 53)
        if tilemap.terrain_at(col, row) == "V"
    ]
    assert len(square_gaps) > 100, len(square_gaps)
    for col, row in square_gaps:
        crossable = any(
            not tilemap.is_solid(col - dc, row - dr)
            and tilemap.terrain_at(col - dc, row - dr) != "V"
            and not tilemap.is_solid(col + dc, row + dr)
            and tilemap.terrain_at(col + dc, row + dr) != "V"
            for dc, dr in ((1, 0), (0, 1))
        )
        assert crossable or (col, row) not in hopped, (col, row)

    # The slabs are only reachable by jumping.
    interior = (20, 17)
    assert interior in hopped and interior not in walked


def test_the_jumps_are_tempting_but_never_required() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_city_day_3"][0]
    walked = _flood(tilemap, start, hops=False)
    hopped = _flood(tilemap, start, hops=True)

    # Somebody who never jumps can still cross the map and save.
    assert markers["boundary:modern_city_day_5"][0] in walked
    assert markers["anchor:modern_city_day_4_anchor"][0] in walked
    assert markers["boundary:modern_city_day_3"][0] in walked

    # ...but every cigarette is out on the slabs.
    caches = markers["cigarette"]
    assert len(caches) == 4
    assert all(cache in hopped for cache in caches)
    assert not any(cache in walked for cache in caches)


def test_day_3_and_4_connect_and_share_the_day_cue() -> None:
    onward = AREA_WALK_EXITS[(DAY_3, "⮟")]
    assert (onward.destination, onward.arrival) == (
        MAP_NAME, "from_city_day_3")
    back = AREA_WALK_EXITS[(MAP_NAME, "⮝")]
    assert (back.destination, back.arrival) == (DAY_3, "from_city_day_4")
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[DAY_3] == "city_day.wav"

    entry = CHECKPOINT_BY_ID[MAP_NAME]
    assert (entry.display_name, entry.map_name) == ("City Day 4", MAP_NAME)
    assert entry.runtime_entry
    assert CHECKPOINT_BY_ID["modern_city_day_4_anchor"].saveable

    directory, game, world = _game_and_world(DAY_3)
    try:
        south = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮟"
        )
        world.player.x = south[0] * config.TILE_SIZE
        world.player.y = south[1] * config.TILE_SIZE
        world.update(0.0)
        assert world.map_name == MAP_NAME
        assert game.active_checkpoint_id == MAP_NAME
        world.update(0.0)
        assert world.map_name == MAP_NAME  # no bounce
    finally:
        game._shutdown()
        directory.cleanup()


def test_a_missed_jump_falls_and_returns_to_the_ashtray() -> None:
    directory, game, world = _game_and_world("modern_city_day_4_anchor")
    try:
        from src.systems.fall import fall_zone_kind

        assert world.city_rain is not None
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        crack = next(
            (col, row)
            for row in range(15, 38) for col in range(18, 53)
            if world.tilemap.terrain_at(col, row) == "V"
        )
        world.player.x = crack[0] * config.TILE_SIZE
        world.player.y = crack[1] * config.TILE_SIZE
        assert fall_zone_kind(world.tilemap, world.player.hitbox, False)
        # ...but not while the jump is still carrying him across.
        assert fall_zone_kind(world.tilemap, world.player.hitbox, True) is None

        anchor = (world.anchors[0].x, world.anchors[0].y)
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert (world.player.x, world.player.y) == anchor
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
    print("All City Day 4 tests passed.")


if __name__ == "__main__":
    _run_all()
