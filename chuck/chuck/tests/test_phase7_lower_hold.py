"""Phase 7's first playable ship-interior branch: the lower hold."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.jar_shelf import PantryJar, PantryJarShelf
from src.entities.pickup import CigaretteCarton
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "ship_lower_hold"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_lower_hold_is_a_cargo_filled_rat_map() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (40, 30)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_ship_room") == 1
    assert kinds.count("anchor:ship_lower_hold_anchor") == 1
    assert kinds.count("rat") == 16
    prop_kinds = [kind for kind, _col, _row in tilemap.prop_tiles]
    assert prop_kinds.count("pantry_shelf") == 8
    assert prop_kinds.count("grain_sack") >= 10
    assert prop_kinds.count("crate") >= 6
    assert prop_kinds.count("barrel") >= 5


def test_hold_shelves_and_jars_reuse_pantry_breakable_cartons() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_lower_hold")
        shelves = [b for b in scene.breakables
                   if isinstance(b, PantryJarShelf)]
        jars = [b for b in scene.breakables if isinstance(b, PantryJar)]
        assert len(shelves) == 8
        assert len(jars) >= 10
        assert not any(p.kind in {"pantry_shelf", "grain_sack"}
                       for p in scene.props)
        assert all(scene.tilemap.terrain_at(
            int(shelf._drop[0] // config.TILE_SIZE),
            int(shelf._drop[1] // config.TILE_SIZE)) == "="
                   for shelf in shelves)

        jar = jars[0]
        col = int(jar._center_x // config.TILE_SIZE)
        row = int(jar._bottom // config.TILE_SIZE) - 1
        assert scene.tilemap.is_solid(col, row)
        scene.player.x = col * config.TILE_SIZE + 3
        scene.player.y = (row + 1) * config.TILE_SIZE + 1
        scene.player.facing = "up"
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.01)
        assert not jar.intact
        carton = next(p for p in scene.pickups
                      if isinstance(p, CigaretteCarton))
        assert carton.cigarette_count == config.CARTON_CIGARETTE_COUNT
        # The same scratch invokes the shared callback and opens ship planks.
        assert not scene.tilemap.is_solid(col, row)
        assert scene.tilemap.terrain_at(col, row) == "="
    finally:
        game._shutdown()


def test_lower_hold_uses_shared_ship_systems_and_returns_upstairs() -> None:
    assert tileset_for(MAP_NAME).sheet == "ship.png"
    assert AREA_MUSIC[MAP_NAME] == "ship_shanty.wav"
    upstairs = AREA_WALK_EXITS[(MAP_NAME, "ℓ")]
    assert upstairs.destination == "ship_deck"
    assert upstairs.arrival == "from_lower_hold"

    entry = CHECKPOINT_BY_ID["ship_lower_hold"]
    assert entry.display_name == "Ship Hold"
    assert entry.map_name == MAP_NAME and entry.runtime_entry
    anchor = CHECKPOINT_BY_ID["ship_lower_hold_anchor"]
    assert anchor.map_name == MAP_NAME
    assert anchor.saveable and not anchor.development_visible


def test_ladder_transition_and_rat_respawn_use_existing_architecture() -> None:
    game = Game()
    try:
        room = game.checkpoints.load_checkpoint("ship_deck")
        room._arrival_fade_t = None
        ladder_col = next(
            col for row in room.tilemap._grid for col, char in enumerate(row)
            if char == "ℓ"
        )
        ladder_row = next(
            row for row, line in enumerate(room.tilemap._grid) if "ℓ" in line
        )
        room.player.x = ladder_col * config.TILE_SIZE + 4
        room.player.y = ladder_row * config.TILE_SIZE + 4
        room.update(0.0)
        hold = game.scenes.current
        assert hold.map_name == MAP_NAME
        assert hold._player_tile() == (19, 4)
        assert len(hold.rats) == 16

        hold.rats[0].alive = False
        hold.rats = [rat for rat in hold.rats if rat.alive]
        hold._reset_enemies()
        assert len(hold.rats) == 16

        hold.player.x = 19 * config.TILE_SIZE + 4
        hold.player.y = 3 * config.TILE_SIZE + 4
        hold.update(0.0)
        room = game.scenes.current
        assert room.map_name == "ship_deck"
        assert room._player_tile() == (12, 9)
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
    print("All Phase 7 lower-hold tests passed.")


if __name__ == "__main__":
    _run_all()
