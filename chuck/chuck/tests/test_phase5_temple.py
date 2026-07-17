"""Phase 5 Chult Map 5 temple exterior and phase boundary."""

from collections import Counter, deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / "chult_temple.txt")


def _flood(tilemap: TileMap, start: tuple[int, int]) -> set[tuple[int, int]]:
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point not in reached and not tilemap.is_solid(*point):
                reached.add(point)
                frontier.append(point)
    return reached


def test_temple_map_is_a_connected_enemy_free_exterior() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (64, 48)
    reached = _flood(tilemap, (32, 45))
    assert (31, 4) in reached

    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert not any(kind in {
        "zombie", "skeleton", "raptor", "massive_dinosaur",
    } or kind.startswith("staged_undead:") for kind in kinds)
    assert kinds.count("breakable_grass") == 8
    assert kinds.count("anchor:chult_5_anchor") == 1
    assert kinds.count("arrival:from_chult_4") == 1
    assert kinds.count("boundary:temple_interior") == 1


def test_pyramid_is_large_stepped_and_has_a_broad_readable_stair() -> None:
    tilemap = _map()
    counts = Counter("".join(tilemap._grid))
    assert counts["π"] == 468
    assert counts["τ"] == 110
    assert counts["Ω"] == 4

    bands = ((4, 6, 23, 40), (7, 10, 20, 43),
             (11, 14, 17, 46), (15, 18, 14, 49),
             (19, 22, 11, 52))
    previous_width = 0
    for row0, row1, left, right in bands:
        width = right - left + 1
        assert width > previous_width
        previous_width = width
        for row in range(row0, row1 + 1):
            assert tilemap.terrain_at(left, row) == "π"
            assert tilemap.terrain_at(right, row) == "π"
            assert all(tilemap.terrain_at(col, row) in {"τ", "Ω"}
                       for col in range(29, 35))

    tileset = tileset_for("chult_temple")
    assert tileset.char_to_terrain["π"] == "temple_stone"
    assert tileset.char_to_terrain["τ"] == "temple_stairs"
    assert tileset.char_to_terrain["Ω"] == "temple_entrance"


def test_map_4_boundary_enters_named_chult_5_arrival_without_bounce() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("chult_4")
        scene.player.x = 54 * config.TILE_SIZE + 3
        scene.player.y = 1 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "chult_temple"
        assert game.active_checkpoint_id == "chult_5"
        assert scene._player_tile() == (32, 45)
        scene.update(0.0)
        assert scene.map_name == "chult_temple"
    finally:
        game._shutdown()


def test_chult_5_ashtray_saves_continue_and_respawns_through_shared_loader() -> None:
    entry = CHECKPOINT_BY_ID["chult_5"]
    assert entry.display_name == "Chult 5"
    assert entry.map_name == "chult_temple"
    assert entry.arrival == "from_chult_4"
    assert entry.runtime_entry and entry.development_visible
    anchor_entry = CHECKPOINT_BY_ID["chult_5_anchor"]
    assert anchor_entry.position == (436.0, 693.0)
    assert anchor_entry.saveable and not anchor_entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("chult_5")
        anchor, = scene.anchors
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.sanity.current = 53
        scene.update(0.01)
        assert game.active_checkpoint_id == "chult_5_anchor"
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert (scene.player.x, scene.player.y) == (anchor.x, anchor.y)
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == "chult_temple"
        assert resumed.active_checkpoint_id == "chult_5_anchor"
        assert (scene.player.x, scene.player.y) == (436.0, 693.0)
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_temple_entrance_is_a_stable_inert_next_phase_boundary() -> None:
    tilemap = _map()
    boundaries = [entry for entry in tilemap.object_spawns
                  if entry[0].startswith("boundary:")]
    assert boundaries == [("boundary:temple_interior", (504.0, 72.0))]
    assert tilemap.terrain_at(31, 4) == "Ω"
    assert ("chult_temple", "Ω") not in AREA_WALK_EXITS
    assert AREA_MUSIC["chult_temple"] == "chult.wav"


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 5 temple-exterior tests passed.")


if __name__ == "__main__":
    _run_all()
