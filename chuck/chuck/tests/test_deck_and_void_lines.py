"""Four small things: a smaller wheel, a warning, a mast, and the void.

The wheel is held to the trace rather than to a pixel grid, because it
is now resampled down from it. The three lines are held to where they
appear and to the fact that they fit the panel they appear in -- a line
that wraps past three rows is a line the player reads half of.
"""

import json
import os
from pathlib import Path
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.prop import MUTE_PROPS_AT, PROP_DIALOGUE_AT
from src.scenes.world_scene import TERRAIN_DIALOGUE, WorldScene
from src.ui.bitmap_font import ADVANCE, GLYPH_ORDER
from src.ui.dialogue_box import MARGIN, PAD
from src.ui.text import wrap_text

DECK = "ship_exterior_deck"
# What the dialogue panel holds: three rows of text, and this wide.
PANEL_ROWS = 3
PANEL_W = config.NATIVE_WIDTH - 2 * MARGIN - 2 * PAD


def _dialogue(name):
    path = Path("data/dialogue") / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(line: str) -> int:
    return len(wrap_text(line, PANEL_W,
                         lambda s: max(0, len(s) * ADVANCE - 1)))


def _fits(lines) -> None:
    for line in lines:
        assert _rows(line) <= PANEL_ROWS, (_rows(line), line)
        for char in line:
            assert char in GLYPH_ORDER, char


# ----------------------------------------------------------------------
# The wheel
# ----------------------------------------------------------------------
def test_the_helm_came_down_from_the_trace_and_kept_its_angle() -> None:
    """Smaller, but still the traced wheel rather than a new drawing."""
    from PIL import Image

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
    import generate_ship_props as props

    grid = props.HELM.strip().splitlines()
    assert len(grid) == 66 and {len(row) for row in grid} == {46}
    assert 0.7 < props.HELM_SCALE < 1.0

    art = Image.open(
        config.SPRITES_DIR / "objects" / "ship_helm.png").convert("RGBA")
    assert art.size == (round(46 * props.HELM_SCALE),
                        round(66 * props.HELM_SCALE))
    assert art.size == (39, 56)
    # Smaller than it was, and still taller than it is wide, which is
    # the angle the trace exists to keep.
    assert art.width < 46 and art.height < 66
    assert art.height > art.width * 1.4

    # Every pixel is still one of the nine colours of the grid: a
    # resample that left its own colours behind would not be pixel art.
    allowed = set(props.HELM_PALETTE.values()) | {props.TRANSPARENT}
    seen = {art.getpixel((x, y))
            for y in range(art.height) for x in range(art.width)}
    assert seen <= allowed, seen - allowed
    # The brass hub survived the shrink: it is the centre of the wheel.
    brass = {props.HELM_PALETTE["G"], props.HELM_PALETTE["g"]}
    assert sum(1 for y in range(art.height) for x in range(art.width)
               if art.getpixel((x, y)) in brass) > 40


def test_the_deck_still_stands_the_smaller_wheel_where_it_was() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
        helm = next(p for p in scene.props if p.kind == "ship_helm")
        assert helm._size == (39, 56)
    finally:
        game._shutdown()


# ----------------------------------------------------------------------
# The pirate
# ----------------------------------------------------------------------
def test_a_deck_pirate_warns_about_the_captains_quarters() -> None:
    """On the second word and after, not on the first."""
    deck = _dialogue(DECK)
    warning = "Don't let the captain catch you sniffing around in his quarters!"
    repeats = [key for key, lines in deck.items()
               if key.endswith("_repeat") and warning in lines]
    assert repeats == ["cheering_pirate_repeat"]
    # Said by the pirate who already keeps an eye on the captain's
    # things, so it is the same character talking.
    assert any("captain" in line for line in deck["cheering_pirate_first"]
               + deck["cheering_pirate_repeat"])
    # And never on a first meeting, which is where the mad Jeffries
    # joke lives.
    assert all(warning not in lines for key, lines in deck.items()
               if key.endswith("_first"))
    _fits(deck["cheering_pirate_repeat"])


def test_that_pirate_is_really_on_the_deck_to_say_it() -> None:
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
        pirates = [npc for npc in scene.npcs
                   if getattr(npc, "dialogue_id", "").startswith(
                       "cheering_pirate")]
        assert len(pirates) == 1
    finally:
        game._shutdown()


# ----------------------------------------------------------------------
# The mast
# ----------------------------------------------------------------------
def test_the_east_mast_explains_the_rig_and_the_west_one_says_nothing() -> None:
    """Forward is east here, and the fore is the mast that stands there.

    The bowsprit runs east off the bow and the helm stands at the far
    west, so the east mast is the one forward of the other. The west
    mast is Jeffries' -- see the test below.
    """
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
        masts = sorted((p for p in scene.props
                        if p.kind == "ship_mast_sail"),
                       key=lambda p: p._draw_x)
        assert len(masts) == 2
        west, east = masts
        assert east.dialogue_id == "examine_ship_foremast"
        assert west.dialogue_id is None
        assert PROP_DIALOGUE_AT[("ship_mast_sail", 42, 22)] == east.dialogue_id
        assert ("ship_mast_sail", 21, 22) in MUTE_PROPS_AT

        # The ship agrees. Compared by the tile each prop is anchored
        # to, not by where its art starts: a mast sprite is fourteen
        # tiles wide and a helm is three, so their left edges say
        # nothing about which is further forward.
        columns = {kind: col for kind, col, _row in scene.tilemap.prop_tiles
                   if kind in ("ship_helm", "ship_bowsprit")}
        masts = sorted(col for kind, col, _row in scene.tilemap.prop_tiles
                       if kind == "ship_mast_sail")
        assert columns["ship_helm"] < masts[0] < masts[1]             < columns["ship_bowsprit"]
        assert masts == [21, 42]
    finally:
        game._shutdown()


