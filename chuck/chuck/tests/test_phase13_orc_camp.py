"""Phase 13's orc camp: the first thing north of the hub.

The phase document is unusually specific here, and specific in a way
that is easy to satisfy loosely. Orcs must be built on the existing
undead architecture rather than given a combat system of their own;
they must be *slightly* faster than a zombie and tougher; the sacks
must be the Waterdeep pantry's, not desert-styled lookalikes; and the
north and west edges must be closed by rock. Each of those is checked
against the thing it is supposed to match rather than against a number
copied out of the document, so that changing one end moves the other.

The rest is the property that makes the camp an encounter rather than a
wall: everything in it can be reached, the only way out is the way in,
and the ground you arrive on is clear.
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
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_desert_orc_camp import (  # noqa: E402
    APPROACH, GAP, HEIGHT, RIM, WIDTH,
)


MAP_NAME = "desert_orc_camp"
HUB = "desert_central"


def _tilemap(name: str = MAP_NAME) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _world(checkpoint: str = "desert_orc_camp"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _flood(tilemap: TileMap, origin: tuple[int, int]) -> set[tuple[int, int]]:
    seen = {origin}
    frontier = [origin]
    while frontier:
        x, y = frontier.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in seen or tilemap.is_solid(*cell):
                continue
            seen.add(cell)
            frontier.append(cell)
    return seen


def test_orcs_are_the_undead_architecture_with_the_dial_moved() -> None:
    """Built on it, not beside it -- and measured against the zombie."""
    assert "orc" in _STATS
    orc = UndeadEnemy(0.0, 0.0, "orc")
    zombie = UndeadEnemy(0.0, 0.0, "zombie")
    skeleton = UndeadEnemy(0.0, 0.0, "skeleton")
    assert type(orc) is type(zombie), "no bespoke orc class"

    # Slightly faster than a zombie -- and still slower than a skeleton,
    # because "slightly" is the word the phase document uses.
    assert zombie.speed < orc.speed < skeleton.speed
    assert orc.speed - zombie.speed <= zombie.speed * 0.35
    # ...and tougher than a zombie, which is the other half of the ask.
    assert orc.max_scratches > zombie.max_scratches

    # It fights by walking at you and nothing else: the same update,
    # the same scratch lifecycle, no new system.
    orc.on_scratched()
    assert orc.scratches_remaining == orc.max_scratches - 1
    for _ in range(orc.max_scratches):
        orc.on_scratched()
    assert not orc.alive

    pygame.init()
    sheet = pygame.image.load(
        str(config.ASSETS_DIR / "sprites" / "hazards" / "orc.png"))
    assert sheet.get_size() == (config.UNDEAD_FRAME_W * 3,
                                config.UNDEAD_FRAME_H)


def test_the_camp_stores_are_the_pantrys_own_sacks() -> None:
    """The same asset and the same behaviour, on different ground.

    The phase document asks for reuse by name. What that has to mean in
    practice is that a player who scratched one open in Waterdeep gets
    the identical thing here -- so this checks the prop, not a sprite
    that happens to look similar.
    """
    camp = TILE_DEFS["⛰"]
    pantry = TILE_DEFS["z"]
    assert camp.prop == pantry.prop == "grain_sack"
    assert camp.solid == pantry.solid
    # Only the ground under it differs, which is all `under` is for.
    assert camp.under == "." and pantry.under == "p"

    directory, game, world = _world()
    try:
        sacks = [b for b in world.breakables
                 if type(b).__name__ == "PantryJar"]
        assert len(sacks) >= 6, len(sacks)
        # ...and they are the map's own sacks, not decoration: one
        # breakable per authored tile.
        authored = [1 for kind, _, _ in world.tilemap.prop_tiles
                    if kind == "grain_sack"]
        assert len(sacks) == len(authored)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_canyon_closes_the_north_and_west() -> None:
    """Rock where the document says rock, and one way out.

    The edges are checked as a whole rather than sampled: a cliff with a
    hole in it is a map that leaks, and a hole two tiles wide in a
    wandering front is exactly the kind of thing that survives a glance.
    """
    tilemap = _tilemap()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (WIDTH, HEIGHT)
    assert tileset_for(MAP_NAME).sheet == "desert.png"

    for y in range(HEIGHT):
        assert tilemap.terrain_at(0, y) == "#", ("west", y)
    for x in range(WIDTH):
        assert tilemap.terrain_at(x, 0) == "#", ("north", x)

    # The rock is a mass, not a line: several tiles deep along both.
    # How far in the rock reaches, column by column and row by row.
    # Some of both are solid the whole way -- the corner where the two
    # fronts meet is one mass -- so the sentinel is the map's own size.
    fronts = [
        next((y for y in range(HEIGHT) if tilemap.terrain_at(x, y) != "#"),
             HEIGHT)
        for x in range(WIDTH)
    ]
    reaches = [
        next((x for x in range(WIDTH) if tilemap.terrain_at(x, y) != "#"),
             WIDTH)
        for y in range(HEIGHT)
    ]
    assert min(fronts) >= 3, min(fronts)
    assert min(reaches) >= 3, min(reaches)

    # ...and both wander, rather than being ruled straight.
    assert len(set(fronts)) >= 5, sorted(set(fronts))
    assert len(set(reaches)) >= 5, sorted(set(reaches))


def test_everything_in_the_camp_can_be_reached_and_nothing_else_can() -> None:
    tilemap = _tilemap()
    arrival = [position for kind, position in tilemap.object_spawns
               if kind == "arrival:from_desert_central"]
    assert len(arrival) == 1
    ts = config.TILE_SIZE
    origin = (int(arrival[0][0]) // ts, int(arrival[0][1]) // ts)
    seen = _flood(tilemap, origin)

    # Every sack has walkable ground beside it, or it cannot be scratched.
    sacks = [(col, row) for kind, col, row in tilemap.prop_tiles
             if kind == "grain_sack"]
    assert len(sacks) >= 6
    for col, row in sacks:
        assert any((col + dx, row + dy) in seen
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), (col, row)

    # Every orc stands on ground it can walk off.
    orcs = [(int(p[0]) // ts, int(p[1]) // ts)
            for kind, p in tilemap.object_spawns if kind == "orc"]
    assert len(orcs) >= 5
    for cell in orcs:
        assert cell in seen, cell

    anchor = [p for kind, p in tilemap.object_spawns
              if kind == "anchor:desert_orc_camp_anchor"]
    assert len(anchor) == 1
    assert (int(anchor[0][0]) // ts, int(anchor[0][1]) // ts) in seen

    # The way in is the only way out. Anything else on the boundary is
    # a leak in the canyon.
    edge = sorted(cell for cell in seen
                  if cell[0] in (0, WIDTH - 1) or cell[1] in (0, HEIGHT - 1))
    assert len(edge) == GAP, edge
    assert {cell[1] for cell in edge} == {HEIGHT - 1}


def test_you_are_not_ambushed_on_the_way_in() -> None:
    """Clear ground at the threshold.

    An orc standing in the doorway is not an encounter, it is a toll --
    the player should be able to see the camp before it reaches them.
    """
    tilemap = _tilemap()
    ts = config.TILE_SIZE
    mid_x = WIDTH // 2
    half = GAP // 2
    orcs = {(int(p[0]) // ts, int(p[1]) // ts)
            for kind, p in tilemap.object_spawns if kind == "orc"}
    for x in range(mid_x - half, mid_x + half + 1):
        for y in range(HEIGHT - RIM - APPROACH, HEIGHT - RIM):
            assert not tilemap.is_solid(x, y), (x, y)
            assert (x, y) not in orcs, (x, y)


def test_the_road_north_is_walked_in_both_directions() -> None:
    """Out of the hub and back into it, for real.

    Both halves matter. A one-way exit is a map you can fall into, and
    the hub's north gap was cut before this map existed -- so this also
    proves the gap became a door rather than the map being reshaped.
    """
    assert AREA_WALK_EXITS[(HUB, "⮝")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "⮟")].destination == HUB
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[HUB], "one theme for the region"

    ts = config.TILE_SIZE
    directory, game, world = _world("desert_central_start")
    try:
        assert world.map_name == HUB
        world.player.x = (world.tilemap.width_tiles // 2) * ts + 2
        world.player.y = 2.0
        for _ in range(4):
            world.update(1 / 60)
        camp = game.scenes.current
        assert camp.map_name == MAP_NAME
        assert len([u for u in camp.undead if u.kind == "orc"]) >= 5
        camp._arrival_fade_t = None

        camp.player.x = (camp.tilemap.width_tiles // 2) * ts + 2
        camp.player.y = (camp.tilemap.height_tiles - 1) * ts + 2
        for _ in range(4):
            camp.update(1 / 60)
        back = game.scenes.current
        assert back.map_name == HUB
        # He comes back out of the north gap, not somewhere else.
        assert int(back.player.y) // ts <= RIM + 2, back.player.y
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_camp_has_its_own_entries() -> None:
    for entry in ("desert_orc_camp", "desert_orc_camp_anchor",
                  "desert_central_from_orc_camp"):
        checkpoint = CHECKPOINT_BY_ID[entry]
        assert checkpoint.required_flags == DESERT_ENTRY_FLAGS, entry
    assert CHECKPOINT_BY_ID["desert_orc_camp_anchor"].saveable
    assert CHECKPOINT_BY_ID["desert_orc_camp"].development_visible


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
    print("All orc camp tests passed.")


if __name__ == "__main__":
    _run_all()
