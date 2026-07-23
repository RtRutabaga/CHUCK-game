"""Progression gate for the Phase 7 captain confrontation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.systems.checkpoints import ProgressState


CAPTAIN_CONFRONTED_FLAG = "captain_confronted"
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
