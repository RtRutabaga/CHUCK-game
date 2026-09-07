"""The red dragon crossing the final encounter, and its burning trail.

This is the fourth thing pressing Chuck in that room and it had to be a
different *kind* of thing from the other three, or it would only have
been more of them. The arrows come from a fixed point, the horde walks
fixed courses, the churn repaints the floor without ever making it
dangerous -- all three are pressure he reads around himself. A stripe of
fire crossing the arena at whatever row he is standing on is the one
kind he has to read about himself, which is why what is tested hardest
here is the *aim*: taken from him when the pass begins, and then fixed
for the whole crossing.

The other half is the telegraph, and it is the reason this hazard is
survivable at all. The lane is three tiles wide, which is more than a
one-foot rat can step out of on reflex, so the ground glows for a full
second before it catches and the glow is not lethal. The tests pin that
window as a window rather than as a number: what has to be true is that
every patch spends time warm and harmless before it spends time
burning, and that a player who moves when the dragon passes over is not
hit while a player who does not is.

And the blue dragon's contract, which this one inherits whole: no
health, no death, nothing to fight, and -- the one that matters for a
room that is already tearing itself apart -- it writes nothing to the
map. The floor it burns is the floor it found.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities import blue_dragon
from src.entities.red_dragon import (
    BURN, EMBERS, FLY_FRAMES, GLOW, LANE, LIFE, PASS_GAP, ROW_MARGIN,
    SANITY_DAMAGE, SPEED, RedDragonFlyby,
)
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import DESERT_ENTRY_FLAGS
from src.world.tilemap import TileMap


MAP_NAME = "desert_trio"
STEP = 1 / 30
# Somewhere the Astral coming in from the west never reaches. Left on
# the arrival tile a player is taken by that front about half a minute
# in, which kills him and restarts the encounter -- correct, and the
# whole point of the front, and useless for a test about anything else.
CLEAR_OF_IT = (46 * config.TILE_SIZE, 26 * config.TILE_SIZE)


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


def _play(game, world, seconds: float, *, hold="clear") -> None:
    """Run the room, popping conversations. `hold` pins Chuck somewhere.

    Parked clear of the western front by default: left on the
    arrival tile the Astral takes him about half a minute in and
    the encounter restarts, which is right and is not what a test
    about the dragon is asking.
    """
    if hold == "clear":
        hold = CLEAR_OF_IT
    for _ in range(int(seconds / STEP)):
        if isinstance(game.scenes.current, DialogueScene):
            game.scenes.pop()
            continue
        if not isinstance(game.scenes.current, type(world)):
            return
        world.sanity.current = world.sanity.maximum
        if hold is not None:
            world.player.x, world.player.y = hold
        world.update(STEP)


def _cross(dragon: RedDragonFlyby, row: int) -> None:
    """One whole pass, from off the edge to off the other one."""
    dragon.begin(row)
    while dragon.flying:
        dragon.update(STEP)


def _snapshot(tilemap: TileMap):
    return [
        [tilemap.terrain_at(x, y) for x in range(tilemap.width_tiles)]
        for y in range(tilemap.height_tiles)
    ]


# ----------------------------------------------------------------------
# When it comes
# ----------------------------------------------------------------------
def test_it_is_saved_for_the_climax() -> None:
    """Nothing until the worlds start arriving, and then it is there.

    Running the whole encounter it would be a fourth hazard competing
    with the conversation for the first minute. Arriving with the
    collision it is what the climax is made of -- the heroes closing the
    rift, everywhere landing on top of everywhere, and a dragon coming
    through the middle of it.
    """
    directory, game, world = _world()
    try:
        assert world.red_dragon is not None
        _play(game, world, 40.0)
        assert not world.trio.collided
        assert world.red_dragon.passes == 0
        assert not world.red_dragon.fires

        _play(game, world, 60.0)
        assert world.trio.collided
        assert world.red_dragon.passes >= 2, world.red_dragon.passes
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_passes_alternate_sides_and_leave_a_gap() -> None:
    """A hazard that always comes from the west has a safe west side."""
    dragon = RedDragonFlyby(_tilemap())
    directions = []
    for _ in range(4):
        _cross(dragon, 20)
        directions.append(dragon.direction)
        # ...and it does not immediately come back.
        assert not dragon.flying
        dragon.update(PASS_GAP / 2)
        assert not dragon.flying
    assert directions == [1, -1, 1, -1], directions


# ----------------------------------------------------------------------
# Where it goes
# ----------------------------------------------------------------------
def test_it_aims_at_him_once_and_then_commits() -> None:
    """The whole difference between a dodge and a chase.

    The row comes from where Chuck is standing when the pass starts, so
    a player who stays put is hit. It is then fixed for the crossing, so
    a player who moves is not -- and the approach is a promise about
    where the fire is going to be rather than a thing that keeps
    changing its mind about him.
    """
    dragon = RedDragonFlyby(_tilemap())
    dragon.update(dragon._wait + STEP, player_tile=(10, 31))
    assert dragon.flying
    assert dragon.row == 31

    # Re-aimed at a different row every frame from here on; it should
    # not move an inch.
    rows = set()
    for frame in range(200):
        dragon.update(STEP, player_tile=(10, frame % 40))
        rows.add(dragon.row)
    assert rows == {31}, rows
    assert {round(fire[1]) for fire in dragon.fires} == {31 * 16 + 8}


def test_the_lane_always_fits_inside_the_arena() -> None:
    """Aimed at the very edge it would burn half a stripe against a wall."""
    tilemap = _tilemap()
    dragon = RedDragonFlyby(tilemap)
    for row in (-40, 0, 1, 25, 51, 500):
        dragon.begin(row)
        last = tilemap.height_tiles - 1 - ROW_MARGIN
        assert ROW_MARGIN <= dragon.row <= last, row
        top = dragon.track_y - LANE / 2
        bottom = dragon.track_y + LANE / 2
        assert top > 0, row
        assert bottom < tilemap.height_tiles * config.TILE_SIZE, row


def test_nothing_catches_over_the_rift_or_the_rim() -> None:
    """Fire hanging in the Astral Sea would hide the edge of the Sea.

    Which is the one edge in this room that has always killed him. A
    stripe painted straight over it says nothing and covers the thing it
    is drawn on top of, so the trail simply has a hole in it wherever
    there is no floor -- and that hole is legible, because it is exactly
    the shape of the hole in the ground.
    """
    tilemap = _tilemap()
    dragon = RedDragonFlyby(tilemap)
    landed = 0
    for row in range(ROW_MARGIN, tilemap.height_tiles - ROW_MARGIN, 5):
        dragon.begin(row)
        while dragon.flying:
            dragon.update(STEP)
            for fire in dragon.fires:
                col = int(fire[0]) // config.TILE_SIZE
                line = int(fire[1]) // config.TILE_SIZE
                assert 0 <= col < tilemap.width_tiles, fire
                assert not tilemap.is_solid(col, line), (col, line)
                assert tilemap.terrain_at(col, line) != "V", (col, line)
                landed += 1
    assert landed > 0


def test_it_writes_nothing_to_the_map() -> None:
    """The floor it burns is the floor it found.

    The rift takes ground and the churn repaints it; between them this
    arena is already changing under the player faster than anything else
    in the game. A hazard that also edited the map would make it
    impossible to say what any given tile is, and the collision's whole
    safety argument rests on being able to say exactly that.
    """
    tilemap = _tilemap()
    before = _snapshot(tilemap)
    dragon = RedDragonFlyby(tilemap)
    for row in (10, 26, 40):
        _cross(dragon, row)
    assert _snapshot(tilemap) == before


# ----------------------------------------------------------------------
# What it costs
# ----------------------------------------------------------------------
def test_every_stretch_glows_before_it_burns_and_dies_after() -> None:
    """The telegraph, as a window rather than as a number.

    Three tiles is wider than a one-foot rat steps out of on reflex, so
    the ground has to announce itself. What must be true is the order:
    warm and harmless, then lethal, then harmless again -- and the
    harmless parts have to be long enough to be seen and read.
    """
    assert GLOW > 0 and BURN > 0 and EMBERS > 0
    assert LIFE == GLOW + BURN + EMBERS

    dragon = RedDragonFlyby(_tilemap())
    dragon.begin(20)
    # It comes in from off the map, and nothing catches out there --
    # so wait for the first patch that actually lands on floor.
    while not dragon.fires:
        dragon.update(STEP)
    patch = dragon.fires[0]
    lethal_for = 0.0
    glowed_for = 0.0
    while patch in dragon.fires:
        burning = any(rect.collidepoint(round(patch[0]), round(patch[1]))
                      for rect in dragon.lethal_rects)
        if burning:
            lethal_for += STEP
        elif lethal_for == 0.0:
            glowed_for += STEP
        else:
            assert not burning, "it caught again after going out"
        dragon.update(STEP)
    assert abs(glowed_for - GLOW) < 0.1, glowed_for
    assert abs(lethal_for - BURN) < 0.1, lethal_for


def test_standing_in_it_hurts_and_stepping_out_of_it_does_not() -> None:
    """The dodge, measured as the difference between the two.

    Not "the fire does damage" -- of course it does. What has to be true
    is that moving is the answer, because a hazard three tiles wide
    sweeping the whole arena is only fair if getting out of the way
    works.
    """
    def burned(dodge: bool) -> int:
        directory, game, world = _world()
        try:
            hits = 0
            spot = [40 * config.TILE_SIZE,
                    IN_THE_STREAM * config.TILE_SIZE]
            for _ in range(int(140 / STEP)):
                if isinstance(game.scenes.current, DialogueScene):
                    game.scenes.pop()
                    continue
                if not isinstance(game.scenes.current, type(world)):
                    break
                world.sanity.current = world.sanity.maximum
                world.player.hurt_blink = 0.0
                dragon = world.red_dragon
                if dodge and dragon.flying:
                    lane = dragon.track_y
                    if abs(spot[1] - lane) < LANE * 1.4:
                        spot[1] = lane + LANE * 1.6
                world.player.x, world.player.y = spot
                before = world.sanity.current
                world.update(STEP)
                if world.sanity.current < before:
                    hits += 1
            return hits
        finally:
            game._shutdown()
            directory.cleanup()

    standing = burned(False)
    moving = burned(True)
    assert standing >= 3, standing
    assert moving < standing, (moving, standing)
    # ...and standing in it is not survivable: it is the most expensive
    # touch in the phase, and three passes of it is more Sanity than
    # anybody has.
    assert SANITY_DAMAGE * standing > config.SANITY_MAX


# Where the horde actually is. The two streams converge on the fighter
# and the ranger and leave a seam between them -- the middle row of the
# arena is a road with nobody on it -- so a test that parks Chuck in the
# middle aims the dragon down the one lane the horde does not use, and
# concludes the fire cannot burn orcs. It can. This is one of the rows
# the southern stream walks.
IN_THE_STREAM = 31


def test_it_does_not_care_whose_side_anybody_is_on() -> None:
    """Orcs burn in it too, which is most of what sells it as weather.

    A fire that stepped around the horde would be a fire that had been
    told who the player is.

    Counted at the call rather than by looking at the room between
    frames, and that is not a shortcut. A patch becomes lethal and kills
    whatever is standing on it inside the same update, so an orc is
    never observed *in* the fire from outside -- it is alive at the top
    of the frame and gone at the bottom. Sampling for one caught nothing
    and looked exactly like the fire not working.
    """
    directory, game, world = _world()
    try:
        spot = (40 * config.TILE_SIZE, IN_THE_STREAM * config.TILE_SIZE)
        cut_down = world.horde.cut_down
        burnt = []

        def spy(box):
            killed = cut_down(box)
            # The dragon's box is the width of the lane; the fighter's
            # arc is less than half as tall. Nothing else swings.
            if box.height >= LANE:
                burnt.append(killed)
            return killed

        world.horde.cut_down = spy
        _play(game, world, 140.0, hold=spot)
        assert world.trio.collided
        assert world.red_dragon.passes >= 2, world.red_dragon.passes
        assert sum(burnt) > 0, "nothing in the horde ever caught fire"
    finally:
        game._shutdown()
        directory.cleanup()


# ----------------------------------------------------------------------
# The blue dragon's contract, in motion
# ----------------------------------------------------------------------
def test_it_has_no_health_and_no_ending() -> None:
    """The same absences the blue one is pinned on.

    The document is firm that a dragon in this game is not a boss. This
    one is even further from being one: there is nothing to hit, nothing
    that stops it coming, and no state in which it is done.
    """
    dragon = RedDragonFlyby(_tilemap())
    for name in ("scratches_remaining", "max_scratches", "on_scratched",
                 "alive", "health"):
        assert not hasattr(dragon, name), name
    assert not hasattr(blue_dragon.BlueDragon, "on_scratched")

    for _ in range(6):
        _cross(dragon, 20)
    assert dragon.passes == 6
    # It is between passes, not finished: there is no such state.
    dragon.update(PASS_GAP + STEP, player_tile=(10, 12))
    assert dragon.flying


def test_the_same_pass_twice_is_the_same_pass() -> None:
    """Fixed, like the churn and the horde: a room nobody can tell is
    working is a room nobody can improve."""
    def run():
        dragon = RedDragonFlyby(_tilemap())
        dragon.begin(18)
        for _ in range(120):
            dragon.update(STEP)
        return [(round(x, 3), round(y, 3), round(age, 3))
                for x, y, age in dragon.fires]

    assert run() == run()


def test_the_animal_is_in_the_air_and_the_fire_is_on_the_floor() -> None:
    """Two draw calls, and neither of them is sorted with the room.

    The trail goes under everything standing on it, so a player can see
    their own feet in the fire. The dragon goes over everything, because
    it is not on the floor at all -- sorted by its feet the way the rest
    of the room is sorted, a flying dragon ends up behind a waist-high
    rock.
    """
    directory, game, world = _world()
    try:
        assert world.red_dragon not in world._sorted_drawables()
        _play(game, world, 66.0)
        dragon = world.red_dragon
        assert dragon.flying or dragon.fires, "nothing to draw yet"
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.camera.focus_on(dragon.x, dragon.track_y)
        world.camera.update(0.0)
        world.draw(surface)
        # The sprite is drawn a good way above its own track, which is
        # what makes the shadow readable as a separate thing.
        assert dragon.track_y - LANE > 0
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_sheet_beats_its_wings_the_whole_time_it_breathes() -> None:
    """Twelve frames, and the breathing half is a wingbeat too.

    Given its own two-frame pose the way the blue dragon's breath is,
    the wings would stop mid-air for as long as it was breathing -- and
    it breathes for the entire crossing.
    """
    directory, game, world = _world()
    try:
        dragon = world.red_dragon
        assert len(dragon._frames) == FLY_FRAMES * 2
        dragon.begin(20)
        seen = set()
        while dragon.flying:
            seen.add(dragon.frame_index)
            dragon.update(STEP)
        assert seen == set(range(FLY_FRAMES, FLY_FRAMES * 2)), sorted(seen)
        # ...and off duty it is on the plain wingbeat.
        assert dragon.frame_index < FLY_FRAMES
    finally:
        game._shutdown()
        directory.cleanup()


def test_only_the_trios_map_has_one_and_dying_sends_it_home() -> None:
    directory, game, world = _world()
    try:
        elsewhere = game.checkpoints.load_checkpoint(
            "desert_east_8", progress_flags=set(DESERT_ENTRY_FLAGS))
        assert elsewhere.red_dragon is None

        _play(game, world, 70.0)
        assert world.red_dragon.passes > 0
        world._reset_enemies()
        assert world.red_dragon.passes == 0
        assert not world.red_dragon.fires
        assert not world.red_dragon.flying
        assert world.red_dragon._frames, "the new one has no sprite"
    finally:
        game._shutdown()
        directory.cleanup()


def test_a_crossing_takes_about_as_long_as_it_should() -> None:
    """Slow enough to see coming, quick enough to be an event.

    Derived rather than asserted: the arena's own width over the speed,
    which is the only number that means anything here.
    """
    tilemap = _tilemap()
    dragon = RedDragonFlyby(tilemap)
    elapsed = 0.0
    dragon.begin(20)
    while dragon.flying:
        dragon.update(STEP)
        elapsed += STEP
    span = tilemap.width_tiles * config.TILE_SIZE
    assert abs(elapsed - span / SPEED) < 3.0, elapsed
    # Three tiles of lane, and the arena is many times that: there is
    # always somewhere it is not.
    assert LANE * 4 < tilemap.height_tiles * config.TILE_SIZE


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
    print("All red-dragon tests passed.")


if __name__ == "__main__":
    _run_all()
