"""Temple interior dressing: idols, stelae, urns, and fallen columns.

The temple's version of the game's established style add-ons (the
three-quarter Waterdeep buildings, market stall, jungle cog, trees, and
shrubs): y-sorted, procedural set pieces. Wall pieces keep the wall's
solidity so no route, torch count, or hazard lane changes; floor pieces
occupy single tiles in broad rooms only. Idols, stelae, and columns are
mute scenery; urns are scratch-breakables (see test_temple_urns) but
still speak no dialogue and are placed by the same dressing chars.
"""

from collections import Counter, deque

from src.core import config
from src.entities.prop import _SPRITES
from src.world.tilemap import MARKER_DEFS, TILE_DEFS, TileMap


TEMPLE_MAPS = (
    "temple_entrance", "temple_spikes", "temple_skeletons",
    "temple_darts", "temple_snakes", "temple_astral_wind",
)
DRESSING_KINDS = ("temple_idol", "temple_stela", "temple_urn",
                  "temple_column")
WALL_CHARS = ("†", "‡", "¦")
FLOOR_CHARS = ("¢", "¬")

# Locked placements: dressing per map, by prop kind. (The entrance
# hall's two north-wall idols became the facade's carved skulls in
# session 114; its other dressing is unchanged.)
EXPECTED = {
    "temple_entrance": {"temple_stela": 4,
                        "temple_urn": 7, "temple_column": 2},
    "temple_spikes": {"temple_stela": 4, "temple_urn": 2},
    "temple_skeletons": {"temple_idol": 2, "temple_stela": 3,
                         "temple_urn": 9, "temple_column": 1},
    "temple_darts": {"temple_idol": 1, "temple_stela": 2,
                     "temple_urn": 2},
    "temple_snakes": {"temple_idol": 2, "temple_stela": 2,
                      "temple_urn": 3, "temple_column": 1},
    "temple_astral_wind": {"temple_stela": 2, "temple_urn": 3},
}


def _map(name: str) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def test_every_temple_map_carries_the_authored_dressing() -> None:
    for name in TEMPLE_MAPS:
        tilemap = _map(name)
        kinds = Counter(kind for kind, _c, _r in tilemap.prop_tiles
                        if kind in DRESSING_KINDS)
        assert dict(kinds) == EXPECTED[name], (name, dict(kinds))


def test_dressing_chars_are_solid_scenery_over_temple_terrain() -> None:
    for char in WALL_CHARS:
        tile = TILE_DEFS[char]
        assert tile.solid and tile.under == "█", char
    for char in FLOOR_CHARS:
        tile = TILE_DEFS[char]
        assert tile.solid and tile.under == "·", char
    for char in WALL_CHARS + FLOOR_CHARS:
        assert TILE_DEFS[char].prop in DRESSING_KINDS
        assert char not in MARKER_DEFS  # scenery, never a spawn


def test_dressing_is_mute_scenery_with_variant_sprites() -> None:
    from src.entities.prop import PROP_CHOICE, PROP_DIALOGUE

    for kind in DRESSING_KINDS:
        assert kind not in PROP_DIALOGUE and kind not in PROP_CHOICE
        variants = _SPRITES[kind]
        assert isinstance(variants, tuple) and len(variants) >= 2
        for relative in variants:
            path = config.SPRITES_DIR / relative
            assert path.is_file(), path


def test_dressing_scale_matches_the_temple_language() -> None:
    """Idols and stelae rise past human height/tile scale; urns and
    fallen columns stay low. All are readable at native resolution."""
    import struct
    import zlib

    def png_size(path):
        data = path.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", data[16:24])
        return width, height

    for relative in _SPRITES["temple_idol"]:
        w, h = png_size(config.SPRITES_DIR / relative)
        assert h > 30, "an idol should rise past the human NPC scale"
    for relative in _SPRITES["temple_stela"]:
        w, h = png_size(config.SPRITES_DIR / relative)
        assert h > config.TILE_SIZE * 2 - 2
    for kind in ("temple_urn", "temple_column"):
        for relative in _SPRITES[kind]:
            w, h = png_size(config.SPRITES_DIR / relative)
            assert h <= 18, (kind, "stays low to the floor")


