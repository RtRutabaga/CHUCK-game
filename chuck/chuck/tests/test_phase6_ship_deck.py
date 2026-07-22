"""The ship deck — the Phase 6 -> 7 boundary (session 138).

Chuck crawls out of the rubble through the narrow crawlspace and emerges
into a cramped wooden hold; a breach in the hull opens onto the open sea.
This is the first structural slice: the arrival, the sea reveal, and the
ashtray. The escape cutscene and any onward (Phase 7) gameplay are later
work, so there is deliberately no exit off the deck.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

MAP_NAME = "ship_deck"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_the_deck_is_a_wooden_compartment_with_portholes() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (26, 13)
    kinds = [kind for kind, _pos in tilemap.object_spawns]
    assert kinds.count("arrival:from_crawlspace") == 1
    assert kinds.count("anchor:ship_deck_anchor") == 1
    # A wooden compartment (plank floor) whose hull is set with portholes
    # onto the sea — matching the escape cutscene's look.
    planks = sum(row.count("=") for row in tilemap._grid)
    portholes = sum(row.count("Ø") for row in tilemap._grid)
    assert planks >= 120, planks
    assert portholes >= 6, portholes
    # The portholes are solid hull, not walkable openings.
    from src.world.tilemap import TILE_DEFS
    assert TILE_DEFS["Ø"].solid
    # No enemies and no onward exit (the escape is a later slice).
    assert not any(k in {"rat", "zombie", "skeleton", "raptor",
                         "massive_dinosaur", "snake"} for k in kinds)
    assert not any(m == MAP_NAME for (m, _c) in AREA_WALK_EXITS)


def test_the_deck_uses_the_ship_art_and_shanty_theme() -> None:
    tileset = tileset_for(MAP_NAME)
    assert tileset.sheet == "ship.png"
    # The porthole row is animated (rolling waves), like the cutscene.
    assert tileset.info()["porthole"][1] >= 2  # frames
    assert AREA_MUSIC[MAP_NAME] == "ship_shanty.wav"


def test_ship_checkpoints_are_registered() -> None:
    entry = CHECKPOINT_BY_ID["ship_deck"]
    assert entry.display_name == "Ship 1"
    assert entry.map_name == MAP_NAME
    assert entry.arrival == "from_crawlspace"
    assert entry.runtime_entry and entry.fade_in
    anchor = CHECKPOINT_BY_ID["ship_deck_anchor"]
    assert anchor.map_name == MAP_NAME
    assert anchor.position == (116.0, 117.0)
    assert anchor.saveable and not anchor.development_visible


def test_saying_yes_to_the_crevice_plays_the_escape_then_reaches_the_ship() -> None:
    from src.scenes.escape_cutscene_scene import EscapeCutsceneScene

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_rubble")
        scene._arrival_fade_t = None
        scene.sanity.current = 40
        # Walk into the crevice zone — the prompt pops, no interact press.
        trigger = scene.choice_triggers[0]
        assert trigger.walk_triggered
        scene.player.x = trigger.x + trigger.width / 2 - scene.player.width / 2
        scene.player.y = trigger.y + trigger.height / 2 - scene.player.height / 2
        scene.update(0.0)
        prompt = game.scenes.current
        assert prompt is not scene  # the "Enter crevice?" choice opened
        # Pick YES; control returns to the rubble, which fires the escape.
        scene._on_choice(next(o for o in scene.choices.get("crevice").options
                              if o.label == "YES"))
        game.scenes.pop()  # the choice scene closes
        scene.update(0.0)
        cutscene = game.scenes.current
        assert isinstance(cutscene, EscapeCutsceneScene)
        # Play it through; it hands off to the playable ship deck itself.
        for _ in range(int(16.0 / 0.05)):
            cutscene.update(0.05)
            if game.scenes.current is not cutscene:
                break
        deck = game.scenes.current
        assert deck.map_name == MAP_NAME
        assert game.active_checkpoint_id == "ship_deck"
        assert deck._player_tile() == (13, 10)  # the from_crawlspace arrival
        assert deck.sanity.current == 40  # Sanity carried across the escape
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
    print("All ship deck tests passed.")


if __name__ == "__main__":
    _run_all()
