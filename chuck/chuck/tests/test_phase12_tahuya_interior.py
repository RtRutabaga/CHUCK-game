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
from src.entities.prop import (
    _PROP_FRAME_TIME, _PROP_FRAME_TIMES,
)
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
    COUCH_ROW, COUNTER_BOTTOM, COUNTER_TOP, DOOR_ROW, FLOOR_BOTTOM,
    FLOOR_ROWS, FLOOR_TOP, HEIGHT, WALL_BOTTOM, WALL_ROWS,
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
        "cabin_curtain_window": 2,
        "cabin_macrame": 1,
        "cabin_goose_mount": 1,
        "cabin_side_table": 1,
    }
    positions = {
        kind: (col, row) for kind, col, row in tilemap.prop_tiles
        if kind not in {"cabin_chair", "cabin_curtain_window"}
    }
    assert positions["cabin_big_couch"] == (5, COUCH_ROW)
    assert positions["cabin_couch"] == (15, COUCH_ROW)
    assert positions["cabin_table"] == (5, FLOOR_TOP - 1)
    assert positions["cabin_connector_shelf"] == (1, FLOOR_BOTTOM)
    assert positions["cabin_mini_fridge"] == (10, FLOOR_TOP - 1)
    assert positions["cabin_closed_door_west"] == (14, SEALED_DOOR_ROW)
    assert positions["cabin_kitchen"] == (5, COUNTER_BOTTOM)
    assert positions["cabin_woodstove"] == (16, FLOOR_TOP - 1)
    chair_positions = sorted(
        (col, row) for kind, col, row in tilemap.prop_tiles
        if kind == "cabin_chair"
    )
    # Both chairs are pushed flush against the east wall, so the seated
    # pair face west across the room rather than sitting in it.
    assert chair_positions == [(18, COUCH_ROW + 3), (18, COUCH_ROW + 6)]
    assert all(tilemap.is_solid(19, COUCH_ROW + step)
               for step in (1, 3, 6))

    # A door in the north wall between the couches that does not open,
    # curtains drawn on the wall behind each couch, and a lava lamp on
    # the one strip of floor between the stove and the east wall.
    assert positions["cabin_closed_door_north"] == (10, WALL_BOTTOM)
    assert positions["cabin_lava_lamp"] == (19, FLOOR_TOP - 2)
    # The knotted hanging goes on the panel to the right of the big
    # couch's window, between it and the door.
    assert positions["cabin_macrame"] == (8, WALL_BOTTOM)
    # The goose hangs on the west wall, on the stretch between the map
    # table below it and the couch above.
    goose = positions["cabin_goose_mount"]
    assert goose[0] == 1
    assert COUCH_ROW < goose[1] < FLOOR_TOP - 4
    # ...and it lies on its side, wider than it is tall, with its plaque
    # left of centre so the board lands on the wall rather than hanging
    # half over the carpet in front of it.
    image = pygame.image.load(str(
        config.SPRITES_DIR / "objects" / "cabin_goose_mount.png"
    ))
    width, height = image.get_size()
    assert width > height, image.get_size()
    opaque = [
        x for x in range(width)
        if any(image.get_at((x, y))[3] > 0 for y in range(height))
    ]
    assert min(opaque) == 0, min(opaque)
    # Props centre on their tile, so the empty columns on the right are
    # what carry the plaque left onto the wall.
    assert max(opaque) < width - 4, (max(opaque), width)
    windows = sorted((col, row) for kind, col, row in tilemap.prop_tiles
                     if kind == "cabin_curtain_window")
    # One centred behind each couch, hanging from the wall itself.
    assert windows == [(5, WALL_BOTTOM), (15, WALL_BOTTOM)]
    # ...and a side table east of the couch that moved west for it.
    assert positions["cabin_side_table"] == (19, COUCH_ROW)

    # The north wall is deep enough for what hangs on it. A one-row wall
    # clipped the tops of these off against the edge of the map and left
    # their bottoms sitting out on the carpet.
    assert WALL_ROWS >= 3
    for row in range(WALL_ROWS):
        assert all(tilemap.is_solid(col, row)
                   for col in range(tilemap.width_tiles)), row
    assert all(tilemap.terrain_at(col, WALL_ROWS) != "ć"
               for col in range(1, 13)), "the carpet starts below the wall"
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


def test_all_interior_routes_and_the_far_side_are_reachable() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    front = markers["arrival:from_front_door"]
    reachable = _flood(tilemap, front)
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