def test_deeper_door_is_a_monumental_facade_with_fires_and_skulls() -> None:
    """Session 114 showcase: Temple Map 1's north door is the reference
    facade — one spanning gate over the walkable threshold, carved
    skulls flanking it on the wall, and two animated pedestal braziers
    burning before it. The broad chambers carry the language onward."""
    entrance = _map("temple_entrance")
    kinds = Counter(kind for kind, _c, _r in entrance.prop_tiles)
    assert kinds["temple_gate"] == 1
    assert kinds["temple_skull"] == 2
    assert kinds["temple_arch_ns"] == 1  # the south arch remains
    gate = TILE_DEFS["£"]
    assert not gate.solid and gate.under == "∇"  # still a threshold
    skull = TILE_DEFS["€"]
    assert skull.solid and skull.under == "█"
    assert TILE_DEFS["ø"].solid
    assert sum(row.count("ø") for row in entrance._grid) == 2
    # The processional path runs unbroken down the aisle to the gate:
    # every aisle row between the doors carries walkable path (the
    # three center markers sit ON it via their under-terrain).
    assert not TILE_DEFS["≡"].solid
    for row_i in range(3, 35):
        aisle = [entrance.terrain_at(c, row_i) for c in (21, 22, 23, 24)]
        assert any(ch in "≡υρκ" for ch in aisle), (row_i, aisle)
        assert all(not entrance.is_solid(c, row_i)
                   for c in (21, 22, 23, 24)), row_i
    # The chambers continue the language: skulls in the skeleton hall,
    # braziers beside the snake chamber's serpent idols.
    skeletons = _map("temple_skeletons")
    assert Counter(k for k, _c, _r in skeletons.prop_tiles)[
        "temple_skull"] == 2
    assert sum(row.count("ø") for row in skeletons._grid) == 2
    snakes = _map("temple_snakes")
    assert sum(row.count("ø") for row in snakes._grid) == 2


def test_guardian_monuments_stand_in_rows_through_the_open_halls() -> None:
    """Sessions 115-116: large ziggurat statues (48x64 props on 3x2
    solid wall footprints; 'Ϙ' skull and 'Ϟ' serpent anchors) close
    down the broad rooms' open space in dense alternating guardian
    rows. The snake chamber's guardians are all serpents — its statues
    match its inhabitants."""
    expected = {
        "temple_entrance": {"temple_monument": 6,
                            "temple_serpent_monument": 4},
        "temple_spikes": {"temple_monument": 3,
                          "temple_serpent_monument": 2},
        "temple_skeletons": {"temple_monument": 4,
                             "temple_serpent_monument": 2},
        "temple_darts": {"temple_monument": 1,
                         "temple_serpent_monument": 1},
        "temple_snakes": {"temple_serpent_monument": 4},
    }
    monument_kinds = ("temple_monument", "temple_serpent_monument")
    for name, counts in expected.items():
        tilemap = _map(name)
        kinds = Counter(kind for kind, _c, _r in tilemap.prop_tiles
                        if kind in monument_kinds)
        assert dict(kinds) == counts, (name, dict(kinds))
        anchors = [(c, r) for kind, c, r in tilemap.prop_tiles
                   if kind in monument_kinds]
        for col, row in anchors:
            # The full 3x2 footprint is solid; the anchor carries the prop.
            for c in (col - 1, col, col + 1):
                for r in (row - 1, row):
                    assert tilemap.is_solid(c, r), (name, (c, r))
        # Rows: every monument shares its anchor column or row with
        # another — statues stand in formation, never scattered singly.
        for col, row in anchors:
            assert any((c == col or r == row) and (c, r) != (col, row)
                       for c, r in anchors), (name, (col, row))
    for char, kind in (("Ϙ", "temple_monument"),
                       ("Ϟ", "temple_serpent_monument")):
        tile = TILE_DEFS[char]
        assert tile.solid and tile.under == "█"
        assert tile.prop == kind
        assert isinstance(_SPRITES[kind], tuple)


def test_every_temple_door_has_a_centered_path_stub() -> None:
    """Session 119: short runs of the processional path sit centered
    before every temple doorway (the entrance hall's full aisle already
    connects both of its doors). Door arrivals/anchors inside a stub
    declare the path as their under-terrain, so the counts below are
    grid counts — markers included, seamless."""
    expected = {"temple_spikes": 18, "temple_skeletons": 12,
                "temple_darts": 6, "temple_snakes": 15,
                "temple_astral_wind": 18}
    for name, count in expected.items():
        tilemap = _map(name)
        path = sum(row.count("≡") for row in tilemap._grid)
        assert path == count, (name, path)
        for row_i, row in enumerate(tilemap._grid):
            for col_i, char in enumerate(row):
                if char == "≡":
                    assert not tilemap.is_solid(col_i, row_i)


def test_floor_dressing_never_seals_a_route() -> None:
    """Each dressed map's arrival still reaches its onward boundary
    (jump-only terrain treated as crossable, matching gameplay)."""
    crossable_by_jump = {"♠", "V"}
    for name in TEMPLE_MAPS:
        tilemap = _map(name)
        points = {}
        for kind, (x, y) in tilemap.object_spawns:
            if kind.startswith(("arrival:", "boundary:")):
                points[kind] = (int(x // config.TILE_SIZE),
                                int(y // config.TILE_SIZE))
        assert points, name
        start = next(p for k, p in points.items()
                     if k.startswith("arrival:"))
        reached = {start}
        frontier = deque([start])
        while frontier:
            col, row = frontier.popleft()
            for nxt in ((col - 1, row), (col + 1, row),
                        (col, row - 1), (col, row + 1)):
                if nxt in reached:
                    continue
                if (tilemap.is_solid(*nxt)
                        and tilemap.terrain_at(*nxt)
                        not in crossable_by_jump):
                    continue
                reached.add(nxt)
                frontier.append(nxt)
        for kind, point in points.items():
            assert point in reached, (name, kind)


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
    print("All temple dressing tests passed.")


if __name__ == "__main__":
    _run_all()
