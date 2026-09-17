"""The two ordered lists a save code is written against.

A code stores *positions* in these tuples, not names: one 8-bit number
for where Chuck is, 25 bits for what has happened to him. That is what
makes a code 21 characters instead of a paragraph, and it is also what
makes these two tuples part of the wire format.

    Append only. Never reorder. Never remove.

Move one entry and every code ever written silently resumes somewhere
else -- no error, no complaint, just the wrong room. Retire an entry by
leaving its slot in place as a tombstone (an empty string), so the
positions after it do not shift and a code naming it can be refused.

`tests/test_save_registry.py` holds the frozen prefix of each tuple to a
digest, so an edit in place fails and an append does not. That test is
the whole safety net; do not weaken it to make a change go through.

Neither tuple is derived from anything at import time -- not from
iteration over CHECKPOINTS, not from a set, not from a glob. Derived
order is order that can change when something unrelated changes, which
is exactly the failure this module exists to prevent.
"""

from __future__ import annotations


# Every point the game can resume at: the doors Chuck walks in by, which
# is also where he reappears when he dies. Authored order, frozen.
SAVE_ENTRIES: tuple[str, ...] = (
    "waterdeep_start",
    "sewer_entrance",
    "waterdeep_return",
    "waterdeep_plaza_from_docks",
    "tavern_entry",
    "pantry_entry",
    "chult_landing",
    "chult_2",
    "chult_3",
    "chult_4",
    "chult_4_from_falls",
    "chult_falls",
    "chult_5",
    "temple_1",
    "temple_2",
    "temple_3",
    "temple_4",
    "temple_5",
    "temple_6",
    "temple_7",
    "temple_8",
    "temple_9",
    "temple_rubble",
    "ship_deck",
    "ship_lower_hold",
    "ship_galley",
    "ship_deck_galley_return",
    "ship_crew_quarters",
    "ship_deck_crew_return",
    "ship_captain_cabin",
    "ship_crew_captain_return",
    "ship_exterior_deck",
    "ship_crew_exterior_return",
    "phlegethos_arrival",
    "phlegethos_road",
    "phlegethos_1_return",
    "phlegethos_lake",
    "phlegethos_rubble_pass",
    "phlegethos_fractured_way",
    "phlegethos_fortress_approach",
    "phlegethos_fractured_return",
    "phlegethos_rubble_return",
    "phlegethos_3_return",
    "phlegethos_2_return",
    "feywild_riverbank",
    "feywild_2",
    "feywild_1_return",
    "feywild_3",
    "feywild_4",
    "feywild_5",
    "feywild_6",
    "feywild_7",
    "feywild_8",
    "feywild_9",
    "feywild_2_return",
    "feywild_3_return",
    "feywild_4_return",
    "feywild_5_return",
    "feywild_8_return",
    "feywild_7_return",
    "feywild_10",
    "feywild_9_return",
    "feywild_11",
    "feywild_10_return",
    "feywild_12",
    "feywild_11_return",
    "feywild_13",
    "feywild_12_return",
    "zephyros_1",
    "feywild_13_return",
    "zephyros_2",
    "zephyros_3",
    "zephyros_exterior_return",
    "modern_city_1",
    "modern_city_2",
    "modern_city_1_return",
    "modern_city_3",
    "modern_city_2_return",
    "modern_city_4",
    "modern_city_3_return",
    "modern_city_5",
    "modern_city_4_return",
    "modern_city_6",
    "modern_city_5_return",
    "modern_city_sewer_1",
    "modern_city_sewer_2",
    "modern_city_sewer_1_return",
    "modern_city_sewer_3",
    "modern_city_sewer_4",
    "modern_city_day_1",
    "modern_city_day_2",
    "modern_city_day_3",
    "modern_city_day_4",
    "modern_city_day_5",
    "modern_city_day_6",
    "tahuya_exterior",
    "tahuya_interior",
    "tahuya_exterior_front_return",
    "modern_city_day_5_return",
    "modern_city_day_4_return",
    "modern_city_day_3_return",
    "modern_city_day_2_return",
    "modern_city_day_1_return",
    "modern_city_sewer_3_return",
    "modern_city_sewer_2_return",
    "modern_city_6_return",
    "feywild_6_return",
    "ship_deck_return",
    "temple_8_return",
    "temple_7_return",
    "temple_6_return",
    "temple_5_return",
    "temple_4_return",
    "temple_3_return",
    "temple_2_return",
    "temple_1_return",
    "chult_temple_return",
    "waterdeep_tavern_return",
    "waterdeep_docks_from_plaza",
    "tavern_pantry_return",
    "tavern_default",
    "pantry_default",
    "desert_central_start",
    "desert_central_from_orc_camp",
    "desert_orc_camp",
    "desert_central_from_oasis",
    "desert_oasis",
    "desert_central_from_ruins",
    "desert_undead_ruins",
    "desert_central_from_east_1",
    "desert_east_1",
    "desert_east_1_from_east_2",
    "desert_east_2",
    "desert_east_2_from_east_3",
    "desert_east_3",
    "desert_east_3_from_east_4",
    "desert_east_4",
    "desert_east_4_from_east_5",
    "desert_east_5",
    "desert_east_5_from_east_6",
    "desert_east_6",
    "desert_east_6_from_east_7",
    "desert_east_7",
    "desert_east_7_from_east_8",
    "desert_east_8",
    "desert_east_8_from_trio",
    "desert_trio",
)

