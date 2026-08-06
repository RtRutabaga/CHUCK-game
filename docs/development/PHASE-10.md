# PHASE 10 --- ZEPHYROS' TOWER

## Status

Phase 9 is complete. Chuck has crossed the thirteen-map Feywild region and
reached the stable boundary at the Twilight Crossroads.

Phase 10 begins beyond that boundary with a peaceful Feywild approach to the
Cloud Staircase. It introduces Zephyros the Cloud Giant, the first major
character who clearly understands the collided worlds.

By the end of this phase, Chuck is hurled from the top of Zephyros' tower and
arrives in a modern rainy city. Phase 11 begins with playable city content.

The supplied visual references establish three useful anchors:

- Zephyros is ancient, bald, warm-faced, and dressed in purple and gold.
- His tower is impossibly tall, narrow, pale stone beneath a whimsical pointed
  roof, with the Aerie at its upper level.
- The Aerie is a vast open polygonal chamber with four enormous nests around a
  central opening to the levels below.

Translate those ideas into CHUCK's native 320x180 procedural pixel-art style.
Do not copy text, labels, or non-game presentation from the references.

------------------------------------------------------------------------

## Phase Goal

By the end of Phase 10, the player should:

1. Discover the Cloud Staircase.
2. Reach Zephyros' tower.
3. Explore the tower.
4. Meet Zephyros.
5. Learn the first substantial information about the collided worlds.
6. Be launched toward another world.
7. Arrive in a modern rainy city.

The following phase begins in the modern city.

------------------------------------------------------------------------

# 1. Feywild Cloud Staircase

Create a peaceful Feywild map centered around a Cloud Staircase.

The staircase should dominate the area and immediately attract the player's
attention. The surrounding environment must remain visually consistent with
the established Feywild. There are no combat encounters here.

The existing Twilight Crossroads boundary should connect to this map through
the normal map-transition and checkpoint architecture.

As with every authored gameplay map, include one physical Ashtray/checkpoint.

------------------------------------------------------------------------

# 2. Cloud Staircase Interaction

Approaching the staircase displays:

> Climb the cloud staircase?

Options:

- `YES`
- `NO`

Selecting `NO` closes the dialogue with no additional text.

Selecting `YES` begins the Tower Arrival cutscene.

------------------------------------------------------------------------

# 3. Tower Arrival Cutscene

Present Zephyros' tower from a side, street-level perspective.

The cloud staircase retracts upward into the tower as Chuck climbs. Once the
animation finishes, transition back to the normal top-down perspective.

Chuck now stands on the southern stone platform outside the tower.

------------------------------------------------------------------------

# 4. Tower Exterior Map

The player begins on a circular stone platform surrounded by open sky and
drifting clouds.

Features:

- open sky
- drifting clouds
- southern platform
- a large northern archway

There is intentionally very little to interact with. The obvious path is north
through the arch.

Include one physical Ashtray/checkpoint. Until the Aerie slice is implemented,
the northern arch remains a stable, readable, inert boundary.

------------------------------------------------------------------------

# 5. The Aerie

Walking through the northern arch loads the Aerie.

The Aerie contains:

- four enormous griffon nests
- open tower walls
- clouds surrounding the tower
- a central hole in the floor
- a rope descending into the tower

One nest contains a griffon.

Reuse the Horned Devil / massive Chult dinosaur behavior. The griffon is a
roaming hazard that is easy to outrun. Its purpose is to reinforce the scale of
the tower rather than create a difficult fight.

Include one physical Ashtray/checkpoint.

------------------------------------------------------------------------

# 6. Rope Descent

Approaching the rope displays:

> Climb down the rope?

Options:

- `YES`
- `NO`

Selecting `NO` closes the dialogue with no additional text.

Selecting `YES` begins the Zephyros Introduction cutscene.

------------------------------------------------------------------------

# 7. Zephyros Introduction Cutscene

The perspective changes to a side view.

Chuck climbs down the rope. After several moments, an impossibly enormous face
slowly enters the frame. Zephyros blinks, smiles, and raises a gigantic hand
beneath Chuck. Chuck steps onto the palm.

The remainder of the scene consists of Zephyros filling nearly the entire
screen, with dialogue displayed beneath him.

Zephyros must read as ancient, kindly, immense, and quietly whimsical rather
than threatening.

------------------------------------------------------------------------

# 8. Zephyros Dialogue

Use this dialogue exactly, preserving the pauses as separate dialogue beats:

