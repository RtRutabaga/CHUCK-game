"""Phase 7 exterior deck's rhythmic non-combat pirate cast."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.deck_pirate import DeckPirateNPC
from src.systems.dialogue import DialogueSystem
from src.world.tilemap import TileMap


MAP_NAME = "ship_exterior_deck"
FLAGS = {
    "deck_concertina_met",
    "deck_cheering_met",
    "deck_dancer_met",
    "deck_jeffries_met",
}


def test_map_authors_the_four_noncombat_performers_and_no_fencers() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    deck_spawns = [
        (kind, position) for kind, position in tilemap.object_spawns
        if kind.startswith("deck_pirate:")
    ]
    assert len(deck_spawns) == 4
    kinds = {kind for kind, _position in deck_spawns}
    assert kinds == {
        "deck_pirate:concertina_pirate:deck_concertina_met:concertina",
        "deck_pirate:cheering_pirate:deck_cheering_met:cheer",
        "deck_pirate:dancing_pirate:deck_dancer_met:dance",
        "deck_pirate:jeffries:deck_jeffries_met:struggle",
    }
    jeffries = next(position for kind, position in deck_spawns
                    if ":jeffries:" in kind)
    assert jeffries == (21 * config.TILE_SIZE + 8, 23 * config.TILE_SIZE + 8)
    assert DeckPirateNPC(
        *jeffries, "jeffries", progress=object(),
        progress_flag="deck_jeffries_met", performance="struggle",
    ).draw_lift == 24
    assert all("fencer" not in kind for kind, _position in tilemap.object_spawns)


def test_dialogue_uses_authored_collided_world_lines_and_repeat_ids() -> None:
    dialogue = DialogueSystem()
    assert dialogue.get("jeffries_first") == [
        "The sea is wrong, the land is wrong. Open your eyes!",
        "Half the crew is gone... lost to the purple. They don't even remember them.",
    ]
    assert dialogue.get("jeffries_repeat") == [
        "Don't go into the purple! DON'T GO INTO THE PURPLE!",
        "Why don't they see!?",
    ]
    assert dialogue.get("cheering_pirate_first") == [
        "Don't mind Jeffries over there tied to the mast. He's gone mad. Too much sun, I think."
    ]


def test_each_performer_has_four_distinct_shanty_timed_frames() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(MAP_NAME)
        pirates = [npc for npc in scene.npcs
                   if isinstance(npc, DeckPirateNPC)]
        assert len(pirates) == 4
        assert {npc.performance for npc in pirates} == {
            "concertina", "cheer", "dance", "struggle"
        }
        for pirate in pirates:
            assert all(len(frames) == 4
                       for frames in pirate._deck_frames.values())
            first = pirate.animation_frame
            pirate.update((60.0 / 126.0) / 2.0 + 0.001)
            assert pirate.animation_frame == (first + 1) % 4
    finally:
        game._shutdown()


def test_all_four_pirates_switch_to_repeat_dialogue_and_persist() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "save.json"
        game = Game(save_path=path)
        try:
            scene = game.checkpoints.load_checkpoint(MAP_NAME)
            pirates = [npc for npc in scene.npcs
                       if isinstance(npc, DeckPirateNPC)]
            for pirate in pirates:
                assert pirate.interact(scene.player) == f"{pirate.npc_id}_first"
                assert pirate.interact(scene.player) == f"{pirate.npc_id}_repeat"
            assert FLAGS <= game.progress.flags
            assert game.checkpoints.activate_checkpoint(
                "ship_exterior_anchor", scene.sanity.current
            )
        finally:
            game._shutdown()

        resumed = Game(save_path=path)
        try:
            scene = resumed.checkpoints.continue_game()
            assert FLAGS <= resumed.progress.flags
            pirates = [npc for npc in scene.npcs
                       if isinstance(npc, DeckPirateNPC)]
            assert all(npc.interact(scene.player) == f"{npc.npc_id}_repeat"
                       for npc in pirates)
        finally:
            resumed._shutdown()


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
    print("All Phase 7 deck-cast tests passed.")


if __name__ == "__main__":
    _run_all()