def test_shared_loader_and_the_interior_save_persists() -> None:
    entry = CHECKPOINT_BY_ID["tahuya_interior"]
    assert entry.display_name == "Cabin Interior"

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

        assert game.checkpoints.write_save(
            "tahuya_interior", sanity=world.sanity.current
        )
        record = game.checkpoints.saves.load()
        assert record is not None
        assert record.checkpoint_id == "tahuya_interior"
        continued = game.checkpoints.continue_game()
        assert continued.map_name == MAP_NAME
        assert game.active_checkpoint_id == "tahuya_interior"

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
        assert lamp.dialogue_id == "cabin_lava_lamp"
        # Every frame is different: blobs on one shared cycle would give
        # duplicate frames and a visible beat.
        # ...and it runs at its own pace, far slower than the fire it
        # stands beside: at the stove's frame rate the blobs shot up and
        # down like a boiling kettle.
        pace = _PROP_FRAME_TIMES["cabin_lava_lamp"]
        assert pace > _PROP_FRAME_TIME * 6, pace
        shots = []
        for _ in range(6):
            shots.append(pygame.image.tostring(lamp._image, "RGBA"))
            lamp.update(pace)
        assert len(set(shots)) == 6, len(set(shots))

        goose = next(prop for prop in world.props
                     if prop.kind == "cabin_goose_mount")
        assert goose.dialogue_id == "cabin_goose_mount"
        assert goose.choice_id is None
        # The joke is the whole point of it being there, so the line is
        # pinned. Written with three dots rather than an ellipsis
        # character, which is what every other line in the game uses.
        assert world.dialogue.get("cabin_goose_mount") == [
            "It's a mounted goose head... did it just wink?"
        ]

        curtains = [prop for prop in world.props
                    if prop.kind == "cabin_curtain_window"]
        assert len(curtains) == 2
        # Curtains are scenery: E says what they are, and nothing opens.
        assert all(prop.dialogue_id == "examine_cabin_curtain_window"
                   and prop.choice_id is None
                   for prop in curtains)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_room_answers_when_you_look_at_it() -> None:
    """Five things in the cabin have something to say about themselves.

    The cabin is a room to look at rather than walk through, so the
    fixtures that reward a look carry a line. The table keeps its line
    in both states -- the planar question belongs to the walk trigger,
    not to the prop -- so describing the map never competes with being
    asked whether to step into it.
    """
    expected = {
        "cabin_table": (
            "It looks like a map of the desert, there's some strange "
            "dice next to it"
        ),
        "cabin_mini_fridge": "it's softly humming",
        "cabin_lava_lamp":
            "Blobs move up and down the tube, it's hot to the touch",
        "cabin_woodstove": (
            "someone built this fire perfectly, each log is in the "
            "optimal spot"
        ),
        "cabin_macrame": (
            "it looks like it's supposed to be decorative, it "
            "depicts.... something? It's hairy and it has eyes"
        ),
    }
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("tahuya_interior")
        world._arrival_fade_t = None
        font = game.assets.bitmap_font()
        for kind, line in expected.items():
            prop = next(p for p in world.props if p.kind == kind)
            assert prop.dialogue_id is not None, kind
            assert prop.choice_id is None, kind
            assert world.dialogue.get(prop.dialogue_id) == [line], kind
            # Every line has to render: the box wraps, but a missing
            # glyph would come through as a hole rather than an error.
            assert font.render(line).get_bounding_rect().width > 0, kind
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_fridge_answers_for_itself_and_not_for_the_table() -> None:
    """Standing at the fridge asks the fridge.

    The map table is nine tiles wide and its interaction zone swallows
    the fridge parked at the end of it, so first-in-the-list gave the
    map's line to anyone walking up to the fridge's south side. The
    nearer of two overlapping targets is the one that answers.
    """
    from src.systems.interaction import find_target

    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("tahuya_interior")
        world._arrival_fade_t = None
        fridge = next(p for p in world.props if p.kind == "cabin_mini_fridge")
        table = next(p for p in world.props if p.kind == "cabin_table")
        from src.systems.interaction import rects_overlap

        fx, fy, fw, fh = fridge.interaction_bounds()
        # Chuck standing against the fridge's south face, looking north.
        box = (fx + fw / 2 - 6, fy + fh - 10, 12, 14)
        probe = (fx + fw / 2 - 4, fy + fh - 16, 8, 8)
        # The premise: he really is in reach of the table as well, so
        # this is a genuine tie for the old rule to have got wrong.
        assert rects_overlap(box, table.interaction_bounds())
        assert rects_overlap(box, fridge.interaction_bounds())

        assert find_target(probe, box, [], world.props) is fridge
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


def test_the_table_is_drawn_over_the_fridge_beside_it() -> None:
    """The long table's end, not the fridge's side.

    The fridge stands at the table's east end and both are wider than
    the tile they stand on, so one of them is drawn over the other.
    Sorted by their feet alone they tie, and the fridge won it -- the
    table's end cap disappeared into the fridge's side. A pixel of
    sort-lift stands the fridge a hair further back instead.
    """
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        world = game.checkpoints.load_checkpoint("tahuya_interior")
        table = next(prop for prop in world.props
                     if prop.kind.startswith("cabin_table"))
        fridge = next(prop for prop in world.props
                      if prop.kind == "cabin_mini_fridge")
        # They touch, which is why the order matters at all.
        assert table.interaction_bounds()[0] < fridge.interaction_bounds()[0]
        assert (table.interaction_bounds()[0]
                + table.interaction_bounds()[2]) > fridge.interaction_bounds()[0]
        assert fridge.sort_y < table.sort_y
        order = [prop.kind for prop in world._sorted_drawables()
                 if getattr(prop, "kind", None) in
                 (table.kind, "cabin_mini_fridge")]
        assert order.index("cabin_mini_fridge") < order.index(table.kind)
    finally:
        game._shutdown()
        directory.cleanup()
