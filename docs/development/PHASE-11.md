# PHASE 11 --- THE RAINY CITY

## Status

Phase 10 is complete. Zephyros has thrown Chuck between worlds, Chuck has
fallen through a rain-dark modern city, struck the sidewalk, vanished, and
reformed at the first city Ashtray.

The existing playable endpoint is:

- map `modern_city_arrival`
- development checkpoint `City 1`
- physical checkpoint `City 1 Ashtray`
- durable progression flag `modern_city_reached`

Phase 11 begins from that authoritative state. Do not create a second city
arrival path or replay the Zephyros transition.

This phase contains sixteen playable maps:

- six rainy night-city maps
- four modern urban-sewer maps
- six rainy day-city maps

The final daytime map ends at a Doug fir forest fragment and a short transition
cutscene. Playable forest content belongs to the following phase.

------------------------------------------------------------------------

## Phase Goal

By the end of Phase 11, the player should:

1. Explore six modern city maps at night in continuous rain.
2. Meet stationary and walking businesspeople.
3. Meet one seated homeless man.
4. Encounter raccoons using the existing combat language.
5. Learn to cross city traffic as a fast Frogger-like environmental hazard.
6. Cross one larger highway-focused map.
7. Enter an urban sewer through a YES/NO entrance.
8. Traverse four long, narrow, winding sewer maps.
9. Encounter aggressive rats, toxic sludge, Astral gaps, and one crocodile.
10. Climb out of the sewer into a different part of the city during daytime.
11. Explore six rainy daytime city maps.
12. Avoid Animal Control officers, police gunfire, traffic, and increasing
    Astral collision damage.
13. Cross a final chaotic city map where Chult and the Astral Sea have broken
    visibly into the modern world.
14. Enter the Doug Fir Forest at Night fragment through a YES/NO prompt.
15. See Chuck walk out of a Douglas fir tree at night, establishing the stable
    boundary for the following phase.

Phase 11 should make the modern city feel like a complete region with three
distinct movement rhythms: open street navigation, claustrophobic sewer
traversal, and increasingly unstable daytime streets.

------------------------------------------------------------------------

# 1. Region Structure

Use the following ordered structure:

1. `City Night 1` --- existing arrival area, expanded into the region start
2. `City Night 2`
3. `City Night 3`
4. `City Night 4`
5. `City Night 5` --- major highway crossing
6. `City Night 6` --- sewer entrance
7. `City Sewer 1`
8. `City Sewer 2`
9. `City Sewer 3`
10. `City Sewer 4` --- ladder to daytime city
11. `City Day 1`
12. `City Day 2`
13. `City Day 3`
14. `City Day 4`
15. `City Day 5`
16. `City Day 6` --- collided-city climax and forest fragment

These are recommended display names. Use the repository's established naming
conventions for final checkpoint and map IDs.

The route is ordered, but internal map layouts must vary. Streets, sewer
passages, and transitions should turn north, south, east, and west rather than
forming one continuous straight line.

Every playable map receives:

- exactly one physical Ashtray/checkpoint
- one development checkpoint through the shared checkpoint loader
- a valid arrival from the previous map
- a valid return arrival where backtracking remains available
- stable collision and camera bounds
- a tested Sanity-zero respawn state

Normal map changes within the same region must not restart that region's music.

------------------------------------------------------------------------

# 2. Modern City Visual Language

The city is modern, human-scaled, and enormous relative to one-foot Chuck.

Core materials include:

- wet concrete sidewalks
- asphalt roads
- painted traffic lines and crosswalks
- curbs and gutters
- brick, concrete, glass, and metal building faces
- lit office windows at night
- rain-dark alleys
- streetlights, traffic signals, signs, hydrants, bins, and drains
- scattered human-scale litter
- puddles and reflected light

The nighttime maps use dark blue-grey streets, warm window light, neon or
signal accents, and visible rain. The daytime maps use cold overcast light,
muted building colors, wet pavement, and the same persistent rain.

Do not make daytime sunny. It remains rainy throughout the city.

Maintain native 320x180 rendering, procedural pixel-art construction, readable
silhouettes, and the established simple animation language.

Chuck's scale must remain clear. Curbs are substantial edges, bottles are
large props, vehicle tires dwarf him, and ordinary human pedestrians read as
much larger than Chuck without drifting beyond the established NPC scale.

