"""Phase 13's undead ruins: the reward for walking south.

The one thing here that could go quietly and badly wrong is the chest.
The phase document asks for the sea captain's chest language, and the
honest way to give a player that language is to give them that chest --
but the captain's chest is keyed to a specific pair of progress flags,
and a second one sharing them would open itself the moment the first
was opened and pay out once between the two. So the flags moved from
the class to the instance, and the test that matters is that the two
chests do not know about each other.

The rest is the shape of a place worth walking into: one building with
rooms rather than scattered rubble, a chest far enough inside that
reaching it means going past the skeletons, and the Astral Sea closing
the two sides the document names.

This file used to also assert that the hub had three doors and four
identical gaps. The eastern route gave it its fourth door, and the
stronger version of that property -- four doors, four identical gaps,
four identical approaches -- lives in the east-1 suite now, where the
temptation to start hinting at the way forward actually arises.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.captain_chest import CaptainChest
from src.entities.undead import UndeadEnemy
from src.systems.checkpoints import CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS
from src.systems.checkpoints import KNOWN_PROGRESS_FLAGS
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import DESERT, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_desert_undead_ruins import (  # noqa: E402
    ASTRAL, CHEST, COURT, GAP, GATE, GREAT_PILLARS, HEIGHT, OUTER, RIM,
    WIDTH,
)


MAP_NAME = "desert_undead_ruins"
HUB = "desert_central"


def _tilemap() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _world(checkpoint: str = "desert_undead_ruins"):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _safe_flood(tilemap: TileMap, origin) -> set[tuple[int, int]]:
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


def test_the_two_chests_do_not_know_about_each_other() -> None:
    """The same chest, twice, with separate memories.

    Keyed to one pair of flags, opening the captain's would have opened
    this one across the map and spent its carton -- so the important
    assertion is not that the desert chest works, it is that using one
    leaves the other shut.
    """
    for flag in ("desert_ruin_chest_opened",
                 "desert_ruin_chest_carton_collected"):
        assert flag in KNOWN_PROGRESS_FLAGS, flag
    assert CaptainChest.progress_flag == "captain_chest_opened"
    assert CaptainChest.collected_flag == "captain_chest_carton_collected"

    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        game.checkpoints.load_checkpoint(
            "desert_undead_ruins", progress_flags=set(DESERT_ENTRY_FLAGS)
        )
        ruins = CaptainChest(
            2, 2, game.assets, game.progress, kind="desert_ruin_chest",
            progress_flag="desert_ruin_chest_opened",
            collected_flag="desert_ruin_chest_carton_collected",
        )
        ship = CaptainChest(4, 4, game.assets, game.progress)
        assert not ruins.opened and not ship.opened

        ruins.on_scratched()
        ruins.update(CaptainChest.opening_duration)
        assert ruins.opened
        assert game.progress.has("desert_ruin_chest_opened")
        # The captain's is untouched, in its own state and its own flag.
        assert not ship.opened
        assert not game.progress.has("captain_chest_opened")

        # ...and the carton it drops banks the desert's flag, not the
        # captain's, so the ship's reward is still there to collect.
        drop = ruins.take_drop_position()
        assert drop is not None
        carton = ruins.create_pickup(drop, game.assets)
        assert carton.progress_flag == "desert_ruin_chest_carton_collected"
        from src.entities.pickup import GoldenCigaretteCarton
        assert isinstance(carton, GoldenCigaretteCarton)
        assert GoldenCigaretteCarton.progress_flag == \
            "captain_chest_carton_collected"
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_chest_is_the_captains_chest_and_it_is_in_the_courtyard() -> None:
    tile = TILE_DEFS["⎈"]
    assert tile.prop == "desert_ruin_chest"
    assert tile.solid and tile.under == "⌖"

    directory, game, world = _world()
    try:
        chests = [p for p in world.props
                  if isinstance(p, CaptainChest)]
        assert len(chests) == 1
        chest = chests[0]
        assert chest.kind == "desert_ruin_chest"
        assert chest.progress_flag == "desert_ruin_chest_opened"
        # Literally the captain's art: the same sheet, so a player who
        # opened one in the captain's quarters knows what this is.
        assert chest._frames
        assert len(chest._frames) == len(
            game.assets.sheet("objects/ship_captain_chest.png", 32, 24)[0])
    finally:
        game._shutdown()
        directory.cleanup()

    # ...and it stands inside the courtyard, inside the building.
    left, top, width, height = COURT
    assert left < CHEST[0] < left + width - 1
    assert top < CHEST[1] < top + height - 1
    outer_left, outer_top, outer_w, outer_h = OUTER
    assert outer_left < CHEST[0] < outer_left + outer_w - 1
    assert outer_top < CHEST[1] < outer_top + outer_h - 1


def test_skeletons_patrol_it_and_they_are_the_chult_skeletons() -> None:
    directory, game, world = _world()
    try:
        bones = [u for u in world.undead if u.kind == "skeleton"]
        assert len(bones) >= 8, len(bones)
        assert all(isinstance(u, UndeadEnemy) for u in bones)
        # Unchanged from the implementation Chult established.
        reference = UndeadEnemy(0.0, 0.0, "skeleton")
        assert {b.speed for b in bones} == {reference.speed}
        assert {b.max_scratches for b in bones} == {reference.max_scratches}
        assert all(u.kind == "skeleton" for u in world.undead), \
            "the ruins are skeletons only"
    finally:
        game._shutdown()
        directory.cleanup()


def test_it_reads_as_a_building_rather_than_as_rubble() -> None:
    """Corners, doorways, and an inside you can get into.

    The hub already has scattered broken rectangles in it. This map only
    earns its own place on the map if it is legibly somebody's building,
    and the cheapest test of that is that its outer wall has four intact
    corners and more than one way through.
    """
    tilemap = _tilemap()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (WIDTH, HEIGHT)
    assert tileset_for(MAP_NAME) is DESERT

    left, top, width, height = OUTER
    right, bottom = left + width - 1, top + height - 1
    for corner in ((left, top), (right, top), (left, bottom), (right, bottom)):
        assert tilemap.terrain_at(*corner) == "⌗", corner

    # The wall is broken, but not mostly missing.
    wall_cells = [
        (x, y) for y in range(top, bottom + 1) for x in range(left, right + 1)
        if y in (top, bottom) or x in (left, right)
    ]
    standing = sum(1 for cell in wall_cells if tilemap.terrain_at(*cell) == "⌗")
    assert 0.55 < standing / len(wall_cells) < 0.95, standing / len(wall_cells)

    # There is floor inside it, and a good deal of it.
    floor = sum(1 for y in range(top, bottom + 1)
                for x in range(left, right + 1)
                if tilemap.terrain_at(x, y) in ("⌖", "ᛏ"))
    assert floor > width * height * 0.4, floor


def test_the_building_is_the_size_the_fragments_implied() -> None:
    """A great order, a gate, and a wall with two leaves to it.

    Every column in here was a broken one, because the whole ruin
    vocabulary is *fragments* -- which is right for the hub, where the
    scattered rectangles are pieces of this building, and wrong here,
    where this is the building. Nothing on the map was ever the size
    the fragments were fragments of.

    So: pillars nearly seven tiles tall against the old ones' three, a
    gate still standing whole over the way in, and an outer wall built
    two tiles thick instead of one. One tile of stone is a garden wall.
    """
    tilemap = _tilemap()
    from PIL import Image

    objects = config.SPRITES_DIR / "objects"
    with Image.open(objects / "desert_column_1.png") as small:
        with Image.open(objects / "desert_great_pillar_1.png") as great:
            assert great.height > small.height * 2, (great.size, small.size)
            # ...and still on a one-tile footprint, so a pillar can
            # stand anywhere a small column could and can never be the
            # reason a room closed.
            assert great.width > config.TILE_SIZE
            assert great.width < config.TILE_SIZE * 2

    standing = [(col, row) for kind, col, row in tilemap.prop_tiles
                if kind == "desert_great_pillar"]
    assert len(standing) >= 8, standing
    assert set(standing) <= set(GREAT_PILLARS), \
        sorted(set(standing) - set(GREAT_PILLARS))
    for col, row in standing:
        assert tilemap.is_solid(col, row), (col, row)

    # The wall is two leaves for most of its run, and not for all of it:
    # the facing stays up and the rubble core behind it goes, so the
    # thickness has to come and go or two tiles of wall read as one
    # tile of wall drawn twice.
    left, top, width, height = OUTER
    right, bottom = left + width - 1, top + height - 1
    doubled = sum(
        1 for col in range(left, right + 1)
        if tilemap.terrain_at(col, top) == "⌗"
        and tilemap.terrain_at(col, top + 1) == "⌗"
    )
    single = sum(1 for col in range(left, right + 1)
                 if tilemap.terrain_at(col, top) == "⌗")
    assert 0.4 < doubled / single < 0.95, (doubled, single)


def test_the_gate_is_the_one_thing_still_whole_and_chuck_walks_under_it():
    """An arch over the door the player arrives at.

    A ruin where everything has fallen is a field of rubble; one thing
    left standing is what says how high the rest of it was. It is one
    sprite five tiles across rather than five tiles of art, because
    what makes an arch read is the curve running unbroken from one pier
    into the other and a curve cut into sixteen-pixel tiles is a
    staircase.
    """
    tilemap = _tilemap()
    left, top, _width, _height = OUTER

    arch = [(col, row) for kind, col, row in tilemap.prop_tiles
            if kind == "desert_ruin_arch"]
    assert arch == [(GATE, top)], arch

    from PIL import Image
    with Image.open(config.SPRITES_DIR / "objects"
                    / "desert_ruin_arch.png") as sprite:
        assert sprite.width == config.TILE_SIZE * 5, sprite.size
        # Anchored on the middle tile and drawn upward, so it covers
        # exactly the two tiles either side of the opening.
        assert sprite.height > config.TILE_SIZE * 5

    # The opening is three tiles of it, and they are walkable...
    for offset in (-1, 0, 1):
        assert not tilemap.is_solid(GATE + offset, top), offset
        assert not tilemap.is_solid(GATE + offset, top + 1), offset
    # ...and what is solid about the gate is the stone that looks it.
    for offset in (-2, 2):
        assert tilemap.terrain_at(GATE + offset, top) == "⌗", offset
        assert tilemap.terrain_at(GATE + offset, top + 1) == "⌗", offset

    # And it is a way in rather than a monument: the sand in front of
    # the gate reaches the floor behind it.
    seen = _safe_flood(tilemap, (GATE, top - 2))
    assert (GATE, top + 2) in seen


def test_the_sea_closes_the_west_and_south_and_the_chest_is_reachable() -> None:
    tilemap = _tilemap()
    for y in range(RIM, HEIGHT - 1):
        assert tilemap.terrain_at(0, y) == "V", ("west", y)
    for x in range(RIM, WIDTH - RIM):
        assert tilemap.terrain_at(x, HEIGHT - 1) == "V", ("south", x)
    assert ASTRAL >= 3

    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k == "arrival:from_desert_central")
    seen = _safe_flood(tilemap, (int(arrival[0]) // ts,
                                 int(arrival[1]) // ts))

    # The chest is solid, so what has to be reachable is a tile beside it.
    assert any((CHEST[0] + dx, CHEST[1] + dy) in seen
               for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), \
        "the courtyard is sealed"

    for kind, position in tilemap.object_spawns:
        if kind != "skeleton":
            continue
        cell = (int(position[0]) // ts, int(position[1]) // ts)
        assert cell in seen, (kind, cell)

    # Only the way in is a way out on your feet.
    edge = sorted(cell for cell in seen
                  if cell[0] in (0, WIDTH - 1) or cell[1] in (0, HEIGHT - 1))
    assert len(edge) == GAP, edge
    assert {cell[1] for cell in edge} == {0}


def test_the_road_south_is_walked_in_both_directions() -> None:
    assert AREA_WALK_EXITS[(HUB, "⮟")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "⮝")].destination == HUB
    assert AREA_MUSIC[MAP_NAME] == AREA_MUSIC[HUB]

    ts = config.TILE_SIZE
    directory, game, world = _world("desert_central_start")
    try:
        world.player.x = (world.tilemap.width_tiles // 2) * ts + 2
        world.player.y = (world.tilemap.height_tiles - 1) * ts + 2
        for _ in range(4):
            world.update(1 / 60)
        ruins = game.scenes.current
        assert ruins.map_name == MAP_NAME
        assert len(ruins.undead) >= 8
        ruins._arrival_fade_t = None

        ruins.player.x = (ruins.tilemap.width_tiles // 2) * ts + 2
        ruins.player.y = 2.0
        for _ in range(4):
            ruins.update(1 / 60)
        back = game.scenes.current
        assert back.map_name == HUB
        assert int(back.player.y) // ts >= back.tilemap.height_tiles - RIM - 4
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_ruins_have_their_own_entries() -> None:
    for entry in ("desert_undead_ruins", "desert_undead_ruins",
                  "desert_central_from_ruins"):
        assert CHECKPOINT_BY_ID[entry].required_flags == DESERT_ENTRY_FLAGS

    tilemap = _tilemap()
    ts = config.TILE_SIZE


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
    print("All undead ruins tests passed.")


if __name__ == "__main__":
    _run_all()
