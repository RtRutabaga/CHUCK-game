"""Every doorway is one arch, and every arch sits on its path.

Two things kept going wrong by hand:

*Arches off their path.* The temple's entrance hall has a processional
four tiles wide and doors three tiles wide, so its north door sat
against the aisle's left edge and its south door against the right.

*Two doorways where there should be one.* A threshold tile outside the
arch's art is a bare dark square in the wall, and next to a real door it
reads as a second, rat-sized one.

Both are checked here against the art itself: a north/south arch's
opening is centred on its own tile, and an east-west arch's opening is
centred one row above its tile -- which is why every side door in the
game sits at the bottom of a three-row threshold with the path running
through the middle row.
"""

from collections import deque
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from PIL import Image

from src.core import config
from src.world.tilemap import TileMap

ARCHES = {"⌂": "ns", "⌄": "ns", "£": "ns", "«": "ew", "»": "ew"}
THRESHOLD = ("∇", "Δ")
PATH = "≡"
# How far from a doorway its path is allowed to start.
REACH = 4
TS = config.TILE_SIZE


def _maps():
    for path in sorted(config.MAPS_DIR.glob("*.txt")):
        tilemap = TileMap(path)
        arches = [
            (col, row, tilemap.terrain_at(col, row))
            for row in range(tilemap.height_tiles)
            for col in range(tilemap.width_tiles)
            if tilemap.terrain_at(col, row) in ARCHES
        ]
        if arches:
            yield path.stem, tilemap, arches


def _run(tilemap, fixed: int, start: int, vertical: bool):
    """The unbroken run of path tiles through one row or column."""
    def path_at(along):
        col, row = (fixed, along) if vertical else (along, fixed)
        if not (0 <= col < tilemap.width_tiles
                and 0 <= row < tilemap.height_tiles):
            return False
        return tilemap.terrain_at(col, row) == PATH

    if not path_at(start):
        return None
    low = high = start
    while path_at(low - 1):
        low -= 1
    while path_at(high + 1):
        high += 1
    return (low + high) / 2


def test_the_art_puts_the_opening_where_the_rule_says() -> None:
    """The premise the alignment rule rests on, read off the sprites."""
    for name, axis in (("temple_arch_ns", "ns"), ("temple_arch_ew", "ew"),
                       ("temple_arch_ew_east", "ew"),
                       ("phlegethos_arch_ns", "ns"),
                       ("phlegethos_arch_ew", "ew"),
                       ("phlegethos_arch_ew_east", "ew")):
        art = Image.open(
            config.SPRITES_DIR / "objects" / f"{name}.png").convert("RGBA")
        width, height = art.size
        dark = [(x, y) for y in range(height) for x in range(width)
                if art.getpixel((x, y))[3] > 200
                and sum(art.getpixel((x, y))[:3]) < 70]
        assert dark, name
        centre_x = (min(x for x, _ in dark) + max(x for x, _ in dark)) / 2
        centre_y = (min(y for _, y in dark) + max(y for _, y in dark)) / 2
        if axis == "ns":
            # Centred on the tile it stands on, and in that tile's row,
            # so a three-wide path centred on its column lines up.
            assert abs(centre_x - width / 2) <= 1.5, (name, centre_x)
            assert height - centre_y <= TS + 2, (name, centre_y)
        else:
            # A side door is cut into the wall it faces, so its opening
            # leans that way rather than sitting centred in the art.
            # What matters is the row: one above the tile it stands on.
            assert TS < height - centre_y <= TS * 2, (name, centre_y)


def test_every_arch_is_centred_on_its_path() -> None:
    for name, tilemap, arches in _maps():
        for col, row, char in arches:
            if ARCHES[char] == "ns":
                found = next(
                    (r for step in range(1, REACH + 1) for r in
                     (row + step, row - step)
                     if 0 <= r < tilemap.height_tiles
                     and tilemap.terrain_at(col, r) == PATH), None)
                if found is None:
                    continue            # a doorway with no paved approach
                centre = _run(tilemap, found, col, vertical=False)
                assert centre == col, (name, char, (col, row), centre)
            else:
                # The opening is one row above the arch's own tile.
                opening = row - 1
                found = next(
                    (c for step in range(1, REACH + 1) for c in
                     (col + step, col - step)
                     if 0 <= c < tilemap.width_tiles
                     and tilemap.terrain_at(c, opening) == PATH), None)
                if found is None:
                    continue
                centre = _run(tilemap, found, opening, vertical=True)
                assert centre == opening, (name, char, (col, row), centre)


def test_no_doorway_has_a_second_little_doorway_beside_it() -> None:
    """Threshold tiles the arch's art does not cover.

    Allowed in a run -- the temple's north approach is a long dark
    corridor of them, and reads as one -- but a stray one or two beside
    a gate is a small door in the wall with nothing over it.
    """
    for name, tilemap, arches in _maps():
        covered = {
            (col + dx, row + dy)
            for col, row, _char in arches
            for dx in (-1, 0, 1) for dy in (-2, -1, 0)
        }
        loose = {
            (col, row)
            for row in range(tilemap.height_tiles)
            for col in range(tilemap.width_tiles)
            if tilemap.terrain_at(col, row) in THRESHOLD
        } - covered
        seen: set[tuple[int, int]] = set()
        for cell in sorted(loose):
            if cell in seen:
                continue
            run = {cell}
            seen.add(cell)
            frontier = deque([cell])
            while frontier:
                col, row = frontier.popleft()
                for step in ((col + 1, row), (col - 1, row),
                             (col, row + 1), (col, row - 1)):
                    if step in loose and step not in seen:
                        seen.add(step)
                        run.add(step)
                        frontier.append(step)
            assert len(run) > 2, (name, sorted(run))


def test_a_side_doors_reveal_is_on_the_far_side_of_its_passage() -> None:
    """The arch is handed, and its hand follows the wall it stands in.

    What you see through a side door is the thickness of the wall --
    the reveal -- and that is on the FAR side of the passage: to the
    west of a door that leads west, to the east of one that leads east.
    Both used to draw the same way round, so every east door had its
    reveal on the near side, which reads as a doorway cut backwards.

    Which way a door leads is taken from the map rather than from the
    character on it: a side door in the western half of a hall is the
    hall's west door, and vice versa. A future door that disagrees with
    its own art fails here.
    """
    from PIL import ImageChops

    west = Image.open(
        config.SPRITES_DIR / "objects" / "temple_arch_ew.png").convert("RGBA")
    east = Image.open(
        config.SPRITES_DIR / "objects"
        / "temple_arch_ew_east.png").convert("RGBA")
    assert not ImageChops.difference(
        east, west.transpose(Image.FLIP_LEFT_RIGHT)).getbbox()

    from src.world.tilemap import TILE_DEFS

    found = 0
    for name, tilemap, arches in _maps():
        for col, row, char in arches:
            if ARCHES[char] != "ew":
                continue
            found += 1
            leads_east = col > tilemap.width_tiles / 2
            kind = TILE_DEFS[char].prop
            assert kind.endswith("_east") == leads_east, (
                name, char, (col, row), kind)
    assert found >= 8, found