City maps use a readable road-and-sidewalk grid flanked by genuinely large,
solid office-building footprints. Never use narrow freestanding stretches of
office terrain: at Chuck's scale they read as implausible two-foot-tall walls,
not buildings. Most of each city block should be inaccessible building mass.
Use broad rooftop planes, deep multi-row facades, cornices, side faces, and
restrained animated office windows to establish three-quarter-view height.
Sidewalk pockets and alleys may interrupt the street edge, but must not carve
an office footprint into thin leftover strips.

------------------------------------------------------------------------

# 3. Night City Maps

Create six connected rainy city maps at night.

The maps should combine sidewalks, roads, alleys, building edges, and small
optional pockets. Not every road or sidewalk is a transition. Where ordinary
city geometry would appear to continue beyond an edge but no next map exists,
use visible Astral Sea fall blocks to show that the world is physically broken
there.

Astral blocks are impossible geography and fall hazards, not generic glowing
barriers. Do not use invisible walls where the street appears to continue.

Scatter single-cigarette collectibles throughout the night city. They should
reward observation and occasional risk without becoming a formal collectible
checklist.

## Night-City NPCs

Businesspeople appear on sidewalks. Some stand still; others use a short
patrol walk along a safe stretch of sidewalk.

Every businessperson uses this exact interaction text:

> Ah! A rat!

Include one homeless man in the night city. He sits on the sidewalk with
several bottles around him and does not patrol.

His exact interaction text is:

> Hey there buddy!

Keep the presentation restrained. The bottles and seated pose establish the
scene without additional exposition.

## Raccoons

Raccoons are the night city's ordinary enemy.

They should:

- use simple pursuit and contact damage
- be slightly stronger than rats
- remain weaker and less durable than Chult zombies
- be readable as raccoons at native scale
- reset normally after Sanity-zero return
- remain avoidable where possible

Do not turn every street into a required combat encounter.

------------------------------------------------------------------------

# 4. Traffic and Road Crossings

Roads are active Frogger-like traversal hazards.

Use fast-moving modern vehicles in readable lanes. Vehicles should enter from
offscreen or a visually credible road boundary, travel in a fixed direction,
and leave cleanly without accumulating indefinitely.

Traffic behavior must be deterministic or sufficiently patterned that the
player can observe a safe crossing window. It should feel fast and dangerous,
not random or unfair.

Vehicle contact uses the existing Sanity, damage, death, and checkpoint-return
systems. It must be severe enough that the player respects lane timing. Exact
damage may be tuned during implementation, but traffic is an environmental
hazard rather than an enemy Chuck is expected to scratch.

Road collision must not let Chuck become embedded in a vehicle or pushed out
of map bounds.

## Highway Map

One night-city map is a substantially larger highway crossing. Its main task
is navigating multiple fast traffic lanes in sequence.

The highway should include readable pauses or safe median spaces so the player
can solve it in stages. Difficulty comes from timing and lane patterns, not
from offscreen impacts or unreadable vehicle speeds.

Include the map's required Ashtray somewhere safe from active traffic.

------------------------------------------------------------------------

# 5. Night-City Sewer Entrance

The final night-city map leads to an open modern sewer entrance.

Approaching the entrance displays:

> Enter the sewer?

Options:

- `YES`
- `NO`

Selecting `NO` closes the dialogue with no additional text.

Selecting `YES` transitions to `City Sewer 1` through the normal map and
checkpoint architecture.

The entrance should visibly read as open and large enough for a human worker,
not as a Chuck-sized hole or a medieval Waterdeep grate.

------------------------------------------------------------------------

# 6. Urban Sewer Region

Create four modern urban-sewer maps.

These maps must look distinct from the Waterdeep sewer. Use modern poured
concrete, brick utility tunnels, metal pipes, maintenance walkways, drains,
ladders, culverts, warning markings, dirty runoff, and artificial utility
lighting.

The sewer maps are long, narrow, and winding. Vary their direction of travel
so the region turns through east-west and north-south runs rather than becoming
four parallel corridors.

Every sewer map receives one physical Ashtray and one development checkpoint.

## Sewer Rats

Rats are the primary sewer enemy. They use the aggressive pursuit behavior
established by the ship-hold rats rather than short passive patrols.

