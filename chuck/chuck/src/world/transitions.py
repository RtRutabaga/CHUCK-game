"""Per-area music configuration.

Choice destinations, named arrivals, and arrival choreography live in choice
data (see src/systems/choice.py). This module holds walk-over exits and each
area's looping music.
"""

from __future__ import annotations

from typing import NamedTuple


class AreaExit(NamedTuple):
    """A walk-over transition with a safe named arrival off the exit tile."""

    destination: str
    arrival: str
    facing: str


AREA_WALK_EXITS: dict[tuple[str, str], AreaExit] = {
    ("waterdeep_docks", "v"): AreaExit(
        "waterdeep_tavern", "front_entrance", "up"
    ),
    ("waterdeep_tavern", ">"): AreaExit(
        "waterdeep_docks", "tavern_return", "down"
    ),
    ("waterdeep_tavern", "?"): AreaExit(
        "waterdeep_pantry", "pantry_entry", "up"
    ),
    ("waterdeep_pantry", "^"): AreaExit(
        "waterdeep_tavern", "pantry_return", "down"
    ),
    ("chult_jungle", '"'): AreaExit(
        "chult_cog", "from_chult_1", "up"
    ),
    ("chult_cog", '"'): AreaExit(
        "chult_run", "from_chult_2", "up"
    ),
    ("chult_run", "ð"): AreaExit(
        "chult_respite", "from_chult_3", "right"
    ),
    ("chult_respite", "ð"): AreaExit(
        "chult_temple", "from_chult_4", "up"
    ),
    ("chult_temple", "Ω"): AreaExit(
        "temple_entrance", "from_temple_exterior", "up"
    ),
    ("temple_entrance", "Δ"): AreaExit(
        "chult_temple", "from_temple_interior", "down"
    ),
}


# Per-area looping music (filename in assets/audio/music/), or None for
# silence. Each area's theme is composition data under data/music/,
# rendered by tools/generate_music.py.
AREA_MUSIC: dict[str, str | None] = {
    "waterdeep_docks": "waterdeep_docks.wav",
    "sewer": "sewer.wav",
    # Reuse the warm Waterdeep theme until the dedicated tavern audio pass.
    "waterdeep_tavern": "waterdeep_docks.wav",
    "waterdeep_pantry": "waterdeep_docks.wav",
    "chult_jungle": "chult.wav",
    "chult_cog": "chult.wav",
    "chult_run": "chult.wav",
    "chult_respite": "chult.wav",
    "chult_temple": "chult.wav",
    "temple_entrance": "temple.wav",
}
