"""Phase 12's first slice: real-place cabin grounds and shared entry."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.prop import Prop
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import MAP_TILESET, TAHUYA, tileset_for


import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from generate_tahuya_cabin_exterior import (
    DRIVEWAY_HALF, FIRE, FIRE_BAY_WIDTH, FOREST_EDGE, FOREST_SOLID,
    NORTH_BAY, NORTH_BAY_WIDTH, NORTH_TREE, _north_edge, _south_edge,
)


MAP_NAME = "tahuya_cabin_exterior"


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


def _game():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game


def test_dedicated_materials_and_real_place_landmarks_exist() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (80, 64)
    assert MAP_TILESET[MAP_NAME] == "tahuya"
    assert tileset_for(MAP_NAME) is TAHUYA

    terrain = Counter(char for row in tilemap._grid for char in row)
    for char in ("ᶠ", "♟", "⌇", "▣", "↟", "ᵿ"):
        assert terrain[char] > 0, char

    # The strip of astroturf from the reference photographs: laid on the
    # dirt at the foot of the cabin steps, straight-edged, and walked on
    # rather than walked around.
    turf = {(col, row)
            for row, line in enumerate(tilemap._grid)
            for col, char in enumerate(line) if char == "ᵿ"}
    assert len(turf) == 15, len(turf)
    columns = {col for col, _row in turf}
    rows = {row for _col, row in turf}
    assert columns == {57, 58, 59}
    assert rows == set(range(35, 40))
    assert all(not tilemap.is_solid(col, row) for col, row in turf)
    # It starts under the steps and stops short of the fire.
    assert min(rows) == 35 and max(rows) < FIRE[1]

    props = Counter(kind for kind, _col, _row in tilemap.prop_tiles)
    assert props["tahuya_ufo"] == 1
    assert props["tahuya_firepit"] == 1
    assert props["tahuya_firewood_shed"] == 1
    assert props["tahuya_cabin"] == 1
    assert props["tahuya_mushroom_light"] == 5
    assert props["tahuya_fir"] >= 100
    fir_positions = [
        (col, row) for kind, col, row in tilemap.prop_tiles
        if kind == "tahuya_fir"
    ]
    assert sum(7 <= col <= 43 for col, _row in fir_positions) >= 100
    # The authored stand is deterministic but not planted on a visible grid.
    assert len({col % 5 for col, _row in fir_positions}) == 5
    assert len({row % 5 for _col, row in fir_positions}) == 5
    light_positions = [
        (col, row) for kind, col, row in tilemap.prop_tiles
        if kind == "tahuya_mushroom_light"
    ]
    # The lit path turns in at the fire and stops there with it. It used
    # to run on south past the fire and off the bottom of the map, which
    # read as a way out that goes nowhere.
    assert light_positions == [
        (44, 13), (45, 20), (44, 27), (45, 34), (48, 39),
    ]
    fire_positions = [
        (col, row) for kind, col, row in tilemap.prop_tiles
        if kind == "tahuya_firepit"
    ]
    # The fire and the woodshed sit just south of the porch steps now,
    # not out at the far edge of the clearing.
    assert fire_positions == [(57, 43)]
    assert max(row for _col, row in light_positions) <= 43
    shed = [(col, row) for kind, col, row in tilemap.prop_tiles
            if kind == "tahuya_firewood_shed"]
    assert shed == [(70, 42)]
    assert len(_markers(tilemap)["breakable_grass"]) >= 6


def test_the_wood_opens_north_of_the_cabin_and_a_driveway_leaves_it() -> None:
    """The north side answers the south.

    A second bay above the cabin, the stand bowing round it on the same
    curve the fire bay uses, and a road's width of dirt out of the top
    of it -- which is how anyone got a cabin onto this ground at all.
    """
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")

    # Everything above the tree line in a column is closed forest, or
    # the track, or the ring of Sea the map ends in.
    for col in range(1, tilemap.width_tiles - 1):
        for row in range(1, _north_edge(col)):
            assert tilemap.is_solid(col, row) or tilemap.terrain_at(
                col, row) == "⌇", (col, row)
    # ...and the line bows away from the opening rather than running
    # straight across the top of the map.
    far = NORTH_BAY + NORTH_BAY_WIDTH + 4
    assert _north_edge(NORTH_BAY) + 4 < _north_edge(far) == NORTH_TREE

    drive = {(col, row)
             for row, line in enumerate(tilemap._grid)
             for col, char in enumerate(line)
             if char == "⌇" and row < NORTH_TREE}
    columns = {col for col, _row in drive}
    assert columns == set(range(NORTH_BAY - DRIVEWAY_HALF,
                                NORTH_BAY + DRIVEWAY_HALF + 1))
    assert len(columns) == 3, "a driveway is a road's width of dirt"
    # It runs up into the trees and stops short of the border, so it
    # goes out of sight rather than ending against the edge of the map.
    assert min(row for _col, row in drive) >= 2
    assert all(tilemap.is_solid(col, 1) for col in columns)

    # The circular object stands in the opening, west of the track.
    ufo = next((col, row) for kind, col, row in tilemap.prop_tiles
               if kind == "tahuya_ufo")
    assert ufo[0] < NORTH_BAY - DRIVEWAY_HALF
    assert _north_edge(ufo[0]) <= ufo[1] < NORTH_TREE + 6


def test_the_astral_sea_closes_the_map_on_every_side() -> None:
    """The ground ends in the Sea, the way it does everywhere else.

    One block is enough. The wood is already impassable well inside it,
    so this is never somewhere Chuck stands and looks at -- it is there
    so the map stops at something rather than at an invisible wall.
    """
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    width, height = tilemap.width_tiles, tilemap.height_tiles

    edge = [(col, 0) for col in range(width)]
    edge += [(col, height - 1) for col in range(width)]
    edge += [(0, row) for row in range(height)]
    edge += [(width - 1, row) for row in range(height)]
    for col, row in edge:
        assert tilemap.terrain_at(col, row) == "V", (col, row)

    # One block, and no deeper: the second ring in is still forest.
    assert tilemap.terrain_at(width // 2, 1) != "V"
    assert tilemap.terrain_at(1, height // 2) != "V"

    # ...and it is never reachable, which is why it can be this thin.
    markers = _markers(tilemap)
    reachable = _flood(tilemap, markers["arrival:from_doug_fir"][0])
    assert not any(point in reachable for point in edge)


def test_western_arrival_is_a_narrow_winding_footpath() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    path_rows = []
    for col in range(6, 41):
        rows = [row for row in range(26, 37)
                if tilemap.terrain_at(col, row) == "⌇"]
        assert 1 <= len(rows) <= 2, (col, rows)
        path_rows.append(round(sum(rows) / len(rows)))
    assert max(path_rows) - min(path_rows) >= 3


def test_sole_south_door_and_the_ashtray_are_reachable() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    markers = _markers(tilemap)
    reachable = _flood(tilemap, markers["arrival:from_doug_fir"][0])
    assert markers["anchor:tahuya_exterior_anchor"][0] in reachable

    for point in ((59, 31), (59, 33), (59, 44)):
        assert point in reachable, point
    # South of the fire is forest, not a corridor running off the map.
    # The trail ends at the fire circle and the stand closes over it --
    # but the line it closes on bows away from the fire, so the wood
    # opens out around it in a bay instead of stopping at it in a fence.
    for col in range(1, tilemap.width_tiles - 1):
        for row in range(_south_edge(col), tilemap.height_tiles - 1):
            assert tilemap.is_solid(col, row), (col, row)
    assert not any((col, row) in reachable
                   for col in range(1, tilemap.width_tiles - 1)
                   for row in range(_south_edge(col),
                                    tilemap.height_tiles - 1))

    far = FIRE[0] + FIRE_BAY_WIDTH + 4
    assert _south_edge(FIRE[0]) > _south_edge(far) + 4

    def open_rows(col):
        return sum(not tilemap.is_solid(col, row)
                   for row in range(FOREST_EDGE, tilemap.height_tiles))

    # ...and there is materially more standing room under the fire than
    # there is off to the side of it.
    assert open_rows(FIRE[0]) >= open_rows(far) + 4, (
        open_rows(FIRE[0]), open_rows(far)
    )
    assert all(tilemap.terrain_at(col, row) != "⌇"
               for row in range(FOREST_EDGE, tilemap.height_tiles)
               for col in range(tilemap.width_tiles))
    assert tilemap.terrain_at(59, 31) == "Ɛ"
    # Three tiles of doorway, not one: a single-tile door on a building
    # this size has to be lined up on before it will open.
    assert sum(char == "Ɛ" for row in tilemap._grid for char in row) == 3
    assert not any(char == "Ɣ" for row in tilemap._grid for char in row)
    assert markers["arrival:from_cabin_front"][0] == (59, 33)
    assert "arrival:from_cabin_back" not in markers
    assert not any(kind.startswith(("rat", "raccoon", "zombie", "skeleton"))
                   for kind, _position in tilemap.object_spawns)


def test_the_visible_south_door_enters_the_interior() -> None:
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("tahuya_exterior")
        world._arrival_fade_t = None
        world.player.x = 59 * config.TILE_SIZE + (
            config.TILE_SIZE - config.PLAYER_HITBOX_W
        ) / 2
        world.player.y = 31 * config.TILE_SIZE + (
            config.TILE_SIZE - config.PLAYER_HITBOX_H
        ) / 2
        world.update(1 / 60)
        assert world.map_name == "tahuya_cabin_interior"
    finally:
        game._shutdown()
        directory.cleanup()


def test_shared_checkpoint_loader_and_physical_ashtray_persist() -> None:
    entry = CHECKPOINT_BY_ID["tahuya_exterior"]
    anchor = CHECKPOINT_BY_ID["tahuya_exterior_anchor"]
    assert entry.display_name == "Cabin Exterior"
    assert entry.runtime_entry and not entry.saveable
    assert anchor.saveable and not anchor.development_visible

    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("tahuya_exterior", sanity=61)
        assert world.map_name == MAP_NAME
        assert world.player.facing == "right"
        assert world.sanity.current == 61
        assert game.progress.has("doug_fir_transition_completed")
        assert game.checkpoints.saves.load() is None

        assert game.checkpoints.activate_checkpoint(
            "tahuya_exterior_anchor", sanity=world.sanity.current
        )
        record = game.checkpoints.saves.load()
        assert record is not None
        assert record.checkpoint_id == "tahuya_exterior_anchor"
        continued = game.checkpoints.continue_game()
        assert continued.map_name == MAP_NAME
        assert game.active_checkpoint_id == "tahuya_exterior_anchor"

        continued._arrival_fade_t = None
        continued.player.x, continued.player.y = 120.0, 120.0
        continued.sanity.deplete()
        continued.update(config.RESPAWN_FADE_OUT + 0.01)
        continued.update(config.RESPAWN_HOLD + 0.01)
        assert continued._respawn_phase == "in"
        assert (continued.player.x, continued.player.y) == anchor.position
    finally:
        game._shutdown()
        directory.cleanup()


def test_mushroom_lights_have_stable_unsynchronised_phases() -> None:
    directory, game = _game()
    try:
        first = Prop("tahuya_mushroom_light", 44, 13, game.assets)
        second = Prop("tahuya_mushroom_light", 45, 20, game.assets)
        repeated = Prop("tahuya_mushroom_light", 44, 13, game.assets)
        firepit = Prop("tahuya_firepit", 59, 59, game.assets)
        ufo = Prop("tahuya_ufo", 18, 13, game.assets)
        cabin = Prop("tahuya_cabin", 62, 34, game.assets)
        assert first._animation_t != second._animation_t
        assert first._animation_t == repeated._animation_t
        assert len(first._frames) == 8
        assert firepit._size == (64, 56)
        assert len(firepit._frames) == 6
        assert ufo._size == (132, 76)
        # The cabin is a full gable-roofed landmark now, not a compact block.
        assert cabin._size == (370, 263)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_cabin_is_a_gable_landmark_and_collision_follows_it() -> None:
    """The cabin has to be a building, and the map has to agree with it.

    The old exterior was a compact block with a shallow roof, and its
    footprint was a hand-written rectangle. A gable-roofed building is
    not a rectangle -- the roof reaches further at the ridge than at the
    eaves -- so the two drifted apart whenever the art moved. The
    footprint is read back off the sprite's own alpha now, which is what
    this checks: every tile marked solid is one the cabin actually
    stands on, and every tile it stands on is solid.
    """
    from tools.generate_tahuya_cabin_exterior import (
        CABIN_COVERAGE, CABIN_TILE, _cabin_footprint,
    )

    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    mass, boards = _cabin_footprint()
    footprint = set(mass) | set(boards)
    assert len(footprint) >= 100, len(footprint)
    assert len(boards) >= 20, len(boards)

    walkable = {"▣", "↟", "Ɛ", "ኂ"}
    for row, col in footprint:
        char = tilemap._grid[row][col]
        assert tilemap.is_solid(col, row) or char in walkable, (col, row, char)
    # Boards are boards and mass is mass: nothing the cabin draws as
    # decking is solid, and no plank is left lying outside the drawing.
    for row, col in boards:
        assert not tilemap.is_solid(col, row), (col, row)
    planks = {(row, col)
              for row, line in enumerate(tilemap._grid)
              for col, char in enumerate(line) if char in {"▣", "↟"}}
    assert planks <= set(boards), sorted(planks - set(boards))[:6]

    # The silhouette steps rather than squaring off: a gable seen at an
    # angle is wider at the eaves than at the ridge.
    widths = {}
    for row, col in footprint:
        widths.setdefault(row, []).append(col)
    spans = {row: max(cols) - min(cols) + 1 for row, cols in widths.items()}
    assert len(set(spans.values())) >= 4, spans

    # The porch is walkable, the door is on it, and the steps come down
    # off it onto ground Chuck can stand on.
    assert tilemap.terrain_at(59, 31) == "Ɛ"
    for col in range(58, 61):
        assert tilemap.terrain_at(col, 31) == "Ɛ", col
    for col in range(57, 60):
        assert not tilemap.is_solid(col, 34), col
    assert CABIN_TILE == (62, 34) and 0.0 < CABIN_COVERAGE < 1.0


def test_the_wood_has_an_understory_and_it_is_still_walkable() -> None:
    """Firs on bare ground read as posts standing in a lawn.

    A Douglas-fir stand in this part of Washington has evergreen
    huckleberry and salal under it, so both are scattered through the
    wooded parts. They follow the trees rather than covering the map --
    a tile only gets brush if there is a fir within a couple of tiles --
    which is what keeps the clearing, the trail and the fire circle open
    without any of them having to be named as exclusions.
    """
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    props = Counter(kind for kind, _col, _row in tilemap.prop_tiles)
    assert props["tahuya_salal"] > 60, props["tahuya_salal"]
    assert props["tahuya_huckleberry"] > 60, props["tahuya_huckleberry"]

    brush = [(col, row) for kind, col, row in tilemap.prop_tiles
             if kind in {"tahuya_salal", "tahuya_huckleberry"}]
    firs = {(col, row) for kind, col, row in tilemap.prop_tiles
            if kind == "tahuya_fir"}
    for col, row in brush:
        # Under the trees, never out in the open.
        assert any((col + dx, row + dy) in firs
                   for dx in range(-2, 3) for dy in range(-2, 3)), (col, row)
        # Chuck is a foot tall and these are shrubs: he goes through
        # them. Solid brush this thick would fence off the whole wood.
        assert not tilemap.is_solid(col, row), (col, row)

    # The route in and the things on it are untouched by the planting.
    markers = _markers(tilemap)
    reachable = _flood(tilemap, markers["arrival:from_doug_fir"][0])
    assert markers["anchor:tahuya_exterior_anchor"][0] in reachable
    assert (59, 33) in reachable
    assert not any((col, row) in brush
                   for col, row in ((57, 43), (70, 42)))


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
    print("All Cabin exterior tests passed.")


if __name__ == "__main__":
    _run_all()
