"""Phase 7 crew quarters, progressive pirate, routes, and checkpoint."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.pirate_npc import PirateNPC
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.dialogue import DialogueSystem
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "ship_crew_quarters"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_crew_quarters_contains_the_authored_room_and_one_checkpoint() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (42, 30)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_ship_room") == 1
    assert kinds.count("anchor:ship_crew_anchor") == 1
    assert kinds.count(
        "pirate_npc:seated_pirate:crew_pirate_met"
    ) == 1
    assert kinds.count("boundary:ship_deck") == 1
    assert kinds.count("boundary:captain_cabin") == 1
    props = [kind for kind, _col, _row in tilemap.prop_tiles]
    assert props.count("ship_hammock") == 8
    assert props.count("ship_round_table") == 1
    assert tileset_for(MAP_NAME).sheet == "ship.png"
    assert AREA_MUSIC[MAP_NAME] == "ship_shanty.wav"

    entry = CHECKPOINT_BY_ID["ship_crew_quarters"]
    assert entry.display_name == "Ship Crew Quarters"
    assert entry.runtime_entry and entry.map_name == MAP_NAME
    anchor = CHECKPOINT_BY_ID["ship_crew_anchor"]
    assert anchor.saveable and not anchor.development_visible


def test_east_compartment_passage_is_reversible_but_future_routes_are_inert() -> None:
    into_quarters = AREA_WALK_EXITS[("ship_deck", "┃")]
    assert (into_quarters.destination, into_quarters.arrival) == (
        MAP_NAME, "from_ship_room"
    )
    return_room = AREA_WALK_EXITS[(MAP_NAME, "│")]
    assert (return_room.destination, return_room.arrival) == (
        "ship_deck", "from_crew_quarters"
    )
    assert (MAP_NAME, "ℓ") not in AREA_WALK_EXITS
    assert (MAP_NAME, "┃") not in AREA_WALK_EXITS


def test_seated_pirate_uses_first_then_repeat_dialogue_and_animates() -> None:
    dialogue = DialogueSystem()
    assert dialogue.get("seated_pirate_first") == [
        "Well I'll be. Never seen a rat wearin' a coat before."
    ]
    assert dialogue.get("seated_pirate_repeat") == [
        "Still wearin' the coat, then."
    ]
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_crew_quarters")
        pirate = next(npc for npc in scene.npcs if isinstance(npc, PirateNPC))
        before = pirate._anim_t
        pirate.update(0.5)
        assert pirate._anim_t > before
        assert pirate.interact(scene.player) == "seated_pirate_first"
        assert game.progress.has("crew_pirate_met")
        assert pirate.interact(scene.player) == "seated_pirate_repeat"
    finally:
        game._shutdown()


def test_crew_pirate_memory_persists_through_shared_save_loader() -> None:
    with tempfile.TemporaryDirectory() as directory:
        save_path = Path(directory) / "save.json"
        game = Game(save_path=save_path)
        try:
            game.checkpoints.load_checkpoint("ship_crew_quarters")
            game.progress.enable("crew_pirate_met")
            assert game.checkpoints.activate_checkpoint(
                "ship_crew_anchor", config.SANITY_START
            )
        finally:
            game._shutdown()

        resumed = Game(save_path=save_path)
        try:
            scene = resumed.checkpoints.continue_game()
            assert scene.map_name == MAP_NAME
            assert resumed.progress.has("crew_pirate_met")
            pirate = next(npc for npc in scene.npcs
                          if isinstance(npc, PirateNPC))
            assert pirate.interact(scene.player) == "seated_pirate_repeat"
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
    print("All Phase 7 crew-quarter tests passed.")


if __name__ == "__main__":
    _run_all()
