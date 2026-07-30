# PHASE 9 --- THE FEYWILD

## Status

Phase 8 is complete. Chuck escaped Phlegethos through a river caught
between collided worlds, washed ashore in the Feywild, and regained
control.

The first playable Feywild map already exists:

- `feywild_riverbank`
- development checkpoint `Feywild 1`
- physical checkpoint `Feywild Ashtray`
- durable progression flag `feywild_reached`

Phase 9 begins on that riverbank and builds the first large playable
Feywild region. Its first implementation slice is complete: `Feywild 2`
(Blooming Path), its Ashtray, and the reusable scratch-reactive flower
system now connect to the riverbank in both directions. `Feywild 3`
(Pollen Orchard) is also complete, providing the safe, enemy-free slowing
pollen lesson and the region's third Ashtray.

This phase contains **thirteen playable Feywild maps total**: the
existing riverbank plus twelve new maps. Chult's exterior region and
Phlegethos each contain five maps, so Phase 9 is deliberately more than
twice their size.

This phase does not contain the later floating wizard's tower, its
cutscene, or the transition beyond the Feywild. Those belong to a later
phase document.

------------------------------------------------------------------------

# Phase Goal

By the end of Phase 9, the player should be able to:

1. Regain control on the existing Feywild riverbank.
2. Activate the first Feywild Ashtray.
3. Explore a large region consisting of thirteen connected maps.
4. Learn that large flowers can change authored vegetation routes.
5. Cross slowing pollen without treating it as ordinary Sanity damage.
6. Use roots, tables, and mushrooms as passages that Chuck can enter but
   larger enemies cannot.
7. Encounter small Feywild enemies that Chuck can defeat with one
   scratch.
8. Encounter gnome-sized redcaps that can be fought but are usually
   better avoided.
9. Avoid stationary projectile plants and weaving airborne hazards.
10. Survive at least one massive Feywild creature best avoided entirely.
11. Find optional side paths, cigarette grass, breakables, and quiet
    environmental scenes.
12. Reach a stable final Feywild boundary without beginning the floating
    wizard's tower phase or playing a new ending cutscene.

Phase 9 should feel like a complete, substantial adventure region rather
than a short connector between major story scenes.

Exploration remains more important than combat.

------------------------------------------------------------------------

# 1. Regional Identity

The playable Feywild must continue directly from the completed river
cutscene and existing `feywild_riverbank` map.

Use the established:

- deep blue-green ground
- teal water
- emerald vegetation
- violet, cyan, pink, and gold magical accents
- luminous spiral plants
- oversized mushrooms
- enormous roots
- broad leaves
- glowing flowers
- dense, hand-authored paths

The Feywild should be beautiful, inviting, slightly psychedelic, and
quietly untrustworthy. It is not a horror realm and should not become a
generic pastel fairyland.

The region's danger comes from:

- vegetation changing familiar routes
- movement being altered by pollen
- creatures occupying spaces built at very different scales
- attractive hazards
- paths that connect in geographically incorrect ways

Do not explain these effects through lore panels or a tutorial NPC.
Teach them through readable animation, repeated visual language, and
safe early examples.

Maintain:

- native 320x180 rendering
- procedural pixel-art construction
- readable silhouettes
- limited animation frames
- cardinal movement
- existing camera behavior
- existing jump and scratch controls

------------------------------------------------------------------------

# 2. Region Structure and Map Count

Phase 9 contains thirteen playable maps:

1. `Feywild 1` --- Riverbank *(existing)*
2. `Feywild 2` --- Blooming Path
3. `Feywild 3` --- Pollen Orchard
4. `Feywild 4` --- Rootways
5. `Feywild 5` --- Giant Tea Table
6. `Feywild 6` --- Needle Garden
7. `Feywild 7` --- Moonmoth Fen
8. `Feywild 8` --- Redcap Warrens
9. `Feywild 9` --- Shifting Hedge
10. `Feywild 10` --- Displacer Meadow
11. `Feywild 11` --- Mushroom Underways
12. `Feywild 12` --- Luminous Rapids
13. `Feywild 13` --- Twilight Crossroads

These names are recommended display names. Use repository naming
conventions for final map IDs and checkpoint IDs.

