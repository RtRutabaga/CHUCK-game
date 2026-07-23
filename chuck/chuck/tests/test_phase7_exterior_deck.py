"""Phase 7 exterior-deck foundation, motion, route, and checkpoint."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.ship_motion import deck_rock_offset
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "ship_exterior_deck"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_exterior_is_a_large_reference_led_ship_in_animated_sea() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (64, 44)
    masts = [(col, row) for kind, col, row in tilemap.prop_tiles
             if kind == "ship_mast_sail"]
    assert masts == [(21, 22), (42, 22)]
    helms = [(col, row) for kind, col, row in tilemap.prop_tiles
             if kind == "ship_helm"]
    assert helms == [(17, 24)]
    bowsprits = [(col, row) for kind, col, row in tilemap.prop_tiles
                 if kind == "ship_bowsprit"]
    assert bowsprits == [(55, 22)]
    deck_rows = [row for row, tiles in enumerate(tilemap._grid)
                 if "=" in tiles]
    assert (min(deck_rows), max(deck_rows)) == (12, 31)
    assert sum(row.count("~") for row in tilemap._grid) > 1200
    assert tileset_for(MAP_NAME).char_to_terrain["~"] == "ship_ocean"
    assert AREA_MUSIC[MAP_NAME] == "ship_shanty.wav"


def test_deck_has_one_checkpoint_and_uses_the_shared_loader() -> None:
    tilemap = _map()
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_crew_quarters") == 1
    assert kinds.count("anchor:ship_exterior_anchor") == 1
    assert sum(kind.startswith("anchor:") for kind in kinds) == 1

    entry = CHECKPOINT_BY_ID["ship_exterior_deck"]
    assert entry.display_name == "Ship Exterior Deck"
    assert entry.runtime_entry and entry.development_visible
    anchor = CHECKPOINT_BY_ID["ship_exterior_anchor"]
    assert anchor.saveable and not anchor.development_visible

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
        assert scene.map_name == MAP_NAME
        assert len(scene.anchors) == 1
        mast_sizes = [prop._size for prop in scene.props
                      if prop.kind == "ship_mast_sail"]
        assert mast_sizes == [(224, 192), (224, 192)]
        helm = next(prop for prop in scene.props if prop.kind == "ship_helm")
        assert helm._size == (56, 54)
        bowsprit = next(prop for prop in scene.props
                        if prop.kind == "ship_bowsprit")
        assert bowsprit._size == (400, 96)
    finally:
        game._shutdown()


def test_crew_ladder_is_reversible() -> None:
    outward = AREA_WALK_EXITS[("ship_crew_quarters", "ℓ")]
    assert (outward.destination, outward.arrival) == (
        MAP_NAME, "from_crew_quarters"
    )
    inward = AREA_WALK_EXITS[(MAP_NAME, "ℓ")]
    assert (inward.destination, inward.arrival) == (
        "ship_crew_quarters", "from_exterior_deck"
    )
    crew = TileMap(config.MAPS_DIR / "ship_crew_quarters.txt")
    assert any(kind == "arrival:from_exterior_deck"
               for kind, _position in crew.object_spawns)


def test_exterior_ashtray_persists_and_continues_on_the_deck() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "save.json"
        game = Game(save_path=path)
        try:
            scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
            assert game.checkpoints.activate_checkpoint(
                "ship_exterior_anchor", scene.sanity.current
            )
        finally:
            game._shutdown()

        resumed = Game(save_path=path)
        try:
            scene = resumed.checkpoints.continue_game()
            assert scene.map_name == MAP_NAME
            assert resumed.active_checkpoint_id == "ship_exterior_anchor"
        finally:
            resumed._shutdown()


def test_deck_rock_is_subtle_and_returns_to_its_shanty_phase_origin() -> None:
    samples = [deck_rock_offset(i / 20) for i in range(100)]
    assert all(abs(x) <= 1 and abs(y) <= 1 for x, y in samples)
    assert len(set(samples)) > 1
    period = (60.0 / 126.0) * 8.0
    assert deck_rock_offset(0.0) == deck_rock_offset(period)


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
    print("All Phase 7 exterior-deck tests passed.")


if __name__ == "__main__":
    _run_all()
