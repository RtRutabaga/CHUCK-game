"""Unit tests for src/world/tilemap.py.

Run from the project root with:

    python -m tests.test_tilemap      (plain asserts, no dependencies)
    pytest                            (if you have pytest)

TileMap parsing and collision don't touch pygame, so these run anywhere.
"""

import tempfile
from pathlib import Path

from src.core import config
from src.world.tilemap import TileMap

TS = config.TILE_SIZE


def _write_map(text: str) -> Path:
    f = tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8"
    )
    f.write(text)
    f.close()
    return Path(f.name)


def test_parses_dimensions_and_solidity() -> None:
    m = TileMap(_write_map("###\n#.#\n###\n"))
    assert (m.width_tiles, m.height_tiles) == (3, 3)
    assert m.is_solid(0, 0) and m.is_solid(2, 2)
    assert not m.is_solid(1, 1)


def test_out_of_bounds_is_solid() -> None:
    m = TileMap(_write_map("...\n...\n"))
    assert m.is_solid(-1, 0)
    assert m.is_solid(0, -1)
    assert m.is_solid(3, 0)
    assert m.is_solid(0, 2)


def test_water_and_barrels_are_solid_planks_and_stone_are_not() -> None:
    m = TileMap(_write_map("~o\n=,\n"))
    assert m.is_solid(0, 0)      # water
    assert m.is_solid(1, 0)      # barrel
    assert not m.is_solid(0, 1)  # planks
    assert not m.is_solid(1, 1)  # stone


def test_spawn_point_is_tile_center_in_pixels() -> None:
    m = TileMap(_write_map("...\n.C.\n...\n"))
    assert m.spawn_points["player"] == (1 * TS + TS / 2, 1 * TS + TS / 2)


def test_comment_lines_are_ignored() -> None:
    m = TileMap(_write_map("; a note about this map\n##\n#.\n; trailing note\n"))
    assert (m.width_tiles, m.height_tiles) == (2, 2)
    assert not m.is_solid(1, 1)


def test_ragged_lines_pad_solid() -> None:
    m = TileMap(_write_map("....\n..\n....\n"))
    assert m.is_solid(2, 1) and m.is_solid(3, 1)
    assert not m.is_solid(1, 1)


def test_unknown_character_raises_with_location() -> None:
    try:
        TileMap(_write_map("..\n.@\n"))
    except ValueError as exc:
        msg = str(exc)
        assert "'@'" in msg and "row 1" in msg and "col 1" in msg, msg
    else:
        raise AssertionError("expected ValueError for unknown tile char")


def test_prop_tiles_are_solid_and_listed() -> None:
    m = TileMap(_write_map(",o=\n.X,\n"))
    assert m.is_solid(1, 0) and m.is_solid(1, 1)  # barrel + crate solid
    assert ("barrel", 1, 0) in m.prop_tiles
    assert ("crate", 1, 1) in m.prop_tiles
    assert len(m.prop_tiles) == 2


def test_docks_has_its_barrels_and_crates() -> None:
    from collections import Counter
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    counts = Counter(kind for kind, _, _ in m.prop_tiles)
    assert counts["barrel"] >= 2 and counts["crate"] >= 4, dict(counts)
    # Exactly one Bobert, asleep beside Chuck's spawn, and he is pure
    # scenery: solid terrain, no object spawn, nothing to interact with.
    assert counts["bobert_barrel"] == 1
    (col, row) = next((c, r) for k, c, r in m.prop_tiles
                      if k == "bobert_barrel")
    sx, sy = m.spawn_points["player"]
    assert abs(col * TS - sx) <= 2 * TS and abs(row * TS - sy) <= 2 * TS
    assert all(not k.startswith("bobert") for k, _ in m.object_spawns)


def test_awning_is_walkable_with_overhead_and_stone_beneath() -> None:
    from src.world.tilemap import TILE_DEFS
    m = TileMap(_write_map(",a,\n,,,\n"))
    assert not m.is_solid(1, 0)            # Chuck walks under it
    tile = TILE_DEFS["a"]
    assert tile.overhead == "awning" and tile.under == ","


def test_door_is_solid() -> None:
    m = TileMap(_write_map(",D,\n"))
    assert m.is_solid(1, 0)