def test_the_west_mast_is_jeffries_and_nothing_else() -> None:
    """He is roped to it, so that patch of deck is his conversation.

    A mast sprite is fourteen tiles wide. Left with a line of its own,
    the west mast answered from well outside the reach of the man tied
    to it, and the note about spars talked over him.
    """
    game = Game()
    try:
        scene = game.checkpoints.load_checkpoint("ship_exterior_deck")
        west = min((p for p in scene.props if p.kind == "ship_mast_sail"),
                   key=lambda p: p._draw_x)
        ts = config.TILE_SIZE
        answers, jeffries = set(), set()
        for row in range(14, 30):
            for col in range(15, 29):
                if scene.tilemap.is_solid(col, row):
                    continue
                for facing in ("up", "down", "left", "right"):
                    _stand(scene, col, row, facing)
                    target = scene._interactable_in_range()
                    if target is west:
                        answers.add((col, row))
                    if getattr(target, "dialogue_id", "") == "jeffries_first":
                        jeffries.add((col, row))
        assert answers == set(), sorted(answers)
        # And he is still reachable all round the mast he is tied to.
        assert len(jeffries) > 10
    finally:
        game._shutdown()


def test_the_mast_line_is_the_rig_explained_and_it_fits_the_panel() -> None:
    lines = _dialogue("examine")["examine_ship_foremast"]
    assert lines[0].startswith("The foremast")
    assert "mizzen" in lines[1] and "ketch or yawl" in lines[1]
    assert lines[-1].endswith("fore and main.")
    # Three panels of it, none of them overflowing.
    assert len(lines) == 3
    _fits(lines)


def test_a_prop_position_override_only_touches_that_one_prop() -> None:
    """The mechanism, not the mast: the same kind elsewhere is unchanged."""
    from src.entities.prop import (
        MUTE_PROPS, PROP_DIALOGUE, examine_line_id)

    for (kind, _col, _row), line in PROP_DIALOGUE_AT.items():
        # An override is for two of the same thing with different things
        # to say, so the kind must still have a line of its own to fall
        # back to everywhere else.
        assert PROP_DIALOGUE.get(kind) or examine_line_id(kind)
        assert line in _dialogue("examine") or line in PROP_DIALOGUE.values()
    for kind, _col, _row in MUTE_PROPS_AT:
        assert kind not in MUTE_PROPS, (
            f"{kind} is already silent everywhere; the position is noise")


# ----------------------------------------------------------------------
# The Astral Sea
# ----------------------------------------------------------------------
def test_the_astral_sea_is_the_one_ground_that_answers() -> None:
    assert TERRAIN_DIALOGUE == {"V": "examine_astral_void"}
    lines = _dialogue("examine")["examine_astral_void"]
    assert lines == [
        "The astral sea, the space between worlds ... what's it doing here?"]
    _fits(lines)


def test_chuck_can_examine_the_void_from_the_edge_of_it() -> None:
    """Facing it answers; facing away does not."""
    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            game.scenes.replace(WorldScene(game, "sewer"))
            scene = game.scenes.current
            col, row = _void_edge(scene.tilemap)
            _stand(scene, col, row, "right")
            target = scene._interactable_in_range()
            assert target is not None
            assert target.dialogue_id == "examine_astral_void"
            assert scene.dialogue.get(target.dialogue_id)

            scene.player.facing = "left"
            assert scene._interactable_in_range() is None
        finally:
            game._shutdown()


def test_anything_at_all_answers_before_the_ground_does() -> None:
    """A barrel at the edge of the void is still a barrel.

    The ground is the last thing asked, so putting a line on seventeen
    thousand tiles cannot talk over anything that was already there.
    """
    from src.entities.prop import Prop

    with tempfile.TemporaryDirectory() as directory:
        game = Game(save_path=Path(directory) / "save.json")
        try:
            game.scenes.replace(WorldScene(game, "sewer"))
            scene = game.scenes.current
            col, row = _void_edge(scene.tilemap)
            _stand(scene, col, row, "right")
            assert scene._interactable_in_range().dialogue_id                 == "examine_astral_void"

            barrel = Prop("bobert_barrel", col + 1, row, game.assets)
            scene.props.append(barrel)
            assert scene._interactable_in_range() is barrel
        finally:
            game._shutdown()


def test_the_terrain_stand_in_carries_a_line_and_nothing_else() -> None:
    """It must not look like a prop to the rest of the interact path."""
    from src.scenes.world_scene import _TerrainTarget

    target = _TerrainTarget("examine_astral_void")
    assert target.dialogue_id == "examine_astral_void"
    assert not hasattr(target, "choice_id")
    assert not hasattr(target, "interact")
    assert not hasattr(target, "hitbox")
    assert not hasattr(target, "kind")


def _void_edge(tilemap) -> tuple[int, int]:
    """A tile Chuck can stand on with the Astral Sea one step east."""
    return next(
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) != "V"
        and not tilemap.is_solid(col, row)
        and tilemap.terrain_at(col + 1, row) == "V")


def _stand(scene, col: int, row: int, facing: str) -> None:
    ts = config.TILE_SIZE
    scene.player.x = col * ts + (ts - scene.player.width) / 2
    scene.player.y = row * ts + (ts - scene.player.height) / 2
    scene.player.facing = facing


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
    print("All deck and void line tests passed.")


if __name__ == "__main__":
    _run_all()
