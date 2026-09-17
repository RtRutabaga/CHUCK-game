"""Phase 7 exterior-deck foundation, motion, route, and checkpoint."""

import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.systems.checkpoints import CHECKPOINT_BY_ID
from src.systems.ship_motion import deck_rock_offset
from src.world.tilemap import TileMap
from src.world.tileset_layout import tileset_for
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


MAP_NAME = "ship_exterior_deck"


def _map() -> TileMap:
    return TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")


def test_exterior_is_a_large_reference_led_ship_in_animated_sea() -> None:
    tilemap = _map()
    assert (tilemap.width_tiles, tilemap.height_tiles) == (64, 44)
    masts = [(col, row) for kind, col, row in tilemap.prop_tiles
             if kind == "ship_mast_sail"]
    assert masts == [(21, 22), (42, 22)]
    helms = [(col, row) for kind, col, row in tilemap.prop_tiles
             if kind == "ship_helm"]
    assert helms == [(17, 22)]
    assert {row for _col, row in helms + masts} == {22}
    bowsprits = [(col, row) for kind, col, row in tilemap.prop_tiles
                 if kind == "ship_bowsprit"]
    assert bowsprits == [(55, 22)]
    deck_rows = [row for row, tiles in enumerate(tilemap._grid)
                 if "=" in tiles]
    assert (min(deck_rows), max(deck_rows)) == (12, 31)
    assert sum(row.count("~") for row in tilemap._grid) > 1200
    assert tileset_for(MAP_NAME).char_to_terrain["~"] == "ship_ocean"
    assert AREA_MUSIC[MAP_NAME] == "ship_shanty.wav"


def test_deck_has_one_checkpoint_and_uses_the_shared_loader() -> None:
    tilemap = _map()
    kinds = [kind for kind, _position in tilemap.object_spawns]
    assert kinds.count("arrival:from_crew_quarters") == 1
    assert kinds.count("anchor:ship_exterior_anchor") == 1
    assert sum(kind.startswith("anchor:") for kind in kinds) == 1

    entry = CHECKPOINT_BY_ID["ship_exterior_deck"]
    assert entry.display_name == "Ship Exterior Deck"
    assert entry.runtime_entry and entry.development_visible
    anchor = CHECKPOINT_BY_ID["ship_exterior_anchor"]
    assert anchor.saveable and not anchor.development_visible

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
        assert scene.map_name == MAP_NAME
        assert len(scene.anchors) == 1
        mast_sizes = [prop._size for prop in scene.props
                      if prop.kind == "ship_mast_sail"]
        assert mast_sizes == [(224, 240), (224, 240)]
        helm = next(prop for prop in scene.props if prop.kind == "ship_helm")
        assert helm._size == (39, 56)
        bowsprit = next(prop for prop in scene.props
                        if prop.kind == "ship_bowsprit")
        assert bowsprit._size == (400, 96)
    finally:
        game._shutdown()


def test_crew_ladder_is_reversible() -> None:
    outward = AREA_WALK_EXITS[("ship_crew_quarters", "ℓ")]
    assert (outward.destination, outward.arrival) == (
        MAP_NAME, "from_crew_quarters"
    )
    assert outward.confirmation == "Climb up ladder?"
    inward = AREA_WALK_EXITS[(MAP_NAME, "ℓ")]
    assert (inward.destination, inward.arrival) == (
        "ship_crew_quarters", "from_exterior_deck"
    )
    assert inward.confirmation == "Climb down ladder?"
    assert AREA_WALK_EXITS[("ship_crew_quarters", "ɭ")] == outward
    assert AREA_WALK_EXITS[(MAP_NAME, "ɭ")] == inward
    crew = TileMap(config.MAPS_DIR / "ship_crew_quarters.txt")
    assert any(kind == "arrival:from_exterior_deck"
               for kind, _position in crew.object_spawns)

    game = Game()
    try:
        assert game.checkpoints.entry_checkpoint_id(
            MAP_NAME, "from_crew_quarters"
        ) == "ship_exterior_deck"
    finally:
        game._shutdown()