The broad route is ordered, but individual maps should contain optional
loops, side pockets, alternate passages, and opportunities to wander.
Do not turn the region into an open world or require a minimap.

Vary the direction of travel:

- north
- east
- south
- west
- winding or looping internal routes

The player should not feel that every map is another straight northward
corridor.

Connections may be geographically wrong, but each region remains
internally believable. A normal path may leave one map heading east and
enter the next from the south. Do not present these connections as
glowing portals or explain them.

Every newly authored gameplay map receives:

- exactly one physical Ashtray/checkpoint
- one development checkpoint through the shared checkpoint loader
- a valid arrival from the prior map
- a valid return arrival where backtracking is allowed
- stable camera bounds
- a tested Sanity-zero respawn state

The existing riverbank already satisfies the Map 1 checkpoint
requirement.

------------------------------------------------------------------------

# 3. Pressure and Pacing

Thirteen maps must not mean thirteen combat gauntlets.

Use this pressure cadence:

1. quiet arrival
2. safe mechanic introduction
3. low-pressure terrain hazard
4. first pursuit and scale escape
5. major exploration respite
6. projectile timing
7. jump and moving-hazard traversal
8. redcap pressure
9. complex route-changing puzzle
10. massive-creature pursuit
11. quiet scale-focused underways
12. traversal synthesis
13. broad exploratory culmination

At least four maps should be predominantly exploratory and contain no
ordinary pursuing enemies:

- Riverbank
- Blooming Path
- Giant Tea Table
- Mushroom Underways

Twilight Crossroads may contain hazards but should not become a boss
arena.

No map should require Chuck to defeat every enemy before its exit opens.

------------------------------------------------------------------------

# 4. Core Mechanic --- Reactive Flower Switches

Add a reusable reactive-flower system.

A reactive flower is an authored map switch. Activating it changes a
specific authored group of vegetation tiles.

Activation should use Chuck's existing scratch action. Do not add a new
button.

Possible results include:

- dense vines retract into walkable ground
- a previously open passage fills with growth
- flower pads bloom into safe stepping tiles
- roots shift to expose a Chuck-sized opening
- a side path opens while the direct path closes

## Rules

1. Flower changes are authored, deterministic, and inspectable in the
   map data or a small companion definition.
2. Do not procedurally regenerate the whole map.
3. A flower must visibly pulse, shake, flash, or bloom before terrain
   changes.
4. Changes must never occur beneath Chuck.
5. A change must never permanently trap Chuck.
6. Every required flower puzzle must have a safe reset state or a
   reachable reciprocal flower.
7. The initial state must restore correctly on Sanity-zero respawn.
8. Loading a map checkpoint must always produce a valid authored state.
9. Flower state should remain map-local unless a later design explicitly
   requires durable progression.
10. Do not save every individual flower state in the persistent save
    file.

The first flower in Blooming Path should be safe to activate and should
make its changed route visible on the same native screen whenever
possible.

Later maps may chain several flowers, but the player should never need
to memorize a large invisible switch network.

------------------------------------------------------------------------

# 5. Core Mechanic --- Slowing Pollen

Add **slowing pollen** as Phase 9's one new terrain hazard.

Pollen is walkable ground covered by luminous spores or low flowers.
While Chuck is grounded on it, his walking speed is reduced.

## Rules

- Pollen does not directly damage Sanity.
- Pollen is not a fall hazard.
- Jumping clears or bypasses a one-tile pollen strip using the existing
  committed jump.
- The slowdown applies only while Chuck is touching pollen; do not add a
  long status timer.
- The visual effect must be readable before Chuck enters it.
- Use a consistent slowdown value throughout the region.
- Do not reverse controls, randomize input, or add multiple pollen
  status effects in this phase.
- Do not combine the first pollen introduction with enemies.
- Later maps may combine pollen with pursuit or projectile timing, but
  every required route must remain fair.

This should extend the existing terrain-effect architecture rather than
becoming a general buff/debuff system.

Pollen is the only new terrain mechanic required for Phase 9. Ordinary
water, fall hazards, jumps, and solid vegetation may still return where
appropriate.

------------------------------------------------------------------------

# 6. Core Scale Mechanic --- Chuck-Sized Passages

Create reusable narrow passage terrain for:

