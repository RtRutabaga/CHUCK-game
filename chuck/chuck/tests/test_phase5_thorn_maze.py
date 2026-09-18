"""Phase 5 thorn maze, Chult Map 3 staging, and checkpoint contract."""

from collections import deque
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.systems import save_code
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


def _map(name: str) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _flood(tilemap: TileMap, start: tuple[int, int], blocked=()) -> set:
    blocked = set(blocked)
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


def _distance(tilemap: TileMap, start: tuple[int, int], goal: tuple[int, int],
              blocked=()) -> int | None:
    blocked = set(blocked)
    frontier = deque([(start, 0)])
    reached = {start}
    while frontier:
        point, distance = frontier.popleft()
        if point == goal:
            return distance
        col, row = point
        for neighbor in ((col - 1, row), (col + 1, row),
                         (col, row - 1), (col, row + 1)):
            if (neighbor not in reached and neighbor not in blocked
                    and not tilemap.is_solid(*neighbor)):
                reached.add(neighbor)
                frontier.append((neighbor, distance + 1))
    return None


def test_northern_thorn_maze_is_compact_branching_and_safely_solvable() -> None:
    tilemap = _map("chult_cog")
    thorns = {
        (col, row)
        for row, line in enumerate(tilemap._grid)
        for col, char in enumerate(line)
        if char == "|"
    }
    assert len(thorns) == 136
    assert all(2 <= row <= 11 and 19 <= col <= 59
               for col, row in thorns)

    start = (40, 12)
    exit_tile = (40, 1)
    safe = _flood(tilemap, start, blocked=thorns)
    assert exit_tile in safe
    # The sole safe entrance now commits Chuck to a substantial winding route;
    # crossing a thorn barrier remains a dangerous player-chosen shortcut.
    assert _distance(tilemap, start, exit_tile, blocked=thorns) >= 120

    maze_nodes = {
        point for point in safe
        if 1 <= point[1] <= 11 and 18 <= point[0] <= 61
    }
    # More graph edges than a tree proves the safe route contains loops rather
    # than one disguised corridor; the many degree-3 nodes supply choices.
    edges = sum(
        neighbor in maze_nodes
        for col, row in maze_nodes
        for neighbor in ((col + 1, row), (col, row + 1))
    )
    branches = sum(
        sum(neighbor in maze_nodes
            for neighbor in ((col - 1, row), (col + 1, row),
                             (col, row - 1), (col, row + 1))) >= 3
        for col, row in maze_nodes
    )
    assert edges - len(maze_nodes) + 1 >= 5
    assert branches >= 20


def test_maze_exit_targets_one_named_chult_3_arrival() -> None:
    cog = _map("chult_cog")
    boundaries = [entry for entry in cog.object_spawns
                  if entry[0].startswith("boundary:")]
    assert boundaries == [("boundary:chult_run", (648.0, 24.0))]
    assert cog.terrain_at(40, 1) == '"'
    assert cog.is_solid(40, 0)

    exit_config = AREA_WALK_EXITS[("chult_cog", '"')]
    assert exit_config.destination == "chult_run"
    assert exit_config.arrival == "from_chult_2"
    assert exit_config.facing == "up"
    arrivals = [entry for entry in _map("chult_run").object_spawns
                if entry[0].startswith("arrival:")]
    assert arrivals == [("arrival:from_chult_2", (392.0, 552.0))]


def test_chult_3_run_is_connected_and_reuses_chult_language() -> None:
    tilemap = _map("chult_run")
    assert (tilemap.width_tiles, tilemap.height_tiles) == (48, 36)
    walkable = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if not tilemap.is_solid(col, row)
    }
    assert _flood(tilemap, (24, 34)) == walkable
    assert len([kind for kind, _ in tilemap.object_spawns
                if kind.startswith("staged_undead:")]) == 24
    assert len([kind for kind, _ in tilemap.object_spawns
                if kind == "breakable_grass"]) == 6
    assert tileset_for("chult_run") is tileset_for("chult_cog")
    assert AREA_MUSIC["chult_run"] == AREA_MUSIC["chult_cog"]


def test_chult_3_has_one_physical_save_checkpoint_and_shared_dev_entry() -> None:
    tilemap = _map("chult_run")

    entry = CHECKPOINT_BY_ID["chult_3"]
    assert entry.display_name == "Chult 3"
    assert entry.map_name == "chult_run"
    assert entry.arrival == "from_chult_2"
    assert entry.runtime_entry and entry.development_visible


def test_maze_transition_and_chult_3_save_do_not_bounce() -> None:
    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("chult_2")
        scene.player.x = 40 * config.TILE_SIZE + (
            config.TILE_SIZE - scene.player.width
        ) / 2
        scene.player.y = config.TILE_SIZE + (
            config.TILE_SIZE - scene.player.height
        ) / 2
        scene.update(0.0)
        assert scene.map_name == "chult_run"
        assert game.active_checkpoint_id == "chult_3"
        assert scene._player_tile() == (24, 34)
        scene.update(0.0)
        assert scene.map_name == "chult_run"

        # The save the menu banks, at the door he came in by.
        code = save_code.for_display(
            game.checkpoints.save_here("chult_3", scene.sanity.current))
        assert game.active_checkpoint_id == "chult_3"
        assert save_code.decode(code).checkpoint_id == "chult_3"
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.resume_from(save_code.decode(code))
        assert scene.map_name == "chult_run"
        assert resumed.active_checkpoint_id == "chult_3"
    finally:
        resumed._shutdown()
        directory.cleanup()


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 5 thorn-maze and Chult 3 staging tests passed.")


if __name__ == "__main__":
    _run_all()
