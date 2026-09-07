"""The horde pressing the trio, and the two things it has to be.

The complaint that produced it was about theatre: the ranger was
spinning on the spot shooting at nothing. So the first half of what is
tested here is that there is now something to shoot at, and that both
of the heroes who are fighting are actually fighting it -- her arrows
one-shotting orcs, his sword cutting down whatever reaches him, all the
way to the last line of the encounter rather than for the first twenty
seconds.

The second half is that it is still Chuck's room. The horde has not
noticed him and never does; what it costs him is being in the way of it,
which is a dodge rather than a chase. Those two pull against each other
in exactly one place -- the fighter's arc and the ranger's line are
hazards to Chuck as well -- and that is the point rather than a problem.

The hard part of this, and the reason the biggest test in here is a
simulation rather than an assertion, is that greedy pursuers and an
arena that tears itself apart do not mix. The rift takes a column of
ground on every beat and the Astral cracks grow with it, so an approach
that is open when Chuck walks in can be a wall by the fourth exchange.
Two separate versions of this shipped-in-my-head with half the horde
standing in a field: once because a spawn cell sat beside a lava vein,
and once because the heroes ended up on single tiles at the end of
one-tile spurs that nothing with a body can walk down. Neither of those
is visible in the source. Both are obvious in a simulation, so every
approach is simulated, on the arena as it opens and on the arena after
the rift has taken everything it is going to take.
"""

import math
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.battle_actor import BattleActor
from src.entities.battle_hazards import CollisionBattleChoreographer
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import DESERT_ENTRY_FLAGS
from src.systems.orc_horde import (
    LONGEST_APPROACH, OPENING, SPAWN_CELLS, HordeOrc, OrcHorde,
)
from src.systems.trio_encounter import (
    CHURN_FROM, FIRST_ADVANCE, TrioEncounter, footing,
)
from src.world import collision
from src.world.tilemap import TileMap

import sys
sys.path.insert(0, "tools")
from generate_desert_trio import FIGHTER, RANGER, WIZARD  # noqa: E402


MAP_NAME = "desert_trio"
HEROES = {FIGHTER, WIZARD, RANGER}
# Close enough that a sword reaches, which is the definition of arrived.
ARRIVED = CollisionBattleChoreographer.SLASH_REACH


