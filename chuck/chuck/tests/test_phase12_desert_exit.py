"""Phase 12's exit: the table portal and the desert arrival.

The phase document is precise about when the question may be asked --
the ordinary D&D map has no planar interaction, only its awakened state
can prompt -- and that is still worth pinning, because it is the one
gate the whole ending hangs off.

The rest is shape. The crossing opens out of the table's own surface
rather than cutting to black, the desert fades up out of the light the
portal drained into, he walks out of a second mouth that then closes
behind him, and the whole thing hands off into Phase 13's playable
desert rather than back to the title.
"""

import importlib
import math
import os
from pathlib import Path
import struct
import tempfile
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.choice_trigger import _TRIGGER_TILES, _WALK_TRIGGERS
from src.scenes.desert_arrival_cutscene_scene import (
    CIGARETTE_SEATED, CIGARETTE_START, COLLAPSE_END, COLLAPSE_START,
    DESERT_IN, DRAG_START, DRAIN_END, FADE_END, HOLD_END, LOOK_START,
    DESERT_ENTRY_CHECKPOINT, SWELL_END, WALK_END, WALK_START,
    DesertArrivalCutsceneScene,
    _GROUND_Y, _PORTAL_HALF_W, _PORTAL_X, _SAND,
)
from src.scenes.return_to_waterdeep_cutscene_scene import (
    FADE_END as RETURN_FADE_END,
)
from src.scenes.world_scene import WorldScene
from src.systems.cabin_progress import (
    CABIN_ENTITY_FLAGS, COUNTER_MAP_AWAKENED_FLAG, DESERT_TRANSITION_FLAG,
)
from src.systems.checkpoints import KNOWN_PROGRESS_FLAGS
from src.systems.choice import ChoiceSystem
from src.world.tileset_layout import MAP_TILESET
from src.world.transitions import AREA_MUSIC


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
    # Two of them, one either side of the table: walking down the room
    # to it and walking up the room to it are the same arrival.

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
        triggers = world.choice_triggers
        assert [trigger.choice_id for trigger in triggers] == [
            "cabin_table_portal", "cabin_table_portal"
        ]
        # One north of the table, one south of it, on the same column.
        north, south = sorted(triggers, key=lambda t: t.y)
        assert north.x == south.x
        assert south.y > north.y
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


def test_he_comes_out_of_a_mouth_that_then_closes_behind_him() -> None:
    """He is not placed in the desert, he arrives through something.

    The far mouth stands open before he does anything, he walks out of
    it, and it folds up afterwards -- so by the time the tableau holds
    there is nothing in the frame to explain how he got there.
    """
    directory, game, world = _world(AWAKE)
    try:
        scene = DesertArrivalCutsceneScene(game, sanity=52)
        scene.on_enter()

        # Standing open before he moves, still open while he walks out,
        # gone by the time he looks around.
        assert DESERT_IN <= WALK_START < WALK_END <= COLLAPSE_START
        assert COLLAPSE_START < COLLAPSE_END <= LOOK_START < CIGARETTE_START
        for moment in (DESERT_IN, WALK_START, WALK_END):
            scene.elapsed = moment
            assert scene.portal_scale == 1.0, moment
        scene.elapsed = COLLAPSE_END
        assert scene.portal_scale == 0.0
        scene.elapsed = HOLD_END
        assert scene.portal_scale == 0.0

        # ...and it shrinks the whole way rather than in a jump.
        scale = [
            (scene.__setattr__("elapsed", COLLAPSE_START + step * 0.2)
             or scene.portal_scale)
            for step in range(9)
        ]
        assert scale == sorted(scale, reverse=True), scale

        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        # He is walking out of the mouth, so he starts where it stands.
        scene.elapsed = WALK_START
        arrive_x = scene.chuck_position[0]
        assert abs(arrive_x - _PORTAL_X) < config.CHUCK_FRAME_W
        # ...and stops clear of it.
        scene.elapsed = WALK_END
        assert scene.chuck_position[0] > _PORTAL_X + _PORTAL_HALF_W

        # The mouth is drawn, in colour, on the sand.
        scene.elapsed = WALK_START
        scene.draw(surface)
        mouth = surface.get_at((_PORTAL_X, _GROUND_Y - 30))[:3]
        assert mouth != _SAND, mouth
        # ...and once it has closed that spot is plain sand again.
        scene.elapsed = LOOK_START
        scene.draw(surface)
        assert surface.get_at((_PORTAL_X, _GROUND_Y - 30))[:3] == _SAND
    finally:
        game._shutdown()
        directory.cleanup()