# Everything that has durably happened, one bit each.
SAVE_FLAGS: tuple[str, ...] = (
    "cabin_counter_map_awakened",
    "cabin_entity_big_couch_spoken",
    "cabin_entity_chair_north_spoken",
    "cabin_entity_chair_south_spoken",
    "cabin_entity_couch_spoken",
    "captain_chest_carton_collected",
    "captain_chest_opened",
    "captain_confronted",
    "chult_falls_chest_carton_collected",
    "chult_falls_chest_opened",
    "chult_reached",
    "crew_pirate_met",
    "deck_cheering_met",
    "deck_concertina_met",
    "deck_dancer_met",
    "deck_jeffries_met",
    "desert_ruin_chest_carton_collected",
    "desert_ruin_chest_opened",
    "desert_transition_completed",
    "doug_fir_transition_completed",
    "feywild_reached",
    "modern_city_reached",
    "pirate_chef_met",
    "sewer_completed",
    "waterdeep_returned",
)

# How much of each tuple is spoken for by codes already in the wild,
# and what it hashed to when it was frozen. Appending raises the count
# in a later session; the digest of the prefix never changes.
FROZEN_ENTRY_COUNT = 147
FROZEN_ENTRY_DIGEST = "b591d1e3bc9ea9dc"
FROZEN_FLAG_COUNT = 25
FROZEN_FLAG_DIGEST = "5ddabc4f441d3fed"


ENTRY_INDEX: dict[str, int] = {
    entry: index for index, entry in enumerate(SAVE_ENTRIES) if entry
}
FLAG_INDEX: dict[str, int] = {
    flag: index for index, flag in enumerate(SAVE_FLAGS) if flag
}


def entry_index(checkpoint_id: str) -> int:
    """The slot a resume point is written to, or a loud error."""
    try:
        return ENTRY_INDEX[checkpoint_id]
    except KeyError as exc:
        raise KeyError(
            f"{checkpoint_id!r} is not a save entry. A new one has to be "
            f"APPENDED to SAVE_ENTRIES -- never inserted."
        ) from exc


def entry_id(index: int) -> str:
    """The resume point a slot names, or a loud error for a dead slot."""
    if not 0 <= index < len(SAVE_ENTRIES) or not SAVE_ENTRIES[index]:
        raise ValueError(f"No save entry at slot {index}")
    return SAVE_ENTRIES[index]


def flags_to_bits(flags) -> int:
    """Pack progress flags into one integer. Unknown flags are dropped."""
    bits = 0
    for flag in flags:
        index = FLAG_INDEX.get(flag)
        if index is not None:
            bits |= 1 << index
    return bits


def bits_to_flags(bits: int) -> tuple[str, ...]:
    """Unpack the integer back into flag names, in registry order."""
    return tuple(flag for index, flag in enumerate(SAVE_FLAGS)
                 if flag and bits >> index & 1)
