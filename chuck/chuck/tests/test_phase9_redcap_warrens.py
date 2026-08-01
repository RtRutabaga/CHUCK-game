"""Phase 9 Map 8 --- the Redcap Warrens.

The region's strongest ordinary-enemy area, and the one place the phase
document makes an explicit promise: the player must be able to cross it
without defeating a redcap. These tests hold that promise to the map --
a notice-aware flood proves a safe crossing exists, while the camp centre
stays genuinely contested and the redcaps genuinely cannot follow Chuck
through the root arch or the toadstool caps.
"""

from collections import deque
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import FEYWILD, tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS

MAP_NAME = "feywild_redcap_warrens"
FEN = "feywild_moonmoth_fen"

PASSAGES = frozenset({"≀", "ᚿ"})
GEAR = {
    "ᚠ": "redcap_boot",
    "ᚢ": "redcap_cauldron",
    "ᚦ": "redcap_sickle",
    "ᚱ": "redcap_shelter",
}


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def _tile(position):
    ts = config.TILE_SIZE
    return (int(position[0] // ts), int(position[1] // ts))


def _points(tilemap):
    return {kind.split(":", 1)[1]: _tile(pos)
            for kind, pos in tilemap.object_spawns
            if kind.startswith(("arrival:", "anchor:", "boundary:"))}


def _redcaps(tilemap):
    return [_tile(pos) for kind, pos in tilemap.object_spawns
            if kind == "redcap"]


def _flood(tilemap, start, *, large_actor=False, avoid=()):
    notice = config.REDCAP_NOTICE_RANGE / config.TILE_SIZE

    def open_tile(col, row):
        if tilemap.is_solid(col, row):
            return False
        if large_actor and tilemap._grid[row][col] in PASSAGES:
            return False
        return not any(math.hypot(col - c, row - r) <= notice
                       for c, r in avoid)

    reached = {start}
    frontier = deque([start])
    while frontier:
        col, row = frontier.popleft()
        for point in ((col - 1, row), (col + 1, row),
                      (col, row - 1), (col, row + 1)):
            x, y = point
            if not (0 <= x < tilemap.width_tiles
                    and 0 <= y < tilemap.height_tiles):
                continue
            if point in reached or not open_tile(x, y):
                continue
            reached.add(point)
            frontier.append(point)
    return reached


def test_the_warrens_can_be_crossed_without_meeting_a_redcap() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (76, 50)
    points = _points(tilemap)
    start = points["from_feywild_7"]
    exit_tile = points["feywild_9"]
    redcaps = _redcaps(tilemap)
    assert len(redcaps) == 4

    walkable = _flood(tilemap, start)
    assert exit_tile in walkable and points["feywild_8_anchor"] in walkable

    # The promise: a whole crossing outside every notice range.
    safe = _flood(tilemap, start, avoid=redcaps)
    assert exit_tile in safe, "the warrens cannot be crossed safely"
    assert points["feywild_8_anchor"] in safe

    # ...but the camp is still theirs. The ground around the middle
    # redcap must not appear on any safe route.
    middle = redcaps[len(redcaps) // 2]
    assert not any(
        math.hypot(col - middle[0], row - middle[1]) <= 3
        for col, row in safe
    ), "the camp centre is not actually contested"


def test_redcaps_cannot_follow_chuck_into_the_passages() -> None:
    """Both caches sit behind an opening only a one-foot rat fits through."""
    tilemap = _map()
    start = _points(tilemap)["from_feywild_7"]
    for char in PASSAGES:
        assert not TILE_DEFS[char].solid
        assert TILE_DEFS[char].overhead  # an arch drawn over Chuck's head
        # The engine rule, not just the geometry: a redcap treats the
        # opening as solid and visibly stops at its mouth.
        assert char in collision.LARGE_ACTOR_PASSAGE_TERRAIN, char
    text = "".join(tilemap._grid)
    assert text.count("≀") == 1 and text.count("ᚿ") == 2
    # The toadstool thicket the caps grow from is a solid wall.
    assert TILE_DEFS["ᛘ"].solid
    assert FEYWILD.char_to_terrain["ᛘ"] == "fey_mushroom_thicket"

    caches = {_tile(pos) for kind, pos in tilemap.object_spawns
              if kind == "breakable_grass"}
    assert len(caches) == 2
    chuck = _flood(tilemap, start)
    large = _flood(tilemap, start, large_actor=True)
    assert caches <= chuck
    assert not (caches & large), "a redcap can reach a cache"


def test_thorn_mites_are_the_rat_role_as_fey_wildlife() -> None:
    from src.entities.rat import SewerRat

    tilemap = _map()
    nests = [pos for kind, pos in tilemap.object_spawns
             if kind == "thorn_mite"]
    assert len(nests) == 6

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_8")
        scene._arrival_fade_t = None
        mites = scene.rats
        assert len(mites) == 6
        assert all(isinstance(m, SewerRat) for m in mites)
        assert all(m.variant == "thorn_mite" for m in mites)
        assert all(m.damage == config.RAT_SANITY_DAMAGE for m in mites)
        # They patrol; they do not hunt Chuck across the map.
        assert not any(m.attack_chase_enabled for m in mites)

        # One committed scratch clears one mite, exactly like a rat.
        mite = mites[0]
        scene.player.x = mite.x - 4
        scene.player.y = mite.y
        scene.player.facing = "right"
        before = len(scene.rats)
        game.input.begin_frame()
        game.input._actions_just_pressed.add("scratch")
        scene.update(0.001)
        scene.update(0.001)
        assert len(scene.rats) == before - 1
    finally:
        game._shutdown()


def test_the_camp_is_dressed_in_gnome_sized_gear() -> None:
    """The scale premise, told by scenery before any redcap notices."""
    import struct

    from src.entities.prop import _SPRITES

    tilemap = _map()
    kinds = {kind for kind, _c, _r in tilemap.prop_tiles}
    for char, prop in GEAR.items():
        assert TILE_DEFS[char].solid and TILE_DEFS[char].prop == prop
        assert prop in kinds, prop

    def png_size(relative):
        data = (config.SPRITES_DIR / relative).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        return struct.unpack(">II", data[16:24])

    def first(prop):
        sprite = _SPRITES[prop]
        return sprite[0] if isinstance(sprite, tuple) else sprite

    # Chuck stands 14px. A discarded boot matches him; the shelter and
    # the planted sickle tower over him.
    _boot_w, boot_h = png_size(first("redcap_boot"))
    assert boot_h >= 14
    assert png_size(first("redcap_shelter"))[1] >= 32
    assert png_size(first("redcap_sickle"))[1] >= 32
    assert png_size(first("redcap_cauldron"))[1] >= 20

    # The camp floor is its own trampled earth, not the region's path.
    assert not TILE_DEFS["ᛜ"].solid
    assert FEYWILD.char_to_terrain["ᛜ"] == "fey_camp_dirt"
    assert sum(row.count("ᛜ") for row in tilemap._grid) >= 200


def test_warrens_checkpoints_music_and_the_fen_connection() -> None:
    entry = CHECKPOINT_BY_ID["feywild_8"]
    assert entry.display_name == "Feywild 8" and entry.runtime_entry
    assert entry.map_name == MAP_NAME and entry.arrival == "from_feywild_7"
    anchor = CHECKPOINT_BY_ID["feywild_8_anchor"]
    assert anchor.saveable and not anchor.development_visible
    assert tileset_for(MAP_NAME).sheet == "feywild.png"
    assert AREA_MUSIC[MAP_NAME] == "feywild.wav"
    assert AREA_WALK_EXITS[(FEN, "→")].destination == MAP_NAME
    assert AREA_WALK_EXITS[(MAP_NAME, "←")].destination == FEN

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("feywild_7")
        scene._arrival_fade_t = None
        onward = next((c, r) for r in range(scene.tilemap.height_tiles)
                      for c in range(scene.tilemap.width_tiles)
                      if scene.tilemap.terrain_at(c, r) == "→")
        scene.player.x = onward[0] * config.TILE_SIZE + 3
        scene.player.y = onward[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == MAP_NAME
        assert game.active_checkpoint_id == "feywild_8"
        scene.update(0.0)
        assert scene.map_name == MAP_NAME  # no bounce

        back = next((c, r) for r in range(scene.tilemap.height_tiles)
                    for c in range(scene.tilemap.width_tiles)
                    if scene.tilemap.terrain_at(c, r) == "←")
        scene.player.x = back[0] * config.TILE_SIZE + 3
        scene.player.y = back[1] * config.TILE_SIZE + 4
        scene.update(0.0)
        assert scene.map_name == FEN
        assert game.active_checkpoint_id == "feywild_7_return"
    finally:
        game._shutdown()


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
    print("All Redcap Warrens tests passed.")


if __name__ == "__main__":
    _run_all()
