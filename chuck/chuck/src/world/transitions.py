"""Per-area configuration that isn't part of a map's tiles.

Where a choice carries Chuck now lives in the choice data itself (a
choice option's `goto`; see src/systems/choice.py), so this module only
holds the rest of an area's setup — currently its looping music.

    grate YES -> option goto "sewer" -> WorldScene.load_map("sewer")

Kept a plain dict — no pygame — so it stays unit-testable and the next
area is one line, not new logic.
"""

from __future__ import annotations

from typing import NamedTuple


class AreaExit(NamedTuple):
    """Where a walk-over exit leads and which arrival marker it uses."""

    destination: str
    arrival: str
    climb_from_water: bool


# (current map, terrain char) -> destination configuration. The sewer gate is
# a real map tile rather than a portal or dialogue interaction.
AREA_EXIT_TILES: dict[tuple[str, str], AreaExit] = {
    ("sewer", "Q"): AreaExit("waterdeep_docks", "sewer_outflow", True),
}

# Per-area looping music (filename in assets/audio/music/), or None for
# silence. Each area's theme is composition data under data/music/,
# rendered by tools/generate_music.py.
AREA_MUSIC: dict[str, str | None] = {
    "waterdeep_docks": "waterdeep_docks.wav",
    "sewer": "sewer.wav",
}
