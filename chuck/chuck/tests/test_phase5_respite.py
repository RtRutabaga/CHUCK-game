"""Phase 5 Chuck-sized escape and low-pressure Chult Map 4 respite."""

from collections import deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.player import Player
from src.entities.undead import UndeadEnemy
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world import collision
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


class StillInput:
    def __init__(self):
        self.press_jump = False
        self.movement = (0.0, 0.0)

    def was_pressed(self, _action):
        pressed = _action == "jump" and self.press_jump
        self.press_jump = False
        return pressed

    def movement_vector(self):
        return self.movement


def _map(name: str) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _flood(tilemap: TileMap, start: tuple[int, int]) -> set:
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


def _distance(tilemap: TileMap, start: tuple[int, int], goal: tuple[int, int]):
    reached = {start}
    frontier = deque([(start, 0)])
    while frontier:
        point, distance = frontier.popleft()
        if point == goal:
            return distance
        col, row = point
        for neighbor in ((col - 1, row), (col + 1, row),
                         (col, row - 1), (col, row + 1)):
            if neighbor not in reached and not tilemap.is_solid(*neighbor):
                reached.add(neighbor)
                frontier.append((neighbor, distance + 1))
    return None


def test_map_3_escape_is_readable_and_only_chuck_can_cross() -> None:
    tilemap = _map("chult_run")
    tunnel = [(col, 2) for col in range(29, 35)]
    assert all(tilemap.terrain_at(*point) == "_" for point in tunnel)
    assert all(tilemap.is_solid(col, 1) and tilemap.is_solid(col, 3)
               for col, _row in tunnel)
    assert tilemap.terrain_at(35, 2) == "ð"

    player_y = 2 * config.TILE_SIZE + 4
    player_x, _ = collision.move_and_collide(
        28 * config.TILE_SIZE, player_y,
        config.PLAYER_HITBOX_W, config.PLAYER_HITBOX_H,
        10 * config.TILE_SIZE, 0.0, tilemap,
    )
    assert int((player_x + config.PLAYER_HITBOX_W / 2) // config.TILE_SIZE) == 35

    target = Player(35 * config.TILE_SIZE, player_y, StillInput())
    undead = UndeadEnemy((28.5) * config.TILE_SIZE,
                         (2.5) * config.TILE_SIZE, "zombie")
    undead.tilemap = tilemap
    undead.update(10.0, target)
    assert undead.x + undead.width <= 29 * config.TILE_SIZE


def test_escape_transitions_to_named_chult_4_arrival_without_bounce() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("chult_3")
        scene.player.x = 35 * config.TILE_SIZE + (
            config.TILE_SIZE - scene.player.width
        ) / 2
        scene.player.y = 2 * config.TILE_SIZE + (
            config.TILE_SIZE - scene.player.height
        ) / 2
        scene.update(0.0)
        assert scene.map_name == "chult_respite"
        assert game.active_checkpoint_id == "chult_4"
        assert scene._player_tile() == (3, 50)
        assert scene.undead == [] and scene.raptors == [] and scene.dinosaurs == []
        scene.update(0.0)
        assert scene.map_name == "chult_respite"
    finally:
        game._shutdown()


def test_respite_is_dense_meandering_connected_and_enemy_free() -> None:
    tilemap = _map("chult_respite")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (64, 56)
    walkable = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if not tilemap.is_solid(col, row)
    }
    south_bank = _flood(tilemap, (3, 50))
    north_bank = _flood(tilemap, (54, 1))
    assert south_bank.isdisjoint(north_bank)
    assert south_bank | north_bank == walkable
    assert len(south_bank) > 250 and len(north_bank) > 500
    assert len(walkable) / (64 * 56) < 0.40
    assert len(tilemap.prop_tiles) >= 275

    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert not any(kind in {
        "zombie", "skeleton", "raptor", "massive_dinosaur",
    } or kind.startswith("staged_undead:") for kind in kinds)
    assert kinds.count("breakable_grass") == 16
    assert kinds.count("anchor:chult_4_anchor") == 1
    assert kinds.count("boundary:chult_temple") == 1
    assert tileset_for("chult_respite") is tileset_for("chult_jungle")
    assert AREA_MUSIC["chult_respite"] == "chult.wav"


def test_stream_spans_the_map_and_requires_the_existing_jump() -> None:
    tilemap = _map("chult_respite")
    stream = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == "≈"
    }
    assert len(stream) == 68
    assert any(col == 0 for col, _row in stream)
    assert any(col == tilemap.width_tiles - 1 for col, _row in stream)

    reached = {next(point for point in stream if point[0] == 0)}
    frontier = deque(reached)
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in stream and point not in reached:
                reached.add(point)
                frontier.append(point)
    assert reached == stream

    # The route crosses one tile of water at column 44. Walking stops at the
    # bank; the existing committed jump clears it without a stream-only input.
    controls = StillInput()
    controls.movement = (0.0, -1.0)
    player = Player(44 * config.TILE_SIZE + 3,
                    40 * config.TILE_SIZE + 4, controls)
    player.tilemap = tilemap
    player.facing = "up"
    player.update(0.2)
    assert player.y >= 40 * config.TILE_SIZE

    controls.press_jump = True
    for _ in range(12):
        player.update(0.03)
    assert not player.jumping
    assert player.y < 39 * config.TILE_SIZE
    assert tileset_for("chult_respite").char_to_terrain["≈"] == "jungle_stream"


def test_chult_4_checkpoint_and_physical_ashtray_share_loader() -> None:
    entry = CHECKPOINT_BY_ID["chult_4"]
    assert entry.display_name == "Chult 4"
    assert entry.map_name == "chult_respite"
    assert entry.arrival == "from_chult_3"
    assert entry.runtime_entry and entry.development_visible
    anchor = CHECKPOINT_BY_ID["chult_4_anchor"]
    assert anchor.map_name == "chult_respite"
    assert anchor.position == (132.0, 805.0)
    assert anchor.saveable and not anchor.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("chult_4")
        ashtray, = scene.anchors
        scene.player.x, scene.player.y = ashtray.x, ashtray.y
        scene.update(0.01)
        assert game.active_checkpoint_id == "chult_4_anchor"
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == "chult_respite"
        assert resumed.active_checkpoint_id == "chult_4_anchor"
        assert (scene.player.x, scene.player.y) == (132.0, 805.0)
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_future_temple_boundary_is_stable_but_inert() -> None:
    tilemap = _map("chult_respite")
    boundaries = [entry for entry in tilemap.object_spawns
                  if entry[0].startswith("boundary:")]
    assert boundaries == [("boundary:chult_temple", (872.0, 24.0))]
    assert tilemap.terrain_at(54, 1) == "ð"
    assert ("chult_respite", "ð") not in AREA_WALK_EXITS


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 5 Chult respite tests passed.")


if __name__ == "__main__":
    _run_all()
