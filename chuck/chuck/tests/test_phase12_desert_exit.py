"""Phase 12's exit: the table portal and the desert arrival.

The phase document is precise about when the question may be asked --
the ordinary D&D map has no planar interaction, only its awakened state
can prompt -- and equally precise that no desert may exist yet. Both
halves are worth pinning.

The rest is shape. The crossing opens out of the table's own surface
rather than cutting to black, the desert fades up out of the light the
portal drained into, and the phase ends on a recorded flag against a
save that still points at the cabin.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.choice_trigger import _TRIGGER_TILES, _WALK_TRIGGERS
from src.scenes.desert_arrival_cutscene_scene import (
    DESERT_IN, DRAIN_END, FADE_END, HOLD_END, SWELL_END, WALK_END,
    WALK_START, DesertArrivalCutsceneScene,
)
from src.scenes.title_scene import TitleScene
from src.scenes.world_scene import WorldScene
from src.systems.cabin_progress import (
    CABIN_ENTITY_FLAGS, COUNTER_MAP_AWAKENED_FLAG, DESERT_TRANSITION_FLAG,
)
from src.systems.checkpoints import KNOWN_PROGRESS_FLAGS
from src.systems.choice import ChoiceSystem
from src.world.tileset_layout import MAP_TILESET


INTERIOR = "tahuya_cabin_interior"
AWAKE = set(CABIN_ENTITY_FLAGS) | {COUNTER_MAP_AWAKENED_FLAG}


def _world(flags=frozenset()):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        "tahuya_interior", progress_flags=set(flags)
    )
    world._arrival_fade_t = None
    return directory, game, world


def test_only_the_awakened_table_asks_the_question() -> None:
    choice = ChoiceSystem().get("cabin_table_portal")
    assert choice.prompt == "Enter planar portal?"
    yes, no = choice.options
    assert (yes.label, no.label) == ("YES", "NO")
    # NO closes with no further text at all.
    assert no.goto is None and no.dialogue is None and no.action is None
    assert yes.action == "desert_arrival"
    assert yes.goto is None and yes.dialogue is None

    # It asks on approach, at the table itself rather than across the room.
    assert "cabin_table_portal" in _WALK_TRIGGERS
    assert _TRIGGER_TILES["cabin_table_portal"] == (1, 1)

    # The ordinary map has no planar interaction: the trigger is not
    # built at all rather than being built and kept quiet.
    directory, game, world = _world()
    try:
        assert world.map_name == INTERIOR
        assert world.choice_triggers == []
    finally:
        game._shutdown()
        directory.cleanup()

    directory, game, world = _world(AWAKE)
    try:
        assert [trigger.choice_id for trigger in world.choice_triggers] == [
            "cabin_table_portal"
        ]
    finally:
        game._shutdown()
        directory.cleanup()


def test_yes_at_the_table_leaves_the_cabin_for_the_desert() -> None:
    yes = ChoiceSystem().get("cabin_table_portal").options[0]
    directory, game, world = _world(AWAKE)
    try:
        world._on_choice(yes)
        # The action waits for the prompt to close, exactly as a map
        # transition does, and only then replaces the world.
        assert isinstance(game.scenes.current, WorldScene)
        world.update(0.0)
        assert isinstance(game.scenes.current, DesertArrivalCutsceneScene)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_crossing_opens_out_of_the_table_and_into_daylight() -> None:
    directory, game, world = _world(AWAKE)
    try:
        scene = DesertArrivalCutsceneScene(game, sanity=52)
        scene.on_enter()
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))

        # It opens out of the portal's own surface rather than cutting
        # to black: the middle of the screen is lit and coloured from
        # the first moment.
        scene.elapsed = 0.2
        scene.draw(surface)
        middle = surface.get_at(
            (config.NATIVE_WIDTH // 2, config.NATIVE_HEIGHT // 2))[:3]
        assert sum(middle) > 240, middle

        # By the time it has swelled there is no black left in a corner
        # for the desert to fade up behind.
        scene.elapsed = SWELL_END - 0.05
        scene.draw(surface)
        for corner in ((2, 2), (config.NATIVE_WIDTH - 3, 2),
                       (2, config.NATIVE_HEIGHT - 3)):
            assert sum(surface.get_at(corner)[:3]) > 200, corner

        # ...and it drains to light, not to dark, because he is going
        # from a cabin at night into the middle of a day.
        scene.elapsed = DRAIN_END - 0.05
        scene.draw(surface)
        drained = surface.get_at(
            (config.NATIVE_WIDTH // 2, config.NATIVE_HEIGHT // 2))[:3]
        assert sum(drained) > sum(middle), (drained, middle)

        # Nothing moves until the desert has arrived.
        assert DRAIN_END < DESERT_IN <= WALK_START < WALK_END < HOLD_END
        scene.elapsed = DESERT_IN
        assert scene.walk_progress == 0.0
        start_x, start_y = scene.chuck_position
        scene.elapsed = WALK_END
        clear_x, clear_y = scene.chuck_position
        assert clear_x > start_x + config.CHUCK_FRAME_W
        assert clear_y == start_y
        assert HOLD_END - WALK_END >= 3.0

        for moment in (4.0, WALK_START + 1.0, HOLD_END + 0.4):
            scene.elapsed = moment
            scene.draw(surface)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_phase_ends_on_a_flag_and_a_save_that_points_at_the_cabin() -> None:
    assert DESERT_TRANSITION_FLAG in KNOWN_PROGRESS_FLAGS

    directory, game, world = _world(AWAKE)
    try:
        assert game.checkpoints.activate_checkpoint(
            "tahuya_interior_anchor", sanity=52
        )
        scene = DesertArrivalCutsceneScene(game, sanity=52)
        scene.on_enter()
        game.scenes.replace(scene)

        scene.update(FADE_END - 0.05)
        assert DESERT_TRANSITION_FLAG not in game.progress.flags
        assert isinstance(game.scenes.current, DesertArrivalCutsceneScene)

        scene.update(0.1)
        assert DESERT_TRANSITION_FLAG in game.progress.flags
        assert isinstance(game.scenes.current, TitleScene)

        record = game.checkpoints.saves.load()
        assert record is not None
        assert record.checkpoint_id == "tahuya_interior_anchor"
        assert record.sanity == 52
        assert DESERT_TRANSITION_FLAG in record.progress_flags
        assert COUNTER_MAP_AWAKENED_FLAG in record.progress_flags

        # Handing off is a one-time event, however long the scene runs.
        scene.update(30.0)
        assert isinstance(game.scenes.current, TitleScene)
    finally:
        game._shutdown()
        directory.cleanup()


def test_no_playable_desert_exists_yet() -> None:
    """Phase 12's out-of-scope list, held to."""
    desert = [name for name in MAP_TILESET if "desert" in name]
    assert desert == [], desert
    assert not list(config.MAPS_DIR.glob("*desert*"))
    # The arrival is a drawn backdrop with nothing playable in it.
    assert not hasattr(DesertArrivalCutsceneScene, "update_player")


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
    print("All desert exit tests passed.")


if __name__ == "__main__":
    _run_all()
