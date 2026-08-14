"""Phase 11 City Sewer 4: the last tunnel and the way back up.

The region has run east, dropped south, and doubled back west; this map
turns north and climbs to a human-scale maintenance ladder with daylight
at its head.

Its "Climb up ladder?" prompt now leads to City Day 1, which is where
the phase's daytime half begins.
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
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.choice import ChoiceSystem
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import MAP_TILESET, tileset_for
from src.world.transitions import AREA_WALK_EXITS


MAP_NAME = "modern_city_sewer_4"
SEWER_3 = "modern_city_sewer_3"
LADDER_TOP, LADDER_BOTTOM = "Ɫ", "ɬ"


def _markers(tilemap):
    result = {}
    for kind, (x, y) in tilemap.object_spawns:
        result.setdefault(kind, []).append((
            int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)
        ))
    return result


def _flood(tilemap, start):
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
            found.add(point)
            queue.append(point)
    return found


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game, game.checkpoints.load_checkpoint(checkpoint)


def test_the_last_tunnel_turns_north_and_climbs() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (54, 50)
    assert MAP_TILESET[MAP_NAME] == "city_sewer"
    assert tileset_for(MAP_NAME).sheet != tileset_for("sewer").sheet

    markers = _markers(tilemap)
    arrival = markers["arrival:from_city_sewer_3_west"][0]
    ladder = next(
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == LADDER_TOP
    )
    # The route climbs more than it runs: that is the region's fourth turn.
    assert abs(arrival[1] - ladder[1]) > abs(arrival[0] - ladder[0])

    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["anchor:modern_city_sewer_4_anchor"] == 1
    assert kinds["rat"] == 4
    assert kinds["cigarette"] == 3
    # The region gets exactly one crocodile, and it lives in Sewer 3.
    assert kinds["crocodile"] == 0

    used = Counter(char for row in tilemap._grid for char in row)
    for material in ("#", "b", "R", "i", "d", ",", "M", "%", "ʓ"):
        assert used[material] > 0, material


def test_the_ladder_is_one_human_scale_structure_at_the_end() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    tops = [(col, row)
            for row in range(tilemap.height_tiles)
            for col in range(tilemap.width_tiles)
            if tilemap.terrain_at(col, row) == LADDER_TOP]
    assert len(tops) == 1
    col, row = tops[0]
    # Two cells, one 16x32 structure -- the ship ladder's exact shape.
    assert tilemap.terrain_at(col, row + 1) == LADDER_BOTTOM
    assert not TILE_DEFS[LADDER_TOP].solid
    assert not TILE_DEFS[LADDER_BOTTOM].solid
    assert tileset_for(MAP_NAME).char_to_terrain[LADDER_TOP] == (
        "city_sewer_ladder_top")

    # It climbs into the ceiling rather than standing free in the room.
    assert tilemap.is_solid(col, row - 1)

    markers = _markers(tilemap)
    reachable = _flood(tilemap, markers["arrival:from_city_sewer_3_west"][0])
    assert (col, row + 1) in reachable, "the ladder's foot is unreachable"
    assert markers["anchor:modern_city_sewer_4_anchor"][0] in reachable


def test_the_ladder_asks_before_it_climbs() -> None:
    """The prompt this map was built toward. Walking to the ladder's foot
    asks; NO closes silently; YES leaves the sewer for the day city."""
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    triggers = [pos for kind, pos in tilemap.object_spawns
                if kind == "choice:city_sewer_ladder"]
    assert len(triggers) == 1
    ladder = next(
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == LADDER_TOP
    )
    trigger = (int(triggers[0][0] // config.TILE_SIZE),
               int(triggers[0][1] // config.TILE_SIZE))
    # It fires from the floor at the ladder's foot, so Chuck is standing
    # on ordinary ground when the question appears.
    assert trigger == (ladder[0], ladder[1] + 2)
    assert not tilemap.is_solid(*trigger)

    choice = ChoiceSystem().get("city_sewer_ladder")
    assert choice.prompt == "Climb up ladder?"
    yes, no = choice.options
    assert yes.goto == "modern_city_day_1"
    assert yes.arrival == "from_city_sewer_4_ladder" and yes.facing == "up"
    assert no.goto is None and no.dialogue is None and no.action is None

    directory, game, world = _game_and_world()
    try:
        runtime_trigger = world.choice_triggers[0]
        assert runtime_trigger.choice_id == "city_sewer_ladder"
        assert (runtime_trigger.width, runtime_trigger.height) == (
            config.TILE_SIZE, config.TILE_SIZE
        )
        world._arrival_fade_t = None
        # One tile below the authored foot is still approach space, not the
        # ladder itself, and must leave play uninterrupted.
        world.player.x = trigger[0] * config.TILE_SIZE + 3
        world.player.y = (trigger[1] + 1) * config.TILE_SIZE + 4
        world.update(0.0)
        assert game.scenes.current is world
        world.player.x = (
            runtime_trigger.x + runtime_trigger.width / 2
            - world.player.width / 2
        )
        world.player.y = (
            runtime_trigger.y + runtime_trigger.height / 2
            - world.player.height / 2
        )
        world.update(0.0)
        assert isinstance(game.scenes.current, DialogueScene)
        game.scenes.pop()

        world._on_choice(yes)
        world.update(0.0)
        assert game.scenes.current.map_name == "modern_city_day_1"
    finally:
        game._shutdown()
        directory.cleanup()


def test_sewer_3_leads_west_into_sewer_4_and_back() -> None:
    onward = AREA_WALK_EXITS[(SEWER_3, "⮜")]
    assert (onward.destination, onward.arrival) == (
        MAP_NAME, "from_city_sewer_3_west")
    back = AREA_WALK_EXITS[(MAP_NAME, "⮞")]
    assert (back.destination, back.arrival) == (SEWER_3, "from_city_sewer_4")

    entry = CHECKPOINT_BY_ID[MAP_NAME]
    assert (entry.display_name, entry.map_name) == ("City Sewer 4", MAP_NAME)
    assert entry.runtime_entry
    assert CHECKPOINT_BY_ID["modern_city_sewer_4_anchor"].saveable

    directory, game, world = _game_and_world(SEWER_3)
    try:
        world._arrival_fade_t = None
        west = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮜"
        )
        world.player.x = west[0] * config.TILE_SIZE
        world.player.y = west[1] * config.TILE_SIZE + 4
        world.update(0.0)
        assert world.map_name == MAP_NAME
        assert game.active_checkpoint_id == MAP_NAME
        world.update(0.0)
        assert world.map_name == MAP_NAME  # no bounce

        east = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.terrain_at(col, row) == "⮞"
        )
        world.player.x = east[0] * config.TILE_SIZE
        world.player.y = east[1] * config.TILE_SIZE + 4
        world.update(0.0)
        assert world.map_name == SEWER_3
        assert game.active_checkpoint_id == "modern_city_sewer_3_return"
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_last_tunnel_draws_and_respawns_at_its_own_ashtray() -> None:
    directory, game, world = _game_and_world("modern_city_sewer_4_anchor")
    try:
        assert world.city_rain is None
        assert all(rat.attack_chase_enabled for rat in world.rats)
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
        assert len(world.rats) == 4
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
    print("All City Sewer 4 tests passed.")


if __name__ == "__main__":
    _run_all()
