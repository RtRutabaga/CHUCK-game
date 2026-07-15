"""Phase 4 previous-traveler environmental scene."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.entities.prop import Prop
from src.systems.dialogue import DialogueSystem
from src.world.tilemap import TileMap


class FakeImage:
    def __init__(self, size):
        self._size = size

    def get_size(self):
        return self._size


class FakeAssets:
    def __init__(self, size):
        self._size = size

    def image(self, _path):
        return FakeImage(self._size)


def test_abandoned_expedition_scene_is_compact_and_optional() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_jungle.txt")
    props = [
        (kind, col, row)
        for kind, col, row in tilemap.prop_tiles
        if kind in {"expedition_backpack", "abandoned_boot"}
    ]
    assert props == [
        ("expedition_backpack", 20, 15),
        ("abandoned_boot", 24, 15),
    ]
    # The clearing remains broad around the two solid objects, so neither is a
    # progression gate and Chuck can inspect them from every side.
    for _kind, col, row in props:
        assert sum(
            not tilemap.is_solid(col + dx, row + dy)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
        ) >= 3


def test_expedition_objects_reinforce_chucks_scale() -> None:
    backpack = pygame.image.load(
        config.SPRITES_DIR / "objects" / "expedition_backpack.png"
    )
    boot = pygame.image.load(config.SPRITES_DIR / "objects" / "abandoned_boot.png")
    assert backpack.get_height() > config.NPC_FRAME_H
    assert backpack.get_height() > config.CHUCK_FRAME_H * 2
    assert boot.get_width() > config.CHUCK_FRAME_W * 2


def test_backpack_has_one_restrained_line_and_boot_stays_mute() -> None:
    backpack = Prop(
        "expedition_backpack", 20, 15, FakeAssets((30, 32))
    )
    boot = Prop("abandoned_boot", 24, 15, FakeAssets((26, 16)))
    assert backpack.dialogue_id == "expedition_backpack"
    assert backpack.choice_id is None
    assert boot.dialogue_id is None and boot.choice_id is None
    assert DialogueSystem().get("expedition_backpack") == [
        "Someone left quickly."
    ]


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All previous-traveler scene tests passed.")


if __name__ == "__main__":
    _run_all()
