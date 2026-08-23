"""Phase 12's authored Cabin interior and reversible thresholds."""

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
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import MAP_TILESET, TAHUYA, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from generate_cabin_interior_objects import (
    CONNECTOR_SHELF_SIZE, CONNECTOR_SHELF_TILES,
)
from generate_tahuya_cabin_interior import (
    COUNTER_BOTTOM, COUNTER_TOP, DOOR_ROW, FLOOR_BOTTOM, FLOOR_ROWS,
    FLOOR_TOP, HEIGHT,
)


SEALED_DOOR_ROW = (FLOOR_TOP + 1 + COUNTER_BOTTOM) // 2
MAP_NAME = "tahuya_cabin_interior"


def _markers(tilemap):
    return {
        kind: (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
        for kind, (x, y) in tilemap.object_spawns
    }


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


def _game():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game


def test_interior_matches_the_authored_long_cabin_layout() -> None:
    """Measured off the generator, not written out again here.

    The hardwood room's depth is one number in
    `generate_tahuya_cabin_interior`, and the sink, the sealed room, the
    doorway, the arrival and the west counter are all placed from it. If
    this test restated their rows as literals it would only ever record
    where they happened to be the last time somebody moved the wall.
    """
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (21, HEIGHT)
    assert MAP_TILESET[MAP_NAME] == "tahuya"
    assert tileset_for(MAP_NAME) is TAHUYA
    assert AREA_MUSIC[MAP_NAME] == "cabin.wav"

    terrain = Counter(char for row in tilemap._grid for char in row)
    assert terrain["Ħ"] > 0 and terrain["Ŀ"] > 0
    assert terrain["Ƃ"] == 0
    assert terrain["ć"] >= 2 * 21 + 2 * HEIGHT - 4
    assert tilemap.terrain_at(10, 0) == "ć"
    assert tilemap.terrain_at(10, HEIGHT - 1) == "Ɯ"
    assert all(tilemap.terrain_at(x, 0) == "ć" for x in range(9, 12))
    assert all(tilemap.terrain_at(x, y) == "Ɯ"
               for y in (DOOR_ROW, DOOR_ROW + 1) for x in range(9, 12))

    props = Counter(kind for kind, _col, _row in tilemap.prop_tiles)
    assert props == {
        "cabin_big_couch": 1,
        "cabin_couch": 1,
        "cabin_chair": 2,
        "cabin_table": 1,
        "cabin_connector_shelf": 1,
        "cabin_mini_fridge": 1,
        "cabin_closed_door_west": 1,
        "cabin_kitchen": 1,
        "cabin_woodstove": 1,
        "cabin_closed_door_north": 1,
        "cabin_lava_lamp": 1,
        "cabin_curtain_window": 4,
    }
    positions = {
        kind: (col, row) for kind, col, row in tilemap.prop_tiles
        if kind not in {"cabin_chair", "cabin_curtain_window"}
    }
    assert positions["cabin_big_couch"] == (5, 3)
    assert positions["cabin_couch"] == (16, 3)
    assert positions["cabin_table"] == (5, 13)
    assert positions["cabin_connector_shelf"] == (1, FLOOR_BOTTOM)
    assert positions["cabin_mini_fridge"] == (10, 13)
    assert positions["cabin_closed_door_west"] == (14, SEALED_DOOR_ROW)
    assert positions["cabin_kitchen"] == (5, COUNTER_BOTTOM)
    assert positions["cabin_woodstove"] == (16, 13)
    chair_positions = sorted(
        (col, row) for kind, col, row in tilemap.prop_tiles
        if kind == "cabin_chair"
    )
    # Both chairs are pushed flush against the east wall, so the seated
    # pair face west across the room rather than sitting in it.
    assert chair_positions == [(18, 6), (18, 9)]
    assert all(tilemap.is_solid(19, row) for row in (4, 6, 9))

    # A door in the north wall between the couches that does not open,
    # curtains drawn on the wall behind each couch, and a lava lamp on
    # the one strip of floor between the stove and the east wall.
    assert positions["cabin_closed_door_north"] == (10, 2)
    assert positions["cabin_lava_lamp"] == (19, 12)
    windows = sorted((col, row) for kind, col, row in tilemap.prop_tiles
                     if kind == "cabin_curtain_window")
    assert windows == [(3, 1), (7, 1), (14, 1), (18, 1)]
    # Two behind each couch, and above it: the tops have to show over
    # the couch back or there is no point drawing them.
    assert all(row < 3 for _col, row in windows)
    # Entities and stove sit on green carpet; the southern working area is
    # hardwood, with the counter visually flush against the south wall.
    assert all(tilemap.terrain_at(x, y) != "Ħ"
               for y in range(1, FLOOR_TOP) for x in range(1, 20))
    assert tilemap.terrain_at(5, COUNTER_TOP + 1) == "ħ"
    # Six rows of floor between the fire and the sink, not eleven: the
    # two halves of the cabin have to be visible at the same time.
    assert FLOOR_ROWS == 6
    assert COUNTER_TOP - FLOOR_TOP == FLOOR_ROWS
    # The southeast room is a complete enclosed section, not a prop-sized box.
    top, bottom = FLOOR_TOP + 1, COUNTER_BOTTOM
    assert all(tilemap.terrain_at(x, top) == "ć" for x in range(14, 20))
    assert all(tilemap.terrain_at(x, bottom) == "ć" for x in range(14, 20))
    assert all(tilemap.terrain_at(14, y) in {"ć", "ƚ"}
               for y in range(top, bottom))
    assert all(tilemap.terrain_at(19, y) == "ć" for y in range(top, bottom))
    assert all(tilemap.terrain_at(x, y) == "◼"
               for y in range(top + 1, bottom) for x in range(15, 19))


def test_all_interior_routes_and_the_ashtray_are_reachable() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    front = markers["arrival:from_front_door"]
    anchor = markers["anchor:tahuya_interior_anchor"]
    reachable = _flood(tilemap, front)
    assert anchor in reachable
    assert (10, 0) not in reachable and (10, HEIGHT - 1) in reachable
    assert "arrival:from_back_door" not in markers
    # The long table's visual and solid footprints agree, leaving a generous
    # route into the complete north living section.
    assert all(not tilemap.is_solid(x, y)
               for y in range(10, 14) for x in range(12, 15))
    # The fridge sprite is wider than one tile, but must not leave an invisible
    # collision cell on its east side that blocks this southbound approach.
    assert all(not tilemap.is_solid(11, y) for y in range(12, 15))
    # The horseshoe's west arm hugs the wall from the table to the sink; it
    # cannot consume the open room or the repaired north passage.
    assert all(tilemap.is_solid(x, y)
               for y in range(FLOOR_TOP, FLOOR_BOTTOM + 1)
               for x in range(1, 3))
    assert all(not tilemap.is_solid(3, y)
               for y in range(FLOOR_TOP, FLOOR_BOTTOM + 1))
    assert not any(kind.startswith(("rat", "raccoon", "zombie", "skeleton"))
                   for kind, _position in tilemap.object_spawns)


def test_sole_south_threshold_is_reversible_and_aligned() -> None:
    assert not TILE_DEFS["Ɛ"].solid
    assert not TILE_DEFS["Ɯ"].solid
    front_in = AREA_WALK_EXITS[("tahuya_cabin_exterior", "Ɛ")]
    front_out = AREA_WALK_EXITS[(MAP_NAME, "Ɯ")]
    assert (front_in.destination, front_in.arrival, front_in.facing) == (
        MAP_NAME, "from_front_door", "up"
    )
    assert (front_out.destination, front_out.arrival, front_out.facing) == (
        "tahuya_cabin_exterior", "from_cabin_front", "down"
    )
    assert ("tahuya_cabin_exterior", "Ɣ") not in AREA_WALK_EXITS
    assert (MAP_NAME, "Ƣ") not in AREA_WALK_EXITS


def test_shared_loader_and_interior_ashtray_persist() -> None:
    entry = CHECKPOINT_BY_ID["tahuya_interior"]
    anchor = CHECKPOINT_BY_ID["tahuya_interior_anchor"]
    assert entry.display_name == "Cabin Interior"
    assert entry.runtime_entry and not entry.saveable
    assert anchor.saveable and not anchor.development_visible

    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("tahuya_interior", sanity=73)
        assert world.map_name == MAP_NAME
        assert world.player.facing == "up"
        assert world.sanity.current == 73
        assert game.checkpoints.saves.load() is None
        stove = next(prop for prop in world.props
                     if prop.kind == "cabin_woodstove")
        assert stove._size == (72, 82)
        assert len(stove._frames) == 6
        shelf = next(prop for prop in world.props
                     if prop.kind == "cabin_connector_shelf")
        # The counter runs the whole west side of the hardwood room, so
        # its sprite is exactly as tall as the room is deep. Shrinking
        # the room without shrinking this left the cabinet standing up
        # through the carpet and across the map table.
        assert shelf._size == CONNECTOR_SHELF_SIZE
        assert CONNECTOR_SHELF_TILES == FLOOR_ROWS
        fridge = next(prop for prop in world.props
                      if prop.kind == "cabin_mini_fridge")
        assert fridge._size == (32, 42)
        closed_door = next(prop for prop in world.props
                           if prop.kind == "cabin_closed_door_west")
        assert closed_door.dialogue_id == "closed_door"

        assert game.checkpoints.activate_checkpoint(
            "tahuya_interior_anchor", sanity=world.sanity.current
        )
        record = game.checkpoints.saves.load()
        assert record is not None
        assert record.checkpoint_id == "tahuya_interior_anchor"
        continued = game.checkpoints.continue_game()
        assert continued.map_name == MAP_NAME
        assert game.active_checkpoint_id == "tahuya_interior_anchor"

    finally:
        game._shutdown()
        directory.cleanup()


def test_the_north_door_is_shut_and_the_lamp_is_the_only_thing_moving() -> None:
    """Two pieces of furnishing that carry a rule between them.

    The north door exists to be closed: it uses the same interaction the
    cabin's other closed door does, so both say the same thing rather
    than one of them growing its own line. The lava lamp is the only
    animated thing in the room now that the stove has company, and its
    blobs run on separate cycles so it never reads as a pulse.
    """
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("tahuya_interior")
        world._arrival_fade_t = None

        door = next(prop for prop in world.props
                    if prop.kind == "cabin_closed_door_north")
        west = next(prop for prop in world.props
                    if prop.kind == "cabin_closed_door_west")
        assert door.dialogue_id == west.dialogue_id == "closed_door"
        assert door.choice_id is None
        assert world.dialogue.get("closed_door") == ["it's closed"]

        lamp = next(prop for prop in world.props
                    if prop.kind == "cabin_lava_lamp")
        assert len(lamp._frames) == 6
        assert lamp.dialogue_id is None
        # Every frame is different: blobs on one shared cycle would give
        # duplicate frames and a visible beat.
        shots = []
        for _ in range(6):
            shots.append(pygame.image.tostring(lamp._image, "RGBA"))
            lamp.update(0.15)
        assert len(set(shots)) == 6, len(set(shots))

        curtains = [prop for prop in world.props
                    if prop.kind == "cabin_curtain_window"]
        assert len(curtains) == 4
        # Curtains are scenery, not something to talk to or open.
        assert all(prop.dialogue_id is None and prop.choice_id is None
                   for prop in curtains)
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
    print("All Cabin interior tests passed.")


if __name__ == "__main__":
    _run_all()
