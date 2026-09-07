# PHASE 14 --- RETURN TO WATERDEEP

## Status

Active. The first implementation slice establishes the direct playable return
and state-driven midday presentation on the shared docks map.

The previous phase returns Chuck to Waterdeep. Phase 14 begins on the
original Waterdeep exterior map.

This is fundamentally the same place where the game began, but it is now
midday and noticeably busier. Do not redesign the original map. The main
differences between starting and ending Waterdeep should be **lighting
and volume of NPCs**, along with a few appropriate environmental
changes.

## Phase Goal

By the end of Phase 14:

1.  Chuck has returned to the familiar Waterdeep docks.
2.  The map clearly reads as midday.
3.  The docks feel more populated and active.
4.  A ship is now present at the dock.
5.  New ambient NPCs populate the docks and market.
6.  The open eastern edge south of the tavern leads to a new fountain
    plaza.
7.  The fountain plaza contains shops, stands, townsfolk, and a guarded
    northern gate.
8.  The new plaza is also added to the starting Waterdeep state.
9.  Starting and ending Waterdeep remain primarily differentiated by
    lighting and NPC population.

------------------------------------------------------------------------

# 1. Main Waterdeep Map

Reuse the existing Waterdeep exterior.

Preserve the docks, tavern, market, warehouses, northern wall, ruins,
Bobert's barrel area, paths, architecture, collision, and established
scale.

The player should immediately recognize that Chuck is back where the
game began.

## Midday State

The ending version takes place around midday.

Make the overall presentation brighter and sunnier.

### Sea

Change the sea to a noticeably more teal color appropriate to a sunny
blue-sky midday.

Keep the established water rendering style; this is a
palette/time-of-day change, not a redesign.

### Northern Wall Torches

The torches along the northern wall are now extinguished.

Keep the fixtures visible, but remove the flames/light because it is
daytime.

------------------------------------------------------------------------

# 2. Docked Ship

Add a ship at the dock.

It should fit the established perspective, scale, and simple procedural
pixel-art style.

The ship helps communicate that the harbor is more active than it was at
the beginning.

It is environmental scenery during this phase and does not need to be
explorable.

------------------------------------------------------------------------

# 3. Increased NPC Population

The ending Waterdeep should contain noticeably more people than the
opening version.

Continue using the existing dock worker as the reference for human NPC
scale.

Do not overcrowd the map or interfere with Chuck's navigation.

## Fisherman

Add a man fishing from the pier.

Give him a simple fishing idle animation appropriate to the existing NPC
animation style.

No fishing gameplay is required.

## Market

Add townsfolk around the existing market stand.

They can stand, browse, face the merchant, and use simple idle movement.

Do not substantially redesign the existing market.

------------------------------------------------------------------------

# 4. Eastern Waterdeep Expansion

Add another section of Waterdeep accessible through the open eastern
edge of the existing map south of the tavern.

This leads to a new **fountain plaza**.

Importantly, this plaza should also be added back into the **starting
Waterdeep map**.

The physical city layout therefore remains consistent between the
beginning and ending of the game.

------------------------------------------------------------------------

# 5. Fountain Plaza

Build a Waterdeep courtyard/plaza centered around a stone fountain.

The plaza should feel like a small commercial/public area naturally
connected to the docks district.

Include:

-   central stone fountain
-   stone paving
-   shops
-   market stands
-   townsfolk
-   northern city wall
-   guarded northern gate

Keep its architecture, scale, palette, and level of detail consistent
with the existing Waterdeep maps.

Do not make the plaza dramatically more elaborate than the docks.

## Fountain

Place a readable stone fountain near the center.

Use simple animated water appropriate to the native 320×180
presentation.

The fountain is scenery rather than a gameplay system.

------------------------------------------------------------------------

# 6. Northern Gate

The northern edge of the plaza contains a gated city wall.

Use the same architectural style as the open gate/wall to the north of
the main Waterdeep map.

This gate, however, is guarded and inaccessible.

Chuck cannot proceed beyond it.

Do not build the area beyond the gate.

------------------------------------------------------------------------

# 7. Shops and Stands

Populate the plaza with several shops and stands.

At minimum include:

-   blacksmith
-   alchemist

Additional small stands can be added where they improve the plaza
without overcrowding it.

## Blacksmith

Use simple readable elements such as:

-   forge
-   anvil
-   tools
-   weapon/armor shapes

## Alchemist

Use simple readable elements such as:

-   bottles
-   jars
-   potion shapes
-   shop displays

