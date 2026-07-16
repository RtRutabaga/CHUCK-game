"""Phase 5 Chult Map 2 foundation and shared checkpoint contract."""

from collections import deque
import tempfile
from pathlib import Path

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC


def _map(name: str = "chult_cog") -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def test_chult_map_2_is_substantially_larger_than_map_1() -> None:
    first = _map("chult_jungle")
    second = _map()
    assert (second.width_tiles, second.height_tiles) == (80, 80)
    assert second.width_tiles * second.height_tiles > (
        first.width_tiles * first.height_tiles * 1.5
    )


def test_chult_map_2_walkable_space_is_one_connected_exploration_area() -> None:
    tilemap = _map()
    walkable = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if not tilemap.is_solid(col, row)
    }
    start = next(iter(walkable))
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point in walkable and point not in reached:
                reached.add(point)
                frontier.append(point)
    assert reached == walkable
    # Southern, central, and northern authored zones remain connected.
    assert {(40, 70), (40, 40), (40, 10)} <= reached


def test_chult_2_checkpoint_uses_the_shared_loader_definition() -> None:
    checkpoint = CHECKPOINT_BY_ID["chult_2"]
    assert checkpoint.display_name == "Chult 2"
    assert checkpoint.map_name == "chult_cog"
    assert checkpoint.arrival == "from_chult_1"
    assert checkpoint.facing == "up"
    assert checkpoint.runtime_entry
    assert checkpoint.development_visible
    assert checkpoint.required_flags == {
        "sewer_completed", "chult_reached"
    }
    arrivals = dict(
        (kind.removeprefix("arrival:"), position)
        for kind, position in _map().object_spawns
        if kind.startswith("arrival:")
    )
    assert arrivals["from_chult_1"] == (648.0, 1224.0)


def test_chult_map_2_reuses_the_chult_visual_and_audio_language() -> None:
    assert tileset_for("chult_cog") is tileset_for("chult_jungle")
    assert AREA_MUSIC["chult_cog"] == AREA_MUSIC["chult_jungle"]
    grass = [kind for kind, _ in _map().object_spawns
             if kind == "breakable_grass"]
    assert len(grass) == 10


def test_phase_4_boundary_enters_chult_2_without_a_transition_bounce() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("chult_anchor")
        scene.player.x = 31 * config.TILE_SIZE + (
            config.TILE_SIZE - config.PLAYER_HITBOX_W
        ) / 2
        scene.player.y = config.TILE_SIZE + (
            config.TILE_SIZE - config.PLAYER_HITBOX_H
        ) / 2
        scene.update(0.0)
        assert scene.map_name == "chult_cog"
        assert game.active_checkpoint_id == "chult_2"
        assert scene.player.facing == "up"
        assert scene._player_tile() == (40, 76)
        scene.update(0.0)
        assert scene.map_name == "chult_cog"
    finally:
        game._shutdown()
        directory.cleanup()


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 5 Chult Map 2 tests passed.")


if __name__ == "__main__":
    _run_all()
