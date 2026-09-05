# THE COLLIDED DESERT

## Status

This is the last major adventure leg before the game's final return to
Waterdeep.

The previous phase ends with Chuck arriving in the open desert of Chult.
This phase begins directly from that point and should visually match the
desert established by the preceding cutscene.

The first portion is open-ended desert exploration. From there, the
world becomes increasingly unstable, with larger and larger pieces of
other settings appearing throughout Chult.

The phase culminates in Chuck encountering the trio of adventurers one
final time as they attempt to resolve the collided-worlds problem.

Their success blasts Chuck back to Waterdeep.

The final phase will take place at the Waterdeep docks at midday, with
lighting changes, additional NPCs, and the final Bobert interaction. Do
not implement that ending during this phase.

------------------------------------------------------------------------

# Phase Goal

By the end of this phase the player should:

1.  Explore a five-map desert region without explicit route markers.
2.  Discover an orc camp, oasis, and undead ruins.
3.  Find the eastern route out of the initial desert.
4.  Progress through a substantial sequence of increasingly collided
    maps.
5.  Revisit environments, enemies, hazards, and traversal ideas from
    earlier parts of the game.
6.  Encounter fragments of worlds Chuck has never visited.
7.  Reach the final encounter involving the fighter, wizard, and ranger.
8.  Survive the heroes' climactic attempt to resolve the collided
    worlds.
9.  Be blasted back to Waterdeep.

------------------------------------------------------------------------

# 1. Desert Visual Direction

The opening maps take place in the open desert of Chult.

Match the look, palette, lighting, terrain, and overall color tone of
the desert shown in the preceding cutscene.

Primary materials include:

-   sand
-   brown desert rock
-   canyon cliffs
-   scattered ruins
-   sparse desert vegetation
-   occasional Astral Sea barriers

The initial desert should still feel like a coherent place.

The heavy world mash-up begins primarily after the player finds the
eastern route.

------------------------------------------------------------------------

# 2. Initial Five-Map Desert Region

Create five connected desert exploration maps.

There should be no quest arrow, road painted through the sand, or other
obvious path marking telling the player where to go.

The player should explore and learn the layout naturally.

The starting map is the center of this five-map region.

The surrounding maps are:

-   north --- orc camp
-   west --- oasis
-   south --- undead ruins
-   east --- route forward

The fifth map is the central starting map itself.

------------------------------------------------------------------------

# 3. Central Desert

Chuck begins here.

This map should be mostly open desert with scattered desert ruins.

It acts as the hub for the initial exploration region.

Connections lead:

-   north to the orc camp
-   west to the oasis
-   south to the undead ruins
-   east toward the actual route forward

Do not visually announce that east is the correct direction.

The player should be free to investigate the other areas first.

------------------------------------------------------------------------

# 4. Desert Orc Camp

North of the starting map is an orc camp.

## Orcs

Introduce desert orcs.

Use the existing zombie/skeleton enemy architecture as the starting
point.

Orcs should:

-   be roughly comparable in size to the existing human-sized undead
-   move slightly faster than zombies
-   have somewhat higher durability/HP than zombies

Keep their behavior straightforward.

Do not build a large new combat system specifically for orcs.

## Camp

The camp can include simple desert encampment elements appropriate to
the existing visual style.

Place several scratchable sacks around the camp.

Reuse the same scratchable sack assets and behavior previously used in
the Waterdeep pantry.

The north and west edges of this region are blocked by brown desert rock
cliffs, creating the feeling that the area lies within a desert canyon.

------------------------------------------------------------------------

# 5. Desert Oasis

West of the central desert is an oasis.

The oasis is a quiet exploration/recovery area.

It contains:

-   water
-   desert vegetation
-   scratchable cigarette grass
-   no enemies

Reuse the established cigarette-grass behavior.

The oasis is bounded:

-   to the north by desert cliffs
-   to the west by desert cliffs
-   to the south by an Astral Sea barrier

The oasis should feel like a small reward for exploration rather than
part of the critical route.

------------------------------------------------------------------------

# 6. Undead Ruins

South of the central desert are larger desert ruins.

Skeletons patrol the area.

Reuse the existing skeleton implementation.

Place a treasure chest near the middle of the ruins.

Reuse the same chest visual language established in the sea captain's
quarters.

The west and south sides of this area are blocked by Astral Sea
sections.

The ruins should feel worth exploring even though they do not contain
the route forward.

------------------------------------------------------------------------

# 7. Eastern Route

East of the central map is the path toward the remainder of the phase.

Do not make the first eastern transition dramatically different from the
rest of the desert.

The world mash-up should escalate as Chuck continues eastward rather
than appearing all at once.

Beyond the initial five-map region, create a substantial number of
authored maps.

This should feel like the final long traversal of the game rather than a
short corridor leading immediately to the climax.

------------------------------------------------------------------------

# 8. Increasing World Collision

As Chuck progresses, increasingly large pieces of other worlds should
appear inside the Chult desert.

Early maps can contain relatively small intrusions.

Later maps should become heavily fragmented and geographically
impossible.

Reuse the established Astral Sea visual language between and around
these fragments.

