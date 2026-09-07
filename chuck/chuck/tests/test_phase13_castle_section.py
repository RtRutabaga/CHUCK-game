"""The collided desert's castle, finished, and whose it is.

The medieval fragment shipped as flat coursed ashlar: correct stone, and
unmistakably a boundary rather than a building. Out here that matters
more than it would anywhere else -- this is the one world in the
collision Chuck never visited, so there is no map of it to remember and
the walls are the whole of what anybody ever learns about the place.

A wall becomes a castle wall the moment it is notched and has a tower on
the corner, and it belongs to somebody the moment there is cloth on it.
So: crenellation along the curtain, drum towers on the corners and the
stumps, and banners on the faces that show.

The rule underneath all of it, and the reason it could be run over maps
whose geometry other suites measure to the tile: it is collision
neutral. Merlons and towers are converted *from* wall, so they are solid
tiles standing exactly where solid tiles already stood, and banners are
non-solid and go on ground that was already open. Nothing the pass does
can close a route, and that is asserted here rather than assumed.
"""

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.entities.prop import _ANIMATED_SPRITES
from src.world.tilemap import TILE_DEFS, TileMap

import sys
sys.path.insert(0, "tools")
from generate_collided_common import (  # noqa: E402
    BANNER_ON_SAND, BANNER_ON_STONE, BANNER_SPACING, CASTLE_WALLS,
    COURTYARD_MERLON, COURTYARD_STONE, COURTYARD_TOWER, COURTYARD_WALL,
    dress_castle,
)


# Every map the castle fragment landed on. East 6 has flagstones and no
# wall at all, which is why it is not here: there is nothing to
# crenellate, and inventing a wall for it would put solid tiles on a map
# whose routes are measured elsewhere.
CASTLE_MAPS = ("desert_east_5", "desert_east_7", "desert_east_8")
BANNERS = (BANNER_ON_STONE, BANNER_ON_SAND)


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
        banners = sum(_count(rows, char) for char in BANNERS)
        assert merlons > 0, map_name
        assert towers > 0, map_name
        assert banners > 0, map_name
        # Crenellation is the bulk of it and towers are the punctuation.
        # The other way round is a field of towers, which is what the
        # first pass produced on the two island maps: every clump of
        # wall there is two tiles thick, and calling anything thick a
        # tower made forty of them in a heap.
        assert towers < merlons, (map_name, towers, merlons)


def test_a_banner_hangs_in_front_of_a_wall_and_over_open_ground() -> None:
    """Pinned to stone, hanging onto floor -- not floating in a courtyard.

    Props anchor to the bottom of their tile and draw upward, so a
    banner authored on the wall would rise off the battlements like a
    flag on a pole. It goes on the ground tile in front instead, which
    is why there has to be a wall directly behind every one of them and
    open ground directly under it.
    """
    for map_name in CASTLE_MAPS:
        rows = _rows(map_name)
        for col, row in _cells(rows, BANNERS):
            assert row > 0, (map_name, col, row)
            behind = rows[row - 1][col]
            assert behind in CASTLE_WALLS, (map_name, col, row, behind)
            # ...and it is not itself in the way.
            assert not TILE_DEFS[rows[row][col]].solid, (map_name, col, row)
            # The ground it hangs over says which character it is: the
            # courtyard's flagstones inside, the desert's sand out.
            wanted = (BANNER_ON_STONE if TILE_DEFS[rows[row][col]].under
                      == COURTYARD_STONE else BANNER_ON_SAND)
            assert rows[row][col] == wanted, (map_name, col, row)


def test_the_banners_are_an_announcement_rather_than_bunting() -> None:
    """Spaced out, and few. There are four on the whole south wall."""
    for map_name in CASTLE_MAPS:
        hung = sorted(_cells(_rows(map_name), BANNERS))
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
    for char in BANNERS:
        assert TILE_DEFS[char].prop == "castle_banner"


# ----------------------------------------------------------------------
# ...and what it did not do
# ----------------------------------------------------------------------
def test_finishing_the_castle_moved_nobody() -> None:
    """The claim the whole pass rests on, measured rather than trusted.

    Every one of these maps has its geometry measured by another suite --
    east 8's islands, east 7's nine worlds, and the arena the horde has
    to cross. Running a furnishing pass over them is only safe because
    it converts solid stone into different solid stone and puts cloth on
    ground that was already open, so the set of tiles anybody can stand
    on comes out identical.
    """
    import tempfile

    for map_name in CASTLE_MAPS:
        shipped = TileMap(config.MAPS_DIR / f"{map_name}.txt")
        before = {
            (col, row)
            for row in range(shipped.height_tiles)
            for col in range(shipped.width_tiles)
            if not shipped.is_solid(col, row)
        }

        # The same map with the castle taken back off it, dressed again,
        # and read through the real tilemap -- which is the only thing
        # that knows how a marker resolves to the ground under it.
        bare = [
            "".join(
                COURTYARD_WALL if char in (COURTYARD_MERLON, COURTYARD_TOWER)
                else (COURTYARD_STONE if char == BANNER_ON_STONE
                      else ("." if char == BANNER_ON_SAND else char))
                for char in line
            )
            for line in _rows(map_name)
        ]
        undressed = [list(line) for line in bare]
        counts = dress_castle(undressed, seed=0)
        assert counts[COURTYARD_MERLON] > 0, map_name

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bare.txt"
            path.write_text("\n".join(bare) + "\n", encoding="utf-8")
            plain = TileMap(path)
            after = {
                (col, row)
                for row in range(plain.height_tiles)
                for col in range(plain.width_tiles)
                if not plain.is_solid(col, row)
            }
        assert before == after, (map_name,
                                 sorted(before ^ after)[:8])


def test_it_is_the_same_castle_every_time() -> None:
    """Deterministic, like everything else scattered in this project.

    A castle that crenellates itself differently per run is one nobody
    can tell is working -- including whoever has to decide whether the
    last change to it was an improvement.
    """
    for map_name in CASTLE_MAPS:
        rows = [
            "".join(
                COURTYARD_WALL if char in (COURTYARD_MERLON, COURTYARD_TOWER)
                else (COURTYARD_STONE if char == BANNER_ON_STONE
                      else ("." if char == BANNER_ON_SAND else char))
                for char in line
            )
            for line in _rows(map_name)
        ]

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
    assert counts == {COURTYARD_MERLON: 0, COURTYARD_TOWER: 0, "banner": 0}
    assert "".join(grid[2]) == "..." + COURTYARD_STONE + "......"

    rows = _rows("desert_east_6")
    assert _count(rows, COURTYARD_STONE) > 0
    assert _count(rows, COURTYARD_WALL) == 0
    for char in (COURTYARD_MERLON, COURTYARD_TOWER, *BANNERS):
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
