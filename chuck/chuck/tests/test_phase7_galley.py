"""Phase 7 galley map, chef pursuit, checkpoint, and shared transitions."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.dialogue import DialogueSystem
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "ship_galley"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_galley_is_authored_as_one_ship_map_with_one_checkpoint() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (40, 26)
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_ship_room") == 1
    assert kinds.count("pirate_chef") == 1
    assert kinds.count("anchor:ship_galley_anchor") == 1
    assert tileset_for(MAP_NAME).sheet == "ship.png"
    assert AREA_MUSIC[MAP_NAME] == "ship_shanty.wav"

    entry = CHECKPOINT_BY_ID["ship_galley"]
    assert entry.display_name == "Ship Galley"
    assert entry.map_name == MAP_NAME and entry.runtime_entry
    anchor = CHECKPOINT_BY_ID["ship_galley_anchor"]
    assert anchor.map_name == MAP_NAME
    assert anchor.saveable and not anchor.development_visible


def test_galley_and_arrival_compartment_use_reversible_open_passages() -> None:
    into_galley = AREA_WALK_EXITS[("ship_deck", "│")]
    assert (into_galley.destination, into_galley.arrival) == (
        MAP_NAME, "from_ship_room"
    )
    into_room = AREA_WALK_EXITS[(MAP_NAME, "┃")]
    assert (into_room.destination, into_room.arrival) == (
        "ship_deck", "from_galley"
    )
    room = TileMap(config.MAPS_DIR / "ship_deck.txt")
    assert any(kind == "arrival:from_galley"
               for kind, _position in room.object_spawns)


def test_chef_delivers_authored_warning_then_begins_pursuit() -> None:
    assert DialogueSystem().get("pirate_chef_notice") == [
        "Damn! Another rat got in, come er' you little bugger!"
    ]
    game = Game()
    try:
        galley = game.checkpoints.load_checkpoint("ship_galley")
        galley._arrival_fade_t = None
        chef = galley.chefs[0]
        galley.player.x = chef.x + config.PIRATE_CHEF_NOTICE_RANGE - 8
        galley.player.y = chef.y
        galley.update(0.0)
        assert isinstance(game.scenes.current, DialogueScene)
        assert galley._chef_notice_shown
        assert game.progress.has("pirate_chef_met")
        assert not chef.pursuing

        game.scenes.pop()
        old_position = (chef.x, chef.y)
        galley.update(0.1)
        assert chef.pursuing
        assert (chef.x, chef.y) != old_position
    finally:
        game._shutdown()


def test_chef_contact_damages_sanity_and_death_reset_rearms_notice() -> None:
    game = Game()
    try:
        galley = game.checkpoints.load_checkpoint("ship_galley")
        galley._arrival_fade_t = None
        chef = galley.chefs[0]
        galley._chef_notice_shown = True
        chef.begin_pursuit()
        galley.player.x, galley.player.y = chef.x, chef.y
        before = galley.sanity.current
        galley.update(0.0)
        assert galley.sanity.current == before - chef.damage

        galley._reset_enemies()
        assert len(galley.chefs) == 1
        assert not galley.chefs[0].pursuing
        assert not galley._chef_notice_shown
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
    print("All Phase 7 galley tests passed.")


if __name__ == "__main__":
    _run_all()