They should:

- notice and chase Chuck promptly
- use the existing rat-sized combat role
- reset after death/return
- stop at collision and fall hazards correctly
- remain numerous enough to create pressure without filling every corridor

## Crocodile

Include one crocodile encounter in a late sewer map.

The crocodile should:

- be much larger than Chuck and visually credible in an urban sewer
- use durability and contact danger similar to a Chult zombie
- move faster than a Chult zombie
- use straightforward pursuit
- remain escapable or avoidable rather than becoming a mandatory combat gate

Do not add a broader sewer bestiary during this phase.

------------------------------------------------------------------------

# 7. Toxic Green Sludge

Toxic green sludge is the sewer's single new terrain hazard.

It combines two established effects:

- the Sanity damage behavior of Chult thorns
- the movement slowing behavior of Feywild pollen

Standing or moving through sludge should visibly slow Chuck and inflict Sanity
damage at a consistent, readable cadence. The two effects must use the existing
terrain-hazard and ground-speed architecture rather than a sewer-only duplicate
inside `main.py`.

Sludge should be visually unmistakable from ordinary sewer water and safe wet
floor. Use it to shape routes and pressure movement, not to cover every map.

Test damage timing, slowdown, jumping interaction, respawn, and leaving the
terrain.

------------------------------------------------------------------------

# 8. Sewer Astral Jump Challenge

Astral Sea blocks appear within the sewer as visible collided-world damage.

One meaningful progression section must require a more challenging sequence
of committed jumps than previous one-gap tutorials. Build the challenge from
the existing jump and fall-hazard systems rather than adding a new movement
ability.

The sequence may combine:

- several one-tile Astral gaps
- narrow safe landings
- turns between jumps
- changing camera framing along a longer route
- nearby sludge pressure where it remains readable and fair

Every required jump must remain possible with the established committed jump.
Do not require unexplained diagonal precision, blind landings, or landing on
solid water. Failed jumps use the existing Astral fall/death presentation and
return to the current sewer Ashtray.

The Ashtray must not be placed inside the jump sequence or an enemy's immediate
notice range.

------------------------------------------------------------------------

# 9. Sewer Exit to Daytime

The fourth sewer map ends at a human-sized maintenance ladder.

Approaching it displays:

> Climb up ladder?

Options:

- `YES`
- `NO`

Selecting `NO` closes with no additional text.

Selecting `YES` transitions to `City Day 1` through the established choice,
map-transition, and checkpoint systems.

Chuck emerges in a different part of the city. It is now daytime and still
raining.

------------------------------------------------------------------------

# 10. Day City Maps

Create six connected rainy daytime city maps with layouts distinct from the
night region.

Retain the modern-city scale and traffic language while changing street
geometry, building faces, routes, and landmarks. Daylight reveals the collision
damage more clearly, and Astral Sea blocks should become increasingly common
throughout the daytime progression.

As at night, any road or sidewalk that visually continues toward a nonexistent
map must end in visible Astral fall blocks rather than an unexplained invisible
wall.

Continue scattering single-cigarette collectibles through the daytime maps.

## Day-City NPCs

Businesspeople remain present and use the same exact dialogue:

> Ah! A rat!

Do not include the homeless man in the daytime region.

Include one woman in a red dress. She patrols a longer safe stretch of sidewalk
and uses the same dialogue as the businesspeople:

> Ah! A rat!

Her red dress and longer patrol should make her readable as a distinct city
figure without adding a quest or subplot.

------------------------------------------------------------------------

# 11. Animal Control Officers

Animal Control officers are mobile daytime enemies carrying nets on long
sticks.

They use general durability and contact danger comparable to Chult zombies.
Their distinct behavior is a close-range net catch.

When Chuck is caught:

- a readable net overlay or entanglement state appears
- Chuck cannot simply walk out of the catch
- Sanity drains continuously to zero over four seconds
- normal Sanity-zero disappearance and checkpoint return follow

The four-second capture must be stable across frame rates and must not create a
second death or respawn system. Resetting or leaving the map clears any active
net state.

Animal Control officers should be avoidable where possible. Do not make every
one a mandatory combat gate.

------------------------------------------------------------------------

# 12. Police Officers

Police officers are stationary ranged hazards.

