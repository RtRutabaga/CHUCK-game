"""The collided desert's castle, finished, and whose it is.

The medieval fragment shipped as flat coursed ashlar: correct stone, and
unmistakably a boundary rather than a building. Out here that matters
more than it would anywhere else -- this is the one world in the
collision Chuck never visited, so there is no map of it to remember and
the walls are the whole of what anybody ever learns about the place.

A wall becomes a castle wall the moment it is notched and has a tower on
the corner, and it belongs to somebody the moment there is cloth on it.
So: crenellation along the curtain, drum towers on the corners and the
stumps, turrets standing on the corners the curtain turns around, and
banners on the faces that show.

Two of those add stone rather than swapping it, and that is the thing
this file exists to police. A turret or a buttress that shuts a gate or
strands a knight would be a route closed by a furnishing pass, on maps
whose geometry three other suites measure to the tile -- so the pass
floods the map after every block it writes and takes back the ones that
cut something off. That guard is tested here on the case it exists for,
and the shipped maps are checked for the failure it prevents.
"""

import os
from collections import deque

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.entities.prop import _ANIMATED_SPRITES, _SPRITES
from src.world.tilemap import MARKER_DEFS, TILE_DEFS

import sys
sys.path.insert(0, "tools")
from generate_collided_common import (  # noqa: E402
    BANNER_ON_WALL, BANNER_SPACING, CASTLE_TURRET, CASTLE_WALLS,
    COURTYARD_MERLON, COURTYARD_STONE, COURTYARD_TOWER, COURTYARD_WALL,
    dress_castle,
)


# Every map the castle fragment landed on. East 6 has flagstones and no
# wall at all, which is why it is not here: there is nothing to
# crenellate, and inventing a wall for it would put solid tiles on a map
# whose routes are measured elsewhere.
CASTLE_MAPS = ("desert_east_5", "desert_east_7", "desert_east_8")
# The only one with a courtyard whose curtain closes, which is the only
# shape a corner turret can stand on.
TURRETED = "desert_east_5"


def _rows(map_name: str) -> list[str]:
    text = (config.MAPS_DIR / f"{map_name}.txt").read_text(encoding="utf-8")
    return [line for line in text.splitlines() if not line.startswith(";")]


def _count(rows: list[str], char: str) -> int:
    return sum(line.count(char) for line in rows)


def _cells(rows: list[str], chars) -> set[tuple[int, int]]:
    return {
        (col, row)
        for row, line in enumerate(rows)
        for col, found in enumerate(line) if found in chars
    }


def _open(rows: list[str]) -> set[tuple[int, int]]:
    """Every tile nothing solid is standing on, markers resolved."""
    found = set()
    for row, line in enumerate(rows):
        for col, char in enumerate(line):
            marker = MARKER_DEFS.get(char)
            if not TILE_DEFS[marker.under if marker else char].solid:
                found.add((col, row))
    return found


def _regions(open_cells: set[tuple[int, int]]) -> list[set]:
    """The open ground, split into the pieces that cannot reach each other."""
    unseen, out = set(open_cells), []
    while unseen:
        start = next(iter(unseen))
        seen, frontier = {start}, deque([start])
        while frontier:
            col, row = frontier.popleft()
            for spot in ((col + 1, row), (col - 1, row),
                         (col, row + 1), (col, row - 1)):
                if spot in open_cells and spot not in seen:
                    seen.add(spot)
                    frontier.append(spot)
        unseen -= seen
        out.append(seen)
    return out


def _stripped(map_name: str) -> list[str]:
    """The map with the castle taken back off it, ready to dress again."""
    plain = {
        COURTYARD_MERLON: COURTYARD_WALL,
        COURTYARD_TOWER: COURTYARD_WALL,
        CASTLE_TURRET: COURTYARD_WALL,
        BANNER_ON_WALL: COURTYARD_WALL,
    }
    return ["".join(plain.get(char, char) for char in line)
            for line in _rows(map_name)]


# ----------------------------------------------------------------------
# What is standing there
# ----------------------------------------------------------------------
def test_the_walls_are_notched_and_towered_and_flying_colours() -> None:
    """All three, on every map that has a castle on it.

    A run of ashlar and a garden wall are the same object until one of
    them is crenellated. The tower is what a corner is for, and the
    banner is the only thing in the whole fragment with a colour in it.
    """
    for map_name in CASTLE_MAPS:
        rows = _rows(map_name)
        merlons = _count(rows, COURTYARD_MERLON)
        towers = _count(rows, COURTYARD_TOWER)
        banners = _count(rows, BANNER_ON_WALL)
        assert merlons > 0, map_name
        assert towers > 0, map_name
        assert banners > 0, map_name
        # Crenellation is the bulk of it and towers are the punctuation.
        # The other way round is a field of towers, which is what the
        # first pass produced on the two island maps: every clump of
        # wall there is two tiles thick, and calling anything thick a
        # tower made forty of them in a heap.
        assert towers < merlons, (map_name, towers, merlons)