- exposed roots
- spaces beneath giant tables
- gaps beneath mushroom shelves
- openings between large plates, cups, or roots

Chuck should enter these routes simply by walking into them. Do not add
a crouch button.

These routes should use the existing overhead/collision language:

- scenery draws above Chuck where appropriate
- Chuck remains visible enough to track
- large actors treat the route as solid
- small one-hit enemies may enter when explicitly intended

Redcaps, projectile plants, lantern moths, and the massive creature
should not pass through Chuck-sized route terrain.

At least three maps must use these passages as meaningful gameplay:

- Rootways
- Giant Tea Table
- Displacer Meadow

Mushroom Underways should build an entire low-pressure exploration map
around this scale language.

The player should understand that Chuck survives because he is small,
not because an invisible enemy leash abruptly turns enemies off.

------------------------------------------------------------------------

# 7. Feywild Enemy Roster

All Phase 9 enemies should belong visually and thematically to the
Feywild. Do not reuse Chult, temple, pirate, or infernal sprites with
only a palette swap.

Reuse established behavior architectures where practical.

## 7.1 Thorn Mites --- Small, One-Scratch Enemies

Thorn mites are tiny fey creatures, visibly smaller than Chuck.

They fill the rats/snakes combat role:

- low Sanity damage
- short notice range
- brief chase or patrol
- defeated by one committed scratch
- reset when the map resets

They may move through selected Chuck-sized root passages.

Keep groups small. They should add movement and light combat, not turn
the Feywild into a swarm game.

## 7.2 Redcaps --- Gnome-Sized Durable Pursuers

Redcaps are gnome-sized fey: much larger than one-foot-tall Chuck but
smaller than human NPCs.

Their art should clearly show:

- heavy boots
- red caps
- broad tools or sickles sized dangerously relative to Chuck
- compact, dense silhouettes

They fill the skeleton/zombie role:

- direct, collision-aware pursuit
- several scratches required to defeat
- meaningful contact damage
- possible to fight
- usually more practical to evade

Redcaps cannot enter Chuck-sized passages.

Do not require clearing every redcap to progress. Route geometry should
let a patient player watch, slip past, or escape through scale-specific
openings.

## 7.3 Spitting Orchids --- Stationary Projectile Enemies

Spitting orchids are rooted plants that fire hard seeds or thorns along
authored cardinal lanes.

They fill the spined-devil role:

- stationary
- visibly face their firing direction
- deterministic cadence
- staggered timing when several share an area
- projectiles stop against solid terrain
- projectile contact damages Sanity

Treat them primarily as traversal hazards. Do not require Chuck to
destroy them.

Their wind-up animation must be readable at native scale. A swelling
bulb, opening petals, or bright color flash should precede each shot.

## 7.4 Lantern Moths --- Weaving Airborne Hazards

Lantern moths are large magical insects with wingspans larger than Chuck.
They weave around fixed horizontal or vertical haunts.

They fill the flameskull role:

- rapid, predictable sine-like movement
- no pathfinding pursuit
- contact damages Sanity
- flight ignores ground terrain
- cannot be cleared with the scratch attack

Use luminous wings and a short pixel trail to make their paths readable.
They should resemble living Feywild wildlife, not recolored infernal
skulls.

## 7.5 Displacer Beast --- Massive Avoidance Enemy

The phase's massive enemy is a displacer beast or a similarly
Feywild-specific great cat if later art direction changes its exact
name.

It should be enormous relative to Chuck:

- substantially wider and taller than redcaps
- broad multi-tile visual silhouette
- long body and tail or tentacle shapes
- clear planted shadow

It fills the massive-dinosaur/horned-devil gameplay role:

- large notice range
- collision-aware direct pursuit
- extremely durable
- technically engageable with scratches
- clearly intended to be avoided

It cannot enter root, table, or mushroom passages.

The encounter must provide multiple readable escape opportunities.
Do not place it directly on the map arrival, Ashtray, or mandatory exit.
Do not require its defeat.

Phase 9 does not need a boss.

------------------------------------------------------------------------

# 8. Map-by-Map Plan

## Map 1 --- Feywild Riverbank

Status: implemented.

Purpose:

