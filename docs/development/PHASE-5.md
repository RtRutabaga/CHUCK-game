# PHASE 5 --- DEEPER INTO CHULT

## Status

Phase 5 is complete. The temple exterior now connects to the Phase 6 entrance
hall; all dungeon content remains governed by `PHASE-6.md`.

Phase 4 establishes the first playable Chult map, Chult
ashtray/checkpoint, thorns, narrow Chuck-sized routes, and durable
zombie and skeleton enemies.

Phase 5 continues through the next four Chult maps.

This phase introduces a sailing cog stranded in the jungle, two large
raptors, a thorn maze, a high-pressure undead escape sequence, a
low-pressure jungle respite, and the exterior of a pyramid/temple.

Phase 5 ends at the temple. The temple dungeon crawl begins in the next
phase.

------------------------------------------------------------------------

## Phase Goal

By the end of Phase 5, the player should be able to:

1.  Enter Chult Map 2.
2.  Discover a sailing cog in the middle of the jungle.
3.  See scattered Astral Sea blocks around the ship's base.
4.  Speak with a sailor on the deck.
5.  Navigate a jungle area containing two large raptors.
6.  Pass through a thorn maze using the existing thorn system.
7.  Enter Chult Map 3.
8.  Run through large volumes of zombies and skeletons funneling from
    jungle openings.
9.  Escape through a narrow route only Chuck can fit through.
10. Enter Chult Map 4.
11. Meander through a dense, low-pressure jungle respite with plentiful
    cigarette grass.
12. Enter Chult Map 5.
13. Discover a pyramid/temple.
14. Reach the temple entrance and the transition point for the next
    phase.

Do not build the temple dungeon interior during Phase 5.

------------------------------------------------------------------------

# 1. Chult Map 2

Create the second major Chult jungle map.

Continue the visual language established by the completed Chult cutscene
and existing playable Chult map.

Preserve the established jungle palette, vegetation style, terrain
language, graphical simplicity, and native 320×180 presentation.

The major landmark is a sailing cog in the middle of the jungle.

------------------------------------------------------------------------

# 2. The Sailing Cog

Place a sailing cog in the jungle.

The ship should be unmistakable as a substantial sailing vessel and
dramatically oversized relative to Chuck.

It is not a small wreck, canoe, or decorative fragment.

The player should be able to see enough of the ship and move around
enough of its base to understand its scale.

Use surrounding vegetation, terrain, and path composition to frame the
ship as the map's major discovery.

## Astral Sea Blocks

Place scattered Astral Sea blocks around the base of the cog.

Reuse the established purple and dark-blue Astral Sea visual language
and existing hazard behavior.

Do not create a new Astral Sea system.

The visual implication should be readable through the ship's placement
and the scattered Astral Sea blocks.

------------------------------------------------------------------------

# 3. Sailor NPC

Place a sailor on the cog's deck.

The sailor should use the established human NPC scale.

Position the sailor so the player can clearly see someone standing on
the ship and can interact from an appropriate position using the
existing interaction system.

## Dialogue

Use three sequential dialogue boxes.

First:

> "Oi!"

Next:

> "Look at that rat."

Next:

> "Walkin' on the sea..."

Preserve this wording and sequence.

Use the existing dialogue system.

No larger dialogue tree is required.

------------------------------------------------------------------------

# 4. Chult Map 2 Overall Flow

Treat Chult Map 2 as one large jungle area with several major sections
rather than three small maps stitched together.

A broad intended progression is:

1.  Jungle exploration and approach.
2.  Discovery of the sailing cog and Astral Sea blocks.
3.  Sailor interaction.
4.  Continued movement through the larger jungle.
5.  Raptor territory containing two large raptors.
6.  Approach to the thorn maze.
7.  Thorn maze.
8.  Exit to Chult Map 3.

The exact path does not need to be a straight line.

Small route variations, loops, or side spaces are appropriate.

The cog, raptors, and thorn maze should each have enough environmental
space to read as distinct parts of the map.

Do not place the raptors immediately beside the cog simply because they
are part of the same phase.

Do not place the thorn maze directly against the ship.

Use the map's larger scale to give each major feature room.

------------------------------------------------------------------------

# 5. Raptors

Chult Map 2 contains two large raptors.

These are the primary enemies for the map.

The raptors should be significantly larger than Chuck and immediately
read as dangerous.

Use exactly two authored raptors unless a placement needs to be adjusted
during playtesting.

## Combat and Avoidance

Use the existing combat, damage, and Sanity systems.

