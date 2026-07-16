"""Phase 5 Chult Map 3 authored openings and finite undead release."""

from collections import Counter, deque
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.undead_release import UndeadReleaseController
from src.world.tilemap import TileMap


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / "chult_run.txt")


def _staged(tilemap: TileMap):
    return [entry for entry in tilemap.object_spawns
            if entry[0].startswith("staged_undead:")]


def test_openings_author_three_increasing_finite_groups() -> None:
    tilemap = _map()
    staged = _staged(tilemap)
    groups = Counter(int(kind.split(":")[1]) for kind, _position in staged)
    kinds = Counter(kind.rsplit(":", 1)[1] for kind, _position in staged)
    assert groups == {1: 6, 2: 8, 3: 10}
    assert kinds == {"zombie": 12, "skeleton": 12}

    for _kind, (cx, cy) in staged:
        col, row = int(cx // config.TILE_SIZE), int(cy // config.TILE_SIZE)
        assert tilemap.terrain_at(col, row) == '"'
        assert not tilemap.is_solid(col, row)

    # Each release shelf retains a clear three-tile route north. The enemies
    # enter through flanking canopy arches rather than appearing in open ground.
    for row in (10, 17, 24):
        assert all(tilemap.terrain_at(col, row) == "."
                   for col in range(23, 26))


def test_controller_releases_each_group_once_at_authored_rows() -> None:
    tilemap = _map()
    controller = UndeadReleaseController("chult_run", _staged(tilemap))
    assert controller.total_count == 24
    assert controller.release_for_row(28) == []
    assert len(controller.release_for_row(27)) == 6
    assert controller.release_for_row(27) == []
    assert len(controller.release_for_row(20)) == 8
    assert len(controller.release_for_row(13)) == 10
    assert controller.release_for_row(1) == []
    assert controller.released_groups == {1, 2, 3}
    controller.reset()
    assert controller.released_groups == set()
    assert len(controller.release_for_row(13)) == 24


def test_each_opening_reaches_the_run_lane_within_notice_range() -> None:
    tilemap = _map()
    for _kind, (cx, _cy) in _staged(tilemap):
        lane_centers = ((col + 0.5) * config.TILE_SIZE
                        for col in range(23, 26))
        distance_to_lane = min(abs(cx - lane_cx)
                               for lane_cx in lane_centers)
        assert distance_to_lane <= config.UNDEAD_NOTICE_RANGE


def test_chult_3_scene_starts_quiet_then_releases_without_duplication() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("chult_3")
        assert scene.map_name == "chult_run"
        assert scene.undead == []

        for row, expected in ((27, 6), (20, 14), (13, 24)):
            scene.player.x = 24 * config.TILE_SIZE
            scene.player.y = row * config.TILE_SIZE
            scene.update(0.0)
            assert len(scene.undead) == expected
            scene.update(0.0)
            assert len(scene.undead) == expected
        assert scene.undead_release.released_groups == {1, 2, 3}
    finally:
        game._shutdown()


def test_released_undead_move_out_of_openings_toward_the_run_lane() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("chult_3")
        scene.player.x = 24 * config.TILE_SIZE
        scene.player.y = 27 * config.TILE_SIZE
        scene.update(0.0)
        starts = {id(enemy): enemy.y for enemy in scene.undead}
        scene.update(0.5)
        assert len(scene.undead) == 6
        assert all(enemy.y > starts[id(enemy)] for enemy in scene.undead)
    finally:
        game._shutdown()


def test_astral_return_rewinds_the_finite_run_to_checkpoint_state() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("chult_3")
        scene.player.x = 24 * config.TILE_SIZE
        scene.player.y = 13 * config.TILE_SIZE
        scene.update(0.0)
        assert len(scene.undead) == 24

        scene._begin_respawn()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert scene.undead == []
        assert scene.undead_release.released_groups == set()
        assert scene._player_tile()[1] >= 30
    finally:
        game._shutdown()


def test_main_route_remains_connected_without_a_kill_gate() -> None:
    tilemap = _map()
    start = (24, 34)
    goal = (24, 2)
    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            if point not in reached and not tilemap.is_solid(*point):
                reached.add(point)
                frontier.append(point)
    assert goal in reached


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 5 undead-run release tests passed.")


if __name__ == "__main__":
    _run_all()
