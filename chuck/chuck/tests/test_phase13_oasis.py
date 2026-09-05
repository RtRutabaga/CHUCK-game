"""Phase 13's oasis: the reward for walking west.

The phase document describes this one mostly by what it does not have.
No enemies, no route forward, nothing to solve. That makes the tests
here unusual: the important assertions are absences, and absences are
exactly what a later edit adds to without noticing.

The rest is the shape of a dead end. It is closed three ways -- rock
north, rock west, Astral Sea south -- and only one of those three is
something a player can walk into and survive, so "sealed" has to be
measured against the fall hazards as well as the walls.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.breakable_grass import BreakableGrass
from src.systems.checkpoints import CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import DESERT, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_desert_oasis import (  # noqa: E402
    ASTRAL, GAP, HEIGHT, NORTH_ROCK, RIM, WEST_ROCK, WIDTH,
)


MAP_NAME = "desert_oasis"
HUB = "desert_central"


def _tilemap() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _world(checkpoint: str = "desert_oasis"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _safe_flood(tilemap: TileMap, origin) -> set[tuple[int, int]]:
    """Everywhere Chuck can walk without falling out of the world.

    Solid tiles stop him; Astral tiles do not, they kill him -- so a
    plain solidity flood would call this map wide open to the south.
    """
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


def test_the_oasis_is_empty_of_everything_that_fights() -> None:
    """The document's own word for it: no enemies.

    Written as a list of the enemy collections the WorldScene keeps, so
    that adding a new kind of thing to a map cannot slip past a test
    that only remembered to look for zombies.
    """
    directory, game, world = _world()
    try:
        assert world.map_name == MAP_NAME
        hostile = (
            "undead", "raptors", "redcaps", "snakes", "spined_devils",
            "flameskulls", "cats", "displacer_beasts", "spitting_orchids",
            "massive_dinosaurs", "police", "sword_fighters",
        )
        for name in hostile:
            group = getattr(world, name, ())
            assert not group, (name, len(group))
        # ...and nothing authored on the map either, so this is a
        # property of the place and not of what happens to spawn.
        kinds = {kind for kind, _ in world.tilemap.object_spawns}
        assert kinds <= {"arrival:from_desert_central", "breakable_grass",
                         "anchor:desert_oasis_anchor"}, sorted(kinds)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_cigarette_grass_is_the_established_scratchable() -> None:
    """The same entity as everywhere else, on green ground.

    The phase document says to reuse the behaviour. In practice that
    means the marker resolves to the same class with the same drop --
    a lookalike tuft that gave nothing would satisfy a screenshot and
    fail the player.
    """
    from src.world.tilemap import MARKER_DEFS

    turf = MARKER_DEFS["⩏"]
    sand = MARKER_DEFS["<"]
    assert turf.kind == sand.kind == "breakable_grass"
    assert turf.under == "⩊" and sand.under == "."

    directory, game, world = _world()
    try:
        tufts = [b for b in world.breakables if isinstance(b, BreakableGrass)]
        assert len(tufts) >= 8, len(tufts)
        assert len(tufts) == len(world.breakables), "nothing else breakable"
        assert all(t.intact for t in tufts)

        # Every one of them can be walked up to.
        tilemap = world.tilemap
        ts = config.TILE_SIZE
        arrival = next(p for k, p in tilemap.object_spawns
                       if k == "arrival:from_desert_central")
        seen = _safe_flood(tilemap, (int(arrival[0]) // ts,
                                     int(arrival[1]) // ts))
        for kind, position in tilemap.object_spawns:
            if kind != "breakable_grass":
                continue
            assert (int(position[0]) // ts, int(position[1]) // ts) in seen, \
                position
    finally:
        game._shutdown()
        directory.cleanup()


def test_there_is_water_and_shade_to_walk_under() -> None:
    """The two things that make it an oasis rather than a clearing."""
    tilemap = _tilemap()
    water = sum(1 for y in range(HEIGHT) for x in range(WIDTH)
                if tilemap.terrain_at(x, y) == "~")
    turf = sum(1 for y in range(HEIGHT) for x in range(WIDTH)
               if tilemap.terrain_at(x, y) in ("⩊", "⏦", "⩏"))
    assert water >= 40, water
    # Small enough to be a pool rather than a lake: it should not be
    # most of the map, because the point of it is that you found it.
    assert water < WIDTH * HEIGHT * 0.10, water
    assert turf >= water * 0.4, (turf, water)

    # Water is solid -- Chuck does not swim.
    assert TILE_DEFS["~"].solid

    # The palms are an overhead layer: walkable ground with art drawn
    # on top of him, which is the whole reason they exist.
    palm = TILE_DEFS["⏦"]
    assert not palm.solid
    assert palm.overhead == "palm_canopy"
    assert palm.under == "⩊"
    assert DESERT.overhead_char_to_terrain["⏦"] == "palm_canopy"


def test_chuck_walks_underneath_the_palms() -> None:
    """Rendered, not asserted from the tile table.

    An overhead tile that is authored but never drawn looks exactly like
    an overhead tile that works, right up until you stand under one.
    """
    directory, game, world = _world()
    try:
        tilemap = world.tilemap
        palm = next((x, y) for y in range(HEIGHT) for x in range(WIDTH)
                    if tilemap.terrain_at(x, y) == "⏦")
        ts = config.TILE_SIZE
        world.player.x = palm[0] * ts
        world.player.y = palm[1] * ts
        world.camera.x = palm[0] * ts - config.NATIVE_WIDTH // 2
        world.camera.y = palm[1] * ts - config.NATIVE_HEIGHT // 2
        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.draw(surface)

        # Somewhere over him is frond, not rat and not turf: the palm
        # colours are darker than everything else on this map.
        screen_x = config.NATIVE_WIDTH // 2
        screen_y = config.NATIVE_HEIGHT // 2
        found = [
            surface.get_at((screen_x + dx, screen_y + dy))[:3]
            for dx in range(0, ts) for dy in range(0, ts)
        ]
        assert any(pixel[1] > pixel[0] and pixel[1] > pixel[2]
                   and sum(pixel) < 260 for pixel in found), \
            "no frond drawn over Chuck"
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_is_closed_three_ways_and_only_one_of_them_is_a_wall() -> None:
    tilemap = _tilemap()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (WIDTH, HEIGHT)
    assert tileset_for(MAP_NAME) is DESERT

    for y in range(HEIGHT):
        assert tilemap.terrain_at(0, y) in ("#", "V"), ("west", y)
    for x in range(WIDTH):
        assert tilemap.terrain_at(x, 0) == "#", ("north", x)
    # The south is Astral rather than rock, all the way across bar the
    # eastern rim column the rim itself claims back.
    southern = {tilemap.terrain_at(x, HEIGHT - 1) for x in range(WIDTH - RIM)}
    assert southern == {"V"}, southern

    # Both rock fronts are a mass, and both wander.
    fronts = [next((y for y in range(HEIGHT)
                    if tilemap.terrain_at(x, y) != "#"), HEIGHT)
              for x in range(WIDTH)]
    # The western front is measured above the Astral band only: down in
    # it the west edge is sea rather than rock, which is the point.
    reaches = [next((x for x in range(WIDTH)
                     if tilemap.terrain_at(x, y) != "#"), WIDTH)
               for y in range(HEIGHT - ASTRAL - 2)]
    assert min(fronts) >= 3, min(fronts)
    assert min(reaches) >= 3, min(reaches)
    assert len(set(fronts)) >= 4 and len(set(reaches)) >= 4
    assert NORTH_ROCK >= 3 and WEST_ROCK >= 3 and ASTRAL >= 3

    # ...and the only way off the map on your feet is the way in.
    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k == "arrival:from_desert_central")
    seen = _safe_flood(tilemap, (int(arrival[0]) // ts, int(arrival[1]) // ts))
    edge = sorted(cell for cell in seen
                  if cell[0] in (0, WIDTH - 1) or cell[1] in (0, HEIGHT - 1))
    assert len(edge) == GAP, edge
    assert {cell[0] for cell in edge} == {WIDTH - 1}


def test_the_road_west_is_walked_in_both_directions() -> None:
    assert AREA_WALK_EXITS[(HUB, "⮜")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "⮞")].destination == HUB
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[HUB], "one theme for the region"

    ts = config.TILE_SIZE
    directory, game, world = _world("desert_central_start")
    try:
        world.player.x = 2.0
        world.player.y = (world.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            world.update(1 / 60)
        oasis = game.scenes.current
        assert oasis.map_name == MAP_NAME
        oasis._arrival_fade_t = None

        oasis.player.x = (oasis.tilemap.width_tiles - 1) * ts + 2
        oasis.player.y = (oasis.tilemap.height_tiles // 2) * ts + 2
        for _ in range(4):
            oasis.update(1 / 60)
        back = game.scenes.current
        assert back.map_name == HUB
        # He comes back out of the west gap, not somewhere else.
        assert int(back.player.x) // ts <= RIM + 2, back.player.x
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_oasis_has_its_own_entries() -> None:
    for entry in ("desert_oasis", "desert_oasis_anchor",
                  "desert_central_from_oasis"):
        assert CHECKPOINT_BY_ID[entry].required_flags == DESERT_ENTRY_FLAGS
    anchor = CHECKPOINT_BY_ID["desert_oasis_anchor"]
    assert anchor.saveable
    # The ashtray stands on the turf. It paints its own under-terrain, so
    # placed out on the sand it drew one green square in a desert.
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    assert anchor.position is not None
    col, row = int(anchor.position[0]) // ts, int(anchor.position[1]) // ts
    assert tilemap.terrain_at(col, row) == "⩊"
    assert any(tilemap.terrain_at(col + dx, row + dy) == "⩊"
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))


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
    print("All oasis tests passed.")


if __name__ == "__main__":
    _run_all()