The player should be able to evade, move around, or escape the raptors.

Do not require both raptors to be defeated for progression.

The raptors should feel faster and more immediately dangerous than the
zombies and skeletons from the prior Chult map.

Keep behavior simple and readable.

Possible behavior includes:

-   noticing Chuck within a defined range
-   pursuing Chuck
-   faster movement than zombies
-   a simple direct attack or lunge
-   disengaging according to the existing enemy architecture

Do not build a complex dinosaur combat system.

The existing scratch attack should still function if the player chooses
to fight.

------------------------------------------------------------------------

# 6. Thorn Maze

The next section is reached through a thorn maze.

Thorns are already established from the prior Chult map.

Reuse the existing thorn object and behavior.

Do not create a separate maze-specific thorn system.

The maze should be compact and create a simple navigation challenge
using:

-   narrow routes
-   wrong turns
-   small loops
-   visual pressure
-   a readable eventual exit

Do not make the maze enormous.

Do not require a minimap or quest marker.

The two raptors and the thorn layout may create pressure around the
approach, but avoid unavoidable damage states.

The maze exit leads to Chult Map 3.

------------------------------------------------------------------------

# 7. Chult Map 3 --- Undead Run

Chult Map 3 is a high-pressure escape section.

Reuse the zombies and skeletons established in Phase 4.

The map contains openings that large volumes of zombies and skeletons
funnel out of.

The intended experience is a stressful run through the jungle toward the
only escape point.

## Enemy Openings

Create readable openings in the jungle environment that function as
undead entry points.

Possible forms include:

-   gaps in dense vegetation
-   dark openings between jungle walls
-   broken passages
-   ruined openings
-   foliage-obscured paths

Choose the form that best matches the existing Chult art.

Enemies should visibly emerge or funnel from these openings rather than
appearing from nowhere in open terrain.

## Enemy Pressure

Large numbers of zombies and skeletons should move into the playable
area.

The player should quickly understand that stopping to fight every enemy
is impractical.

This builds directly on the established durability of the undead, which
already take many scratches to defeat.

The player should primarily:

-   keep moving
-   read the route
-   move around enemies
-   avoid being surrounded
-   use available space
-   identify the escape point

Do not require the player to clear the map.

Do not lock the exit behind a kill count.

Do not add a wave counter or combat-arena UI.

This is an escape sequence using normal gameplay systems.

------------------------------------------------------------------------

# 8. Undead Funnel Implementation

Use the existing enemy architecture where possible.

The jungle openings should release or funnel undead in a controlled
authored sequence.

Possible approaches include:

-   trigger regions
-   staged enemy activation
-   limited spawn groups
-   authored release points

Choose the simplest stable implementation that creates the intended
pressure.

The encounter does not need unlimited spawning.

Test the intended enemy volume for performance and responsiveness.

Do not broadly rewrite the existing zombie and skeleton systems solely
for this sequence.

------------------------------------------------------------------------

# 9. Chuck-Sized Escape Route

The only escape point from the undead run is a narrow section that only
Chuck can fit through.

Reuse the awning-like narrow passage language already established in the
prior Chult map.

The escape should reinforce Chuck's small size as a gameplay advantage.

## Readability

The narrow route should be visible and understandable while the player
is under pressure.

It should not require pixel hunting.

Use path composition, environmental framing, contrast, surrounding
terrain, and enemy movement to draw attention toward the escape.

Do not add a quest arrow.

## Enemy Interaction

Human-sized zombies and skeletons cannot fit through the narrow passage.

Chuck can.

When Chuck enters the route, the undead should remain outside or
otherwise be prevented from following.

Use existing collision and enemy navigation systems where possible.

Do not simply delete all enemies when Chuck touches the passage.

The player should clearly understand that Chuck escaped because he can
fit somewhere the undead cannot.

The route leads to Chult Map 4.

------------------------------------------------------------------------

# 10. Chult Map 4 --- Jungle Respite

Chult Map 4 deliberately releases the pressure after the undead ambush.

It should feel similar to the exploratory language of Chult Map 1, but
use more dense vegetation blocks to create a longer meandering route.
The path should remain readable without a minimap while offering small
clearings, bends, and optional-looking branches.

Include a good amount of the established scratchable cigarette grass
tufts. Use the shared breakable-grass behavior without adding the early
Waterdeep/sewer proximity tutorial.

A narrow jungle stream should run through the map and divide the route.
Chuck must use the existing jump to cross its one-tile width. Keep the
water visually distinct from ordinary ground, prevent walking through
it, and do not add swimming, drowning, or a stream-specific control.

