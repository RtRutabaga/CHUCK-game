"""The save registries are part of the wire format, so they are frozen.

A save code stores positions in `SAVE_ENTRIES` and `SAVE_FLAGS`, not
names. Reorder either tuple and every code ever written silently means
something else: no error, no crash, just the wrong room or the wrong
progress. There is nothing at runtime that can notice, which is why the
guard has to be here.

These tests allow appending and refuse everything else.
"""

import hashlib
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from src.core import config
from src.systems import save_registry as registry
from src.systems.checkpoints import CHECKPOINT_BY_ID, KNOWN_PROGRESS_FLAGS
from src.world.tilemap import TileMap


def _digest(items) -> str:
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


def test_the_frozen_prefix_of_each_registry_still_hashes_the_same() -> None:
    """Append freely; change what is already there and this fails.

    Only the frozen prefix is hashed, so adding a new entry or flag at
    the end costs nothing. Editing, reordering or deleting inside the
    prefix moves everything after it and breaks every code in the wild.
    If this test fails, the fix is almost never to update the digest.
    """
    assert len(registry.SAVE_ENTRIES) >= registry.FROZEN_ENTRY_COUNT
    assert len(registry.SAVE_FLAGS) >= registry.FROZEN_FLAG_COUNT
    assert _digest(registry.SAVE_ENTRIES[:registry.FROZEN_ENTRY_COUNT]) == \
        registry.FROZEN_ENTRY_DIGEST
    assert _digest(registry.SAVE_FLAGS[:registry.FROZEN_FLAG_COUNT]) == \
        registry.FROZEN_FLAG_DIGEST


def test_the_fields_are_wide_enough_for_what_is_in_them() -> None:
    """Eight bits of entry and twenty-five of flags, per the spec."""
    assert len(registry.SAVE_ENTRIES) <= 256
    assert len(registry.SAVE_FLAGS) <= 25


def test_every_entry_is_a_real_resume_point() -> None:
    live = [entry for entry in registry.SAVE_ENTRIES if entry]
    assert len(set(live)) == len(live), "an entry is in the registry twice"
    for entry in live:
        checkpoint = CHECKPOINT_BY_ID.get(entry)
        assert checkpoint is not None, entry
        # A resume point is a door Chuck walks in by. Anything else --
        # a development jump, a cutscene handoff -- is not somewhere a
        # save should ever put him back.
        #
        # A retired slot is the one exception, and it is named in the
        # registry rather than inferred from the checkpoint, so that
        # nothing can drift into this gap quietly.
        if entry in registry.RETIRED_ENTRIES:
            continue
        assert checkpoint.runtime_entry, entry


def test_every_retired_slot_still_lands_somewhere_real() -> None:
    """Retiring a slot keeps old codes working, so it has to still resolve.

    The point of retiring rather than tombstoning is that a code already
    written to the slot comes back somewhere sensible. That only holds
    while the entry names a checkpoint whose map and arrival marker
    actually exist, which is what this checks.
    """
    for entry in sorted(registry.RETIRED_ENTRIES):
        assert entry in registry.SAVE_ENTRIES, entry
        checkpoint = CHECKPOINT_BY_ID.get(entry)
        assert checkpoint is not None, entry
        assert not checkpoint.runtime_entry, (
            f"{entry} takes saves again -- drop it from RETIRED_ENTRIES")
        tilemap = TileMap(config.MAPS_DIR / f"{checkpoint.map_name}.txt")
        arrivals = {kind for kind, _ in tilemap.object_spawns}
        assert f"arrival:{checkpoint.arrival}" in arrivals, (
            entry, checkpoint.map_name, checkpoint.arrival)


def test_every_door_in_the_game_has_a_slot() -> None:
    """A map entrance with no slot is a place a save cannot be taken."""
    doors = {cp.checkpoint_id for cp in CHECKPOINT_BY_ID.values()
             if cp.runtime_entry}
    missing = doors - set(registry.SAVE_ENTRIES)
    assert not missing, f"append these to SAVE_ENTRIES: {sorted(missing)}"


def test_the_flag_registry_and_the_game_agree_exactly() -> None:
    live = {flag for flag in registry.SAVE_FLAGS if flag}
    assert live == KNOWN_PROGRESS_FLAGS, {
        "only in the registry": sorted(live - KNOWN_PROGRESS_FLAGS),
        "only in the game": sorted(KNOWN_PROGRESS_FLAGS - live),
    }


def test_slots_survive_a_round_trip_and_dead_slots_are_refused() -> None:
    for index, entry in enumerate(registry.SAVE_ENTRIES):
        if not entry:
            continue
        assert registry.entry_index(entry) == index
        assert registry.entry_id(index) == entry

    for bad in (-1, len(registry.SAVE_ENTRIES)):
        try:
            registry.entry_id(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"slot {bad} should not resolve")
    try:
        registry.entry_index("not_a_checkpoint")
    except KeyError:
        pass
    else:
        raise AssertionError("an unknown entry should not resolve")


def test_flags_survive_a_round_trip_and_strangers_are_dropped() -> None:
    for flags in ((), tuple(registry.SAVE_FLAGS),
                  ("sewer_completed",), ("chult_reached", "feywild_reached")):
        bits = registry.flags_to_bits(flags)
        assert set(registry.bits_to_flags(bits)) == set(flags), flags
        assert bits.bit_length() <= len(registry.SAVE_FLAGS)
    # A flag from a newer build must not corrupt the ones beside it.
    assert registry.flags_to_bits(("sewer_completed", "a_flag_from_later")) \
        == registry.flags_to_bits(("sewer_completed",))


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
    print("All save registry tests passed.")


if __name__ == "__main__":
    _run_all()
