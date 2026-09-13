"""Waterdeep's people say something different the second time.

Everyone in the opening and finale Waterdeep except Bobert and the
guards. The guards say one thing, the same thing, every time -- and the
plaza's two say what the docks' north-east guard says, because they are
the same watch on the same wall.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core.game import Game
from src.systems.waterdeep_finale import PLAZA_TOWNSFOLK


# Checkpoints that stand Chuck in every Waterdeep room, both eras.
WATERDEEP_STOPS = (
    "waterdeep_start", "tavern_entry", "waterdeep_plaza_from_docks",
    "waterdeep_finale", "waterdeep_plaza_finale",
)


def _people(scene):
    return [npc for npc in scene.npcs if type(npc).__name__ in
            ("NPC", "FishermanNPC")]


def test_plaza_guards_say_what_the_docks_guard_says() -> None:
    guards = [spawn for spawn in PLAZA_TOWNSFOLK if spawn.sprite_id == "guard"]
    assert len(guards) == 2
    assert all(spawn.dialogue_id == "guard" for spawn in guards)


def test_everyone_but_the_guards_has_a_second_word() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        seen = set()
        for checkpoint in WATERDEEP_STOPS:
            scene = game.checkpoints.load_checkpoint(checkpoint)
            for npc in _people(scene):
                seen.add(npc.dialogue_id)
                if npc.dialogue_id == "guard":
                    assert not scene.dialogue.has("guard_repeat")
                    continue
                assert scene.dialogue.has(f"{npc.dialogue_id}_repeat"), \
                    npc.dialogue_id
        # Every kind of Waterdeep person got checked.
        for dialogue_id in ("dock_worker", "market_woman", "guard",
                            "bartender", "patron", "musician", "fisherman",
                            "return_dock_worker", "market_browser",
                            "blacksmith", "alchemist", "plaza_townsperson",
                            "return_plaza_townsperson"):
            assert dialogue_id in seen, dialogue_id
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_second_word_is_per_person_and_resets_on_new_game() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_plaza_finale")
        browsers = [npc for npc in scene.npcs
                    if npc.dialogue_id == "return_plaza_townsperson"]
        first, second = browsers[0], browsers[1]
        assert scene._second_word(first, first.dialogue_id) == \
            "return_plaza_townsperson"
        assert scene._second_word(first, first.dialogue_id) == \
            "return_plaza_townsperson_repeat"
        # A different person with the same line still gets a first word.
        assert scene._second_word(second, second.dialogue_id) == \
            "return_plaza_townsperson"
        # Guards never change.
        guard = next(npc for npc in scene.npcs if npc.dialogue_id == "guard")
        assert scene._second_word(guard, "guard") == "guard"
        assert scene._second_word(guard, "guard") == "guard"

        game.checkpoints.new_game()
        assert not game.spoken_to
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
    print("All Waterdeep second-word tests passed.")


if __name__ == "__main__":
    _run_all()
