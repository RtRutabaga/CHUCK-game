"""Per-area music configuration.

Choice destinations, named arrivals, and arrival choreography live in choice
data (see src/systems/choice.py). This module holds each area's looping music.
"""

from __future__ import annotations


# Per-area looping music (filename in assets/audio/music/), or None for
# silence. Each area's theme is composition data under data/music/,
# rendered by tools/generate_music.py.
AREA_MUSIC: dict[str, str | None] = {
    "waterdeep_docks": "waterdeep_docks.wav",
    "sewer": "sewer.wav",
}
