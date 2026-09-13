"""Waterdeep's harbour dressing, held to the rules of the vantage.

The pier shows its front only where water lies south of it and a shadow
only where water lies east of it; posts stand on edges that face the
camera or the open water; the boat lies against a pier face with its
line to a post; nothing solid cuts a route; and the return swaps every
kind with a midday twin -- the lamps go out.
"""

import os
from pathlib import Path
import sys
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import waterdeep_harbour_dressing as harbour  # noqa: E402
from src.core.game import Game  # noqa: E402
from src.entities.prop import MUTE_PROPS, midday_variant  # noqa: E402
from src.systems.dialogue import DialogueSystem  # noqa: E402
from src.entities.prop import examine_line_id  # noqa: E402


def _grid():
    return harbour._read()[2]


def _undressed(grid):
    """The shipped map with only the pier's derived edges taken back off."""
    return [[harbour.WATER if char in harbour.EDGES else char
             for char in row] for row in grid]


def test_every_pier_edge_is_what_the_camera_would_see_there() -> None:
    grid = _grid()
    bare = _undressed(grid)
    faces = 0
    for row, line in enumerate(grid):
        for col, char in enumerate(line):
            if char in harbour.EDGES or char == harbour.WATER:
                expected = harbour.edge_for(bare, col, row) or harbour.WATER
                assert char == expected, (col, row, char, expected)
                faces += char in (harbour.PIER_FACE, harbour.PIER_FACE_SHADOW)
    assert faces >= 20
    # Nothing is drawn on the pier's north or west sides: water with planks
    # only south or east of it stays plain water.
    for row, line in enumerate(bare):
        for col, char in enumerate(line):
            if char != harbour.WATER:
                continue
            north = row > 0 and harbour._is_deck(bare[row - 1][col])
            west = col > 0 and harbour._is_deck(bare[row][col - 1])
            north_west = (row > 0 and col > 0
                          and harbour._is_deck(bare[row - 1][col - 1]))
            if not (north or west or north_west):
                assert grid[row][col] == harbour.WATER, (col, row)


def test_posts_stand_on_visible_edges_and_the_boat_is_moored_to_one() -> None:
    grid = _grid()
    for col, row in harbour.BOLLARDS_SOUTH:
        assert grid[row][col] == harbour.BOLLARD
        assert grid[row + 1][col] in (harbour.PIER_FACE,
                                      harbour.PIER_FACE_SHADOW)
    for col, row in harbour.BOLLARDS_WEST:
        assert grid[row][col] == harbour.BOLLARD_WEST
    for col, row in harbour.BOATS:
        assert grid[row][col] == harbour.ROWBOAT
        assert grid[row - 1][col] in (harbour.PIER_FACE,
                                      harbour.PIER_FACE_SHADOW)
        assert grid[row - 2][col] == harbour.BOLLARD


def test_nothing_placed_cuts_a_route() -> None:
    from src.world.tilemap import TILE_DEFS

    grid = _grid()
    placed_solid = sum(
        1 for line in grid for char in line
        if char in harbour.DRESSING - harbour.EDGES
        and TILE_DEFS[char].solid and TILE_DEFS[char].under in ("=", ","))
    restored = [[TILE_DEFS[char].under
                 if char in harbour.DRESSING and TILE_DEFS[char].under
                 else char for char in line] for line in grid]
    before = harbour.reachable(restored)
    after = harbour.reachable(grid)
    assert len(after) == len(before) - placed_solid


def test_the_return_puts_the_lamps_out_and_retints_the_pier() -> None:
    assert midday_variant("waterdeep_lamp") == "waterdeep_lamp_midday"
    assert midday_variant("pier_face") == "pier_face_midday"
    assert midday_variant("shop_sign_bread") == "shop_sign_bread"
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        opening = game.checkpoints.load_checkpoint("waterdeep_start")
        kinds = {prop.kind for prop in opening.props}
        assert {"waterdeep_lamp", "pier_face", "harbour_rowboat"} <= kinds
        assert not any(kind.endswith("_midday") for kind in kinds)
        game.progress.enable("waterdeep_returned")
        finale = game.checkpoints.load_checkpoint(
            "waterdeep_finale", progress_flags=game.progress.flags)
        kinds = {prop.kind for prop in finale.props}
        assert {"waterdeep_lamp_midday", "pier_face_midday",
                "harbour_rowboat_midday"} <= kinds
        assert "waterdeep_lamp" not in kinds
        plaza = game.checkpoints.load_checkpoint(
            "waterdeep_plaza_finale", progress_flags=game.progress.flags)
        assert "waterdeep_lamp_midday" in {prop.kind for prop in plaza.props}
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_pier_is_mute_and_the_rest_answers_e() -> None:
    dialogue = DialogueSystem()
    for kind in ("pier_face", "pier_shadow_midday", "pier_corner"):
        assert kind in MUTE_PROPS
    for kind in ("harbour_bollard", "harbour_bollard_west", "harbour_rowboat",
                 "harbour_rowboat_midday", "waterdeep_lamp",
                 "waterdeep_lamp_midday", "shop_sign_bread", "shop_sign_fish",
                 "shop_sign_barrel", "shop_sign_anvil", "shop_sign_potion",
                 "window_box", "washing_line_6", "washing_line_4"):
        assert kind not in MUTE_PROPS
        assert dialogue.get(examine_line_id(kind)), kind
