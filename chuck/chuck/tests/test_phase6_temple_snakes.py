"""Phase 6 Temple Map 5 one-hit snake chamber and checkpoint flow."""

from collections import deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.snake import TempleSnake
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.combat import scratch_first_target
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / "temple_snakes.txt")


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


def test_snake_chamber_is_broad_torch_lit_and_routes_south() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (60, 44)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("snake") == 20
    assert kinds.count("anchor:temple_5_anchor") == 1
    assert kinds.count("arrival:from_temple_4") == 1
    assert kinds.count("boundary:temple_6") == 1
    assert sum(row.count("i") for row in tilemap._grid) == 18
    reached = _flood(tilemap, (51, 14))
    assert (17, 40) in reached
    assert all(kind not in {"zombie", "skeleton", "raptor"} for kind in kinds)


def test_snake_is_small_mobile_and_defeated_by_one_scratch() -> None:
    tilemap = _map()
    snake = TempleSnake(20 * 16 + 8, 15 * 16 + 8)
    assert snake.max_scratches == 1
    assert snake.width < config.UNDEAD_FRAME_W
    snake.tilemap = tilemap

    class Target:
        x = snake.x + 40
        y = snake.y
        width = config.PLAYER_HITBOX_W
        height = config.PLAYER_HITBOX_H

    start = snake.x
    snake.update(0.25, Target())
    assert snake.x > start
    assert scratch_first_target(snake.hitbox.inflate(2, 2), [snake])
    assert not snake.alive


def test_maps_4_and_5_connect_both_ways_without_bounce() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_4")
        scene._arrival_fade_t = None
        scene.player.x = 2 * config.TILE_SIZE + 3
        scene.player.y = 11 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_snakes"
        assert game.active_checkpoint_id == "temple_5"
        assert scene._player_tile() == (51, 14)
        assert len(scene.snakes) == 20
        scene.update(0.0)
        assert scene.map_name == "temple_snakes"

        scene.player.x = 56 * config.TILE_SIZE + 3
        scene.player.y = 14 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_darts"
        assert game.active_checkpoint_id == "temple_4_return"
        assert scene._player_tile() == (7, 11)
        scene.update(0.0)
        assert scene.map_name == "temple_darts"
    finally:
        game._shutdown()


def test_temple_5_checkpoint_saves_continues_and_resets_snakes() -> None:
    entry = CHECKPOINT_BY_ID["temple_5"]
    assert entry.display_name == "Temple 5"
    assert entry.map_name == "temple_snakes"
    assert entry.arrival == "from_temple_4"
    assert entry.runtime_entry and entry.development_visible
    anchor_entry = CHECKPOINT_BY_ID["temple_5_anchor"]
    assert anchor_entry.position == (788.0, 293.0)
    assert anchor_entry.saveable and not anchor_entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("temple_5")
        scene._arrival_fade_t = None
        anchor, = scene.anchors
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.sanity.current = 67
        scene.update(0.01)
        assert game.active_checkpoint_id == "temple_5_anchor"
        scene.snakes[0].alive = False
        scene.snakes = []
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert (scene.player.x, scene.player.y) == (anchor.x, anchor.y)
        assert len(scene.snakes) == 20
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == "temple_snakes"
        assert resumed.active_checkpoint_id == "temple_5_anchor"
        assert scene.sanity.current == 67
        assert len(scene.snakes) == 20
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_snake_room_uses_temple_identity_and_holds_future_exit() -> None:
    assert tileset_for("temple_snakes").sheet == "temple.png"
    assert AREA_MUSIC["temple_snakes"] == "temple.wav"
    assert AREA_MUSIC["temple_snakes"] == AREA_MUSIC["temple_darts"]
    assert ("temple_snakes", "∇") not in AREA_WALK_EXITS
    assert AREA_WALK_EXITS[("temple_snakes", "Δ")].destination == (
        "temple_darts"
    )


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 6 temple-snake tests passed.")


if __name__ == "__main__":
    _run_all()