Reuse existing asset language where practical.

------------------------------------------------------------------------

# 8. Chuck Cannot Shop

Chuck cannot purchase anything because he is a rat.

Shopkeeper interactions can briefly acknowledge this rather than opening
a functional purchasing interface.

Do not create:

-   currency systems
-   shop menus
-   purchasable equipment
-   inventory expansion

Keep these interactions short and deadpan.

------------------------------------------------------------------------

# 9. Starting vs. Ending Waterdeep

The fountain plaza exists in both versions.

## Starting Waterdeep

Use:

-   original Waterdeep lighting
-   original sea appearance
-   lower NPC population
-   quieter plaza

## Ending Waterdeep

Use:

-   midday lighting
-   brighter teal sea
-   extinguished northern wall torches
-   docked ship
-   fisherman
-   more market NPCs
-   more plaza NPCs
-   generally greater activity

The architecture and major layout should remain the same.

The important difference is that Waterdeep feels like the same place at
a different time of day, with more people out and about.

------------------------------------------------------------------------

# 10. Architecture and State

Where practical, use one shared Waterdeep environment with
progression/state-driven differences rather than duplicating the maps.

Possible state differences include:

-   lighting palette
-   ocean palette
-   torch state
-   docked ship visibility
-   NPC population
-   NPC placement

The fountain plaza should share the same underlying layout in both
versions.

Reuse existing map, dialogue, interaction, collision, NPC, camera, save,
and checkpoint systems.

------------------------------------------------------------------------

# 11. Art Requirements

New or adjusted art may include:

-   midday Waterdeep palette
-   teal midday ocean
-   extinguished wall torches
-   docked ship
-   fisherman NPC and fishing rod
-   additional townsfolk
-   stone fountain
-   fountain water animation
-   guarded plaza gate
-   blacksmith area
-   forge and anvil
-   alchemist area
-   bottles/potion displays
-   additional market props

Match the established simple procedural pixel-art style and native
320×180 rendering.

------------------------------------------------------------------------

# 12. Out of Scope

Do not add:

-   functional shopping
-   equipment purchasing
-   new inventory systems
-   explorable docked ship
-   area beyond the guarded northern gate
-   major new combat encounters
-   another adventure region

------------------------------------------------------------------------

# 13. Acceptance Criteria

## Main Waterdeep

-   [x] Original Waterdeep remains immediately recognizable.
-   [x] Ending state clearly reads as midday.
-   [x] Sea is noticeably more teal.
-   [x] Northern wall torches are extinguished.
-   [ ] Ship is docked at the pier.
-   [ ] NPC population is noticeably higher.
-   [ ] Fisherman is present.
-   [ ] Market has additional townsfolk.
-   [ ] Chuck remains easy to see and navigate.

## Fountain Plaza

-   [ ] Eastern route south of the tavern leads to the plaza.
-   [ ] Plaza contains a central animated fountain.
-   [ ] Plaza architecture matches Waterdeep.
-   [ ] Northern wall/gate matches the established city-wall style.
-   [ ] Northern gate is guarded and inaccessible.
-   [ ] Blacksmith is visually readable.
-   [ ] Alchemist is visually readable.
-   [ ] Shops and stands do not provide purchasing interfaces.

## Starting Waterdeep Integration

-   [ ] Fountain plaza is also accessible from a new game.
-   [ ] Starting and ending states use the same underlying plaza layout.
-   [ ] Starting version retains earlier lighting.
-   [ ] Starting version has fewer NPCs.
-   [ ] Ending version feels significantly busier without changing the
    city's basic architecture.

## Technical

-   [x] Existing Waterdeep collision remains stable.
-   [ ] Eastern map transition works in both states.
-   [ ] Existing progression remains unaffected by adding the plaza.
-   [ ] Save/checkpoint behavior remains functional.
-   [x] State-driven Waterdeep differences are implemented cleanly where
    practical.

------------------------------------------------------------------------

# 14. Final Playtest

Test both Waterdeep states.

### New Game

Verify the new fountain plaza is accessible, uses the opening Waterdeep
state, has a relatively light NPC population, and the guarded northern
gate prevents further progression.

### Ending Return

Verify the player immediately recognizes Waterdeep while also noticing
the midday teal water, extinguished torches, docked ship, fisherman,
increased market activity, and busier fountain plaza.

Phase 14 is complete when the opening and ending versions of Waterdeep
share the expanded city layout while clearly reading as the same
location at different times and levels of activity.