## Returning Worlds

Fragments can come from locations already visited during the game,
including:

-   modern rainy city
-   Feywild
-   Phlegethos / Hell
-   ships at sea
-   jungle Chult
-   earlier Forgotten Realms environments

These should visually recall the environments the player remembers.

Reuse existing procedural assets and systems wherever possible.

## Unvisited Worlds

Also introduce fragments of worlds Chuck never visited during the
playable adventure.

These should imply that the collision is much larger than the specific
route Chuck happened to travel.

Include at least:

### Medieval Courtyard

A fragment of a medieval town or castle courtyard.

Possible elements:

-   stone courtyard
-   armored knights
-   castle walls or towers visible through/behind Astral Sea sections

This should clearly read as somewhere distinct from the game's Waterdeep
docks.

### Snowy Region

A fragment of a frozen landscape.

Include a blue dragon.

The blue dragon uses lightning breath as a major dodge hazard.

It cannot be defeated by Chuck.

Do not build this as a boss fight.

The player's task is to survive the hazard and continue through the
collided terrain.

------------------------------------------------------------------------

# 9. Reusing the Adventure

The collided maps should act as a final mechanical remix of the
adventure.

Reuse enemies, hazards, and traversal systems established earlier where
appropriate.

Possible returning elements include:

-   skeletons
-   zombies
-   rats
-   snakes
-   orcs
-   large pursuit enemies
-   ranged dodge hazards
-   jump gaps
-   Astral Sea fall hazards
-   narrow routes
-   environmental chase sequences
-   lava hazards where Hell fragments appear
-   moving environmental hazards
-   scratchable resources

Do not mechanically recreate every previous encounter.

Use familiar systems in new combinations.

The increasing mash-up should allow mechanics that previously belonged
to separate regions to appear together.

------------------------------------------------------------------------

# 10. Final Trio Encounter

Eventually Chuck reaches the trio of adventurers for the final time:

-   male fighter
-   wizard
-   female ranger

This is the culmination of the recurring encounters established earlier
in the game.

They are actively attempting to resolve the collided-worlds problem.

They may also be fighting enemies or another threat while completing
whatever process is required.

Chuck once again enters the middle of their encounter and must survive
the resulting hazards.

This should be the most chaotic version of the trio encounters.

------------------------------------------------------------------------

# 11. Final Encounter Dialogue

Dialogue occurs automatically during the encounter.

Keep gameplay moving between dialogue moments.

## Opening

**FIGHTER**

> "There! It's opening!"

**WIZARD**

> "I see it. Hold them back!"

**RANGER**

> "We've come too far to lose it now."

The hazard sequence begins.

## Early Encounter

**WIZARD**

> "The boundaries are collapsing faster."

**FIGHTER**

> "Can you still do it?"

**WIZARD**

> "I think so."

**RANGER**

> "You think?"

**WIZARD**

> "Would you prefer I lie?"

Return immediately to gameplay.

## Midpoint

As the world collision becomes increasingly intense:

**RANGER**

> "It's getting worse!"

**WIZARD**

> "No. That's good."

**FIGHTER**

> "That doesn't look good."

**WIZARD**

> "It's all in one place."

The environment should become increasingly unstable around Chuck.

## Approaching the Climax

**WIZARD**

> "I need another minute!"

**FIGHTER**

> "You said that a minute ago!"

**RANGER**

> "Just keep them off him!"

Later:

**WIZARD**

> "Wait."

Allow a brief pause.

**WIZARD**

> "I found it."

**RANGER**

> "You're certain?"

**WIZARD**

> "No."

Brief beat.

**FIGHTER**

> "Good enough."

Begin the final escalation.

------------------------------------------------------------------------

# 12. Final Collision Sequence

As the heroes complete their work, the desert should become overwhelmed
by fragments of different worlds.

Use large, rapidly changing sections representing locations from
throughout the game.

Possible fragments include:

-   Waterdeep stone and dock structures
-   Chult jungle
-   desert ruins
-   Phlegethos basalt and lava
-   Feywild vegetation
-   modern pavement and building walls
-   ship decking
-   snow
-   medieval stonework
-   Astral Sea

The player should still be able to read Chuck and immediate hazards
clearly.

Do not sacrifice gameplay readability simply to put more effects on
screen.

The sequence should build toward the heroes finally succeeding.

------------------------------------------------------------------------

# 13. Resolution Dialogue

As the heroes' work begins taking effect:

**RANGER**

> "It's working!"

**WIZARD**

> "Don't move!"

**FIGHTER**

> "Wasn't planning on it!"

The effect intensifies.

Then:

**WIZARD**

> "Something's caught in it."

**RANGER**

> "What?"

The wizard notices Chuck.

Brief pause.

**WIZARD**

> "...the rat."

**FIGHTER**

> "Can you get him out?"

**WIZARD**

> "No!"

Chuck begins being pulled or blasted away as the collided terrain
separates around him.

**RANGER**

> "Then where's he going?"

**WIZARD**

> "Where he belongs!"

Trigger the final transition.

------------------------------------------------------------------------

