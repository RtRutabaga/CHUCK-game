"""Things big enough to hide somebody thin out while somebody is under them.

Two routes to the same behaviour. Big props -- the great trees, the
ship's sails, the cog in the jungle, the arches, the turrets, the cabin
-- thin while a walker stands behind them. Overhead tiles -- market
awnings, the city gate, palm crowns, the jungle's exit canopy, the
Feywild's hedge openings -- thin a whole connected canopy at a time,
because fading only the tiles a rat is touching cuts a rat-shaped hole
in the canvas.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.prop import SEE_THROUGH_PROPS
from src.world.tilemap import TILE_DEFS, TileMap


TS = config.TILE_SIZE


def _game():
    directory = tempfile.TemporaryDirectory()
    return directory, Game(save_path=Path(directory.name) / "save.json")


def _hold(scene, col, row, seconds):
    for _ in range(round(seconds * 60)):
        scene.player.x, scene.player.y = col * TS + 4, row * TS + 5
        scene.update(1 / 60)


def test_the_named_things_are_all_see_through() -> None:
    for kind in ("feywild_great_tree", "ship_mast_sail", "sailing_cog",
                 "waterdeep_docked_ship", "tahuya_cabin"):
        assert kind in SEE_THROUGH_PROPS, kind
    # The cabin's porch is walked on; it must not fade under Chuck's feet.
    assert SEE_THROUGH_PROPS["tahuya_cabin"] >= 60


def test_an_awning_is_one_piece_of_canvas() -> None:
    """Every tile of one market awning belongs to one region; the next
    awning over is a different one."""
    tilemap = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    regions = tilemap.overhead_regions()
    awning = {regions[(col, row)] for col in range(41, 53)
              for row in (28, 29, 30)
              if (col, row) in regions}
    assert len(awning) == 1, awning
    assert len(set(regions.values())) > 1
    for (col, row) in regions:
        assert TILE_DEFS[tilemap.terrain_at(col, row)].overhead


def test_standing_under_an_awning_thins_all_of_it_and_leaving_restores_it():
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        regions = scene.tilemap.overhead_regions()
        awning = regions[(44, 29)]
        _hold(scene, 44, 29, 0.6)
        assert scene._overhead_veils.get(awning) == 1.0
        # The other awnings are left alone.
        assert all(region == awning for region in scene._overhead_veils)
        _hold(scene, 44, 34, 0.6)
        assert awning not in scene._overhead_veils
    finally:
        game._shutdown()
        directory.cleanup()


def test_nobody_but_chuck_fades_a_canopy() -> None:
    """It thins for the player and for nothing else.

    This used to fade for anyone with feet, on the grounds that an enemy
    vanishing under an awning is a hit the player cannot see coming. In
    practice what it mostly did was flicker: the ship's sails went half
    transparent every time a fencer walked his loop behind them, and
    Chult's dinosaur thinned a tree out from across the map with Chuck
    nowhere near it. A canopy that fades for things the player is not
    doing reads as a bug in the canopy.
    """
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        regions = scene.tilemap.overhead_regions()
        awning = regions[(44, 29)]
        _hold(scene, 44, 40, 0.1)          # Chuck well away from it

        class Walker:
            hitbox = pygame.Rect(46 * TS, 29 * TS, 10, 8)
            sort_y = 29 * TS + 8

        real = scene._sorted_drawables
        scene._sorted_drawables = lambda: [*real(), Walker()]
        scene._update_see_through_props(1.0)
        assert scene._overhead_veils.get(awning) is None

        # ...and it still thins the moment Chuck walks under it himself.
        _hold(scene, 44, 29, 0.6)
        assert scene._overhead_veils.get(awning) == 1.0
    finally:
        game._shutdown()
        directory.cleanup()


def test_a_prop_does_not_thin_for_an_npc_walking_behind_it() -> None:
    """The ship's sails, with a fencer at his loop and Chuck elsewhere."""
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
        sail = next(prop for prop in scene.props
                    if prop.kind == "ship_mast_sail")
        col = (sail._draw_x + sail._size[0] // 2) // TS
        row = int(sail.sort_y // TS) - 3
        crew = [npc for npc in scene.npcs
                if sail.cover_rect().colliderect(npc.hitbox)]
        _hold(scene, col, row + 12, 0.6)   # Chuck well clear of the rig
        assert sail.veil == 0.0, [npc.hitbox for npc in crew]
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_ship_sail_thins_while_chuck_is_behind_it() -> None:
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
        sail = next(prop for prop in scene.props
                    if prop.kind == "ship_mast_sail")
        col = (sail._draw_x + sail._size[0] // 2) // TS
        row = int(sail.sort_y // TS) - 3
        _hold(scene, col, row, 0.6)
        assert sail.veil == 1.0
        _hold(scene, col, row + 6, 0.6)
        assert sail.veil == 0.0
    finally:
        game._shutdown()
        directory.cleanup()


def test_a_thinned_overhead_tile_is_actually_thinner() -> None:
    directory, game = _game()
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        tilemap = scene.tilemap
        art = tilemap._overhead_art["a"][0]
        thin = tilemap._thinned_overhead_tile("a", 0, 6, art)
        sample = [(x, y) for x in range(0, art.get_width(), 3)
                  for y in range(0, art.get_height(), 3)
                  if art.get_at((x, y)).a == 255]
        assert sample
        assert all(thin.get_at(p).a < 128 for p in sample)
    finally:
        game._shutdown()
        directory.cleanup()


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
    print("All see-through tests passed.")


if __name__ == "__main__":
    _run_all()
