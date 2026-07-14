"""Phase 2 sewer outflow and restrained return-to-docks tests."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.dialogue_scene import DialogueScene
from src.scenes.world_scene import WorldScene


def _place_at_outflow_approach(scene) -> None:
    ts = config.TILE_SIZE
    scene.player.x = 16 * ts + (ts - scene.player.width) / 2
    scene.player.y = 69 * ts + (ts - scene.player.height) / 2
    scene.player.facing = "down"


def _choose_exit(game, scene, selected: int) -> None:
    game.input._actions_just_pressed.add("interact")
    scene.update(0.01)
    dialogue = game.scenes.current
    assert isinstance(dialogue, DialogueScene)
    assert dialogue._lines == ["Leave the sewer?"]
    dialogue._box.complete()
    dialogue._selected = selected
    game.input._actions_just_pressed.add("interact")
    dialogue.update(0.01)
    assert game.scenes.current is scene
    game.input.begin_frame()


def test_outflow_waits_for_interaction_and_no_leaves_chuck_in_sewer() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "sewer"))
        scene = game.scenes.current
        _place_at_outflow_approach(scene)

        scene.update(0.01)
        assert scene.map_name == "sewer"
        target = scene._interactable_in_range()
        assert target is not None and target.choice_id == "sewer_exit"

        _choose_exit(game, scene, selected=1)
        scene.update(0.01)
        assert scene.map_name == "sewer"
        assert scene._pending_map is None
    finally:
        game._shutdown()


def test_outflow_yes_climbs_from_water_onto_south_pier() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "sewer"))
        scene = game.scenes.current
        _place_at_outflow_approach(scene)

        _choose_exit(game, scene, selected=0)
        scene.update(0.01)
        assert scene.map_name == "waterdeep_docks"
        assert scene._sewer_completed
        assert scene.tilemap.terrain_at(44, 17) == "v"
        assert not scene.tilemap.is_solid(44, 17)
        assert any(prop.kind == "tavern_open" for prop in scene.props)
        assert scene._climb_t == 0.0
        assert scene.player.facing == "up"
        start_y, target_y = scene._climb_from_y, scene._climb_target_y
        assert start_y == target_y + config.TILE_SIZE

        scene.update(config.CLIMB_OUT_DURATION / 2)
        assert target_y < scene.player.y < start_y
        assert scene.player.climb_progress is not None
        game.scenes.draw(game.native_surface)

        scene.update(config.CLIMB_OUT_DURATION)
        assert scene._climb_t is None
        assert scene.player.climb_progress is None
        assert scene.player.y == target_y
        assert not scene.player.moving
        assert scene.tilemap.terrain_at(*scene._player_tile()) == "="
    finally:
        game._shutdown()


def test_maze_ashtray_attunes_and_becomes_respawn_point() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "sewer"))
        scene = game.scenes.current
        assert len(scene.anchors) == 1
        anchor = scene.anchors[0]
        scene.player.x, scene.player.y = anchor.x, anchor.y

        assert scene._anchor_hint_visible()
        scene.update(0.01)
        assert anchor.lit
        assert scene.anchors_system.respawn_position_for_chuck() == (
            anchor.x, anchor.y
        )

        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT)
        scene.update(config.RESPAWN_HOLD)
        assert (scene.player.x, scene.player.y) == (anchor.x, anchor.y)
        assert scene.player.visible
    finally:
        game._shutdown()


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All outflow tests passed.")


if __name__ == "__main__":
    _run_all()