- quiet recovery after Phlegethos
- establish the region's palette
- introduce the broad enchanted river
- provide the first Feywild checkpoint
- offer an enemy-free route toward Map 2

Preserve this map's current low-pressure identity. Do not retrofit its
first screen with combat.

Small visual refinements may be made only when required to connect Map 2
or unify later Feywild art.

## Map 2 --- Blooming Path

Purpose:

- safely introduce reactive flower switches
- demonstrate vegetation closing one route while opening another
- establish that scratching scenery can alter traversal

Structure:

- broad initial clearing
- one clearly framed flower and nearby vine wall
- two short route branches
- optional cigarette-grass pocket
- one physical Ashtray
- no enemies

The first switch result should be visible without scrolling far away.
The player must be able to return the map to a navigable state.

## Map 3 --- Pollen Orchard

Purpose:

- introduce slowing pollen without enemy pressure
- teach that jumping can clear narrow pollen strips
- combine normal ground, pollen, and solid flowering hedges

Structure:

- winding orchard lanes
- several shallow pollen beds
- one optional flower-switched shortcut
- thorn mites only after the main pollen lesson
- one physical Ashtray

The opening pollen bed must not damage Sanity or conceal another hazard.

## Map 4 --- Rootways

Purpose:

- introduce Chuck-sized passages as reliable enemy escapes
- begin meaningful pursuit pressure

Structure:

- giant roots divide a broad forest floor
- one main route exposed to two or three redcaps
- narrow root gaps connect protected pockets
- one optional cache reached entirely through root passages
- thorn mites may occupy one narrow tunnel
- one physical Ashtray

Redcaps should visibly fail to enter the passages rather than disappear.

## Map 5 --- Giant Tea Table

Purpose:

- major exploration respite
- strongly reinforce Chuck's scale
- provide environmental storytelling and restrained humor

Structure:

- a colossal tea table or abandoned Fey gathering
- chair legs as columns
- plates, cups, crumbs, napkins, and spilled tea as level geometry
- routes under the table and beneath place settings
- mushroom or root passages
- breakable containers or sugar-flower equivalents
- one physical Ashtray
- no pursuing enemies

Possible short interaction text:

> Still warm.

> Set for one.

Do not add a long conversation or lore dump. Chuck does not speak or
think in text.

## Map 6 --- Needle Garden

Purpose:

- introduce spitting orchids
- create readable projectile-lane timing

Structure:

- dense flowerbeds define several cardinal lanes
- the first orchid fires across a broad safe approach
- later orchids use staggered, never simultaneous cadences
- side paths allow careful players to bypass the densest lane
- pollen appears only after the player understands the projectile timing
- one physical Ashtray

Do not place projectiles across the Ashtray interaction space.

## Map 7 --- Moonmoth Fen

Purpose:

- introduce lantern moths
- combine moving hazards with existing one-tile jumps

Structure:

- dark luminous wetland
- shallow solid water or dangerous deep channels
- small safe islands
- one-tile committed jumps
- fixed-axis lantern moth haunts
- one optional side island with cigarette grass
- one physical Ashtray

Do not create moving platforms. Keep landing tiles static and jumps
consistent with the existing jump system.

## Map 8 --- Redcap Warrens

Purpose:

- provide the region's strongest ordinary-enemy area
- combine redcap pursuit with several ways to avoid combat

Structure:

- broad redcap camp or burrow exterior
- oversized tools, boots, cooking vessels, and crude shelters
- several redcaps with separated notice zones
- root and mushroom passages connecting safe pockets
- small thorn-mite nests
- alternate east-west route around the central camp
- one physical Ashtray

The player should be able to cross without defeating a redcap.

## Map 9 --- Shifting Hedge

Purpose:

- fully develop the reactive-flower mechanic
- create the phase's main authored navigation puzzle

Structure:

- a large hedge with three or four flower groups
- each flower changes a nearby, visible vegetation group
- routes form a small loop rather than a single corridor
- reset flowers prevent softlocks
- one optional reward pocket
- a few thorn mites, but no redcaps or massive enemies
- one physical Ashtray

Do not randomize the hedge. The player should learn and reason about its
deterministic states.

## Map 10 --- Displacer Meadow

Purpose:

- deliver the phase's massive-creature avoidance encounter
- make Chuck-sized routes essential under pressure

