"""Phase 6 Temple Map 3 skeleton chamber and shared checkpoint flow."""

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
    return TileMap(config.MAPS_DIR / "temple_skeletons.txt")


def _flood(
    tilemap: TileMap,
    start: tuple[int, int],
    extra_blocked: set[tuple[int, int]] | None = None,
) -> set[tuple[int, int]]:
    blocked = extra_blocked or set()
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


def test_skeleton_chamber_is_broad_connected_and_combat_is_avoidable() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (56, 44)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("skeleton") == 12
    assert kinds.count("anchor:temple_3_anchor") == 1
    assert kinds.count("arrival:from_temple_2") == 1
    assert kinds.count("boundary:temple_4") == 1
    assert sum(row.count("i") for row in tilemap._grid) == 12
    assert not any(kind in {
        "zombie", "rat", "raptor", "massive_dinosaur",
    } for kind in kinds)

    skeleton_tiles = {
        (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
        for kind, (x, y) in tilemap.object_spawns if kind == "skeleton"
    }
    # Reserve a 3x3 avoidance area around every skeleton: a route through
    # the chamber still exists without defeating or brushing past one.
    blocked = {
        (col + dx, row + dy)
        for col, row in skeleton_tiles
        for dx in (-1, 0, 1) for dy in (-1, 0, 1)
    }
    reached = _flood(tilemap, (27, 39), blocked)
    assert (2, 20) in reached


def test_temple_maps_2_and_3_connect_both_ways_without_bounce() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_2")
        scene.player.x = 23 * config.TILE_SIZE + 3
        scene.player.y = 2 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_skeletons"
        assert game.active_checkpoint_id == "temple_3"
        assert scene._player_tile() == (27, 39)
        assert AREA_MUSIC["temple_spikes"] == AREA_MUSIC["temple_skeletons"]
        scene.update(0.0)
        assert scene.map_name == "temple_skeletons"

        scene.player.x = 27 * config.TILE_SIZE + 3
        scene.player.y = 42 * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == "temple_spikes"
        assert game.active_checkpoint_id == "temple_2_return"
        assert scene._player_tile() == (23, 3)
        scene.update(0.0)
        assert scene.map_name == "temple_spikes"
    finally:
        game._shutdown()


def test_temple_3_ashtray_saves_continues_and_respawns_enemies() -> None:
    entry = CHECKPOINT_BY_ID["temple_3"]
    assert entry.display_name == "Temple 3"
    assert entry.map_name == "temple_skeletons"
    assert entry.arrival == "from_temple_2"
    assert entry.runtime_entry and entry.development_visible
    anchor_entry = CHECKPOINT_BY_ID["temple_3_anchor"]
    assert anchor_entry.position == (436.0, 597.0)
    assert anchor_entry.saveable and not anchor_entry.development_visible

    directory = tempfile.TemporaryDirectory()
    save_path = Path(directory.name) / "save.json"
    game = Game(save_path=save_path)
    try:
        scene = game.checkpoints.load_checkpoint("temple_3")
        assert len(scene.undead) == 12
        assert all(enemy.kind == "skeleton" for enemy in scene.undead)
        scene.undead[0].alive = False
        scene.undead = [enemy for enemy in scene.undead if enemy.alive]
        anchor, = scene.anchors
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.sanity.current = 63
        scene.update(0.01)
        assert game.active_checkpoint_id == "temple_3_anchor"
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert (scene.player.x, scene.player.y) == (anchor.x, anchor.y)
        assert len(scene.undead) == 12
    finally:
        game._shutdown()

    resumed = Game(save_path=save_path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene.map_name == "temple_skeletons"
        assert resumed.active_checkpoint_id == "temple_3_anchor"
        assert scene.sanity.current == 63
        assert len(scene.undead) == 12
    finally:
        resumed._shutdown()
        directory.cleanup()


def test_skeleton_chamber_uses_temple_art_and_turns_west_to_map_4() -> None:
    assert tileset_for("temple_skeletons").sheet == "temple.png"
    assert AREA_MUSIC["temple_skeletons"] == "temple.wav"
    assert AREA_WALK_EXITS[("temple_skeletons", "∇")].destination == (
        "temple_darts"
    )
    boundary = next(
        position for kind, position in _map().object_spawns
        if kind == "boundary:temple_4"
    )
    assert boundary == (40.0, 328.0)
    assert AREA_WALK_EXITS[("temple_skeletons", "Δ")].destination == (
        "temple_spikes"
    )


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Phase 6 temple-skeleton tests passed.")


if __name__ == "__main__":
    _run_all()
