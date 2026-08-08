"""Phase 11 police officers: the spined devil's lane, with a warning.

The phase document asks to reuse the established projectile architecture
where practical, so a bullet *is* a spine -- the same travel, the same
"stops dead against solid geometry" rule -- retuned faster and smaller.
The one thing added is the tell: an officer raises his weapon for most
of a second before every shot, which is the difference between a hazard
to route around and an ambush.

Chuck gains nothing ranged of his own, and these tests check that too.
"""

from collections import Counter
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.police import Bullet, PoliceOfficer
from src.entities.spined_devil import FlamingSpine
from src.world.tilemap import TileMap


MAP_NAME = "modern_city_day_2"


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(checkpoint)
    world._arrival_fade_t = None
    return directory, game, world


def _fire(officer):
    """Run the cadence until the officer produces a round."""
    for _ in range(int(config.POLICE_INTERVAL / 0.02) + 20):
        bullet = officer.update(0.02)
        if bullet is not None:
            return bullet
    raise AssertionError("the officer never fired")


def test_a_bullet_is_the_spined_devils_projectile_retuned() -> None:
    bullet = Bullet(100.0, 100.0, "right")
    assert isinstance(bullet, FlamingSpine)
    assert bullet.damage == config.BULLET_SANITY_DAMAGE
    assert bullet.speed == config.BULLET_SPEED
    # Faster and smaller than the spine it inherits from.
    assert config.BULLET_SPEED > config.SPINE_SPEED
    assert bullet.width < config.SPINE_HITBOX_LONG

    # A horizontal round is long across, a vertical one long down.
    down = Bullet(100.0, 100.0, "down")
    assert bullet.width > bullet.height
    assert down.height > down.width


def test_an_officer_aims_before_every_shot() -> None:
    officer = PoliceOfficer(100.0, 100.0, "right")
    # The tell is up for the last stretch before each shot, and the
    # officer is not aiming for the whole of the rest of the cycle.
    saw_aiming = saw_quiet = False
    for _ in range(int(config.POLICE_INTERVAL * 2 / 0.02)):
        if officer.aiming:
            saw_aiming = True
        else:
            saw_quiet = True
        officer.update(0.02)
    assert saw_aiming and saw_quiet

    # And the aim really does immediately precede the round.
    officer = PoliceOfficer(100.0, 100.0, "right")
    aiming_before_shot = False
    for _ in range(int(config.POLICE_INTERVAL * 2 / 0.02)):
        was_aiming = officer.aiming
        if officer.update(0.02) is not None:
            aiming_before_shot = was_aiming
            break
    assert aiming_before_shot


def test_bullets_travel_the_lane_and_stop_at_city_geometry() -> None:
    directory, game, world = _game_and_world()
    try:
        officer = world.police[0]
        bullet = _fire(officer)
        start = (bullet.x, bullet.y)
        for _ in range(6):
            bullet.update(0.02, world.tilemap)
        assert (bullet.x, bullet.y) != start
        assert bullet.alive

        # Fired into a wall, a round dies rather than passing through.
        wall = next(
            (col, row)
            for row in range(world.tilemap.height_tiles)
            for col in range(world.tilemap.width_tiles)
            if world.tilemap.is_solid(col, row)
        )
        blocked = Bullet((wall[0] - 1) * config.TILE_SIZE + 8,
                         wall[1] * config.TILE_SIZE + 8, "right")
        for _ in range(20):
            blocked.update(0.02, world.tilemap)
            if not blocked.alive:
                break
        assert not blocked.alive
    finally:
        game._shutdown()
        directory.cleanup()


def test_a_round_costs_sanity_and_is_spent_on_the_hit() -> None:
    directory, game, world = _game_and_world("modern_city_day_2_anchor")
    try:
        bullet = Bullet(world.player.hitbox.centerx,
                        world.player.hitbox.centery, "right")
        world.bullets.append(bullet)
        world.sanity.current = world.sanity.maximum
        world.update(0.001)
        assert world.sanity.current == (
            world.sanity.maximum - config.BULLET_SANITY_DAMAGE)
        # The round is spent: it does not keep hitting him.
        assert bullet not in world.bullets
    finally:
        game._shutdown()
        directory.cleanup()


def test_officers_hold_their_post_and_reset_with_the_map() -> None:
    directory, game, world = _game_and_world()
    try:
        assert len(world.police) == 2
        posts = [(officer.x, officer.y) for officer in world.police]
        for _ in range(60):
            world.update(0.05)
        # Stationary hazards: they never chase.
        assert [(officer.x, officer.y) for officer in world.police] == posts
        assert world.bullets              # ...but the lanes are live

        world._reset_enemies()
        assert len(world.police) == 2
        assert not world.bullets
        assert [(officer.x, officer.y) for officer in world.police] == posts
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_lanes_never_point_at_the_ashtray_or_the_arrival() -> None:
    """A hazard to route around must not fire on a respawn point."""
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    ts = config.TILE_SIZE
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert sum(count for kind, count in kinds.items()
               if kind.startswith("police:")) == 2

    def tile(position):
        return (int(position[0] // ts), int(position[1] // ts))

    safe = {tile(pos) for kind, pos in tilemap.object_spawns
            if kind.startswith(("anchor:", "arrival:"))}
    vectors = {"left": (-1, 0), "right": (1, 0),
               "up": (0, -1), "down": (0, 1)}
    for kind, position in tilemap.object_spawns:
        if not kind.startswith("police:"):
            continue
        col, row = tile(position)
        # Officers stand on pavement, not in a live traffic lane.
        assert tilemap.terrain_at(col, row) != "="
        dc, dr = vectors[kind.split(":", 1)[1]]
        for step in range(1, 40):
            point = (col + dc * step, row + dr * step)
            if not (0 <= point[0] < tilemap.width_tiles
                    and 0 <= point[1] < tilemap.height_tiles):
                break
            if tilemap.is_solid(*point):
                break
            assert point not in safe, (kind, point)


def test_chuck_never_gains_a_ranged_attack() -> None:
    """Police are scenery with consequences, not a shooting gallery."""
    from src.entities.player import Player

    for name in dir(Player):
        assert "shoot" not in name and "fire" not in name, name

    directory, game, world = _game_and_world()
    try:
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)          # the aim tell and muzzle flash draw
        for _ in range(40):
            world.update(0.05)
        world.draw(surface)
        # Scratching an officer does nothing: they are not fightable.
        officer = world.police[0]
        assert not hasattr(officer, "on_scratched")
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
    print("All police tests passed.")


if __name__ == "__main__":
    _run_all()
