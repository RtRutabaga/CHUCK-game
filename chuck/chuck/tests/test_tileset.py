"""Unit tests for the tileset layout contract and ground rendering math.

Run from the project root with:

    python -m tests.test_tileset     (pure Python, no pygame needed)
    pytest                           (if you have pytest)
"""

from src.core import config
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import (
    ANIM_FPS, CHAR_TO_TERRAIN, TILESET_ORDER, TILESETS, art_index,
    tileset_for,
)

import tempfile
from pathlib import Path

REAL_MAPS = (
    "waterdeep_docks", "sewer", "waterdeep_tavern", "waterdeep_pantry",
)


def _map(text: str) -> TileMap:
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                    encoding="utf-8")
    f.write(text); f.close()
    return TileMap(Path(f.name))


def test_each_tileset_is_internally_consistent() -> None:
    # Every char a tileset maps must name a row that actually exists in
    # that tileset's sheet order — the generator and the slicer reading
    # the same contract, per area.
    for name, ts in TILESETS.items():
        row_names = {n for n, _, _ in ts.order}
        assert set(ts.char_to_terrain.values()) <= row_names, name
        assert set(ts.overhead_char_to_terrain.values()) <= row_names, name


def test_every_real_map_is_drawable_by_its_tileset() -> None:
    # Mirrors draw_ground's rule (ground = under if set, else the char)
    # and draw_overhead's mapping: every terrain a real map actually uses
    # must have art in that map's tileset — a char its sheet can't draw
    # is a loud failure here, not an invisible square in the world.
    for map_name in REAL_MAPS:
        m = TileMap(config.MAPS_DIR / f"{map_name}.txt")
        ts = tileset_for(map_name)
        used = {ch for row in m._grid for ch in row}
        for ch in used:
            tile = TILE_DEFS[ch]
            ground = tile.under if tile.under else ch
            assert ground in ts.char_to_terrain, (map_name, ch, ground)
            if tile.overhead:
                assert ch in ts.overhead_char_to_terrain, (map_name, ch)


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
