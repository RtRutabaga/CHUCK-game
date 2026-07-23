"""The ship arrival compartment — the Phase 6 -> 7 boundary.

Chuck crawls out of the rubble through the narrow crawlspace and emerges
into a cramped wooden compartment. North-wall portholes continue the
cutscene's sea view, while human-scale side doors and a southern ladder
establish the Phase 7 routes.
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
    # A wooden compartment whose NORTH hull alone keeps the porthole view.
    planks = sum(row.count("=") for row in tilemap._grid)
    portholes = sum(row.count("Ø") for row in tilemap._grid)
    assert planks >= 120, planks
    assert portholes == 4, portholes
    assert all(row == 2 for row, line in enumerate(tilemap._grid)
               for char in line if char == "Ø")
    # The portholes are solid hull, not walkable openings.
    from src.world.tilemap import TILE_DEFS
    assert TILE_DEFS["Ø"].solid
    # Dark open doorway recesses occupy every non-porthole wall and are
    # walkable at the threshold; the southern ladder is the first live route.
    assert "╭" in tilemap._grid[5] and "╰" in tilemap._grid[7]
    assert "╮" in tilemap._grid[5] and "╯" in tilemap._grid[7]
    assert "┌┬┐" in tilemap._grid[11]
    assert "├┼┤" in tilemap._grid[12]
    for char in "╭│╰╮┃╯┌┬┐├┼┤":
        assert not TILE_DEFS[char].solid
    assert sum(row.count("ℓ") for row in tilemap._grid) == 2
    assert not any(k in {"rat", "zombie", "skeleton", "raptor",
                         "massive_dinosaur", "snake"} for k in kinds)
    lower_exit = AREA_WALK_EXITS[(MAP_NAME, "ℓ")]
    assert lower_exit.destination == "ship_lower_hold"
    assert lower_exit.arrival == "from_ship_room"


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
        assert deck._player_tile() == (13, 9)  # the from_crawlspace arrival
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
