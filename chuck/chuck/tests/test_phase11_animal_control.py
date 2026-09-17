"""Phase 11 Animal Control officers and their net.

An officer is the undead pursuer's role wearing a uniform: the same
durability, the same contact damage, the same straightforward walk. The
one new thing is the net, and the phase document is specific about it --
Chuck cannot walk out, Sanity drains continuously to zero over four
seconds, the ordinary disappearance follows, the timing is stable across
frame rates, and it must not become a second death or respawn system.

Each of those is a test here, and the frame-rate one is the reason the
drain is computed from elapsed time rather than subtracted per frame.
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
from src.entities.animal_control import AnimalControlOfficer
from src.entities.undead import UndeadEnemy
from src.systems.net_capture import NetCapture
from src.world.tilemap import TileMap


MAP_NAME = "modern_city_day_2"


def _game_and_world(checkpoint=MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(checkpoint)
    world._arrival_fade_t = None
    return directory, game, world


def _snare(world):
    """Put an officer on top of Chuck and let the wind-up finish."""
    officer = next(enemy for enemy in world.undead
                   if isinstance(enemy, AnimalControlOfficer))
    officer.x = world.player.x
    officer.y = world.player.y
    officer.net_thrown = True
    world._check_net_capture()
    return officer


def test_an_officer_is_the_undead_role_in_a_uniform() -> None:
    assert config.ANIMAL_CONTROL_SANITY_DAMAGE == config.ZOMBIE_SANITY_DAMAGE
    assert config.ANIMAL_CONTROL_SCRATCHES == config.ZOMBIE_SCRATCHES

    directory, game, world = _game_and_world()
    try:
        officers = [enemy for enemy in world.undead
                    if isinstance(enemy, AnimalControlOfficer)]
        assert len(officers) == 2
        officer = officers[0]
        assert isinstance(officer, UndeadEnemy)
        assert officer.kind == "animal_control"
        assert officer.max_scratches == config.ANIMAL_CONTROL_SCRATCHES

        # It pursues like the rest of the role, and can be fought down.
        home = (officer.x, officer.y)
        world.player.x = officer.x + config.UNDEAD_NOTICE_RANGE * 2
        world.player.y = officer.y
        for _ in range(20):
            officer.update(0.05, world.player)
        assert (officer.x, officer.y) == home
        world.player.x = officer.x + config.UNDEAD_NOTICE_RANGE / 3
        for _ in range(20):
            officer.update(0.05, world.player)
        assert officer.x > home[0]

        for _ in range(config.ANIMAL_CONTROL_SCRATCHES):
            officer.on_scratched()
        assert not officer.alive
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_net_winds_up_before_it_catches() -> None:
    """A caught rat has always had a moment to see the net coming."""
    directory, game, world = _game_and_world()
    try:
        officer = next(enemy for enemy in world.undead
                       if isinstance(enemy, AnimalControlOfficer))
        officer.x = world.player.x
        officer.y = world.player.y
        assert officer.in_net_range(world.player)

        # In range, but the first frame only raises the net.
        officer.update(0.016, world.player)
        assert officer.winding_up
        world._check_net_capture()
        assert not world.net_capture.active

        # ...and it comes down once the wind-up runs out. The throw is a
        # single frame, so the scene has to be asked on every one.
        for _ in range(int(config.NET_WIND_UP_SECONDS / 0.05) + 4):
            officer.update(0.05, world.player)
            world._check_net_capture()
            if world.net_capture.active:
                break
        assert world.net_capture.active

        # The net is a close-range tool; it does not reach across a road.
        world.net_capture.clear()
        world.player.x = officer.x + config.NET_RANGE * 3
        assert not officer.in_net_range(world.player)
    finally:
        game._shutdown()
        directory.cleanup()


def test_being_netted_holds_chuck_and_drains_him_to_zero() -> None:
    directory, game, world = _game_and_world()
    try:
        world.sanity.current = world.sanity.maximum
        _snare(world)
        assert world.net_capture.active
        held = (world.player.x, world.player.y)

        # Walking is not an escape: input does not move him at all.
        game.input._actions_down.add("right")
        elapsed = 0.0
        while elapsed < config.NET_CAPTURE_SECONDS - 0.2:
            world.update(0.05)
            elapsed += 0.05
        assert (world.player.x, world.player.y) == held
        # ...and Sanity has been falling the whole time.
        assert 0 < world.sanity.current < world.sanity.maximum

        # At four seconds it reaches zero and the ordinary disappearance
        # takes over -- the same one a lethal fall uses.
        world.update(0.3)
        assert not world.net_capture.active
        assert world.sanity.current == 0
        assert world._respawn_phase is not None
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_drain_is_the_same_at_any_frame_rate() -> None:
    """Computed from elapsed time, so a lag spike cannot cheat it."""
    target = config.NET_CAPTURE_SECONDS / 2.0

    def drain_to(step):
        """Advance to the same wall-clock moment in different sized steps."""
        capture = NetCapture()
        capture.begin(config.SANITY_MAX)
        elapsed = 0.0
        last = config.SANITY_MAX
        while elapsed + step <= target:
            value = capture.advance(step)
            assert value is not None
            assert value <= last          # never goes back up
            last = value
            elapsed += step
        return last

    # A quarter-second frame and a 240Hz frame land in the same place.
    assert abs(drain_to(0.25) - drain_to(1.0 / 240.0)) <= 2
    assert abs(drain_to(0.5) - drain_to(1.0 / 60.0)) <= 2

    # One enormous frame still ends the hold rather than overshooting.
    capture = NetCapture()
    capture.begin(config.SANITY_MAX)
    assert capture.advance(config.NET_CAPTURE_SECONDS * 5) is None


def test_the_net_is_not_a_second_death_system() -> None:
    """It ends by depleting Sanity; respawning is the game's own."""
    directory, game, world = _game_and_world("modern_city_day_2")
    try:
        depletions = []
        real = world.sanity._on_depleted
        world.sanity._on_depleted = lambda: (depletions.append(1), real())[1]

        world.sanity.current = 40
        _snare(world)
        for _ in range(int(config.NET_CAPTURE_SECONDS / 0.05) + 4):
            world.update(0.05)
        # Exactly one depletion, through the ordinary hook.
        assert depletions == [1]
        assert world._respawn_phase is not None

        world.update(config.RESPAWN_FADE_OUT + 0.01)
        world.update(config.RESPAWN_HOLD + 0.01)
        assert world.sanity.current == config.SANITY_MAX
        assert not world.net_capture.active
    finally:
        game._shutdown()
        directory.cleanup()


