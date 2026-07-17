"""Dense-jungle tree art and collision regression coverage."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core import config
from src.entities.prop import Prop
from src.world.tilemap import TileMap


class FakeImage:
    def get_size(self):
        return (34, 46)


class RecordingAssets:
    def __init__(self):
        self.paths = []

    def image(self, path):
        self.paths.append(path)
        return FakeImage()


def test_chult_dense_masses_layer_solid_trees_and_shrubs() -> None:
    tilemap = TileMap(config.MAPS_DIR / "chult_jungle.txt")
    trees = [
        (col, row)
        for kind, col, row in tilemap.prop_tiles
        if kind == "jungle_tree"
    ]
    # The session-111 densification pass grew the map's vegetation mass
    # (~10% of open ground became new blobs), so the decoration band
    # widened with it.
    assert 150 <= len(trees) <= 240
    for col, row in trees:
        assert tilemap.terrain_at(col, row) == "/"
        assert tilemap.is_solid(col, row)
    shrubs = [
        (col, row)
        for kind, col, row in tilemap.prop_tiles
        if kind == "jungle_shrub"
    ]
    assert 160 <= len(shrubs) <= 240
    for col, row in shrubs:
        assert tilemap.terrain_at(col, row) == "\\"
        assert tilemap.is_solid(col, row)


def test_tree_silhouettes_are_large_and_all_variants_are_authored() -> None:
    sizes = []
    for index in range(1, 4):
        path = config.SPRITES_DIR / "objects" / f"jungle_tree_{index}.png"
        image = pygame.image.load(path)
        sizes.append(image.get_size())
    assert sizes == [(34, 46)] * 3
    assert sizes[0][1] > config.NPC_FRAME_H
    assert sizes[0][1] > config.CHUCK_FRAME_H * 3


def test_shrub_variants_are_broad_leafed_at_chucks_scale() -> None:
    sizes = []
    for index in range(1, 4):
        path = config.SPRITES_DIR / "objects" / f"jungle_shrub_{index}.png"
        image = pygame.image.load(path)
        sizes.append(image.get_size())
    assert sizes == [(28, 24)] * 3
    assert sizes[0][0] > config.CHUCK_FRAME_W * 2
    assert sizes[0][1] > config.CHUCK_FRAME_H


def test_tree_variant_selection_is_stable_and_uses_all_three_sprites() -> None:
    assets = RecordingAssets()
    for col in range(12):
        Prop("jungle_tree", col, 7, assets)
    assert set(assets.paths) == {
        "objects/jungle_tree_1.png",
        "objects/jungle_tree_2.png",
        "objects/jungle_tree_3.png",
    }
    first = RecordingAssets()
    second = RecordingAssets()
    Prop("jungle_tree", 13, 9, first)
    Prop("jungle_tree", 13, 9, second)
    assert first.paths == second.paths

    shrubs = RecordingAssets()
    for col in range(12):
        Prop("jungle_shrub", col, 7, shrubs)
    assert set(shrubs.paths) == {
        "objects/jungle_shrub_1.png",
        "objects/jungle_shrub_2.png",
        "objects/jungle_shrub_3.png",
    }


def _run_all() -> None:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  PASS  {name}")
    print("All Chult vegetation tests passed.")


if __name__ == "__main__":
    _run_all()
