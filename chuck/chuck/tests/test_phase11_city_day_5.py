"""Phase 11 City Day 5: the overpass, and what is left of it.

The last ordinary daytime map. A raised deck is all that survives here,
nine tiles wide with the Astral Sea on both sides and traffic still
running on it. Two spans have dropped out, and unlike City Day 4's
square these jumps are the route rather than a reward.

That makes fairness the thing to prove: each gap is a single tile, the
deck resumes directly beyond it, and a pavement crosses every gap so a
player is never forced to launch from or land in a live lane.
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


MAP_NAME = "modern_city_day_5"
DAY_4 = "modern_city_day_4"
DECK_LEFT, DECK_RIGHT = 17, 28
DAY_MAPS = ("modern_city_day_1", "modern_city_day_2", "modern_city_day_3",
            DAY_4, MAP_NAME)


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


def _spans(tilemap):
    return [row for row in range(1, tilemap.height_tiles - 1)
            if all(tilemap.terrain_at(col, row) == "V"
                   for col in range(DECK_LEFT, DECK_RIGHT + 1))]


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(checkpoint)
    world._arrival_fade_t = None
    return directory, game, world


def test_the_deck_is_the_only_ground_left() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (46, 68)
    assert MAP_TILESET[MAP_NAME] == "city_day"
    # Tall and narrow: a crossing, not a district.
    assert tilemap.height_tiles > tilemap.width_tiles

    # Everything off the deck is Sea, on both sides, top to bottom.
    for row in range(tilemap.height_tiles):
        assert tilemap.terrain_at(0, row) == "V", row
        assert tilemap.terrain_at(tilemap.width_tiles - 1, row) == "V", row

    # The damage ratchet holds across the whole daytime run.
    def density(name):
        other = TileMap(config.MAPS_DIR / f"{name}.txt")
        total = other.width_tiles * other.height_tiles
        return sum(row.count("V") for row in other._grid) / total

    densities = [density(name) for name in DAY_MAPS]
    assert densities == sorted(densities), dict(zip(DAY_MAPS, densities))

    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["cigarette"] == 4
    assert sum(count for kind, count in kinds.items()
               if kind.startswith("traffic_lane:")) == 3
    assert not any(kind.endswith("homeless_man") for kind in kinds)


def test_the_broken_spans_are_the_route_and_are_fair() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    start = markers["arrival:from_city_day_4"][0]
    onward = markers["boundary:modern_city_day_6"][0]

    hopped = _flood(tilemap, start, hops=True)
    walked = _flood(tilemap, start, hops=False)
    assert onward in hopped, "the overpass cannot be crossed"
    assert onward not in walked, "the spans can be walked around"
    # The Ashtray sits before the first gap, so a missed jump is cheap.
    assert markers["anchor:modern_city_day_5_anchor"][0] in walked

    spans = _spans(tilemap)
    assert len(spans) == 2, spans
    for row in spans:
        # One tile deep, with deck directly either side of it.
        for col in range(DECK_LEFT, DECK_RIGHT + 1):
            assert tilemap.terrain_at(col, row - 1) != "V", (col, row)
            assert tilemap.terrain_at(col, row + 1) != "V", (col, row)
        # ...and a footway crosses it, so no jump is forced into a lane.
        pavement = (DECK_LEFT, DECK_LEFT + 1, DECK_RIGHT - 1, DECK_RIGHT)
        assert any(
            tilemap.terrain_at(col, row - 1) not in {"=", "≡", "‖", "V"}
            and tilemap.terrain_at(col, row + 1) not in {"=", "≡", "‖", "V"}
            for col in pavement
        ), row


def test_day_4_and_5_connect_and_share_the_day_cue() -> None:
    onward = AREA_WALK_EXITS[(DAY_4, "⮞")]
    assert (onward.destination, onward.arrival) == (
        MAP_NAME, "from_city_day_4")
    back = AREA_WALK_EXITS[(MAP_NAME, "⮝")]
    assert (back.destination, back.arrival) == (DAY_4, "from_city_day_5")
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[DAY_4] == "city_day.wav"

    entry = CHECKPOINT_BY_ID[MAP_NAME]
    assert (entry.display_name, entry.map_name) == ("City Day 5", MAP_NAME)
    assert entry.runtime_entry
    assert CHECKPOINT_BY_ID["modern_city_day_5_anchor"].saveable

    directory, game, world = _game_and_world(DAY_4)
    try:
        east = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮞"
        )
        world.player.x = east[0] * config.TILE_SIZE
        world.player.y = east[1] * config.TILE_SIZE
        world.update(0.0)
        assert world.map_name == MAP_NAME
        assert game.active_checkpoint_id == MAP_NAME
        world.update(0.0)
        assert world.map_name == MAP_NAME  # no bounce
    finally:
        game._shutdown()
        directory.cleanup()


def test_traffic_still_runs_on_a_road_that_goes_nowhere() -> None:
    directory, game, world = _game_and_world("modern_city_day_5_anchor")
    try:
        assert world.city_rain is not None
        assert len(world.traffic_lanes) == 3
        assert world.traffic_vehicles

        before = [(car.x, car.y) for car in world.traffic_vehicles]
        for _ in range(10):
            world.update(0.05)
        after = [(car.x, car.y) for car in world.traffic_vehicles]
        assert before != after

        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)

        anchor = (world.anchors[0].x, world.anchors[0].y)
        world.sanity.deplete()
        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert (world.player.x, world.player.y) == anchor
        # Respawning lands on the footway, never in a lane or a gap.
        tile = (int(world.player.x // config.TILE_SIZE),
                int(world.player.y // config.TILE_SIZE))
        assert world.tilemap.terrain_at(*tile) not in {"=", "≡", "‖", "V"}
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
    print("All City Day 5 tests passed.")


if __name__ == "__main__":
    _run_all()
