"""Phase 7 paired wandering sword-fighter hazard."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.sword_fighter import SwordFighter
from src.world.tilemap import TileMap


MAP_NAME = "ship_exterior_deck"


def test_map_authors_exactly_two_fencers_on_an_avoidable_open_route() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    spawns = [(kind, position) for kind, position in tilemap.object_spawns
              if kind.startswith("sword_fighter:")]
    assert spawns == [
        ("sword_fighter:a", (30 * config.TILE_SIZE + 8,
                             20 * config.TILE_SIZE + 8)),
        ("sword_fighter:b", (34 * config.TILE_SIZE + 8,
                             20 * config.TILE_SIZE + 8)),
    ]
    # Broad lanes remain above and below the encounter; it is not a combat gate.
    assert all(not tilemap.is_solid(col, row)
               for row in (18, 25) for col in range(28, 37))


def test_pair_wanders_together_and_animates_on_shanty_half_beats() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(MAP_NAME)
        assert len(scene.fencers) == 2
        first, second = scene.fencers
        assert isinstance(first, SwordFighter)
        assert {first.role, second.role} == {"a", "b"}
        assert first._pair_center == second._pair_center
        assert (first.animation_frame, second.animation_frame) == (0, 2)
        starts = [(fencer.x, fencer.y) for fencer in scene.fencers]
        half_beat = (60.0 / 126.0) / 2.0
        for fencer in scene.fencers:
            fencer.update(half_beat + 0.001)
        assert (first.animation_frame, second.animation_frame) == (1, 3)
        for _step in range(180):
            for fencer in scene.fencers:
                fencer.update(1.0 / 60.0)
        assert any((fencer.x, fencer.y) != start
                   for fencer, start in zip(scene.fencers, starts))
        for fencer in scene.fencers:
            col = int((fencer.x + fencer.width / 2) // config.TILE_SIZE)
            row = int((fencer.y + fencer.height / 2) // config.TILE_SIZE)
            assert not scene.tilemap.is_solid(col, row)
    finally:
        game._shutdown()


def test_contact_damages_sanity_and_reset_restores_the_pair() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint(MAP_NAME)
        scene._arrival_fade_t = None
        first = scene.fencers[0]
        scene.player.x, scene.player.y = first.x, first.y
        before = scene.sanity.current
        scene.update(0.0)
        assert scene.sanity.current == before - config.SWORD_FIGHTER_SANITY_DAMAGE

        for fencer in scene.fencers:
            fencer.update(1.0)
        scene._reset_enemies()
        assert len(scene.fencers) == 2
        assert [(round(f.x), round(f.y)) for f in scene.fencers] == [
            (30 * config.TILE_SIZE + 8 - config.NPC_HITBOX_W // 2,
             20 * config.TILE_SIZE + 8 - config.NPC_HITBOX_H // 2),
            (34 * config.TILE_SIZE + 8 - config.NPC_HITBOX_W // 2,
             20 * config.TILE_SIZE + 8 - config.NPC_HITBOX_H // 2),
        ]
        assert scene.fencers[0]._pair_center == scene.fencers[1]._pair_center
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
    print("All Phase 7 sword-fighter tests passed.")


if __name__ == "__main__":
    _run_all()
