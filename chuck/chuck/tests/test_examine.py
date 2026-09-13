"""E looks at things; a scratch breaks them.

Every prop answers E with what it is. The ones worth scratching say so,
the ones that look scratchable and aren't say that instead, and the
decorative ones just say what they are. Chests only describe themselves
on E -- opening one takes a scratch, which is the whole point of having
two buttons.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.breakable_grass import BreakableGrass
from src.entities.breakable_urn import BreakableUrn
from src.entities.captain_chest import CaptainChest
from src.entities.jar_shelf import PantryJar, PantryJarShelf
from src.entities.prop import (
    MUTE_PROPS, PROP_CHOICE, PROP_DIALOGUE, _SPRITES, examine_line_id,
)
from src.entities.reactive_flower import ReactiveFlower
from src.scenes.dialogue_scene import DialogueScene
from src.systems.dialogue import DialogueSystem


def test_every_prop_has_something_to_say() -> None:
    dialogue = DialogueSystem()
    for kind in _SPRITES:
        if kind in PROP_CHOICE or kind in MUTE_PROPS:
            continue
        line = PROP_DIALOGUE.get(kind) or examine_line_id(kind)
        assert dialogue.get(line), kind


def test_things_that_look_scratchable_say_whether_they_are() -> None:
    dialogue = DialogueSystem()

    def says(line_id):
        return " ".join(dialogue.get(line_id)).lower()

    # Too sturdy: barrels, crates, rubble -- the line says a scratch won't.
    for kind in ("barrel", "crate", "crate_green", "crate_red",
                 "crate_orange", "desert_rubble", "temple_rubble_block",
                 "tavern_chair", "tavern_table"):
        text = says(examine_line_id(kind))
        assert "scratch" in text, kind
    # Worth it: the line invites one.
    for line_id in ("examine_breakable_grass", "examine_reactive_flower",
                    "examine_breakable_urn", "examine_pantry_jar",
                    "examine_ship_captain_chest",
                    "examine_desert_ruin_chest"):
        assert "scratch" in says(line_id) or "cigarette" in says(line_id), \
            line_id
    # Decoration just says what it is, briefly.
    assert says(examine_line_id("feywild_spiral")) == "a very large flower."


def test_breakables_and_switch_flowers_answer_e_until_broken() -> None:
    grass = BreakableGrass(40, 40)
    assert grass.dialogue_id == "examine_breakable_grass"
    assert len(grass.interaction_bounds()) == 4
    grass.on_scratched()
    assert grass.dialogue_id is None

    urn = BreakableUrn(3, 3, wall_mounted=False)
    assert urn.dialogue_id == "examine_breakable_urn"
    urn.on_scratched()
    assert urn.dialogue_id is None

    jar = PantryJar(3, 3)
    assert jar.dialogue_id == "examine_pantry_jar"

    shelf = PantryJarShelf(3, 3, drop=(0, 0))
    assert shelf.dialogue_id == "examine_jar_shelf"
    shelf.on_scratched()
    assert shelf.dialogue_id == "examine_jar_shelf_empty"

    flower = ReactiveFlower(40, 40, "g", trigger=lambda: True)
    assert flower.dialogue_id == "examine_reactive_flower"


def test_pressing_e_by_grass_reads_the_hint_and_leaves_it_whole() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        grass = next(item for item in scene.breakables
                     if isinstance(item, BreakableGrass))
        scene.player.x = grass.x
        scene.player.y = grass.y
        game.input._actions_just_pressed.add("interact")
        scene.update(0.0)
        game.input._actions_just_pressed.discard("interact")
        assert isinstance(game.scenes.current, DialogueScene)
        assert grass.intact
    finally:
        game._shutdown()
        directory.cleanup()


def test_e_only_describes_a_chest_and_a_scratch_opens_it() -> None:
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        game.checkpoints.load_checkpoint("ship_captain_cabin")
        for kind, flag in (("ship_captain_chest", None),
                           ("desert_ruin_chest", "desert_ruin_chest_opened")):
            chest = CaptainChest(2, 2, game.assets, game.progress, kind=kind,
                                 progress_flag=flag)
            assert chest.interact(None) == f"examine_{kind}"
            assert chest.interact(None) == f"examine_{kind}"
            assert not chest.opened
            chest.on_scratched()
            assert chest.opened
            assert chest.interact(None) == f"examine_{kind}_open"
            DialogueSystem().get(f"examine_{kind}_open")
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
    print("All examine tests passed.")


if __name__ == "__main__":
    _run_all()
