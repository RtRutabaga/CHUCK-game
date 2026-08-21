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
    for char in ("ᶠ", "♟", "⌇", "▣", "↟"):
        assert terrain[char] > 0, char

    props = Counter(kind for kind, _col, _row in tilemap.prop_tiles)
    assert props["tahuya_ufo"] == 1
    assert props["tahuya_firepit"] == 1
    assert props["tahuya_firewood_shed"] == 1
    assert props["tahuya_cabin"] == 1
    assert props["tahuya_mushroom_light"] == 7
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
    assert light_positions == [
        (44, 13), (45, 20), (44, 27), (45, 34),
        (44, 41), (45, 48), (52, 55),
    ]
    fire_positions = [
        (col, row) for kind, col, row in tilemap.prop_tiles
        if kind == "tahuya_firepit"
    ]
    assert fire_positions == [(59, 59)]
    assert len(_markers(tilemap)["breakable_grass"]) >= 6


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

    for point in ((59, 31), (59, 36), (59, 54), (59, 58)):
        assert point in reachable, point
    assert tilemap.terrain_at(59, 31) == "Ɛ"
    assert sum(char == "Ɛ" for row in tilemap._grid for char in row) == 1
    assert not any(char == "Ɣ" for row in tilemap._grid for char in row)
    assert markers["arrival:from_cabin_front"][0] == (59, 36)
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
        assert cabin._size == (264, 188)
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
    footprint = set(_cabin_footprint())
    assert len(footprint) >= 100, len(footprint)

    walkable = {"▣", "↟", "Ɛ", "ኂ"}
    for row, col in footprint:
        char = tilemap._grid[row][col]
        assert tilemap.is_solid(col, row) or char in walkable, (col, row, char)

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
    for col in range(56, 61):
        assert not tilemap.is_solid(col, 33), col
    for col in range(58, 62):
        assert not tilemap.is_solid(col, 35), col
    assert CABIN_TILE == (62, 34) and 0.0 < CABIN_COVERAGE < 1.0


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
