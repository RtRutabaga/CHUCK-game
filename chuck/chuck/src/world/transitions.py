"""Per-area music configuration.

Choice destinations, named arrivals, and arrival choreography normally live in
choice data (see src/systems/choice.py). This module holds walk-over exits,
their optional approach confirmations, and each area's looping music.
"""

from __future__ import annotations

from typing import NamedTuple


class AreaExit(NamedTuple):
    """A transition with a safe named arrival and optional YES/NO prompt."""

    destination: str
    arrival: str
    facing: str
    confirmation: str | None = None


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
    ("temple_entrance", "⌄"): AreaExit(
        "chult_temple", "from_temple_interior", "down"
    ),
    ("temple_entrance", "∇"): AreaExit(
        "temple_spikes", "from_temple_1", "up"
    ),
    # The deeper door's monumental gate tile (session 114) transitions
    # exactly as the arch char it replaced.
    ("temple_entrance", "£"): AreaExit(
        "temple_spikes", "from_temple_1", "up"
    ),
    ("temple_spikes", "Δ"): AreaExit(
        "temple_entrance", "from_temple_2", "down"
    ),
    ("temple_spikes", "⌄"): AreaExit(
        "temple_entrance", "from_temple_2", "down"
    ),
    ("temple_spikes", "∇"): AreaExit(
        "temple_skeletons", "from_temple_2", "up"
    ),
    ("temple_spikes", "⌂"): AreaExit(
        "temple_skeletons", "from_temple_2", "up"
    ),
    ("temple_skeletons", "Δ"): AreaExit(
        "temple_spikes", "from_temple_3", "down"
    ),
    ("temple_skeletons", "⌄"): AreaExit(
        "temple_spikes", "from_temple_3", "down"
    ),
    ("temple_skeletons", "∇"): AreaExit(
        "temple_darts", "from_temple_3", "left"
    ),
    ("temple_skeletons", "«"): AreaExit(
        "temple_darts", "from_temple_3", "left"
    ),
    ("temple_darts", "Δ"): AreaExit(
        "temple_skeletons", "from_temple_4", "right"
    ),
    ("temple_darts", "»"): AreaExit(
        "temple_skeletons", "from_temple_4", "right"
    ),
    ("temple_darts", "∇"): AreaExit(
        "temple_snakes", "from_temple_4", "left"
    ),
    ("temple_darts", "«"): AreaExit(
        "temple_snakes", "from_temple_4", "left"
    ),
    ("temple_snakes", "Δ"): AreaExit(
        "temple_darts", "from_temple_5", "right"
    ),
    ("temple_snakes", "»"): AreaExit(
        "temple_darts", "from_temple_5", "right"
    ),
    ("temple_snakes", "∇"): AreaExit(
        "temple_astral_wind", "from_temple_5", "down"
    ),
    ("temple_snakes", "⌂"): AreaExit(
        "temple_astral_wind", "from_temple_5", "down"
    ),
    ("temple_astral_wind", "Δ"): AreaExit(
        "temple_snakes", "from_temple_6", "up"
    ),
    # Map 6's east boundary is live now: the shrine hall beyond it.
    ("temple_astral_wind", "∇"): AreaExit(
        "temple_shrine", "from_temple_6", "right"
    ),
    ("temple_astral_wind", "«"): AreaExit(
        "temple_shrine", "from_temple_6", "right"
    ),
    # The shrine hall's north boundary is live now: the gauntlet.
    ("temple_shrine", "∇"): AreaExit(
        "temple_gauntlet", "from_temple_7", "up"
    ),
    ("temple_shrine", "⌂"): AreaExit(
        "temple_gauntlet", "from_temple_7", "up"
    ),
    ("temple_gauntlet", "Δ"): AreaExit(
        "temple_shrine", "from_temple_8", "down"
    ),
    # The gauntlet's west boundary is live now: the final chamber.
    ("temple_gauntlet", "∇"): AreaExit(
        "temple_sanctum", "from_temple_8", "left"
    ),
    ("temple_gauntlet", "«"): AreaExit(
        "temple_sanctum", "from_temple_8", "left"
    ),
    ("temple_sanctum", "Δ"): AreaExit(
        "temple_gauntlet", "from_temple_9", "right"
    ),
    ("temple_sanctum", "»"): AreaExit(
        "temple_gauntlet", "from_temple_9", "right"
    ),
    # Phase 7 begins below the arrival compartment. Both maps use the same
    # visible ladder tile and resolve through ordinary named arrivals after
    # the shared approach confirmation.
    ("ship_deck", "ℓ"): AreaExit(
        "ship_lower_hold", "from_ship_room", "down",
        "Climb down ladder?",
    ),
    ("ship_deck", "ɭ"): AreaExit(
        "ship_lower_hold", "from_ship_room", "down",
        "Climb down ladder?",
    ),
    ("ship_lower_hold", "ℓ"): AreaExit(
        "ship_deck", "from_lower_hold", "up",
        "Climb up ladder?",
    ),
    ("ship_lower_hold", "ɭ"): AreaExit(
        "ship_deck", "from_lower_hold", "up",
        "Climb up ladder?",
    ),
    # The arrival compartment's open west passage enters the galley. Every
    # visible jamb section is live so the three-tile doorway reads and plays
    # as one opening rather than a single hidden trigger pixel.
    ("ship_deck", "╭"): AreaExit("ship_galley", "from_ship_room", "left"),
    ("ship_deck", "│"): AreaExit("ship_galley", "from_ship_room", "left"),
    ("ship_deck", "╰"): AreaExit("ship_galley", "from_ship_room", "left"),
    ("ship_galley", "╮"): AreaExit("ship_deck", "from_galley", "right"),
    ("ship_galley", "┃"): AreaExit("ship_deck", "from_galley", "right"),
    ("ship_galley", "╯"): AreaExit("ship_deck", "from_galley", "right"),
    # The east passage leads to the crew quarters; its matching west doorway
    # returns to the compartment. The quarters' deck hatch and captain route
    # are intentionally visible but inert until those maps exist.
    ("ship_deck", "╮"): AreaExit(
        "ship_crew_quarters", "from_ship_room", "right"
    ),
    ("ship_deck", "┃"): AreaExit(
        "ship_crew_quarters", "from_ship_room", "right"
    ),
    ("ship_deck", "╯"): AreaExit(
        "ship_crew_quarters", "from_ship_room", "right"
    ),
    ("ship_crew_quarters", "╭"): AreaExit(
        "ship_deck", "from_crew_quarters", "left"
    ),
    ("ship_crew_quarters", "│"): AreaExit(
        "ship_deck", "from_crew_quarters", "left"
    ),
    ("ship_crew_quarters", "╰"): AreaExit(
        "ship_deck", "from_crew_quarters", "left"
    ),
    ("ship_crew_quarters", "╮"): AreaExit(
        "ship_captain_cabin", "from_crew_quarters", "right"
    ),
    ("ship_crew_quarters", "┃"): AreaExit(
        "ship_captain_cabin", "from_crew_quarters", "right"
    ),
    ("ship_crew_quarters", "╯"): AreaExit(
        "ship_captain_cabin", "from_crew_quarters", "right"
    ),
    ("ship_captain_cabin", "╭"): AreaExit(
        "ship_crew_quarters", "from_captain_cabin", "left"
    ),
    ("ship_captain_cabin", "│"): AreaExit(
        "ship_crew_quarters", "from_captain_cabin", "left"
    ),
    ("ship_captain_cabin", "╰"): AreaExit(
        "ship_crew_quarters", "from_captain_cabin", "left"
    ),
    ("ship_crew_quarters", "ℓ"): AreaExit(
        "ship_exterior_deck", "from_crew_quarters", "down",
        "Climb up ladder?",
    ),
    ("ship_crew_quarters", "ɭ"): AreaExit(
        "ship_exterior_deck", "from_crew_quarters", "down",
        "Climb up ladder?",
    ),
    ("ship_exterior_deck", "ℓ"): AreaExit(
        "ship_crew_quarters", "from_exterior_deck", "down",
        "Climb down ladder?",
    ),
    ("ship_exterior_deck", "ɭ"): AreaExit(
        "ship_crew_quarters", "from_exterior_deck", "down",
        "Climb down ladder?",
    ),
    # (The rubble's one way out is the "Enter crevice?" prompt at the
    # crawlspace, not a walk-over exit — see the choice:crevice trigger.)
    ("temple_gauntlet", "⌄"): AreaExit(
        "temple_shrine", "from_temple_8", "down"
    ),
    ("temple_shrine", "Δ"): AreaExit(
        "temple_astral_wind", "from_temple_7", "left"
    ),
    ("temple_shrine", "»"): AreaExit(
        "temple_astral_wind", "from_temple_7", "left"
    ),
    ("temple_astral_wind", "⌄"): AreaExit(
        "temple_snakes", "from_temple_6", "up"
    ),
    # Phase 8 --- Phlegethos. The ash-choked passes join the maps both ways.
    ("phlegethos_arrival", "∇"): AreaExit(
        "phlegethos_road", "from_phlegethos_1", "up"
    ),
    ("phlegethos_road", "Δ"): AreaExit(
        "phlegethos_arrival", "from_phlegethos_2", "down"
    ),
    ("phlegethos_road", "∇"): AreaExit(
        "phlegethos_lake", "from_phlegethos_2", "up"
    ),
    ("phlegethos_lake", "Δ"): AreaExit(
        "phlegethos_road", "from_phlegethos_3", "down"
    ),
    ("phlegethos_lake", "∇"): AreaExit(
        "phlegethos_rubble_pass", "from_phlegethos_3", "right"
    ),
    ("phlegethos_rubble_pass", "«"): AreaExit(
        "phlegethos_lake", "from_phlegethos_4", "down"
    ),
    ("phlegethos_rubble_pass", "›"): AreaExit(
        "phlegethos_fortress_approach", "from_phlegethos_rubble", "up"
    ),
    ("phlegethos_fortress_approach", "Δ"): AreaExit(
        "phlegethos_rubble_pass", "from_phlegethos_fortress", "left"
    ),
    # Phase 9 --- ordinary paths connect in geographically wrong directions.
    ("feywild_riverbank", "→"): AreaExit(
        "feywild_blooming_path", "from_feywild_1", "right"
    ),
    ("feywild_blooming_path", "←"): AreaExit(
        "feywild_riverbank", "from_feywild_2", "left"
    ),
    ("feywild_blooming_path", "→"): AreaExit(
        "feywild_pollen_orchard", "from_feywild_2", "up"
    ),
    ("feywild_pollen_orchard", "⇩"): AreaExit(
        "feywild_blooming_path", "from_feywild_3", "left"
    ),
    ("feywild_pollen_orchard", "⇧"): AreaExit(
        "feywild_rootways", "from_feywild_3", "right"
    ),
    ("feywild_rootways", "←"): AreaExit(
        "feywild_pollen_orchard", "from_feywild_4", "down"
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
    "temple_spikes": "temple.wav",
    "temple_skeletons": "temple.wav",
    "temple_darts": "temple.wav",
    "temple_snakes": "temple.wav",
    "temple_astral_wind": "temple.wav",
    "temple_shrine": "temple.wav",
    "temple_gauntlet": "temple.wav",
    # The final chamber gets its own climactic boss theme (session 136).
    "temple_sanctum": "boss_battle.wav",
    "temple_rubble": "temple.wav",
    # Out of the temple at last: a jaunty sea-shanty reel for the ship.
    "ship_deck": "ship_shanty.wav",
    "ship_lower_hold": "ship_shanty.wav",
    "ship_galley": "ship_shanty.wav",
    "ship_crew_quarters": "ship_shanty.wav",
    "ship_captain_cabin": "ship_shanty.wav",
    "ship_exterior_deck": "ship_shanty.wav",
    # Phlegethos: its own driving infernal theme (Phase 8).
    "phlegethos_arrival": "phlegethos.wav",
    "phlegethos_road": "phlegethos.wav",
    "phlegethos_lake": "phlegethos.wav",
    "phlegethos_rubble_pass": "phlegethos.wav",
    "phlegethos_fortress_approach": "phlegethos.wav",
    # One uninterrupted regional theme follows Chuck between Feywild maps.
    "feywild_riverbank": "feywild.wav",
    "feywild_blooming_path": "feywild.wav",
    "feywild_pollen_orchard": "feywild.wav",
    "feywild_rootways": "feywild.wav",
}
