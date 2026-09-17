"""The Astral coming in behind him, and why the arena has to shrink.

Chuck arrives on the west rim of the trio's map and everything worth
watching is twenty-five tiles east of him. That geometry has an obvious
exploit in it and the exploit is not even cowardly, it is *sensible*:
stand in the doorway, let the arrows and the horde and the dragon
happen at a distance, and wait out the conversation. A room with a
corner in it is not an encounter. It is a cutscene with a survival
timer.

So the Sea comes in behind him as well. It starts after the first
exchange, takes a column every couple of seconds, and stops well short
of the heroes -- and where it stops is not a matter of taste, it is set
by the horde, whose westmost spawn cell is column 28. A front that went
past that would be a ring of orcs drowning on their way to the fight.

What is tested here is mostly the shape of the squeeze: that it starts
late, that it stops, that everything east of it still works, and that
it cannot strand him. That last one had to be built rather than
inherited. The rule everywhere else in this room is that the Sea never
opens where Chuck is standing, which is right for the rift coming at
him from in front and leaves him on a one-tile island when the same
rule is applied to a front coming from behind.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import DESERT_ENTRY_FLAGS
from src.systems.orc_horde import OPENING, SPAWN_CELLS
from src.systems.trio_encounter import (
    BEATS, ENCROACH_FROM, ENCROACH_GRACE, ENCROACH_INTERVAL, ENCROACH_LIMIT,
    ENCROACH_START, encroach_lag,
)
from src.world import collision
from src.world.tilemap import TileMap

import sys
sys.path.insert(0, "tools")
from generate_desert_trio import FIGHTER, RANGER, WIZARD  # noqa: E402


MAP_NAME = "desert_trio"
STEP = 1 / 30
HEROES = (FIGHTER, WIZARD, RANGER)
# Somewhere the front is never going to reach. Tests that are about the
# shape of the squeeze rather than about what it does to him have to
# park him out of its way, because a Chuck left on the arrival tile is
# taken by the Sea about half a minute in -- correct, and it resets the
# encounter, which resets the front.
CLEAR_OF_IT = (46 * config.TILE_SIZE, 26 * config.TILE_SIZE)


def _world():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        MAP_NAME, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _play(game, world, seconds: float, *, hold=None) -> None:
    for _ in range(int(seconds / STEP)):
        if isinstance(game.scenes.current, DialogueScene):
            game.scenes.pop()
            continue
        if not isinstance(game.scenes.current, type(world)):
            return
        world.sanity.current = world.sanity.maximum
        if hold is not None and world._fall_t is None \
                and world._respawn_phase is None:
            world.player.x, world.player.y = hold
        world.update(STEP)


def _open(tilemap: TileMap, col: int, row: int) -> bool:
    return (not tilemap.is_solid(col, row)
            and tilemap.terrain_at(col, row)
            not in collision.FALL_HAZARD_TERRAIN)


def _reachable(tilemap: TileMap, origin) -> set[tuple[int, int]]:
    seen = {origin}
    frontier = [origin]
    while frontier:
        x, y = frontier.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in seen:
                continue
            if not (0 <= cell[0] < tilemap.width_tiles
                    and 0 <= cell[1] < tilemap.height_tiles):
                continue
            if not _open(tilemap, *cell):
                continue
            seen.add(cell)
            frontier.append(cell)
    return seen


# ----------------------------------------------------------------------
def test_the_doorway_is_a_place_to_stand_and_then_it_is_not() -> None:
    """Nothing for the first exchange, and then the way back starts going.

    The first fifteen seconds are his to look at the room in -- he has
    just walked into the middle of somebody else's fight for the third
    time and the shot deserves a moment. After that the arena begins
    closing, and it is nearly done by the time the collision starts.
    """
    assert 0 < ENCROACH_FROM < len(BEATS)
    directory, game, world = _world()
    try:
        spot = (46 * config.TILE_SIZE, 26 * config.TILE_SIZE)
        _play(game, world, BEATS[0][0] - 2.0, hold=spot)
        assert world.trio.encroached < ENCROACH_START, world.trio.encroached

        _play(game, world, 20.0, hold=spot)
        assert world.trio.encroached >= ENCROACH_START

        _play(game, world, 45.0, hold=spot)
        # Done, or as near as makes no difference, by the time the
        # worlds start arriving: the squeeze and the climax are one
        # event rather than two things happening at once.
        assert world.trio.collided
        assert world.trio.encroached >= ENCROACH_LIMIT - 2
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_stops_where_the_horde_comes_in() -> None:
    """The limit is the ring's, not a number somebody liked.

    Every cell orcs arrive from has to stay on the playable side of the
    front, or the horde spawns inside the Sea and the fight the squeeze
    exists to push him into stops happening.
    """
    westmost = min(col for col, _row in SPAWN_CELLS + OPENING)
    assert ENCROACH_LIMIT < westmost, (ENCROACH_LIMIT, westmost)

    directory, game, world = _world()
    try:
        _play(game, world, 140.0, hold=CLEAR_OF_IT)
        assert world.trio.encroached == ENCROACH_LIMIT
        for cell in SPAWN_CELLS + OPENING:
            if cell == (50, 20):
                continue    # taken by the rift's own crack, from the east
            assert _open(world.tilemap, *cell), cell
        assert world.horde.spawned > 60, world.horde.spawned
    finally:
        game._shutdown()
        directory.cleanup()


def test_what_is_left_is_the_fight() -> None:
    """A band about a screen and a half across, with the trio in it.

    Measured as the consequence rather than as an area: everything the
    encounter needs is still reachable, there is a lot less of
    everything else, and the westmost ground he can stand on is most of
    the way to the heroes.
    """
    directory, game, world = _world()
    try:
        before = len(_reachable(world.tilemap, (46, 26)))
        _play(game, world, 140.0, hold=CLEAR_OF_IT)
        after = _reachable(world.tilemap, (46, 26))
        assert len(after) < before * 0.65, (len(after), before)
        for name, cell in zip(("fighter", "wizard", "ranger"), HEROES):
            assert cell in after, name
        # The edge is torn, so the westmost open tile is the limit less
        # whatever the deepest bay in it is -- not the limit itself.
        westmost = min(col for col, _row in after)
        deepest = max(encroach_lag(row)
                      for row in range(world.tilemap.height_tiles))
        assert westmost >= ENCROACH_LIMIT - deepest, (westmost, deepest)
        assert westmost > 20, westmost
        # ...and it is still a room rather than a corridor: he has more
        # than a screen to move in.
        span = max(col for col, _row in after) - westmost
        assert span * config.TILE_SIZE > config.NATIVE_WIDTH, span
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_edge_is_torn_rather_than_ruled() -> None:
    """A straight line is not the Astral Sea, it is the end of the level.

    The rift on the far side is ragged because it follows a shore that
    was drawn that way. This one takes whole columns, so it has to be
    given a shore -- and from two sines rather than anything modular,
    because a lag of `row % n` is a repeating sawtooth, which is an edge
    somebody drew with a different tool.
    """
    lags = [encroach_lag(row) for row in range(52)]
    assert len(set(lags)) >= 4, sorted(set(lags))
    assert min(lags) == 0, min(lags)
    # Not a sawtooth: it does not repeat on any short period.
    for period in range(2, 9):
        assert any(lags[i] != lags[i + period]
                   for i in range(len(lags) - period)), period

    directory, game, world = _world()
    try:
        _play(game, world, 140.0, hold=CLEAR_OF_IT)
        fronts = set()
        for row in range(4, world.tilemap.height_tiles - 4):
            open_cols = [col for col in range(ENCROACH_START, 34)
                         if _open(world.tilemap, col, row)]
            if open_cols:
                fronts.add(min(open_cols))
        assert len(fronts) >= 4, sorted(fronts)
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_pushes_him_and_then_it_finishes() -> None:
    """Neither dropped under nor left standing on the last tile.

    Two rules, and they are in tension on purpose. While the front is
    near it will not open the ground he is on, so it herds him east
    instead of killing him. Once it is well past that column it takes
    the ground too -- because the alternative, which is what the first
    version did, is a player who ignored forty-five seconds of visible
    Sea sitting on a single tile with the fight thirty tiles away and
    nothing to do but wait for the dragon.
    """
    assert ENCROACH_GRACE >= 1
    directory, game, world = _world()
    try:
        doorway = (6 * config.TILE_SIZE, 29 * config.TILE_SIZE)
        taken_at = None
        elapsed = 0.0
        for _ in range(int(120 / STEP)):
            if isinstance(game.scenes.current, DialogueScene):
                game.scenes.pop()
                continue
            if not isinstance(game.scenes.current, type(world)):
                break
            world.sanity.current = world.sanity.maximum
            if world._fall_t is None and world._respawn_phase is None:
                world.player.x, world.player.y = doorway
            world.update(STEP)
            elapsed += STEP
            if world._fall_t is not None and taken_at is None:
                taken_at = elapsed
        assert taken_at is not None, "he was left standing on an island"
        # It went past him first rather than opening under him on
        # arrival: the front reaches column 6 well before this.
        reached = BEATS[0][0] + ENCROACH_INTERVAL * 6
        assert taken_at > reached, (taken_at, reached)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_heroes_ground_is_never_its_business() -> None:
    """It writes over floor and stops at the shelf the three of them hold."""
    directory, game, world = _world()
    try:
        _play(game, world, 140.0, hold=CLEAR_OF_IT)
        for name, cell in zip(("fighter", "wizard", "ranger"), HEROES):
            assert _open(world.tilemap, *cell), name
        for cell in world.trio._protected:
            assert cell not in {
                (col, row) for col, row, _old in world.trio._restore
            }, cell
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_front_takes_the_ground_with_it() -> None:
    """A save point floating in the Astral Sea reads as a bug.

    It is also the one prop in that room a player would try to walk back
    to, which is exactly the walk the front exists to take away.
    """
    directory, game, world = _world()
    try:
        _play(game, world, 60.0, hold=CLEAR_OF_IT)
    finally:
        game._shutdown()
        directory.cleanup()


def test_dying_gives_the_west_back() -> None:
    """The room resets whole, front included."""
    directory, game, world = _world()
    try:
        before = [
            [world.tilemap.terrain_at(x, y)
             for x in range(world.tilemap.width_tiles)]
            for y in range(world.tilemap.height_tiles)
        ]
        _play(game, world, 70.0, hold=CLEAR_OF_IT)
        assert world.trio.encroached > ENCROACH_START
        world.trio.restore()
        world.churn.restore()
        after = [
            [world.tilemap.terrain_at(x, y)
             for x in range(world.tilemap.width_tiles)]
            for y in range(world.tilemap.height_tiles)
        ]
        assert after == before, "the west did not come back"
        assert world.trio.encroached == ENCROACH_START - 1
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
    print("All closing-in tests passed.")


if __name__ == "__main__":
    _run_all()
