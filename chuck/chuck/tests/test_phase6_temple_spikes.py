"""Phase 6 Temple Map 2 spike corridor and shared checkpoint flow."""

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
    return TileMap(config.MAPS_DIR / "temple_spikes.txt")


def _flood(tilemap: TileMap, start: tuple[int, int],
           blocked: frozenset = frozenset()) -> set[tuple[int, int]]:
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if (point not in reached and point not in blocked
                    and not tilemap.is_solid(*point)):
                reached.add(point)
                frontier.append(point)
    return reached


def test_spike_corridor_has_five_jump_bands_skeletons_and_one_ashtray() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (48, 44)
    spikes = {(col, row) for row, line in enumerate(tilemap._grid)
              for col, char in enumerate(line) if char == "♠"}
    assert spikes == {
        (col, row) for row in (6, 12, 18, 24, 30)
        for col in range(14, 34)
    }
    # Spikes are walkable fall hazards now (session 124): stepping on a
    # band on foot is the Astral fall, so SAFE on-foot progress cannot
    # pass even the first band — the committed jump remains the answer.
    from src.systems.fall import fall_zone_kind

    class Box:
        x = 23 * config.TILE_SIZE + 3
        y = 30 * config.TILE_SIZE + 4
        width = config.PLAYER_HITBOX_W
        height = config.PLAYER_HITBOX_H

    assert not tilemap.is_solid(23, 30)
    assert fall_zone_kind(tilemap, Box(), airborne=False) == "astral"
    assert fall_zone_kind(tilemap, Box(), airborne=True) is None
    safe_reached = _flood(tilemap, (23, 40), blocked=spikes)
    assert (23, 31) in safe_reached
    assert (23, 29) not in safe_reached

    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_temple_1") == 1
    assert kinds.count("anchor:temple_2_anchor") == 1
    assert kinds.count("boundary:temple_3") == 1
    assert kinds.count("skeleton") == 5
    assert sum(row.count("i") for row in tilemap._grid) == 14
    assert not any(kind in {
        "zombie", "rat", "raptor", "massive_dinosaur",
    } for kind in kinds)

    skeleton_rows = {
        int(y // config.TILE_SIZE)
        for kind, (_x, y) in tilemap.object_spawns if kind == "skeleton"
    }
    assert skeleton_rows == {9, 15, 21, 27, 34}


def test_temple_maps_connect_both_ways_without_bounce_or_music_restart() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_1")
        scene.player.x = 23 * config.TILE_SIZE + 3
        scene.player.y = 2 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_spikes"
        assert game.active_checkpoint_id == "temple_2"
        assert scene._player_tile() == (23, 40)
        assert AREA_MUSIC["temple_entrance"] == AREA_MUSIC["temple_spikes"]
        scene.update(0.0)
        assert scene.map_name == "temple_spikes"

        scene.player.x = 23 * config.TILE_SIZE + 3
        scene.player.y = 42 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_entrance"
        assert game.active_checkpoint_id == "temple_1_return"
        assert scene._player_tile() == (23, 3)
        scene.update(0.0)
        assert scene.map_name == "temple_entrance"
    finally:
        game._shutdown()


def test_temple_2_ashtray_saves_continues_and_respawns() -> None:
    entry = CHECKPOINT_BY_ID["temple_2"]
    assert entry.display_name == "Temple 2"
    assert entry.map_name == "temple_spikes"
    assert entry.arrival == "from_temple_1"
    assert entry.runtime_entry and entry.development_visible
    anchor_entry = CHECKPOINT_BY_ID["temple_2_anchor"]
    assert anchor_entry.position == (372.0, 613.0)
    assert anchor_entry.saveable and not anchor_entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("temple_2")
        assert len(scene.undead) == 5
        anchor, = scene.anchors
        came_in = scene.anchors_system.respawn_position_for_chuck()
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.sanity.current = 64
        scene.update(0.01)
        assert game.active_checkpoint_id == "temple_2_anchor"
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        # The door he came in by, not the Ashtray he touched.
        assert (scene.player.x, scene.player.y) == came_in
        assert len(scene.undead) == 5
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == "temple_spikes"
        assert resumed.active_checkpoint_id == "temple_2_anchor"
        assert scene.sanity.current == 64
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_spikes_use_temple_art_and_north_boundary_enters_map_3() -> None:
    tileset = tileset_for("temple_spikes")
    assert tileset.sheet == "temple.png"
    assert tileset.char_to_terrain["♠"] == "temple_spikes"
    assert tileset.char_to_terrain["i"] == "temple_torch"
    assert AREA_MUSIC["temple_spikes"] == "temple.wav"
    assert AREA_WALK_EXITS[("temple_spikes", "∇")].destination == (
        "temple_skeletons"
    )
    assert AREA_WALK_EXITS[("temple_spikes", "Δ")].destination == (
        "temple_entrance"
    )


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 6 temple-spike tests passed.")


if __name__ == "__main__":
    _run_all()
