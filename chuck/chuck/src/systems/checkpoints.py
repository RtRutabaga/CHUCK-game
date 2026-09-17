"""Authored checkpoints and the one shared checkpoint-loading path.

NEW GAME, CONTINUE, and the temporary development selector all choose an ID
from this registry and call CheckpointLoader.load_checkpoint(). Map transitions
also use registry entries to preserve the established local-respawn behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.core import config
from src.systems.cabin_progress import (
    CABIN_ENTITY_FLAGS, COUNTER_MAP_AWAKENED_FLAG, DESERT_TRANSITION_FLAG,
)
from src.systems.captain_confrontation import CAPTAIN_REQUIRED_FLAGS
from src.systems import save_registry
from src.systems.save import SaveRecord, SaveSystem

if TYPE_CHECKING:
    from src.core.game import Game


WATERDEEP_RETURN_FLAG = "waterdeep_returned"

KNOWN_PROGRESS_FLAGS = frozenset({
    "sewer_completed",
    "chult_reached",
    "crew_pirate_met",
    "pirate_chef_met",
    "captain_chest_opened",
    "captain_chest_carton_collected",
    # Phase 13: the same chest in the desert ruins, with its own pair --
    # sharing the captain's would open both at once.
    "desert_ruin_chest_opened",
    "desert_ruin_chest_carton_collected",
    # And again at Chult Falls.
    "chult_falls_chest_opened",
    "chult_falls_chest_carton_collected",
    "deck_concertina_met",
    "deck_cheering_met",
    "deck_dancer_met",
    "deck_jeffries_met",
    "captain_confronted",
    "feywild_reached",
    "modern_city_reached",
    "doug_fir_transition_completed",
    # Phase 13's own end: the heroes closed the collision and the
    # blast put Chuck back on the Waterdeep docks. Nothing reads it
    # yet -- the finale is the phase that will -- but the crossing
    # is recorded when it happens rather than when something wants
    # it, the same way every crossing before it was.
    WATERDEEP_RETURN_FLAG,
}) | CABIN_ENTITY_FLAGS | {COUNTER_MAP_AWAKENED_FLAG,
                          DESERT_TRANSITION_FLAG}
# Everything Phase 13 needs behind it. The desert is only reachable
# once the table portal has actually been stepped through.
DESERT_ENTRY_FLAGS = frozenset({
    "sewer_completed", "chult_reached", "feywild_reached",
    "modern_city_reached", "doug_fir_transition_completed",
    DESERT_TRANSITION_FLAG,
})
OPENING_CHECKPOINT_ID = "waterdeep_start"


@dataclass(frozen=True)
class CheckpointDefinition:
    checkpoint_id: str
    display_name: str
    map_name: str
    position: tuple[float, float] | None = None
    arrival: str | None = None
    facing: str | None = None
    climb_from_water: bool = False
    required_flags: frozenset[str] = field(default_factory=frozenset)
    development_visible: bool = True
    runtime_entry: bool = False
    fade_in: bool = False
    # What the arrival fades up out of. Black for every crossing that
    # went to black, which is all of them until the desert: that one
    # whites out, and fading it back in from black would put a flash
    # between the cutscene and the map it hands to.
    fade_from: tuple[int, int, int] = (0, 0, 0)


CHECKPOINTS = (
    CheckpointDefinition(
        # Facing left: the opening cutscene ends on Chuck standing beside
        # Bobert's barrel in profile with a cigarette, and the docks come
        # up on the same pose. (The cutscene adds the fade up itself, so a
        # direct load from the development menu is not held in a fade.)
        "waterdeep_start", "Waterdeep 1", "waterdeep_docks",
        facing="left", runtime_entry=True,
    ),
    CheckpointDefinition(
        "sewer_entrance", "Sewer 1", "sewer",
        facing="down", runtime_entry=True,
    ),
    CheckpointDefinition(
        "waterdeep_return", "Waterdeep 2", "waterdeep_docks",
        arrival="sewer_outflow", facing="up", climb_from_water=True,
        required_flags=frozenset({"sewer_completed"}), runtime_entry=True,
    ),
    CheckpointDefinition(
        # No position of its own: it lands on the map's own player
        # marker, which is the plank beside Bobert's barrel that the
        # game opened on. Two reasons. The authored one is that the
        # whole phase is about recognising the place, and there is no
        # stronger way to say "you are back" than putting him on the
        # exact board he started from, with Bobert still asleep beside
        # him and everything else louder and brighter.
        #
        # The other is that the explicit position it used to carry --
        # (32, 208) -- is tile (2, 13), which is open harbour. Water is
        # solid here, so the finale was dropping him inside a solid tile
        # seven tiles off the end of the pier. Sharing the opening's
        # marker means the two spawns cannot drift apart again.
        "waterdeep_finale", "Waterdeep Finale", "waterdeep_docks",
        facing="down",
        required_flags=DESERT_ENTRY_FLAGS | {WATERDEEP_RETURN_FLAG},
        fade_in=True, fade_from=(250, 250, 252),
    ),
    CheckpointDefinition(
        "waterdeep_plaza_from_docks", "Fountain Plaza", "waterdeep_plaza",
        arrival="from_docks", facing="right", runtime_entry=True,
    ),
    CheckpointDefinition(
        "waterdeep_plaza_finale", "Fountain Plaza Finale",
        "waterdeep_plaza", position=(40.0, 312.0), facing="right",
        required_flags=DESERT_ENTRY_FLAGS | {WATERDEEP_RETURN_FLAG},
    ),
    CheckpointDefinition(
        "tavern_entry", "Tavern 1", "waterdeep_tavern",
        arrival="front_entrance", facing="up",
        required_flags=frozenset({"sewer_completed"}), runtime_entry=True,
    ),
    CheckpointDefinition(
        "pantry_entry", "Pantry 1", "waterdeep_pantry",
        arrival="pantry_entry", facing="up",
        required_flags=frozenset({"sewer_completed"}), runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_landing", "Chult Landing", "chult_jungle",
        facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "chult_2", "Chult 2", "chult_cog",
        arrival="from_chult_1", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_3", "Chult 3", "chult_run",
        arrival="from_chult_2", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_4", "Chult 4", "chult_respite",
        arrival="from_chult_3", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_4_from_falls", "Chult 4 (from the Falls)", "chult_respite",
        arrival="from_chult_falls", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True, development_visible=False,
    ),
    CheckpointDefinition(
        "chult_falls", "Chult Falls", "chult_falls",
        arrival="from_chult_respite", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_5", "Chult 5", "chult_temple",
        arrival="from_chult_4", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_1", "Temple 1", "temple_entrance",
        arrival="from_temple_exterior", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_2", "Temple 2", "temple_spikes",
        arrival="from_temple_1", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_3", "Temple 3", "temple_skeletons",
        arrival="from_temple_2", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_4", "Temple 4", "temple_darts",
        arrival="from_temple_3", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_5", "Temple 5", "temple_snakes",
        arrival="from_temple_4", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_6", "Temple 6", "temple_astral_wind",
        arrival="from_temple_5", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_7", "Temple 7", "temple_shrine",
        arrival="from_temple_6", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_8", "Temple 8", "temple_gauntlet",
        arrival="from_temple_7", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_9", "Temple 9", "temple_sanctum",
        arrival="from_temple_8", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_rubble", "Rubble 1", "temple_rubble",
        arrival="from_fireball", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "ship_deck", "Ship 1", "ship_deck",
        arrival="from_crawlspace", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "ship_lower_hold", "Ship Hold", "ship_lower_hold",
        arrival="from_ship_room", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_galley", "Ship Galley", "ship_galley",
        arrival="from_ship_room", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_deck_galley_return", "Ship Galley Return", "ship_deck",
        arrival="from_galley", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_crew_quarters", "Ship Crew Quarters", "ship_crew_quarters",
        arrival="from_ship_room", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_deck_crew_return", "Ship Crew Return", "ship_deck",
        arrival="from_crew_quarters", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_captain_cabin", "Ship Captain Cabin", "ship_captain_cabin",
        arrival="from_crew_quarters", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_crew_captain_return", "Ship Captain Return",
        "ship_crew_quarters", arrival="from_captain_cabin", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_exterior_deck", "Ship Exterior Deck", "ship_exterior_deck",
        arrival="from_crew_quarters", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_captain_arrival", "Captain Arrival", "ship_exterior_deck",
        arrival="from_crew_quarters", facing="down",
        required_flags=(
            frozenset({"sewer_completed", "chult_reached"})
            | CAPTAIN_REQUIRED_FLAGS
        ),
        runtime_entry=False,
    ),
    CheckpointDefinition(
        "ship_crew_exterior_return", "Ship Exterior Return",
        "ship_crew_quarters", arrival="from_exterior_deck", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    # Phase 8 --- Phlegethos, the Nine Hells overworld.
    CheckpointDefinition(
        "phlegethos_arrival", "Phlegethos 1", "phlegethos_arrival",
        arrival="from_hell", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "phlegethos_road", "Phlegethos 2", "phlegethos_road",
        arrival="from_phlegethos_1", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_1_return", "Phlegethos 1 Return", "phlegethos_arrival",
        arrival="from_phlegethos_2", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_lake", "Phlegethos 3", "phlegethos_lake",
        arrival="from_phlegethos_2", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_rubble_pass", "Phlegethos 4",
        "phlegethos_rubble_pass",
        arrival="from_phlegethos_3", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_fractured_way", "Phlegethos 5",
        "phlegethos_fractured_way",
        arrival="from_phlegethos_rubble", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_fortress_approach", "Phlegethos 6",
        "phlegethos_fortress_approach",
        arrival="from_phlegethos_rubble", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_fractured_return", "Phlegethos 5 Return",
        "phlegethos_fractured_way",
        arrival="from_phlegethos_fortress", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_rubble_return", "Phlegethos 4 Return",
        "phlegethos_rubble_pass",
        arrival="from_phlegethos_fortress", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_3_return", "Phlegethos 3 Return", "phlegethos_lake",
        arrival="from_phlegethos_4", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_2_return", "Phlegethos 2 Return", "phlegethos_road",
        arrival="from_phlegethos_3", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    # Phase 9 begins at the bank reached by the completed river cutscene.
    CheckpointDefinition(
        "feywild_riverbank", "Feywild 1", "feywild_riverbank",
        arrival="from_river", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "feywild_2", "Feywild 2", "feywild_blooming_path",
        arrival="from_feywild_1", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_1_return", "Feywild 1 Return", "feywild_riverbank",
        arrival="from_feywild_2", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_3", "Feywild 3", "feywild_pollen_orchard",
        arrival="from_feywild_2", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_4", "Feywild 4", "feywild_rootways",
        arrival="from_feywild_3", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_5", "Feywild 5", "feywild_tea_table",
        arrival="from_feywild_4", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_6", "Feywild 6", "feywild_needle_garden",
        arrival="from_feywild_5", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_7", "Feywild 7", "feywild_moonmoth_fen",
        arrival="from_feywild_6", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_8", "Feywild 8", "feywild_redcap_warrens",
        arrival="from_feywild_7", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_9", "Feywild 9", "feywild_shifting_hedge",
        arrival="from_feywild_8", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_2_return", "Feywild 2 Return",
        "feywild_blooming_path",
        arrival="from_feywild_3", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_3_return", "Feywild 3 Return",
        "feywild_pollen_orchard",
        arrival="from_feywild_4", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_4_return", "Feywild 4 Return", "feywild_rootways",
        arrival="from_feywild_5", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_5_return", "Feywild 5 Return", "feywild_tea_table",
        arrival="from_feywild_6", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_8_return", "Feywild 8 Return", "feywild_redcap_warrens",
        arrival="from_feywild_9", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_7_return", "Feywild 7 Return", "feywild_moonmoth_fen",
        arrival="from_feywild_8", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_10", "Feywild 10", "feywild_displacer_meadow",
        arrival="from_feywild_9", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_9_return", "Feywild 9 Return", "feywild_shifting_hedge",
        arrival="from_feywild_10", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_11", "Feywild 11", "feywild_mushroom_underways",
        arrival="from_feywild_10", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_10_return", "Feywild 10 Return", "feywild_displacer_meadow",
        arrival="from_feywild_11", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_12", "Feywild 12", "feywild_luminous_rapids",
        arrival="from_feywild_11", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_11_return", "Feywild 11 Return", "feywild_mushroom_underways",
        arrival="from_feywild_12", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_13", "Feywild 13", "feywild_twilight_crossroads",
        arrival="from_feywild_12", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_12_return", "Feywild 12 Return",
        "feywild_luminous_rapids",
        arrival="from_feywild_13", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "zephyros_1", "Zephyros 1", "feywild_cloud_staircase",
        arrival="from_feywild_13", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_13_return", "Feywild 13 Return",
        "feywild_twilight_crossroads", arrival="from_feywild_tower",
        facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "zephyros_2", "Zephyros 2", "zephyros_tower_exterior",
        arrival="from_staircase", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "zephyros_3", "Zephyros 3", "zephyros_aerie",
        arrival="from_exterior", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "zephyros_exterior_return", "Zephyros Exterior Return",
        "zephyros_tower_exterior", arrival="from_aerie", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_1", "City Night 1", "modern_city_arrival",
        arrival="from_flight", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_2", "City Night 2", "modern_city_night_2",
        arrival="from_city_night_1", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_1_return", "City Night 1 Return",
        "modern_city_arrival", arrival="from_city_night_2", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_3", "City Night 3", "modern_city_night_3",
        arrival="from_city_night_2", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_2_return", "City Night 2 Return",
        "modern_city_night_2", arrival="from_city_night_3", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_4", "City Night 4", "modern_city_night_4",
        arrival="from_city_night_3", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_3_return", "City Night 3 Return",
        "modern_city_night_3", arrival="from_city_night_4", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_5", "City Night 5", "modern_city_night_5",
        arrival="from_city_night_4", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_4_return", "City Night 4 Return",
        "modern_city_night_4", arrival="from_city_night_5", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_6", "City Night 6", "modern_city_night_6",
        arrival="from_city_night_5", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_5_return", "City Night 5 Return",
        "modern_city_night_5", arrival="from_city_night_6", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_sewer_1", "City Sewer 1", "modern_city_sewer_1",
        arrival="from_city_night_6", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_sewer_2", "City Sewer 2", "modern_city_sewer_2",
        arrival="from_city_sewer_1_culvert", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_sewer_1_return", "City Sewer 1 Return",
        "modern_city_sewer_1", arrival="from_city_sewer_2", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_sewer_3", "City Sewer 3", "modern_city_sewer_3",
        arrival="from_city_sewer_2_drop", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_sewer_4", "City Sewer 4", "modern_city_sewer_4",
        arrival="from_city_sewer_3_west", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_1", "City Day 1", "modern_city_day_1",
        arrival="from_city_sewer_4_ladder", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_2", "City Day 2", "modern_city_day_2",
        arrival="from_city_day_1", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_3", "City Day 3", "modern_city_day_3",
        arrival="from_city_day_2", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_4", "City Day 4", "modern_city_day_4",
        arrival="from_city_day_3", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_5", "City Day 5", "modern_city_day_5",
        arrival="from_city_day_4", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_6", "City Day 6", "modern_city_day_6",
        arrival="from_city_day_5", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "tahuya_exterior", "Cabin Exterior",
        "tahuya_cabin_exterior", arrival="from_doug_fir", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached", "doug_fir_transition_completed",
        }),
        runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "tahuya_interior", "Cabin Interior",
        "tahuya_cabin_interior", arrival="from_front_door", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached", "doug_fir_transition_completed",
        }),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "tahuya_exterior_front_return", "Cabin Front Porch Return",
        "tahuya_cabin_exterior", arrival="from_cabin_front", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached", "doug_fir_transition_completed",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_5_return", "City Day 5 Return",
        "modern_city_day_5", arrival="from_city_day_6", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_4_return", "City Day 4 Return",
        "modern_city_day_4", arrival="from_city_day_5", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_3_return", "City Day 3 Return",
        "modern_city_day_3", arrival="from_city_day_4", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_2_return", "City Day 2 Return",
        "modern_city_day_2", arrival="from_city_day_3", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_day_1_return", "City Day 1 Return",
        "modern_city_day_1", arrival="from_city_day_2", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_sewer_3_return", "City Sewer 3 Return",
        "modern_city_sewer_3", arrival="from_city_sewer_4", facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_sewer_2_return", "City Sewer 2 Return",
        "modern_city_sewer_2", arrival="from_city_sewer_3", facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "modern_city_6_return", "City Night 6 Return",
        "modern_city_night_6", arrival="from_city_sewer_1", facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "feywild_6_return", "Feywild 6 Return", "feywild_needle_garden",
        arrival="from_feywild_7", facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_deck_return", "Ship Return", "ship_deck",
        arrival="from_lower_hold", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_8_return", "Temple 8 Return", "temple_gauntlet",
        arrival="from_temple_9", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_7_return", "Temple 7 Return", "temple_shrine",
        arrival="from_temple_8", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_6_return", "Temple 6 Return", "temple_astral_wind",
        arrival="from_temple_7", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_5_return", "Temple 5 Return", "temple_snakes",
        arrival="from_temple_6", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_4_return", "Temple 4 Return", "temple_darts",
        arrival="from_temple_5", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_3_return", "Temple 3 Return", "temple_skeletons",
        arrival="from_temple_4", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_2_return", "Temple 2 Return", "temple_spikes",
        arrival="from_temple_3", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_1_return", "Temple 1 Return", "temple_entrance",
        arrival="from_temple_2", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_temple_return", "Chult Temple Return", "chult_temple",
        arrival="from_temple_interior", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        development_visible=False, runtime_entry=True,
    ),
    # Internal return entries keep existing local retry positions, but do not
    # clutter the temporary test menu.
    CheckpointDefinition(
        "waterdeep_tavern_return", "Waterdeep Tavern Return",
        "waterdeep_docks", arrival="tavern_return", facing="down",
        required_flags=frozenset({"sewer_completed"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "waterdeep_docks_from_plaza", "Waterdeep Plaza Return",
        "waterdeep_docks", arrival="from_plaza", facing="left",
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "tavern_pantry_return", "Tavern Pantry Return",
        "waterdeep_tavern", arrival="pantry_return", facing="down",
        required_flags=frozenset({"sewer_completed"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "tavern_default", "Tavern Default Spawn", "waterdeep_tavern",
        required_flags=frozenset({"sewer_completed"}),
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "pantry_default", "Pantry Default Spawn", "waterdeep_pantry",
        required_flags=frozenset({"sewer_completed"}),
        development_visible=False, runtime_entry=True,
    ),
    # ----------------------------------------------------------------
    # Phase 13. The desert opens where Phase 12's crossing left him, so
    # both entries are gated on that crossing having happened. The
    # phase document asks for convenient development access to each
    # major section rather than testing every map from the beginning,
    # so the hub's entry is deliberately development-visible.
    # ----------------------------------------------------------------
    CheckpointDefinition(
        "desert_central_start", "Desert Central", "desert_central",
        position=(448.0, 496.0), facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True, fade_in=True, fade_from=(252, 248, 238),
    ),
    # Coming back down out of the camp. Every walk exit needs a runtime
    # checkpoint on the far side naming its arrival; this is the hub's.
    CheckpointDefinition(
        "desert_central_from_orc_camp", "Desert Central North Return",
        "desert_central", arrival="from_orc_camp", facing="down",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_orc_camp", "Orc Camp", "desert_orc_camp",
        arrival="from_desert_central", facing="up",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_central_from_oasis", "Desert Central West Return",
        "desert_central", arrival="from_oasis", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_oasis", "Oasis", "desert_oasis",
        arrival="from_desert_central", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_central_from_ruins", "Desert Central South Return",
        "desert_central", arrival="from_undead_ruins", facing="up",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_undead_ruins", "Undead Ruins", "desert_undead_ruins",
        arrival="from_desert_central", facing="down",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    # ----------------------------------------------------------------
    # ...and east out of the region, into the collided traversal.
    # ----------------------------------------------------------------
    CheckpointDefinition(
        "desert_central_from_east_1", "Desert Central East Return",
        "desert_central", arrival="from_east_1", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_1", "Collided Desert 1", "desert_east_1",
        arrival="from_desert_central", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_1_from_east_2", "Collided Desert 1 East Return",
        "desert_east_1", arrival="from_east_2", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_2", "Collided Desert 2", "desert_east_2",
        arrival="from_east_1", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_2_from_east_3", "Collided Desert 2 East Return",
        "desert_east_2", arrival="from_east_3", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_3", "Collided Desert 3", "desert_east_3",
        arrival="from_east_2", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_3_from_east_4", "Collided Desert 3 East Return",
        "desert_east_3", arrival="from_east_4", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_4", "Collided Desert 4", "desert_east_4",
        arrival="from_east_3", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_4_from_east_5", "Collided Desert 4 East Return",
        "desert_east_4", arrival="from_east_5", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_5", "Collided Desert 5", "desert_east_5",
        arrival="from_east_4", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_5_from_east_6", "Collided Desert 5 East Return",
        "desert_east_5", arrival="from_east_6", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_6", "Collided Desert 6", "desert_east_6",
        arrival="from_east_5", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_6_from_east_7", "Collided Desert 6 East Return",
        "desert_east_6", arrival="from_east_7", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_7", "Collided Desert 7", "desert_east_7",
        arrival="from_east_6", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_7_from_east_8", "Collided Desert 7 East Return",
        "desert_east_7", arrival="from_east_8", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_8", "Collided Desert 8", "desert_east_8",
        arrival="from_east_7", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "desert_east_8_from_trio", "Collided Desert 8 East Return",
        "desert_east_8", arrival="from_trio", facing="left",
        required_flags=DESERT_ENTRY_FLAGS,
        development_visible=False, runtime_entry=True,
    ),
    # The phase document asks for the final trio encounter by name as a
    # development entry, because it is the far end of a very long walk
    # and testing it from the hub is not testing it.
    CheckpointDefinition(
        "desert_trio", "Final Trio Encounter", "desert_trio",
        arrival="from_east_8", facing="right",
        required_flags=DESERT_ENTRY_FLAGS,
        runtime_entry=True,
    ),
)

CHECKPOINT_BY_ID = {checkpoint.checkpoint_id: checkpoint for checkpoint in CHECKPOINTS}


class ProgressState:
    """The deliberately tiny set of durable world-state flags."""

    def __init__(self) -> None:
        self.flags: set[str] = set()

    def replace(self, flags) -> None:
        flags = set(flags)
        unknown = flags - KNOWN_PROGRESS_FLAGS
        if unknown:
            raise ValueError(f"Unknown progress flags: {sorted(unknown)}")
        self.flags = flags

    def enable(self, flag: str) -> None:
        if flag not in KNOWN_PROGRESS_FLAGS:
            raise ValueError(f"Unknown progress flag {flag!r}")
        self.flags.add(flag)

    def has(self, flag: str) -> bool:
        return flag in self.flags


def is_save_point(checkpoint_id: str) -> bool:
    """Is this somewhere a save may be written?

    A door Chuck walked in by, and nothing else: those are the places a
    save code can name, and the door is the respawn point too.
    """
    return checkpoint_id in save_registry.ENTRY_INDEX


class CheckpointLoader:
    """Owns checkpoint selection, initialization, and save restoration."""

    def __init__(self, game: "Game", saves: SaveSystem) -> None:
        self.game = game
        self.saves = saves

    @property
    def development_checkpoints(self) -> tuple[CheckpointDefinition, ...]:
        return tuple(cp for cp in CHECKPOINTS if cp.development_visible)

    def definition(self, checkpoint_id: str) -> CheckpointDefinition:
        try:
            return CHECKPOINT_BY_ID[checkpoint_id]
        except KeyError as exc:
            raise KeyError(f"Unknown checkpoint {checkpoint_id!r}") from exc

    def entry_checkpoint_id(self, map_name: str, arrival: str | None) -> str:
        matches = [
            cp.checkpoint_id for cp in CHECKPOINTS
            if cp.runtime_entry and cp.map_name == map_name and cp.arrival == arrival
        ]
        if len(matches) != 1:
            raise ValueError(
                f"Expected one runtime checkpoint for {map_name!r} arrival "
                f"{arrival!r}, found {matches}"
            )
        return matches[0]

    def set_runtime_checkpoint(self, checkpoint_id: str) -> None:
        """Set the local retry point without writing the player save slot."""
        checkpoint = self.definition(checkpoint_id)
        self.game.progress.flags.update(checkpoint.required_flags)
        self.game.active_checkpoint_id = checkpoint_id
        # A new respawn point: bank the running cigarette total so a
        # later death rewinds exactly to here.
        self.game.cigarettes.commit()

    def load_checkpoint(
        self,
        checkpoint_id: str,
        *,
        progress_flags=None,
        sanity: int | None = None,
        cigarettes: int | None = None,
        deaths: int | None = None,
    ):
        """Rebuild a checkpoint identically for NEW, CONTINUE, or development."""
        from src.scenes.world_scene import WorldScene

        checkpoint = self.definition(checkpoint_id)
        flags = set(checkpoint.required_flags)
        if progress_flags is not None:
            flags.update(progress_flags)
        self.game.progress.replace(flags)
        if cigarettes is not None:
            self.game.cigarettes.replace(cigarettes)
        else:
            # The count is continuous across the whole run: cutscene
            # handoffs and development jumps carry it forward, banking
            # it as the new respawn-point value.
            self.game.cigarettes.commit()
        # Deaths carry through every handoff untouched; only NEW GAME and
        # CONTINUE set them.
        if deaths is not None:
            self.game.deaths.replace(deaths)
        self.game.active_checkpoint_id = checkpoint_id
        scene = WorldScene(
            self.game,
            checkpoint.map_name,
            initial_arrival=checkpoint.arrival,
            initial_position=checkpoint.position,
            initial_facing=checkpoint.facing,
            initial_climb_from_water=checkpoint.climb_from_water,
            initial_sanity=(config.SANITY_START if sanity is None else sanity),
            initial_checkpoint_id=checkpoint_id,
            initial_fade_in=checkpoint.fade_in,
            initial_fade_from=checkpoint.fade_from,
        )
        self.game.scenes.replace(scene)
        return scene

    def new_game(self):
        self.saves.delete()
        self.game.spoken_to.clear()
        return self.load_checkpoint(OPENING_CHECKPOINT_ID, cigarettes=0,
                                    deaths=0)

    @staticmethod
    def can_resume(record: SaveRecord) -> bool:
        """Whether this record names a game this build can actually load.

        Asked of a pasted code before anything is torn down, so a code
        for a door that no longer exists is refused on the menu rather
        than halfway into a load.
        """
        checkpoint = CHECKPOINT_BY_ID.get(record.checkpoint_id)
        return (checkpoint is not None
                and is_save_point(record.checkpoint_id)
                and set(record.progress_flags) <= KNOWN_PROGRESS_FLAGS)

    def valid_save(self) -> SaveRecord | None:
        record = self.saves.load()
        if record is None or not self.can_resume(record):
            return None
        return record

    @property
    def can_continue(self) -> bool:
        return self.valid_save() is not None

    def resume_from(self, record: SaveRecord, *, remember: bool = True):
        """Start playing from a record, wherever it came from.

        `remember` writes it to the local slot, which is what a pasted
        code wants: having loaded it, CONTINUE should come back here and
        not to whatever was on this machine before.
        """
        if not self.can_resume(record):
            return None
        self.game.spoken_to = set(record.spoken)
        if remember:
            self.saves.write(record)
        return self.load_checkpoint(
            record.checkpoint_id,
            progress_flags=record.progress_flags,
            sanity=record.sanity,
            cigarettes=record.cigarettes,
            deaths=record.deaths,
        )

    def continue_game(self):
        record = self.valid_save()
        if record is None:
            return None
        # Already on disk, and already the record we are loading.
        return self.resume_from(record, remember=False)

    def write_save(self, checkpoint_id: str, sanity: int) -> bool:
        """Persist durable resume state at a door Chuck has walked in by.

        The door is the save point and the respawn point both, so this
        is the only thing that writes the slot. It refuses anything that
        is not in the save registry, because a record it cannot write as
        a code is a record that cannot leave the machine it is on.
        """
        self.definition(checkpoint_id)
        if not is_save_point(checkpoint_id):
            raise ValueError(
                f"Checkpoint {checkpoint_id!r} is not a save point")
        self.set_runtime_checkpoint(checkpoint_id)
        return self.saves.write(self.current_record(checkpoint_id, sanity))

    def current_record(self, checkpoint_id: str, sanity: int) -> SaveRecord:
        """The game as it stands, whether or not it is being written down.

        The menu needs this twice over: once for the slot on disk and
        once for the code it puts on screen, and the two must be the
        same game or the code is a lie.
        """
        return SaveRecord(
            checkpoint_id=checkpoint_id,
            sanity=sanity,
            progress_flags=tuple(sorted(self.game.progress.flags)),
            cigarettes=self.game.cigarettes.total,
            deaths=self.game.deaths.total,
            spoken=tuple(sorted(
                (str(map_name), int(x), int(y), str(line))
                for map_name, x, y, line in self.game.spoken_to)),
        )

