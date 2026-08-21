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

# What the interior plays once the table map has woken. The exterior
# keeps the ordinary cue, so the lift belongs to the room the aurora is
# actually in, and walking back out of the door drops the intensity
# again rather than carrying it into the trees.
AWAKENED_INTERIOR = "tahuya_cabin_interior"
AWAKENED_MUSIC = "cabin_awakened.wav"


def awakened_music_for(map_name: str, progress: "ProgressState"):
    """The cue this map plays right now, or None to leave it alone."""
    if map_name != AWAKENED_INTERIOR:
        return None
    if not progress.has(COUNTER_MAP_AWAKENED_FLAG):
        return None
    return AWAKENED_MUSIC

_CABIN_DOOR_CROSSINGS = frozenset({
    (
        "tahuya_cabin_exterior",
        "tahuya_cabin_interior",
        "from_front_door",
    ),
    (
        "tahuya_cabin_interior",
        "tahuya_cabin_exterior",
        "from_cabin_front",
    ),
})


def all_entities_spoken(progress: "ProgressState") -> bool:
    """Derive the prerequisite without storing a second source of truth."""
    return CABIN_ENTITY_FLAGS <= progress.flags


def apply_cabin_door_crossing(
    progress: "ProgressState",
    source_map: str,
    destination_map: str,
    arrival: str,
) -> bool:
    """Awaken the counter only on a qualifying later cabin-door crossing.

    Returns True exactly when this crossing changes the durable state.
    """
    crossing = (source_map, destination_map, arrival)
    if crossing not in _CABIN_DOOR_CROSSINGS:
        return False
    if progress.has(COUNTER_MAP_AWAKENED_FLAG):
        return False
    if not all_entities_spoken(progress):
        return False
    progress.enable(COUNTER_MAP_AWAKENED_FLAG)
    return True
