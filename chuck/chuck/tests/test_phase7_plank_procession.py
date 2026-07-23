"""Phase 7 staged starboard plank and ordered approach."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.deck_pirate import DeckPirateNPC
from src.scenes.dialogue_scene import DialogueScene
from src.systems.captain_confrontation import (
    CAPTAIN_CONFRONTED_FLAG,
    CAPTAIN_REQUIRED_FLAGS,
    DECK_PLANK_LENGTH,
    DECK_PLANK_TERRAIN,
)
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for


MAP_NAME = "ship_exterior_deck"
PLANK_ORIGIN = (42, 32)


def _pirate(scene, npc_id: str) -> DeckPirateNPC:
    return next(
        npc for npc in scene.npcs
        if isinstance(npc, DeckPirateNPC) and npc.npc_id == npc_id
    )


def _tile_centered_position(entity, col: int, row: int) -> tuple[float, float]:
    ts = config.TILE_SIZE
    return (
        col * ts + (ts - entity.width) / 2,
        row * ts + (ts - entity.height) / 2,
    )


def test_map_authors_one_plank_origin_in_the_starboard_rail() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    origins = [
        position for kind, position in tilemap.object_spawns
        if kind == "deck_plank_origin"
    ]
    assert origins == [(
        PLANK_ORIGIN[0] * config.TILE_SIZE + 8,
        PLANK_ORIGIN[1] * config.TILE_SIZE + 8,
    )]
    assert tilemap.terrain_at(*PLANK_ORIGIN) == "═"
    assert tilemap.is_solid(*PLANK_ORIGIN)
    assert tileset_for(MAP_NAME).char_to_terrain[DECK_PLANK_TERRAIN] == (
        "ship_plank"
    )


def test_plank_is_hidden_before_confrontation_and_staged_afterward() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(MAP_NAME)
        col, row = PLANK_ORIGIN
        assert scene.tilemap.terrain_at(col, row) == "═"
        assert all(
            scene.tilemap.terrain_at(col, plank_row) != DECK_PLANK_TERRAIN
            for plank_row in range(row, row + DECK_PLANK_LENGTH)
        )

        scene = game.checkpoints.load_checkpoint(
            MAP_NAME,
            progress_flags=(
                CAPTAIN_REQUIRED_FLAGS | {CAPTAIN_CONFRONTED_FLAG}
            ),
        )
        assert all(
            scene.tilemap.terrain_at(col, plank_row) == DECK_PLANK_TERRAIN
            and not scene.tilemap.is_solid(col, plank_row)
            for plank_row in range(row, row + DECK_PLANK_LENGTH)
        )
        assert scene.tilemap.terrain_at(col, row + DECK_PLANK_LENGTH) == "~"
        assert scene.tilemap.is_solid(col, row + DECK_PLANK_LENGTH)
        assert scene.tilemap.is_solid(col - 1, row + 2)
        assert scene.tilemap.is_solid(col + 1, row + 2)
    finally:
        game._shutdown()


def test_completed_state_places_captain_and_objector_at_the_approach() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(
            MAP_NAME,
            progress_flags=(
                CAPTAIN_REQUIRED_FLAGS | {CAPTAIN_CONFRONTED_FLAG}
            ),
        )
        captain = _pirate(scene, "captain_pirate")
        objector = _pirate(scene, "cheering_pirate")
        assert (captain.x, captain.y) == _tile_centered_position(
            captain, 39, 30
        )
        assert (objector.x, objector.y) == _tile_centered_position(
            objector, 45, 30
        )
        assert captain.facing == "right"
        assert objector.facing == "left"
        assert not scene._plank_procession_active
    finally:
        game._shutdown()


def test_dialogue_hands_off_to_short_scripted_walk_then_returns_control() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(
            MAP_NAME, progress_flags=CAPTAIN_REQUIRED_FLAGS
        )
        scene.update(0.0)
        assert isinstance(game.scenes.current, DialogueScene)
        game.scenes.pop()

        scene.update(0.0)
        assert scene._plank_procession_active
        assert game.progress.has(CAPTAIN_CONFRONTED_FLAG)
        assert (scene.player.x, scene.player.y) == _tile_centered_position(
            scene.player, 42, 27
        )
        assert scene.player.facing == "down"
        assert all(
            scene.tilemap.terrain_at(42, row) == DECK_PLANK_TERRAIN
            for row in range(32, 32 + DECK_PLANK_LENGTH)
        )

        scene.update(2.0)
        assert not scene._plank_procession_active
        assert scene._plank_procession_target is None
        assert (scene.player.x, scene.player.y) == _tile_centered_position(
            scene.player, 42, 31
        )
        assert not scene.player.moving
        assert game.scenes.current is scene
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
    print("All Phase 7 plank-procession tests passed.")


if __name__ == "__main__":
    _run_all()