Reuse the established Spined Devil projectile architecture where practical:

- officers hold a fixed position
- a readable aiming or muzzle-flash tell precedes each shot
- bullets travel as avoidable projectiles
- projectile contact costs Sanity
- solid city geometry blocks shots consistently
- officers reset with the map

Police officers are hazards to route around, not a new cover-shooter combat
system. Do not add guns, ammunition, or ranged attacks for Chuck.

------------------------------------------------------------------------

# 13. Final Day-City Collision Map

`City Day 6` is the phase's most visibly damaged city map.

It should contain:

- many Astral Sea fall blocks and committed-jump hazards
- a patch of Chult ground tiles and shrubbery embedded in the city
- Chult raptors chasing fleeing businesspeople
- businesspeople running away along authored safe paths
- one prone businessperson on the ground
- one Chult massive dinosaur appearing to eat the prone businessperson
- police officers firing toward the dinosaurs while remaining hazards to Chuck
- one police officer who spins while firing, reusing the rotational projectile
  language of the archer in the Beholder fight
- part of a northern modern building damaged by street-view Astral Sea blocks
- one clearly readable `Doug Fir Forest at Night` reality fragment

The scene should feel chaotic, but its gameplay lanes must remain readable.
NPC pursuit tableaux, raptors, dinosaur motion, police projectiles, Astral
falls, and traffic must not create unavoidable damage at the map's Ashtray or
arrival.

The massive dinosaur is an environmental spectacle and overwhelming hazard,
not a boss. Chuck should avoid it.

The prone businessperson tableau should remain restrained and readable at
native scale. Do not add gore or a long dialogue sequence.

This map reuses the existing Beholder fight soundtrack rather than the normal
day-city music.

------------------------------------------------------------------------

# 14. Doug Fir Forest Fragment and Phase Exit

The northern building contains visible side-view Astral Sea damage and a
`Doug Fir Forest at Night` block. This is the only Phase 11 boundary presented
as an explicit planar portal interaction.

Approaching the forest block displays:

> Enter planar portal?

Options:

- `YES`
- `NO`

Selecting `NO` closes with no additional text.

Selecting `YES` begins a short side-view cutscene:

1. Begin from black.
2. Fade in on a Douglas fir forest at night.
3. Chuck walks out from a large Douglas fir tree.
4. Hold long enough for the new environment to read clearly.
5. End at a stable boundary for the next phase.

Do not implement playable forest exploration, forest enemies, or the next
region's systems during Phase 11.

------------------------------------------------------------------------

# 15. Cigarettes and Recovery

Scatter individual cigarette collectibles throughout both night and daytime
city maps.

Use the existing single-cigarette collectible and Sanity restoration behavior.
Do not introduce a new city currency, inventory item, or collectible menu.

Place cigarettes in:

- optional sidewalk pockets
- alleys
- safe traffic medians
- edges of Astral-damaged routes
- small detours that reward observation

Do not place required recovery directly inside unavoidable traffic, active
gunfire, or a checkpoint spawn.

The sewer may use recovery more sparingly unless playtesting shows its longer
hazard sequences need additional support.

------------------------------------------------------------------------

# 16. Music and Ambience

Create three regional musical identities and one intentional reuse.

## Night City

Compose an original jazzy synth city theme. It should feel nocturnal, rain-lit,
urban, catchy, and compatible with CHUCK's established retro/procedural music
language.

Favor:

- syncopated synth bass
- restrained electronic drums
- electric-key or bell-like jazz harmony
- a memorable melodic hook
- wet, reflective atmosphere

Do not make it modern cinematic synthwave or generic lo-fi background music.

## Urban Sewer

Compose a darker funky sewer theme. The broad reference is the memorable
underground groove associated with classic Super Mario Bros. underground
music, but the composition must remain original.

Favor:

- a sparse, catchy low-register motif
- dark funk bass
- clipped percussion
- pipe-like or hollow industrial timbres
- enough rhythmic motion for long winding maps

Do not copy Nintendo melodies, bass lines, harmony, or arrangement.

## Day City

Compose a daytime counterpart to the jazzy synth identity. It may share a motif
or harmonic language with the night theme, but its arrangement should reflect
cold overcast daylight rather than nighttime neon.

The day maps remain rainy and slightly uneasy.

