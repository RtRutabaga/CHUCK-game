"""Phase 13's end: the heroes succeed and Chuck goes home.

Two things happen here and the join between them is the whole slice.
The resolution conversation plays -- the heroes realising it is taking,
and then realising what else is caught in it -- and its last line is
the trigger. "Where he belongs!" closes, the worlds come apart, and the
blast puts him back on the Waterdeep docks.

The tests are mostly about that join and about the boundary at the far
end of it. The trigger must wait for the conversation to close rather
than firing on the line, or the sentence gets cut off by its own
consequence. And the cutscene must end at the title with the crossing
recorded, because the finale is a phase that does not exist yet: this
one only has to deliver him back in a clean state, which is the
document's own wording.

There is also one regression pinned here on purpose. The streaming
sequence was, briefly, twelve seconds of white -- the fade meant for
the last two seconds was written as "before the docks arrive", which is
true from the first frame. A whiteout that covers the thing it is meant
to reveal is invisible in the source and obvious for one second on
screen.
"""

import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.dialogue_scene import DialogueScene
from src.scenes.return_to_waterdeep_cutscene_scene import (
    BLAST_END, DOCKS_IN, DRAG_START, FADE_END, HOLD_END, LOOK_START,
    STREAM_END,
    ReturnToWaterdeepCutsceneScene,
)
from src.scenes.title_scene import TitleScene
from src.systems.checkpoints import (
    CHECKPOINTS, DESERT_ENTRY_FLAGS, KNOWN_PROGRESS_FLAGS,
    WATERDEEP_RETURN_FLAG,
)
from src.systems.trio_encounter import BEATS, CHURN_FROM


MAP_NAME = "desert_trio"

RESOLUTION = {
    "trio_resolution": [
        "It's working!",
        "Don't move!",
        "Wasn't planning on it!",
    ],
    "trio_caught": [
        "Something's caught in it.",
        "What?",
        "...the rat.",
        "Can you get him out?",
        "No!",
        "Then where's he going?",
        "Where he belongs!",
    ],
}


def _world():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        MAP_NAME, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _cutscene():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    scene = ReturnToWaterdeepCutsceneScene(game, sanity=48)
    scene.on_enter()
    return directory, game, scene


def test_the_resolution_is_the_documents_resolution() -> None:
    """Both exchanges, verbatim, and the second one is the last thing said."""
    data = json.loads(
        (config.DIALOGUE_DIR / "desert_trio.json").read_text(encoding="utf-8")
    )
    for beat, lines in RESOLUTION.items():
        assert data[beat] == lines, beat
    assert [name for _, name in BEATS][-2:] == list(RESOLUTION), BEATS
    assert data["trio_caught"][-1] == "Where he belongs!"


