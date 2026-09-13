"""The hub's ribcage and the orc camp's gear.

One ribcage, in the hub's open sand, fading when walked behind. The orc
camp gets tents, weapon racks and a war drum -- and no totem -- all of it
standing on open ground, all of it leaving the camp as reachable as it
was.
"""

import importlib
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from src.core import config  # noqa: E402
from src.entities.prop import MUTE_PROPS, SEE_THROUGH_PROPS  # noqa: E402
from src.world.tilemap import TileMap  # noqa: E402


def _answers_e(kinds) -> None:
    """Each kind has its examine line and is not in the mute scatter."""
    from src.entities.prop import examine_line_id
    from src.systems.dialogue import DialogueSystem

    dialogue = DialogueSystem()
    for kind in kinds:
        assert kind not in MUTE_PROPS, kind
        assert dialogue.get(examine_line_id(kind)), kind


def _props(name):
    return TileMap(config.MAPS_DIR / f"{name}.txt").prop_tiles


def test_one_ribcage_lies_in_the_hubs_open_sand() -> None:
    central = importlib.import_module("generate_desert_central")
    ribcages = [(col, row) for kind, col, row in _props("desert_central")
                if kind == "desert_ribcage"]
    assert ribcages == [central.RIBCAGE]
    for name in ("desert_east_1", "desert_east_2", "desert_oasis",
                 "desert_orc_camp"):
        assert all(kind != "desert_ribcage" for kind, _, _ in _props(name))
    assert "desert_ribcage" in SEE_THROUGH_PROPS


def test_the_generators_reproduce_the_shipped_maps() -> None:
    for module_name, map_name in (("generate_desert_central", "desert_central"),
                                  ("generate_desert_orc_camp",
                                   "desert_orc_camp")):
        module = importlib.import_module(module_name)
        built = ["".join(row) for row in module.build()]
        shipped = [line for line in (config.MAPS_DIR / f"{map_name}.txt")
                   .read_text(encoding="utf-8").splitlines()
                   if not line.startswith(";")]
        assert built == shipped, map_name


def test_the_orc_camp_has_tents_racks_and_a_drum_but_no_totem() -> None:
    kinds = [kind for kind, _, _ in _props("desert_orc_camp")]
    assert kinds.count("orc_tent") == 3
    assert kinds.count("orc_weapon_rack") == 2
    assert kinds.count("orc_war_drum") == 1
    assert not any("totem" in kind for kind in kinds)
    _answers_e({"desert_ribcage", "orc_tent", "orc_weapon_rack",
                "orc_war_drum"})
