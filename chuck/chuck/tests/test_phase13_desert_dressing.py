"""The desert's second pass: texture, ruins, palms, fires and axes.

Everything here is art, which makes it the easiest thing in the project
to get wrong invisibly. A prop that is authored but never drawn, a
canopy that lands two tiles above the tree casting it, an axe hidden
behind the arm holding it -- none of those raise anything, and all of
them look fine in the source.

So the assertions are about consequences rather than about presence.
Not "the cliff tile exists" but "every quarter of it has more than one
colour in it"; not "the map has palm props" but "each one has its own
shade above it and stands the same distance from the water as the
rest"; not "the fire pit sprite is bigger" but "it is bigger than the
tile it replaced, and the ground it stands on is walkable now that the
fire is a prop rather than a wall".

The one thing that is checked by presence is the axe, and even that is
checked outside the orc's silhouette: a weapon drawn behind the body is
a weapon nobody sees.
"""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.core.game import Game
from src.entities.prop import _ANIMATED_SPRITES, _SPRITES
from src.systems.checkpoints import DESERT_ENTRY_FLAGS
from src.world import collision
from src.world.tilemap import TILE_DEFS, TileMap
from src.world.tileset_layout import DESERT, TILE_PX

import sys
sys.path.insert(0, "tools")
from generate_desert_central import RUINS  # noqa: E402
from generate_desert_oasis import (  # noqa: E402
    CROWN_ROWS, PALM_COUNT, PALM_RING, POOL,
)
from generate_desert_orc_camp import BURN, FIRES  # noqa: E402
from generate_desert_ruin_dressing import (  # noqa: E402
    COLUMN, COLUMN_SAND, FALLEN, FALLEN_SAND, RUBBLE, RUBBLE_SAND,
    dress_ruin,
)
from generate_desert_undead_ruins import COURT, OUTER  # noqa: E402


COLUMNS = (COLUMN, COLUMN_SAND)
FALLENS = (FALLEN, FALLEN_SAND)
RUBBLES = (RUBBLE, RUBBLE_SAND)
RUIN_PIECES = COLUMNS + FALLENS + RUBBLES

PALM_CHARS = ("⍑", "⍒")
CANOPY_CHARS = ("⏦", "⍚")
SCORCH = "⚱"
FIRE_PIT = "⍘"


def _tilemap(name: str) -> TileMap:
    return TileMap(config.MAPS_DIR / f"{name}.txt")


def _world(checkpoint: str):
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    world = game.checkpoints.load_checkpoint(
        checkpoint, progress_flags=set(DESERT_ENTRY_FLAGS)
    )
    world._arrival_fade_t = None
    return directory, game, world


def _safe_flood(tilemap: TileMap, origin) -> set[tuple[int, int]]:
    seen = {origin}
    frontier = [origin]
    while frontier:
        x, y = frontier.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cell = (x + dx, y + dy)
            if cell in seen or tilemap.is_solid(*cell):
                continue
            if tilemap.terrain_at(*cell) in collision.FALL_HAZARD_TERRAIN:
                continue
            seen.add(cell)
            frontier.append(cell)
    return seen


def _rock_tile(sheet, variant: int):
    row = [name for name, _, _ in DESERT.order].index("desert_rock")
    return [[sheet.get_at((variant * TILE_PX + x, row * TILE_PX + y))[:3]
             for y in range(TILE_PX)] for x in range(TILE_PX)]


def test_the_cliffs_are_grained_all_over_rather_than_in_one_corner() -> None:
    """Texture measured where it has to be, not where it is easiest.

    A tile can pass "has plenty of colours in it" while being a flat
    slab with a busy stripe down one side, and a wall of that reads as
    panelling. So the tile is quartered and each quarter has to carry
    its own variation -- which is the property the reference photograph
    actually has: there is no smooth area of sandstone anywhere on it.
    """
    pygame.init()
    sheet = pygame.image.load(str(config.ASSETS_DIR / "tilesets" / DESERT.sheet))
    variants, _ = DESERT.info()["desert_rock"]
    for variant in range(variants):
        pixels = _rock_tile(sheet, variant)
        half = TILE_PX // 2
        for qx in (0, half):
            for qy in (0, half):
                found = {pixels[x][y]
                         for x in range(qx, qx + half)
                         for y in range(qy, qy + half)}
                assert len(found) >= 3, (variant, qx, qy, len(found))
        assert len({tuple(column) for column in pixels}) > 8, variant