## Final Day Map

Reuse the established Beholder fight soundtrack for `City Day 6`.

## Ambience and Continuity

Rain remains audible throughout both city regions. Traffic, distant horns,
tires on wet pavement, sewer drips, pipe resonance, and gunfire may appear as
stylized secondary ambience or effects.

Music must continue uninterrupted between maps sharing the same regional cue.
It changes only at the night-city/sewer boundary, sewer/day-city boundary, and
the final chaotic map's deliberate Beholder-theme switch.

------------------------------------------------------------------------

# 17. State, Saves, and Development Checkpoints

Use only the progression state needed to restore this region reliably.

Possible durable flags include:

- modern city reached *(existing)*
- night city completed
- urban sewer entered
- daytime city reached
- final city collision reached
- Doug Fir Forest transition completed

Do not create a general quest system.

Every map uses the shared checkpoint-loading architecture. Development
checkpoints expose all sixteen maps for testing regardless of player progress.
Real Continue loads only the player's active saved Ashtray and progression
state.

Sanity-zero return must reset:

- raccoons
- sewer rats
- crocodile
- traffic entities and lane timing to a safe deterministic state
- toxic-sludge damage state
- Animal Control net capture
- police projectiles
- final-map chase/tableau actors as appropriate

Respawning must never place Chuck inside moving traffic, sludge, active
gunfire, an enemy notice radius, or an Astral fall tile.

------------------------------------------------------------------------

# 18. Architecture

Reuse the established systems for:

- maps and transitions
- checkpoints, saves, Continue, and development loading
- NPC dialogue and patrols
- enemy pursuit and reset
- scratch combat
- Sanity damage and return
- committed jumping
- Astral fall hazards
- terrain damage and slowdown
- projectile enemies
- YES/NO interactions
- cutscene scenes
- camera and native rendering
- music continuity and sound effects

Add modular systems only where Phase 11 requires genuinely new behavior:

- reusable traffic lanes and vehicle hazards
- combined slowing/damaging toxic sludge
- Animal Control net capture

Keep city, sewer, traffic, and cutscene content out of `main.py`. Do not place
all sixteen maps' special cases directly into `world_scene.py`; prefer data and
small reusable controllers where repeated behavior is expected.

Vehicle, NPC, enemy, and projectile collections must remove offscreen or dead
objects cleanly. The region should not accumulate entities or progressively
lose performance during a long play session.

------------------------------------------------------------------------

# 19. Out of Scope

Do not implement during Phase 11:

- playable Doug Fir forest maps
- forest NPCs or enemies
- city interiors
- drivable vehicles
- weapons or ammunition for Chuck
- a police wanted system
- stealth meters
- traffic-light hacking
- a quest log
- inventory or equipment progression
- collectible tracking UI
- a sewer crafting or survival system
- additional city or sewer regions beyond the specified sixteen maps
- a boss fight

Phase 11 is focused on:

**six rainy night streets, four modern sewer maps, six rainy day streets,
traffic traversal, modern-city NPCs and enemies, one combined sludge hazard,
increasing Astral collision damage, and the short Doug Fir Forest handoff.**

------------------------------------------------------------------------

# 20. Acceptance Criteria

## Region Structure

- [ ] The existing Phase 10 city arrival becomes `City Night 1` without a
      duplicate startup path.
- [ ] Six night-city maps are playable and connected.
- [ ] Four urban-sewer maps are playable and connected.
- [ ] Six day-city maps are playable and connected.
- [ ] Every map has exactly one physical Ashtray.
- [ ] Every map has a shared-loader development checkpoint.
- [ ] Travel directions vary across the region.
- [ ] Camera bounds, transitions, return arrivals, saves, and respawns are
      stable.

## Night City

- [ ] Night streets visibly read as a modern city in rain.
- [ ] Stationary and walking businesspeople are present.
- [ ] Businesspeople say only `Ah! A rat!`.
- [ ] One seated homeless man appears with bottles around him.
- [ ] He says only `Hey there buddy!`.
- [ ] Raccoons are stronger than rats and weaker than zombies.
- [ ] Raccoons pursue, damage, reset, and can be avoided.
- [ ] Single cigarettes are scattered through optional routes.
- [ ] Non-transitioning street edges use visible Astral fall blocks where the
      city otherwise appears to continue.

