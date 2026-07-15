# PHASE 3 — WATERDEEP TAVERN, PANTRY, AND FALL TO CHULT

## Status

Phase 2 is complete.

Phase 3 begins with the tavern entrance accessible in Waterdeep and ends with a dedicated cutscene of Chuck falling through the sky toward Chult.

Phase 4 will begin in Chult.

---

## Phase Goal

By the end of Phase 3, the player must be able to:

1. Enter the Waterdeep tavern.
2. Explore a readable tavern interior.
3. Notice a cheese-related exploration hook.
4. Follow the cheese hook toward the pantry.
5. Enter the pantry.
6. Discover a broken floor made from normal floor, Astral Sea hazard blocks, and teal sky/cloud blocks.
7. Navigate the pantry floor hazards.
8. Fall through a teal sky/cloud block.
9. Trigger Chuck's existing fall animation.
10. Transition from gameplay into a dedicated circa-1994-style falling cutscene.
11. Watch Chuck fall through the sky toward Chult.

The phase ends with the falling-to-Chult cutscene.

Do not build the playable Chult area during Phase 3.

---

# 1. Waterdeep Tavern Interior

Create the tavern interior accessible through the tavern entrance prepared at the end of Phase 2.

The tavern should be a compact, readable top-down interior consistent with the game's existing native 320×180 presentation and procedural pixel-art rendering.

Suggested visible features:

- front entrance
- common room
- bar or serving counter
- tables and chairs
- hearth or fireplace
- barrels and crates
- a small number of patrons or staff
- a rear route toward the pantry

Do not overfill the room.

Chuck's small size should remain visually clear through the scale of furniture and the interior layout.

Use the existing dock worker as the human scale reference for new human NPCs.

## Tavern Transition

Entering through the exterior tavern doorway should transition Chuck into the tavern.

Requirements:

- Chuck appears at the corresponding interior entrance.
- Chuck can return to Waterdeep through the tavern entrance before entering the pantry transition.
- Movement input should not immediately bounce Chuck back through the doorway.
- Interior collision should be stable.
- Camera behavior should remain consistent with the existing game.
- Tavern music or ambience should transition cleanly.

Use existing scene, map, transition, camera, and audio systems where appropriate.

---

# 2. Tavern NPCs

Use only enough NPCs to make the tavern feel occupied.

Possible roles include:

- bartender
- server
- patron
- cook or kitchen worker

Dialogue should remain short and use the game's existing dialogue system.

The tavern does not need to function as a quest hub.

NPC interactions may help draw attention toward the rear of the tavern or food area, but the cheese hook should remain primarily environmental.

---

# 3. The Cheese Hook

The cheese is an exploration hook rather than an inventory item.

Place a visually readable cheese element or simple cheese trail in the tavern that naturally draws Chuck toward the rear of the building and the pantry.

Possible implementations include:

- a dropped piece of cheese
- several crumbs
- cheese visible beneath or around furniture
- cheese positioned near the route into the pantry

Use the simplest version that reads clearly at the game's native scale.

The player should not need to pixel hunt.

## Cheese Interaction

If Chuck reaches or interacts with cheese:

- do not add an inventory system
- do not add a cheese counter
- do not add equipment
- do not add a permanent stat bonus

A small sound cue or very brief text response is sufficient.

Possible text:

> Cheese.

or:

> It is cheese.

The pantry should remain discoverable without requiring the player to collect every cheese element.

---

# 4. The Pantry

Create a small pantry connected to the rear of the tavern.

The pantry should read through simple environmental elements such as:

- shelves
- sacks
- barrels
- crates
- jars
- food storage
- cheese
- wooden floorboards

The main gameplay feature of the pantry is the damaged and partially replaced floor.

## Pantry Floor Layout

The pantry floor should contain a deliberate mix of three floor types.

### Normal Floor

Standard walkable pantry floor.

Chuck can move normally across these blocks.

### Astral Sea Blocks

Reuse the established Astral Sea visual language from the Phase 2 sewer.

Use the same or closely related purple and dark-blue pixelated nebula appearance already established in the game.

Astral Sea blocks are fall hazards.

If Chuck falls through an Astral Sea block:

1. Trigger the existing fall animation and hazard behavior established in the sewer.
2. Treat the fall as a legitimate gameplay death/failure.
3. Use the existing death or recovery flow associated with this hazard.

Do not create a separate Astral Sea fall system if the Phase 2 implementation can be reused.

### Teal Sky and Cloud Blocks

Add a second visually distinct broken-world floor type.

These blocks should depict a simple teal sky with readable clouds.

At the game's scale, this sky is the visual connection to Chult.

Do not attempt to render detailed jungle scenery below the pantry floor.

