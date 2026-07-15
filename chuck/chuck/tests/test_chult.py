"""Phase 4 landing handoff, map, and first Chult checkpoint."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.falling_cutscene_scene import (
    CHULT_FADE_OUT_START, CHULT_HANDOFF_TIME, FallingCutsceneScene,
)
from src.scenes.world_scene import WorldScene
from src.systems.save import SaveRecord
from src.world.tilemap import TileMap


def _game():
    directory = tempfile.TemporaryDirectory()
    return directory, Game(save_path=Path(directory.name) / "save.json")


def test_chult_map_has_landing_and_first_anchor() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_jungle.txt")
    assert tilemap.width_tiles >= 60 and tilemap.height_tiles >= 60
    assert "player" in tilemap.spawn_points
    anchors = [kind for kind, _position in tilemap.object_spawns
               if kind == "anchor:chult_anchor"]
    assert anchors == ["anchor:chult_anchor"]

    # Every authored floor remains connected to the landing; islands of dense
    # growth shape exploration without producing accidental trapped pockets.
    start = tuple(int(value // config.TILE_SIZE)
                  for value in tilemap.spawn_points["player"])
    walkable = {
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if not tilemap.is_solid(col, row)
    }
    reached = {start}
    frontier = [start]
    while frontier:
        col, row = frontier.pop()
        for neighbor in ((col - 1, row), (col + 1, row),
                         (col, row - 1), (col, row + 1)):
            if neighbor in walkable and neighbor not in reached:
                reached.add(neighbor)
                frontier.append(neighbor)
    assert reached == walkable


def test_fallen_log_is_a_readable_chuck_sized_shortcut() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_jungle.txt")
    log_tiles = [
        (col, row)
        for row, line in enumerate(tilemap._grid)
        for col, char in enumerate(line)
        if char == "_"
    ]
    assert len(log_tiles) == 3
    assert len({row for _col, row in log_tiles}) == 1
    for col, row in log_tiles:
        assert tilemap.is_solid(col, row - 1)
        assert tilemap.is_solid(col, row + 1)
    left = min(col for col, _row in log_tiles) - 1
    right = max(col for col, _row in log_tiles) + 1
    row = log_tiles[0][1]
    assert not tilemap.is_solid(left, row)
    assert not tilemap.is_solid(right, row)


def test_cutscene_hands_off_through_shared_checkpoint_loader() -> None:
    directory, game = _game()
    try:
        game.scenes.replace(FallingCutsceneScene(game))
        calls = []
        real_load = game.checkpoints.load_checkpoint
        game.checkpoints.load_checkpoint = lambda checkpoint_id, **kwargs: (
            calls.append((checkpoint_id, kwargs))
            or real_load(checkpoint_id, **kwargs)
        )
        game.scenes.current.update(CHULT_HANDOFF_TIME + 0.01)
        scene = game.scenes.current
        assert calls == [("chult_landing", {})]
        assert isinstance(scene, WorldScene)
        assert scene.map_name == "chult_jungle"
        assert game.progress.has("chult_reached")
        assert game.active_checkpoint_id == "chult_landing"
        assert scene._arrival_fade_t == 0.0
    finally:
        game._shutdown()
        directory.cleanup()


def test_cutscene_fades_to_black_then_chult_fades_in() -> None:
    directory, game = _game()
    try:
        game.scenes.replace(FallingCutsceneScene(game))
        cutscene = game.scenes.current
        cutscene.update(CHULT_FADE_OUT_START + config.AREA_FADE_DURATION / 2)
        assert 0.49 < cutscene.fade_out_progress < 0.51
        game.scenes.draw(game.native_surface)

        cutscene.update(CHULT_HANDOFF_TIME - cutscene.elapsed + 0.01)
        scene = game.scenes.current
        assert isinstance(scene, WorldScene)
        start = (scene.player.x, scene.player.y)
        game.input._actions_down.add("move_up")
        scene.update(config.AREA_FADE_DURATION / 2)
        assert scene._arrival_fade_t is not None
        assert (scene.player.x, scene.player.y) == start
        game.scenes.draw(game.native_surface)
        scene.update(config.AREA_FADE_DURATION / 2 + 0.01)
        assert scene._arrival_fade_t is None
    finally:
        game._shutdown()
        directory.cleanup()


def test_chult_anchor_saves_and_continue_restores_it() -> None:
    directory, game = _game()
    path = game.saves.path
    try:
        scene = game.checkpoints.load_checkpoint("chult_landing")
        scene.update(config.AREA_FADE_DURATION + 0.01)
        anchor = scene.anchors[0]
        scene.sanity.current = 63
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.update(0.01)
        assert game.saves.load() == SaveRecord(
            "chult_anchor", 63, ("chult_reached", "sewer_completed")
        )
        assert game.active_checkpoint_id == "chult_anchor"
    finally:
        game._shutdown()

    game = Game(save_path=path)
    try:
        scene = game.checkpoints.continue_game()
        assert scene.map_name == "chult_jungle"
        assert scene.sanity.current == 63
        assert game.active_checkpoint_id == "chult_anchor"
        assert scene.anchors[0].lit
    finally:
        game._shutdown()
        directory.cleanup()


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Chult landing tests passed.")


if __name__ == "__main__":
    _run_all()
