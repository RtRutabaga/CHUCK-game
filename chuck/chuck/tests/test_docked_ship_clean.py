"""The cog tied up in Waterdeep at the end has no jungle on it."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from PIL import Image

from src.core import config
from src.entities.prop import _SPRITES

VINES = {(19, 62, 34), (43, 104, 49)}


def _colours(name: str) -> set:
    image = Image.open(config.SPRITES_DIR / "objects" / f"{name}.png")
    return {pixel[:3] for pixel in image.convert("RGBA").getdata()
            if pixel[3]}


def test_the_docked_ship_is_the_cog_without_its_vines() -> None:
    assert _SPRITES["waterdeep_docked_ship"] == \
        "objects/waterdeep_docked_ship.png"
    assert not VINES & _colours("waterdeep_docked_ship")
    # Chult's stranded cog keeps them.
    assert _SPRITES["sailing_cog"] == "objects/sailing_cog.png"
    assert VINES <= _colours("sailing_cog")
    # Otherwise the same ship: same size, same outline.
    clean = Image.open(config.SPRITES_DIR / "objects"
                       / "waterdeep_docked_ship.png")
    stranded = Image.open(config.SPRITES_DIR / "objects" / "sailing_cog.png")
    assert clean.size == stranded.size == (224, 152)
