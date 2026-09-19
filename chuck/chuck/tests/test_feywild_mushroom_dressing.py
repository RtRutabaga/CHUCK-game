"""Later Feywild maps carry the region's mushroom language consistently."""

import importlib

from src.core import config
from src.world.tilemap import TileMap
from tools.feywild_mushroom_dressing import MUSHROOMS_BY_MAP


GENERATOR_MAPS = frozenset(MUSHROOMS_BY_MAP) - {"feywild_moonmoth_fen"}


def _mushroom_positions(map_name: str) -> set[tuple[int, int]]:
    tilemap = TileMap(config.MAPS_DIR / f"{map_name}.txt")
    return {
        (col, row)
        for kind, col, row in tilemap.prop_tiles
        if kind == "feywild_mushroom"
    }


def test_later_feywild_maps_have_dense_authored_mushroom_dressing() -> None:
    # Nine, not ten: the tea table was cut and took its dressing with it.
    assert len(MUSHROOMS_BY_MAP) == 9
    for map_name, expected in MUSHROOMS_BY_MAP.items():
        assert len(expected) == 6
        assert set(expected) <= _mushroom_positions(map_name)

    # Maps 1--4 already carried the visual language; the new pass is
    # deliberately weighted toward Map 5 and everything after it.
    for map_name in (
        "feywild_riverbank",
        "feywild_blooming_path",
        "feywild_pollen_orchard",
        "feywild_rootways",
    ):
        assert len(_mushroom_positions(map_name)) >= 3


def test_generator_backed_maps_share_the_same_mushroom_coordinates() -> None:
    for map_name in GENERATOR_MAPS:
        suffix = map_name.removeprefix("feywild_")
        module = importlib.import_module(f"tools.generate_feywild_{suffix}")
        grid = module.build()
        module.validate(grid)
        assert all(
            grid[row][col] == "ŋ"
            for col, row in MUSHROOMS_BY_MAP[map_name]
        )


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
    print("All Feywild mushroom-dressing tests passed.")


if __name__ == "__main__":
    _run_all()
