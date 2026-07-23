"""Phase 7 captain gate, arrival, accusation, and durable completion."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.deck_pirate import DeckPirateNPC
from src.scenes.dialogue_scene import DialogueScene
from src.systems.captain_confrontation import (
    CAPTAIN_CONFRONTED_FLAG,
    CAPTAIN_REQUIRED_FLAGS,
    captain_confrontation_ready,
)
from src.systems.dialogue import DialogueSystem
from src.world.tilemap import TileMap


MAP_NAME = "ship_exterior_deck"


def _captains(scene) -> list[DeckPirateNPC]:
    return [
        npc for npc in scene.npcs
        if isinstance(npc, DeckPirateNPC)
        and npc.npc_id == "captain_pirate"
    ]


def _enable_gate(game: Game) -> None:
    for flag in CAPTAIN_REQUIRED_FLAGS:
        game.progress.enable(flag)


def test_deck_authors_one_hidden_captain_beside_the_stern_helm() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    spawns = [
        (kind, position) for kind, position in tilemap.object_spawns
        if kind.startswith("deck_captain:")
    ]
    assert spawns == [(
        "deck_captain:captain_pirate:captain_confronted:captain",
        (13 * config.TILE_SIZE + 8, 24 * config.TILE_SIZE + 8),
    )]

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(MAP_NAME)
        assert _captains(scene) == []
        scene.update(0.0)
        assert game.scenes.current is scene
        assert _captains(scene) == []
    finally:
        game._shutdown()


def test_gate_requires_every_major_pirate_and_the_captain_chest() -> None:
    game = Game()
    try:
        _enable_gate(game)
        assert captain_confrontation_ready(game.progress)
        for missing in CAPTAIN_REQUIRED_FLAGS:
            game.progress.flags.remove(missing)
            assert not captain_confrontation_ready(game.progress)
            game.progress.enable(missing)
        game.progress.enable(CAPTAIN_CONFRONTED_FLAG)
        assert not captain_confrontation_ready(game.progress)
    finally:
        game._shutdown()


def test_development_checkpoint_uses_the_real_captain_arrival_gate() -> None:
    game = Game()
    try:
        definition = game.checkpoints.definition("ship_captain_arrival")
        assert definition.display_name == "Captain Arrival"
        assert definition.development_visible and not definition.saveable
        assert CAPTAIN_REQUIRED_FLAGS <= definition.required_flags
        assert CAPTAIN_CONFRONTED_FLAG not in definition.required_flags

        scene = game.checkpoints.load_checkpoint("ship_captain_arrival")
        assert scene.map_name == MAP_NAME
        assert CAPTAIN_REQUIRED_FLAGS <= game.progress.flags
        assert not game.progress.has(CAPTAIN_CONFRONTED_FLAG)
        assert _captains(scene) == []
        scene.update(0.0)
        assert scene._captain_arrival_active
        assert len(_captains(scene)) == 1
    finally:
        game._shutdown()


def test_ready_gate_spawns_captain_and_plays_complete_authored_exchange() -> None:
    dialogue = DialogueSystem()
    arrival_lines = [
        "Captain on deck!",
        "...",
    ]
    expected = [
        "That's the rat who stole my Premium Buhetian Halfling Leaf.",
        "Put him on the plank.",
        "But we've all grown fond of the smoking rat, Cap.",
        "...",
        "No.",
    ]
    assert dialogue.get("captain_arrival") == arrival_lines
    assert dialogue.get("captain_confrontation") == expected

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(
            MAP_NAME, progress_flags=CAPTAIN_REQUIRED_FLAGS
        )
        scene.update(0.0)
        assert len(_captains(scene)) == 1
        captain = _captains(scene)[0]
        assert scene._captain_arrival_active
        assert game.scenes.current is scene
        assert scene.camera._target is captain
        assert (captain.x, captain.y) == (
            31 * config.TILE_SIZE
            + (config.TILE_SIZE - captain.width) / 2,
            27 * config.TILE_SIZE
            + (config.TILE_SIZE - captain.height) / 2,
        )
        assert captain.performance == "captain"
        assert all(len(frames) == 4
                   for frames in captain._deck_frames.values())
        assert all(len(frames) == 4
                   for frames in captain._walk_frames.values())
        assert not game.progress.has(CAPTAIN_CONFRONTED_FLAG)

        start_y = captain.y
        scene.update(0.5)
        assert captain.y < start_y
        assert captain.facing == "up"
        assert captain.scripted_moving

        for _ in range(100):
            scene.update(0.1)
            if isinstance(game.scenes.current, DialogueScene):
                break
        assert isinstance(game.scenes.current, DialogueScene)
        assert game.scenes.current._lines == arrival_lines
        assert not scene._captain_arrival_active
        assert (captain.x, captain.y) == (
            13 * config.TILE_SIZE
            + (config.TILE_SIZE - captain.width) / 2,
            24 * config.TILE_SIZE
            + (config.TILE_SIZE - captain.height) / 2,
        )
        announcer = next(
            npc for npc in scene.npcs
            if isinstance(npc, DeckPirateNPC)
            and npc.npc_id == "concertina_pirate"
        )
        assert announcer.facing == "down"
        assert not game.progress.has(CAPTAIN_CONFRONTED_FLAG)

        game.scenes.pop()
        scene.update(0.0)
        assert isinstance(game.scenes.current, DialogueScene)
        assert game.scenes.current._lines == expected
        assert not game.progress.has(CAPTAIN_CONFRONTED_FLAG)

        game.scenes.pop()
        scene.update(0.0)
        assert game.progress.has(CAPTAIN_CONFRONTED_FLAG)
        assert captain.interact(scene.player) == "captain_pirate_repeat"
        assert scene.camera._target is scene.player
    finally:
        game._shutdown()


def test_completed_confrontation_saves_and_restores_without_replaying() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "save.json"
        game = Game(save_path=path)
        try:
            scene = game.checkpoints.load_checkpoint(
                MAP_NAME,
                progress_flags=(
                    CAPTAIN_REQUIRED_FLAGS | {CAPTAIN_CONFRONTED_FLAG}
                ),
            )
            assert len(_captains(scene)) == 1
            assert game.checkpoints.activate_checkpoint(
                "ship_exterior_anchor", scene.sanity.current
            )
        finally:
            game._shutdown()

        resumed = Game(save_path=path)
        try:
            scene = resumed.checkpoints.continue_game()
            assert resumed.progress.has(CAPTAIN_CONFRONTED_FLAG)
            assert len(_captains(scene)) == 1
            scene.update(0.0)
            assert resumed.scenes.current is scene
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
    print("All Phase 7 captain-confrontation tests passed.")


if __name__ == "__main__":
    _run_all()