Structure:

- broad open meadow with a meandering main route
- one massive displacer beast away from the arrival
- several giant root arches and hollow mushroom shelves
- at least three protected passages the beast cannot enter
- pollen beds that complicate the exposed route
- no redcaps
- one physical Ashtray

The Ashtray must sit in a genuinely safe pocket. Respawning must never
place Chuck inside the creature's active notice range.

## Map 11 --- Mushroom Underways

Purpose:

- low-pressure recovery after the massive encounter
- explore vertical scale through enormous mushroom shelves

Structure:

- layered mushroom canopy
- long routes beneath caps and between stems
- alternating overhead and open clearings
- luminous pools and optional side chambers
- scratchable grass or fungal tufts with cigarette rewards
- no pursuing enemies
- one physical Ashtray

This map should feel cozy, melancholy, and strange rather than empty.

## Map 12 --- Luminous Rapids

Purpose:

- synthesize the region's traversal systems
- provide the phase's largest non-combat traversal challenge

Structure:

- bright river or rapids divide the map
- static safe stones and giant flower pads
- one-tile jumps
- reactive flowers change which authored pads are safe
- pollen affects the approaches, not the landing tiles
- lantern moths cross selected lanes
- spitting orchids appear only in optional or late sections
- one physical Ashtray

Never require a blind jump onto an offscreen tile. Keep required landing
silhouettes readable.

## Map 13 --- Twilight Crossroads

Purpose:

- act as the large playable region's culmination
- combine exploration, wrong geography, and restrained mechanical
  synthesis
- end at a stable boundary for a later floating-wizard-tower phase

Structure:

- broad twilight clearing with several normal-looking paths
- connections enter from geographically unexpected directions
- one flower-switch route
- one pollen route
- one Chuck-sized optional shortcut
- small thorn mites
- a restrained redcap or lantern-moth presence
- no massive enemy
- no boss
- one physical Ashtray

The final boundary should be stable and visually readable but inert
until the later phase exists.

Do not begin a cutscene.
Do not transition Chuck to another region.
Do not build the floating wizard's tower in this phase.

------------------------------------------------------------------------

# 9. Rewards, Breakables, and Secrets

Continue using cigarettes and cartons as the practical exploration
reward.

Across the region:

- scatter scratchable grass or Feywild fungal tufts
- reuse breakable-container behavior where visually appropriate
- place rewards on optional paths rather than the center of every route
- include some empty or purely scenic side pockets

Do not place a cigarette reward behind every flower switch. Discovery
should not become mechanically predictable.

At least one secret should rely on:

- noticing a Chuck-sized opening
- activating a non-required flower
- crossing a short pollen bed
- watching a moving hazard's timing

Do not add:

- inventory
- keys
- equipment
- currency
- crafting materials
- permanent combat upgrades

------------------------------------------------------------------------

# 10. Environmental Storytelling

The Feywild should contain evidence of habitation without becoming
dialogue-heavy.

Possible scenes include:

- an abandoned tea setting
- an enormous chair slowly being reclaimed by roots
- tiny redcap tools
- a path marked by old cigarette burns
- a cup holding an entire pond
- a mushroom home with nobody inside
- a table place set for a guest who never arrived
- flowers growing around an object from another world

Use no more than a few brief interactions.

The region may quietly suggest that Chuck has some deeper relationship
to the Feywild because he is a fey spirit, but do not explain his origin
or give him internal monologue.

Do not introduce the floating wizard's tower story during this phase.

------------------------------------------------------------------------

# 11. Feywild Music and Ambience

Create an original Feywild exploration theme shared across the region
unless later implementation benefits from one restrained variation.

The music should feel:

- lush
- playful
- hypnotic
- slightly unstable
- exploratory
- memorable
- warm enough to invite wandering

Favor:

- syncopated mallet or bell-like figures
- elastic bass
- hand percussion
- woody or breathy synthesized voices
- phrases that resolve in unexpected places
- occasional reversed-feeling envelopes or pitch bends

Avoid:

- generic quiet fairy ambience
- modern cinematic orchestration
- constant music-box sweetness
- horror drones
- direct imitation of an existing game soundtrack

The music should have enough rhythmic identity to support a large
region without becoming exhausting.

