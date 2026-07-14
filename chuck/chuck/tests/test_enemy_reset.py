"""Enemy patrol setup and reset through Chuck's respawn lifecycle."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.world_scene import WorldScene


def _advance_to_return(scene) -> None:
    scene._begin_respawn()
    scene.update(config.RESPAWN_FADE_OUT + 0.01)
    scene.update(config.RESPAWN_HOLD + 0.01)


def test_defeated_rats_reset_when_chuck_returns() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "sewer"))
        scene = game.scenes.current
        original_rats = list(scene.rats)
        assert len(scene.rats) == 7
        assert sum(rat.patrolling for rat in scene.rats) == 4

        choke_x = [rat.x for rat in scene._scratch_tutorial_rats]
        late_rat = next(rat for rat in scene.rats if rat.patrolling)
        late_x = late_rat.x
        scene.update(0.25)
        assert [rat.x for rat in scene._scratch_tutorial_rats] == choke_x
        assert late_rat.x != late_x

        for rat in scene.rats:
            rat.on_scratched()
        scene.rats = [rat for rat in scene.rats if rat.alive]
        assert not scene.rats

        _advance_to_return(scene)
        assert len(scene.rats) == 7
        assert all(rat.alive for rat in scene.rats)
        assert all(new is not old for new in scene.rats for old in original_rats)
        assert sum(rat.patrolling for rat in scene.rats) == 4
        assert len(scene._scratch_tutorial_rats) == 3
    finally:
        game._shutdown()


def test_existing_cat_resets_to_its_marker_when_chuck_returns() -> None:
    game = Game()
    try:
        game.scenes.replace(WorldScene(game, "waterdeep_docks"))
        scene = game.scenes.current
        assert len(scene.hazards) == 1
        original = scene.hazards[0]
        spawn = (original.x, original.y)
        original.x += 40

        _advance_to_return(scene)
        assert len(scene.hazards) == 1
        assert scene.hazards[0] is not original
        assert (scene.hazards[0].x, scene.hazards[0].y) == spawn
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
    print("All enemy reset tests passed.")


if __name__ == "__main__":
    _run_all()