def test_he_lights_a_cigarette_once_he_is_alone_in_it() -> None:
    """The arrival is not over until he has done what he always does."""
    directory, game, world = _world(AWAKE)
    try:
        scene = DesertArrivalCutsceneScene(game, sanity=52)
        scene.on_enter()
        # He reaches for it only after the portal has gone, and it is
        # alight with real time left to stand there smoking.
        assert COLLAPSE_END < CIGARETTE_START < CIGARETTE_SEATED
        assert HOLD_END - CIGARETTE_SEATED >= 4.0

        scene.elapsed = CIGARETTE_START
        assert not scene.cigarette_lit
        scene.elapsed = CIGARETTE_SEATED
        assert scene.cigarette_lit

        # In profile for the whole gesture: played against the
        # front-facing frame the cigarette floats beside his ear.
        for moment in (CIGARETTE_START, CIGARETTE_SEATED, HOLD_END - 0.1):
            scene.elapsed = moment
            assert scene._facing() in {"left", "right"}, moment

        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        for moment in (CIGARETTE_START + 0.4, CIGARETTE_SEATED + 0.1,
                       DRAG_START + 1.0):
            scene.elapsed = moment
            scene.draw(surface)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_desert_arrival_starts_the_regions_theme_and_quiet_noises_under_it() -> None:
    """The cue is gone; the region's theme starts here instead.

    Phase 12 wrote this scene a one-shot of its own that ended as the
    scene faded, which was right while there was nothing on the far side
    for it to hand to. Phase 13's region has a theme, and a cue in front
    of a theme is two pieces of music with a join in them -- so the
    scene starts the theme itself, looping, exactly as the desert map
    will ask for it, and the map's request is a no-op. The join is not
    smoothed over, it does not exist.

    The old cue is not orphaned: the return-to-Waterdeep cutscene plays
    it, so the tune from Chuck's arrival is what plays as he leaves. It
    is checked here for the same properties it always had, because it is
    still a rendered one-shot that has to be the right length for the
    scene that now owns it.
    """
    song = importlib.import_module("data.music.desert_arrival")
    seconds = song.TOTAL_BEATS * 60.0 / song.TEMPO_BPM
    # Sized to the sequence that plays it now, ending before its fade.
    assert seconds < RETURN_FADE_END, (seconds, RETURN_FADE_END)
    assert seconds > RETURN_FADE_END - 8.0, seconds

    path = config.MUSIC_DIR / "desert_arrival.wav"
    with wave.open(str(path)) as handle:
        assert handle.getnchannels() == 1
        rate = handle.getframerate()
        raw = handle.readframes(handle.getnframes())
    samples = [value / 32767 for (value,) in struct.iter_unpack("<h", raw)]
    assert abs(len(samples) / rate - seconds) < 0.2
    peak = max(abs(sample) for sample in samples)
    assert peak <= 0.95, peak
    level = math.sqrt(sum(s * s for s in samples) / len(samples))
    assert 0.08 <= level <= 0.20, level

    # The three new noises exist and are short: none of them is an
    # event in its own right, they are texture under the cue.
    for name in ("portal_hum", "portal_collapse", "lighter"):
        effect = config.SFX_DIR / f"{name}.wav"
        assert effect.exists(), name
        with wave.open(str(effect)) as handle:
            length = handle.getnframes() / handle.getframerate()
        assert 0.2 <= length <= 2.5, (name, length)

    # ...and every cue the scene fires names a file that is really there.
    directory, game, world = _world(AWAKE)
    try:
        scene = DesertArrivalCutsceneScene(game, sanity=52)
        scene.on_enter()
        played: list = []
        game.audio.play_sfx = played.append
        game.audio.play_music = lambda name, loop=True: played.append(
            (name, loop))
        for step in range(int(FADE_END / 0.1) + 2):
            scene.elapsed = step * 0.1
            scene._play_cues(scene.elapsed - 0.1, scene.elapsed)
        # The region's theme, looping, and nothing else: the scene asks
        # for precisely what the map it hands to will ask for.
        music = [entry for entry in played if isinstance(entry, tuple)]
        assert music == [("desert.wav", True)], music
        assert AREA_MUSIC["desert_central"] == "desert.wav"
        for name in ("portal_hum", "portal_collapse", "lighter"):
            assert played.count(name) == 1, (name, played)
        assert len([p for p in played if isinstance(p, str)
                    and p.startswith("footstep")]) == 3
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_crossing_comes_out_in_the_playable_desert() -> None:
    """Both halves of the journey, joined.

    This used to end at the title. Phase 12 closed with no playable
    region on the far side of the table, so recording the crossing and
    letting Continue come back to the cabin was the only honest thing
    the scene could do. Phase 13 built the far side, so the crossing now
    goes where it always meant to: out into the desert, through the same
    shared checkpoint path the Douglas fir crossing uses.
    """
    assert DESERT_TRANSITION_FLAG in KNOWN_PROGRESS_FLAGS

    directory, game, world = _world(AWAKE)
    try:
        assert game.checkpoints.activate_checkpoint(
            "tahuya_interior_anchor", sanity=52
        )
        scene = DesertArrivalCutsceneScene(game, sanity=52)
        scene.on_enter()
        game.scenes.replace(scene)

        # Nothing happens until the fade is over.
        scene.update(FADE_END - 0.05)
        assert DESERT_TRANSITION_FLAG not in game.progress.flags
        assert isinstance(game.scenes.current, DesertArrivalCutsceneScene)

        scene.update(0.1)
        assert DESERT_TRANSITION_FLAG in game.progress.flags
        arrived = game.scenes.current
        assert isinstance(arrived, WorldScene)
        assert arrived.map_name == "desert_central"
        assert game.active_checkpoint_id == DESERT_ENTRY_CHECKPOINT

        # Sanity is carried through the crossing rather than restored,
        # and so is everything the cabin recorded on the way to it.
        assert arrived.sanity.current == 52
        assert COUNTER_MAP_AWAKENED_FLAG in game.progress.flags
        assert set(CABIN_ENTITY_FLAGS) <= game.progress.flags

        # The desert's own Ashtray owns persistence from here: the
        # handoff itself writes nothing, so the save still points at the
        # cabin until the player reaches the new one.
        record = game.checkpoints.saves.load()
        assert record is not None
        assert record.checkpoint_id == "tahuya_interior_anchor"
        assert arrived.anchors
        assert arrived.anchors[0].checkpoint_id == "desert_central_anchor"

        # Handing off is a one-time event, however long the scene runs.
        scene.update(30.0)
        assert game.scenes.current is arrived
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_desert_is_still_gated_behind_the_crossing() -> None:
    """The phase boundary moved; it did not disappear.

    Phase 12's version of this asserted that no desert map and no desert
    tileset existed at all -- the cleanest possible statement of an
    out-of-scope list, and one that could only ever be true once. What
    outlives it is the gate underneath: the desert is reachable only
    once the crossing this scene performs has actually been recorded.
    """
    from src.systems.checkpoints import CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS

    # The arrival is still a drawn backdrop with nothing playable in it.
    assert not hasattr(DesertArrivalCutsceneScene, "update_player")

    desert_maps = [name for name in MAP_TILESET if name.startswith("desert")]
    assert desert_maps, "Phase 13 should have built at least one"
    assert DESERT_TRANSITION_FLAG in DESERT_ENTRY_FLAGS
    entries = [c for c in CHECKPOINT_BY_ID.values()
               if c.map_name in desert_maps]
    assert entries
    for entry in entries:
        assert DESERT_TRANSITION_FLAG in entry.required_flags,             entry.checkpoint_id

    # ...and the scene hands off to one of them rather than naming a
    # position of its own, so the map decides where its start is.
    assert DESERT_ENTRY_CHECKPOINT in CHECKPOINT_BY_ID
    assert CHECKPOINT_BY_ID[DESERT_ENTRY_CHECKPOINT].map_name in desert_maps


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