Simple ambience may include:

- insects
- distant birds
- water
- leaf movement
- soft magical pulses

Ambience remains secondary to the regional theme.

Music must remain uninterrupted when moving between Feywild maps that
share the same theme. Death and checkpoint respawn must not layer or
duplicate playback.

------------------------------------------------------------------------

# 12. Save, Checkpoint, and State Requirements

Use the shared checkpoint-loading architecture.

Define development checkpoints for all thirteen maps:

- `Feywild 1`
- `Feywild 2`
- `Feywild 3`
- `Feywild 4`
- `Feywild 5`
- `Feywild 6`
- `Feywild 7`
- `Feywild 8`
- `Feywild 9`
- `Feywild 10`
- `Feywild 11`
- `Feywild 12`
- `Feywild 13`

Each map receives exactly one physical Ashtray. The first map's existing
Ashtray counts.

Every checkpoint must:

1. load its map through the shared loader
2. use a safe authored spawn
3. initialize required regional progression
4. set a valid active respawn point when activated
5. save correctly
6. restore the proper map on `CONTINUE`
7. reset enemies and map-local encounter state after Sanity-zero death

The development selector may expose all Phase 9 checkpoints regardless
of normal progress.

Normal `CONTINUE` must load only the player's saved checkpoint.

Do not create a separate Feywild teleport or debug loader.

Avoid adding durable flags for:

- individual defeated enemies
- broken grass
- individual flower positions
- temporary pollen contact

Add durable progression only if a later map genuinely cannot initialize
correctly from its checkpoint without it.

------------------------------------------------------------------------

# 13. Architecture

Reuse the existing architecture for:

- text-authored maps
- tilesets and animated tiles
- marker-authored spawns
- map transitions and named arrivals
- y-sorted props
- overhead scenery
- collision
- jumping
- scratch hit detection
- Sanity damage
- death and respawn
- enemy reset
- breakables and cigarette drops
- checkpoints and saves
- regional music continuity

Prefer the following extensions:

- flower-switch controller modeled on existing authored tile mutation
- one pollen movement modifier integrated with terrain contact
- reusable large-actor exclusion terrain for Chuck-sized passages
- thorn mites based on rat/snake lifecycle
- redcaps based on durable direct-pursuit enemies
- spitting orchids based on stationary projectile launchers
- lantern moths based on fixed-axis weaving hazards
- displacer beast based on the massive pursuit enemy

Keep repeated content data-driven.

Do not place all Feywild logic directly into `world_scene.py`.

Do not broadly refactor completed Chult, temple, ship, or Phlegethos
systems merely to add Feywild variants.

Implement Phase 9 through bounded feature slices. A reasonable sequence
is:

1. Map 2 plus reactive flowers
2. Map 3 plus pollen
3. Map 4 plus scale-gated passages and redcaps
4. Map 5 exploration respite
5. Map 6 plus spitting orchids
6. Map 7 plus lantern moths
7. Map 8 redcap encounter
8. Map 9 advanced flower puzzle
9. Map 10 massive creature encounter
10. Map 11 exploration respite
11. Map 12 traversal synthesis
12. Map 13 regional culmination
13. regional audio and complete balancing pass, if not completed earlier

Keep the game runnable and testable after every slice.

------------------------------------------------------------------------

# 14. Art Requirements

Phase 9 may add:

- reactive flower closed/open frames
- retracting vine or flowering hedge tiles
- slowing-pollen terrain and airborne motes
- giant root overhead pieces
- table legs, cups, plates, crumbs, napkins, and spilled tea
- large mushroom shelves and passages
- thorn mites
- redcaps
- spitting orchids and seed projectiles
- lantern moths and light trails
- displacer beast
- flower stepping pads
- Feywild-specific breakable tufts
- path and boundary variants

Match the existing procedural pixel-art presentation.

At native scale:

- thorn mites are smaller than Chuck
- Chuck remains approximately one foot tall
- redcaps are gnome-sized and clearly larger than Chuck
- tableware is architectural
- lantern moth wingspans exceed Chuck's body length
- the displacer beast is massive but readable in top-down play

Prioritize silhouette, color grouping, and route readability over
texture density.

Do not use generated high-resolution art directly in the game without
translating it into the established native pixel language.

