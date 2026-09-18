"""Phase 6 Temple Map 4 dart-wall connector and checkpoint flow."""

from collections import deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.systems import save_code
from src.core.game import Game
from src.entities.dart_trap import DartTrap, TempleDart
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / "temple_darts.txt")


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


def test_dart_connector_is_long_torch_lit_and_enemy_free() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (72, 24)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("dart_trap:down") == 4
    assert kinds.count("dart_trap:up") == 4
    assert kinds.count("arrival:from_temple_3") == 1
    assert kinds.count("boundary:temple_5") == 1
    assert sum(row.count("i") for row in tilemap._grid) == 11
    assert sum(row.count("W") for row in tilemap._grid) == 8
    assert not any(kind in {
        "zombie", "skeleton", "rat", "raptor", "massive_dinosaur",
    } for kind in kinds)
    assert (2, 11) in _flood(tilemap, (63, 11))


def test_darts_fire_move_hit_and_stop_at_masonry() -> None:
    tilemap = _map()
    trap = DartTrap(15 * 16 + 8, 7 * 16 + 8, "down")
    dart = None
    for _ in range(180):
        dart = trap.update(1.0 / 60.0)
        if dart is not None:
            break
    assert dart is not None and dart.direction == "down"
    start_y = dart.y
    dart.update(0.1, tilemap)
    assert dart.alive and dart.y > start_y
    for _ in range(180):
        dart.update(1.0 / 60.0, tilemap)
        if not dart.alive:
            break
    assert not dart.alive

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_4")
        scene._arrival_fade_t = None
        before = scene.sanity.current
        player_box = scene.player.hitbox
        scene.darts.append(TempleDart(player_box.centerx, player_box.centery,
                                      "left"))
        scene.update(0.0)
        assert scene.sanity.current == before - config.DART_SANITY_DAMAGE
        assert not scene.darts
    finally:
        game._shutdown()


def test_temple_maps_3_and_4_connect_both_ways_without_bounce() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_3")
        scene.player.x = 2 * config.TILE_SIZE + 3
        scene.player.y = 20 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_darts"
        assert game.active_checkpoint_id == "temple_4"
        assert scene._player_tile() == (63, 11)
        assert AREA_MUSIC["temple_skeletons"] == AREA_MUSIC["temple_darts"]
        scene.update(0.0)
        assert scene.map_name == "temple_darts"

        scene.player.x = 68 * config.TILE_SIZE + 3
        scene.player.y = 11 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_skeletons"
        assert game.active_checkpoint_id == "temple_3_return"
        assert scene._player_tile() == (9, 20)
        scene.update(0.0)
        assert scene.map_name == "temple_skeletons"
    finally:
        game._shutdown()


def test_temple_4_save_continues_and_resets_darts() -> None:
    entry = CHECKPOINT_BY_ID["temple_4"]
    assert entry.display_name == "Temple 4"
    assert entry.map_name == "temple_darts"
    assert entry.arrival == "from_temple_3"
    assert entry.runtime_entry and entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("temple_4")
        scene._arrival_fade_t = None
        assert len(scene.dart_traps) == 8
        for _ in range(120):
            scene.update(1.0 / 60.0)
            if scene.darts:
                break
        assert scene.darts
        came_in = scene.respawn.position_for_chuck()
        scene.sanity.current = 62
        # The save the menu banks, at the door he came in by.
        code = save_code.for_display(
            game.checkpoints.save_here("temple_4", scene.sanity.current))
        assert game.active_checkpoint_id == "temple_4"
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        # The door he came in by.
        assert (scene.player.x, scene.player.y) == came_in
        assert len(scene.dart_traps) == 8 and not scene.darts
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.resume_from(save_code.decode(code))
        assert scene.map_name == "temple_darts"
        assert resumed.active_checkpoint_id == "temple_4"
        # A code does not carry sanity.
        assert scene.sanity.current == config.SANITY_START
        assert len(scene.dart_traps) == 8 and not scene.darts
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_dart_room_uses_temple_art_and_has_stable_west_boundary() -> None:
    tileset = tileset_for("temple_darts")
    assert tileset.sheet == "temple.png"
    assert tileset.char_to_terrain["W"] == "temple_dart_wall"
    assert AREA_MUSIC["temple_darts"] == "temple.wav"
    assert AREA_WALK_EXITS[("temple_darts", "∇")].destination == (
        "temple_snakes"
    )
    assert AREA_WALK_EXITS[("temple_darts", "Δ")].destination == (
        "temple_skeletons"
    )


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 6 temple-dart tests passed.")


if __name__ == "__main__":
    _run_all()
