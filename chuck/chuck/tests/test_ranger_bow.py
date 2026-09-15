"""The ranger holds her bow the right way round."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from PIL import Image

from src.core import config
from src.entities.battle_actor import _SPRITES
from src.scenes.credits_scene import CAST

BOW = (112, 80, 46)
STRING = (226, 222, 210)


def _columns(image, colour, rows):
    return sorted({x for y in rows for x in range(8)
                   if image.getpixel((x, y))[3]
                   and image.getpixel((x, y))[:3] == colour})


def test_the_bow_bows_away_from_her_and_the_string_is_on_her_side() -> None:
    image = Image.open(config.SPRITES_DIR / "npcs" / "ranger.png").convert(
        "RGBA")
    # She faces west (the ponytail is behind her, east), so the bow is out
    # to the west: its grip is the westernmost wood, the string lies east
    # of it, between the bow and her, and the tips come back to the string.
    grip = _columns(image, BOW, range(12, 17))
    string = _columns(image, STRING, range(6, 23))
    tips = _columns(image, BOW, (4, 24))
    assert grip and string and tips
    assert max(grip) < min(string), (grip, string)
    assert min(tips) > min(grip)
    assert max(tips) >= min(string)


def test_the_game_and_the_credits_draw_the_same_sprite() -> None:
    assert _SPRITES["ranger"] == "npcs/ranger.png"
    ranger = next(member for section in CAST for member in section.members
                  if member.name == "The Ranger")
    assert ranger.sprite.path == "npcs/ranger.png"
