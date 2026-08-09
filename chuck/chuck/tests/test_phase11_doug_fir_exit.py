"""Phase 11's exit: the planar portal and the Douglas fir cutscene.

The phase document asks for a specific shape here -- begin from black,
fade in on a side-view forest at night, Chuck walks out of a large
Douglas fir, hold long enough to read, end at a stable boundary -- and
is equally specific that no playable forest may exist yet.

Both halves are worth testing. The order and the hold are what make the
sequence readable, and the boundary is what stops the phase leaking
into the next one: the crossing is recorded as a progress flag against
a save that still points at the City Day 6 Ashtray, so Continue comes
back to the portal rather than to a region that has not been built.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.doug_fir_cutscene_scene import (
    DOUG_FIR_FLAG, FADE_END, FADE_IN_END, HOLD_END, WALK_END, WALK_START,
    DougFirCutsceneScene,
)
from src.scenes.title_scene import TitleScene
from src.scenes.world_scene import WorldScene
from src.systems.checkpoints import KNOWN_PROGRESS_FLAGS
from src.systems.choice import ChoiceSystem
from src.world.tileset_layout import MAP_TILESET


MAP_NAME = "modern_city_day_6"
ANCHOR = "modern_city_day_6_anchor"


def _game():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game


def _scene(game, sanity=64):
    scene = DougFirCutsceneScene(game, sanity=sanity)
    scene.on_enter()
    return scene


def test_yes_at_the_portal_leaves_the_city_for_the_forest() -> None:
    yes = ChoiceSystem().get("doug_fir_portal").options[0]
    assert yes.action == "doug_fir_portal"

    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint(ANCHOR)
        world._arrival_fade_t = None
        world._on_choice(yes)
        # The action waits for the prompt to close, exactly as a map
        # transition does, and only then replaces the world.
        assert isinstance(game.scenes.current, WorldScene)
        world.update(0.0)
        assert isinstance(game.scenes.current, DougFirCutsceneScene)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_forest_arrives_out_of_black_and_then_chuck_does() -> None:
    directory, game = _game()
    try:
        scene = _scene(game)
        # Nothing moves until the forest has resolved: the environment
        # is the reveal, and Chuck walking during the fade would steal it.
        assert WALK_START >= FADE_IN_END
        assert scene.phase == "fade_in"
        assert scene.walk_progress == 0.0

        scene.elapsed = WALK_START + 0.01
        assert scene.phase == "walking"
        # He starts inside the trunk of the hero fir...
        start_x, start_y = scene.chuck_position
        assert abs(start_x + config.CHUCK_FRAME_W // 2 - 108) <= 1
        assert start_y + config.CHUCK_FRAME_H == 138  # standing on the floor

        scene.elapsed = WALK_END
        clear_x, clear_y = scene.chuck_position
        # ...and finishes clear of it, on the same ground, facing camera.
        assert clear_x > start_x + config.CHUCK_FRAME_W
        assert clear_y == start_y
        assert scene.walk_progress == 1.0

        # Then it simply holds, wordlessly, long enough to take in.
        scene.elapsed = WALK_END + 0.1
        assert scene.phase == "hold"
        assert HOLD_END - WALK_END >= 3.0
        scene.elapsed = HOLD_END + 0.1
        assert scene.phase == "fade_out"

        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        for moment in (0.1, FADE_IN_END + 0.1, WALK_START + 1.0,
                       HOLD_END + 0.2):
            scene.elapsed = moment
            scene.draw(surface)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_phase_ends_at_a_boundary_that_can_be_resumed() -> None:
    assert DOUG_FIR_FLAG in KNOWN_PROGRESS_FLAGS

    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint(ANCHOR)
        world._arrival_fade_t = None
        assert game.active_checkpoint_id == ANCHOR

        scene = _scene(game, sanity=57)
        game.scenes.replace(scene)
        scene.update(FADE_END - 0.05)
        assert DOUG_FIR_FLAG not in game.progress.flags
        assert isinstance(game.scenes.current, DougFirCutsceneScene)

        scene.update(0.1)
        assert DOUG_FIR_FLAG in game.progress.flags
        assert isinstance(game.scenes.current, TitleScene)

        # The crossing is durable, and Continue comes back to the
        # Ashtray beside the portal rather than to unbuilt forest.
        record = game.checkpoints.saves.load()
        assert record is not None
        assert record.checkpoint_id == ANCHOR
        assert record.sanity == 57
        assert DOUG_FIR_FLAG in record.progress_flags

        # Handing off is a one-time event, however long the scene runs.
        scene.update(30.0)
        assert isinstance(game.scenes.current, TitleScene)
    finally:
        game._shutdown()
        directory.cleanup()


def test_no_playable_forest_exists_yet() -> None:
    """Phase 11's out-of-scope list, held to."""
    forest = [name for name in MAP_TILESET if "fir" in name or "forest" in name]
    assert forest == [], forest
    assert not list(config.MAPS_DIR.glob("*doug_fir*"))
    # The forest exists only as one terrain inside the city map...
    from src.world.tilemap import TileMap

    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert sum(row.count("ᶂ") for row in tilemap._grid) == 9
    # ...and as a drawn backdrop with nothing playable in it.
    assert not hasattr(DougFirCutsceneScene, "update_player")


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
    print("All Doug fir exit tests passed.")


if __name__ == "__main__":
    _run_all()