def test_the_room_stops_closing_once_it_starts_working() -> None:
    """"It's working" and the rift still eating would contradict itself.

    The rift takes a column on every beat from the midpoint up to the
    one where the collision arrives, and none after. From there the
    heroes are *closing* it, and a room that kept taking ground while
    they said so would be the floor arguing with the dialogue.
    """
    assert CHURN_FROM < len(BEATS), (CHURN_FROM, len(BEATS))

    directory, game, world = _world()
    try:
        advances = []
        for _ in range(int(200 / (1 / 30))):
            if isinstance(game.scenes.current, DialogueScene):
                game.scenes.pop()
                advances.append((world.trio.beats_played, world.trio.advances))
                continue
            if not isinstance(game.scenes.current, type(world)):
                break
            world.sanity.current = world.sanity.maximum
            world.update(1 / 30)
        played = dict(advances)
        assert played[len(BEATS)] == played[CHURN_FROM], played
        assert played[CHURN_FROM] > played[CHURN_FROM - 1], played
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_last_line_is_the_trigger_and_it_waits_for_the_line() -> None:
    """Fired on the line it would cut the sentence off with its own result.

    The same shape as the sanctum's Fireball, which waits for the
    argument that decides on it to finish before it lands.
    """
    directory, game, world = _world()
    try:
        saw_last = False
        for _ in range(int(220 / (1 / 30))):
            scene = game.scenes.current
            if isinstance(scene, DialogueScene):
                if scene._lines[-1] == "Where he belongs!":
                    saw_last = True
                    # Still in the conversation: nothing has happened yet.
                    assert world._trio_after_dialogue
                    assert isinstance(game.scenes.current, DialogueScene)
                game.scenes.pop()
                continue
            if isinstance(scene, ReturnToWaterdeepCutsceneScene):
                break
            world.sanity.current = world.sanity.maximum
            world.update(1 / 30)
        assert saw_last, "the last exchange never played"
        assert isinstance(game.scenes.current, ReturnToWaterdeepCutsceneScene)
        # Sanity goes with him, the way it does through every crossing.
        assert game.scenes.current._sanity == world.sanity.current
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_worlds_leave_one_at_a_time() -> None:
    """Thinning out, not switching off.

    All the bands stopping together is an effect being turned off. Them
    leaving one by one is a thing ending, which is what the sequence is
    for -- everything that had been jammed into one place going back to
    where it came from.
    """
    directory, game, scene = _cutscene()
    try:
        counts = []
        while scene.elapsed < STREAM_END:
            scene.update(1 / 30)
            counts.append(scene.bands_left)
        assert counts[0] >= 8, counts[0]
        assert counts == sorted(counts, reverse=True), "a world came back"
        assert counts[-1] == 0, counts[-1]
        # ...and they do not all go at once.
        distinct = sorted(set(counts), reverse=True)
        assert len(distinct) >= 6, distinct
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_sequence_goes_blast_stream_docks_and_ends() -> None:
    directory, game, scene = _cutscene()
    try:
        phases = []
        while scene.elapsed < FADE_END:
            scene.update(1 / 30)
            if not phases or phases[-1] != scene.phase:
                phases.append(scene.phase)
        assert phases == ["blast", "streaming", "arriving", "docks",
                          "fading"], phases
        assert BLAST_END < STREAM_END < DOCKS_IN < LOOK_START < HOLD_END \
            < FADE_END
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_streaming_sequence_is_not_a_whiteout() -> None:
    """The regression, pinned.

    The two-second fade into the quay was written as "before the docks
    arrive", which is true from the first frame -- so the whole rush
    played under full white. It cost nothing to write and showed
    nothing at all.
    """
    directory, game, scene = _cutscene()
    try:
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        while scene.elapsed < (BLAST_END + STREAM_END) / 2:
            scene.update(1 / 30)
        scene.draw(surface)
        pixels = [
            surface.get_at((x, y))[:3]
            for x in range(0, config.NATIVE_WIDTH, 7)
            for y in range(0, config.NATIVE_HEIGHT, 5)
        ]
        white = [p for p in pixels if min(p) > 230]
        assert len(white) < len(pixels) * 0.2, len(white)
        # ...and there is more than one world on the screen.
        assert len(set(pixels)) > 8, len(set(pixels))
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_ends_on_the_docks_with_chuck_on_them() -> None:
    directory, game, scene = _cutscene()
    try:
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        # After the drag rather than after the look: he takes the
        # place in first, and the cigarette is the last thing.
        while scene.elapsed < (DRAG_START + HOLD_END) / 2:
            scene.update(1 / 30)
        scene.draw(surface)
        pixels = [
            surface.get_at((x, y))[:3]
            for x in range(0, config.NATIVE_WIDTH, 5)
            for y in range(0, config.NATIVE_HEIGHT, 4)
        ]
        # Nothing warm is left. Not "everything is blue" -- the quay
        # stone is a grey with a warm tilt to it and would fail that --
        # but nothing with the desert's own bias in it, which is the
        # thing that has to be gone.
        warm = [p for p in pixels if p[0] - p[2] > 40]
        assert len(warm) < len(pixels) * 0.05, len(warm)
        top = [
            surface.get_at((x, y))[:3]
            for x in range(0, config.NATIVE_WIDTH, 5)
            for y in range(0, config.NATIVE_HEIGHT // 2, 4)
        ]
        assert len([p for p in top if p[2] > p[0]]) > len(top) * 0.8
        assert scene.cigarette_lit, "he got home and did not light one"
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_phase_ends_at_the_title_with_the_crossing_recorded() -> None:
    """The boundary, and why it is where it is.

    The finale is a phase that does not exist yet, so there is nowhere
    for this to hand to. The honest end is the one the desert arrival
    used before the desert was built: record what happened, let the
    title take over, and leave the player's own Ashtray owning their
    save. This test is the statement of that -- and it is written so
    that building the finale is what makes it fail.
    """
    assert WATERDEEP_RETURN_FLAG in KNOWN_PROGRESS_FLAGS
    directory, game, scene = _cutscene()
    try:
        assert WATERDEEP_RETURN_FLAG not in game.progress.flags
        while scene.elapsed < FADE_END + 0.2:
            scene.update(1 / 30)
        assert isinstance(game.scenes.current, TitleScene)
        assert WATERDEEP_RETURN_FLAG in game.progress.flags
        # Nothing was written: the crossing is not a save point.
        assert not game.checkpoints.can_continue

        # ...and there is no Waterdeep entry gated on it yet. When the
        # finale is built this is the line that says so.
        gated = [
            cp.checkpoint_id for cp in CHECKPOINTS
            if WATERDEEP_RETURN_FLAG in cp.required_flags
        ]
        assert not gated, gated
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_handoff_only_happens_once() -> None:
    """Held past its own end without pushing the title twice."""
    directory, game, scene = _cutscene()
    try:
        while scene.elapsed < FADE_END + 3.0:
            scene.update(1 / 30)
        assert isinstance(game.scenes.current, TitleScene)
        assert scene._handed_off
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
    print("All return-to-Waterdeep tests passed.")


if __name__ == "__main__":
    _run_all()
