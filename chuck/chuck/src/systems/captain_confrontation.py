"""Progression gate for the Phase 7 captain confrontation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.systems.checkpoints import ProgressState


CAPTAIN_CONFRONTED_FLAG = "captain_confronted"
DECK_PLANK_TERRAIN = "∥"
DECK_PLANK_LENGTH = 8
DECK_PLANK_WIDTH = 2
PLANK_PROCESSION_SPEED = 38.0
CAPTAIN_ARRIVAL_SPEED = 48.0
PLANK_KICK_APPROACH_SPEED = 46.0
PLANK_KICK_WINDUP = 0.28
PLANK_KICK_FALL_DURATION = 0.72
CAPTAIN_REQUIRED_FLAGS = frozenset({
    "pirate_chef_met",
    "crew_pirate_met",
    "captain_chest_opened",
    "deck_concertina_met",
    "deck_cheering_met",
    "deck_dancer_met",
    "deck_jeffries_met",
})


def captain_confrontation_ready(progress: "ProgressState") -> bool:
    """True only once every authored ship conversation and reward is done."""
    return (
        not progress.has(CAPTAIN_CONFRONTED_FLAG)
        and CAPTAIN_REQUIRED_FLAGS <= progress.flags
    )


def stage_deck_plank(tilemap, origin: tuple[int, int]) -> None:
    """Open the starboard rail and lay a broad walkable plank over sea."""
    first_col, first_row = origin
    for col in range(first_col, first_col + DECK_PLANK_WIDTH):
        for row in range(first_row, first_row + DECK_PLANK_LENGTH):
            tilemap.set_terrain(col, row, DECK_PLANK_TERRAIN)
