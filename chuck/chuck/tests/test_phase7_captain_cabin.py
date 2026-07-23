"""Phase 7 captain cabin, physical chest reward, save, and transitions."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.captain_chest import CaptainChest
from src.entities.pickup import GoldenCigaretteCarton
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "ship_captain_cabin"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_captain_cabin_is_one_complete_checkpointed_ship_map() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (36, 21)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_crew_quarters") == 1
    assert kinds.count("anchor:ship_captain_anchor") == 1
    props = [kind for kind, _col, _row in tilemap.prop_tiles]
    assert props.count("ship_captain_chest") == 1
    assert tileset_for(MAP_NAME).sheet == "ship.png"
    assert AREA_MUSIC[MAP_NAME] == "ship_shanty.wav"

    entry = CHECKPOINT_BY_ID["ship_captain_cabin"]
    assert entry.display_name == "Ship Captain Cabin"
    assert entry.runtime_entry and entry.map_name == MAP_NAME
    anchor = CHECKPOINT_BY_ID["ship_captain_anchor"]
    assert anchor.position == (100.0, 229.0)
    assert anchor.saveable and not anchor.development_visible


def test_cabin_passage_is_reversible_through_the_existing_open_doorway() -> None:
    into_cabin = AREA_WALK_EXITS[("ship_crew_quarters", "┃")]
    assert (into_cabin.destination, into_cabin.arrival) == (
        MAP_NAME, "from_crew_quarters"
    )
    return_crew = AREA_WALK_EXITS[(MAP_NAME, "│")]
    assert (return_crew.destination, return_crew.arrival) == (
        "ship_crew_quarters", "from_captain_cabin"
    )
    crew = TileMap(config.MAPS_DIR / "ship_crew_quarters.txt")
    assert any(kind == "arrival:from_captain_cabin"
               for kind, _position in crew.object_spawns)


def test_interacting_animates_chest_then_drops_physical_gold_carton() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_captain_cabin")
        chest = next(prop for prop in scene.props
                     if isinstance(prop, CaptainChest))
        before = game.cigarettes.total
        x, y, w, h = chest.interaction_bounds()
        scene.player.x = x + w / 2 - scene.player.width / 2
        scene.player.y = y + h + 1
        scene.player.facing = "up"
        game.input._actions_just_pressed.add("interact")
        scene.update(0.0)
        game.input._actions_just_pressed.discard("interact")
        assert game.scenes.current is scene
        assert chest.opened
        assert game.progress.has("captain_chest_opened")
        assert not scene.pickups
        assert game.cigarettes.total == before

        scene.update(chest.opening_duration)
        assert len(scene.pickups) == 1
        carton = scene.pickups[0]
        assert isinstance(carton, GoldenCigaretteCarton)
        assert carton.cigarette_count == 40
        # "In front" is the open floor immediately south of the chest.
        assert carton.y >= chest.y + chest.height

        scene.player.x = carton.x
        scene.player.y = carton.y
        scene.update(0.0)
        assert not scene.pickups
        assert game.progress.has("captain_chest_carton_collected")
        assert game.cigarettes.total == before + config.HALFLING_LEAF_CIGARETTES
        game.cigarettes.rollback()
        assert game.cigarettes.total == before + config.HALFLING_LEAF_CIGARETTES
    finally:
        game._shutdown()


def test_scratch_opens_chest_without_dialogue_or_duplicate_drop() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_captain_cabin")
        chest = next(prop for prop in scene.props
                     if isinstance(prop, CaptainChest))
        scene.player.x = chest.x + chest.width / 2 - scene.player.width / 2
        scene.player.y = chest.y + chest.height + 1
        scene.player.facing = "up"
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.0)
        game.input._actions_just_pressed.discard("scratch")
        assert game.scenes.current is scene
        assert chest.opened

        scene.update(chest.opening_duration)
        assert len(scene.pickups) == 1
        chest.on_scratched()
        chest.interact(scene.player)
        scene.update(chest.opening_duration)
        assert len(scene.pickups) == 1
    finally:
        game._shutdown()


def test_collected_gold_carton_and_open_chest_persist_through_continue() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "save.json"
        game = Game(save_path=path)
        try:
            scene = game.checkpoints.load_checkpoint("ship_captain_cabin")
            chest = next(prop for prop in scene.props
                         if isinstance(prop, CaptainChest))
            chest.interact(scene.player)
            scene.update(chest.opening_duration)
            carton = next(pickup for pickup in scene.pickups
                          if isinstance(pickup, GoldenCigaretteCarton))
            scene.player.x = carton.x
            scene.player.y = carton.y
            scene.update(0.0)
            assert game.checkpoints.activate_checkpoint(
                "ship_captain_anchor", scene.sanity.current
            )
        finally:
            game._shutdown()

        resumed = Game(save_path=path)
        try:
            scene = resumed.checkpoints.continue_game()
            assert scene.map_name == MAP_NAME
            assert resumed.progress.has("captain_chest_opened")
            assert resumed.progress.has("captain_chest_carton_collected")
            assert resumed.cigarettes.total == config.HALFLING_LEAF_CIGARETTES
            chest = next(prop for prop in scene.props
                         if isinstance(prop, CaptainChest))
            assert chest.opened
            assert not any(isinstance(pickup, GoldenCigaretteCarton)
                           for pickup in scene.pickups)
            assert chest.interact(scene.player) is None
            assert resumed.cigarettes.total == config.HALFLING_LEAF_CIGARETTES
        finally:
            resumed._shutdown()


def test_open_uncollected_chest_reconstructs_carton_on_continue() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "save.json"
        game = Game(save_path=path)
        try:
            scene = game.checkpoints.load_checkpoint("ship_captain_cabin")
            chest = next(prop for prop in scene.props
                         if isinstance(prop, CaptainChest))
            chest.interact(scene.player)
            scene.update(chest.opening_duration)
            assert game.checkpoints.activate_checkpoint(
                "ship_captain_anchor", scene.sanity.current
            )
        finally:
            game._shutdown()

        resumed = Game(save_path=path)
        try:
            scene = resumed.checkpoints.continue_game()
            assert resumed.progress.has("captain_chest_opened")
            assert not resumed.progress.has("captain_chest_carton_collected")
            assert sum(isinstance(pickup, GoldenCigaretteCarton)
                       for pickup in scene.pickups) == 1
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
    print("All Phase 7 captain-cabin tests passed.")


if __name__ == "__main__":
    _run_all()