> Hello little friend!
>
> ...
>
> Yes... YES!
>
> ...
>
> The Entity said you would be coming.
>
> Now, as you know, the worlds have been shuffled.
>
> Smashed.
>
> A little bit crinkled.
>
> Most don't know.
>
> Most don't see.
>
> The typical being, you see, is like the halfling leaf inside a cigarette.
>
> They don't know whether they're still neat inside the pack...
>
> ...or whether they've already been smashed together in the ashtray.
>
> But you, Chuck...
>
> You're part of the ashtray.
>
> You see.
>
> ...
>
> The Entity has gone quiet.
>
> It is frightened, Chuck.
>
> Yes...
>
> Yes...
>
> Something must be done.
>
> ...
>
> Oh...
>
> No.
>
> Not you.
>
> Heavens, no.
>
> You're more of a fighter than a winner, aren't you, Chuck?
>
> Not to worry.
>
> I have my best people working on it.
>
> Your role in all this...
>
> ...is simply to make it through.
>
> As you always do.
>
> ...
>
> Now then!
>
> I shall fling you onward!

This conversation intentionally answers some questions while creating many
more.

Do not explain:

- who The Entity is
- why Zephyros knows Chuck
- why Zephyros knows Chuck's name

Chuck remains silent and has no internal monologue.

------------------------------------------------------------------------

# 9. Tower Launch Cutscene

Return to the exterior side view of the tower.

Zephyros casually throws Chuck into the sky. From this distance Chuck is only
a tiny moving dot. The throw should feel effortless rather than violent: it is
simply absurdly powerful.

------------------------------------------------------------------------

# 10. Flight Between Worlds

Transition to the established falling motif.

Unlike previous transitions, Chuck initially moves horizontally across the
screen before gradually beginning to descend.

Astral Sea blocks appear throughout the sky. As the flight continues,
skyscraper wall cross-sections, office windows, and concrete building
fragments appear among the Astral blocks. They should resemble pieces of a
modern city stitched into the sky.

Eventually Chuck collides with one city fragment. The perspective shifts and
Chuck flies diagonally downward through a rainy modern city. Rain falls
throughout the remainder of the sequence.

------------------------------------------------------------------------

# 11. Modern City Arrival

Chuck loses momentum, falls the remaining distance, and strikes a sidewalk.

His Sanity reaches zero. He disappears exactly as in normal gameplay deaths,
then immediately reforms at the city's first Ashtray checkpoint. The camera
remains fixed.

Chuck quietly lights a cigarette, looks around, and control returns.

The modern city endpoint may be a contained arrival tableau sufficient to
support the cutscene handoff and checkpoint. Do not implement playable city
exploration during Phase 10.

------------------------------------------------------------------------

# 12. Music

Compose three pieces for this phase.

## Cloud Staircase / Tower

Peaceful, airy, wonder-filled, and ancient. It should evoke height, openness,
and quiet curiosity.

## Zephyros Conversation

Gentle, wise, slightly whimsical, and warm rather than mysterious. This is not
ominous exposition. It should feel like talking to a kindly old giant who
casually understands impossible things.

## Launch / Modern City Transition

Reuse the established falling motif, then gradually layer in wind, rain, urban
textures, and subtle synth elements. The music should evolve seamlessly into
the modern-city atmosphere without a hard cut.

All compositions must remain original and follow the established procedural
retro soundtrack language.

------------------------------------------------------------------------

# 13. State, Checkpoints, and Architecture

Use the shared map, checkpoint, save, scene, choice, collision, camera, and
audio systems.

- Every new playable map receives exactly one physical Ashtray.
- Development entries use the shared checkpoint loader.
- `CONTINUE` and Sanity-zero return use the same authored checkpoints.
- YES/NO prompts must use the established choice presentation.
- `NO` closes silently.
- Cutscenes remain input-free apart from `ESC` quitting the application.
- Sanity carries across non-death transitions.
- The city impact uses the established death/return presentation rather than
  inventing a second death system.

Keep cutscene logic in dedicated scene modules. Do not place the phase in
`main.py` or fold its presentation into unrelated world-map logic.

------------------------------------------------------------------------

# 14. Out of Scope

Do not implement during Phase 10:

- modern city gameplay
- city NPCs
- city enemies
- city interiors
- an inventory or equipment system
- new player powers
- a quest log

Those city systems begin in Phase 11.

------------------------------------------------------------------------

# 15. Acceptance Criteria

## Cloud Staircase

- [x] Peaceful Feywild staircase map is implemented.
- [x] The staircase dominates the composition.
- [x] There are no combat encounters.
- [x] One physical Ashtray saves and respawns correctly.
- [x] Approaching the staircase opens the exact YES/NO prompt.
- [x] `NO` closes silently.
- [x] `YES` begins the arrival cutscene.

## Tower Arrival and Exterior

- [x] The tower is shown from a side perspective.
- [x] Chuck visibly climbs while the cloud staircase retracts upward.
- [x] The cutscene returns to top-down play on the southern platform.
- [x] The exterior has open sky, drifting clouds, and a large north arch.
- [x] One physical Ashtray saves and respawns correctly.

## Aerie and Griffon

- [x] The Aerie contains four enormous nests.
- [x] One nest contains a griffon.
- [x] The griffon reuses the established massive-hazard behavior.
- [x] It is easy to outrun and not a mandatory fight.
- [x] The central hole and descending rope are visually readable.
- [x] One physical Ashtray saves and respawns correctly.