def test_the_corners_are_the_tallest_thing_on_the_map() -> None:
    """A turret on every corner the courtyard's curtain turns around.

    A corner tower exists because a corner is where a castle wants
    height, and at one tile each the corners read as a slightly
    different piece of wall. The turret is an object rather than a
    tile: three tiles of stone with a slate cone on it, standing on the
    middle of its own block and drawing up over all of it.
    """
    rows = _rows(TURRETED)
    turrets = _cells(rows, {CASTLE_TURRET})
    assert len(turrets) == 4, turrets      # one per corner, and no more
    assert TILE_DEFS[CASTLE_TURRET].solid
    assert TILE_DEFS[CASTLE_TURRET].under == COURTYARD_TOWER
    for col, row in turrets:
        block = [rows[row + drow][col + dcol]
                 for dcol in (-1, 0, 1) for drow in (-2, -1, 0)]
        # The tile it stands on and the corner above it are always
        # stone -- without those two there is nothing to stand on and
        # no turret gets built.
        assert rows[row][col] == CASTLE_TURRET, (col, row)
        assert rows[row - 1][col] in CASTLE_WALLS, (col, row)
        # The rest of the block is stone wherever it can be. This
        # courtyard's south-west corner stands on the lip of a chasm,
        # and refusing to build a turret that cannot have all nine
        # tiles left one corner of a four-cornered castle bare; the
        # block is clipped there and the sprite overhangs the drop,
        # which is what a tower on a cliff edge does anyway.
        standing = sum(1 for spot in block if spot in CASTLE_WALLS)
        assert standing >= 6, ((col, row), block)
    # Turrets are three tiles across, so two of them any closer than
    # that would be one lumpy building.
    spread = sorted(turrets)
    for index, (col, row) in enumerate(spread):
        for other_col, other_row in spread[index + 1:]:
            assert max(abs(col - other_col), abs(row - other_row)) >= 3

    sprite = config.SPRITES_DIR / _SPRITES[CASTLE_TURRET_PROP]
    assert sprite.is_file(), sprite


CASTLE_TURRET_PROP = "castle_turret"


def test_a_banner_hangs_on_the_wall_and_the_wall_is_widened_for_it() -> None:
    """Cloth on stone, with stone under all of it.

    A banner is two tiles of sprite drawn upward from the bottom of the
    tile it stands on. Hung on the open ground in front of a one-tile
    curtain -- which is where these started -- two thirds of it came
    down past the bottom of the wall and lay on the courtyard floor, a
    banner as tall as the building it was on. So the wall grows a
    buttress under every one of them: three tiles wide and one deep, on
    the face that shows, with the banner on the middle of it.
    """
    for map_name in CASTLE_MAPS:
        rows = _rows(map_name)
        for col, row in _cells(rows, {BANNER_ON_WALL}):
            # The curtain it belongs to is directly behind it...
            assert row > 0, (map_name, col, row)
            assert rows[row - 1][col] in CASTLE_WALLS, (map_name, col, row)
            # ...the buttress carries it either side...
            assert rows[row][col - 1] in CASTLE_WALLS, (map_name, col, row)
            assert rows[row][col + 1] in CASTLE_WALLS, (map_name, col, row)
            # ...and the cloth reaches the top of the curtain behind it,
            # which is the whole reason the buttress is there.
            assert TILE_DEFS[BANNER_ON_WALL].under == COURTYARD_WALL
            assert TILE_DEFS[BANNER_ON_WALL].solid


def test_the_banners_are_an_announcement_rather_than_bunting() -> None:
    """Spaced out, and few. There are three on the whole south wall."""
    for map_name in CASTLE_MAPS:
        hung = sorted(_cells(_rows(map_name), {BANNER_ON_WALL}))
        for index, (col, row) in enumerate(hung):
            for other_col, other_row in hung[index + 1:]:
                apart = max(abs(col - other_col), abs(row - other_row))
                assert apart >= BANNER_SPACING, (map_name, (col, row),
                                                 (other_col, other_row))


def test_the_cloth_moves_and_does_not_snap() -> None:
    """Four frames of a lift, on the shared animated-prop path.

    Nothing else on these maps moves in a wind -- the fires are out and
    the snow falls straight down -- so a banner flapping would be the
    one thing on screen with weather of its own.
    """
    frames = _ANIMATED_SPRITES["castle_banner"]
    assert len(frames) == 4, frames
    for path in frames:
        assert (config.ASSETS_DIR / "sprites" / path).is_file(), path
    assert TILE_DEFS[BANNER_ON_WALL].prop == "castle_banner"
    # The turret does not move. It is masonry.
    assert CASTLE_TURRET_PROP not in _ANIMATED_SPRITES
    assert TILE_DEFS[CASTLE_TURRET].prop == CASTLE_TURRET_PROP