## Traffic

- [ ] Vehicles move quickly in readable lanes and clean themselves up.
- [ ] Traffic timing is observable and fair.
- [ ] Vehicle contact uses Sanity and checkpoint return correctly.
- [ ] One larger highway map makes multi-lane crossing its primary challenge.
- [ ] Safe medians or staged pauses keep the highway readable.
- [ ] Respawn never occurs in active traffic.

## Urban Sewer

- [ ] The entrance uses `Enter the sewer?` with silent `NO`.
- [ ] The sewer looks modern rather than medieval.
- [ ] All four maps are narrow, long, winding, and directionally varied.
- [ ] Aggressive rats use ship-hold pursuit.
- [ ] One late sewer map contains a faster zombie-strength crocodile.
- [ ] The crocodile can be avoided or escaped.
- [ ] Toxic green sludge both slows and damages Chuck.
- [ ] Sludge remains readable from safe water and floor.
- [ ] A multi-jump Astral challenge is harder than prior single-gap crossings
      while remaining fair with the existing jump.
- [ ] Failed jumps return Chuck to the current sewer Ashtray.
- [ ] The final ladder uses `Climb up ladder?` with silent `NO`.

## Day City

- [ ] Daytime is visibly distinct from night while remaining rainy.
- [ ] Day-city layouts are new rather than palette swaps of the night maps.
- [ ] Businesspeople retain the exact night-city dialogue.
- [ ] The homeless man does not appear during the day.
- [ ] A woman in a red dress patrols a long sidewalk and says `Ah! A rat!`.
- [ ] Animal Control officers use zombie-like durability and a readable net
      catch.
- [ ] Net capture drains Sanity to zero over exactly four seconds and clears on
      reset.
- [ ] Stationary police use readable, avoidable gun projectiles.
- [ ] Astral damage becomes increasingly visible through the day maps.
- [ ] Single cigarettes remain scattered through optional routes.

## Final Collision Map

- [ ] The last map contains many Astral jump hazards.
- [ ] A Chult tile-and-shrub fragment is embedded in the city.
- [ ] Raptors visibly chase fleeing businesspeople.
- [ ] One prone businessperson and massive-dinosaur feeding tableau are
      readable without gore.
- [ ] Police fire toward the dinosaurs while remaining hazards to Chuck.
- [ ] One police officer spins and shoots using the Beholder archer language.
- [ ] The Beholder fight soundtrack is reused intentionally.
- [ ] The northern building contains street-view Astral damage and a readable
      Doug Fir Forest at Night block.
- [ ] The Ashtray and arrival are safe from all active hazards.

## Forest Handoff

- [ ] The forest block asks `Enter planar portal?`.
- [ ] `NO` closes with no additional text.
- [ ] `YES` begins from black and fades into a side-view forest at night.
- [ ] Chuck walks out of a large Douglas fir tree.
- [ ] The phase ends at a stable boundary without playable forest content.

## Audio and Technical Quality

- [ ] Night city has an original catchy jazzy synth theme.
- [ ] The urban sewer has an original dark funky underground theme.
- [ ] Day city has a rainy daytime jazzy synth counterpart.
- [ ] City rain ambience remains stable across map transitions and respawns.
- [ ] Music does not restart between maps sharing a regional cue.
- [ ] The final map switches cleanly to the Beholder fight soundtrack.
- [ ] Traffic and projectile entities do not accumulate over time.
- [ ] Existing tests pass.
- [ ] Targeted tests cover traffic, sludge, net capture, projectiles,
      checkpoints, transitions, and the forest handoff.

------------------------------------------------------------------------

## Implementation Progress

- [x] Slice 1: expanded the authoritative Phase 10 endpoint into a 72x54
      `City Night 1` region start while preserving its map/checkpoint IDs.
- [x] Established wet modern building, window, sidewalk, curb, road, rain,
      loose-cigarette, and exact shared Astral fall-hazard language.
- [x] Kept the first physical Ashtray wired through save, Continue, direct
      development loading, and Sanity-zero respawn.
- [x] Added reusable deterministic four-direction traffic lanes and City
      Night 1's two-lane teaching crossing, with fixed populations, severe
      Sanity contact, safe-footing recovery, and normal Ashtray reset.
