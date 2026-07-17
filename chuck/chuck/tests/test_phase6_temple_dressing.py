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

# Locked placements: dressing per map, by prop kind.
EXPECTED = {
    "temple_entrance": {"temple_idol": 2, "temple_stela": 4,
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