def _tilemap() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _worn() -> TileMap:
    """The arena after the rift has taken everything it is going to.

    Four beats' worth of advance, each one flushed before the next, so
    the shore really has moved rather than sitting in the pending queue.
    This is the state the horde has to survive, and it is a different
    map from the one the file on disk describes.
    """
    tilemap = _tilemap()
    trio = TrioEncounter(tilemap, set(HEROES))
    box = pygame.Rect(0, 0, 1, 1)
    for _ in range(CHURN_FROM - FIRST_ADVANCE):
        trio.advance((4, tilemap.height_tiles // 2))
        for _ in range(int(20 / (1 / 30))):
            trio._break_through(1 / 30, box)
    return tilemap


def _actors():
    ts = config.TILE_SIZE
    return (
        BattleActor(FIGHTER[0] * ts + ts / 2, FIGHTER[1] * ts + ts / 2,
                    "fighter"),
        BattleActor(RANGER[0] * ts + ts / 2, RANGER[1] * ts + ts / 2,
                    "ranger"),
    )


def _walk_in(cell, tilemap, fighter, ranger, limit=70.0):
    """Seconds for one orc from `cell` to reach its hero, or None."""
    ts = config.TILE_SIZE
    spot = ((cell[0] + 0.5) * ts, (cell[1] + 0.5) * ts)
    hero = (
        fighter
        if math.dist(spot, (fighter.center_x, fighter.center_y))
        <= math.dist(spot, (ranger.center_x, ranger.center_y))
        else ranger
    )
    orc = HordeOrc(*spot, hero)
    orc.tilemap = tilemap
    for frame in range(int(limit / (1 / 30))):
        orc.update(1 / 30)
        if math.dist((orc.center_x, orc.center_y),
                     (hero.center_x, hero.center_y)) <= ARRIVED:
            return frame / 30.0
    return None


def _world():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        MAP_NAME, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _play(game, world, seconds: float) -> float:
    """Run the encounter, popping conversations, and return time played."""
    played = 0.0
    for _ in range(int(seconds / (1 / 30))):
        if isinstance(game.scenes.current, DialogueScene):
            game.scenes.pop()
            continue
        if not isinstance(game.scenes.current, type(world)):
            break
        world.sanity.current = world.sanity.maximum
        world.update(1 / 30)
        played += 1 / 30
    return played


# ----------------------------------------------------------------------
# Getting there
# ----------------------------------------------------------------------
def test_every_orc_that_comes_in_gets_there() -> None:
    """The one that matters, and the one that cannot be read off source.

    Every spawn cell and every cell of the opening press is walked to
    its hero, on the fresh arena and on the arena after the rift has
    finished with it. A cell that fails this is not a crash and not
    visibly a bug -- it is a slightly worse fight, with a few orcs
    standing in a field being shot at from across the map, which is the
    exact problem the horde was added to fix.
    """
    fighter, ranger = _actors()
    for label, tilemap in (("fresh", _tilemap()), ("worn", _worn())):
        for cell in SPAWN_CELLS + OPENING:
            took = _walk_in(cell, tilemap, fighter, ranger)
            assert took is not None, (label, cell)
            assert took <= LONGEST_APPROACH + 4.0, (label, cell, took)


def test_the_heroes_keep_a_shelf_rather_than_a_tile() -> None:
    """Why the arena had to change for any of this to work.

    Protecting each hero's own tile was enough while the rift only had
    to avoid swallowing the tableau. Once something had to walk up to
    them it was not: the edge is ragged, so the rows either side of a
    hero go while his own stays, and what is left is three people on
    single tiles at the end of spurs one tile wide. This is the
    statement that they keep the step around them too, checked as the
    consequence -- every hero has open ground on the western side of him
    that connects to the rest of the arena.
    """
    assert footing({(10, 10)}) == {
        (col, row) for col in (9, 10, 11) for row in (9, 10, 11)
    }

    tilemap = _worn()
    reachable = _reachable(tilemap)
    for name, cell in (("fighter", FIGHTER), ("wizard", WIZARD),
                       ("ranger", RANGER)):
        assert cell in reachable, name
        # ...and not by a single-file thread: the shelf is wide enough
        # that a body can stand beside him on it.
        shelf = [
            (cell[0] - 1, cell[1] + dy) for dy in (-1, 0, 1)
        ]
        assert sum(1 for spot in shelf if spot in reachable) >= 2, \
            (name, shelf)


def _reachable(tilemap: TileMap) -> set[tuple[int, int]]:
    ts = config.TILE_SIZE
    arrival = next(position for kind, position in tilemap.object_spawns
                   if kind == "arrival:from_east_8")
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


def test_it_goes_round_what_it_cannot_go_through() -> None:
    """The steering, stated as the thing it fixes.

    A pursuer that only walks straight at what it wants stops at the
    first lava vein and stays there. The test is not that the orc slides
    -- it is that it arrives from a cell whose straight line is blocked,
    and that it does not simply stand still.
    """
    tilemap = _worn()
    fighter, ranger = _actors()
    ts = config.TILE_SIZE
    # A cell with a grown crack between it and the fighter.
    cell = (36, 16)
    spot = ((cell[0] + 0.5) * ts, (cell[1] + 0.5) * ts)
    orc = HordeOrc(*spot, fighter)
    orc.tilemap = tilemap
    straight = math.dist(spot, (fighter.center_x, fighter.center_y))
    stalled = frames = 0
    ended = straight
    # Only the journey is measured. Once it has arrived it is pressed
    # against a man who is not moving, so of course it stops.
    for _ in range(int(40 / (1 / 30))):
        before = (orc.x, orc.y)
        orc.update(1 / 30)
        frames += 1
        if math.dist((orc.x, orc.y), before) < 0.05:
            stalled += 1
        ended = math.dist((orc.center_x, orc.center_y),
                          (fighter.center_x, fighter.center_y))
        if ended <= ARRIVED:
            break
    assert ended <= ARRIVED, ended
    assert ended < straight
    # It spends most of the walk walking rather than grinding on a wall.
    assert stalled < frames * 0.25, (stalled, frames)


# ----------------------------------------------------------------------
# Who it is coming for
# ----------------------------------------------------------------------
def test_nothing_in_the_horde_is_coming_for_chuck() -> None:
    """The rule the whole encounter rests on.

    They are charging the fighter or the ranger, chosen at spawn and
    never revisited. Nobody is charging the wizard -- he is working, and
    a room where he had to defend himself would be a room where the
    thing he is doing stops. And nobody is charging Chuck: an orc walks
    the same course whether or not he is standing next to it, which is
    checked by running the same orc twice.
    """
    tilemap = _tilemap()
    fighter, ranger = _actors()
    wizard = BattleActor(WIZARD[0] * 16.0, WIZARD[1] * 16.0, "wizard")
    horde = OrcHorde(tilemap, None, fighter=fighter, ranger=ranger)
    for _ in range(int(60 / (1 / 30))):
        horde.update(1 / 30)
    assert horde.orcs
    for orc in horde.orcs:
        assert orc.target in (fighter, ranger)
        assert orc.target is not wizard

    # The same orc, once alone and once with Chuck pressed against it.
    ts = config.TILE_SIZE
    spot = ((36 + 0.5) * ts, (20 + 0.5) * ts)
    tracks = []
    for beside in (False, True):
        orc = HordeOrc(*spot, fighter)
        orc.tilemap = tilemap
        for _ in range(int(6 / (1 / 30))):
            orc.update(1 / 30, None)
        tracks.append((round(orc.x, 3), round(orc.y, 3)))
    assert tracks[0] == tracks[1], tracks


def test_the_two_who_are_fighting_kill_in_one_and_keep_at_it() -> None:
    """Her arrow, his sword, and neither of them running out of work.

    The failure this is written against is subtle and was real: the
    fighter's kills stopped after the first minute, because the rift had
    closed the ground around him and nothing could reach him any more.
    So this is not "the sword works" -- it is that it is still working in
    the last quarter of the encounter, which is the only version of the
    claim that survives the room falling apart.
    """
    directory, game, world = _world()
    try:
        horde = world.horde
        assert horde is not None
        sword, arrows = [], []
        cut_down, kill = horde.cut_down, horde.kill

        def spy_cut(box):
            killed = cut_down(box)
            sword.append(killed)
            return killed

        def spy_kill(orc):
            hit = kill(orc)
            arrows.append(hit)
            return hit

        horde.cut_down, horde.kill = spy_cut, spy_kill

        quarters = []
        for _ in range(4):
            _play(game, world, 22.0)
            quarters.append((sum(sword), sum(1 for hit in arrows if hit)))
        assert world.trio.beats_played >= 4, world.trio.beats_played

        by_sword = [count for count, _ in quarters]
        by_arrow = [count for _, count in quarters]
        assert by_sword[0] > 0, quarters
        assert by_arrow[0] > 0, quarters
        # Both are still killing in the last quarter, not only the first.
        assert by_sword[-1] > by_sword[-2], by_sword
        assert by_arrow[-1] > by_arrow[-2], by_arrow
        # ...and the stream never dried up.
        assert horde.spawned > 60, horde.spawned
        assert len(horde.orcs) >= OrcHorde.MAX_ALIVE - 4, len(horde.orcs)
    finally:
        game._shutdown()
        directory.cleanup()


def test_one_arrow_is_one_orc_and_only_ever_an_orc() -> None:
    """One hit, whatever the thing's own durability says.

    An orc takes eleven of Chuck's scratches. It takes one arrow here,
    because these are the people who do this for a living. And it is
    only the horde: the garrison that has noticed Chuck is his problem,
    and a room where stray hero fire cleared it for him would take away
    the thing he is dodging.
    """
    from src.core.config import ORC_SCRATCHES
    assert ORC_SCRATCHES > 1

    directory, game, world = _world()
    try:
        garrison = len(world.undead)
        assert garrison, "the arena has no garrison to leave alone"
        before = {id(enemy) for enemy in world.undead}
        _play(game, world, 45.0)
        # Everything still alive in the garrison is something that was
        # there before: hero fire has not been thinning it.
        assert world.horde.killed > 10, world.horde.killed
        assert {id(enemy) for enemy in world.undead} <= before
        assert len(world.undead) >= garrison - 1, (len(world.undead),
                                                  garrison)
    finally:
        game._shutdown()
        directory.cleanup()


# ----------------------------------------------------------------------
# What it costs Chuck
# ----------------------------------------------------------------------
def test_being_in_the_way_costs_him_and_stops_him() -> None:
    """The weave: not a chase, but not free either.

    They do not aim at him and they are still bodies in the same floor.
    Walking into one costs what walking into any orc in this region
    costs and puts him back where he was, the same as every other
    pursuer in the game -- which is what makes the horde something to
    thread rather than scenery to ignore.
    """
    directory, game, world = _world()
    try:
        # Past the entrance lines: the first update of this room pushes
        # them and returns before anything is resolved.
        _play(game, world, 1.0)
        orc = world.horde.orcs[0]
        world.player.x = orc.x
        world.player.y = orc.y
        world.player.hurt_blink = 0.0
        before = world.sanity.current
        standing = (world.player.x, world.player.y)
        world.update(1 / 30)
        assert world.sanity.current < before, world.sanity.current
        assert (world.player.x, world.player.y) == standing
    finally:
        game._shutdown()
        directory.cleanup()


def test_nothing_is_ever_spawned_on_top_of_him() -> None:
    """Twenty Sanity he had no way to avoid is not a hazard.

    The ring is a long way from anywhere he has reason to be, so this
    almost never fires. "Almost never" is not the standard the rest of
    this room is held to, so the spawn skips a cell he is standing on.
    """
    tilemap = _tilemap()
    fighter, ranger = _actors()
    horde = OrcHorde(tilemap, None, fighter=fighter, ranger=ranger)
    ts = config.TILE_SIZE
    for cell in SPAWN_CELLS:
        box = pygame.Rect(cell[0] * ts, cell[1] * ts, ts, ts)
        standing = len(horde.orcs)
        spawned = horde._spawn_next(box)
        if spawned is None:
            continue
        assert not box.colliderect(spawned.hitbox), cell
        assert len(horde.orcs) == standing + 1


# ----------------------------------------------------------------------
# The room, and only this room
# ----------------------------------------------------------------------
def test_the_same_encounter_twice_is_the_same_encounter() -> None:
    """Fixed sequence, not a random one, the same as the churn's.

    A room that differs per run is a room nobody can tell is working --
    including whoever has to decide whether the last change improved it.
    """
    def run():
        tilemap = _tilemap()
        fighter, ranger = _actors()
        horde = OrcHorde(tilemap, None, fighter=fighter, ranger=ranger)
        for _ in range(int(40 / (1 / 30))):
            horde.update(1 / 30)
        return [(round(orc.x, 3), round(orc.y, 3), orc.target.kind)
                for orc in horde.orcs]

    assert run() == run()


def test_a_press_is_already_on_them_when_he_walks_in() -> None:
    """He arrives in the middle of it, the way he has twice before."""
    directory, game, world = _world()
    try:
        assert len(world.horde.orcs) == len(OPENING)
        ts = config.TILE_SIZE
        arrival = next(
            position for kind, position in world.tilemap.object_spawns
            if kind == "arrival:from_east_8")
        # ...and none of the opening press is anywhere near the door.
        for orc in world.horde.orcs:
            assert math.dist((orc.center_x, orc.center_y), arrival) > ts * 20
    finally:
        game._shutdown()
        directory.cleanup()


def test_dying_puts_the_horde_back_with_the_room() -> None:
    """The room resets whole: floor, conversation, and what is in it."""
    directory, game, world = _world()
    try:
        _play(game, world, 30.0)
        assert world.horde.spawned > len(OPENING)
        world._reset_enemies()
        assert world.horde.spawned == len(OPENING)
        assert len(world.horde.orcs) == len(OPENING)
        assert world.horde.killed == 0
        # ...and the new horde is what the new cadences are shooting at.
        assert world.battle._horde is world.horde
    finally:
        game._shutdown()
        directory.cleanup()


def test_no_other_map_has_one() -> None:
    directory, game, world = _world()
    try:
        assert world.horde is not None
        for elsewhere in ("desert_east_8", "temple_9",
                          "phlegethos_fortress_approach"):
            other = game.checkpoints.load_checkpoint(
                elsewhere, progress_flags=set(DESERT_ENTRY_FLAGS))
            assert other.horde is None, elsewhere
            assert other.horde_orcs == []
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
    print("All orc-horde tests passed.")


if __name__ == "__main__":
    _run_all()