- [x] Added connected `City Night 2` with its own Ashtray, four loose
      cigarettes, reciprocal street opening, full-scale office blocks, rain,
      and a second deterministic two-lane crossing.
- [x] Added the first two stationary businesspeople, one patrol
      businessperson, exact `Ah! A rat!` dialogue, and an avoidable
      three-scratch raccoon using the normal damage/combat/reset lifecycle.
- [x] Added east-turning `City Night 3` with its own Ashtray, four cigarettes,
      two avoidable raccoons, north/south traffic, one stationary and one
      patrol businessperson, and only Astral-severed unauthored edges.
- [x] Added the one seated homeless man beside oversized bottle clusters with
      exact `Hey there buddy!` dialogue and no patrol or extra exposition.
- [ ] Next: City Night 4 using the shared city systems and another route turn;
      reserve the major highway for City Night 5.
- [ ] The dedicated night-city soundtrack remains an authored audio pass.

------------------------------------------------------------------------

# 21. Suggested Implementation Sequence

Keep each pass bounded to one coherent slice:

1. Formalize city terrain/art and expand the existing arrival into
   `City Night 1` with its checkpoint and regional music continuity.
2. Implement reusable traffic lanes and one teaching street crossing.
3. Complete Night City Maps 2--4 with businesspeople, homeless man, raccoons,
   cigarettes, rain, and Astral-broken non-exits.
4. Build the highway-focused Night City Map 5.
5. Build Night City Map 6 and the modern sewer entrance choice.
6. Establish urban-sewer terrain, aggressive rats, and Sewer Maps 1--2.
7. Implement toxic sludge and the harder Astral jump sequence.
8. Complete Sewer Maps 3--4, the crocodile encounter, and daytime ladder.
9. Establish rainy daytime art and Day City Maps 1--2, including the red-dress
   patrol NPC.
10. Implement Animal Control net capture and Police projectile behavior.
11. Complete Day City Maps 3--5 with increasing Astral damage.
12. Build Day City Map 6's full collision tableau and Beholder-theme reuse.
13. Implement the forest-fragment choice and short Douglas fir cutscene.
14. Complete the three-cue music pass, full checkpoint audit, performance
    soak, and start-to-finish playtest.

Do not build all sixteen maps in one implementation pass. Finish and verify one
map or tightly related system slice at a time.

------------------------------------------------------------------------

# 22. Final Playtest

## Full Route

Play from the Phase 10 city arrival through:

1. all six night-city maps
2. the highway crossing
3. the sewer entrance prompt
4. all four urban-sewer maps
5. the Astral jump challenge
6. the crocodile encounter
7. the ladder to daytime
8. all six day-city maps
9. the collided-city climax
10. the Doug Fir Forest prompt and cutscene

## Development Checkpoints

Load every one of the sixteen maps directly and verify that each initializes
enough progression state to function without replaying Zephyros' tower or the
preceding city maps.

Check specifically:

1. Does nighttime immediately read as modern, wet, and human-scaled?
2. Are businesspeople and the homeless man readable without exposition?
3. Are raccoons dangerous but clearly below zombie durability?
4. Can every traffic pattern be understood before committing to a crossing?
5. Is the highway demanding without relying on blind impacts?
6. Does the sewer feel modern and distinct from Waterdeep?
7. Do rats use the intended aggressive pursuit?
8. Does toxic sludge both slow and damage consistently?
9. Is the Astral jump sequence harder but still fair?
10. Can the crocodile be escaped without defeating it?
11. Does daytime feel like a different city district rather than a palette
    swap?
12. Does net capture last four seconds and resolve through normal Sanity-zero
    return?
13. Are police shots readable and blocked by city geometry?
14. Does the final map feel chaotic while preserving a readable route?
15. Are the Chult fragment, fleeing NPCs, dinosaur tableau, and police response
    understandable at native scale?
16. Does the forest fragment clearly establish the next region without
    beginning its gameplay?
17. Do all sixteen Ashtrays save, Continue, and respawn correctly?
18. Does a long playthrough remain stable without traffic, rain, projectiles,
    or enemies accumulating?

Phase 11 is complete when Chuck has crossed the rainy city at night, survived
the urban sewer, emerged into the rainy daytime city, navigated its collided
final district, and walked out of a Douglas fir tree at night.