# ----------------------------------------------------------------------
# ...and what it did not do
# ----------------------------------------------------------------------
def test_a_buttress_that_would_shut_a_gate_is_not_built() -> None:
    """The guard, on the case it exists for.

    Crenellation and drum towers are safe however they land: they are
    solid tiles standing exactly where solid tiles already stood. The
    turrets and the banner buttresses are not, because they add stone,
    and a gate on these maps is a hole in a wall that looks exactly
    like the floor either side of it -- so there is no reading of the
    characters that tells a buttress it is about to plug one.

    What tells it is flooding the map after it writes and taking the
    block back off if anything stopped reaching anything. Here is a
    wall whose only gate has a buttress-sized hole under it, and the
    pass has to come away empty.
    """
    rock, wall = "#", COURTYARD_WALL
    shut = [
        list(rock * 7),
        list(rock + "....." + rock),
        list(rock + wall * 2 + "." + wall * 2 + rock),
        list(rock + "....." + rock),
        list(rock + "....." + rock),
        list(rock * 7),
    ]
    counts = dress_castle([row[:] for row in shut], seed=0)
    assert counts["banner"] == 0, counts

    grid = [row[:] for row in shut]
    dress_castle(grid, seed=0)
    assert grid[3][3] == ".", "the gate has been plugged"
    assert len(_regions(_open(["".join(row) for row in grid]))) == 1

    # ...and the same wall with room beside the gate does get its
    # banner, so what is being tested is the guard and not a pass that
    # never builds anything.
    roomy = [
        list(rock * 13),
        list(rock + "..........." + rock),
        list(rock + wall * 5 + "." + wall * 5 + rock),
        list(rock + "..........." + rock),
        list(rock + "..........." + rock),
        list(rock * 13),
    ]
    counts = dress_castle(roomy, seed=0)
    assert counts["banner"] >= 1, counts
    assert roomy[3][6] == "."
    assert len(_regions(_open(["".join(row) for row in roomy]))) == 1


def test_nothing_got_walled_into_a_pocket() -> None:
    """No stranded ground on any map the castle was built on.

    The failure a pass that adds stone can produce and nobody notices
    is a couple of tiles left open with a wall all the way round them.
    East 7 ships three sealed rooms of its own, from three different
    worlds, and the smallest of those is thirty-nine tiles -- so
    anything smaller than that would be new, and would be a buttress
    or a turret having closed the last way out of somewhere.
    """
    for map_name in CASTLE_MAPS:
        regions = _regions(_open(_rows(map_name)))
        assert regions, map_name
        assert min(len(region) for region in regions) >= 20, \
            (map_name, sorted(len(region) for region in regions))


def test_it_is_the_same_castle_every_time() -> None:
    """Deterministic, like everything else scattered in this project.

    A castle that crenellates itself differently per run is one nobody
    can tell is working -- including whoever has to decide whether the
    last change to it was an improvement.
    """
    for map_name in CASTLE_MAPS:
        rows = _stripped(map_name)

        def run():
            grid = [list(line) for line in rows]
            dress_castle(grid, seed=5)
            return ["".join(line) for line in grid]

        assert run() == run(), map_name


def test_a_map_with_no_wall_gets_no_castle() -> None:
    """Nothing is invented. Crenellation needs something to crenellate.

    East 6 has flagstones from the same world and not one tile of wall,
    and the honest answer there is to leave it alone -- a section of
    castle conjured onto it would be solid stone appearing on a map
    whose routes are measured somewhere else.
    """
    grid = [list("..........") for _ in range(6)]
    grid[2][3] = COURTYARD_STONE
    counts = dress_castle(grid, seed=1)
    assert counts == {COURTYARD_MERLON: 0, COURTYARD_TOWER: 0,
                      CASTLE_TURRET: 0, "banner": 0}
    assert "".join(grid[2]) == "..." + COURTYARD_STONE + "......"

    rows = _rows("desert_east_6")
    assert _count(rows, COURTYARD_STONE) > 0
    assert _count(rows, COURTYARD_WALL) == 0
    for char in (COURTYARD_MERLON, COURTYARD_TOWER, CASTLE_TURRET,
                 BANNER_ON_WALL):
        assert _count(rows, char) == 0, char


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
    print("All castle-section tests passed.")


if __name__ == "__main__":
    _run_all()


def test_no_banner_is_drawn_into_a_turret() -> None:
    """Cloth beside a drum tower, not behind its base.

    A banner is 26 pixels wide on a 16-pixel tile and a turret is 48,
    so a banner on the tile next to a turret has its top corner drawn
    under the turret's stonework -- it reads as hanging off the end of
    the wall rather than on it. One clear tile between them fixes it,
    which is all the width either sprite needs.
    """
    ts = config.TILE_SIZE

    def box(kind, col, row):
        sprite = _SPRITES[kind]
        if isinstance(sprite, tuple):
            sprite = sprite[0]       # the variants are all one size
        width, height = pygame.image.load(
            config.SPRITES_DIR / sprite).get_size()
        return pygame.Rect(col * ts + ts // 2 - width // 2,
                           (row + 1) * ts - height, width, height)

    for map_name in CASTLE_MAPS:
        rows = _rows(map_name)
        turrets = [box("castle_turret", col, row)
                   for col, row in _cells(rows, {CASTLE_TURRET})]
        for col, row in _cells(rows, {BANNER_ON_WALL}):
            banner = box("castle_banner", col, row)
            for turret in turrets:
                overlap = banner.clip(turret)
                assert overlap.width < 5 or overlap.height < 5, \
                    (map_name, col, row, overlap)
