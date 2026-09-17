"""Phase 13's fifth eastern map: somewhere Chuck has never been.

Everything that has fallen into the desert so far was a place the
player remembers. This map is the phase document's other requirement --
fragments of worlds Chuck never visited, so that the collision reads as
much larger than the route he happened to walk -- and it brings two
things that need holding to.

The first is that the courtyard must not read as another ruin. The
region already has three kinds of fallen-down stone in it and this is
supposed to be somewhere still in use, so its wall is unbroken except
where it is gated. That is a property a later edit weathers away
without meaning to.

The second is the knight. The phase document allows new systems only
for the orc, the dragon, the final encounter and the final transition,
which means the knight has to be the existing pursuer with its numbers
moved -- and it is checked against the others rather than against
constants, so the range stays a range.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.undead import UndeadEnemy, _STATS
from src.systems.checkpoints import CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import COLLIDED, DOCKS, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_collided_common import PROP_GROUND  # noqa: E402
from generate_desert_ruin_dressing import PIECES  # noqa: E402
from generate_desert_east_5 import (  # noqa: E402
    COURT, GAP, GATES, HEIGHT, RIM, WIDTH,
)


MAP_NAME = "desert_east_5"
BEHIND = "desert_east_4"
# The desert's own vocabulary, masonry included.
DESERT_GROUND = (".", ",", "⟁", "#", "⌗", "⌖", "⍟") + PIECES


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


def _entry() -> tuple[int, int]:
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k.startswith("arrival:"))
    return int(arrival[0]) // ts, int(arrival[1]) // ts


def test_the_knight_is_the_pursuer_at_the_far_end_of_its_range() -> None:
    """New numbers, not a new system -- and measured against the rest.

    The phase document's architecture section allows new systems for
    four named things and the knight is not one of them. So it is the
    same class as the zombie with the dial pushed the other way from
    the orc's: heavier, slower, much harder to shift.
    """
    assert "knight" in _STATS
    knight = UndeadEnemy(0.0, 0.0, "knight")
    zombie = UndeadEnemy(0.0, 0.0, "zombie")
    orc = UndeadEnemy(0.0, 0.0, "orc")
    skeleton = UndeadEnemy(0.0, 0.0, "skeleton")
    assert type(knight) is type(zombie), "no bespoke knight class"

    # The slowest and the toughest of the four: armour, both ways.
    assert knight.speed < zombie.speed < orc.speed < skeleton.speed
    assert knight.max_scratches > orc.max_scratches > zombie.max_scratches
    assert knight.damage >= zombie.damage

    # Same lifecycle, no additions.
    for _ in range(knight.max_scratches):
        assert knight.alive
        knight.on_scratched()
    assert not knight.alive

    pygame.init()
    sheet = pygame.image.load(
        str(config.ASSETS_DIR / "sprites" / "hazards" / "knight.png"))
    assert sheet.get_size() == (config.UNDEAD_FRAME_W * 3,
                                config.UNDEAD_FRAME_H)


def test_the_courtyard_is_kept_rather_than_ruined() -> None:
    """Unbroken wall, gates, swept floor -- not a fourth kind of rubble.

    The region's ruins are all broken on purpose, by a rule that leaves
    two tiles in seven missing. This wall must not acquire that: it is
    the one thing separating a place that was taken from a place that
    fell down.
    """
    tilemap = _tilemap()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (WIDTH, HEIGHT)
    assert tileset_for(MAP_NAME) is COLLIDED

    left, top, width, height = COURT
    right, bottom = left + width - 1, top + height - 1
    perimeter = [
        (x, y) for y in range(top, bottom + 1) for x in range(left, right + 1)
        if y in (top, bottom) or x in (left, right)
    ]
    # The wall's own vocabulary. It was ashlar and gate-gap when the
    # courtyard was first built; it is now ashlar, crenellation, drum
    # towers, the corner turrets standing on them, and the banners
    # hanging on the wall itself -- and a gate is still a gap and
    # nothing else. The banners used to be able to land in one, because
    # they hung on open ground and a gate gap is open ground; they are
    # stone now and cannot.
    STONEWORK = {"⌾", "ᛦ", "ᛧ", "ᛪ", "ᛮ"}
    gates = sum(1 for cell in perimeter
                if tilemap.terrain_at(*cell) == "⌽")
    walls = sum(1 for cell in perimeter
                if tilemap.terrain_at(*cell) in STONEWORK)
    assert walls + gates == len(perimeter), "something else is in the wall"
    # ...and it is a castle rather than a boundary: notched, towered,
    # and flying somebody's colours.
    assert any(tilemap.terrain_at(*cell) == "ᛦ" for cell in perimeter)
    assert any(tilemap.terrain_at(*cell) == "ᛧ" for cell in perimeter)
    # Three tiles per gate and nothing else missing.
    assert gates == len(GATES) * 3, gates

    # It is not Waterdeep's castle: the docks sheet has a castle_wall
    # row of its own and this must not be it, because the phase
    # document asks for somewhere clearly distinct from the docks.
    assert "castle_wall" in DOCKS.info()
    assert "castle_wall" not in COLLIDED.info()
    assert "courtyard_wall" in COLLIDED.info()

    assert TILE_DEFS["⌾"].solid and not TILE_DEFS["⌽"].solid


def test_the_knights_are_inside_and_the_walls_can_be_gone_round() -> None:
    tilemap = _tilemap()
    origin = _entry()
    ts = config.TILE_SIZE
    reachable = _flood(tilemap, origin)

    east_gap = [(WIDTH - 1, y) for y in range(HEIGHT)
                if not tilemap.is_solid(WIDTH - 1, y)]
    assert len(east_gap) == GAP
    assert all(cell in reachable for cell in east_gap)

    # Round: with the whole castle solid the way on still exists, so
    # fighting through the knights is a choice rather than the route.
    without = _flood(tilemap, origin, extra_solid={"⌽", "⌾"})
    assert all(cell in without for cell in east_gap), \
        "the courtyard has closed the map"

    # ...and in: the courtyard is enterable, and the knights are in it.
    floor = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
             if tilemap.terrain_at(x, y) == "⌽"]
    assert len(floor) > 400
    assert sum(1 for cell in floor if cell in reachable) > len(floor) * 0.95

    knights = [(int(p[0]) // ts, int(p[1]) // ts)
               for k, p in tilemap.object_spawns if k == "knight"]
    assert len(knights) >= 5
    left, top, width, height = COURT
    for cell in knights:
        assert left < cell[0] < left + width - 1, cell
        assert top < cell[1] < top + height - 1, cell
        assert cell in reachable, cell

    directory, game, world = _world()
    try:
        assert len([u for u in world.undead if u.kind == "knight"]) >= 5
        assert all(u.kind == "knight" for u in world.undead)
    finally:
        game._shutdown()
        directory.cleanup()


def test_two_hazards_stand_in_the_same_place() -> None:
    """The document's familiar systems in new combinations.

    A fall and a burn, side by side, which have belonged to separate
    regions for the whole game. Checked as adjacency rather than as two
    counts, because two hazards at opposite corners of a map is not a
    combination, it is a list.
    """
    tilemap = _tilemap()
    lava = {(x, y) for y in range(HEIGHT) for x in range(WIDTH)
            if tilemap.terrain_at(x, y) == "≋"}
    astral = {(x, y) for y in range(HEIGHT) for x in range(WIDTH)
              if tilemap.terrain_at(x, y) == "V"}
    assert len(lava) >= 12, len(lava)
    assert len(astral) >= 40, len(astral)
    for char in ("≋", "V"):
        assert char in collision.FALL_HAZARD_TERRAIN

    # They meet: some lava is within a few tiles of the tear.
    close = [cell for cell in lava
             if any(abs(cell[0] - a[0]) + abs(cell[1] - a[1]) <= 4
                    for a in astral)]
    assert close, "the two hazards are nowhere near each other"

    # ...and neither can be walked on.
    reachable = _flood(tilemap, _entry())
    assert not (lava | astral) & reachable


def test_the_worlds_keep_arriving() -> None:
    """Five worlds on this one, and the ship among them."""
    tilemap = _tilemap()
    fragments = {
        "=": "modern_city", "≡": "modern_city",
        "ᛗ": "chult", "ᚷ": "chult", "ᚺ": "chult",
        "ᛟ": "feywild", "ᛇ": "feywild", "☼": "feywild", "ᛞ": "feywild",
        "·": "hell", "█": "hell", "≋": "hell",
        "⌼": "ship",
        "⌽": "medieval", "⌾": "medieval",
        # The castle, finished: its crenellation, its drum towers, the
        # turrets on its corners and the banners hanging on its walls.
        # All of it the same world.
        "ᛦ": "medieval", "ᛧ": "medieval",
        "ᛪ": "medieval", "ᛮ": "medieval",
    }
    # ...and everything standing on them. A bush on the Feywild's floor
    # is a piece of the Feywild, so it is attributed through the ground
    # it grows out of rather than listed again here.
    fragments.update({
        prop: fragments[ground]
        for prop, ground in PROP_GROUND.items()
        if ground in fragments
    })
    worlds = {fragments[tilemap.terrain_at(x, y)]
              for y in range(HEIGHT) for x in range(WIDTH)
              if tilemap.terrain_at(x, y) in fragments}
    assert worlds == {"modern_city", "chult", "feywild", "hell", "ship",
                      "medieval"}, worlds
    seen = {tilemap.terrain_at(x, y)
            for y in range(HEIGHT) for x in range(WIDTH)}
    allowed = set(DESERT_GROUND) | set(fragments) | {"V", "⮜", "⮞"}
    assert seen <= allowed, seen


def test_the_road_east_continues_in_both_directions() -> None:
    assert AREA_WALK_EXITS[(BEHIND, "⮞")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "⮜")].destination == BEHIND
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[BEHIND]

    ts = config.TILE_SIZE
    directory, game, world = _world(BEHIND)
    try:
        world.player.x = (world.tilemap.width_tiles - 1) * ts + 2
        world.player.y = (world.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            world.update(1 / 60)
        here = game.scenes.current
        assert here.map_name == MAP_NAME
        here._arrival_fade_t = None
        here.player.x = 2.0
        here.player.y = (here.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            here.update(1 / 60)
        assert game.scenes.current.map_name == BEHIND
    finally:
        game._shutdown()
        directory.cleanup()

    for entry in (MAP_NAME,                   "desert_east_4_from_east_5"):
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
    print("All east-5 tests passed.")


if __name__ == "__main__":
    _run_all()
