"""The final collision sequence: everywhere arriving at once.

When the wizard says "Good enough", the desert stops being a desert.
The phase document asks for it to be overwhelmed by fragments of
locations from throughout the game, in large sections that change
rapidly, and then adds the constraint that makes the whole thing
buildable: the player must still be able to read Chuck and the
immediate hazards, and readability must not be spent on spectacle.

The way those two live together is that the churn only ever writes
*floors*. It cannot kill him, cannot block him, and cannot take a route
away -- what changes is what he is standing on, several tiles at a
time, quicker every few seconds. That is one claim with three
consequences, and all three are worth measuring rather than trusting,
because the failure mode is not a crash: it is a section of lava
arriving under a player who had nowhere to be.

The rest is timing. It must not start before the wizard has found what
he was looking for, it must accelerate, and dying must put the arena
back. The two exchanges after that -- the resolution -- play over the
top of it, which is the point: the collision is what the heroes'
success looks like from the outside, and they talk through it.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import DESERT_ENTRY_FLAGS
from src.systems.trio_encounter import (
    BEATS, CHURN_FASTEST, CHURN_FIRST, CHURN_FLOORS, CHURN_FROM,
    CHURN_MIN, WorldChurn,
)
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap

import sys
sys.path.insert(0, "tools")
from generate_desert_trio import FIGHTER, RANGER, WIZARD  # noqa: E402


MAP_NAME = "desert_trio"
# Somewhere the Astral coming in from the west is never going to reach.
# These tests were written when a player could stand on the arrival tile
# for the whole encounter; the front takes that ground about half a
# minute in now, which kills him and restarts the conversation. Correct,
# and the entire point of the front -- and useless for a test about what
# the rift does or what gets said in what order.
CLEAR_OF_IT = (46 * config.TILE_SIZE, 26 * config.TILE_SIZE)
PROTECTED = {FIGHTER, WIZARD, RANGER}


def _tilemap() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _world():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        MAP_NAME, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _snapshot(tilemap: TileMap):
    return [
        [tilemap.terrain_at(x, y) for x in range(tilemap.width_tiles)]
        for y in range(tilemap.height_tiles)
    ]


def _run_churn(seconds: float = 90.0):
    """A churn on its own tilemap, with nothing else touching it."""
    tilemap = _tilemap()
    churn = WorldChurn(tilemap, PROTECTED)
    for _ in range(int(seconds / (1 / 30))):
        churn.update(1 / 30)
    return tilemap, churn


def test_nothing_it_writes_can_hurt_anybody() -> None:
    """The whole safety argument, checked tile by tile.

    A churn that could write lava or Astral Sea would be a room where
    the ground kills you at random, and no amount of telegraphing makes
    that survivable when it is arriving nine tiles at a time. So every
    terrain it is allowed to write is walkable, and every tile it
    actually wrote is checked against that.
    """
    for char in CHURN_FLOORS:
        tile = TILE_DEFS[char]
        assert not tile.solid, char
        assert char not in collision.FALL_HAZARD_TERRAIN, char

    tilemap, churn = _run_churn()
    assert churn.sections > 20, churn.sections
    assert churn._restore, "nothing changed at all"
    for (col, row) in churn._restore:
        char = tilemap.terrain_at(col, row)
        assert char in CHURN_FLOORS, (col, row, char)
        assert not tilemap.is_solid(col, row), (col, row)
        assert char not in collision.FALL_HAZARD_TERRAIN, (col, row)


def test_it_leaves_the_map_it_found_alone() -> None:
    """Everything that is not a floor stays exactly where it was.

    The rift, the lava veins, the rim, and the ground the three of them
    are standing on. Each of those is load-bearing in a different way
    and none of them is the churn's business -- it is weather over the
    floor, not an edit to the room.
    """
    before = _snapshot(_tilemap())
    tilemap, _churn = _run_churn()
    after = _snapshot(tilemap)

    for y, row in enumerate(before):
        for x, char in enumerate(row):
            if char in CHURN_FLOORS and (x, y) not in PROTECTED:
                continue
            assert after[y][x] == char, (x, y, char, after[y][x])

    for name, cell in (("fighter", FIGHTER), ("wizard", WIZARD),
                       ("ranger", RANGER)):
        assert after[cell[1]][cell[0]] == before[cell[1]][cell[0]], name

    # ...and it did do something: most of the arena's floor changed.
    changed = sum(
        1 for y, row in enumerate(before) for x, char in enumerate(row)
        if after[y][x] != char
    )
    assert changed > 400, changed


def test_the_way_through_is_never_taken_away() -> None:
    """Readability's other half: he can still get everywhere.

    The document's warning is about what the player can see, but the
    version that actually bites is what the player can reach. A churn
    that wrote solid ground would close routes without anything on
    screen looking wrong.
    """
    def reachable(tilemap: TileMap) -> set[tuple[int, int]]:
        ts = config.TILE_SIZE
        arrival = next(p for k, p in tilemap.object_spawns
                       if k == "arrival:from_east_8")
        origin = (int(arrival[0]) // ts, int(arrival[1]) // ts)
        seen = {origin}
        frontier = [origin]
        while frontier:
            x, y = frontier.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                cell = (x + dx, y + dy)
                if cell in seen or tilemap.is_solid(*cell):
                    continue
                if tilemap.terrain_at(*cell) in collision.FALL_HAZARD_TERRAIN:
                    continue
                seen.add(cell)
                frontier.append(cell)
        return seen

    start = reachable(_tilemap())
    tilemap, _churn = _run_churn()
    assert reachable(tilemap) == start, "the collision closed a route"


def test_the_sections_are_large_and_they_speed_up() -> None:
    """Large, because the document says large; faster, because it builds.

    A churn that repaints a tile at a time is a shimmer. What is wanted
    is whole pieces of somewhere else arriving, and more of them as the
    heroes close in on finishing.
    """
    tilemap = _tilemap()
    churn = WorldChurn(tilemap, PROTECTED)
    assert churn.interval == CHURN_FIRST

    sizes, intervals = [], []
    for _ in range(int(90 / (1 / 30))):
        churn.update(1 / 30)
        for left, top, span_w, span_h, age in churn.flashes:
            if age < 1 / 15:
                sizes.append((span_w, span_h))
        intervals.append(churn.interval)

    assert sizes, "no section ever announced itself"
    assert min(w for w, _ in sizes) >= CHURN_MIN[0], sizes
    assert min(h for _, h in sizes) >= CHURN_MIN[1], sizes
    assert intervals == sorted(intervals, reverse=True), "it did not build"
    assert intervals[-1] == CHURN_FASTEST, intervals[-1]
    # ...and it is not one enormous section repeated: several worlds
    # arrive, which is the point of the sequence.
    floors = {tilemap.terrain_at(col, row)
              for col, row in churn._restore}
    assert len(floors) >= 5, floors


def test_it_waits_until_the_wizard_has_found_it() -> None:
    """Nothing before "Good enough", everything after it.

    The sequence is what the heroes' success looks like from the
    outside. Started earlier it would be a room falling apart for no
    stated reason, which is the opposite of what the script is doing --
    and the two exchanges that follow play over the top of it, because
    that is when there is something for them to be reacting to.
    """
    directory, game, world = _world()
    try:
        assert world.churn is not None
        # Through the entrance lines and the first two beats.
        for _ in range(int(40 / (1 / 30))):
            if isinstance(game.scenes.current, DialogueScene):
                game.scenes.pop()
                continue
            world.sanity.current = world.sanity.maximum
            world.player.x, world.player.y = CLEAR_OF_IT
            world.update(1 / 30)
        assert world.trio.beats_played >= 1
        assert not world.trio.finished
        assert world.churn.sections == 0, world.churn.sections

        for _ in range(int(90 / (1 / 30))):
            if isinstance(game.scenes.current, DialogueScene):
                game.scenes.pop()
                continue
            world.sanity.current = world.sanity.maximum
            world.player.x, world.player.y = CLEAR_OF_IT
            world.update(1 / 30)
        assert world.trio.collided
        assert world.churn.sections > 10, world.churn.sections
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_same_encounter_twice_is_the_same_encounter() -> None:
    """Fixed sequence, not a random one.

    A map is generated once and read many times, and a churn that
    differs per run is a churn nobody can tell is working -- including
    the person who has to decide whether the last change improved it.
    """
    first_map, first = _run_churn(45.0)
    second_map, second = _run_churn(45.0)
    assert first.sections == second.sections
    assert _snapshot(first_map) == _snapshot(second_map)


def test_dying_puts_the_arena_back() -> None:
    """Everything the collision did, undone, the same as the rift's."""
    before = _snapshot(_tilemap())
    tilemap, churn = _run_churn(45.0)
    assert _snapshot(tilemap) != before
    churn.restore()
    assert _snapshot(tilemap) == before
    assert churn.sections == 0
    assert churn.interval == CHURN_FIRST


