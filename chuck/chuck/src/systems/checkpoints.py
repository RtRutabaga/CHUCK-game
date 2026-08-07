"""Authored checkpoints and the one shared checkpoint-loading path.

NEW GAME, CONTINUE, and the temporary development selector all choose an ID
from this registry and call CheckpointLoader.load_checkpoint(). Map transitions
also use registry entries to preserve the established local-respawn behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.core import config
from src.systems.captain_confrontation import CAPTAIN_REQUIRED_FLAGS
from src.systems.save import SaveRecord, SaveSystem

if TYPE_CHECKING:
    from src.core.game import Game


KNOWN_PROGRESS_FLAGS = frozenset({
    "sewer_completed",
    "chult_reached",
    "crew_pirate_met",
    "pirate_chef_met",
    "captain_chest_opened",
    "captain_chest_carton_collected",
    "deck_concertina_met",
    "deck_cheering_met",
    "deck_dancer_met",
    "deck_jeffries_met",
    "captain_confronted",
    "feywild_reached",
    "modern_city_reached",
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
    saveable: bool = False
    development_visible: bool = True
    runtime_entry: bool = False
    fade_in: bool = False


CHECKPOINTS = (
    CheckpointDefinition(
        "waterdeep_start", "Waterdeep 1", "waterdeep_docks",
        facing="down", runtime_entry=True,
    ),
    CheckpointDefinition(
        "waterdeep_anchor", "Waterdeep Ashtray", "waterdeep_docks",
        position=(372.0, 421.0), facing="down", saveable=True,
    ),
    CheckpointDefinition(
        "sewer_entrance", "Sewer 1", "sewer",
        facing="down", runtime_entry=True,
    ),
    CheckpointDefinition(
        "sewer_anchor", "Sewer 2", "sewer",
        position=(196.0, 917.0), facing="down", saveable=True,
    ),
    CheckpointDefinition(
        "waterdeep_return", "Waterdeep 2", "waterdeep_docks",
        arrival="sewer_outflow", facing="up", climb_from_water=True,
        required_flags=frozenset({"sewer_completed"}), runtime_entry=True,
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
        "chult_anchor", "Chult 1", "chult_jungle",
        position=(500.0, 837.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True,
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
        "chult_2_anchor", "Chult 2 Ashtray", "chult_cog",
        position=(644.0, 1157.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "chult_3", "Chult 3", "chult_run",
        arrival="from_chult_2", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_3_anchor", "Chult 3 Ashtray", "chult_run",
        position=(324.0, 501.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "chult_4", "Chult 4", "chult_respite",
        arrival="from_chult_3", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_4_anchor", "Chult 4 Ashtray", "chult_respite",
        position=(132.0, 805.0), facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "chult_5", "Chult 5", "chult_temple",
        arrival="from_chult_4", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "chult_5_anchor", "Chult 5 Ashtray", "chult_temple",
        position=(436.0, 693.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_1", "Temple 1", "temple_entrance",
        arrival="from_temple_exterior", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_1_anchor", "Temple 1 Ashtray", "temple_entrance",
        position=(372.0, 501.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_2", "Temple 2", "temple_spikes",
        arrival="from_temple_1", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_2_anchor", "Temple 2 Ashtray", "temple_spikes",
        position=(372.0, 613.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_3", "Temple 3", "temple_skeletons",
        arrival="from_temple_2", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_3_anchor", "Temple 3 Ashtray", "temple_skeletons",
        position=(436.0, 597.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_4", "Temple 4", "temple_darts",
        arrival="from_temple_3", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_4_anchor", "Temple 4 Ashtray", "temple_darts",
        position=(980.0, 229.0), facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_5", "Temple 5", "temple_snakes",
        arrival="from_temple_4", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_5_anchor", "Temple 5 Ashtray", "temple_snakes",
        position=(788.0, 293.0), facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_6", "Temple 6", "temple_astral_wind",
        arrival="from_temple_5", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_6_anchor", "Temple 6 Ashtray", "temple_astral_wind",
        position=(276.0, 117.0), facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_7", "Temple 7", "temple_shrine",
        arrival="from_temple_6", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_7_anchor", "Temple 7 Ashtray", "temple_shrine",
        position=(420.0, 581.0), facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_8", "Temple 8", "temple_gauntlet",
        arrival="from_temple_7", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_8_anchor", "Temple 8 Ashtray", "temple_gauntlet",
        position=(292.0, 405.0), facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_9", "Temple 9", "temple_sanctum",
        arrival="from_temple_8", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "temple_9_anchor", "Temple 9 Ashtray", "temple_sanctum",
        position=(820.0, 437.0), facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "temple_rubble", "Rubble 1", "temple_rubble",
        arrival="from_fireball", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "temple_rubble_anchor", "Rubble Ashtray", "temple_rubble",
        position=(356.0, 389.0), facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "ship_deck", "Ship 1", "ship_deck",
        arrival="from_crawlspace", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True, fade_in=True,
    ),
    CheckpointDefinition(
        "ship_deck_anchor", "Ship Ashtray", "ship_deck",
        position=(116.0, 117.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "ship_lower_hold", "Ship Hold", "ship_lower_hold",
        arrival="from_ship_room", facing="down",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_lower_hold_anchor", "Ship Hold Ashtray", "ship_lower_hold",
        position=(280.0, 360.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "ship_galley", "Ship Galley", "ship_galley",
        arrival="from_ship_room", facing="left",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "ship_galley_anchor", "Ship Galley Ashtray", "ship_galley",
        position=(116.0, 229.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
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
        "ship_crew_anchor", "Ship Crew Ashtray", "ship_crew_quarters",
        position=(116.0, 181.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
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
        "ship_captain_anchor", "Ship Captain Ashtray",
        "ship_captain_cabin", position=(100.0, 229.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
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
        "ship_exterior_anchor", "Ship Exterior Ashtray",
        "ship_exterior_deck", position=(436.0, 437.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
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
        "phlegethos_anchor", "Phlegethos Ashtray", "phlegethos_arrival",
        position=(340.0, 389.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "phlegethos_road", "Phlegethos 2", "phlegethos_road",
        arrival="from_phlegethos_1", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_road_anchor", "Phlegethos 2 Ashtray", "phlegethos_road",
        position=(388.0, 405.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
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
        "phlegethos_lake_anchor", "Phlegethos 3 Ashtray", "phlegethos_lake",
        position=(276.0, 453.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "phlegethos_rubble_pass", "Phlegethos 4",
        "phlegethos_rubble_pass",
        arrival="from_phlegethos_3", facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_rubble_anchor", "Phlegethos 4 Ashtray",
        "phlegethos_rubble_pass",
        position=(180.0, 405.0), facing="right",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
    ),
    CheckpointDefinition(
        "phlegethos_fortress_approach", "Phlegethos 5",
        "phlegethos_fortress_approach",
        arrival="from_phlegethos_rubble", facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        runtime_entry=True,
    ),
    CheckpointDefinition(
        "phlegethos_4_anchor", "Phlegethos 5 Ashtray",
        "phlegethos_fortress_approach",
        position=(324.0, 453.0), facing="up",
        required_flags=frozenset({"sewer_completed", "chult_reached"}),
        saveable=True, development_visible=False,
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
        "feywild_anchor", "Feywild Ashtray", "feywild_riverbank",
        position=(324.0, 437.0), facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_2_anchor", "Feywild 2 Ashtray",
        "feywild_blooming_path",
        position=(164.0, 533.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_3_anchor", "Feywild 3 Ashtray",
        "feywild_pollen_orchard",
        position=(195.0, 692.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_4_anchor", "Feywild 4 Ashtray", "feywild_rootways",
        position=(180.0, 661.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_5_anchor", "Feywild 5 Ashtray", "feywild_tea_table",
        position=(276.0, 85.0), facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_6_anchor", "Feywild 6 Ashtray",
        "feywild_needle_garden",
        position=(260.0, 101.0), facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_7_anchor", "Feywild 7 Ashtray", "feywild_moonmoth_fen",
        position=(116.0, 325.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_8_anchor", "Feywild 8 Ashtray", "feywild_redcap_warrens",
        position=(1060.0, 453.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_9_anchor", "Feywild 9 Ashtray", "feywild_shifting_hedge",
        position=(132.0, 357.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_10_anchor", "Feywild 10 Ashtray", "feywild_displacer_meadow",
        position=(356.0, 549.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_11_anchor", "Feywild 11 Ashtray",
        "feywild_mushroom_underways",
        position=(548.0, 373.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_12_anchor", "Feywild 12 Ashtray", "feywild_luminous_rapids",
        position=(532.0, 341.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "feywild_13_anchor", "Feywild 13 Ashtray",
        "feywild_twilight_crossroads",
        position=(612.0, 709.0), facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "zephyros_staircase_anchor", "Zephyros 1 Ashtray",
        "feywild_cloud_staircase", position=(836.0, 533.0), facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "zephyros_exterior_anchor", "Zephyros 2 Ashtray",
        "zephyros_tower_exterior", position=(276.0, 405.0), facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "zephyros_aerie_anchor", "Zephyros 3 Ashtray",
        "zephyros_aerie", position=(372.0, 613.0), facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
        }),
        saveable=True, development_visible=False,
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
        "modern_city_anchor", "City Night 1 Ashtray", "modern_city_arrival",
        position=(436.0, 693.0), facing="down",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        saveable=True, development_visible=False, fade_in=True,
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
        "modern_city_2_anchor", "City Night 2 Ashtray",
        "modern_city_night_2", position=(484.0, 757.0), facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        saveable=True, development_visible=False,
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
        "modern_city_3_anchor", "City Night 3 Ashtray",
        "modern_city_night_3", position=(116.0, 533.0), facing="right",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        saveable=True, development_visible=False,
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
        "modern_city_4_anchor", "City Night 4 Ashtray",
        "modern_city_night_4", position=(580.0, 821.0), facing="up",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        saveable=True, development_visible=False,
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
        "modern_city_5_anchor", "City Night 5 Ashtray",
        "modern_city_night_5", position=(1668.0, 389.0), facing="left",
        required_flags=frozenset({
            "sewer_completed", "chult_reached", "feywild_reached",
            "modern_city_reached",
        }),
        saveable=True, development_visible=False,
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
        )
        self.game.scenes.replace(scene)
        return scene

    def new_game(self):
        self.saves.delete()
        return self.load_checkpoint(OPENING_CHECKPOINT_ID, cigarettes=0)

    def valid_save(self) -> SaveRecord | None:
        record = self.saves.load()
        if record is None:
            return None
        checkpoint = CHECKPOINT_BY_ID.get(record.checkpoint_id)
        if checkpoint is None or not checkpoint.saveable:
            return None
        if not set(record.progress_flags) <= KNOWN_PROGRESS_FLAGS:
            return None
        return record

    @property
    def can_continue(self) -> bool:
        return self.valid_save() is not None

    def continue_game(self):
        record = self.valid_save()
        if record is None:
            return None
        return self.load_checkpoint(
            record.checkpoint_id,
            progress_flags=record.progress_flags,
            sanity=record.sanity,
            cigarettes=record.cigarettes,
        )

    def activate_checkpoint(self, checkpoint_id: str, sanity: int) -> bool:
        """Attune an authored Anchor and persist only durable resume state."""
        checkpoint = self.definition(checkpoint_id)
        if not checkpoint.saveable:
            raise ValueError(f"Checkpoint {checkpoint_id!r} is not an Ashtray")
        self.set_runtime_checkpoint(checkpoint_id)
        record = SaveRecord(
            checkpoint_id=checkpoint_id,
            sanity=sanity,
            progress_flags=tuple(sorted(self.game.progress.flags)),
            cigarettes=self.game.cigarettes.total,
        )
        return self.saves.write(record)
