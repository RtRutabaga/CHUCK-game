"""Unit tests for area configuration: per-area music, and the guarantee
that every choice `goto` points at a real, loadable map.

Pure stdlib (no pygame), like the rest of the data-layer tests.

    python -m tests.test_transitions
    pytest
"""

from src.core import config
from src.systems.choice import ChoiceSystem
from src.world.tilemap import TileMap
from src.world.transitions import AREA_MUSIC, AREA_WALK_EXITS


def test_grate_yes_goes_to_the_sewer() -> None:
    # The destination now lives in the choice data (a goto), not a code
    # table: YES carries Chuck to the sewer, and speaks no lines.
    yes = ChoiceSystem().get("sewer_grate").options[0]
    assert yes.label == "YES"
    assert yes.goto == "sewer"
    assert yes.dialogue is None


def test_no_option_is_a_silent_close() -> None:
    no = ChoiceSystem().get("sewer_grate").options[1]
    assert no.label == "NO"
    assert no.goto is None
    assert no.dialogue is None


def test_every_choice_goto_points_at_a_real_map() -> None:
    # A goto aimed at a missing or malformed map would strand Chuck.
    cs = ChoiceSystem()
    for choice_id in cs.ids():
        for opt in cs.get(choice_id).options:
            if opt.goto is not None:
                path = config.MAPS_DIR / f"{opt.goto}.txt"
                assert path.is_file(), (choice_id, opt.label, path)
                destination = TileMap(path)  # parses without raising
                if opt.arrival is not None:
                    arrivals = {
                        kind.split(":", 1)[1]
                        for kind, _ in destination.object_spawns
                        if kind.startswith("arrival:")
                    }
                    assert opt.arrival in arrivals


def test_area_music_is_a_real_file_or_deliberate_silence() -> None:
    assert AREA_MUSIC["chult_jungle"] == "chult.wav"
    assert AREA_MUSIC["chult_cog"] == "chult.wav"
    for name, music in AREA_MUSIC.items():
        if music is not None:
            assert (config.MUSIC_DIR / music).is_file(), (name, music)


def test_every_walk_exit_targets_a_real_named_arrival() -> None:
    assert AREA_WALK_EXITS[("waterdeep_docks", "v")].destination == (
        "waterdeep_tavern"
    )
    assert AREA_WALK_EXITS[("waterdeep_tavern", ">")].destination == (
        "waterdeep_docks"
    )
    assert AREA_WALK_EXITS[("waterdeep_tavern", "?")].destination == (
        "waterdeep_pantry"
    )
    assert AREA_WALK_EXITS[("waterdeep_pantry", "^")].destination == (
        "waterdeep_tavern"
    )
    assert AREA_WALK_EXITS[("chult_jungle", '"')].destination == "chult_cog"
    for (source, terrain), exit_config in AREA_WALK_EXITS.items():
        source_map = TileMap(config.MAPS_DIR / f"{source}.txt")
        if (source, terrain) == ("waterdeep_docks", "v"):
            source_map.open_tavern_entrance()
        assert any(terrain in row for row in source_map._grid), (source, terrain)
        destination = TileMap(
            config.MAPS_DIR / f"{exit_config.destination}.txt"
        )
        arrivals = {
            kind.split(":", 1)[1]
            for kind, _ in destination.object_spawns
            if kind.startswith("arrival:")
        }
        assert exit_config.arrival in arrivals
        assert exit_config.facing in {"up", "down", "left", "right"}


def test_sewer_outflow_targets_the_named_waterdeep_arrival() -> None:
    exit_option = ChoiceSystem().get("sewer_exit").options[0]
    assert exit_option.goto == "waterdeep_docks"
    assert exit_option.arrival == "sewer_outflow"
    assert exit_option.climb_from_water
    docks = TileMap(config.MAPS_DIR / "waterdeep_docks.txt")
    arrivals = {kind: pos for kind, pos in docks.object_spawns
                if kind.startswith("arrival:")}
    assert "arrival:sewer_outflow" in arrivals
    x, y = arrivals["arrival:sewer_outflow"]
    assert (int(x // config.TILE_SIZE), int(y // config.TILE_SIZE)) == (15, 30)


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
    print("All transitions tests passed.")


if __name__ == "__main__":
    _run_all()
