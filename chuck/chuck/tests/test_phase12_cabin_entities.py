"""Phase 12's four seated light entities and exact durable conversations."""

import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.core.game import Game
from src.entities.cabin_light_entity import CabinLightEntity, FRAME_TIME
from src.world.tilemap import TileMap


MAP_NAME = "tahuya_cabin_interior"
EXPECTED_DIALOGUE = {
    "cabin_entity_big_couch": "ꋖꁝꌅꊿꁲꋖꊿꂵꑀ ꃳꁲꏳꈵ",
    "cabin_entity_couch":
        "i̵̖s̵̻̆͗i͙͢t̞ꁲꃔꏳh̵̨i̲͖̣͋c̘̆ͬḩ̜̣͙t̝ͬͣi̽?",
    "cabin_entity_chair_north":
        "l̛͠ơ̶̧͟g̸̶̀͘c҉a͢b͏̸̵̴̵į̷̴̕͜n͘҉ í̸s̵̡͜͏͟͢ "
        "t̶̡́͡͡͡h͏̡̕o̸͜͞ņ̶̸̸̴͟l̶̷̨͘y͢͠҉̧w̢̕͜͜à̵́͡͝y҉",
    "cabin_entity_chair_south":
        "į̷̴̕͜n͘҉ í̸s̵̡͜͏͟͢ꋖꊿl̶̷̨͘y͢͠҉̧w̢̕͜͜t̝ͬͣ",
}
EXPECTED_FLAGS = {
    "cabin_entity_big_couch_spoken",
    "cabin_entity_couch_spoken",
    "cabin_entity_chair_north_spoken",
    "cabin_entity_chair_south_spoken",
}


def _game():
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    return directory, game


def test_exact_dialogue_is_preserved_and_renderable() -> None:
    path = config.DIALOGUE_DIR / "cabin.json"
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    assert {key: lines[0] for key, lines in data.items()} == EXPECTED_DIALOGUE

    directory, game = _game()
    try:
        font = game.assets.bitmap_font()
        for line in EXPECTED_DIALOGUE.values():
            rendered = font.render(line)
            assert rendered.get_width() > 0
            assert rendered.get_bounding_rect().width > 0
    finally:
        game._shutdown()
        directory.cleanup()


def test_exactly_four_entities_occupy_the_authored_seats() -> None:
    tilemap = TileMap(config.MAPS_DIR / f"{MAP_NAME}.txt")
    spawns = {
        kind: (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE))
        for kind, (x, y) in tilemap.object_spawns
        if kind.startswith("cabin_light:")
    }
    assert len(spawns) == 4
    # Two on the couches under the north wall, and the west-facing pair
    # flush against the east wall.
    assert set(spawns.values()) == {(5, 4), (16, 4), (18, 7), (18, 10)}


def test_entities_use_offset_animation_and_durable_idempotent_flags() -> None:
    directory, game = _game()
    try:
        world = game.checkpoints.load_checkpoint("tahuya_interior")
        entities = [npc for npc in world.npcs
                    if isinstance(npc, CabinLightEntity)]
        assert len(entities) == 4
        assert sorted(entity.facing for entity in entities) == [
            "south", "south", "west", "west"
        ]
        assert {entity.progress_flag for entity in entities} == EXPECTED_FLAGS
        phases = {
            int(entity._animation_t / FRAME_TIME) % len(entity._frames)
            for entity in entities
        }
        assert len(phases) == 4
        assert all(len(entity._frames) == 8 for entity in entities)

        for entity in entities:
            expected = entity.dialogue_id
            assert entity.interact(world.player) == expected
            assert entity.interact(world.player) == expected
        assert EXPECTED_FLAGS <= game.progress.flags

        # The existing save/checkpoint path carries all four flags without a
        # cabin-specific format or duplicate all-spoken flag.
        assert game.checkpoints.activate_checkpoint(
            "tahuya_interior_anchor", world.sanity.current
        )
        continued = game.checkpoints.continue_game()
        assert EXPECTED_FLAGS <= game.progress.flags
        assert len([npc for npc in continued.npcs
                    if isinstance(npc, CabinLightEntity)]) == 4
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
                print(f"  FAIL  {name}: {exc!r}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All Cabin light-entity tests passed.")


if __name__ == "__main__":
    _run_all()
