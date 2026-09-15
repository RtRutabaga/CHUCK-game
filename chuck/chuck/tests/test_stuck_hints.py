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
