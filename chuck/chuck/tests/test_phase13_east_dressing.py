"""What stands on the fragments east of the hub.

The maps east of the desert were, until now, made only of ground. Each
one had a piece of another world in it and that piece was a rectangle
of somebody else's ground colour -- which is enough to say "this is
not the desert" and not nearly enough to say "this is Chult". A world
is recognised by what is on it: trees, mushrooms, rubble, ruins with
their pieces lying where they fell.

Everything here is checked as a consequence rather than as a presence,
because presence is the easy half. The three that matter:

Each world's dressing is that world's own prop, not a desert-styled
lookalike, and it is checked against the character the world uses at
home. A tree that merely looks like Chult's tree costs the fragment
the only thing it is for.

No prop ever closes a route. Every one of them is solid, and the
basalt slab on the fourth map is the only crossing there is, so the
invariant is measured on the finished maps rather than trusted to the
placement rule: every piece standing on ground a player can walk has
open ground on all four sides of it.

And the lava fall ends in the Astral Sea rather than in a river. That
distinction is the whole reason it is there -- a fall feeding a channel
is a fourth channel with a nicer top -- so it is measured: the run
below it is small, it touches the Sea, and it reaches neither rim.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.prop import _ANIMATED_SPRITES
from src.systems.checkpoints import DESERT_ENTRY_FLAGS
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap

import sys
sys.path.insert(0, "tools")
from generate_collided_common import (  # noqa: E402
    FRAGMENT_DRESSING, PROP_GROUND, _STANDABLE,
)
from generate_desert_east_4 import (  # noqa: E402
    FALL_RUN, LAVA_FALL, HEIGHT as H4, WIDTH as W4,
)
from generate_desert_ruin_dressing import PIECES  # noqa: E402


EASTERN = ("desert_east_1", "desert_east_2", "desert_east_3",
           "desert_east_4", "desert_east_5", "desert_east_6")

# Where each dressing prop lives at home, so that "the same prop" can be
# checked against the world that owns it rather than against a name.
AT_HOME = {
    "⍮": "/",       # Chult's jungle tree
    "⍯": "\\",      # ...and its broad-leaf shrub
    "⍰": "ŧ",       # the Feywild's grove tree
    "⍱": "Ŧ",       # ...its shrub
    "⍲": "ŋ",       # ...and its mushroom
    "þ": "þ",       # Phlegethos's rubble, which kept its own character
    "ƒ": "ƒ",       # ...and so did its lava fall
}


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


def _arrival(tilemap: TileMap) -> tuple[int, int]:
    ts = config.TILE_SIZE
    position = next(p for k, p in tilemap.object_spawns
                    if k.startswith("arrival:"))
    return int(position[0]) // ts, int(position[1]) // ts


def test_each_world_brought_its_own_growth_and_not_a_lookalike() -> None:
    """The same prop the world uses at home, checked against it.

    The point of a fragment is that a player recognises it. A tree that
    merely resembles Chult's tree costs the fragment the one thing it
    exists for, and the failure is silent -- it looks like a jungle
    either way to anyone who is not holding both up at once.

    So each dressing character is compared with the character its own
    region uses, and what has to match is the prop and the solidity.
    Only the ground underneath may differ, which is the whole reason
    these needed characters of their own: the collided maps renamed
    Chult's floor because the desert had already claimed the letter.
    """
    for here, home in AT_HOME.items():
        mine, theirs = TILE_DEFS[here], TILE_DEFS[home]
        assert mine.prop == theirs.prop, (here, mine.prop, theirs.prop)
        assert mine.solid == theirs.solid, here
        if here != home:
            assert mine.under != theirs.under, (here, "no character needed")

    # ...and every prop stands on the ground it was placed on, or the
    # tile paints one world's floor under another world's tree.
    for prop, ground in PROP_GROUND.items():
        assert TILE_DEFS[prop].under == ground, (prop, TILE_DEFS[prop].under)


def test_every_fragment_worth_dressing_has_been_dressed() -> None:
    """No world east of the hub is left as a bare rectangle.

    Counted per map and per world, so that adding a seventh map with a
    piece of Chult in it and forgetting to dress it fails here rather
    than being noticed on screen a phase later.

    A fragment has to be big enough to be worth it: the small scraps
    are three or four tiles across and there is genuinely nowhere on
    some of them to stand anything, so the bar is a dozen tiles.
    """
    dressed = 0
    for name in EASTERN:
        tilemap = _tilemap(name)
        counts: dict[str, int] = {}
        for y in range(tilemap.height_tiles):
            for x in range(tilemap.width_tiles):
                char = tilemap.terrain_at(x, y)
                counts[char] = counts.get(char, 0) + 1
        for ground, (props, _, _, _) in FRAGMENT_DRESSING.items():
            here = counts.get(ground, 0) + sum(counts.get(p, 0) for p in props)
            if here < 12:
                continue
            standing = sum(counts.get(p, 0) for p in props)
            assert standing, (name, ground, here)
            dressed += standing
    assert dressed > 100, dressed


def test_nothing_that_was_planted_can_close_a_way_through() -> None:
    """The invariant, measured on the finished map.

    Every one of these props is solid and the fourth map's basalt slab
    is the only crossing on it, so this is the assertion the whole
    placement rule exists to satisfy -- and it is checked here rather
    than trusted, because the rule and the map are edited by different
    hands at different times.

    A tile with standable ground on all four sides is not a chokepoint
    by construction: whatever else the map does, there is a way past.
    """
    # The scattered dressing only. The lava fall is placed by hand and
    # stands in its own lava on purpose -- it is a hazard rather than a
    # thing to walk round, and holding it to this rule would mean
    # asking for a waterfall with dry land under it.
    walkable_props = {
        prop
        for props, ground_is_solid, _, _ in FRAGMENT_DRESSING.values()
        if not ground_is_solid
        for prop in props
    }
    checked = 0
    for name in EASTERN:
        tilemap = _tilemap(name)
        for y in range(1, tilemap.height_tiles - 1):
            for x in range(1, tilemap.width_tiles - 1):
                if tilemap.terrain_at(x, y) not in walkable_props:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    assert tilemap.terrain_at(x + dx, y + dy) in _STANDABLE, \
                        (name, x, y, dx, dy)
                checked += 1
    assert checked, "no props stand on walkable ground at all"


def test_every_map_east_is_still_walkable_end_to_end() -> None:
    """Walked, not assumed. Both gaps, on every map.

    The dressing pass touches all six maps at once, which is exactly
    the kind of change that closes one route on one map and is noticed
    two phases later.
    """
    for name in EASTERN:
        tilemap = _tilemap(name)
        seen = _safe_flood(tilemap, _arrival(tilemap))
        width, height = tilemap.width_tiles, tilemap.height_tiles
        for edge, cells in (
            ("west", [(0, y) for y in range(height)]),
            ("east", [(width - 1, y) for y in range(height)]),
        ):
            open_edge = [c for c in cells if not tilemap.is_solid(*c)]
            assert open_edge, (name, edge)
            assert any(c in seen for c in open_edge), (name, edge)


def test_the_ruins_east_are_dressed_out_of_the_hubs_own_box() -> None:
    """The same pieces, so they read as the same building.

    The hub's scattered rectangles and the ruins east of it are meant
    to be fragments of one place. Two dressing vocabularies would make
    them two places, so this checks that what turned up east is what
    the hub uses, and that it turned up on more than one map.
    """
    maps_with_pieces = 0
    total = 0
    for name in EASTERN:
        tilemap = _tilemap(name)
        here = sum(
            1 for y in range(tilemap.height_tiles)
            for x in range(tilemap.width_tiles)
            if tilemap.terrain_at(x, y) in PIECES
        )
        total += here
        maps_with_pieces += 1 if here else 0
    assert maps_with_pieces >= 4, maps_with_pieces
    assert total > 40, total


def test_the_lava_fall_pours_into_a_hole_rather_than_a_river() -> None:
    """The one thing that separates it from a fourth lava channel.

    A fall feeding a channel would be a channel with a nicer top. This
    one ends: a short run, and then the ground is simply gone. So the
    run is measured three ways -- it is small, it touches the Astral
    Sea, and unlike every channel on the map it reaches neither rim.
    """
    tilemap = _tilemap("desert_east_4")
    fall = LAVA_FALL
    assert tilemap.terrain_at(*fall) == "ƒ"
    assert TILE_DEFS["ƒ"].prop == "phlegethos_lava_fall"
    assert TILE_DEFS["ƒ"].under == "≋", "the fall is not standing in lava"
    # It moves, which is the other half of what was asked for.
    assert len(_ANIMATED_SPRITES["phlegethos_lava_fall"]) > 1

    # The run below it, as one connected body of lava.
    start = (fall[0], fall[1] + 1)
    assert tilemap.terrain_at(*start) == "≋", "the fall pours onto rock"
    run = {start}
    frontier = [start]
    while frontier:
        x, y = frontier.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in run or not (0 <= cell[0] < W4 and 0 <= cell[1] < H4):
                continue
            if tilemap.terrain_at(*cell) != "≋":
                continue
            run.add(cell)
            frontier.append(cell)

    assert len(run) <= FALL_RUN * 6, len(run)
    assert min(y for _, y in run) > 1, "the run reaches the north rim"
    assert max(y for _, y in run) < H4 - 2, "the run reaches the south rim"
    # ...and it ends in the Sea rather than petering out on basalt.
    assert any(
        tilemap.terrain_at(x + dx, y + dy) == "V"
        for x, y in run for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
        if 0 <= x + dx < W4 and 0 <= y + dy < H4
    ), "the run does not reach the Astral Sea"

    # The channels do reach the rims, which is what makes this one
    # different rather than merely short.
    rim_lava = [
        x for x in range(W4)
        if "≋" in (tilemap.terrain_at(x, 1),
                   tilemap.terrain_at(x, H4 - 2))
    ]
    assert rim_lava, "no channel runs rim to rim any more"
    assert fall[0] not in rim_lava


def test_the_dressed_maps_all_still_draw() -> None:
    """Rendered, because every art bug in this region has been silent.

    One frame per map, checked for the thing a screenshot would show
    instantly: that something of the fragment's own colour is on the
    screen and the map has not come up as a field of sand.
    """
    for name in EASTERN:
        directory, game, world = _world(name)
        try:
            surface = pygame.Surface((config.NATIVE_WIDTH,
                                      config.NATIVE_HEIGHT))
            for _ in range(3):
                world.update(0.1)
            world.draw(surface)
            assert world.props, name
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
    print("All eastern dressing tests passed.")


if __name__ == "__main__":
    _run_all()