def test_docks_every_walkable_tile_is_reachable_from_spawn() -> None:
    """No sealed pockets, ever — the map must be one connected world."""
    from collections import deque
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    sx, sy = m.spawn_points["player"]
    start = (int(sx // TS), int(sy // TS))
    seen = {start}
    q = deque([start])
    while q:
        c, r = q.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c + dc, r + dr)
            if n not in seen and not m.is_solid(*n):
                seen.add(n)
                q.append(n)
    walkable = {(c, r) for r in range(m.height_tiles)
                for c in range(m.width_tiles) if not m.is_solid(c, r)}
    sealed = walkable - seen
    assert not sealed, f"sealed pockets: {sorted(sealed)[:8]}"


def test_docks_has_the_tavern_front() -> None:
    from collections import Counter
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    counts = Counter(kind for kind, _, _ in m.prop_tiles)
    assert counts["herod_sign"] == 1
    # A door exists somewhere in the tavern's south face.
    assert any("D" in row for row in m._grid)
    # And the market has awning tiles.
    assert any("a" in row for row in m._grid)


def test_docks_tavern_exterior_reads_as_a_building() -> None:
    """Facade-reference reskin: roof above eave above brick facade,
    two lit windows flanking the door, two chimneys, all solid, door
    exactly where it has always been."""
    from collections import Counter
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    assert m.terrain_at(44, 17) == "D"
    counts = Counter(kind for kind, _, _ in m.prop_tiles)
    assert counts["chimney"] == 5  # 2 tavern + 1 per district house
    windows = [(c, r) for r in range(14, 18)
               for c in range(34, 56) if m.terrain_at(c, r) == "W"]
    assert sorted(windows) == [(40, 16), (48, 16)]  # flanking the door
    # Vertical grammar at the door column: roof, eave, facade, door.
    column = [m.terrain_at(44, r) for r in range(8, 18)]
    assert column == ["r", "r", "r", "r", "r", "e", "t", "t", "t", "D"]
    for r in range(8, 18):
        for c in range(34, 56):
            assert m.is_solid(c, r)


def test_docks_district_wall_reads_as_a_castle_wall() -> None:
    """Wall-reference reskin: battlements over brick, banners and
    torches deliberately placed, portcullis gates walkable, footprint
    and collision identical to the old generic wall."""
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    for c in range(7, 34):
        top, body = m.terrain_at(c, 8), m.terrain_at(c, 9)
        if c in (21, 22, 31, 32):  # the two gates
            assert top == "," and body == "g"
            assert not m.is_solid(c, 8) and not m.is_solid(c, 9)
        else:
            assert top == "w", (c, top)
            assert body in "bFi", (c, body)
            assert m.is_solid(c, 8) and m.is_solid(c, 9)
    assert [c for c in range(7, 34) if m.terrain_at(c, 9) == "F"] == [14, 26]
    assert [c for c in range(7, 34) if m.terrain_at(c, 9) == "i"] ==         [20, 23, 30, 33]


def test_docks_district_blocks_are_houses() -> None:
    """The three north blocks read as buildings: roof over eave over
    facade, each with two lit windows, a decorative door, a chimney —
    and all of it solid (never accessible; style only)."""
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    for block, door_col in ((range(10, 18), 14), (range(24, 32), 28),
                            (range(36, 44), 39)):
        for c in block:
            assert m.terrain_at(c, 1) in "rm" and m.terrain_at(c, 2) == "r"
            assert m.terrain_at(c, 3) == "e"
            assert m.terrain_at(c, 4) in "tWh"
            for r in range(1, 5):
                assert m.is_solid(c, r), (c, r)
        assert m.terrain_at(door_col, 4) == "h"
        windows = [c for c in block if m.terrain_at(c, 4) == "W"]
        assert len(windows) == 2, (list(block), windows)



def test_docks_market_stall_reads_like_the_reference() -> None:
    """Cutaway stall: the canopy covers only the back rows and ends in
    a scalloped edge held by corner posts; the goods stand VISIBLE in
    the open front — green, red, table, orange, barrel."""
    from src.world.tilemap import TILE_DEFS
    from src.world.tileset_layout import OVERHEAD_CHAR_TO_TERRAIN
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    # Canopy body over the back rows...
    for c in range(41, 53):
        assert m.terrain_at(c, 28) == "a" and m.terrain_at(c, 29) == "a"
    # ...ending in the scalloped edge with posts at the corners...
    assert m.terrain_at(41, 30) == "P" and m.terrain_at(52, 30) == "P"
    for c in range(42, 52):
        assert m.terrain_at(c, 30) == "u" and not m.is_solid(c, 30)
    # ...and the goods in the open, with NO canvas above them.
    goods = [m.terrain_at(c, 31) for c in (43, 45, 47, 49, 51)]
    assert goods == ["1", "2", "5", "3", "4"]
    for ch in goods:
        tile = TILE_DEFS[ch]
        assert tile.prop and tile.overhead is None
        assert ch not in OVERHEAD_CHAR_TO_TERRAIN
        assert m.is_solid(goods.index(ch) * 2 + 43, 31)


def test_docks_ruined_foundation_is_solid_style() -> None:
    """The mid-map ruin: crumbling perimeter around rubble, with two
    collapsed wall gaps — every tile solid, pure style."""
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    for r in range(21, 25):
        for c in range(26, 32):
            ch = m.terrain_at(c, r)
            edge = r in (21, 24) or c in (26, 31)
            expected = "Rf" if edge else "f"  # gaps allow 'f' on edges
            assert ch in expected, (c, r, ch)
            assert m.is_solid(c, r)
    # The collapse points read through the wall line.
    assert m.terrain_at(29, 21) == "f" and m.terrain_at(26, 23) == "f"


def test_docks_guard_stands_at_the_edge_of_the_upper_plaza() -> None:
    """Phase 2: the guard posts the east end of the upper plaza — the
    way out of the docks. No gate, no barrier: the map edge already
    ends the road, so he only has to stand there and say his line."""
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    guards = [c for k, c in m.object_spawns if k == "npc:guard"]
    assert len(guards) == 1
    gx, gy = guards[0]
    col, row = int(gx // TS), int(gy // TS)
    assert (col, row) == (54, 5)
    assert not m.is_solid(col, row)         # he stands on open street
    # The north wall is unbroken battlements: no gate was ever cut.
    assert all(m.terrain_at(c, 0) == "w" for c in range(7, 56))


def test_gate_is_walkable_with_portcullis_overhead() -> None:
    from src.world.tilemap import TILE_DEFS
    m = TileMap(_write_map(",g,\n"))
    assert not m.is_solid(1, 0)
    tile = TILE_DEFS["g"]
    assert tile.overhead == "gate" and tile.under == ","


def test_terrain_at_returns_char_and_solid_out_of_bounds() -> None:
    m = TileMap(_write_map(",=\n~#\n"))
    assert m.terrain_at(0, 0) == "," and m.terrain_at(1, 0) == "="
    assert m.terrain_at(0, 1) == "~" and m.terrain_at(1, 1) == "#"
    assert m.terrain_at(-1, 0) == "#" and m.terrain_at(0, 9) == "#"


def test_markers_record_spawns_and_use_under_tile() -> None:
    m = TileMap(_write_map(",c,\n,C,\n"))
    # Marker tiles collide/draw as their under-terrain (no seams).
    assert not m.is_solid(1, 0) and not m.is_solid(1, 1)
    assert m.object_spawns == [("cigarette", (1 * TS + TS / 2, TS / 2))]
    assert m.spawn_points["player"] == (1 * TS + TS / 2, 1 * TS + TS / 2)


def test_marker_on_solid_under_tile_is_rejected() -> None:
    # A hypothetical marker over solid terrain must fail loudly. All
    # current markers use walkable under-tiles, so patch one in.
    import src.world.tilemap as tm
    tm.MARKER_DEFS["!"] = tm.MarkerDef(kind="cigarette", under="#")
    try:
        TileMap(_write_map("..\n.!\n"))
    except ValueError as exc:
        assert "solid" in str(exc) and "row 1" in str(exc), str(exc)
    else:
        raise AssertionError("expected ValueError for marker on solid tile")
    finally:
        del tm.MARKER_DEFS["!"]


def test_real_docks_map_loads_and_spawn_is_walkable() -> None:
    m = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    # Big enough to scroll: at least one native screen in each axis.
    assert m.width_tiles * TS >= config.NATIVE_WIDTH
    assert m.height_tiles * TS >= config.NATIVE_HEIGHT
    cx, cy = m.spawn_points["player"]
    assert not m.is_solid(int(cx // TS), int(cy // TS))
    # The harbor's southwest corner is water (solid): Chuck cannot swim.
    assert m.is_solid(0, m.height_tiles - 1)
    # The docks are littered with cigarettes, all on walkable ground.
    cigs = [pos for kind, pos in m.object_spawns if kind == "cigarette"]
    assert len(cigs) >= 3
    for x, y in cigs:
        assert not m.is_solid(int(x // TS), int(y // TS))


def test_sewer_is_a_narrow_connected_descent() -> None:
    """Phase 2: the sewer is a single narrow, mostly-linear descent —
    no sealed pockets, long enough to scroll, its placeholder terrain
    present, and (for now) walled off at the bottom. The outflow exit
    back to the docks is a later Phase 2 session."""
    from collections import deque
    m = TileMap(config.MAPS_DIR / "sewer.txt")
    # Long enough to scroll vertically; at least a screen wide so the
    # camera never shows void past the edge; far narrower than the docks.
    assert m.height_tiles * TS >= config.NATIVE_HEIGHT
    assert m.width_tiles * TS >= config.NATIVE_WIDTH
    docks = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    assert m.width_tiles < docks.width_tiles
    # The entrance spawn sits near the top, on walkable ground.
    sx, sy = m.spawn_points["player"]
    scol, srow = int(sx // TS), int(sy // TS)
    assert srow <= 3
    assert not m.is_solid(scol, srow)
    # The placeholder sewer terrains are all present (dirt, mud, channel).
    chars = {ch for row in m._grid for ch in row}
    assert {"d", "M", "%"} <= chars
    # One connected world: every walkable tile is reachable from spawn.
    seen = {(scol, srow)}
    q = deque([(scol, srow)])
    while q:
        c, r = q.popleft()
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c + dc, r + dr)
            if n not in seen and not m.is_solid(*n):
                seen.add(n)
                q.append(n)
    walkable = {(c, r) for r in range(m.height_tiles)
                for c in range(m.width_tiles) if not m.is_solid(c, r)}
    sealed = walkable - seen
    assert not sealed, f"sealed pockets: {sorted(sealed)[:8]}"
    # Bottom row is solid: no way out yet (the exit is a later session).
    assert all(m.is_solid(c, m.height_tiles - 1)
               for c in range(m.width_tiles))


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
    print("All tilemap tests passed.")


if __name__ == "__main__":
    _run_all()
