"""Phase 6 first temple map, transition, art, music, and checkpoint."""

from collections import deque
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
    return TileMap(config.MAPS_DIR / "temple_entrance.txt")


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


def test_first_temple_map_is_connected_and_has_one_checkpoint() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (48, 37)
    reached = _flood(tilemap, (23, 33))
    assert (23, 2) in reached
    assert len(reached) >= 850

    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_temple_exterior") == 1
    assert kinds.count("anchor:temple_1_anchor") == 1
    assert kinds.count("boundary:temple_deeper") == 1
    assert not any(kind in {
        "zombie", "skeleton", "rat", "raptor", "massive_dinosaur",
    } for kind in kinds)
    assert sum(row.count("i") for row in tilemap._grid) == 10


def test_exterior_and_entrance_hall_connect_without_bouncing() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("chult_5")
        scene.player.x = 31 * config.TILE_SIZE + 3
        scene.player.y = 4 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_entrance"
        assert game.active_checkpoint_id == "temple_1"
        assert scene._player_tile() == (23, 33)
        scene.update(0.0)
        assert scene.map_name == "temple_entrance"

        scene.player.x = 23 * config.TILE_SIZE + 3
        scene.player.y = 35 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "chult_temple"
        assert game.active_checkpoint_id == "chult_temple_return"
        assert scene._player_tile() == (31, 5)
        scene.update(0.0)
        assert scene.map_name == "chult_temple"
    finally:
        game._shutdown()


def test_temple_1_ashtray_saves_continues_and_respawns() -> None:
    entry = CHECKPOINT_BY_ID["temple_1"]
    assert entry.display_name == "Temple 1"
    assert entry.map_name == "temple_entrance"
    assert entry.arrival == "from_temple_exterior"
    assert entry.runtime_entry and entry.development_visible

    anchor_entry = CHECKPOINT_BY_ID["temple_1_anchor"]
    assert anchor_entry.position == (372.0, 501.0)
    assert anchor_entry.saveable and not anchor_entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("temple_1")
        anchor, = scene.anchors
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.sanity.current = 61
        scene.update(0.01)
        assert game.active_checkpoint_id == "temple_1_anchor"
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert (scene.player.x, scene.player.y) == (anchor.x, anchor.y)
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == "temple_entrance"
        assert resumed.active_checkpoint_id == "temple_1_anchor"
        assert scene.sanity.current == 61
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_temple_has_dedicated_art_music_and_map_2_boundary() -> None:
    tileset = tileset_for("temple_entrance")
    assert tileset.sheet == "temple.png"
    assert tileset.char_to_terrain == {
        "·": "temple_floor", "█": "temple_wall",
        "Δ": "temple_doorway", "∇": "temple_doorway",
        "♠": "temple_spikes", "i": "temple_torch",
        "W": "temple_dart_wall",
        "V": "astral_void",
    }
    assert (config.TILESETS_DIR / tileset.sheet).is_file()
    assert AREA_MUSIC["temple_entrance"] == "temple.wav"
    assert (config.MUSIC_DIR / "temple.wav").is_file()
    assert AREA_WALK_EXITS[("temple_entrance", "∇")].destination == (
        "temple_spikes"
    )
    assert AREA_WALK_EXITS[("temple_entrance", "Δ")].destination == (
        "chult_temple"
    )


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 6 temple-entrance tests passed.")


if __name__ == "__main__":
    _run_all()