## Zephyros

- [x] Rope interaction uses the exact YES/NO prompt.
- [x] The side-view descent establishes Chuck's scale.
- [x] Zephyros' face, blink, smile, and hand are readable.
- [x] Chuck steps onto Zephyros' palm.
- [x] The complete supplied dialogue is implemented exactly.
- [x] Zephyros remains kindly and warm rather than ominous.

## Launch and City Arrival

- [x] Zephyros casually throws Chuck from the tower.
- [x] Chuck begins in horizontal flight and gradually descends.
- [x] Astral blocks and modern city fragments appear together.
- [x] The sequence becomes a diagonal rainy-city descent.
- [x] Chuck hits the sidewalk, reaches zero Sanity, and vanishes.
- [x] Chuck reforms at the city's first Ashtray.
- [x] Chuck lights a cigarette and looks around as in the Chult landing.
- [x] Control returns only at the contained city arrival endpoint.

## Audio and Technical Quality

- [ ] Three phase cues are implemented with the specified identities.
- [ ] Music transitions do not hard-cut or layer accidentally.
- [x] Development checkpoints load every playable Phase 10 map.
- [x] Save, Continue, death, and respawn remain stable.
- [x] Existing tests pass.
- [x] Targeted regression tests cover new choices, cutscenes, and checkpoints.

------------------------------------------------------------------------

# 16. Implementation Sequence

Implement Phase 10 in bounded slices:

1. Cloud Staircase map, prompt, Tower Arrival cutscene, and exterior platform.
2. Aerie map, four nests, griffon, central opening, and rope prompt.
3. Zephyros introduction, giant-scale presentation, and full dialogue.
4. Tower launch and horizontal flight between worlds.
5. Rainy-city descent, death/return, first city Ashtray, and final handoff.
6. Three-cue music pass and full Phase 10 acceptance playtest.

Do not start Phase 11 city gameplay while completing these slices.

------------------------------------------------------------------------

# Implementation Log

(Append completed slices here as they land, newest last.)

- Slice 1: added the Cloud Staircase approach, exact silent-NO choice, tower
  arrival cutscene, circular tower exterior, two shared development
  checkpoints, and one physical Ashtray per gameplay map. The existing
  Feywild theme remains uninterrupted pending Phase 10's dedicated audio
  slice. The arrival now uses a long close-scale wall climb followed by a
  distant complete-tower shot where Chuck is too small to render and the cloud
  stair visibly retracts upward. The Aerie arch is a deliberate stable
  boundary for slice 2.
- Slice 2: connected the arch to a 60x46 open-sided Aerie with four enormous
  nests, one slow griffon emerging from a nest, a central solid interior shaft
  and giant rope, reversible exterior travel, one physical Ashtray, and the
  `Zephyros 3` shared development checkpoint. The exact rope prompt is live;
  both answers close silently until slice 3 can connect `YES` to the complete
  Zephyros introduction without a partial cinematic placeholder.
- Slice 2 visual polish: replaced the square-reading clipped platform with a
  rounded elliptical tower floor, changed the central opening from animated
  sky to the near-black tower interior, and anchored the rope to a giant iron
  cleat on the south stone lip.
- Exterior scale polish: reduced the southern exterior platform from a broad
  34x27-tile ellipse to a compact roughly 20x20-tile stone island while
  expanding the embedded tower facade from 192x128 to 320x224 pixels. The
  tower and arch now extend beyond the native viewport and visibly dwarf
  Chuck; checkpoint and Aerie transition behavior are unchanged.
- Slice 3: connected rope `YES` to a dedicated input-free introduction scene.
  Chuck descends against cloud-giant masonry; Zephyros' warm blue-grey face
  enters, blinks and smiles; a giant palm rises and Chuck steps onto it. The
  exact supplied 36-beat dialogue advances automatically in the established
  panel. Its final line served as the stable boundary until slice 4 connected
  the throw; the dedicated conversation cue remains reserved for the planned
  audio pass.
- Slice 4: continued directly from Zephyros' final line into an input-free
  launch. A distant whole-tower shot reduces Chuck to a two-pixel dot during
  the effortless throw; a close shot then follows his horizontal flight and
  gradual descent. Exact animated Astral hazard tiles arrive before authored
  office and concrete fragments accumulate in the same sky. The established
  falling motif returns after a short fade, and a city-fragment collision
  hands directly into slice 5's rainy descent.
- Slice 5: continued the collision into an input-free diagonal descent through
  a rain-dark modern street canyon. Chuck loses horizontal momentum, strikes
  the sidewalk, reaches zero Sanity, vanishes, and reforms beside the first
  city Ashtray using the established return presentation. He looks around,
  inserts a cigarette, and takes a drag before a fade hands control to a
  deliberately contained rainy city block. `City 1` and the saveable City
  Ashtray use the shared checkpoint loader; the map has exactly one physical
  Ashtray and no exits, NPCs, enemies, interiors, or other Phase 11 content.
