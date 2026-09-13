"""Standing props — barrels and crates that Chuck walks behind.

A Prop is a drawable, not a full Entity: it never updates, and its
collision is the solid tile beneath it (the TileMap owns that). A few
props respond to the interact key with a single line (PROP_DIALOGUE):
Bobert snores; the sign says what signs say. He still never wakes,
never gets a name on screen, never becomes a character. Its
job is purely visual: render taller than its tile, anchored at the
tile's bottom edge, and participate in the y-sorted draw so characters
pass in front of and behind it correctly.

Scale note (Game Bible): a barrel is 19px to Chuck's 14. To Chuck,
standing at a barrel is standing at a building. Good.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core import config

if TYPE_CHECKING:
    from src.core.assets import AssetManager

_SPRITES = {
    "barrel": "objects/barrel.png",
    "crate": "objects/crate.png",
    "bobert_barrel": "objects/bobert_barrel.png",
    "herod_sign": "objects/herod_sign.png",
    "tavern_door": "objects/tavern_door.png",
    "tavern_open": "objects/tavern_open.png",
    "tavern_table": "objects/tavern_table.png",
    "tavern_chair": "objects/tavern_chair.png",
    "bar_counter": "objects/bar_counter.png",
    "tavern_hearth": "objects/tavern_hearth.png",
    "cheese": "objects/cheese.png",
    "pantry_door": "objects/pantry_door.png",
    "pantry_open": "objects/pantry_open.png",
    "pantry_shelf": "objects/pantry_shelf.png",
    "grain_sack": "objects/grain_sack.png",
    "ship_hammock": "objects/ship_hammock.png",
    "ship_captain_bed": "objects/ship_captain_bed.png",
    "ship_captain_rug": "objects/ship_captain_rug.png",
    "ship_round_table": "objects/ship_round_table.png",
    "ship_mast_sail": "objects/ship_mast_sail.png",
    "ship_helm": "objects/ship_helm.png",
    "ship_bowsprit": "objects/ship_bowsprit.png",
    # Below-decks dressing: the captain's study, the galley's working
    # gear, and the rope and lashed cargo every deck of a ship has lying
    # about.
    "ship_bookshelf": "objects/ship_bookshelf.png",
    "ship_writing_desk": "objects/ship_writing_desk.png",
    "ship_butcher_block": "objects/ship_butcher_block.png",
    "ship_stew_pot": "objects/ship_stew_pot.png",
    "ship_rope_coil": "objects/ship_rope_coil.png",
    "ship_cargo_stack": "objects/ship_cargo_stack.png",
    "chimney": "objects/chimney.png",
    "sewer_grate": "objects/sewer_grate.png",
    "house_door": "objects/house_door.png",
    "stall_post": "objects/stall_post.png",
    "stall_table": "objects/stall_table.png",
    "crate_green": "objects/crate_green.png",
    "crate_red": "objects/crate_red.png",
    "crate_orange": "objects/crate_orange.png",
    "jungle_tree": (
        "objects/jungle_tree_1.png",
        "objects/jungle_tree_2.png",
        "objects/jungle_tree_3.png",
    ),
    "jungle_shrub": (
        "objects/jungle_shrub_1.png",
        "objects/jungle_shrub_2.png",
        "objects/jungle_shrub_3.png",
    ),
    # The jungle floor: what fell off the jungle, and off the temple's
    # builders. Plus Chult's own great trees.
    "chult_fern": tuple(f"objects/chult_fern_{i + 1}.png" for i in range(3)),
    "chult_leaf_litter": tuple(
        f"objects/chult_leaf_litter_{i + 1}.png" for i in range(3)),
    "chult_fallen_log": tuple(
        f"objects/chult_fallen_log_{i + 1}.png" for i in range(3)),
    "chult_ruin_fragment": tuple(
        f"objects/chult_ruin_fragment_{i + 1}.png" for i in range(3)),
    "chult_great_tree": tuple(
        f"objects/chult_great_tree_{i + 1}.png" for i in range(3)),
    # Phase 13's desert dressing. Tuples, so the variant is chosen from
    # the tile's own position -- three column heights, three heaps, three
    # palms -- and a run of them never repeats in a straight line.
    "desert_column": (
        "objects/desert_column_1.png",
        "objects/desert_column_2.png",
        "objects/desert_column_3.png",
    ),
    # The order the building was actually built at, rather than the
    # pieces that came off it: twenty-eight across and up to seven
    # tiles tall, on a one-tile footprint so it can stand anywhere the
    # small ones could.
    "desert_great_pillar": (
        "objects/desert_great_pillar_1.png",
        "objects/desert_great_pillar_2.png",
        "objects/desert_great_pillar_3.png",
    ),
    # ...and the one piece of it still whole. Five tiles across, and
    # Chuck walks through the middle of it.
    "desert_ruin_arch": "objects/desert_ruin_arch.png",
    "desert_column_fallen": (
        "objects/desert_column_fallen_1.png",
        "objects/desert_column_fallen_2.png",
        "objects/desert_column_fallen_3.png",
    ),
    "desert_rubble": (
        "objects/desert_rubble_1.png",
        "objects/desert_rubble_2.png",
        "objects/desert_rubble_3.png",
    ),
    "desert_palm": (
        "objects/desert_palm_1.png",
        "objects/desert_palm_2.png",
        "objects/desert_palm_3.png",
    ),
    # Animated; the entry here is the first frame, which is what the
    # constructor validates the kind against.
    "desert_fire_pit": "objects/desert_fire_pit_1.png",
    # Something very large that died in the hub's sand, and the orc
    # camp's tents, weapon racks and war drum.
    "desert_ribcage": "objects/desert_ribcage.png",
    "orc_tent": tuple(f"objects/orc_tent_{i + 1}.png" for i in range(3)),
    "orc_weapon_rack": tuple(
        f"objects/orc_weapon_rack_{i + 1}.png" for i in range(2)),
    "orc_war_drum": "objects/orc_war_drum.png",
    "sailing_cog": "objects/sailing_cog.png",
    # Phase 14 reuses the established cog silhouette as dockside scenery.
    "waterdeep_docked_ship": "objects/sailing_cog.png",
    "waterdeep_fountain": "objects/waterdeep_fountain_1.png",
    "waterdeep_closed_gate": "objects/waterdeep_closed_gate.png",
    # A square tower either side of the gate, a tile proud of the wall,
    # and the watch's banners along it.
    "waterdeep_gate_tower": "objects/waterdeep_gate_tower.png",
    "waterdeep_banner": "objects/waterdeep_banner_1.png",
    "tavern_keg_rack": "objects/tavern_keg_rack.png",
    "tavern_notice_board": "objects/tavern_notice_board.png",
    "tavern_rug": "objects/tavern_rug.png",
    "pantry_sack_pile": "objects/pantry_sack_pile.png",
    "pantry_produce_basket": "objects/pantry_produce_basket.png",
    "waterdeep_forge": "objects/waterdeep_forge.png",
    "waterdeep_anvil": "objects/waterdeep_anvil.png",
    "waterdeep_alchemist_display": (
        "objects/waterdeep_alchemist_display.png"
    ),
    "skull_stake": "objects/skull_stake.png",
    "temple_arch_ns": "objects/temple_arch_ns.png",
    "temple_arch_ew": "objects/temple_arch_ew.png",
    "temple_gate": "objects/temple_gate.png",
    "temple_skull": "objects/temple_skull.png",
    "temple_monument": (
        "objects/temple_monument_1.png",
        "objects/temple_monument_2.png",
    ),
    "temple_serpent_monument": (
        "objects/temple_serpent_monument_1.png",
        "objects/temple_serpent_monument_2.png",
    ),
    # Temple interior dressing (mute, y-sorted; the temple's version of
    # the docks' stall and the jungle's trees). Tuples vary by position.
    "temple_idol": (
        "objects/temple_idol_1.png",
        "objects/temple_idol_2.png",
    ),
    "temple_stela": (
        "objects/temple_stela_1.png",
        "objects/temple_stela_2.png",
    ),
    "temple_urn": (
        "objects/temple_urn_1.png",
        "objects/temple_urn_2.png",
        "objects/temple_urn_3.png",
    ),
    "temple_column": (
        "objects/temple_column_1.png",
        "objects/temple_column_2.png",
    ),
    # The temple's damage and leftovers (tools/temple_dressing.py).
    "temple_floor_crack": tuple(
        f"objects/temple_floor_crack_{i + 1}.png" for i in range(3)),
    "temple_missing_slabs": tuple(
        f"objects/temple_missing_slabs_{i + 1}.png" for i in range(2)),
    "temple_moss": tuple(f"objects/temple_moss_{i + 1}.png" for i in range(3)),
    "temple_bones": tuple(
        f"objects/temple_bones_{i + 1}.png" for i in range(3)),
    "temple_wall_carving": tuple(
        f"objects/temple_wall_carving_{i + 1}.png" for i in range(3)),
    "temple_toppled_pillar": tuple(
        f"objects/temple_toppled_pillar_{i + 1}.png" for i in range(3)),
    "temple_pillar_stump": tuple(
        f"objects/temple_pillar_stump_{i + 1}.png" for i in range(3)),
    "temple_grand_arch": "objects/temple_grand_arch.png",
    "temple_rubble_block": tuple(
        f"objects/temple_rubble_block_{i + 1}.png" for i in range(12)
    ),
    "phlegethos_statue": (
        "objects/phlegethos_statue_1.png",
        "objects/phlegethos_statue_2.png",
    ),
    "phlegethos_rubble": tuple(
        f"objects/phlegethos_rubble_{i + 1}.png" for i in range(10)
    ),
    "phlegethos_lava_fall": "objects/phlegethos_lava_fall.png",
    # Hell's leftovers (tools/phlegethos_dressing.py), and the fortress's
    # towers and banners.
    "phlegethos_ember_crack": tuple(
        f"objects/phlegethos_ember_crack_{i + 1}.png" for i in range(3)),
    "phlegethos_vent": "objects/phlegethos_vent_1.png",
    "phlegethos_bone_heap": tuple(
        f"objects/phlegethos_bone_heap_{i + 1}.png" for i in range(3)),
    "phlegethos_iron_spikes": tuple(
        f"objects/phlegethos_iron_spikes_{i + 1}.png" for i in range(3)),
    "phlegethos_fortress_tower": "objects/phlegethos_fortress_tower.png",
    "phlegethos_banner": "objects/phlegethos_banner_1.png",
    # Chult's rounded tree/shrub silhouettes, washed with a subtle violet
    # sheen, plus one deliberately ordinary oak so the region reads as a
    # wood rather than a field of blocks (Phase 9 vegetation pass).
    "feywild_grove_tree": (
        "objects/feywild_grove_tree_1.png",
        "objects/feywild_grove_tree_2.png",
        "objects/feywild_grove_tree_3.png",
    ),
    "feywild_shrub": (
        "objects/feywild_shrub_1.png",
        "objects/feywild_shrub_2.png",
        "objects/feywild_shrub_3.png",
    ),
    # Where the Feywild's root walls gather into a knot.
    "fey_root_knot": (
        "objects/fey_root_knot_1.png",
        "objects/fey_root_knot_2.png",
        "objects/fey_root_knot_3.png",
    ),
    # Eleven tiles across and fourteen tall: the Feywild's old trees.
    "feywild_great_tree": (
        "objects/feywild_great_tree_1.png",
        "objects/feywild_great_tree_2.png",
        "objects/feywild_great_tree_3.png",
    ),
    "feywild_oak": (
        "objects/feywild_oak_1.png",
        "objects/feywild_oak_2.png",
        "objects/feywild_oak_3.png",
    ),
    # The redcap camp's gear, all of it gnome-sized and therefore enormous
    # next to Chuck: kicked-off boots, a cooking pot, a planted sickle he
    # can walk under, and crude hide shelters.
    "redcap_boot": (
        "objects/redcap_boot_1.png",
        "objects/redcap_boot_2.png",
        "objects/redcap_boot_3.png",
    ),
    "redcap_shelter": (
        "objects/redcap_shelter_1.png",
        "objects/redcap_shelter_2.png",
    ),
    "redcap_cauldron": "objects/redcap_cauldron.png",
    "redcap_sickle": "objects/redcap_sickle.png",
    "feywild_tree": (
        "objects/feywild_tree_1.png",
        "objects/feywild_tree_2.png",
        "objects/feywild_tree_3.png",
    ),
    "feywild_spiral": (
        "objects/feywild_spiral_1.png",
        "objects/feywild_spiral_2.png",
        "objects/feywild_spiral_3.png",
    ),
    "feywild_mushroom": (
        "objects/feywild_mushroom_1.png",
        "objects/feywild_mushroom_2.png",
        "objects/feywild_mushroom_3.png",
    ),
    # Lanterns along the Feywild's paths, stones at their edges, and the
    # fen's lily pads and reeds (tools/feywild_path_dressing.py).
    "fey_lantern_teal": "objects/fey_lantern_teal_1.png",
    "fey_lantern_violet": "objects/fey_lantern_violet_1.png",
    "fey_path_stones": tuple(
        f"objects/fey_path_stones_{i + 1}.png" for i in range(3)),
    "fen_lily_pads": tuple(
        f"objects/fen_lily_pads_{i + 1}.png" for i in range(3)),
    "fen_reeds": tuple(f"objects/fen_reeds_{i + 1}.png" for i in range(3)),
    "cloud_staircase": "objects/cloud_staircase.png",
    "cloud_tower_arch": "objects/cloud_tower_arch.png",
    "griffon_nest": "objects/griffon_nest.png",
    "aerie_rope": "objects/aerie_rope.png",
    "city_bottles": (
        "objects/city_bottles_1.png",
        "objects/city_bottles_2.png",
    ),
    "city_sewer_entrance": "objects/city_sewer_entrance.png",
    # The collided desert's castle. Four frames of a slow lift rather
    # than a flap: nothing else out there moves in a wind, so cloth that
    # snapped would be moving for its own reasons.
    "castle_turret": "objects/castle_turret.png",
    "castle_banner": (
        "objects/castle_banner_1.png",
        "objects/castle_banner_2.png",
        "objects/castle_banner_3.png",
        "objects/castle_banner_4.png",
    ),
    "city_fire_hydrant": "objects/city_fire_hydrant.png",
    "city_stop_sign": "objects/city_stop_sign.png",
    # One lamp, two states. A street light is off all day and on all
    # night; the world picks between these at spawn the same way the
    # cabin's table picks its woken sprite.
    "city_streetlight": "objects/city_streetlight.png",
    "city_streetlight_lit": "objects/city_streetlight_lit.png",
    "city_bus_stop": "objects/city_bus_stop.png",
    # A little more furniture (tools/generate_city_map_common.py's
    # furnish_street and furnish_sewer).
    "city_bench": "objects/city_bench.png",
    "city_litter_bin": "objects/city_litter_bin.png",
    "city_neon_bar": "objects/city_neon_1_1.png",
    "city_neon_open": "objects/city_neon_2_1.png",
    "city_neon_24h": "objects/city_neon_3_1.png",
    "city_steam_grate": "objects/city_steam_grate_1.png",
    "sewer_pipe": tuple(f"objects/sewer_pipe_{i + 1}.png" for i in range(2)),
    "sewer_graffiti": tuple(
        f"objects/sewer_graffiti_{i + 1}.png" for i in range(3)),
    "city_planar_portal": "objects/city_planar_portal_1.png",
    "tahuya_fir": (
        "objects/tahuya_fir_1.png",
        "objects/tahuya_fir_2.png",
        "objects/tahuya_fir_3.png",
    ),
    # Understory. Three cuts of each, picked by tile rather than
    # animated, so a stand of them never repeats in a visible rhythm.
    "tahuya_salal": (
        "objects/tahuya_salal_1.png",
        "objects/tahuya_salal_2.png",
        "objects/tahuya_salal_3.png",
    ),
    "tahuya_huckleberry": (
        "objects/tahuya_huckleberry_1.png",
        "objects/tahuya_huckleberry_2.png",
        "objects/tahuya_huckleberry_3.png",
    ),
    "tahuya_mushroom_light": "objects/tahuya_mushroom_light_1.png",
    "tahuya_firepit": "objects/tahuya_firepit_1.png",
    "tahuya_ufo": "objects/tahuya_ufo.png",
    "tahuya_firewood_shed": "objects/tahuya_firewood_shed.png",
    "tahuya_cabin": "objects/tahuya_cabin.png",
    "cabin_big_couch": "objects/cabin_big_couch.png",
    "cabin_couch": "objects/cabin_couch.png",
    "cabin_chair": "objects/cabin_chair.png",
    "cabin_table": "objects/cabin_table.png",
    "cabin_table_awakened": "objects/cabin_table_awakened_1.png",
    "cabin_connector_shelf": "objects/cabin_connector_shelf.png",
    "cabin_mini_fridge": "objects/cabin_mini_fridge.png",
    "cabin_closed_door_west": "objects/cabin_closed_door_west.png",
    "cabin_closed_door_north": "objects/cabin_closed_door_north.png",
    "cabin_macrame": "objects/cabin_macrame.png",
    "cabin_side_table": "objects/cabin_side_table.png",
    "cabin_goose_mount": "objects/cabin_goose_mount.png",
    "cabin_lava_lamp": "objects/cabin_lava_lamp_1.png",
    "cabin_curtain_window": (
        "objects/cabin_curtain_window_1.png",
        "objects/cabin_curtain_window_2.png",
        "objects/cabin_curtain_window_3.png",
    ),
    "cabin_kitchen": "objects/cabin_kitchen.png",
    "cabin_woodstove": "objects/cabin_woodstove_1.png",
    "cabin_wood_storage": "objects/cabin_wood_storage.png",
    "fey_table_leg": (
        "objects/fey_table_leg_1.png",
        "objects/fey_table_leg_2.png",
    ),
    "fey_plate": "objects/fey_plate.png",
    "fey_teacup": "objects/fey_teacup.png",
    "fey_napkin": "objects/fey_napkin.png",
    "fey_crumbs": (
        "objects/fey_crumbs_1.png",
        "objects/fey_crumbs_2.png",
        "objects/fey_crumbs_3.png",
    ),
}

_ANIMATED_SPRITES = {
    "phlegethos_lava_fall": (
        "objects/phlegethos_lava_fall.png",
        "objects/phlegethos_lava_fall_2.png",
        "objects/phlegethos_lava_fall_3.png",
        "objects/phlegethos_lava_fall_4.png",
    ),
    "city_planar_portal": tuple(
        f"objects/city_planar_portal_{index + 1}.png" for index in range(12)
    ),
    "tahuya_mushroom_light": tuple(
        f"objects/tahuya_mushroom_light_{index + 1}.png"
        for index in range(8)
    ),
    "tahuya_firepit": tuple(
        f"objects/tahuya_firepit_{index + 1}.png" for index in range(6)
    ),
    "cabin_table_awakened": tuple(
        f"objects/cabin_table_awakened_{index + 1}.png"
        for index in range(8)
    ),
    "cabin_woodstove": tuple(
        f"objects/cabin_woodstove_{index + 1}.png" for index in range(6)
    ),
    # The blobs drift on their own cycles rather than pulsing together,
    # so six frames is enough for the lamp never to look like it loops.
    "cabin_lava_lamp": tuple(
        f"objects/cabin_lava_lamp_{index + 1}.png" for index in range(6)
    ),
    # The orc camp's fires. Animated only so the embers breathe: the
    # fires are out, and a pit whose flames leap is a camp somebody is
    # still sitting at.
    "desert_fire_pit": tuple(
        f"objects/desert_fire_pit_{index + 1}.png" for index in range(6)
    ),
    "waterdeep_fountain": tuple(
        f"objects/waterdeep_fountain_{index + 1}.png" for index in range(4)
    ),
    # The collided desert's castle. Four frames of a slow lift rather
    # than a flap: nothing else out there moves in a wind, so cloth that
    # snapped would be moving for its own reasons.
    "castle_banner": tuple(
        f"objects/castle_banner_{index + 1}.png" for index in range(4)
    ),
    "waterdeep_banner": tuple(
        f"objects/waterdeep_banner_{index + 1}.png" for index in range(4)
    ),
    "phlegethos_banner": tuple(
        f"objects/phlegethos_banner_{index + 1}.png" for index in range(4)
    ),
    "phlegethos_vent": tuple(
        f"objects/phlegethos_vent_{index + 1}.png" for index in range(6)
    ),
    "fey_lantern_teal": tuple(
        f"objects/fey_lantern_teal_{index + 1}.png" for index in range(4)
    ),
    "fey_lantern_violet": tuple(
        f"objects/fey_lantern_violet_{index + 1}.png" for index in range(4)
    ),
    "city_neon_bar": tuple(
        f"objects/city_neon_1_{index + 1}.png" for index in range(4)
    ),
    "city_neon_open": tuple(
        f"objects/city_neon_2_{index + 1}.png" for index in range(4)
    ),
    "city_neon_24h": tuple(
        f"objects/city_neon_3_{index + 1}.png" for index in range(4)
    ),
    "city_steam_grate": tuple(
        f"objects/city_steam_grate_{index + 1}.png" for index in range(6)
    ),
}
_PROP_FRAME_TIME = 0.14
# Props whose animation runs at its own pace. A lava lamp shares nothing
# with a fire but the fact that both move: at the stove's frame rate its
# blobs shot up and down like a boiling kettle.
_PROP_FRAME_TIMES = {
    "cabin_lava_lamp": 1.6,
    "waterdeep_fountain": 0.24,
    # Smoke is slow.
    "phlegethos_vent": 0.22,
    # A breath, not a flicker.
    "fey_lantern_teal": 0.45,
    "fey_lantern_violet": 0.45,
    # Mostly lit, with the odd stutter.
    "city_neon_bar": 0.5,
    "city_neon_open": 0.61,
    "city_neon_24h": 0.55,
    "city_steam_grate": 0.2,
}

# Props that respond to the interact key with a line of dialogue
# (ids live in data/dialogue/). Everything else stays mute scenery.
PROP_DIALOGUE = {
    "bobert_barrel": "bobert_sleeping",  # he does not wake up
    "herod_sign": "herod_sign",
    "house_door": "closed_door",
    "cabin_closed_door_west": "closed_door",
    "cabin_closed_door_north": "closed_door",
    "cabin_goose_mount": "cabin_goose_mount",
    # The cabin is a room worth looking at rather than walking through,
    # so the things in it that reward a look have something to say.
    "cabin_table": "cabin_table_map",
    "cabin_table_awakened": "cabin_table_map",
    "cabin_mini_fridge": "cabin_fridge",
    "cabin_lava_lamp": "cabin_lava_lamp",
    "cabin_woodstove": "cabin_woodstove",
    "cabin_macrame": "cabin_macrame",
    # The fire outside is the same fire, laid by the same hands.
    "tahuya_firepit": "cabin_woodstove",
    "tahuya_ufo": "tahuya_ufo",
    "waterdeep_closed_gate": "plaza_gate",
    "cheese": "cheese",
    "fey_teacup": "fey_tea_warm",
    "fey_plate": "fey_set_for_one",
}

# Props that ask a question instead of making a statement (ids live in
# data/choices/). A prop has a line or a choice, never both.
PROP_CHOICE = {
    "sewer_grate": "sewer_grate",
}

# Ground scatter that stays mute. Ferns, leaf litter, cracks, moss, loose
# bones, ember cracks, path-edge stones and lily pads are laid down by the
# dozen, and a line on each would put an E prompt under every other step
# and crowd out the things that have something to say. Everything else
# answers E like any other prop.
MUTE_PROPS: frozenset[str] = frozenset({
    "chult_fern",
    "chult_leaf_litter",
    "temple_floor_crack",
    "temple_missing_slabs",
    "temple_moss",
    "temple_bones",
    "phlegethos_ember_crack",
    "fey_path_stones",
    "fen_lily_pads",
})

# Props that lie flat on the ground: drawn under everybody, never sorted.
FLOOR_PROPS: frozenset[str] = frozenset({
    "ship_captain_rug",
    "ship_rope_coil",
    "tavern_rug",
    "chult_leaf_litter",
    "temple_floor_crack",
    "temple_missing_slabs",
    "temple_moss",
    "temple_bones",
    "phlegethos_ember_crack",
    "fey_path_stones",
    "fen_lily_pads",
})

# Kinds that share another kind's examine line rather than having their
# own: the same object in a different state.
EXAMINE_ALIAS = {
    "city_streetlight_lit": "city_streetlight",
    # Authored as props, but the world turns every one of these into the
    # breakable they are; the line has to be the breakable's.
    "temple_urn": "breakable_urn",
    "grain_sack": "pantry_jar",
    "pantry_shelf": "jar_shelf",
    # The same lantern in two lights.
    "fey_lantern_teal": "fey_lantern",
    "fey_lantern_violet": "fey_lantern",
}


def examine_line_id(kind: str) -> str:
    """The id of a prop's plain description in data/dialogue/examine.json.

    Everything Chuck can walk up to says what it is when he presses E.
    Where it looks like something a scratch might break and it isn't,
    the line says so -- so a player learns what scratching is for
    without breaking every barrel in Waterdeep to find out.
    """
    return f"examine_{EXAMINE_ALIAS.get(kind, kind)}"

# How far above its own bottom edge a prop sorts, in pixels.
#
# A prop normally sorts on the tile it stands on, which is right for
# anything Chuck walks around. It is wrong for anything he walks *onto*:
# the cabin's porch deck is drawn as part of the cabin, so sorting the
# cabin on its own feet buried Chuck under the decking the moment he
# stepped up. Sorting it against the back of the deck instead means the
# building still covers him when he is behind it and never when he is
# standing on it.
PROP_SORT_LIFT = {
    "tahuya_cabin": 78,
    # Its anchor is at the map's south edge, but the ship meets the pier much
    # farther north. Sort at that contact so people on the near pier edge can
    # still pass in front of the hull.
    "waterdeep_docked_ship": 80,
}

# Props big enough to hide somebody completely. Most things in the game
# are a couple of tiles tall, so a character behind one is still mostly
# visible; these are not, and walking behind one would lose Chuck -- or
# an enemy -- entirely for several steps. They thin out while anybody is
# behind them.
#
# Each kind says how many pixels of its bottom edge stay solid, so the
# thing still stands on the ground while the rest of it thins: a tree's
# roots, a mast's foot, the cabin's porch -- which Chuck walks on, and
# which would otherwise fade under his own feet.
SEE_THROUGH_SOLID_BASE = 40
SEE_THROUGH_PROPS: dict[str, int] = {
    "feywild_great_tree": SEE_THROUGH_SOLID_BASE,
    "chult_great_tree": SEE_THROUGH_SOLID_BASE,
    "ship_mast_sail": 18,
    "ship_bowsprit": 0,
    "sailing_cog": 36,
    "waterdeep_docked_ship": 36,
    "cloud_tower_arch": 24,
    "desert_ruin_arch": 10,
    "temple_grand_arch": 10,
    "desert_ribcage": 12,
    "castle_turret": 12,
    "tahuya_cabin": 78,
}
# How much of the prop is left when it is fully thinned out.
SEE_THROUGH_ALPHA = 90
SEE_THROUGH_RATE = 4.0
SEE_THROUGH_STEPS = 6
SEE_THROUGH_BLEND = 14


class Prop:
    """One standing object on a tile."""

    def __init__(self, kind: str, col: int, row: int,
                 assets: "AssetManager") -> None:
        if kind not in _SPRITES:
            raise ValueError(f"Unknown prop kind {kind!r}")
        self.kind = kind
        ts = config.TILE_SIZE
        animated = _ANIMATED_SPRITES.get(kind)
        if animated is not None:
            self._frames = tuple(assets.image(path) for path in animated)
            # The real cabin's colour-changing path lights do not pulse in
            # lockstep.  Their authored map position gives each one a stable
            # phase, so the offsets survive reloads without save-state noise.
            phase = (
                (col * 31 + row * 17) % len(self._frames)
                if kind == "tahuya_mushroom_light" else 0
            )
            self._animation_t = phase * _PROP_FRAME_TIME
            self._image = self._frames[phase]
        else:
            self._frames = ()
            self._animation_t = 0.0
            sprite = _SPRITES[kind]
            if isinstance(sprite, tuple):
                # Stable spatial variation: authored trees keep their
                # silhouette between runs without requiring separate chars.
                sprite = sprite[(col * 31 + row * 17) % len(sprite)]
            self._image = assets.image(sprite)
        w, h = self._image.get_size()
        # Horizontally centered on the tile, bottom edges aligned.
        self._draw_x = col * ts + (ts - w) // 2
        self._draw_y = (row + 1) * ts - h
        self._bottom = (row + 1) * ts - PROP_SORT_LIFT.get(kind, 0)
        self._size = (w, h)
        self.floor_layer = kind in FLOOR_PROPS
        # 0 is solid, 1 is as thin as it gets. Only ever moves for the
        # see-through kinds, which get their own copy of the image so
        # thinning one tree does not thin every tree drawn from it.
        self.see_through = kind in SEE_THROUGH_PROPS
        self._solid_base = min(h, SEE_THROUGH_PROPS.get(kind, 0))
        self.veil = 0.0
        self._thinned: dict[int, object] = {}
        self.choice_id = PROP_CHOICE.get(kind)
        self.dialogue_id = PROP_DIALOGUE.get(kind) or (
            None if self.choice_id or kind in MUTE_PROPS
            else examine_line_id(kind)
        )
        if self.dialogue_id and self.choice_id:
            raise ValueError(f"{kind}: a prop has a line OR a choice, not both")

    def interaction_bounds(self) -> tuple[int, int, int, int]:
        """(x, y, w, h) of the interactable area: the visible sprite,
        slightly padded — same convention as NPCs. Pure math."""
        pad = 3
        w, h = self._size
        return (self._draw_x - pad, self._draw_y - pad,
                w + 2 * pad, h + 2 * pad)

    @property
    def sort_y(self) -> float:
        """Depth key: the tile's bottom edge (same rule as entity feet)."""
        return float(self._bottom)

    def cover_rect(self):
        """The part of a see-through prop that can hide somebody."""
        import pygame

        w, h = self._size
        return pygame.Rect(self._draw_x, self._draw_y, w,
                           h - self._solid_base)

    def update_veil(self, walkers, dt: float) -> None:
        """Thin out while any walker is behind this prop and under it."""
        if not self.see_through:
            return
        cover = self.cover_rect()
        hidden = any(
            getattr(walker, "sort_y", self.sort_y) < self.sort_y
            and cover.colliderect(walker.hitbox)
            for walker in walkers
        )
        target = 1.0 if hidden else 0.0
        step = SEE_THROUGH_RATE * dt
        if self.veil < target:
            self.veil = min(target, self.veil + step)
        elif self.veil > target:
            self.veil = max(target, self.veil - step)

    def _thinned_image(self, level: int):
        """The sprite with everything above its base faded, cached by step.

        Baked rather than faded with surface alpha at draw time: setting
        and clearing surface alpha on a per-pixel-alpha sprite each frame
        is exactly the kind of thing that works on one renderer and draws
        a black box on another.
        """
        image = self._thinned.get(level)
        if image is None:
            import pygame

            image = self._image.copy()
            w, h = self._size
            keep = round(255 - (255 - SEE_THROUGH_ALPHA) * level
                         / SEE_THROUGH_STEPS)
            solid_top = h - self._solid_base
            blend = min(SEE_THROUGH_BLEND, self._solid_base)
            image.fill((255, 255, 255, keep),
                       pygame.Rect(0, 0, w, solid_top - blend),
                       special_flags=pygame.BLEND_RGBA_MULT)
            # A short ramp into the solid base, a row at a time. A hard
            # edge there drew a line across the trunk like a waterline.
            for row in range(blend):
                mix = (row + 1) / (blend + 1)
                alpha = round(keep + (255 - keep) * mix)
                image.fill((255, 255, 255, alpha),
                           pygame.Rect(0, solid_top - blend + row, w, 1),
                           special_flags=pygame.BLEND_RGBA_MULT)
            self._thinned[level] = image
        return image

    def draw(self, surface, camera_offset: tuple[int, int]) -> None:
        ox, oy = camera_offset
        image = self._image
        if self.see_through and self.veil > 0.0:
            image = self._thinned_image(
                max(1, round(self.veil * SEE_THROUGH_STEPS)))
        surface.blit(image, (self._draw_x - ox, self._draw_y - oy))

    def draw_region(self, surface, camera_offset: tuple[int, int],
                    region: tuple[int, int, int, int]) -> None:
        """Redraw one rectangle of the current frame, in place.

        For the parts of a prop that are a light source rather than a
        lit object: the woken table map is a hole in the room, so the
        cabin's darkness passes over it and it goes back on top at its
        own full brightness rather than being dimmed with the furniture.
        """
        ox, oy = camera_offset
        rx, ry, rw, rh = region
        width, height = self._image.get_size()
        left, top = max(0, rx), max(0, ry)
        right, bottom = min(width, rx + rw), min(height, ry + rh)
        if right <= left or bottom <= top:
            return
        surface.blit(
            self._image, (self._draw_x - ox + left, self._draw_y - oy + top),
            (left, top, right - left, bottom - top),
        )

    def update(self, dt: float) -> None:
        """Advance the small set of authored animated scenery props."""
        if not self._frames:
            return
        self._animation_t += dt
        pace = _PROP_FRAME_TIMES.get(self.kind, _PROP_FRAME_TIME)
        frame = int(self._animation_t / pace) % len(self._frames)
        self._image = self._frames[frame]