------------------------------------------------------------------------

# 15. Out of Scope

Do not implement during Phase 9:

- the floating wizard's tower
- the wizard's tower cutscene
- transition to the next major region
- a Phase 10 story climax
- a Feywild ruler or boss fight
- a large dialogue quest
- explanation of Chuck's full origin
- explanation of the collided worlds
- procedural map generation
- random flower-puzzle solutions
- day/night simulation
- seasonal world simulation
- control reversal
- a general status-effect system
- inventory
- equipment
- crafting
- currency
- quest log
- minimap requirement
- fast travel
- permanent power upgrades
- a large roster beyond the five defined Feywild enemy roles

Phase 9 is focused on:

**a large, fun, thirteen-map Feywild region built around reactive
flowers, slowing pollen, Chuck-sized passages, Feywild-specific enemies,
exploration, traversal, and one stable endpoint for a later phase.**

------------------------------------------------------------------------

# 16. Acceptance Criteria

## Region

- [ ] Thirteen playable Feywild maps exist, including the current
      riverbank.
- [ ] The twelve new maps connect through normal map transitions.
- [ ] Travel directions vary rather than forming one straight line.
- [ ] Each map has a readable main route.
- [ ] Optional paths and discoveries recur throughout the region.
- [ ] At least four maps are predominantly exploratory and low pressure.
- [ ] No minimap or quest marker is required.
- [ ] The final map ends at a stable boundary without a cutscene or
      transition to the wizard's tower.

## Checkpoints and Saves

- [ ] Every map has exactly one physical Ashtray/checkpoint.
- [ ] `Feywild 1` through `Feywild 13` load through the shared
      development selector.
- [ ] Every development checkpoint initializes a valid playable state.
- [ ] Every Ashtray saves the correct map and checkpoint.
- [ ] `CONTINUE` restores the correct Feywild checkpoint.
- [ ] Sanity-zero death returns Chuck to the current map's Ashtray.
- [ ] Enemy and map-local temporary state reset correctly.

## Reactive Flowers

- [x] Flowers activate through Chuck's existing scratch.
- [x] Flowers mutate only authored vegetation or stepping-pad groups.
- [x] Every change has a readable animation or warning.
- [x] Terrain never changes beneath Chuck.
- [x] Required puzzles cannot permanently trap the player.
- [x] Flower state resets to a valid state after death and checkpoint
      loading.
- [ ] Shifting Hedge uses several deterministic flower groups without
      becoming random.

## Pollen

- [x] Pollen is visually distinct at native scale.
- [x] Grounded contact consistently slows Chuck.
- [x] Pollen does not directly damage Sanity.
- [x] Leaving pollen immediately restores normal movement.
- [x] A one-tile pollen strip can be cleared with the existing jump.
- [x] The first pollen lesson occurs without enemies.
- [ ] Later pollen combinations remain fair.

## Chuck-Sized Passages

- [ ] Root, table, and mushroom passages reuse one consistent collision
      rule.
- [ ] Chuck enters them without a crouch button.
- [ ] Redcaps and the massive enemy cannot enter.
- [ ] Large enemies remain visibly outside rather than disappearing.
- [ ] At least one mandatory or strongly encouraged escape succeeds
      specifically because Chuck is small.
- [ ] Mushroom Underways makes scale meaningful without combat.

## Enemies

- [ ] Thorn mites are smaller than Chuck and fall to one scratch.
- [ ] Redcaps are gnome-sized, durable, and avoidable.
- [ ] Redcaps can be defeated but never form a mandatory clear gate.
- [ ] Spitting orchids fire readable cardinal projectiles on a
      deterministic cadence.
- [ ] Lantern moths weave predictably and cannot be scratched away.
- [ ] The displacer beast is massive, avoidable, and blocked by
      Chuck-sized passages.
- [ ] Enemy collision, Sanity damage, scratch detection, death, and
      reset behavior work correctly.
- [ ] Enemies do not cross inappropriate fall hazards or solid scenery.

## Exploration and Art

- [ ] The region continues the river cutscene and Riverbank palette.
- [ ] The Giant Tea Table makes human/Fey scale architectural relative
      to Chuck.