def test_it_only_runs_where_the_heroes_are() -> None:
    """No churn on any other map, and none without a trio on it."""
    directory, game, world = _world()
    try:
        elsewhere = game.checkpoints.load_checkpoint(
            "desert_east_8", progress_flags=set(DESERT_ENTRY_FLAGS))
        assert elsewhere.churn is None
        assert elsewhere.trio is None
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_arriving_sections_are_drawn_as_outlines() -> None:
    """Announced, and only announced.

    Filled, the flash washed the section it was announcing, and the
    thing a player most needs to keep track of in this room is where
    their own feet are. So it is an outline, and it is brief.
    """
    directory, game, world = _world()
    try:
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        drew = False
        for _ in range(int(140 / (1 / 30))):
            if isinstance(game.scenes.current, DialogueScene):
                game.scenes.pop()
                continue
            world.sanity.current = world.sanity.maximum
            world.player.x, world.player.y = CLEAR_OF_IT
            world.update(1 / 30)
            if world.churn.flashes:
                left, top, _w, _h, _age = world.churn.flashes[0]
                world.camera.focus_on(left * config.TILE_SIZE,
                                      top * config.TILE_SIZE)
                world.draw(surface)
                drew = True
                break
        assert drew, "no section ever announced itself on screen"
        # The flash is short: nothing is still outlined a second later.
        for _ in range(int(1.0 / (1 / 30))):
            world.churn.update(1 / 30)
        assert not [f for f in world.churn.flashes if f[4] > 0.5]
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_beats_and_the_collision_are_the_same_encounter() -> None:
    """One clock, one arena, one reset.

    They are separate objects because they do separate things, but a
    player dying in the middle should get the whole room back rather
    than a healed floor with the conversation already spent.
    """
    assert [name for _, name in BEATS][CHURN_FROM - 1] == "trio_found_it"
    directory, game, world = _world()
    try:
        assert world.trio is not None and world.churn is not None
        assert world.churn._protected == world.trio._protected
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
    print("All final collision tests passed.")


if __name__ == "__main__":
    _run_all()