def test_the_fissure_runs_down_a_whole_cliff_rather_than_one_tile() -> None:
    """The only feature that can be continuous, and it is.

    A tile's variant comes from its position, so it changes from row to
    row. That means anything drawn at a different x in different
    variants stops dead at every tile boundary -- and a face of
    fissures that all stop at the same height is brickwork. Exactly one
    feature is therefore identical in all four variants: the crevice
    that enters the top edge and leaves the bottom edge at the same
    place, so it chains down the whole height of a cliff.
    """
    pygame.init()
    sheet = pygame.image.load(str(config.ASSETS_DIR / "tilesets" / DESERT.sheet))
    variants, _ = DESERT.info()["desert_rock"]
    tiles = [_rock_tile(sheet, variant) for variant in range(variants)]

    def darkest_x(pixels, y: int) -> int:
        return min(range(TILE_PX), key=lambda x: sum(pixels[x][y]))

    entries = {darkest_x(pixels, 0) for pixels in tiles}
    exits = {darkest_x(pixels, TILE_PX - 1) for pixels in tiles}
    assert len(entries) == 1, entries
    assert entries == exits, (entries, exits)

    # ...and it really is a crevice: much darker than the face it is cut
    # into, in every variant.
    for variant, pixels in enumerate(tiles):
        x = next(iter(entries))
        crevice = sum(pixels[x][0])
        face = max(sum(pixels[fx][0]) for fx in range(TILE_PX))
        assert crevice < face * 0.75, (variant, crevice, face)


def test_the_pieces_of_a_ruin_go_outward() -> None:
    """The dressing rule itself, on a blank sheet of sand.

    Tested here rather than by counting blocks on the finished maps,
    because the undead ruins have a courtyard inside an outer wall and
    the two share a centre -- everything the courtyard threw off lands
    inside the outer building, so no measurement taken on that map can
    tell tidied-away from thrown-clear. The rule is what matters and
    the rule is checkable directly: a ruin that has had its blocks
    dropped in the middle of itself looks like a warehouse.
    """
    width, height = 24, 20
    for seed in range(6):
        grid = [["." for _ in range(width)] for _ in range(height)]
        rect = (6, 5, 10, 8)
        placed = dress_ruin(grid, *rect, seed=seed)
        assert placed >= 5, (seed, placed)

        left, top, rect_w, rect_h = rect
        blocks = [(x, y) for y in range(height) for x in range(width)
                  if grid[y][x] in RUBBLES]
        assert blocks, seed
        for x, y in blocks:
            assert not (left <= x < left + rect_w
                        and top <= y < top + rect_h), (seed, x, y)

        # Columns stand at the corners, where the load was -- never in
        # the middle of the floor, which is where a warehouse keeps them.
        standing = [(x, y) for y in range(height) for x in range(width)
                    if grid[y][x] in COLUMNS]
        assert len(standing) >= 2, seed
        for x, y in standing:
            assert not (left < x < left + rect_w - 1
                        and top < y < top + rect_h - 1), (seed, x, y)

        # One column down full length inside, and one outside. It is the
        # loudest thing in the vocabulary: two in the same room reads as
        # a quarry rather than as a building that fell over.
        down = sum(1 for y in range(top, top + rect_h)
                   for x in range(left, left + rect_w)
                   if grid[y][x] in FALLENS)
        assert down <= 1, (seed, down)

    # ...and no two ruins are dressed identically. The seed is the
    # ruin's own position, so a map redraws the same way twice while
    # six ruins in a row do not come out as six copies of one.
    shapes = set()
    for seed in range(6):
        grid = [["." for _ in range(width)] for _ in range(height)]
        dress_ruin(grid, 6, 5, 10, 8, seed=seed)
        shapes.add("".join("".join(row) for row in grid))
    assert len(shapes) >= 5, len(shapes)