def test_leaving_or_resetting_the_map_clears_the_net() -> None:
    directory, game, world = _game_and_world()
    try:
        _snare(world)
        assert world.net_capture.active
        world._reset_enemies()
        assert not world.net_capture.active

        _snare(world)
        assert world.net_capture.active
        world.load_map("modern_city_day_1", arrival="from_city_day_2")
        assert not world.net_capture.active
    finally:
        game._shutdown()
        directory.cleanup()


def test_officers_stand_where_they_can_be_walked_around() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    kinds = Counter(kind for kind, _ in tilemap.object_spawns)
    assert kinds["animal_control"] == 2

    ts = config.TILE_SIZE
    officers = [(int(x // ts), int(y // ts))
                for kind, (x, y) in tilemap.object_spawns
                if kind == "animal_control"]
    arrival = next((int(x // ts), int(y // ts))
                   for kind, (x, y) in tilemap.object_spawns
                   if kind.startswith("arrival:"))
    notice = config.UNDEAD_NOTICE_RANGE / ts
    # The arrival is not inside an officer's reach.
    for officer in officers:
        for safe in (arrival,):
            assert (abs(officer[0] - safe[0]) + abs(officer[1] - safe[1])
                    > notice), (officer, safe)
        # ...and each stands on pavement, not in a traffic lane.
        assert tilemap.terrain_at(*officer) != "="

    directory, game, world = _game_and_world()
    try:
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.update(0)
        world.draw(surface)          # the wind-up tell and net overlay draw
        _snare(world)
        world.draw(surface)
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
    print("All Animal Control tests passed.")


if __name__ == "__main__":
    _run_all()
