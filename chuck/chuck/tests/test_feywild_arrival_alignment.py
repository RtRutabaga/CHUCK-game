"""Feywild named arrivals line up with their visible wilderness openings."""

from src.core import config
from src.world.tilemap import TileMap
from src.world.transitions import AREA_WALK_EXITS


_ARROWS = frozenset({"←", "→", "⇧", "⇩"})


def _arrival(tilemap: TileMap, name: str) -> tuple[int, int]:
    size = config.TILE_SIZE
    matches = [
        (int(x // size), int(y // size))
        for kind, (x, y) in tilemap.object_spawns
        if kind == f"arrival:{name}"
    ]
    assert len(matches) == 1, (tilemap.map_path.name, name, matches)
    return matches[0]


def _opening_center(tilemap: TileMap, arrow: str) -> tuple[int, int]:
    cells = [
        (col, row)
        for row in range(tilemap.height_tiles)
        for col in range(tilemap.width_tiles)
        if tilemap.terrain_at(col, row) == arrow
    ]
    assert len(cells) in {1, 3}, (tilemap.map_path.name, arrow, cells)
    return sorted(cells)[len(cells) // 2]


def _inside(opening: tuple[int, int], arrow: str) -> tuple[int, int]:
    col, row = opening
    return {
        "←": (col + 1, row),
        "→": (col - 1, row),
        "⇧": (col, row + 1),
        "⇩": (col, row - 1),
    }[arrow]


def test_every_reciprocal_feywild_arrival_is_centered_just_inside_its_art() -> None:
    checked = set()
    for (source, _source_arrow), transition in AREA_WALK_EXITS.items():
        destination = transition.destination
        if not (source.startswith("feywild_") and
                destination.startswith("feywild_")):
            continue

        reverse = [
            arrow
            for (map_name, arrow), candidate in AREA_WALK_EXITS.items()
            if map_name == destination
            and candidate.destination == source
            and arrow in _ARROWS
        ]
        assert len(reverse) == 1, (source, destination, reverse)
        arrow = reverse[0]
        tilemap = TileMap(config.MAPS_DIR / f"{destination}.txt")
        opening = _opening_center(tilemap, arrow)
        actual = _arrival(tilemap, transition.arrival)
        assert actual == _inside(opening, arrow), (
            source, destination, transition.arrival, actual, opening
        )
        checked.add((destination, transition.arrival))

    # Twelve authored Feywild links, checked in both directions. It was
    # thirteen until the tea table was cut: it sat between Rootways and
    # Needle Garden, so removing it joined two links into one.
    assert len(checked) == 24


def _run_all() -> None:
    test_every_reciprocal_feywild_arrival_is_centered_just_inside_its_art()
    print("All Feywild arrival-alignment tests passed.")


if __name__ == "__main__":
    _run_all()
