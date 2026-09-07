"""The final encounter's scripted conversations, and what they cost.

The phase document scripts five exchanges across this fight and says
two things about how they should play: they happen automatically, and
gameplay keeps moving between them. So they are on a clock rather than
on trigger volumes, and the clock is what this suite is mostly about --
that all five land, in the document's order, with a real stretch of
play between each pair, and that the camera goes to the three of them
and comes back to Chuck every time.

The other half is the cost. "The environment should become
increasingly unstable around Chuck" is the instruction, and here it
means the rift wins ground: from the midpoint on, every beat takes
another column of the arena. Three things about that are worth pinning
rather than trusting, because all three are the kind of thing that
looks like a bug when it goes wrong and like nothing at all when it
goes right -- it must never open under Chuck, it must never take the
footing out from under the heroes holding it, and dying must put the
whole room back.
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
from src.systems.checkpoints import DESERT_ENTRY_FLAGS
from src.systems.trio_encounter import BEATS, FIRST_ADVANCE, TrioEncounter
from src.world import collision

import sys
sys.path.insert(0, "tools")
from generate_desert_trio import FIGHTER, RANGER, WIZARD  # noqa: E402


MAP_NAME = "desert_trio"

# The document's words, in the document's order.
SCRIPT = {
    "trio_early": [
        "The boundaries are collapsing faster.",
        "Can you still do it?",
        "I think so.",
        "You think?",
        "Would you prefer I lie?",
    ],
    "trio_midpoint": [
        "It's getting worse!",
        "No. That's good.",
        "That doesn't look good.",
        "It's all in one place.",
    ],
    "trio_climax": [
        "I need another minute!",
        "You said that a minute ago!",
        "Just keep them off him!",
    ],
    "trio_found_it": [
        "Wait.",
        "I found it.",
        "You're certain?",
        "No.",
        "Good enough.",
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


def _play(game, world, seconds: float, step: float = 1 / 30):
    """Run the room, closing each conversation as it opens.

    Returns the lines of every conversation that played, in order.
    """
    played: list[list[str]] = []
    for _ in range(int(seconds / step)):
        scene = game.scenes.current
        if isinstance(scene, DialogueScene):
            played.append(list(scene._lines))
            game.scenes.pop()
            continue
        world.update(step)
    return played


def test_the_script_is_the_documents_script() -> None:
    """Every line, verbatim, and nothing else in the file.

    These are quoted in the phase document one by one. Paraphrasing any
    of them is the sort of change that reads fine and is wrong, so the
    file is compared against the text rather than eyeballed.
    """
    data = json.loads(
        (config.DIALOGUE_DIR / "desert_trio.json").read_text(encoding="utf-8")
    )
    assert set(data) == {"trio_opening"} | set(SCRIPT), sorted(data)
    for beat, lines in SCRIPT.items():
        assert data[beat] == lines, beat

    # ...and the clock plays them in the order they are written down.
    assert [name for _, name in BEATS] == list(SCRIPT), BEATS


def test_all_five_conversations_land_with_a_fight_between_them() -> None:
    """Automatic, in order, and not back to back.

    The instruction is to keep gameplay moving between dialogue
    moments. Four beats in quick succession would make the room a
    cutscene with fighting in the gaps rather than the other way round,
    so the gaps are asserted as well as the order.
    """
    for delay, _ in BEATS:
        assert delay >= 10.0, BEATS
    assert sum(delay for delay, _ in BEATS) > 55.0, BEATS

    directory, game, world = _world()
    try:
        played = _play(game, world, sum(d for d, _ in BEATS) + 20.0)
        assert len(played) == len(BEATS) + 1, len(played)
        # The entrance first, then the four scripted beats in order.
        expected = [json.loads(
            (config.DIALOGUE_DIR / "desert_trio.json").read_text(
                encoding="utf-8"))["trio_opening"]]
        expected += [SCRIPT[name] for _, name in BEATS]
        assert played == expected
        assert world.trio.finished
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_camera_goes_to_them_and_comes_back_to_him() -> None:
    """Every beat lands on the tableau, and control returns to Chuck.

    The lines are the heroes'. Played over Chuck's shoulder they are
    three voices from off screen, which is what they would be if this
    were the first time the player met them rather than the last.
    """
    directory, game, world = _world()
    try:
        _play(game, world, 1.0)          # close the entrance lines
        for _ in range(len(BEATS)):
            for _ in range(int(60 / (1 / 30))):
                if isinstance(game.scenes.current, DialogueScene):
                    break
                world.update(1 / 30)
            assert isinstance(game.scenes.current, DialogueScene)
            cx, _cy = world._battle_establishing_focus()
            on_tableau = world.camera.x + config.NATIVE_WIDTH / 2
            assert abs(on_tableau - cx) < 40, (on_tableau, cx)
            assert world._restore_camera_to_player
            game.scenes.pop()
            world.update(1 / 30)
            # ...and back on him the moment it closes.
            assert not world._restore_camera_to_player
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_rift_takes_the_room_from_the_midpoint_onward() -> None:
    """The environment getting worse, measured as ground lost.

    Not from the first beat: the early exchange is talk, and a room
    that starts closing in before anything has been said gives the
    player no read on why. From the midpoint on, every beat costs a
    column.
    """
    directory, game, world = _world()
    try:
        def sea() -> int:
            return sum(
                1 for y in range(world.tilemap.height_tiles)
                for x in range(world.tilemap.width_tiles)
                if world.tilemap.terrain_at(x, y) == "V"
            )

        _play(game, world, 1.0)
        opening = sea()
        sizes = [opening]
        for index in range(len(BEATS)):
            for _ in range(int(60 / (1 / 30))):
                if isinstance(game.scenes.current, DialogueScene):
                    break
                world.update(1 / 30)
            game.scenes.pop()
            # Let the break finish spreading before measuring.
            for _ in range(120):
                world.update(1 / 30)
            sizes.append(sea())
            assert world.trio.advances == max(0, index + 1 - FIRST_ADVANCE), \
                (index, world.trio.advances)

        assert sizes[1] == sizes[0], "the room closed in before it spoke"
        assert sizes == sorted(sizes), sizes
        assert sizes[-1] > sizes[0] * 1.1, sizes
        # ...and it is the same Sea it has always been.
        assert "V" in collision.FALL_HAZARD_TERRAIN
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_never_opens_under_anyone_who_is_standing_there() -> None:
    """Chuck's tile, and the three holding the thing shut.

    Both are the same class of failure: ground disappearing from under
    someone reads as a bug rather than as a cost. Chuck's is checked
    every frame of a full run, and the heroes' is checked at the end,
    which is when the rift has come as far as it ever will.
    """
    directory, game, world = _world()
    try:
        ts = config.TILE_SIZE
        for _ in range(int(120 / (1 / 30))):
            if isinstance(game.scenes.current, DialogueScene):
                game.scenes.pop()
                continue
            world.update(1 / 30)
            col = int(world.player.x + world.player.width / 2) // ts
            row = int(world.player.y + world.player.height / 2) // ts
            assert world.tilemap.terrain_at(col, row) != "V", (col, row)

        assert world.trio.advances >= 2, world.trio.advances
        for name, cell in (("fighter", FIGHTER), ("wizard", WIZARD),
                           ("ranger", RANGER)):
            assert world.tilemap.terrain_at(*cell) != "V", name
        # They are standing on what is left of it: the rift has come in
        # around them rather than through them.
        for name, (x, y) in (("fighter", FIGHTER), ("ranger", RANGER)):
            assert world.tilemap.terrain_at(x + 2, y) == "V", name
    finally:
        game._shutdown()
        directory.cleanup()


def test_dying_puts_the_whole_room_back() -> None:
    """The sanctum's rule, for the same reason.

    A player who dies to the last beat should get the encounter, not
    the wreckage of their previous attempt with the conversation
    already spent.
    """
    directory, game, world = _world()
    try:
        before = [
            [world.tilemap.terrain_at(x, y)
             for x in range(world.tilemap.width_tiles)]
            for y in range(world.tilemap.height_tiles)
        ]
        _play(game, world, 70.0)
        assert world.trio.beats_played >= 2
        assert world.trio.advances >= 1

        # Both of them, because the room resets both: the rift and the
        # collision are separate objects doing separate things to the
        # same arena, and healing one of them would leave the floor of
        # somebody's last attempt lying under the next.
        world.trio.restore()
        world.churn.restore()
        after = [
            [world.tilemap.terrain_at(x, y)
             for x in range(world.tilemap.width_tiles)]
            for y in range(world.tilemap.height_tiles)
        ]
        assert after == before, "the arena did not heal"
        assert world.churn.sections == 0
        assert world.trio.beats_played == 0
        assert world.trio.advances == 0
        assert not world.trio.finished
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_clock_is_its_own_object_and_says_nothing_on_its_own() -> None:
    """No tilemap, no beats -- the encounter is not a global.

    Built directly, so the failure mode this guards is visible: a
    clock that starts running on maps that have no trio on them would
    show up as the heroes talking in an empty desert.
    """
    directory, game, world = _world()
    try:
        assert isinstance(world.trio, TrioEncounter)
        other = game.checkpoints.load_checkpoint(
            "desert_east_8", progress_flags=set(DESERT_ENTRY_FLAGS))
        assert other.trio is None
        assert other.battle is None
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_breaking_ground_is_drawn() -> None:
    """The flash, which is the only warning a tile gives.

    It is the sanctum breach's own flash, because it is the same event
    -- and a break with no flash is a tile that was floor last frame
    and is death this one.
    """
    directory, game, world = _world()
    try:
        _play(game, world, 1.0)
        seen_flash = False
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        for _ in range(int(80 / (1 / 30))):
            if isinstance(game.scenes.current, DialogueScene):
                game.scenes.pop()
                continue
            world.update(1 / 30)
            if world.trio.flashes:
                seen_flash = True
                col, row, _age = world.trio.flashes[0]
                world.camera.focus_on(col * config.TILE_SIZE,
                                      row * config.TILE_SIZE)
                world.draw(surface)
                break
        assert seen_flash, "the ground broke through with no warning"
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
    print("All trio beat tests passed.")


if __name__ == "__main__":
    _run_all()