The teal sky and clouds should be simple, readable, and visually distinct from the Astral Sea blocks.

Sky/cloud blocks are the successful transition route.

If Chuck falls through a sky/cloud block:

1. Trigger the same existing Chuck fall animation used for the Astral Sea hazard.
2. Do not trigger the normal hazard death.
3. Continue the fall into the Phase 3 cutscene.
4. Transition from normal gameplay presentation into the falling-through-the-sky sequence.

---

# 5. Pantry Navigation

Design the pantry floor as a compact hazard-navigation area.

The player should move across safe floor while avoiding Astral Sea fall hazards.

The teal sky/cloud blocks should be positioned so the player can eventually fall through them and trigger the Chult transition.

Do not create a large maze.

Do not add a new equipment requirement.

Do not add a quest marker.

Use the movement and jump systems already established during Phase 2.

The pantry may include a tempting cheese position, route, or environmental arrangement that encourages the player to cross the broken floor.

The transition occurs when Chuck enters or falls into a sky/cloud block.

---

# 6. Fall Behavior

Reuse the existing Phase 2 fall animation and gameplay as the starting point for both pantry fall types.

## Astral Sea Fall

Astral Sea block:

> existing fall animation → existing fall hazard death/recovery behavior

## Sky Fall

Teal sky/cloud block:

> existing fall animation → continue downward → transition into dedicated cutscene

The initial fall should feel mechanically familiar because the player already encountered the Astral Sea hazard in the sewer.

For the sky route, the fall continues instead of resolving as a death.

---

# 7. Falling to Chult Cutscene

The final major feature of Phase 3 is a dedicated cutscene showing Chuck falling through the sky toward Chult.

Present the cutscene in a style appropriate to an approximately 1994-era 16-bit adventure game.

The cutscene should feel authored rather than like normal top-down gameplay.

## Cutscene Goal

Communicate that Chuck is falling a very long distance through open sky toward Chult.

The player does not control Chuck during the cutscene.

## Visual Direction

Use the game's established pixel-art language and native rendering approach.

The sequence may use:

- a dedicated cutscene scene or state
- controlled sprite animation
- vertical background scrolling
- moving cloud layers
- simple parallax
- changing cloud density
- a changing sky background
- deliberate framing of Chuck during the descent

The teal sky/cloud appearance should visually connect to the pantry sky blocks.

Chuck should remain recognizable throughout the sequence.

Keep his animation simple and consistent with the game's style.

Do not use modern cinematic rendering, 3D camera movement, or high-resolution art that conflicts with the rest of the game.

## Suggested Sequence

1. Chuck falls through a pantry sky block.
2. The existing gameplay fall animation begins.
3. Instead of resolving as a hazard death, the fall continues.
4. Gameplay transitions into the dedicated cutscene.
5. Chuck is visible falling through a teal sky.
6. Clouds move vertically past Chuck.
7. The sequence continues long enough to establish significant height.
8. The visual presentation begins to suggest approach toward Chult.
9. The cutscene ends at the transition point into Phase 4.

The exact timing and composition may be adjusted during implementation and playtesting.

## Audio

Use music and sound consistent with the soundtrack bible and existing game.

The cutscene may transition from tavern or pantry audio into a dedicated falling cue or the beginning of Chult's musical identity.

Wind or simple falling sound effects may be used if they fit the existing SNES-inspired audio presentation.

Keep the audio stylized rather than realistic.

---

# 8. Phase End

Phase 3 ends during or immediately at the conclusion of the falling-to-Chult cutscene.

Do not create the playable Chult landing area in this phase.

Do not return player control in Chult during Phase 3.

Phase 4 begins with the Chult arrival and first playable Chult area.

The Phase 3 implementation should leave a clean transition point for Phase 4.

---

# 9. State and Progression

Use only the state required for the tavern, pantry, and Chult transition.

Potential state flags include:

- tavern entered
- pantry entered
- Chult fall triggered
- Phase 3 cutscene started
- Phase 3 cutscene completed

Only create flags that are technically necessary.

Do not build a quest-state system for this phase.

The cheese is not a progression key unless a small technical state is required for the chosen implementation.

---

# 10. Art Requirements

New Phase 3 art may include:

- tavern floor and wall elements
- tavern entrance
- bar or counter
- tables and chairs
- barrels and crates
- hearth or fireplace
- pantry shelves
- sacks and food storage
- cheese and crumbs
- damaged pantry floor
- Astral Sea floor blocks based on existing sewer visuals
- teal sky floor blocks
- simple cloud graphics
- cutscene sky background
- cutscene cloud layers
- Chuck falling animation adjustments if required

Match the game's established simple procedural pixel-art presentation.

Reuse existing rendering systems and visual conventions where possible.

---