def test_every_ship_ladder_is_one_continuous_human_height_structure() -> None:
    for map_name in (
        "ship_deck", "ship_lower_hold",
        "ship_crew_quarters", "ship_exterior_deck",
    ):
        tilemap = TileMap(config.MAPS_DIR / f"{map_name}.txt")
        tops = [
            (col, row)
            for row, line in enumerate(tilemap._grid)
            for col, char in enumerate(line)
            if char == "ℓ"
        ]
        bottoms = [
            (col, row)
            for row, line in enumerate(tilemap._grid)
            for col, char in enumerate(line)
            if char == "ɭ"
        ]
        assert len(tops) == len(bottoms) == 1
        col, row = tops[0]
        assert bottoms[0] == (col, row + 1)
        assert AREA_WALK_EXITS[(map_name, "ɭ")] == (
            AREA_WALK_EXITS[(map_name, "ℓ")]
        )


def test_exterior_ashtray_persists_and_continues_on_the_deck() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "save.json"
        game = Game(save_path=path)
        try:
            scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
            assert game.checkpoints.activate_checkpoint(
                "ship_exterior_anchor", scene.sanity.current
            )
        finally:
            game._shutdown()

        resumed = Game(save_path=path)
        try:
            scene = resumed.checkpoints.continue_game()
            assert scene.map_name == MAP_NAME
            assert resumed.active_checkpoint_id == "ship_exterior_anchor"
        finally:
            resumed._shutdown()


def test_deck_rock_is_subtle_and_returns_to_its_shanty_phase_origin() -> None:
    samples = [deck_rock_offset(i / 20) for i in range(100)]
    assert all(abs(x) <= 1 and abs(y) <= 1 for x, y in samples)
    assert len(set(samples)) > 1
    period = (60.0 / 126.0) * 8.0
    assert deck_rock_offset(0.0) == deck_rock_offset(period)


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
    print("All Phase 7 exterior-deck tests passed.")


if __name__ == "__main__":
    _run_all()