Place exactly one existing massive, slow dinosaur in the broad clearing
near the northern end. Keep it optional and leave enough space to circle
or escape it. Do not add other enemies or staged releases; the map should
remain a substantial reduction in pressure after the undead ambush.

Give the map one physical Ashtray/checkpoint and a clear route toward
the following temple exterior map.

------------------------------------------------------------------------

# 11. Chult Map 5 --- Temple Exterior

The subsequent Chult map contains a pyramid/temple.

The temple is the primary landmark and destination.

Continue the visual language established by the Chult cutscene and prior
Chult maps.

## Temple Visual Direction

The temple should clearly read as an ancient pyramid or temple at native
scale.

Possible elements include:

-   stepped stone construction
-   broad stairs
-   weathered stone
-   jungle growth
-   vines
-   roots
-   partially obscured masonry
-   a dark entrance
-   simple carved shapes or repeated stone patterns
-   skulls mounted on stakes lining the approach path

Keep the art consistent with the game's simple procedural pixel-art
presentation.

The temple should feel very large relative to Chuck.

## Map Structure

The temple exterior should provide a reduction in pressure after the
undead run.

Give the player space to:

-   recover
-   approach the temple
-   inspect the exterior
-   locate the entrance
-   reach the next phase transition

Do not fill the temple exterior with another large combat encounter.

The temple is the focus.

------------------------------------------------------------------------

# 12. Temple Entrance and Phase End

Create the temple entrance and a clean transition boundary for the next
phase.

The entrance should clearly read as accessible.

The player should be able to approach or enter it using the existing
scene transition architecture.

Phase 5 ends at the temple transition point.

Do not build the dungeon crawl during this phase.

The next phase will focus on dungeon crawling through the temple.

------------------------------------------------------------------------

# 13. Ashtrays and Development Checkpoints

Use the existing ashtray/checkpoint and save architecture.

Add development checkpoints for the new authored map boundaries.

Recommended display names:

-   `Chult 2`
-   `Chult 3`
-   `Chult 4`
-   `Chult 5`

Use the project's actual checkpoint ID naming conventions in code.

Each checkpoint should use the shared checkpoint loader.

## Chult 2

Loads the sailing cog and raptor map in a valid state.

## Chult 3

Loads the undead run in a valid pre-encounter state.

## Chult 4

Loads the low-pressure jungle respite and its one massive dinosaur in a valid
state.

## Chult 5

Loads the temple exterior in a valid state.

Do not create separate debug teleport logic.

Physical ashtray/checkpoint placement should use the established save
and respawn behavior.

Checkpoint placement should support reasonable player recovery without
removing the intended pressure of the undead run.

------------------------------------------------------------------------

# 14. State and Progression

Use only the state required for these maps.

Possible state includes:

-   Chult 2 reached
-   sailor dialogue state if needed
-   Chult 3 reached
-   undead run triggered
-   undead run completed
-   Chult 4 reached
-   Chult 5 reached
-   temple exterior reached

Only create flags that are technically necessary.

Do not build a quest-state system.

Do not add inventory-driven progression, equipment progression, or a
permanent combat upgrade.

------------------------------------------------------------------------

# 15. Music and Audio

Continue the Chult soundtrack identity established in Phase 4.

The Chult music still needs to **SLAP**.

Maintain the strong jungle groove, deep bass, memorable bass movement,
rhythmic identity, and established retro/procedural CHUCK sound.

## Chult Map 2

The cog map may use the established Chult theme or a related variation.

The ship discovery does not require a cinematic music sting.

## Chult Map 3

The undead run should increase musical pressure.

Prefer a more urgent arrangement, rhythmic variation, added percussion,
or another treatment connected to the established Chult musical
identity.

Do not switch to generic orchestral chase music.

The sequence should still sound like CHUCK and still belong musically to
Chult.

## Chult Map 4

The jungle respite should reduce the immediate pressure and return to
the established Chult exploration identity.

## Chult Map 5

The temple exterior may become heavier, slower, or more spacious while
retaining Chult's low-end identity.

Prepare the player for the temple without beginning the dungeon
soundtrack work prematurely.

------------------------------------------------------------------------

# 16. Art Requirements

New Phase 5 art may include:

-   sailing cog exterior
-   ship deck details
-   sailor NPC
-   existing Astral Sea blocks
-   large raptor sprites
-   simple raptor movement/attack animation
-   thorn maze layout using existing thorns
-   undead entry openings
-   jungle terrain for the escape sequence
-   narrow Chuck-sized escape passage using the established route
    language