- [ ] Environmental storytelling remains brief and visual.
- [ ] Breakables and cigarette rewards recur without becoming uniform.
- [ ] Required routes remain readable at 320x180.
- [ ] New sprites match the established procedural pixel-art style.

## Audio

- [ ] The Feywild has a memorable original regional theme.
- [ ] The track supports extended exploration without becoming generic
      ambience.
- [ ] Music continues uninterrupted between maps sharing the theme.
- [ ] Death and checkpoint respawn do not duplicate audio.
- [ ] Ambience remains secondary to music.

## Technical Quality

- [ ] `NEW GAME` still works.
- [ ] `CONTINUE` still works.
- [ ] Waterdeep, sewer, Chult, temple, ship, and Phlegethos remain
      functional.
- [ ] Map transitions do not duplicate or lose Chuck.
- [ ] Camera bounds remain stable on all thirteen maps.
- [ ] No map can permanently softlock Chuck.
- [ ] Existing tests pass.
- [ ] Targeted tests cover flower states, pollen, large-actor passage
      blocking, checkpoints, transitions, and enemy reset.

------------------------------------------------------------------------

# 17. Final Playtest

## Full Regional Route

Start at `Feywild 1` and play through:

1. Riverbank
2. Blooming Path
3. Pollen Orchard
4. Rootways
5. Giant Tea Table
6. Needle Garden
7. Moonmoth Fen
8. Redcap Warrens
9. Shifting Hedge
10. Displacer Meadow
11. Mushroom Underways
12. Luminous Rapids
13. Twilight Crossroads

Verify:

1. Does the region feel substantially larger than Chult or Phlegethos?
2. Does each map have a distinct traversal or exploration identity?
3. Does the pressure rise and fall instead of escalating constantly?
4. Are flower changes understandable without tutorial dialogue?
5. Can every flower puzzle be reset or safely completed?
6. Does pollen slow Chuck without feeling like invisible damage?
7. Do Chuck-sized passages consistently stop large enemies?
8. Are thorn mites readable as smaller than Chuck?
9. Are redcaps clearly gnome-sized and dangerous but avoidable?
10. Are projectile lanes and lantern-moth paths predictable?
11. Can the displacer beast be escaped without fighting it?
12. Does each Ashtray save and respawn correctly?
13. Does music continue cleanly throughout the region?
14. Does Twilight Crossroads end without prematurely entering the
    wizard's tower phase?

## Development Checkpoints

Load `Feywild 1` through `Feywild 13` individually.

For each checkpoint, verify:

1. correct map
2. safe spawn
3. correct facing
4. correct initial flower configuration
5. no immediate enemy damage
6. reachable Ashtray
7. valid backward and forward routes
8. correct regional music
9. correct Sanity-zero respawn

Phase 9 is complete when the player can explore the entire thirteen-map
Feywild region, understand and combine its three core environmental
systems, survive its complete enemy scale, and reach the stable final
boundary reserved for the later floating-wizard-tower phase.

------------------------------------------------------------------------

# Implementation Log

(Slices are appended here as they land, newest last.)

- **Blooming Path / reactive-flower introduction:** Added the 60x42,
  enemy-free `feywild_blooming_path` with one physical Ashtray, shared
  `Feywild 2` development checkpoint, one optional cigarette-grass pocket,
  and two authored routes through a dense enchanted clearing. Scratching the
  central flower visibly pulses before atomically opening the direct route
  and closing the upper route; scratching it again reverses the state. The
  reusable controller delays changes beneath Chuck, guarantees a valid
  authored initial state on map load/death, and keeps transient flower state
  out of the save file. Tested both route states, bidirectional transitions,
  scratch integration, Ashtray saving, Continue restoration, and reset.
- **Pollen Orchard / slowing-pollen introduction:** Added the 62x46,
  enemy-free `feywild_pollen_orchard`, its physical Ashtray and shared
  `Feywild 3` development entry. Five shallow animated pollen beds interrupt
  winding orchard lanes; grounded contact immediately reduces walking speed,
  leaving restores it, airborne movement is unaffected, and the first
  one-tile strip can be cleared by the existing jump. A reversible flower
  exchanges the long eastern detour for a direct middle lane. Both states
  retain valid access to the Ashtray, exits, switch, and optional grass.