def test_both_maps_dress_their_ruins_out_of_the_same_box() -> None:
    """Every building has pieces, and they are the same pieces.

    The hub's scattered rectangles are meant to be fragments of the
    building south of them, so they are dressed by the same helper --
    two dressing rules would quietly make them two kinds of place.
    """
    for name, rects in (("desert_central", RUINS),
                        ("desert_undead_ruins", (OUTER, COURT))):
        tilemap = _tilemap(name)
        for left, top, width, height in rects:
            pieces = [
                (x, y)
                for y in range(max(0, top - 4),
                               min(tilemap.height_tiles, top + height + 5))
                for x in range(max(0, left - 4),
                               min(tilemap.width_tiles, left + width + 5))
                if tilemap.terrain_at(x, y) in RUIN_PIECES
            ]
            kinds = {tilemap.terrain_at(x, y) for x, y in pieces}
            assert len(pieces) >= 5, (name, left, top, len(pieces))
            assert kinds & set(COLUMNS), (name, left, top, "nothing standing")
            assert kinds & set(RUBBLES), (name, left, top, "nothing spilled")


def test_the_pieces_are_props_and_they_are_taller_than_the_tile() -> None:
    """The whole reason they are not tiles.

    A column is three tiles tall and a fallen one is two tiles long.
    Neither fits in the grid, and neither repeats, which is what makes
    them props rather than terrain -- so the sizes are asserted, since a
    prop quietly redrawn at tile size would still load and still draw.
    """
    pygame.init()
    ts = config.TILE_SIZE
    for char in RUIN_PIECES + PALM_CHARS:
        tile = TILE_DEFS[char]
        assert tile.solid, char
        assert tile.prop is not None, char
        assert tile.under in (".", "⌖", "⩊"), (char, tile.under)

    for name, minimum in (("desert_column", (0, ts * 1.5)),
                          ("desert_column_fallen", (ts * 2, 0)),
                          ("desert_rubble", (ts, ts)),
                          ("desert_palm", (ts, ts * 2.5))):
        for path in _SPRITES[name]:
            image = pygame.image.load(str(config.ASSETS_DIR / "sprites" / path))
            assert image.get_width() >= minimum[0], (path, image.get_size())
            assert image.get_height() >= minimum[1], (path, image.get_size())

    # The three column heights are three different heights. The same one
    # repeated is a colonnade, which is a building still standing.
    heights = {
        pygame.image.load(
            str(config.ASSETS_DIR / "sprites" / path)).get_height()
        for path in _SPRITES["desert_column"]
    }
    assert len(heights) == 3, heights


