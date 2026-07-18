"""Pantry jar shelves are scratch-breakables that spill cigarette cartons.

The two Waterdeep pantry shelves stand forever (solid, human-scale
furniture), but their JARS break: one scratch rattles them all down into
glazed shards and spills a full carton — worth exactly
CARTON_CIGARETTE_COUNT (20) cigarettes — onto safe plain board. The
emptied shelf keeps drawing with its dedicated bare sprite.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.jar_shelf import PantryJarShelf
from src.entities.pickup import CigaretteCarton


def test_shelf_breaks_once_and_survives_its_debris_pass() -> None:
    shelf = PantryJarShelf(5, 2, drop=(88.0, 56.0))
    assert shelf.intact and shelf.alive
    shelf.on_scratched()
    assert not shelf.intact
    assert shelf.take_drop_position() == (88.0, 56.0)
    assert shelf.take_drop_position() is None  # exactly once
    shelf.on_scratched()  # a second swipe is absorbed silently
    assert shelf.take_drop_position() is None
    shelf.update(config.BREAKABLE_GRASS_DURATION + 0.1)
    assert shelf.alive  # the emptied shelf never leaves the room
    assert shelf.hitbox.width == 0  # but stops consuming scratches


def test_shelf_reward_is_a_twenty_cigarette_carton() -> None:
    shelf = PantryJarShelf(5, 2, drop=(88.0, 56.0))

    class FakeAssets:
        def image(self, path):
            return pygame.Surface((12, 8), pygame.SRCALPHA)

    pygame.init()
    carton = shelf.create_pickup((88.0, 56.0), FakeAssets())
    assert isinstance(carton, CigaretteCarton)
    assert carton.cigarette_count == config.CARTON_CIGARETTE_COUNT == 20


def test_pantry_builds_both_shelves_as_breakables_on_safe_drops() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("pantry_default")
        scene._arrival_fade_t = None
        shelves = [b for b in scene.breakables
                   if isinstance(b, PantryJarShelf)]
        assert len(shelves) == 2
        assert not any(p.kind == "pantry_shelf" for p in scene.props)
        ts = config.TILE_SIZE
        for shelf in shelves:
            col, row = int(shelf._drop[0] // ts), int(shelf._drop[1] // ts)
            # Every carton lands on plain walkable board — never on an
            # Astral fall tile, the sky, or inside furniture.
            assert scene.tilemap.terrain_at(col, row) == "p"
        # The left shelf stands directly above an Astral tile at (3, 3);
        # its drop must sidestep it.
        left = next(s for s in shelves if int(s._center_x // ts) == 3)
        assert (int(left._drop[0] // ts), int(left._drop[1] // ts)) != (3, 3)
    finally:
        game._shutdown()


def test_scratching_a_shelf_spills_a_collectable_carton() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("pantry_default")
        scene._arrival_fade_t = None
        ts = config.TILE_SIZE
        # Stand beneath the right shelf at (22, 2), facing up, low on
        # sanity. The carton spills onto Chuck's own tile, so the same
        # frame collects it: twenty cigarettes at once, clamped at full.
        scene.player.x, scene.player.y = 22 * ts + 3, 3 * ts + 1
        scene.player.facing = "up"
        scene.sanity.current = 15
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.01)
        shelf = next(b for b in scene.breakables
                     if isinstance(b, PantryJarShelf)
                     and int(b._center_x // ts) == 22)
        assert not shelf.intact
        assert scene.sanity.current == scene.sanity.maximum
        assert scene.tilemap.is_solid(22, 2)  # the shelf still blocks
        scene.update(config.BREAKABLE_GRASS_DURATION + 0.1)
        assert shelf in scene.breakables  # emptied, not removed
    finally:
        game._shutdown()


def test_shelves_restock_on_reload() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("pantry_default")
        scene._arrival_fade_t = None
        for shelf in [b for b in scene.breakables
                      if isinstance(b, PantryJarShelf)]:
            shelf.on_scratched()
        scene = game.checkpoints.load_checkpoint("pantry_default")
        shelves = [b for b in scene.breakables
                   if isinstance(b, PantryJarShelf)]
        assert len(shelves) == 2 and all(s.intact for s in shelves)
    finally:
        game._shutdown()


def test_empty_shelf_sprite_is_authored_and_matches_the_stocked_size() -> None:
    stocked = pygame.image.load(
        config.SPRITES_DIR / "objects" / "pantry_shelf.png")
    empty = pygame.image.load(
        config.SPRITES_DIR / "objects" / "pantry_shelf_empty.png")
    assert stocked.get_size() == empty.get_size() == (28, 24)


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
    print("All pantry jar tests passed.")


if __name__ == "__main__":
    _run_all()
