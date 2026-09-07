"""The modern city's street furniture, and which city turns its lamps on.

The blocks were built and never furnished: every city map was a road, a
kerb, a pavement and a wall of building, and between those four things
nothing stood on the ground at all. Lamp posts, hydrants and stop signs
are the boring things that fix that, and all three are solid -- which is
the reason most of this file exists. A furnishing pass is exactly the
kind of change that closes a route while looking fine, so the placement
proves it did not rather than being looked at.

The other half is the light. The night city's lamps throw pools on the
pavement and the day city's do not, and that is the whole of what "the
lights are on" means here: the same post on the same tile, one sprite
with lit glass, and a field of additive pools that only the night maps
build.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.street_light import GLOW_RADIUS, StreetLightField
from src.systems.checkpoints import CHECKPOINTS
from src.world.tilemap import MARKER_DEFS, TILE_DEFS
from src.world.tileset_layout import MAP_TILESET

import sys
sys.path.insert(0, "tools")
from generate_city_map_common import (  # noqa: E402
    FIRE_HYDRANT, HYDRANTS_PER_MAP, KERB, LIGHT_SPACING, PAVEMENT,
    SIGNS_PER_MAP, STOP_SIGN, STREETLIGHT,
)


NIGHT_MAPS = tuple(
    name for name, sheet in MAP_TILESET.items() if sheet == "city"
)
DAY_MAPS = tuple(
    name for name, sheet in MAP_TILESET.items() if sheet == "city_day"
)
FURNITURE = (STREETLIGHT, FIRE_HYDRANT, STOP_SIGN)


def _rows(map_name: str) -> list[str]:
    text = (config.MAPS_DIR / f"{map_name}.txt").read_text(encoding="utf-8")
    return [line for line in text.splitlines() if not line.startswith(";")]


def _walkable(char: str) -> bool:
    marker = MARKER_DEFS.get(char)
    if marker is not None:
        return not TILE_DEFS[marker.under].solid
    tile = TILE_DEFS.get(char)
    return tile is not None and not tile.solid


def _reachable(rows: list[str]) -> set[tuple[int, int]]:
    height, width = len(rows), len(rows[0])
    start = next(
        (col, row) for row in range(height) for col in range(width)
        if _walkable(rows[row][col])
    )
    seen = {start}
    frontier = [start]
    while frontier:
        col, row = frontier.pop()
        for dcol, drow in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (col + dcol, row + drow)
            if cell in seen:
                continue
            if not (0 <= cell[0] < width and 0 <= cell[1] < height):
                continue
            if not _walkable(rows[cell[1]][cell[0]]):
                continue
            seen.add(cell)
            frontier.append(cell)
    return seen


def _placed(rows: list[str], char: str) -> list[tuple[int, int]]:
    return [(col, row) for row, line in enumerate(rows)
            for col, found in enumerate(line) if found == char]


def _game():
    directory = tempfile.TemporaryDirectory()
    return directory, Game(save_path=Path(directory.name) / "save.json")


def _load(game, map_name: str):
    checkpoint = next(
        (cp for cp in CHECKPOINTS
         if cp.map_name == map_name and cp.runtime_entry),
        next(cp for cp in CHECKPOINTS if cp.map_name == map_name),
    )
    for flag in checkpoint.required_flags:
        game.progress.enable(flag)
    return game.checkpoints.load_checkpoint(
        checkpoint.checkpoint_id, progress_flags=set(checkpoint.required_flags)
    )


# ----------------------------------------------------------------------
# Where it stands
# ----------------------------------------------------------------------
def test_every_street_has_lamps_and_a_hydrant_or_two() -> None:
    """Furnished, and sparsely: this is punctuation, not scenery.

    Counts rather than exact placements, because the placement is
    derived from each map's own kerbs and moving a road should be
    allowed to move a lamp.
    """
    for map_name in NIGHT_MAPS + DAY_MAPS:
        rows = _rows(map_name)
        lamps = _placed(rows, STREETLIGHT)
        hydrants = _placed(rows, FIRE_HYDRANT)
        signs = _placed(rows, STOP_SIGN)
        assert lamps, map_name
        assert len(hydrants) <= HYDRANTS_PER_MAP, (map_name, len(hydrants))
        assert len(signs) <= SIGNS_PER_MAP, (map_name, len(signs))
        # Not so many lamps that the pavement becomes fencing.
        assert len(lamps) <= 20, (map_name, len(lamps))

    # ...and the sparse two exist somewhere, which "some" has to mean.
    assert sum(len(_placed(_rows(name), FIRE_HYDRANT))
               for name in NIGHT_MAPS + DAY_MAPS) >= 12
    assert sum(len(_placed(_rows(name), STOP_SIGN))
               for name in NIGHT_MAPS + DAY_MAPS) >= 6


def test_it_all_stands_at_the_kerb() -> None:
    """Against the road, on what was plain pavement.

    Real pavements are furnished at their outer edge because whatever is
    behind the lamp post is the bit you walk down. Here that is not
    style, it is the safety rule: putting the solid thing against the
    kerb is what guarantees a lane behind it.
    """
    for map_name in NIGHT_MAPS + DAY_MAPS:
        rows = _rows(map_name)
        for char in FURNITURE:
            for col, row in _placed(rows, char):
                near = [
                    rows[row + drow][col + dcol]
                    for dcol, drow in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if 0 <= col + dcol < len(rows[0])
                    and 0 <= row + drow < len(rows)
                ]
                assert KERB in near, (map_name, char, col, row, near)
                assert PAVEMENT in near, (map_name, char, col, row, near)


def test_furnishing_the_street_never_closed_it() -> None:
    """The thing a pass like this breaks, checked rather than eyeballed.

    Each map is flooded as it ships and again with every piece of
    furniture lifted back to bare pavement. The two have to agree
    everywhere except on the tiles the furniture is standing on -- so a
    lamp post can never be the reason a corner became unreachable.
    """
    for map_name in NIGHT_MAPS + DAY_MAPS:
        rows = _rows(map_name)
        bare = [
            "".join(PAVEMENT if char in FURNITURE else char for char in line)
            for line in rows
        ]
        standing = {
            cell for char in FURNITURE for cell in _placed(rows, char)
        }
        assert standing, map_name
        assert _reachable(rows) == _reachable(bare) - standing, map_name


def test_both_sides_of_a_road_are_lit() -> None:
    """The bug that made this worth a test.

    Lamps space out along a kerb, and each side of a road is its own
    kerb. Measured as a flat distance between lamps instead, one on the
    north pavement suppressed everything within sixteen tiles -- the
    whole of the south pavement nine rows below it included -- and every
    street came back lit down one side only.
    """
    for map_name in NIGHT_MAPS:
        rows = _rows(map_name)
        lamps = _placed(rows, STREETLIGHT)
        # Which side of its kerb each lamp is on, as the direction from
        # the kerb to the lamp.
        sides = set()
        for col, row in lamps:
            for dcol, drow in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                near = (col - dcol, row - drow)
                if not (0 <= near[0] < len(rows[0])
                        and 0 <= near[1] < len(rows)):
                    continue
                if rows[near[1]][near[0]] == KERB:
                    sides.add((dcol, drow))
                    break
        assert len(sides) >= 2, (map_name, sorted(sides), len(lamps))
    assert LIGHT_SPACING >= 8


# ----------------------------------------------------------------------
# Which city turns them on
# ----------------------------------------------------------------------
def test_the_night_city_lights_them_and_the_day_city_does_not() -> None:
    """The same post on the same kind of tile; only the glass differs.

    Night is taken off which sheet the map draws with rather than off
    its name: the two cities are the same streets at different hours and
    the tileset is the one place that difference is already recorded.
    """
    directory, game = _game()
    try:
        for map_name in NIGHT_MAPS:
            world = _load(game, map_name)
            assert world.after_dark, map_name
            assert world.street_lights is not None, map_name
            lamps = [(col, row) for kind, col, row
                     in world.tilemap.prop_tiles if kind == "city_streetlight"]
            assert len(world.street_lights) == len(lamps), map_name
            lit = [prop for prop in world.props
                   if prop.kind == "city_streetlight_lit"]
            assert len(lit) == len(lamps), map_name

        for map_name in DAY_MAPS:
            world = _load(game, map_name)
            assert not world.after_dark, map_name
            assert world.street_lights is None, map_name
            # The posts are still there -- they are just not on.
            unlit = [prop for prop in world.props
                     if prop.kind == "city_streetlight"]
            assert unlit, map_name
            assert not [prop for prop in world.props
                        if prop.kind == "city_streetlight_lit"], map_name
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_light_is_added_to_the_street_and_not_taken_off_it() -> None:
    """Pools that only ever brighten, and only near a lamp.

    There is no darkening pass: the night city already draws with its
    own night sheet, and multiplying that down to light it back up is
    re-lighting a room that is already lit. What came out of trying it
    was a street darker everywhere except directly under the lamps,
    which reads as fog rather than as night.

    So every pixel either brightens or stays where it was, and the ones
    that brighten are the ones near a post.
    """
    directory, game = _game()
    try:
        world = _load(game, NIGHT_MAPS[0])
        lamp = world.street_lights.centres[0]
        world.camera.focus_on(*lamp)
        world.camera.update(0.0)

        surface = pygame.Surface((config.NATIVE_WIDTH, config.NATIVE_HEIGHT))
        world.draw(surface)
        # Sampled on a grid rather than read as an array: there is no
        # numpy here, and a fifth of the pixels says everything a whole
        # frame would.
        spots = [
            (x, y)
            for x in range(0, config.NATIVE_WIDTH, 3)
            for y in range(0, config.NATIVE_HEIGHT, 3)
        ]
        after = {spot: surface.get_at(spot)[:3] for spot in spots}

        field, world.street_lights = world.street_lights, None
        world.draw(surface)
        before = {spot: surface.get_at(spot)[:3] for spot in spots}
        world.street_lights = field

        brighter = 0
        for spot in spots:
            for lit, dark in zip(after[spot], before[spot]):
                assert lit >= dark, (spot, after[spot], before[spot])
            if after[spot] != before[spot]:
                brighter += 1
        assert brighter, "the lamps added nothing"

        # ...and what they added is under them. Anything more than a
        # radius away from every lamp is untouched.
        ox, oy = world.camera.offset
        for spot in spots:
            world_x, world_y = spot[0] + ox, spot[1] + oy
            near = min(
                max(abs(world_x - cx), abs(world_y - cy))
                for cx, cy in world.street_lights.centres
            )
            if near > GLOW_RADIUS + 2:
                assert after[spot] == before[spot], (spot, near)
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
    print("All city street-furniture tests passed.")


if __name__ == "__main__":
    _run_all()
