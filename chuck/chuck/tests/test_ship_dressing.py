"""The ship's below-decks and deck dressing.

The captain's study gets its bookcases and desk and loses the hammock;
the galley gets its pot and block; rope and lashed cargo lie about the
hold, the crew quarters and the deck. None of it is a chest -- the
captain's is the only one aboard -- and none of it talks.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.entities.prop import MUTE_PROPS, Prop
from src.world.tilemap import TILE_DEFS


SHIP_MAPS = ("ship_deck", "ship_exterior_deck", "ship_lower_hold",
             "ship_galley", "ship_crew_quarters", "ship_captain_cabin")
DRESSING = {"ship_bookshelf", "ship_writing_desk", "ship_butcher_block",
            "ship_stew_pot", "ship_rope_coil", "ship_cargo_stack"}


def _answers_e(kinds) -> None:
    """Each kind has its examine line and is not in the mute scatter."""
    from src.entities.prop import examine_line_id
    from src.systems.dialogue import DialogueSystem

    dialogue = DialogueSystem()
    for kind in kinds:
        assert kind not in MUTE_PROPS, kind
        assert dialogue.get(examine_line_id(kind)), kind


def _kinds(map_name: str) -> list[str]:
    text = (config.MAPS_DIR / f"{map_name}.txt").read_text(encoding="utf-8")
    kinds = []
    for line in text.splitlines():
        if line.startswith(";"):
            continue
        for char in line:
            tile = TILE_DEFS.get(char)
            if tile is not None and tile.prop:
                kinds.append(tile.prop)
    return kinds


def test_the_captains_cabin_is_a_study_without_a_hammock() -> None:
    kinds = _kinds("ship_captain_cabin")
    assert "ship_hammock" not in kinds
    assert kinds.count("ship_bookshelf") == 2
    assert kinds.count("ship_writing_desk") == 1
    # The crew still sleep in theirs.
    assert "ship_hammock" in _kinds("ship_crew_quarters")


def test_every_ship_room_got_its_dressing() -> None:
    assert {"ship_stew_pot", "ship_butcher_block"} <= set(_kinds("ship_galley"))
    hold = _kinds("ship_lower_hold")
    assert "ship_cargo_stack" in hold and "ship_rope_coil" in hold
    deck = _kinds("ship_exterior_deck")
    assert "ship_cargo_stack" in deck and "ship_rope_coil" in deck


def test_the_captains_chest_is_the_only_chest_aboard() -> None:
    chests = [kind for name in SHIP_MAPS for kind in _kinds(name)
              if "chest" in kind]
    assert chests == ["ship_captain_chest"]


def test_the_dressing_answers_e_and_the_rope_lies_flat() -> None:
    _answers_e(DRESSING)

    class Assets:
        def image(self, path):
            import pygame
            return pygame.Surface((16, 16))

    for kind in DRESSING:
        prop = Prop(kind, 3, 3, Assets())
        assert prop.dialogue_id == f"examine_{kind}", kind
        assert prop.floor_layer == (kind == "ship_rope_coil"), kind
    assert not next(t for t in TILE_DEFS.values()
                    if t.prop == "ship_rope_coil").solid