-   pyramid/temple exterior
-   temple stairs
-   temple entrance
-   simple temple stone patterns
-   vines and jungle growth around the temple

Match the established simple procedural pixel-art presentation.

Maintain native 320×180 rendering.

For all Chult maps, use the completed Chult cutscene and existing Chult
maps as the primary visual reference.

Do not independently redesign Chult's palette or jungle style.

------------------------------------------------------------------------

# 17. Architecture

Use the systems established in earlier phases.

Prefer existing architecture for:

-   maps/scenes
-   entities
-   NPCs
-   interaction
-   dialogue
-   collision
-   jumping
-   combat
-   damage and Sanity
-   enemy behavior
-   hazards
-   thorns
-   ashtrays/checkpoints
-   saves
-   camera
-   audio

Reuse existing systems for Astral Sea blocks, thorns, zombies,
skeletons, and narrow Chuck-sized routes.

Add new systems only where required for:

-   raptor behavior
-   controlled undead release/funneling
-   necessary map-specific encounter triggers

Keep implementation modular.

Do not place all Phase 5 logic directly into `main.py`.

Do not broadly rewrite completed systems unless a verified technical
issue requires it.

------------------------------------------------------------------------

# 18. Out of Scope

Do not implement during Phase 5:

-   temple dungeon interior
-   temple dungeon crawl
-   temple puzzles
-   temple bosses
-   the full Chult region
-   Port Nyanzaru
-   the full Tomb of Annihilation plot
-   the Death Curse quest
-   the Soulmonger
-   Omu
-   the Tomb of the Nine Gods
-   Chult guide selection
-   dinosaur racing
-   full jungle survival simulation
-   hunger or thirst
-   crafting
-   equipment progression
-   a large inventory
-   a combat skill tree
-   procedural jungle generation
-   world-map fast travel

Phase 5 is focused on:

**the jungle cog, sailor interaction, two large raptors, thorn maze,
undead jungle run, Chuck-sized escape route, low-pressure jungle respite,
and temple exterior.**

------------------------------------------------------------------------

# 19. Acceptance Criteria

## Chult Map 2 and Cog

-   [ ] The map visually matches established Chult.
-   [ ] A sailing cog is clearly visible in the jungle.
-   [ ] The cog reads as a large sailing vessel at native scale.
-   [ ] Chuck's size is clear relative to the ship.
-   [ ] Scattered Astral Sea blocks are present around the ship's base.
-   [ ] Existing Astral Sea behavior is reused.
-   [ ] Collision and camera bounds are stable.

## Sailor

-   [ ] A human NPC-sized sailor is visible on the deck.
-   [ ] Chuck can interact with the sailor.
-   [ ] Dialogue appears in three sequential boxes.
-   [ ] First: `Oi!`
-   [ ] Second: `Look at that rat.`
-   [ ] Third: `Walkin' on the sea...`
-   [ ] The existing dialogue system is used.

## Raptors

-   [ ] Exactly two authored large raptors are present.
-   [ ] Raptors are significantly larger than Chuck.
-   [ ] Raptors feel more mobile and immediately dangerous than zombies.
-   [ ] The player can evade or move around them.
-   [ ] Defeating both is not required for progression.
-   [ ] Existing scratch combat works against them.

## Thorn Maze

-   [ ] Existing thorn behavior is reused.
-   [ ] The maze is compact.
-   [ ] Wrong turns or small loops are present.
-   [ ] The exit is discoverable without a minimap or quest marker.
-   [ ] The player can reach Chult Map 3.

## Undead Run

-   [ ] Chult Map 3 contains readable enemy entry openings.
-   [ ] Large volumes of existing zombies and skeletons emerge from the
    openings.
-   [ ] Enemies do not visibly appear from nowhere in open terrain.
-   [ ] The encounter creates sustained pressure.
-   [ ] Fighting every enemy is impractical.
-   [ ] The player can progress by running and evading.
-   [ ] The exit is not locked behind a kill count.
-   [ ] The encounter remains responsive.

## Chuck-Sized Escape

-   [ ] The only escape point is a narrow route Chuck can fit through.
-   [ ] The route uses the established narrow passage visual language.
-   [ ] Human-sized undead cannot follow.
-   [ ] The route is readable under pressure.
-   [ ] The escape works because of Chuck's size rather than combat
    completion.

## Jungle Respite

-   [ ] Chult Map 4 contains exactly one massive slow dinosaur and no
    other enemies or staged releases.
