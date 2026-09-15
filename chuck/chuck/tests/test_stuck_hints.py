"""Second words and descriptions that point a stuck player onward."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from src.systems.captain_confrontation import CAPTAIN_REQUIRED_FLAGS
from src.systems.dialogue import DialogueSystem


def test_the_seated_pirate_sends_chuck_round_the_whole_crew() -> None:
    # Every crew conversation gates the captain, so that is the hint.
    assert {"deck_concertina_met", "deck_cheering_met", "deck_dancer_met",
            "deck_jeffries_met", "pirate_chef_met"} <= CAPTAIN_REQUIRED_FLAGS
    assert DialogueSystem().get("seated_pirate_repeat") == [
        "You seem like a good listener, I bet all of the crew would love "
        "to bend your ear"]


def test_a_deck_pirate_asks_about_the_captains_cigarettes() -> None:
    # The captain's chest gates the captain too.
    assert "captain_chest_opened" in CAPTAIN_REQUIRED_FLAGS
    assert DialogueSystem().get("cheering_pirate_repeat") == [
        "You're not smoking the captain's cigarettes, are you!?"]


def test_the_cabin_suggests_going_inside() -> None:
    assert DialogueSystem().get("examine_tahuya_cabin") == [
        "A cabin in the woods. Maybe someone inside knows the way forward"]


def _press_at(game, scene, target) -> list[str]:
    """Face a target from below and read everything it says."""
    from src.scenes.dialogue_scene import DialogueScene

    x, y, w, h = target.interaction_bounds()
    scene.player.x = x + w / 2 - scene.player.width / 2
    scene.player.y = y + h + 1
    scene.player.facing = "up"
    game.input._actions_just_pressed.add("interact")
    game.scenes.update(1 / 60)
    game.input._actions_just_pressed.clear()
    top = game.scenes.current
    lines = list(top._lines) if isinstance(top, DialogueScene) else []
    while isinstance(game.scenes.current, DialogueScene):
        game.scenes.pop()
    return lines


def test_the_pantrys_plain_objects_point_at_the_cheese() -> None:
    import tempfile
    from pathlib import Path

    from src.core.game import Game

    hint = DialogueSystem().get("pantry_cheese_hint")
    assert hint == ["No cheese here, it's in the middle of the room and it "
                    "looks like it will be a leap of faith to reach"]
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("pantry_entry")
        kinds = {p.kind for p in scene.props}
        assert {"barrel", "crate", "pantry_sack_pile",
                "pantry_produce_basket", "cheese"} <= kinds
        for prop in scene.props:
            if prop.dialogue_id is None:
                continue
            wants = prop.kind != "cheese"
            assert scene._points_at_the_cheese(prop) is wants, prop.kind
        # The scratchables are for scratching, not for hints.
        for breakable in scene.breakables:
            assert not scene._points_at_the_cheese(breakable)
        # And through the real interact key: description, then the hint.
        crate = next(p for p in scene.props if p.kind == "crate")
        lines = _press_at(game, scene, crate)
        assert lines == scene.dialogue.get("examine_crate") + hint
    finally:
        game._shutdown()
        directory.cleanup()
    # Nowhere else.
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint("waterdeep_start")
        assert not any(scene._points_at_the_cheese(p) for p in scene.props)
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_path_on_chult_3_runs_up_to_the_tunnel_mouth() -> None:
    from src.core import config
    from src.world.tilemap import TileMap

    tilemap = TileMap(config.MAPS_DIR / "chult_run.txt")
    # The tunnel under the fallen log starts at column 29 on row 2; the
    # trail that climbs rows 5-3 now meets it, and goes no further.
    assert tilemap.terrain_at(29, 2) == "_"
    assert tilemap.terrain_at(28, 2) == "'" and tilemap.terrain_at(27, 2) == "'"
    assert tilemap.terrain_at(26, 2) == "."
    trail = [(c, r) for r in range(tilemap.height_tiles)
             for c in range(tilemap.width_tiles)
             if tilemap.terrain_at(c, r) == "'"]
    assert len(trail) == 8


def test_the_feywilds_plain_flowers_say_they_do_nothing() -> None:
    assert DialogueSystem().get("examine_feywild_spiral") == [
        "A very large flower. Doesn't seem like it does anything, unlike "
        "those other flowers"]


def test_the_homeless_man_points_down_the_road_to_the_sewer() -> None:
    assert DialogueSystem().get("homeless_man_repeat") == [
        "The street runs out a few blocks on. Only way on from there is "
        "down, buddy."]


def test_bobert_has_a_neighbour_on_the_return() -> None:
    import tempfile
    from pathlib import Path

    from src.core.game import Game
    from src.systems.checkpoints import (
        DESERT_ENTRY_FLAGS, WATERDEEP_RETURN_FLAG)

    dialogue = DialogueSystem()
    assert dialogue.get("bobert_neighbour") == [
        "You're back! Bobert's been moping in his barrel all week! I'm sure "
        "he's happy to see you"]
    assert dialogue.get("bobert_neighbour_repeat") == [
        "yep...", "... I'm still unemployed"]
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        scene = game.checkpoints.load_checkpoint(
            "waterdeep_finale",
            progress_flags=set(DESERT_ENTRY_FLAGS) | {WATERDEEP_RETURN_FLAG})
        bobert = next(p for p in scene.props
                      if p.kind.startswith("bobert_barrel"))
        bx, by, bw, bh = bobert.interaction_bounds()
        centre = (bx + bw / 2, by + bh)
        nearest = min(scene.npcs, key=lambda n: (
            (n.x + n.width / 2 - centre[0]) ** 2
            + (n.y + n.height / 2 - centre[1]) ** 2))
        assert nearest.dialogue_id == "bobert_neighbour"
        first = nearest.interact(scene.player)
        assert scene._second_word(nearest, first) == "bobert_neighbour"
        assert scene._second_word(nearest, first) == \
            "bobert_neighbour_repeat"
    finally:
        game._shutdown()
        directory.cleanup()