def test_each_mast_carries_three_yards_of_sail() -> None:
    """A square rig, not one sheet of canvas.

    One enormous sail per mast reads as a sail but not as a sailing
    ship. A square rigger carries a course, a topsail and a topgallant
    on separate yards up the same mast, each smaller than the one below
    it, and from above that stack of three shrinking rectangles is the
    whole silhouette of the thing.
    """
    from PIL import Image

    from src.entities.prop import _SPRITES

    art = Image.open(config.SPRITES_DIR / _SPRITES["ship_mast_sail"])
    art = art.convert("RGBA")
    canvas = {(218, 202, 151), (239, 225, 174), (161, 145, 102)}
    # Rows of the sprite that have canvas in them, grouped into the runs
    # they fall into: three runs, with clear mast between them.
    lit = [row for row in range(art.height)
           if any(art.getpixel((col, row))[:3] in canvas
                  for col in range(art.width))]
    runs = []
    for row in lit:
        if runs and row == runs[-1][-1] + 1:
            runs[-1].append(row)
        else:
            runs.append([row])
    assert len(runs) == 3, [(r[0], r[-1]) for r in runs]

    # ...and each one is wider than the one above it.
    widths = []
    for run in runs:
        middle = run[len(run) // 2]
        cols = [col for col in range(art.width)
                if art.getpixel((col, middle))[:3] in canvas]
        widths.append(max(cols) - min(cols))
    assert widths[0] < widths[1] < widths[2], widths

    # The mast stands in FRONT of its own sails, unbroken from the head
    # of the rig to the deck: drawn behind them it survives only in the
    # gaps between the yards, and a mast that comes and goes behind the
    # cloth reads as three boards rather than one pole carrying sails.
    wood = {(63, 42, 29), (112, 74, 43), (151, 102, 57)}
    spar = [row for row in range(art.height)
            if any(art.getpixel((col, row))[:3] in wood
                   for col in range(105, 120))]
    assert spar == list(range(spar[0], spar[-1] + 1)), "the mast is broken"
    assert spar[0] <= runs[0][0], (spar[0], runs[0][0])
    assert spar[-1] > runs[-1][-1], (spar[-1], runs[-1][-1])
    # ...and in the middle of each sail it is wood, not canvas.
    for run in runs:
        middle = run[len(run) // 2]
        assert art.getpixel((110, middle))[:3] in wood, middle


def test_the_lowest_yard_hangs_clear_of_the_crews_heads() -> None:
    """Canvas over the deck, not resting on the people standing on it.

    Jeffries works at the foot of the forward mast. A course whose foot
    comes down level with his head is a sail lying on the crew, and the
    bare stretch of mast under it is most of what makes the rig read as
    tall rather than as bunting.
    """
    from PIL import Image

    from src.core import config

    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
        jeffries = next(npc for npc in scene.npcs
                        if "jeffries" in str(getattr(npc, "dialogue_id", "")))
        head = jeffries.hitbox.bottom - config.NPC_FRAME_H
        mast = min((prop for prop in scene.props
                    if prop.kind == "ship_mast_sail"),
                   key=lambda prop: prop._draw_x)
        art = Image.open(
            config.SPRITES_DIR / "objects" / "ship_mast_sail.png").convert("RGBA")
        canvas = {(218, 202, 151), (239, 225, 174), (161, 145, 102)}
        lowest = max(row for row in range(art.height)
                     if any(art.getpixel((col, row))[:3] in canvas
                            for col in range(art.width)))
        assert mast._draw_y + lowest < head - 12, (
            mast._draw_y + lowest, head)
        # ...and clear of the helm standing forward of the mast, which
        # is a wheel with spokes: half of one is a broken wheel.
        helm = next(prop for prop in scene.props
                    if prop.kind == "ship_helm")
        assert mast._draw_y + lowest < helm._draw_y, (
            mast._draw_y + lowest, helm._draw_y)
    finally:
        game._shutdown()


def test_the_helm_is_the_traced_wheel_rather_than_a_drawn_circle() -> None:
    """The wheel at its own angle, brought down from the trace.

    It is seen from above and a little to starboard: an upright ellipse
    taller than it is wide, the handles swung round it, and the pedestal
    standing behind and to one side. A circle-and-spokes routine does
    not arrive at that, so the art is a traced grid, resampled down from
    it and put back on its own nine colours. This holds the render to
    the trace it came from; `tests/test_deck_and_void_lines.py` holds
    the shrink itself.
    """
    import sys

    from PIL import Image

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
    import generate_ship_props as props

    rows = props.HELM.strip().splitlines()
    assert len(rows) == 66 and {len(row) for row in rows} == {46}
    # The grid is still the whole of the art: rendered at full size it
    # is the trace, pixel for pixel.
    full = props.helm_grid()
    assert full.size == (46, 66)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            want = props.HELM_PALETTE.get(char, props.TRANSPARENT)
            assert full.getpixel((x, y)) == want, (x, y, char)

    art = Image.open(
        config.SPRITES_DIR / "objects" / "ship_helm.png").convert("RGBA")
    assert art.size == (39, 56)
    # Taller than wide: that is the angle, not a decoration of it.
    assert art.height > art.width * 1.4

    # The brass hub sits in the wheel, well above the sprite's middle --
    # the bottom third is pedestal.
    brass = {props.HELM_PALETTE["G"][:3], props.HELM_PALETTE["g"][:3]}
    hub = [(x, y) for y in range(art.height) for x in range(art.width)
           if art.getpixel((x, y))[:3] in brass]
    assert len(hub) > 30, len(hub)
    # The bulk of the brass is the hub, and the hub is up in the wheel:
    # the bottom third of the sprite is pedestal. A few stray bright
    # pixels elsewhere are the light on the rim, so this weighs the
    # whole of it rather than taking the lowest one.
    assert sum(y for _x, y in hub) / len(hub) < art.height * 0.5
    # ...and the handles reach further out than anything below them, so
    # the widest part of the silhouette is the wheel and not the base.
    def width_at(row: int) -> int:
        cols = [x for x in range(art.width) if art.getpixel((x, row))[3]]
        return max(cols) - min(cols) + 1 if cols else 0

    wheel = max(width_at(row) for row in range(0, int(art.height * 0.62)))
    base = max(width_at(row) for row in range(int(art.height * 0.75),
                                              art.height))
    assert wheel > base, (wheel, base)