-   [ ] The dinosaur can be circled or escaped without defeating it.
-   [ ] Dense vegetation creates a readable meandering route.
-   [ ] The map provides a clear reduction in pressure after the undead
    run.
-   [ ] A good amount of reusable cigarette grass is scattered through
    the map.
-   [ ] A continuous jungle stream divides the route and requires one
    existing jump to cross.
-   [ ] Chuck cannot walk through the stream or bypass its endpoints.
-   [ ] One physical Ashtray saves and respawns correctly.
-   [ ] The route toward Chult Map 5 is readable.

## Temple Exterior

-   [ ] Chult Map 5 contains a readable pyramid/temple.
-   [ ] The temple is the dominant landmark.
-   [ ] The exterior matches established Chult.
-   [ ] The temple feels large relative to Chuck.
-   [ ] The player has space to approach and inspect it.
-   [ ] Skull stakes clearly line the path before the central staircase.
-   [ ] The entrance is readable.
-   [ ] The phase reaches a clean temple dungeon transition point.
-   [ ] The temple dungeon interior is not implemented.

## Checkpoints and Saves

-   [ ] `Chult 2` loads through the development checkpoint selector.
-   [ ] `Chult 3` loads through the development checkpoint selector.
-   [ ] `Chult 4` loads through the development checkpoint selector.
-   [ ] `Chult 5` loads through the development checkpoint selector.
-   [ ] All use the shared checkpoint loader.
-   [ ] Each map initializes in a valid testable state.
-   [ ] Save and respawn behavior remains stable.

## Audio

-   [ ] Chult music retains the strong jungle groove and deep-bass
    identity.
-   [ ] Chult Map 2 audio works correctly.
-   [ ] The undead run increases musical pressure while remaining
    connected to Chult.
-   [ ] Temple exterior audio supports the transition toward the next
    phase.
-   [ ] Audio remains stable after death, respawn, and map transitions.

## Technical Quality

-   [ ] The game works from a clean start through the temple exterior.
-   [ ] `NEW GAME` and `CONTINUE` still work.
-   [ ] Previous development checkpoints still work.
-   [ ] Chult 1 still works.
-   [ ] Earlier game systems remain functional.
-   [ ] Scene transitions do not duplicate or lose Chuck.
-   [ ] Existing tests pass.
-   [ ] Targeted regression tests are added where practical.

------------------------------------------------------------------------

# 20. Final Playtest

Test through normal progression and development checkpoints.

## Full Chult Route

Play through:

1.  Chult 1
2.  Chult Map 2
3.  sailing cog discovery
4.  sailor interaction
5.  two raptors
6.  thorn maze
7.  Chult Map 3
8.  undead run
9.  Chuck-sized escape
10. Chult Map 4
11. low-pressure jungle respite and massive dinosaur
12. Chult Map 5
13. temple exterior
14. temple entrance transition point

## Development Checkpoints

Load:

-   `Chult 2`
-   `Chult 3`
-   `Chult 4`
-   `Chult 5`

Check:

1.  Does Chult Map 2 immediately feel substantially larger than the
    prior Chult map?
2.  Do the cog, raptor territory, and thorn maze have enough space
    between them to feel like distinct parts of one large map?
3.  Does the cog read as a medieval sailing cog that is large relative
    to Chuck without feeling massive?
4.  Do the Astral Sea blocks connect visually to the existing Astral Sea
    language?
5.  Does the sailor dialogue appear exactly in sequence?
6.  Do the two raptors feel large and dangerous?
7.  Can the player avoid the raptors instead of defeating them?
8.  Does the thorn maze reuse established thorn behavior?
9.  Does Chult Map 3 feel substantially more stressful?
10. Do zombies and skeletons visibly funnel from environmental openings?
11. Does enemy volume make stopping to fight impractical?
12. Can the player identify and reach the narrow escape under pressure?
13. Is it clear that Chuck fits and human-sized undead do not?
14. Does Chult Map 4 feel exploratory, meandering, and clearly free of
    combat pressure?
15. Are the grass tufts plentiful without obscuring the route?
16. Does the pyramid/temple read clearly at native scale on Map 5?
17. Does the phase stop before the dungeon crawl?
18. Do `Chult 2`, `Chult 3`, `Chult 4`, and `Chult 5` work as development
    checkpoints?

Phase 5 is complete when Chuck has discovered the jungle cog, passed the
raptors and thorn maze, escaped a large undead pursuit through a
Chuck-sized route, crossed the low-pressure jungle respite, and reached
the Chult temple exterior ready for the next phase's dungeon crawl.
