"""Phase 9 --- the Feywild's vegetation dressing.

The region's dense growth was reading as flat blocks, so Chult's rounded
tree and shrub silhouettes were reused with a subtle violet sheen, plus
one deliberately ordinary oak so the wood never becomes visual noise.

Every piece stands ON dense vegetation that was already solid, so this is
purely a look pass: no route, jump or hazard may change because of it.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from collections import Counter

from src.core import config
from src.entities.prop import _SPRITES
from src.world.tilemap import TILE_DEFS, TileMap

FEYWILD_MAPS = (
    "feywild_riverbank", "feywild_blooming_path", "feywild_pollen_orchard",
    "feywild_rootways", "feywild_tea_table", "feywild_needle_garden",
)
VEGETATION = {
    "ŧ": "feywild_grove_tree",
    "Ŧ": "feywild_shrub",
    "Ɓ": "feywild_oak",
}


def test_vegetation_stands_on_dense_growth_and_never_opens_a_route() -> None:
    """The safety property: each new piece is solid and declares the
    already-solid dense vegetation as its under-terrain, so replacing a
    dense tile with one cannot change where Chuck may walk."""
    assert TILE_DEFS["#"].solid
    for char, kind in VEGETATION.items():
        tile = TILE_DEFS[char]
        assert tile.solid, char
        assert tile.under == "#", char
        assert tile.prop == kind, char
    for name in FEYWILD_MAPS:
        tilemap = TileMap(config.MAPS_DIR / f"{name}.txt")
        for row, line in enumerate(tilemap._grid):
            for col, char in enumerate(line):
                if char in VEGETATION:
                    assert tilemap.is_solid(col, row), (name, col, row)


def test_every_feywild_map_is_dressed_with_trees_and_shrubs() -> None:
    for name in FEYWILD_MAPS:
        tilemap = TileMap(config.MAPS_DIR / f"{name}.txt")
        kinds = Counter(kind for kind, _c, _r in tilemap.prop_tiles)
        trees = kinds["feywild_grove_tree"]
        shrubs = kinds["feywild_shrub"]
        assert trees >= 20, (name, trees)
        assert shrubs >= 15, (name, shrubs)
        # The plain oak stays a rare landmark, never the dominant note.
        oaks = kinds["feywild_oak"]
        assert oaks <= trees, (name, oaks, trees)


def test_the_reused_silhouettes_and_the_plain_oak_are_authored() -> None:
    import struct

    def png_size(relative):
        data = (config.SPRITES_DIR / relative).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        return struct.unpack(">II", data[16:24])

    for kind in VEGETATION.values():
        variants = _SPRITES[kind]
        assert isinstance(variants, tuple) and len(variants) == 3, kind
        for relative in variants:
            assert (config.SPRITES_DIR / relative).is_file(), relative

    # The grove tree and shrub reuse Chult's exact silhouettes, so they
    # keep those frame sizes: the rounded, un-blocky shapes are the point.
    assert png_size(_SPRITES["feywild_grove_tree"][0]) == png_size(
        _SPRITES["jungle_tree"][0])
    assert png_size(_SPRITES["feywild_shrub"][0]) == png_size(
        _SPRITES["jungle_shrub"][0])
    # The oak rises like a tree rather than sitting low like a shrub.
    oak_w, oak_h = png_size(_SPRITES["feywild_oak"][0])
    assert oak_h > 40 and oak_h > oak_w


def test_the_oak_is_ordinary_while_the_grove_keeps_a_violet_sheen() -> None:
    """The oak must stay believable -- no glow, no strange colour -- while
    the reused Chult foliage picks up only a restrained violet highlight."""
    import pygame

    pygame.init()

    def pixels(relative):
        image = pygame.image.load(str(config.SPRITES_DIR / relative))
        return [image.get_at((x, y))
                for x in range(image.get_width())
                for y in range(image.get_height())
                if image.get_at((x, y)).a > 0]

    oak = pixels(_SPRITES["feywild_oak"][0])
    # Ordinary foliage/bark: green or brown, never a violet cast.
    violet_oak = sum(1 for p in oak if p.b > p.g + 12 and p.r > p.g + 12)
    assert violet_oak == 0, violet_oak

    # The grove tree is the Chult tree with violet added, so compare it
    # against the original pixel for pixel.
    def grid(relative):
        image = pygame.image.load(str(config.SPRITES_DIR / relative))
        return image, image.get_width(), image.get_height()

    grove_img, width, height = grid(_SPRITES["feywild_grove_tree"][0])
    chult_img, chult_w, chult_h = grid(_SPRITES["jungle_tree"][0])
    assert (width, height) == (chult_w, chult_h)

    lifted = greener = same_green = 0
    for x in range(width):
        for y in range(height):
            fey, orig = grove_img.get_at((x, y)), chult_img.get_at((x, y))
            if orig.a == 0:
                continue
            if fey.b > orig.b:
                lifted += 1          # violet added on a lit face
            if fey.g == orig.g:
                same_green += 1      # ...without disturbing the green mass
            if fey.g > fey.r and fey.g > fey.b:
                greener += 1
    # The sheen is real, lands only on some pixels (so it is a highlight,
    # not a wash), and never repaints the green that carries the shape.
    opaque = sum(1 for x in range(width) for y in range(height)
                 if chult_img.get_at((x, y)).a > 0)
    assert lifted >= 30, lifted
    assert lifted < same_green, (lifted, same_green)
    # The green channel is untouched everywhere except the handful of
    # deliberate motes caught in the canopy.
    assert same_green >= opaque - 4, (same_green, opaque)
    assert greener >= lifted, (greener, lifted)


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
    print("All Feywild vegetation tests passed.")


if __name__ == "__main__":
    _run_all()
