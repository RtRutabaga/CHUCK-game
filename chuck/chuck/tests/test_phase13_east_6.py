"""Phase 13's frozen world: weather that knows where it is, and a
dragon that cannot be beaten.

Two things here are unlike anything else in the phase.

The snow falls only over snow. That is a visual rule but it is worth a
real test rather than a screenshot, because the failure is silent in
both directions: masked too tightly the weather vanishes, masked not at
all it snows on a desert, and either can survive a glance at a frame
that happens to be mostly fragment. So it is checked by rendering the
seam and counting flake pixels on each side of it.

The dragon is the phase document's one permitted new system, and the
document is firmer about what it must not be than what it is: not a
boss, not defeatable, not a fight. Those are absences again, and the
way they get lost is somebody later giving it a health bar because it
looked like it wanted one. Pinned here as things it does not have.

There is one of it, and it is the biggest thing in the game. Both of
those are load-bearing rather than decorative -- a second one makes it
a species, and a small one makes it a hazard marker -- so both are
measured: against the number of spawns on the map, and against the
largest creature sprite the game had before it.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.blue_dragon import (
    BREATH, CYCLE, FRAME_H, FRAME_W, GAPE_AT, IDLE_FRAMES, SPENT, SPRITE,
    WIND_UP, BlueDragon,
)
from src.entities.snow_fall import SNOW_TERRAIN, SnowFall
from src.entities.undead import UndeadEnemy, _STATS
from src.systems.checkpoints import CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.transitions import AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_desert_east_6 import (  # noqa: E402
    DRAGONS, GAP, HEIGHT, RIM, WIDTH,
)


MAP_NAME = "desert_east_6"
BEHIND = "desert_east_5"
EASTERN = ("desert_east_1", "desert_east_2", "desert_east_3",
           "desert_east_4", "desert_east_5", "desert_east_6")


def _tilemap(name: str = MAP_NAME) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _world(checkpoint: str = MAP_NAME):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _flood(tilemap, origin, extra_solid=()) -> set[tuple[int, int]]:
    seen = {origin}
    frontier = [origin]
    while frontier:
        x, y = frontier.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in seen or tilemap.is_solid(*cell):
                continue
            terrain = tilemap.terrain_at(*cell)
            if terrain in collision.FALL_HAZARD_TERRAIN:
                continue
            if terrain in extra_solid:
                continue
            seen.add(cell)
            frontier.append(cell)
    return seen


def test_it_snows_on_the_snow_and_nowhere_else() -> None:
    """Rendered at the seam and counted on both sides of it.

    Masked too tightly the weather disappears; not masked at all it
    snows on a desert. Both survive a glance at a lucky frame, so this
    finds a frame with plenty of each ground in it and counts flakes.
    """
    directory, game, world = _world()
    try:
        assert world.snow is not None, "no weather on a map made of snow"
        assert isinstance(world.snow, SnowFall)
        tilemap = world.tilemap
        ts = config.TILE_SIZE

        # A camera looking at a stretch of the shelf's southern coast,
        # so the shot has a good deal of both grounds in it.
        seam = next(
            (x, y) for y in range(RIM, HEIGHT - RIM)
            for x in range(RIM, WIDTH - RIM)
            if tilemap.terrain_at(x, y) in SNOW_TERRAIN
            and tilemap.terrain_at(x, y + 1) == "."
        )
        camera = (seam[0] * ts - config.NATIVE_WIDTH // 2,
                  seam[1] * ts - config.NATIVE_HEIGHT // 2)

        snowy = sandy = 0
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        # Several moments, because one frame's flakes are one sample.
        for _ in range(6):
            world.snow.update(0.21)
            world.camera.x, world.camera.y = camera
            world.draw(surface)
            for sx in range(0, config.NATIVE_WIDTH, 2):
                for sy in range(0, config.NATIVE_HEIGHT, 2):
                    pixel = surface.get_at((sx, sy))[:3]
                    if pixel != (255, 255, 255):
                        continue    # only the near flakes are pure white
                    col = (sx + camera[0]) // ts
                    row = (sy + camera[1]) // ts
                    if tilemap.terrain_at(col, row) in SNOW_TERRAIN:
                        snowy += 1
                    else:
                        sandy += 1

        assert snowy > 0, "no snow is falling at all"
        assert sandy == 0, f"{sandy} flakes fell on ground that is not snow"
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_weather_turns_itself_on_from_the_map() -> None:
    """No list of snowy maps anywhere: the tiles are the switch."""
    assert _tilemap().has_terrain(SNOW_TERRAIN)
    assert not _tilemap(BEHIND).has_terrain(SNOW_TERRAIN)

    directory, game, world = _world(BEHIND)
    try:
        assert world.snow is None, "snow on a map with no snow on it"
    finally:
        game._shutdown()
        directory.cleanup()

    # Both snow grounds count as snowy for the weather; only one of
    # them can be walked on.
    assert SNOW_TERRAIN == {"❄", "❅"}
    assert not TILE_DEFS["❄"].solid and TILE_DEFS["❅"].solid


def test_the_dragon_cannot_be_fought() -> None:
    """The document's list of what this must not be, held to.

    Not a boss, not defeatable, not a fight. Absences, which is what
    makes them worth writing down -- the way they get lost is somebody
    later giving it a health bar because it looked like it wanted one.
    """
    dragon = BlueDragon(100.0, 100.0, "left")
    assert "blue_dragon" not in _STATS, "not a pursuer"
    assert not isinstance(dragon, UndeadEnemy)
    for absent in ("on_scratched", "scratches_remaining", "max_scratches",
                   "health", "hp"):
        assert not hasattr(dragon, absent), absent
    # It does not chase: update takes time and nothing else.
    assert dragon.x == 100.0 - dragon.WIDTH / 2
    for _ in range(200):
        dragon.update(0.05)
    assert dragon.x == 100.0 - dragon.WIDTH / 2

    # The cycle: mostly safe, and it comes round again.
    assert CYCLE == WIND_UP + BREATH + SPENT
    assert BREATH < CYCLE * 0.25, "lethal for too much of the time"
    assert WIND_UP > BREATH, "the warning must outlast the bolt"
    stages = set()
    fresh = BlueDragon(100.0, 100.0, "left")
    for _ in range(int(CYCLE / 0.05) + 4):
        stages.add(fresh.stage)
        fresh.update(0.05)
    assert stages == {"winding", "breathing", "spent"}

    # The telegraph shows exactly the ground the bolt will take. A
    # warning that does not match its strike is worse than none.
    lanes = set()
    fresh.elapsed = 0.0
    for _ in range(int(CYCLE / 0.05)):
        lanes.add(tuple(round(v, 3) for v in fresh.strike))
        fresh.update(0.05)
    assert len(lanes) == 1, lanes
    # ...and it is lethal only while it is lit.
    fresh.elapsed = WIND_UP * 0.5
    assert not fresh.lethal
    fresh.elapsed = WIND_UP + BREATH * 0.5
    assert fresh.lethal
    fresh.elapsed = WIND_UP + BREATH + SPENT * 0.5
    assert not fresh.lethal

    # Facing decides which way the lane goes, and nothing else does.
    left = BlueDragon(100.0, 100.0, "left").strike
    right = BlueDragon(100.0, 100.0, "right").strike
    assert left[0] < 100.0 < right[0]
    assert left[2] == right[2] and left[3] == right[3]


def test_there_is_one_dragon_and_it_is_the_biggest_thing_in_the_game() -> None:
    """Size and singularity, both measured rather than asserted.

    There were two smaller ones here first and the arithmetic of that
    was fine -- but two of a thing is a species and one of a thing is
    *the* dragon, and the map only has room for one thing that cannot
    be fought. So the count is pinned to the generator's own list.

    The size is checked against the largest creature the game had
    before it rather than against a number, so that "biggest" stays a
    comparison. A dragon that is merely large is a hazard marker; what
    makes this one land is standing next to a rat one foot tall.
    """
    pygame.init()
    from generate_massive_dinosaur_sprites import (  # noqa: E402
        FRAME_H as DINO_H, FRAME_W as DINO_W,
    )

    assert len(DRAGONS) == 1, DRAGONS
    assert BlueDragon.WIDTH == FRAME_W and BlueDragon.HEIGHT == FRAME_H
    assert FRAME_W > DINO_W * 1.5 and FRAME_H > DINO_H * 1.5
    # ...and against Chuck, which is the comparison the player actually
    # makes: it has to be several times his height, not a bit taller.
    assert FRAME_H > config.CHUCK_FRAME_H * 6

    sheet = pygame.image.load(str(config.SPRITES_DIR / SPRITE))
    assert sheet.get_height() == FRAME_H
    assert sheet.get_width() % FRAME_W == 0
    frames = sheet.get_width() // FRAME_W
    assert frames > IDLE_FRAMES, "no separate pose for the breath"


def test_the_jaw_opens_before_the_bolt_does() -> None:
    """The half of the telegraph you can read without looking down.

    The lane lighting up is the precise warning and the one the timing
    is built on. It is also on the ground, which is not where a player
    looks when there is a dragon on the screen -- so the animal itself
    has to say it too, early enough to matter and from the same clock.
    """
    dragon = BlueDragon(200.0, 200.0, "left")
    dragon.elapsed = 0.0
    assert dragon.frame_index < IDLE_FRAMES, "gaping before it winds up"
    dragon.elapsed = WIND_UP * (GAPE_AT - 0.05)
    assert dragon.frame_index < IDLE_FRAMES
    dragon.elapsed = WIND_UP * (GAPE_AT + 0.05)
    assert dragon.frame_index >= IDLE_FRAMES, "no warning on the animal"
    assert GAPE_AT < 1.0, "the jaw opens with the bolt, not before it"
    dragon.elapsed = WIND_UP + BREATH * 0.5
    assert dragon.frame_index >= IDLE_FRAMES
    dragon.elapsed = WIND_UP + BREATH + SPENT * 0.5
    assert dragon.frame_index < IDLE_FRAMES, "still gaping after the bolt"

    # The idle frames really do cycle, or the wing never moves.
    seen = set()
    for step in range(40):
        dragon.elapsed = WIND_UP + BREATH + SPENT * 0.2 + step * 0.05
        if dragon.stage == "spent":
            seen.add(dragon.frame_index)
    assert len(seen) >= 3, seen

    # The bolt leaves the head rather than the middle of the animal.
    _, sy, _, sh = dragon.strike
    mouth = dragon.y + dragon.HEIGHT * dragon.MOUTH_Y
    assert sy < mouth < sy + sh
    assert mouth < dragon.y + dragon.HEIGHT * 0.5, "a bolt out of the chest"


def test_the_dragon_is_drawn_at_the_size_it_claims() -> None:
    """Blitted, not asserted.

    A sprite that is loaded and never drawn looks exactly like a sprite
    that works, right up until you stand next to it -- and this class
    drew itself out of polygons until recently, so the failure mode is
    a live one. Rendered here, and measured across the frame: the
    bounding box of the animal's own dark blue has to fill most of the
    box it says it occupies.
    """
    directory, game, world = _world()
    try:
        dragon = world.blue_dragons[0]
        assert len(dragon._frames) > IDLE_FRAMES
        # Spent, so the lane is dark and only the animal is on screen.
        dragon.elapsed = WIND_UP + BREATH + SPENT * 0.5
        world.camera.x = dragon.x + dragon.WIDTH / 2 - config.NATIVE_WIDTH // 2
        world.camera.y = dragon.y + dragon.HEIGHT / 2 - config.NATIVE_HEIGHT // 2
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.draw(surface)

        left = round(dragon.x - world.camera.x)
        top = round(dragon.y - world.camera.y)
        # Its own blue: darker and more saturated than any snow, ice or
        # sand on this map, so nothing behind it can be mistaken for it.
        found = [
            (x, y)
            for x in range(left, left + FRAME_W)
            for y in range(top, top + FRAME_H)
            if 0 <= x < config.NATIVE_WIDTH and 0 <= y < config.NATIVE_HEIGHT
            and (lambda p: p[2] > 110 and p[0] < 110 and p[2] > p[0] + 40)(
                surface.get_at((x, y))[:3])
        ]
        assert found, "nothing of the dragon was drawn"
        span_x = max(x for x, _ in found) - min(x for x, _ in found)
        span_y = max(y for _, y in found) - min(y for _, y in found)
        assert span_x > FRAME_W * 0.6, span_x
        assert span_y > FRAME_H * 0.6, span_y
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_dragons_stand_on_the_snow_and_can_be_left_alone() -> None:
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    spots = [(int(p[0]) // ts, int(p[1]) // ts)
             for k, p in tilemap.object_spawns if k.startswith("blue_dragon:")]
    assert len(spots) == len(DRAGONS) == 1, spots
    for cell in spots:
        assert tilemap.terrain_at(*cell) in SNOW_TERRAIN, cell

    arrival = next(p for k, p in tilemap.object_spawns
                   if k.startswith("arrival:"))
    origin = (int(arrival[0]) // ts, int(arrival[1]) // ts)
    reachable = _flood(tilemap, origin)
    east_gap = [(WIDTH - 1, y) for y in range(HEIGHT)
                if not tilemap.is_solid(WIDTH - 1, y)]
    assert len(east_gap) == GAP
    assert all(cell in reachable for cell in east_gap)

    # The shelf can be left alone entirely: the way on survives with
    # every frozen tile made solid.
    without = _flood(tilemap, origin, extra_solid={"❄", "❅", "❆"})
    assert all(cell in without for cell in east_gap), \
        "the shelf has closed the map"

    directory, game, world = _world()
    try:
        assert len(world.blue_dragons) == 1
        dragon = world.blue_dragons[0]
        # It stands on its own snow all the way under itself, not on a
        # square of it: the body is eight tiles across and anything
        # poking out from under it reads as the dragon sitting on a rug.
        left = int(dragon.x) // ts
        right = int(dragon.x + dragon.WIDTH - 1) // ts
        bottom = int(dragon.y + dragon.HEIGHT - 1) // ts
        for x in range(left, right + 1):
            assert world.tilemap.terrain_at(x, bottom) in SNOW_TERRAIN, x
    finally:
        game._shutdown()
        directory.cleanup()


def test_every_fragment_east_has_a_torn_seam() -> None:
    """The Astral fringe, across the whole traversal.

    A fragment with a clean boundary reads as having been laid on the
    sand. These collided, so the seams are torn -- and torn in
    stretches rather than evenly, because a boundary sampled evenly
    comes out as a dashed line round the fragment, which reads as
    somebody having drawn round it. That was the first attempt and it
    is why this measures run length rather than merely counting.
    """
    for name in EASTERN:
        tilemap = _tilemap(name)
        width, height = tilemap.width_tiles, tilemap.height_tiles
        astral = [(x, y) for y in range(height) for x in range(width)
                  if tilemap.terrain_at(x, y) == "V"]
        assert len(astral) > 30, (name, len(astral))

        # Clumped: a good share of the torn tiles have a torn tile
        # beside them. An evenly sampled seam scores near zero here.
        cells = set(astral)
        touching = sum(
            1 for x, y in cells
            if any((x + dx, y + dy) in cells
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        )
        assert touching > len(cells) * 0.7, (name, touching, len(cells))


def test_the_road_east_continues_and_it_has_its_own_entries() -> None:
    assert AREA_WALK_EXITS[(BEHIND, "⮞")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].destination == BEHIND

    ts = config.TILE_SIZE
    directory, game, world = _world(BEHIND)
    try:
        world.player.x = (world.tilemap.width_tiles - 1) * ts + 2
        world.player.y = (world.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            world.update(1 / 60)
        here = game.scenes.current
        assert here.map_name == MAP_NAME
        assert here.snow is not None
        here._arrival_fade_t = None
        here.player.x = 2.0
        here.player.y = (here.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            here.update(1 / 60)
        assert game.scenes.current.map_name == BEHIND
    finally:
        game._shutdown()
        directory.cleanup()

    for entry in (MAP_NAME,                   "desert_east_5_from_east_6"):
        assert CHECKPOINT_BY_ID[entry].required_flags == DESERT_ENTRY_FLAGS


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
    print("All east-6 tests passed.")


if __name__ == "__main__":
    _run_all()
