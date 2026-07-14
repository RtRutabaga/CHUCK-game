"""Unit tests for the tileset layout contract and ground rendering math.

Run from the project root with:

    python -m tests.test_tileset     (pure Python, no pygame needed)
    pytest                           (if you have pytest)
"""

from src.core import config
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import (
    ANIM_FPS, CHAR_TO_TERRAIN, TILESET_ORDER, art_index,
)

import tempfile
from pathlib import Path


def _map(text: str) -> TileMap:
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                    encoding="utf-8")
    f.write(text); f.close()
    return TileMap(Path(f.name))


def test_every_ground_terrain_has_art() -> None:
    # Mirrors draw_ground's rule (ground = under if set, else the char)
    # and draw_overhead's mapping: every drawable char must have art —
    # a new tile char without art is a loud test failure, not an
    # invisible black square.
    from src.world.tileset_layout import OVERHEAD_CHAR_TO_TERRAIN

    needed_ground = {tile.under if tile.under else char
                     for char, tile in TILE_DEFS.items()}
    assert needed_ground <= set(CHAR_TO_TERRAIN),         needed_ground - set(CHAR_TO_TERRAIN)
    needed_overhead = {char for char, tile in TILE_DEFS.items()
                       if tile.overhead}
    assert needed_overhead <= set(OVERHEAD_CHAR_TO_TERRAIN),         needed_overhead - set(OVERHEAD_CHAR_TO_TERRAIN)
    names = {name for name, _, _ in TILESET_ORDER}
    assert set(CHAR_TO_TERRAIN.values()) <= names
    assert set(OVERHEAD_CHAR_TO_TERRAIN.values()) <= names


def test_art_index_variant_is_stable_per_position() -> None:
    a = art_index(5, 7, variants=3, frames=1, time_s=0.0)
    b = art_index(5, 7, variants=3, frames=1, time_s=99.0)
    assert a == b  # ground never rearranges itself over time


def test_art_index_uses_all_variants() -> None:
    seen = {art_index(c, r, 3, 1, 0.0)
            for c in range(10) for r in range(10)}
    assert seen == {0, 1, 2}


def test_art_index_animates_frames_with_time() -> None:
    f0 = art_index(0, 0, variants=1, frames=2, time_s=0.0)
    f1 = art_index(0, 0, variants=1, frames=2, time_s=1.0 / ANIM_FPS)
    assert {f0, f1} == {0, 1}


def test_art_index_stays_inside_the_row() -> None:
    for name, v, f in TILESET_ORDER:
        for c in range(8):
            for r in range(8):
                for t in (0.0, 0.4, 0.8, 1.6):
                    assert 0 <= art_index(c, r, v, f, t) < v * f


def test_visible_range_culls_and_clamps() -> None:
    m = _map("\n".join(["." * 40] * 24))
    # Camera at origin, 320x180 view: 20 cols, 12 rows (ceil of 11.25).
    assert m.visible_range((0, 0), 320, 180) == (0, 20, 0, 12)
    # Mid-map offset includes partially visible edge tiles.
    assert m.visible_range((8, 8), 320, 180) == (0, 21, 0, 12)
    # Far corner clamps to the map.
    assert m.visible_range((320, 204), 320, 180) == (20, 40, 12, 24)
    # Nothing negative if the camera were somehow past the edge.
    c0, c1, r0, r1 = m.visible_range((10_000, 10_000), 320, 180)
    assert c0 <= c1 and r0 <= r1


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
    print("All tileset tests passed.")


if __name__ == "__main__":
    _run_all()
