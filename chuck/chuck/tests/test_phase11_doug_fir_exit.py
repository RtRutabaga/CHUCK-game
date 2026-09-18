"""Phase 11's exit and its Phase 12 handoff.

The phase document asks for a specific shape here -- begin from black,
fade in on a side-view forest at night, Chuck walks out of a large
Douglas fir, hold long enough to read, end at a stable boundary -- and
The completed cutscene remains unchanged; Phase 12 now consumes its stable
boundary by entering the authored cabin grounds through the shared checkpoint
loader. Persistence still waits for the physical exterior door.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.systems import save_code
from src.core.game import Game
from src.scenes.doug_fir_cutscene_scene import (
    DOUG_FIR_FLAG, FADE_END, FADE_IN_END, HOLD_END, WALK_END, WALK_START,
    DougFirCutsceneScene,
)
from src.scenes.world_scene import WorldScene
from src.systems.checkpoints import KNOWN_PROGRESS_FLAGS
from src.systems.choice import ChoiceSystem
from src.world.tileset_layout import MAP_TILESET


MAP_NAME = "modern_city_day_6"

# The door the city hands off from, where the door used to be.
CITY_DOOR = "modern_city_day_6"


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
        world = game.checkpoints.load_checkpoint(CITY_DOOR)
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


def test_the_phase_hands_into_the_shared_cabin_checkpoint() -> None:
    assert DOUG_FIR_FLAG in KNOWN_PROGRESS_FLAGS

    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint(CITY_DOOR)
        world._arrival_fade_t = None

        scene = _scene(game, sanity=57)
        game.scenes.replace(scene)
        scene.update(FADE_END - 0.05)
        assert DOUG_FIR_FLAG not in game.progress.flags
        assert isinstance(game.scenes.current, DougFirCutsceneScene)

        scene.update(0.1)
        assert DOUG_FIR_FLAG in game.progress.flags
        exterior = game.scenes.current
        assert isinstance(exterior, WorldScene)
        assert exterior.map_name == "tahuya_cabin_exterior"
        assert game.active_checkpoint_id == "tahuya_exterior"
        assert exterior.sanity.current == 57

        # The cabin's own door owns persistence: the handoff banks the
        # checkpoint (asserted above) and nothing else.

        # Handing off is a one-time event, however long the scene runs.
        scene.update(30.0)
        assert game.scenes.current is exterior
    finally:
        game._shutdown()
        directory.cleanup()


def test_phase_12_keeps_the_doug_fir_handoff_to_the_authored_cabin() -> None:
    assert MAP_TILESET["tahuya_cabin_exterior"] == "tahuya"
    assert (config.MAPS_DIR / "tahuya_cabin_exterior.txt").is_file()
    assert MAP_TILESET["tahuya_cabin_interior"] == "tahuya"
    assert (config.MAPS_DIR / "tahuya_cabin_interior.txt").is_file()
    # The city still contains exactly one animated portal into the transition.
    from src.world.tilemap import TileMap

    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    assert sum(row.count("Ȣ") for row in tilemap._grid) == 1
    # The cutscene itself remains a drawn backdrop, not a second forest map.
    assert not hasattr(DougFirCutsceneScene, "update_player")


def test_the_tree_opening_is_the_same_portal_as_the_city_one() -> None:
    """Both ends of the crossing have to look like one thing.

    The oval standing in the wrecked city block and the opening in the
    Douglas fir are the same portal seen from either side of it, so
    they share their surface outright rather than being drawn twice and
    kept in step by hand.
    """
    from src.entities import planar_portal

    # The city portal's own frames are built from this same function.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "city_portal_tool",
        Path(__file__).resolve().parents[1] / "tools"
        / "generate_city_planar_portal.py",
    )
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    assert tool.portal_colour is planar_portal.portal_colour

    # The surface turns: the same point is a different colour a moment
    # later, which is the whole difference from the black hole it was.
    still = planar_portal.portal_colour(0.2, -0.3, 0.0)
    later = planar_portal.portal_colour(0.2, -0.3, 1.4)
    assert still != later

    directory, game = _game()
    try:
        scene = _scene(game)
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        scene.elapsed = HOLD_END - 1.0
        scene.draw(surface)
        # Across the opening: lit rather than the near-black it used to
        # be, and carrying more than one colour rather than one flat
        # tone. Any single pixel can happen to be neutral, so this
        # looks at the whole width.
        inside = [surface.get_at((108 + step, 138 - 13))[:3]
                  for step in range(-5, 6)]
        assert all(sum(pixel) > 240 for pixel in inside), inside
        assert len(set(inside)) > 4, inside
        assert max(max(p) - min(p) for p in inside) > 8, inside
    finally:
        game._shutdown()
        directory.cleanup()


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
