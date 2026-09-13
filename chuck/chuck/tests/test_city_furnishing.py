"""The city's little more furniture, kept deliberately few.

One bench and one bin per street map, two different neon signs and a
steam grate per night map, two pipes and at most one tag per sewer --
all placed by the generators, which still reproduce the shipped maps.
"""

import contextlib
import importlib
import io
import os
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from src.core import config  # noqa: E402
from src.entities.prop import MUTE_PROPS  # noqa: E402
from src.world.tilemap import TileMap  # noqa: E402


def _answers_e(kinds) -> None:
    """Each kind has its examine line and is not in the mute scatter."""
    from src.entities.prop import examine_line_id
    from src.systems.dialogue import DialogueSystem

    dialogue = DialogueSystem()
    for kind in kinds:
        assert kind not in MUTE_PROPS, kind
        assert dialogue.get(examine_line_id(kind)), kind


STREETS = ("modern_city_arrival",) + tuple(
    f"modern_city_day_{i}" for i in range(1, 7)) + tuple(
    f"modern_city_night_{i}" for i in range(2, 7))
SEWERS = tuple(f"modern_city_sewer_{i}" for i in range(1, 5))
NEON = {"city_neon_bar", "city_neon_open", "city_neon_24h"}


def _kinds(name):
    return Counter(kind for kind, _, _ in
                   TileMap(config.MAPS_DIR / f"{name}.txt").prop_tiles)


def test_every_street_gets_one_bench_and_one_bin() -> None:
    for name in STREETS:
        kinds = _kinds(name)
        assert kinds["city_bench"] == 1, name
        assert kinds["city_litter_bin"] == 1, name
        night = name == "modern_city_arrival" or "night" in name
        signs = [kind for kind in kinds.elements() if kind in NEON]
        if night:
            assert len(signs) == 2 and len(set(signs)) == 2, (name, signs)
            assert kinds["city_steam_grate"] <= 1
        else:
            assert not signs and not kinds["city_steam_grate"], name


def test_every_sewer_gets_pipes_and_no_more_than_one_tag() -> None:
    for name in SEWERS:
        kinds = _kinds(name)
        assert kinds["sewer_pipe"] == 2, name
        assert kinds["sewer_graffiti"] <= 1, name


def test_the_generators_still_reproduce_the_shipped_maps() -> None:
    for name in STREETS + SEWERS:
        generator = ("generate_modern_city_night_1"
                     if name == "modern_city_arrival"
                     else f"generate_{name}")
        module = importlib.import_module(generator)
        build = getattr(module, "build", None) or module.build_map
        with contextlib.redirect_stdout(io.StringIO()):
            rows = build()
        built = [row if isinstance(row, str) else "".join(row) for row in rows]
        shipped = [line for line in (config.MAPS_DIR / f"{name}.txt")
                   .read_text(encoding="utf-8").splitlines()
                   if not line.startswith(";")]
        assert built == shipped, name


def test_the_new_pieces_answer_e() -> None:
    _answers_e({"city_bench", "city_litter_bin", "city_steam_grate",
                "sewer_pipe", "sewer_graffiti"} | NEON)
