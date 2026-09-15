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
    BALL_DAMAGE, BALL_LIFE, BALL_SPEED, BALL_SPEED_STEP, BREATH_FRAMES, BURN,
    EMBERS, FAN_FIRST, FLY_FRAMES, GLOW, LAND_MARGIN, LAND_STANDOFF,
    LANDED_FRAMES, LANDED_TIME, LANE, LIFE, PASS_GAP, ROW_MARGIN,
    SANITY_DAMAGE, SPEED, SPIT_FRAMES, TOTAL_FRAMES, VOLLEY_INTERVAL,
    FlameBall, RedDragonFlyby,
)
from src.scenes.dialogue_scene import DialogueScene
from src.systems.checkpoints import DESERT_ENTRY_FLAGS
from src.systems.trio_encounter import (
    BEATS as _TRIO_BEATS, CHURN_FROM as _TRIO_COLLIDES)
from src.world.tilemap import TileMap


MAP_NAME = "desert_trio"
STEP = 1 / 30
# A ball's box is square and a fraction of the lane's height, which
# is how a spy on `cut_down` tells the rolling fire apart from the
# stripe and from the fighter's sword.
BALL_RADIUS_SIDE = 2 * 7.0

import sys as _sys
_sys.path.insert(0, "tools")
from generate_desert_trio import (  # noqa: E402
    FIGHTER as _F, RANGER as _R, WIZARD as _W,
)

HEROES = (_F, _W, _R)
# Somewhere the Astral coming in from the west never reaches. Left on
# the arrival tile a player is taken by that front about half a minute
# in, which kills him and restarts the encounter -- correct, and the
# whole point of the front, and useless for a test about anything else.
CLEAR_OF_IT = (46 * config.TILE_SIZE, 26 * config.TILE_SIZE)