def test_nothing_the_ruins_dropped_closed_a_way_through() -> None:
    """The dressing is scenery, and scenery may not change the map.

    Every piece is solid, so this is the failure that matters: one
    column in a doorway and the courtyard is sealed, or a ruin the
    player could walk into becomes one they can only walk around.
    """
    hub = _tilemap("desert_central")
    start = hub.spawn_points.get("player")
    ts = config.TILE_SIZE
    origin = next(
        (int(p[0]) // ts, int(p[1]) // ts)
        for kind, p in hub.object_spawns if kind.startswith("anchor:")
    ) if start is None else (int(start[0]) // ts, int(start[1]) // ts)
    seen = _safe_flood(hub, origin)
    mid_x, mid_y = hub.width_tiles // 2, hub.height_tiles // 2
    for cell in ((mid_x, 0), (mid_x, hub.height_tiles - 1),
                 (0, mid_y), (hub.width_tiles - 1, mid_y)):
        assert cell in seen, cell
    # ...and every ruin still has an inside the player can stand in.
    for left, top, width, height in RUINS:
        inside = [(x, y) for y in range(top + 1, top + height - 1)
                  for x in range(left + 1, left + width - 1)
                  if (x, y) in seen]
        assert inside, (left, top)


def test_every_palm_is_a_tree_rather_than_a_canopy_on_its_own() -> None:
    """Trunk, crown, and the two in the same place.

    The oasis used to have four clumps of overhead shade authored into
    it, three of which fell on sand instead of turf and were dropped --
    so what it actually had was two lonely tiles of canopy with nothing
    casting them. The check is therefore not that canopy exists but
    that each palm has some directly above it, within the rows the
    sprite's crown actually reaches.
    """
    tilemap = _tilemap("desert_oasis")
    palms = [(x, y) for y in range(tilemap.height_tiles)
             for x in range(tilemap.width_tiles)
             if tilemap.terrain_at(x, y) in PALM_CHARS]
    assert len(palms) >= PALM_COUNT - 3, len(palms)

    for x, y in palms:
        crown = [
            (x + dx, y - depth) for depth in CROWN_ROWS for dx in (-1, 0, 1)
            if 0 <= y - depth < tilemap.height_tiles
            and 0 <= x + dx < tilemap.width_tiles
        ]
        assert any(tilemap.terrain_at(*cell) in CANOPY_CHARS
                   for cell in crown), (x, y, "a trunk with no crown")

    # ...and they stand round the water rather than in a line beside it.
    cx, cy, rx, ry = POOL
    import math
    ring = [math.hypot((x - cx) / rx, (y - cy) / ry) for x, y in palms]
    assert min(ring) > 1.0, min(ring)          # none of them in the pool
    assert max(ring) - min(ring) < 0.6, (min(ring), max(ring))
    assert abs(sum(ring) / len(ring) - PALM_RING) < 0.35

    # The shade is still shade: drawn above Chuck, on walkable ground.
    for char in CANOPY_CHARS:
        assert not TILE_DEFS[char].solid
        assert TILE_DEFS[char].overhead == "palm_canopy"
        assert DESERT.overhead_char_to_terrain[char] == "palm_canopy"


def test_the_palms_do_not_stand_in_anything_that_was_already_there() -> None:
    """A palm is the least important thing on the map.

    It must never be the reason the ashtray moved or a tuft of
    cigarette grass went missing, so the oasis is checked to still have
    everything it had: the same spawn kinds, the same count of grass,
    and water nobody has planted a tree in.
    """
    directory, game, world = _world("desert_oasis")
    try:
        kinds = {kind for kind, _ in world.tilemap.object_spawns}
        assert kinds <= {"arrival:from_desert_central", "breakable_grass",
                         "anchor:desert_oasis_anchor"}, sorted(kinds)
        assert len(world.breakables) >= 8, len(world.breakables)
        palms = [p for p in world.props if p.kind == "desert_palm"]
        assert len(palms) >= 6, len(palms)
        for palm in palms:
            col, row = (palm._draw_x + palm._size[0] // 2) // config.TILE_SIZE, \
                (palm._bottom - 1) // config.TILE_SIZE
            assert world.tilemap.terrain_at(col, row) in PALM_CHARS, (col, row)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_camp_fires_are_bigger_than_the_tile_they_replaced() -> None:
    """The whole ask, measured against what it replaced.

    A fire was one sixteen-pixel tile, which made the ring of stones
    three pixels of rock and the fire inside it two. It is a prop now,
    standing in the middle of its own patch of scorched ground -- so
    both halves are checked: the sprite is wider than a tile, and the
    burn it stands on covers several of them.
    """
    pygame.init()
    ts = config.TILE_SIZE
    frames = _ANIMATED_SPRITES["desert_fire_pit"]
    assert len(frames) > 1, "the embers do not move"
    for path in frames:
        image = pygame.image.load(str(config.ASSETS_DIR / "sprites" / path))
        assert image.get_width() >= ts * 2, image.get_size()
        assert image.get_height() > ts, image.get_size()

    tilemap = _tilemap("desert_orc_camp")
    pits = [(x, y) for y in range(tilemap.height_tiles)
            for x in range(tilemap.width_tiles)
            if tilemap.terrain_at(x, y) == FIRE_PIT]
    assert len(pits) == len(FIRES), pits
    for x, y in pits:
        burn = [
            (bx, by)
            for by in range(y - int(BURN) - 1, y + int(BURN) + 2)
            for bx in range(x - int(BURN) - 1, x + int(BURN) + 2)
            if 0 <= by < tilemap.height_tiles and 0 <= bx < tilemap.width_tiles
            and tilemap.terrain_at(bx, by) == SCORCH
        ]
        assert len(burn) >= 8, (x, y, len(burn))
        # Wider than one tile in both directions, or it is a stain
        # rather than the ground a camp is built around.
        assert max(bx for bx, _ in burn) - min(bx for bx, _ in burn) >= 3
        assert max(by for _, by in burn) - min(by for _, by in burn) >= 2

    # The scorch is ground now, not a wall. It used to be the fire, and
    # solid, and an orc camp you cannot walk through is a maze.
    assert not TILE_DEFS[SCORCH].solid
    assert TILE_DEFS[FIRE_PIT].solid and TILE_DEFS[FIRE_PIT].under == SCORCH

    directory, game, world = _world("desert_orc_camp")
    try:
        assert len([p for p in world.props if p.kind == "desert_fire_pit"]) \
            == len(FIRES)
        seen = _safe_flood(world.tilemap, (
            int(world.player.x) // ts, int(world.player.y) // ts))
        for x, y in pits:
            assert any((x + dx, y + dy) in seen
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))), (x, y)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_orc_carries_an_axe_and_you_can_see_it() -> None:
    """Outside the silhouette, in every facing.

    A weapon drawn behind the arm holding it is a weapon nobody sees,
    which is the failure this is really guarding against -- the sprite
    would look armed in the source and unarmed on screen. So the steel
    is looked for in the columns of the frame the orc's own body does
    not occupy, and it has to be there in all three drawn facings.
    """
    pygame.init()
    sheet = pygame.image.load(
        str(config.ASSETS_DIR / "sprites" / "hazards" / "orc.png"))
    assert sheet.get_size() == (config.UNDEAD_FRAME_W * 3,
                                config.UNDEAD_FRAME_H)
    zombie = pygame.image.load(
        str(config.ASSETS_DIR / "sprites" / "hazards" / "zombie.png"))

    for index in range(3):
        left = index * config.UNDEAD_FRAME_W
        opaque = [
            (x, y)
            for x in range(config.UNDEAD_FRAME_W)
            for y in range(config.UNDEAD_FRAME_H)
            if sheet.get_at((left + x, y))[3] > 0
        ]
        # The body of every one of these sprites is drawn between x=1
        # and x=14; anything outside that is something it is holding.
        edges = [cell for cell in opaque if cell[0] in (0, 15)]
        assert edges, index

        # ...and what is out there is steel: much brighter and much
        # less green than the orc, which is green everywhere else.
        steel = [
            sheet.get_at((left + x, y))[:3] for x, y in edges
        ]
        assert any(pixel[2] >= pixel[1] and sum(pixel) > 300
                   for pixel in steel), (index, steel)

    # The orc is the only one of the pursuers holding anything: the
    # zombie it is built to be told apart from stayed empty-handed.
    zombie_edges = [
        (x, y) for x in (0, 15) for y in range(config.UNDEAD_FRAME_H)
        if zombie.get_at((x, y))[3] > 0
    ]
    assert not zombie_edges, zombie_edges


def test_the_camp_and_the_ruins_still_render() -> None:
    """Drawn, not just loaded.

    Every art bug in this region so far has been invisible in the
    source and obvious on screen, so each of the four dressed maps is
    put on a surface -- and checked for the one thing a screenshot
    would show instantly, that it is still a desert.
    """
    for checkpoint in ("desert_central_start", "desert_orc_camp",
                       "desert_oasis", "desert_undead_ruins"):
        directory, game, world = _world(checkpoint)
        try:
            surface = pygame.Surface((config.NATIVE_WIDTH,
                                      config.NATIVE_HEIGHT))
            for _ in range(4):
                world.update(0.1)
            world.draw(surface)
            pixels = [surface.get_at((x, y))[:3]
                      for x in range(0, config.NATIVE_WIDTH, 9)
                      for y in range(0, config.NATIVE_HEIGHT, 7)]
            warm = [p for p in pixels if p[0] >= p[2]]
            assert len(warm) > len(pixels) * 0.6, (checkpoint, len(warm))
        finally:
            game._shutdown()
            directory.cleanup()


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
    print("All desert dressing tests passed.")


if __name__ == "__main__":
    _run_all()
