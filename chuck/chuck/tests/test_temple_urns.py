"""Temple urns are scratch-breakables concealing cigarette cartons.

The dressed urns ('¦' wall-base, '¢' floor) are living entities: one
scratch shatters one urn into terracotta shards and spills a full
carton — worth exactly CARTON_CIGARETTE_COUNT (20) cigarettes. The
number matters beyond the capped sanity refill: a later session adds a
cigarette counter, and a carton must bank exactly 20 into it.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.breakable_urn import BreakableUrn
from src.entities.pickup import CigaretteCarton
from src.systems.sanity import SanitySystem
from src.world.tilemap import TileMap


def test_carton_counts_as_twenty_cigarettes() -> None:
    assert config.CARTON_CIGARETTE_COUNT == 20
    carton = CigaretteCarton(40, 40)
    assert carton.cigarette_count == 20
    assert carton.restore_amount == 20 * config.CIGARETTE_SANITY_RESTORE
    sanity = SanitySystem()
    sanity.current = 5
    carton.on_collect(sanity)
    assert sanity.current == sanity.maximum  # clamped, never over
    assert not carton.alive


def test_urn_breaks_once_and_finishes_its_debris_pass() -> None:
    urn = BreakableUrn(4, 4, wall_mounted=False)
    assert urn.intact and urn.alive
    urn.on_scratched()
    assert not urn.intact
    drop = urn.take_drop_position()
    assert drop is not None
    assert urn.take_drop_position() is None  # exactly once
    urn.on_scratched()  # a second swipe is absorbed silently
    assert urn.take_drop_position() is None
    urn.update(config.BREAKABLE_GRASS_DURATION + 0.01)
    assert not urn.alive


def test_wall_urns_spill_onto_the_floor_below() -> None:
    ts = config.TILE_SIZE
    wall_urn = BreakableUrn(3, 5, wall_mounted=True)
    wall_urn.on_scratched()
    assert wall_urn.take_drop_position() == (3 * ts + ts / 2,
                                             6 * ts + ts / 2)
    floor_urn = BreakableUrn(3, 5, wall_mounted=False)
    floor_urn.on_scratched()
    assert floor_urn.take_drop_position() == (3 * ts + ts / 2,
                                              5 * ts + ts / 2)


def test_breaking_clears_the_tile_to_its_under_terrain() -> None:
    tilemap = TileMap(config.MAPS_DIR / "temple_entrance.txt")
    # The entrance hall's floor urn ('¢') and a wall-base urn ('¦').
    assert tilemap.terrain_at(36, 10) == "¢" and tilemap.is_solid(36, 10)
    tilemap.clear_tile(36, 10)
    assert tilemap.terrain_at(36, 10) == "·" and not tilemap.is_solid(36, 10)
    assert tilemap.terrain_at(14, 7) == "¦" and tilemap.is_solid(14, 7)
    tilemap.clear_tile(14, 7)
    assert tilemap.terrain_at(14, 7) == "█" and tilemap.is_solid(14, 7)


def test_scratching_a_temple_urn_spills_a_collectable_carton() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_1")
        scene._arrival_fade_t = None
        urns = [b for b in scene.breakables
                if isinstance(b, BreakableUrn)]
        assert len(urns) == 7  # every dressed urn is breakable
        assert not any(p.kind == "temple_urn" for p in scene.props)
        ts = config.TILE_SIZE
        # Stand beneath the wall-base urn at (14, 7), facing up, and
        # scratch. The carton spills onto Chuck's own tile, so the same
        # frame collects it: twenty cigarettes at once, clamped at full.
        scene.player.x, scene.player.y = 14 * ts + 3, 8 * ts + 1
        scene.player.facing = "up"
        scene.sanity.current = 10
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.01)
        urn = next(u for u in urns
                   if (u._center_x, u._bottom) == (14 * ts + 8, 8 * ts))
        assert not urn.intact
        assert scene.sanity.current == scene.sanity.maximum
        assert scene.tilemap.is_solid(14, 7)  # the wall remains a wall
    finally:
        game._shutdown()


def test_urns_and_their_tiles_reset_on_checkpoint_reload() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("temple_1")
        scene._arrival_fade_t = None
        for urn in [b for b in scene.breakables
                    if isinstance(b, BreakableUrn)]:
            urn.on_scratched()
        assert not scene.tilemap.is_solid(36, 10)  # floor urn opened
        scene = game.checkpoints.load_checkpoint("temple_1")
        urns = [b for b in scene.breakables
                if isinstance(b, BreakableUrn)]
        assert len(urns) == 7 and all(u.intact for u in urns)
        assert scene.tilemap.is_solid(36, 10)  # tile restored with map
    finally:
        game._shutdown()


def test_every_temple_map_builds_its_urns_as_breakables() -> None:
    game = Game()
    try:
        expected = {
            "temple_1": 7, "temple_2": 2, "temple_3": 9,
            "temple_4": 2, "temple_5": 3, "temple_6": 3,
        }
        for checkpoint, count in expected.items():
            scene = game.checkpoints.load_checkpoint(checkpoint)
            urns = [b for b in scene.breakables
                    if isinstance(b, BreakableUrn)]
            assert len(urns) == count, (checkpoint, len(urns))
            assert not any(p.kind == "temple_urn" for p in scene.props)
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
    print("All temple urn tests passed.")


if __name__ == "__main__":
    _run_all()