def _tilemap() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _worn():
    """The arena after the rift and the western front have had it.

    By the time the dragon is landing, the map it is landing on is not
    the one on disk: the rift has taken columns off the east and the
    Astral has come in from the west. A landing spot chosen against the
    file would put the animal on a hole.
    """
    from src.systems.trio_encounter import (
        CHURN_FROM, ENCROACH_LIMIT, FIRST_ADVANCE, TrioEncounter,
    )

    tilemap = _tilemap()
    trio = TrioEncounter(tilemap, set(HEROES))
    box = pygame.Rect(0, 0, 1, 1)
    for _ in range(CHURN_FROM - FIRST_ADVANCE):
        trio.advance((4, tilemap.height_tiles // 2))
        for _ in range(int(20 / STEP)):
            trio._break_through(1 / 30, box)
    for _ in range(ENCROACH_LIMIT + 1):
        trio.encroach((4, tilemap.height_tiles // 2))
        for _ in range(int(20 / STEP)):
            trio._break_through(1 / 30, box)
    return tilemap


def _world():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        MAP_NAME, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


# When the wizard finds it, and the dragon with it: the talk before that.
_DRAGON_DUE = sum(delay for delay, _ in _TRIO_BEATS[:_TRIO_COLLIDES])


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
    """One whole pass: in, down, up, and off the far side.

    Waits on `present` rather than on `flying`, because a pass now stops
    on the floor part way across and `flying` goes false while it is
    down there.
    """
    dragon.begin(row)
    while dragon.present:
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
        assert not dragon.present
        dragon.update(PASS_GAP / 2)
        assert not dragon.present
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
    rows, burned = set(), set()
    for frame in range(200):
        dragon.update(STEP, player_tile=(10, frame % 40))
        rows.add(dragon.row)
        # Collected as it goes rather than read off the end: the pass
        # now stops on the floor part way across, and by the time it
        # climbs out again the first stretch of stripe has burned out.
        burned |= {round(fire[1]) for fire in dragon.fires}
    assert rows == {31}, rows
    assert burned == {31 * 16 + 8}, burned


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
        while dragon.present:
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
        # `cut_down_any` is the dragon's alone -- the fighter's sword
        # goes through `cut_down` one box at a time -- so counting at
        # this call needs no guesswork about which box belonged to whom.
        cut_down_any = world.horde.cut_down_any
        burnt = []

        def spy(boxes):
            killed = cut_down_any(boxes)
            burnt.append(killed)
            return killed

        world.horde.cut_down_any = spy
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
        _play(game, world, _DRAGON_DUE + 4.0)
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
        assert len(dragon._frames) == TOTAL_FRAMES
        dragon.begin(20)
        crossing, grounded = set(), set()
        while dragon.present:
            if dragon.phase == "flying":
                crossing.add(dragon.frame_index)
            elif dragon.phase == "landed":
                grounded.add(dragon.frame_index)
            dragon.update(STEP)
        # Crossing: every frame of the breathing wingbeat and nothing
        # else.
        breathing = set(range(FLY_FRAMES, FLY_FRAMES + BREATH_FRAMES))
        assert crossing == breathing, sorted(crossing)
        # Down: the folded poses, and it visibly spits rather than
        # sitting still while fire appears in front of it.
        base = FLY_FRAMES + BREATH_FRAMES
        assert grounded, "it never came down"
        assert grounded <= set(range(base, TOTAL_FRAMES)), sorted(grounded)
        assert any(index >= base + LANDED_FRAMES for index in grounded)
        assert any(index < base + LANDED_FRAMES for index in grounded)
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

        _play(game, world, _DRAGON_DUE + 8.0)
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
    while dragon.present:
        dragon.update(STEP)
        elapsed += STEP
    span = tilemap.width_tiles * config.TILE_SIZE
    # The crossing itself, plus the stop in the middle of it. Derived
    # rather than asserted: the arena's own width over the speed is the
    # only number here that means anything, and the landing is the one
    # thing added to it.
    assert abs(elapsed - (span / SPEED + LANDED_TIME)) < 4.0, elapsed
    # Three tiles of lane, and the arena is many times that: there is
    # always somewhere it is not.
    assert LANE * 4 < tilemap.height_tiles * config.TILE_SIZE


# ----------------------------------------------------------------------
# Coming down
# ----------------------------------------------------------------------
def test_it_comes_down_on_ground_it_can_stand_on() -> None:
    """Never the Sea, never the rim, and never on top of him.

    All three of those are failures I would rather not ship. A landing
    on the Astral is a dragon standing on a hole with its fire dying the
    instant it leaves the mouth; a landing at the map's edge is an
    animal that looks placed rather than arrived; and a landing on his
    own tile is a fan of rolling fire at point-blank range, which is not
    a dodge, it is an announcement.

    Checked on the worn arena as well as the fresh one, because by the
    time it starts landing the western half of that floor is gone.
    """
    for label, tilemap in (("fresh", _tilemap()), ("worn", _worn())):
        dragon = RedDragonFlyby(tilemap)
        for col in (10, 30, 40, 50, 60):
            dragon.begin(24, col)
            while dragon.phase != "landed":
                dragon.update(STEP)
                assert dragon.present, (label, col)
            here = int(dragon.x) // config.TILE_SIZE
            assert not tilemap.is_solid(here, dragon.row), (label, col, here)
            assert tilemap.terrain_at(here, dragon.row) != "V", (label, here)
            assert LAND_MARGIN <= here <= tilemap.width_tiles - 1 - LAND_MARGIN
            while dragon.present:
                dragon.update(STEP)


def test_it_stands_off_rather_than_landing_on_him() -> None:
    """Short of him by enough that the fan has somewhere to travel."""
    tilemap = _tilemap()
    dragon = RedDragonFlyby(tilemap)
    for col in (30, 40, 48):
        dragon.begin(24, col)
        while dragon.phase != "landed":
            dragon.update(STEP)
        here = int(dragon.x) // config.TILE_SIZE
        assert abs(here - col) >= LAND_STANDOFF - 2, (col, here)
        while dragon.present:
            dragon.update(STEP)


def test_the_rolling_fire_gets_worse_every_time() -> None:
    """Wider, faster, and closer together. The curve, as three numbers.

    There is no reason for the third landing to be the first one again,
    and a hazard that repeats itself unchanged is one a player stops
    reading after the second look. What matters most is the speed: it
    starts below Chuck's own and ends above it, which is the moment
    outrunning the fire stops working and stepping through the gaps is
    the only thing left.
    """
    dragon = RedDragonFlyby(_tilemap())
    fans, speeds, intervals = [], [], []
    for _ in range(4):
        dragon.landings += 1
        fans.append(dragon.fan)
        speeds.append(dragon.ball_speed)
        intervals.append(dragon.volley_interval)
    assert fans == sorted(fans) and fans[0] == FAN_FIRST and fans[-1] > fans[0]
    assert speeds == sorted(speeds), speeds
    assert intervals == sorted(intervals, reverse=True), intervals
    assert speeds[0] == BALL_SPEED
    # Below him, then past him.
    assert speeds[0] < config.PLAYER_SPEED < speeds[-1], speeds
    assert BALL_SPEED_STEP > 0 and VOLLEY_INTERVAL > 0


def test_a_volley_is_a_fan_aimed_at_him_with_gaps_in_it() -> None:
    """Aimed, spread, and steppable.

    A fan tight enough to have no gaps is a wall, and a wall coming at
    him from one point with no way round it is not a dodge. So the
    spacing is measured where it actually matters: at the range the
    dragon stands off, adjacent balls are further apart than Chuck is
    wide.
    """
    dragon = RedDragonFlyby(_tilemap())
    dragon.begin(24, 40)
    while dragon.phase != "landed":
        dragon.update(STEP)
    dragon.balls.clear()
    target = (dragon.x - 200.0, dragon.track_y + 40.0)
    assert dragon.spit(target) == dragon.fan
    assert len(dragon.balls) == dragon.fan

    # Every ball is going roughly at him, and the middle one is going
    # straight at him.
    import math as _math
    want = _math.atan2(target[1] - dragon.track_y, target[0] - dragon.x)
    angles = sorted(_math.atan2(ball.vy, ball.vx) for ball in dragon.balls)
    assert min(abs(angle - want) for angle in angles) < 0.25, angles

    # ...and they arrive spread out rather than stacked.
    reach = LAND_STANDOFF * config.TILE_SIZE
    gaps = [abs(angles[i + 1] - angles[i]) * reach
            for i in range(len(angles) - 1)]
    assert min(gaps) > 16.0, gaps


def test_a_ball_rolls_straight_and_stops_at_something() -> None:
    """It does not steer, and it does not hang over a hole.

    Not steering is the point of it: a thing that chased him would be a
    second dragon, and what this room wants is an obstacle whose whole
    future he can read the moment it leaves the mouth. Stopping at the
    Sea is the other half -- the holes in that floor are the one thing a
    player is already reading, and a ball of fire sitting in the middle
    of one is a bug.
    """
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    ball = FlameBall(30 * ts, 24 * ts, 1.0, 0.0, BALL_SPEED)
    heading = (ball.vx, ball.vy)
    for _ in range(20):
        ball.update(STEP, tilemap)
    assert (ball.vx, ball.vy) == heading, "it turned"
    assert ball.y == 24 * ts

    # Into the rift: it goes out rather than over.
    edge = next(col for col in range(40, tilemap.width_tiles)
                if tilemap.terrain_at(col, 24) == "V")
    runner = FlameBall((edge - 3) * ts, 24 * ts + 8, 1.0, 0.0, BALL_SPEED)
    for _ in range(int(4.0 / STEP)):
        runner.update(STEP, tilemap)
        if not runner.alive:
            break
    assert not runner.alive, "it rolled out over the Sea"

    # ...and nothing rolls for ever.
    forever = FlameBall(30 * ts, 24 * ts, 0.0, -1.0, 1.0)
    for _ in range(int((BALL_LIFE + 1.0) / STEP)):
        forever.update(STEP, tilemap)
    assert not forever.alive


def test_a_ball_costs_less_than_the_stripe() -> None:
    """One is a wall he chose to stand in; the other is traffic.

    Both are avoidable and only one of them is avoidable at leisure, so
    the one that arrives while he is dealing with three others of its
    kind is the cheaper mistake.
    """
    assert BALL_DAMAGE < SANITY_DAMAGE
    dragon = RedDragonFlyby(_tilemap())
    dragon.begin(24, 40)
    while dragon.phase != "landed":
        dragon.update(STEP)
    # Both cleared: a ball leaves the mouth inside the stripe the
    # dragon laid on its way in, and the stripe is the more expensive
    # of the two, so a ball measured there measures the wrong thing.
    dragon.balls.clear()
    dragon.fires.clear()
    dragon.spit((dragon.x - 100.0, dragon.track_y))
    ball = dragon.balls[0]
    assert dragon.damage_for(ball.hitbox) == BALL_DAMAGE
    assert dragon.burns(ball.hitbox)
    assert dragon.damage_for(pygame.Rect(0, 0, 2, 2)) == 0


def test_the_encounter_gives_it_room_to_get_worse() -> None:
    """The escalation only exists if the room lasts long enough for it.

    Three landings is the minimum that reads as a curve rather than as a
    repeat, and the last two exchanges were doubled precisely to buy
    them. This is the test that fails if somebody shortens them again.
    """
    directory, game, world = _world()
    try:
        _play(game, world, 200.0)
        dragon = world.red_dragon
        assert dragon.landings >= 3, dragon.landings
        assert dragon.passes >= 3, dragon.passes
        # ...and it did all of it after the wizard found what he wanted.
        assert world.trio.collided
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_last_two_exchanges_are_the_long_ones() -> None:
    """The gaps are the dragon's act, and they are twice everyone else's."""
    from src.systems.trio_encounter import BEATS, CHURN_FROM

    talk = [delay for delay, _ in BEATS[:CHURN_FROM]]
    fight = [delay for delay, _ in BEATS[CHURN_FROM:]]
    # Either of the last two is longer than all four of the others, and
    # between them they are more than half the encounter -- which is the
    # claim, rather than any particular pair of numbers.
    assert min(fight) > max(talk), (talk, fight)
    # Half as long again as the talk, since the talk grew to fit the
    # orcs' siege; it was twice as long before that.
    assert min(fight) > sum(talk) / len(talk) * 1.5, (talk, fight)
    assert sum(fight) > sum(talk), (talk, fight)


def test_a_landed_dragon_sorts_with_the_room() -> None:
    """Eight tiles of red on top of Chuck is the one thing this room
    is not allowed to do.

    In the air it draws over everything, because it is not standing on
    the floor at all. Down, it goes in the y-sorted pass with everything
    else that has feet -- so he passes in front of it and behind it and
    is visible either way.
    """
    directory, game, world = _world()
    try:
        assert world.red_dragon not in world._sorted_drawables()
        landed = False
        for _ in range(int(200 / STEP)):
            if isinstance(game.scenes.current, DialogueScene):
                game.scenes.pop()
                continue
            if not isinstance(game.scenes.current, type(world)):
                break
            world.sanity.current = world.sanity.maximum
            world.player.x, world.player.y = CLEAR_OF_IT
            world.update(STEP)
            dragon = world.red_dragon
            if dragon.on_the_ground:
                landed = True
                assert dragon in world._sorted_drawables()
                assert dragon.altitude == 0.0
                assert dragon.sort_y > dragon.track_y
            elif dragon.present:
                assert dragon not in world._sorted_drawables()
        assert landed, "it never came down"
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_rolling_fire_burns_orcs_too() -> None:
    """It does not care whose side anybody is on, the same as the stripe.

    In two halves, because the interesting one cannot be observed from
    outside the frame it happens in. A ball kills whatever it reaches on
    the very update it reaches it, so an orc is alive at the top of that
    frame and gone from the list at the bottom -- sampling between
    frames catches nothing and looks exactly like the fire not working.
    That was true of the burning stripe as well and cost an afternoon.

    So: the room is played, and the dragon's own kill path is counted at
    the call; and then a ball is put on an orc directly and the claim
    that rolling fire is what killed it is made where it can be seen.
    """
    directory, game, world = _world()
    try:
        # `cut_down_any` is the dragon's alone -- the fighter's sword
        # goes through `cut_down`, one box at a time -- so counting here
        # needs no guesswork about whose box was whose.
        cut_down_any = world.horde.cut_down_any
        burnt = []

        def spy(boxes):
            killed = cut_down_any(boxes)
            burnt.append(killed)
            return killed

        world.horde.cut_down_any = spy
        _play(game, world, 200.0, hold=(40 * config.TILE_SIZE,
                                        IN_THE_STREAM * config.TILE_SIZE))
        assert world.red_dragon.landings >= 2, world.red_dragon.landings
        assert sum(burnt) > 0, "the dragon never burned anything of theirs"
    finally:
        game._shutdown()
        directory.cleanup()

    # ...and the rolling fire specifically, put on an orc by hand.
    directory, game, world = _world()
    try:
        dragon = world.red_dragon
        dragon.begin(24, 40)
        while dragon.phase != "landed":
            dragon.update(STEP)
        orc = world.horde.orcs[0]
        orc.x, orc.y = dragon.x - 60, dragon.track_y
        dragon.balls.clear()
        dragon.spit((orc.x, orc.y))
        for _ in range(int(2.0 / STEP)):
            for ball in dragon.balls:
                ball.update(STEP, world.tilemap)
            dragon.balls = [ball for ball in dragon.balls if ball.alive]
            if world.horde.cut_down_any(dragon.ball_rects):
                break
        assert not orc.alive, "a ball rolled through an orc and left it"
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
    print("All red-dragon tests passed.")


if __name__ == "__main__":
    _run_all()
