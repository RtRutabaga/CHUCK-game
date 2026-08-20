"""Small, durable progression rules for the Phase 12 Cabin."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.systems.checkpoints import ProgressState


CABIN_ENTITY_FLAGS = frozenset({
    "cabin_entity_big_couch_spoken",
    "cabin_entity_couch_spoken",
    "cabin_entity_chair_north_spoken",
    "cabin_entity_chair_south_spoken",
})
COUNTER_MAP_AWAKENED_FLAG = "cabin_counter_map_awakened"

_BACK_DOOR_CROSSINGS = frozenset({
    (
        "tahuya_cabin_exterior",
        "tahuya_cabin_interior",
        "from_back_door",
    ),
    (
        "tahuya_cabin_interior",
        "tahuya_cabin_exterior",
        "from_cabin_back",
    ),
})


def all_entities_spoken(progress: "ProgressState") -> bool:
    """Derive the prerequisite without storing a second source of truth."""
    return CABIN_ENTITY_FLAGS <= progress.flags


def apply_back_door_crossing(
    progress: "ProgressState",
    source_map: str,
    destination_map: str,
    arrival: str,
) -> bool:
    """Awaken the counter only on a qualifying later back-door crossing.

    Returns True exactly when this crossing changes the durable state.
    """
    crossing = (source_map, destination_map, arrival)
    if crossing not in _BACK_DOOR_CROSSINGS:
        return False
    if progress.has(COUNTER_MAP_AWAKENED_FLAG):
        return False
    if not all_entities_spoken(progress):
        return False
    progress.enable(COUNTER_MAP_AWAKENED_FLAG)
    return True