# 14. Return to Waterdeep Cutscene

The heroes successfully complete their work.

The resulting blast sends Chuck away from the desert.

Create a climactic transition sequence that carries Chuck back toward
Waterdeep.

This should feel like the culmination of the game's repeated
world-transition sequences.

Fragments of collided worlds can rapidly separate, disappear, or rush
past Chuck during the transition.

The sequence ends with Chuck returning to the Waterdeep docks.

Do not continue into the final Waterdeep gameplay during this phase.

The next phase begins after Chuck has returned.

------------------------------------------------------------------------

# 15. Final Phase Setup

The final phase will revisit Waterdeep.

Planned changes include:

-   midday rather than the original opening atmosphere
-   adjusted lighting
-   additional NPCs
-   final environmental changes
-   dialogue with Bobert
-   story conclusion

Do not implement these changes yet.

This phase only needs to deliver Chuck back to Waterdeep in a clean
state ready for the finale.

------------------------------------------------------------------------

# 16. Checkpoints and Development Access

Use the established ashtray/checkpoint and development checkpoint
systems.

Because this is a long sequence with many maps, provide useful
development entry points for major sections rather than requiring every
map to be tested from the beginning.

At minimum, support convenient testing of:

-   initial desert
-   collided-world traversal
-   final trio encounter

Use the project's existing checkpoint architecture rather than creating
separate debug teleport logic.

------------------------------------------------------------------------

# 17. Architecture

Reuse existing systems wherever possible.

This phase is deliberately built around recombining mechanics and assets
already developed throughout the game.

Prefer reuse for:

-   enemies
-   hazards
-   jumping
-   fall hazards
-   Astral Sea blocks
-   scratchable resources
-   treasure chests
-   dialogue
-   NPC behavior
-   cutscenes
-   map transitions
-   ashtrays/checkpoints
-   Sanity
-   camera
-   environmental rendering

New systems should primarily be limited to what is required for:

-   desert orc variants
-   blue dragon lightning-breath hazard
-   final encounter choreography
-   final world-separation transition

Do not broadly rewrite stable existing systems for this phase.

------------------------------------------------------------------------

# 18. Out of Scope

Do not implement:

-   final Waterdeep gameplay
-   midday Waterdeep NPC population
-   Bobert's ending dialogue
-   credits
-   postgame
-   a full explanation of the collided worlds
-   a lore exposition scene explaining what the trio actually did

Those belong to the final phase or should remain unexplained.

------------------------------------------------------------------------

# 19. Acceptance Criteria

## Initial Desert

-   [ ] Desert visuals match the preceding arrival cutscene.
-   [ ] Five-map opening region is implemented.
-   [ ] Central map connects north, west, south, and east.
-   [ ] Exploration does not use explicit route markers.
-   [ ] Orc camp is north.
-   [ ] Oasis is west.
-   [ ] Undead ruins are south.
-   [ ] Forward route is east.

## Orc Camp

-   [ ] Orcs use existing undead architecture as their base.
-   [ ] Orcs move slightly faster than zombies.
-   [ ] Orcs have higher HP than zombies.
-   [ ] Scratchable Waterdeep-style sacks are present.
-   [ ] Brown desert cliffs block the intended edges.

## Oasis

-   [ ] Oasis contains no enemies.
-   [ ] Scratchable cigarette grass is present.
-   [ ] Cliff and Astral Sea boundaries are correctly placed.

## Undead Ruins

-   [ ] Skeletons patrol the ruins.
-   [ ] Captain's-quarters-style treasure chest is present.
-   [ ] Astral Sea barriers block the intended edges.

## Collided Maps

-   [ ] A substantial sequence of maps follows the eastern route.
-   [ ] World collision increases gradually.
-   [ ] Returning locations are visually recognizable.
-   [ ] Modern city fragments appear.
-   [ ] Feywild fragments appear.
-   [ ] Hell fragments appear.
-   [ ] Ship-at-sea fragments appear.
-   [ ] Chult fragments appear.
-   [ ] At least one unvisited medieval/castle environment appears.
-   [ ] Armored knights appear in the medieval fragment.
-   [ ] A snowy environment appears.
-   [ ] Blue dragon lightning breath functions as an unbeatable dodge
    hazard.
-   [ ] Existing enemies and traversal systems are reused in new
    combinations.

## Final Trio Encounter

-   [ ] Fighter, wizard, and ranger return.
-   [ ] Automatic dialogue occurs throughout the encounter.
-   [ ] Dialogue follows the intended sequence.
-   [ ] The trio is clearly working to resolve the collided worlds.
-   [ ] Chuck's gameplay remains focused on surviving the surrounding
    hazards.
-   [ ] World fragments intensify during the climax.
-   [ ] The wizard eventually notices Chuck.
-   [ ] Final line before Chuck is blasted away is `Where he belongs!`

## Ending

-   [ ] The trio successfully completes their work.
-   [ ] Chuck is blasted away from the desert.
-   [ ] A climactic return transition is implemented.
-   [ ] Chuck returns to Waterdeep.
-   [ ] Final Waterdeep gameplay is left for the next phase.
