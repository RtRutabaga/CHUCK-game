"""The collided sheet, and where every row on it came from.

Phase 13's eastward traversal draws with one sheet that grows a row per
intruding world. The rule that keeps it honest is that no row is ever
drawn here: each is rendered by the generator belonging to the place it
came from, and this suite checks the finished pixels against that
place's own sheet.

That check lives on its own rather than in any one map's tests, because
it is a property of the sheet and every map east of the hub depends on
it. Adding a world means adding one line to PROVENANCE below; if the
line is forgotten the suite fails, which is the point -- an unattributed
row is one somebody has drawn from memory.

Why it matters more than it looks: the failure mode is not a crash and
not even an obviously wrong picture. It is a fragment of the modern
city that is a *slightly* different grey from the modern city, which
nobody notices while the sequence is being built and which quietly
costs the fragment the only thing it is for -- being recognised.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.world import collision
from src.world.tileset_layout import (
    CHULT, CITY, COLLIDED, DESERT, FEYWILD, PHLEGETHOS, SEWER, TILE_PX,
)


# Every row on the collided sheet, and the tileset that owns it.
PROVENANCE = {
    "sand": DESERT,
    "sand_ripple": DESERT,
    "dune": DESERT,
    "desert_rock": DESERT,
    "ruin_stone": DESERT,
    "ruin_floor": DESERT,
    "desert_scrub": DESERT,
    "city_road": CITY,
    "city_road_line_h": CITY,
    "jungle_ground": CHULT,
    "dense_jungle": CHULT,
    "jungle_stream": CHULT,
    "fey_ground": FEYWILD,
    "fey_dense": FEYWILD,
    "fey_pollen": FEYWILD,
    "fey_glow_pool": FEYWILD,
    "basalt": PHLEGETHOS,
    "cliff": PHLEGETHOS,
    "lava": PHLEGETHOS,
    # The Sea is on every sheet in the game and identical on all of
    # them; the sewer's is as good a reference as any.
    "astral_void": SEWER,
}


def _row(sheet, tileset, name) -> list:
    index = [n for n, _, _ in tileset.order].index(name)
    variants, frames = tileset.info()[name]
    return [
        sheet.get_at((x, index * TILE_PX + y))[:3]
        for y in range(TILE_PX)
        for x in range(variants * frames * TILE_PX)
    ]


def test_every_row_is_accounted_for() -> None:
    """No row on the sheet without a world behind it."""
    rows = [name for name, _, _ in COLLIDED.order]
    assert len(rows) == len(set(rows)), rows
    assert set(rows) == set(PROVENANCE), set(rows) ^ set(PROVENANCE)


def test_every_row_is_its_own_worlds_row() -> None:
    """Pixel for pixel, against the sheet it belongs to."""
    pygame.init()
    sheets: dict[int, pygame.Surface] = {}

    def sheet_for(tileset):
        key = id(tileset)
        if key not in sheets:
            sheets[key] = pygame.image.load(
                str(config.ASSETS_DIR / "tilesets" / tileset.sheet))
        return sheets[key]

    collided = sheet_for(COLLIDED)
    for name, source in PROVENANCE.items():
        # The same number of variants and frames, first: a row rendered
        # with fewer would be the same art shown differently, which is
        # the drift this whole arrangement exists to prevent.
        assert COLLIDED.info()[name] == source.info()[name], name
        assert _row(collided, COLLIDED, name) == \
            _row(sheet_for(source), source, name), name


def test_the_sheet_is_the_size_its_layout_says() -> None:
    pygame.init()
    sheet = pygame.image.load(
        str(config.ASSETS_DIR / "tilesets" / COLLIDED.sheet))
    assert sheet.get_width() == COLLIDED.cols * TILE_PX
    assert sheet.get_height() == COLLIDED.rows * TILE_PX


def test_a_character_means_the_same_thing_it_meant_at_home() -> None:
    """Where a character could be kept, it was; where not, the art was.

    The desert claimed "." and "#" before Chult's fragment arrived, and
    a tileset can give a character only one meaning -- so the jungle
    took new letters and kept its pictures. The city's road kept both,
    because nothing had claimed "=" or the lane marking.
    """
    assert COLLIDED.char_to_terrain["="] == CITY.char_to_terrain["="]
    assert COLLIDED.char_to_terrain["≡"] == CITY.char_to_terrain["≡"]
    assert COLLIDED.char_to_terrain["ᛗ"] == CHULT.char_to_terrain["."]
    assert COLLIDED.char_to_terrain["ᚷ"] == CHULT.char_to_terrain["#"]
    assert COLLIDED.char_to_terrain["ᚺ"] == CHULT.char_to_terrain["≈"]
    assert COLLIDED.char_to_terrain["ᛟ"] == FEYWILD.char_to_terrain["."]
    assert COLLIDED.char_to_terrain["ᛇ"] == FEYWILD.char_to_terrain["#"]
    # The Feywild's own oddities kept their letters; nothing had them.
    for char in ("☼", "ᛞ"):
        assert COLLIDED.char_to_terrain[char] == FEYWILD.char_to_terrain[char]
    # Hell kept all of its, including the one that matters: lava has
    # been lethal since Phlegethos and is lethal here for free.
    for char in ("·", "█", "≋"):
        assert (COLLIDED.char_to_terrain[char]
                == PHLEGETHOS.char_to_terrain[char])
    assert "≋" in collision.FALL_HAZARD_TERRAIN
    # ...and the desert kept its own, so the ground under everything
    # still reads the way the opening region taught it.
    for char in (".", ",", "⟁", "#", "⌗", "⌖", "⍟", "V"):
        assert COLLIDED.char_to_terrain[char] == DESERT.char_to_terrain[char]


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
    print("All collided tileset tests passed.")


if __name__ == "__main__":
    _run_all()