# 11. Architecture

Use the architecture established in Phases 1 and 2.

Prefer existing systems for:

- scenes and maps
- entities
- interactions
- collision
- jumping
- fall hazards
- audio
- camera
- game state

Reuse the Phase 2 Astral Sea fall hazard behavior.

The sky/cloud floor should branch from the familiar fall behavior into the new cutscene transition.

Keep the cutscene implementation contained and readable.

Do not place the entire tavern, pantry, and cutscene implementation directly into `main.py`.

Do not build a general-purpose cutscene editor for this phase.

A dedicated cutscene scene/state or similarly bounded implementation is appropriate.

---

# 12. Out of Scope

Do not implement during Phase 3:

- the playable Chult starting area
- full Port Nyanzaru
- the Tomb of Annihilation plot
- Chult guides
- dinosaur racing
- jungle survival systems
- hunger or thirst
- crafting
- equipment progression
- a large inventory
- major combat expansion
- boss fights
- a full Chult enemy roster
- procedural jungle generation
- world-map fast travel

Phase 3 is focused on:

**the tavern, the cheese hook, the pantry hazard floor, the sky-block transition, and the falling-to-Chult cutscene.**

---

# 13. Acceptance Criteria

## Tavern

- [ ] The player can enter the tavern from Waterdeep.
- [ ] The tavern reads clearly as a tavern.
- [ ] Chuck's scale remains consistent.
- [ ] Human NPC scale remains consistent with the existing dock worker.
- [ ] Interior collision is stable.
- [ ] The player can return to Waterdeep before the pantry transition.
- [ ] Tavern audio transitions correctly.

## Cheese Hook

- [ ] The cheese hook is readable from normal gameplay.
- [ ] It draws the player toward the pantry.
- [ ] Cheese does not create an inventory or equipment system.
- [ ] The pantry remains discoverable without collecting every cheese element.

## Pantry

- [ ] The pantry reads clearly as a food-storage room.
- [ ] Normal walkable floor is clearly readable.
- [ ] Astral Sea hazard blocks reuse the established sewer visual language.
- [ ] Teal sky/cloud blocks are visually distinct.
- [ ] Sky/cloud blocks read as teal sky with clouds at native scale.
- [ ] The pantry floor layout is compact and navigable.

## Astral Sea Fall

- [ ] Falling through an Astral Sea block triggers the existing fall animation.
- [ ] The existing hazard death/recovery behavior occurs.
- [ ] The player can retry the pantry.

## Sky Fall

- [ ] Falling through a teal sky/cloud block triggers Chuck's fall animation.
- [ ] The fall does not trigger the normal hazard death.
- [ ] The fall transitions into the dedicated cutscene.
- [ ] The transition is reliable.

## Cutscene

- [ ] The cutscene removes normal player control.
- [ ] Chuck is visibly falling through a teal sky.
- [ ] Clouds or other simple background elements communicate vertical descent.
- [ ] The cutscene visually matches the game's circa-1994 16-bit presentation.
- [ ] The sequence communicates a long fall toward Chult.
- [ ] Audio transitions correctly.
- [ ] The cutscene reaches a clean Phase 4 transition point.
- [ ] Playable Chult is not implemented during Phase 3.

## Technical Quality

- [ ] The full sequence works from a clean game start.
- [ ] Waterdeep and Phase 2 systems continue to work.
- [ ] Scene transitions do not duplicate or lose Chuck.
- [ ] Pantry hazard collision is reliable.
- [ ] Astral Sea and sky falls resolve differently as intended.
- [ ] Camera behavior remains stable.
- [ ] Audio state remains stable.
- [ ] Existing tests pass.
- [ ] Targeted regression tests are added where practical.

---

# 14. Final Playtest

Before declaring Phase 3 complete, play from the existing Waterdeep opening through the full falling cutscene without developer shortcuts.

Check:

1. Can the tavern be entered normally after Phase 2?
2. Does the tavern feel like a complete game area?
3. Is the cheese hook easy to notice without a quest marker?
4. Does the pantry route feel natural?
5. Are normal floor, Astral Sea blocks, and sky/cloud blocks visually distinct?
6. Does an Astral Sea fall behave like the established sewer hazard?
7. Can the player recover and retry after an Astral Sea fall?
8. Does falling through a sky block begin with the familiar fall animation?
9. Does the sky fall continue instead of killing Chuck?
10. Does the cutscene feel visually consistent with a circa-1994 16-bit game?
11. Does the falling sequence clearly communicate movement through open sky toward Chult?
12. Does the phase end at a clean point for Phase 4 to begin in Chult?

Phase 3 is complete when the player has moved from the Waterdeep tavern, through the pantry's broken floor, and into the falling-to-Chult cutscene.
