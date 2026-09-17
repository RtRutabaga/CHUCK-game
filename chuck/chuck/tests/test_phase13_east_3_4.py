"""Phase 13's third and fourth eastern maps: the Feywild, then Hell.

These two are one step of the phase document's escalation taken in two
halves. East 3 makes the intrusion large enough to be a place rather
than a patch. East 4 makes it *cost* something -- it is the first map
east where the fragment cannot be walked past, and it is where the
document's "lava hazards where Hell fragments appear" lands.

The escalation itself is checked across the whole sequence rather than
one map at a time, because it is a property of the run of maps and each
new one has to extend it. That test lives here for now and should keep
being extended east; the day it becomes awkward it wants its own file.

The one thing that would be easy to get quietly wrong is east 4. A slab
that spans the map and a slab that spans the map *and can be crossed*
are one ford apart, and the difference between them is a phase that
cannot be finished. Both halves are proved by flooding.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.redcap import Redcap
from src.entities.spined_devil import SpinedDevil
from src.systems.checkpoints import CHECKPOINT_BY_ID, DESERT_ENTRY_FLAGS
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import COLLIDED, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

import sys
sys.path.insert(0, "tools")
from generate_desert_ruin_dressing import PIECES  # noqa: E402
from generate_collided_common import PROP_GROUND  # noqa: E402
from generate_desert_east_4 import (  # noqa: E402
    CHANNELS, FORDS, GAP, HEIGHT as H4, RIM, WIDTH as W4,
)


# The desert's own vocabulary, masonry included: a fallen column is
# the desert's, not an intruding world's, so it is counted here
# rather than being read as a fragment of somewhere else.
DESERT_GROUND = (".", ",", "⟁", "#", "⌗", "⌖", "⍟") + PIECES
# Every foreign character in the sequence so far, and its world.
FRAGMENTS = {
    "=": "modern_city", "≡": "modern_city",
    "ᛗ": "chult", "ᚷ": "chult", "ᚺ": "chult",
    "ᛟ": "feywild", "ᛇ": "feywild", "☼": "feywild", "ᛞ": "feywild",
    "·": "hell", "█": "hell", "≋": "hell",
}
# ...and what grows or falls on each of them. A tree on Chult's
# jungle is as much a piece of Chult as the jungle is, so the
# dressing is attributed through the ground it stands on rather
# than listed again by hand -- one table, and it cannot drift.
FRAGMENTS.update({
    prop: FRAGMENTS[ground]
    for prop, ground in PROP_GROUND.items()
    if ground in FRAGMENTS
})
SEQUENCE = ("desert_east_1", "desert_east_2", "desert_east_3",
            "desert_east_4")


def _tilemap(name: str) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _world(checkpoint: str):
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


def _survey(name: str) -> tuple[float, set[str]]:
    tilemap = _tilemap(name)
    width, height = tilemap.width_tiles, tilemap.height_tiles
    foreign, worlds = 0, set()
    for y in range(height):
        for x in range(width):
            char = tilemap.terrain_at(x, y)
            if char in FRAGMENTS:
                foreign += 1
                worlds.add(FRAGMENTS[char])
    return foreign / (width * height), worlds


def _entry(name: str) -> tuple[int, int]:
    tilemap = _tilemap(name)
    ts = config.TILE_SIZE
    arrival = next(p for k, p in tilemap.object_spawns
                   if k.startswith("arrival:"))
    return int(arrival[0]) // ts, int(arrival[1]) // ts


def test_each_map_east_is_further_gone_than_the_one_before() -> None:
    """The escalation, across the whole run rather than map by map.

    Every map added east should extend this list and keep it monotone.
    Comparisons rather than thresholds, so that a map tuned today does
    not become the number a map built next month has to work around.
    """
    shares, worlds = [], []
    for name in SEQUENCE:
        share, kinds = _survey(name)
        shares.append(share)
        worlds.append(kinds)

    assert shares == sorted(shares), shares
    assert shares[0] < 0.05, "the first one east must still read as desert"
    assert shares[-1] > 0.35, shares[-1]

    # More worlds on each map than the map behind it. Not a nested set:
    # each map has one big fragment that gives it its character, and
    # scraps of the ones met further back. What escalates is how many
    # different places are arriving at once.
    counts = [len(kinds) for kinds in worlds]
    assert counts == sorted(counts), counts
    assert counts[0] == 1 and counts[-1] >= 4, counts

    # ...and every world met so far is still turning up somewhere.
    cumulative: set[str] = set()
    for kinds in worlds:
        assert not kinds < cumulative, "a map introduced nothing new"
        cumulative |= kinds
    assert cumulative == {"modern_city", "chult", "feywild", "hell"}

    # ...and nothing on any of them is unaccounted for.
    for name in SEQUENCE:
        tilemap = _tilemap(name)
        seen = {tilemap.terrain_at(x, y)
                for y in range(tilemap.height_tiles)
                for x in range(tilemap.width_tiles)}
        assert seen <= set(DESERT_GROUND) | set(FRAGMENTS) | {"V", "⮜", "⮞"}, \
            (name, seen)


def test_the_feywild_is_a_place_you_can_enter_or_go_round() -> None:
    tilemap = _tilemap("desert_east_3")
    assert tileset_for("desert_east_3") is COLLIDED
    origin = _entry("desert_east_3")
    width, height = tilemap.width_tiles, tilemap.height_tiles

    east_gap = [(width - 1, y) for y in range(height)
                if not tilemap.is_solid(width - 1, y)]
    assert len(east_gap) == GAP

    # Round: the desert survives past it on at least one side.
    without = _flood(tilemap, origin, extra_solid=set(FRAGMENTS))
    assert all(cell in without for cell in east_gap), \
        "the fey mass has closed the desert off"

    # Into: the open fey ground is one connected piece, not a lattice.
    reachable = _flood(tilemap, origin)
    floor = [(x, y) for y in range(height) for x in range(width)
             if tilemap.terrain_at(x, y) == "ᛟ"]
    assert len(floor) > 400, len(floor)
    joined = [cell for cell in floor if cell in reachable]
    assert len(joined) > len(floor) * 0.9, (len(joined), len(floor))

    # The pools and the growth are things to walk round, not through.
    assert TILE_DEFS["ᛇ"].solid and TILE_DEFS["ᛞ"].solid
    assert not TILE_DEFS["ᛟ"].solid and not TILE_DEFS["☼"].solid

    directory, game, world = _world("desert_east_3")
    try:
        assert len(world.redcaps) >= 4
        assert all(isinstance(r, Redcap) for r in world.redcaps)
        assert not world.spined_devils
    finally:
        game._shutdown()
        directory.cleanup()


def test_hell_lies_across_the_way_and_has_to_be_crossed() -> None:
    """The first fragment east that is not optional.

    Two halves that are one ford apart: the slab spans the map, and the
    slab can be got over. A phase whose fourth map cannot be finished
    is a phase nobody notices is broken until they play it.
    """
    tilemap = _tilemap("desert_east_4")
    origin = _entry("desert_east_4")
    east_gap = [(W4 - 1, y) for y in range(H4)
                if not tilemap.is_solid(W4 - 1, y)]
    assert len(east_gap) == GAP

    # It spans: with Hell's own ground taken away there is no way on.
    hell = {"·", "█", "≋"}
    without = _flood(tilemap, origin, extra_solid=hell)
    assert not any(cell in without for cell in east_gap), \
        "there is a way round the slab"
    # ...and every row of the map has basalt in it, which is what
    # spanning means when the coasts are ragged.
    for y in range(RIM, H4 - RIM):
        row = {tilemap.terrain_at(x, y) for x in range(RIM, W4 - RIM)}
        assert row & hell, y

    # It can be crossed: the fords are real and the far side is open.
    reachable = _flood(tilemap, origin)
    assert all(cell in east_gap[:1] or cell in reachable
               for cell in east_gap), east_gap
    assert all(cell in reachable for cell in east_gap)
    assert len(FORDS) >= len(CHANNELS) * 2, "each channel wants a way over"

    # The lava is lethal, and there is enough of it to be the point.
    lava = [(x, y) for y in range(H4) for x in range(W4)
            if tilemap.terrain_at(x, y) == "≋"]
    assert len(lava) > 150, len(lava)
    assert "≋" in collision.FALL_HAZARD_TERRAIN
    assert not any(cell in reachable for cell in lava), \
        "the flood should refuse to walk on lava"

    directory, game, world = _world("desert_east_4")
    try:
        assert len(world.spined_devils) >= 3
        assert all(isinstance(d, SpinedDevil) for d in world.spined_devils)
        # They are past the crossing, so the slab is the danger and they
        # are what is waiting on the other side of it.
        ts = config.TILE_SIZE
        for devil in world.spined_devils:
            assert int(devil.x) // ts > max(CHANNELS)[0]
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_road_east_runs_through_both_in_both_directions() -> None:
    ts = config.TILE_SIZE
    for behind, ahead, entry in (
        ("desert_east_2", "desert_east_3", "desert_east_2"),
        ("desert_east_3", "desert_east_4", "desert_east_3"),
    ):
        assert AREA_WALK_EXITS[(behind, "⮞")].destination == ahead
        assert AREA_WALK_EXITS[(ahead, "⮜")].destination == behind
        assert AREA_MUSIC[ahead] == AREA_MUSIC[behind]

        directory, game, world = _world(entry)
        try:
            world.player.x = (world.tilemap.width_tiles - 1) * ts + 2
            world.player.y = (world.tilemap.height_tiles // 2) * ts + 2
            for _ in range(4):
                world.update(1 / 60)
            here = game.scenes.current
            assert here.map_name == ahead
            here._arrival_fade_t = None

            here.player.x = 2.0
            here.player.y = (here.tilemap.height_tiles // 2) * ts + 2
            for _ in range(4):
                here.update(1 / 60)
            assert game.scenes.current.map_name == behind
        finally:
            game._shutdown()
            directory.cleanup()


def test_both_maps_have_their_own_entries() -> None:
    for entry in ("desert_east_3", "desert_east_3",
                  "desert_east_2_from_east_3",
                  "desert_east_4", "desert_east_4",
                  "desert_east_3_from_east_4"):
        assert CHECKPOINT_BY_ID[entry].required_flags == DESERT_ENTRY_FLAGS
    for name in ("desert_east_3", "desert_east_4"):
        assert CHECKPOINT_BY_ID[name].development_visible
        tilemap = _tilemap(name)
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
    print("All east 3/4 tests passed.")


if __name__ == "__main__":
    _run_all()
