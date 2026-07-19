"""The overall-game cigarette counter (session 128).

Chuck's coin counter: every loose cigarette banks one, every carton
banks exactly CARTON_CIGARETTE_COUNT — fulfilling the contract carried
since the carton's introduction. The total lives on Game, survives map
walks and Astral respawns, persists through the save slot, restores on
CONTINUE, resets only with NEW GAME, and shows quietly in the HUD.
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
from src.entities.pickup import Cigarette, CigaretteCarton
from src.systems.cigarettes import CigaretteLedger
from src.systems.sanity import SanitySystem
from src.systems.save import SAVE_VERSION, SaveRecord, SaveSystem


def _temp_save() -> tuple[tempfile.TemporaryDirectory, Path]:
    directory = tempfile.TemporaryDirectory()
    return directory, Path(directory.name) / "save.json"


def test_ledger_accumulates_and_never_goes_negative() -> None:
    ledger = CigaretteLedger()
    assert ledger.total == 0
    ledger.add(1)
    ledger.add(20)
    assert ledger.total == 21
    try:
        ledger.add(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("the ledger only accumulates")
    ledger.replace(7)
    assert ledger.total == 7


def test_cigarette_banks_one_and_carton_banks_exactly_twenty() -> None:
    ledger = CigaretteLedger()
    sanity = SanitySystem()
    Cigarette(40, 40).on_collect(sanity, ledger)
    assert ledger.total == 1
    CigaretteCarton(40, 40).on_collect(sanity, ledger)
    assert ledger.total == 1 + config.CARTON_CIGARETTE_COUNT == 21


def test_collection_banks_in_a_real_scene_and_survives_respawn() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        assert game.cigarettes.total == 0
        pickup = scene.pickups[0]
        scene.player.x = pickup.x
        scene.player.y = pickup.y
        scene.update(0.01)
        assert game.cigarettes.total == 1
        # The count survives the quiet Astral respawn, like coins
        # surviving a lost life.
        scene.sanity.deplete()
        scene.update(config.RESPAWN_FADE_OUT + 0.01)
        scene.update(config.RESPAWN_HOLD + 0.01)
        assert game.cigarettes.total == 1
        # And survives an ordinary walk to another map.
        scene.load_map("sewer")
        assert game.cigarettes.total == 1
    finally:
        game._shutdown()


def test_anchor_save_and_continue_round_trip_the_total() -> None:
    directory, path = _temp_save()
    game = Game(save_path=path)
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        game.cigarettes.add(23)
        anchor = scene.anchors[0]
        scene.player.x, scene.player.y = anchor.x, anchor.y
        scene.sanity.current = 47
        scene.update(0.01)
        raw = json.loads(path.read_text(encoding="utf-8"))
        assert raw["cigarettes"] == 23
    finally:
        game._shutdown()

    resumed = Game(save_path=path)
    try:
        scene = resumed.checkpoints.continue_game()
        assert scene is not None
        assert resumed.cigarettes.total == 23
    finally:
        resumed._shutdown()

    fresh = Game(save_path=path)
    try:
        fresh.checkpoints.new_game()
        assert fresh.cigarettes.total == 0  # NEW GAME resets the ledger
    finally:
        fresh._shutdown()
        directory.cleanup()


def test_pre_counter_saves_stay_valid_with_zero_banked() -> None:
    directory, path = _temp_save()
    try:
        path.write_text(json.dumps({
            "version": SAVE_VERSION,
            "checkpoint_id": "waterdeep_anchor",
            "sanity": 50,
            "progress_flags": [],
        }), encoding="utf-8")
        record = SaveSystem(path).load()
        assert record == SaveRecord("waterdeep_anchor", 50, (), 0)
        # Forged totals are rejected like every other bad field.
        path.write_text(json.dumps({
            "version": SAVE_VERSION,
            "checkpoint_id": "waterdeep_anchor",
            "sanity": 50,
            "progress_flags": [],
            "cigarettes": -3,
        }), encoding="utf-8")
        assert SaveSystem(path).load() is None
    finally:
        directory.cleanup()


def test_hud_shows_the_total_in_the_top_right_corner() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        game.cigarettes.replace(42)
        surface = pygame.Surface(
            (config.NATIVE_WIDTH, config.NATIVE_HEIGHT)
        )
        scene.draw(surface)
        # The counter marks pixels in the top-right corner region that a
        # zero-count HUD leaves different (the label changes width/glyphs).
        top_right = pygame.Surface((60, 14))
        top_right.blit(surface, (0, 0),
                       (config.NATIVE_WIDTH - 60, 0, 60, 14))
        first = pygame.image.tobytes(top_right, "RGB")
        game.cigarettes.replace(999)
        scene.draw(surface)
        top_right.blit(surface, (0, 0),
                       (config.NATIVE_WIDTH - 60, 0, 60, 14))
        assert pygame.image.tobytes(top_right, "RGB") != first
    finally:
        game._shutdown()


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
    print("All cigarette counter tests passed.")


if __name__ == "__main__":
    _run_all()
