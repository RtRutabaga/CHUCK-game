# PHASE 7 --- THE PIRATE SHIP

## Status

The ship transition, opening interior room, and soundtrack were
completed in Phase 6.

Phase 7 begins inside the ship and focuses on exploration, dialogue, and
character animation rather than combat.

Implemented so far:

- The opening compartment now confines its animated sea portholes to the
  north hull. Human-scale dark open doorways occupy the other three walls and
  establish future interior routes, while a southern floor ladder begins the
  playable phase.
- The ladder leads to a reversible cargo-filled lower hold with reused pantry
  shelves and jars that scratch-break into cigarette cartons, sixteen ordinary
  rats, uninterrupted ship music, one physical Ashtray, and shared-loader
  `Ship Hold` development entry.
- The west open passage leads to a reversible working galley with one physical
  Ashtray. The pirate chef gives the authored warning, then begins a
  collision-aware, animated cleaver pursuit; Chuck cannot clear him by
  scratching, so the encounter remains an escape through galley lanes.
- The east open passage leads to reversible crew quarters with hanging bunks,
  an oversized round mess table, one physical Ashtray, and a seated pirate who
  sways with his mug. His first greeting and shorter repeat line are selected
  by a durable conversation flag. The deck hatch remains visible but inert;
  the open captain-cabin passage is now connected to its finished room.
- The crew quarters' east opening now enters the captain's cabin. Its oversized
  chest grants Premium Buhetian Halfling Leaf (+40 cigarettes) exactly once,
  stays visibly open afterward, and persists that state through the cabin's
  Ashtray and CONTINUE. The captain and accusation sequence remain unstarted.
- `docs/design/pirate ship.png` is the authoritative composition reference
  for the later exterior deck map; that deck has not been built yet.

------------------------------------------------------------------------

# Phase Goal

By the end of this phase the player should:

1.  Explore the pirate ship.
2.  Meet the crew.
3.  Find the captain's treasure.
4.  Receive **Premium Buhetian Halfling Leaf** (+40 cigarettes).
5.  Speak to every major NPC.
6.  Witness the captain accuse Chuck of theft.
7.  Walk the plank.
8.  Fall into a moving Hell block and transition to the Nine Hells.

------------------------------------------------------------------------

# 1. Ship Layout

The completed starting room is reused.

From there the player explores:

-   lower hold
-   galley
-   crew quarters
-   captain's cabin
-   deck

## Lower Hold

Reached via the southern ladder.

Contains reused pantry shelving, sacks, jars, crates and many rats.

This is the primary combat area aboard ship.

## Galley

The pirate chef notices Chuck.

Dialogue:

> "Damn! Another rat got in, come er' you little bugger!"

The chef chases Chuck with a cleaver.

## Crew Quarters

Contains hammocks, a round table, a seated pirate, ladder to the deck
and the captain's cabin door.

The pirate greets Chuck in a pirate accent and comments that he's never
seen a rat wearing a coat before.

------------------------------------------------------------------------

# 2. Captain's Cabin

Contains a treasure chest.

Opening it grants:

**Premium Buhetian Halfling Leaf**

+40 cigarettes.

Only obtainable once.

------------------------------------------------------------------------

# 3. Pirate NPC Philosophy

Pirates should have noticeably richer animation than previous NPCs.

Most pirates should have rhythmic body movement synchronized with the
soundtrack and ship rocking.

Every important NPC should have different dialogue on first interaction
versus later conversations.

------------------------------------------------------------------------

# 4. The Deck

The deck is the visual centerpiece.

It contains:

-   concertina player
-   two pirates sword fighting
-   cheering pirate with tankard
-   dancing pirate
-   Jeffries tied to the mast

The concertina player simply performs while the existing soundtrack
continues.

The sword-fighting pirates wander while fencing.

Touching them damages Chuck's Sanity.

The cheering pirate periodically raises his tankard.

The dancing pirate performs a jig.

Jeffries constantly struggles against the mast.

The entire deck should feel lively and synchronized.

------------------------------------------------------------------------

# 5. Ship Motion

The deck should visibly rock with the sea.

Use subtle camera movement, deck movement, or both.

Synchronize rocking with the established soundtrack.

Ocean waves should use animated waves rather than Waterdeep's simple
moving dots.

------------------------------------------------------------------------

# 6. Jeffries

Jeffries is partially aware of the collided worlds.

Example dialogue:

> "The sea is wrong, the land is wrong. Open your eyes!"

> "Don't go into the purple! DON'T GO INTO THE PURPLE!"

> "Why don't they see!?"

> "Half the crew is gone... lost to the purple. They don't even remember
> them."

Other pirates dismiss him:

> "Don't mind Jeffries over there tied to the mast. He's gone mad. Too
> much sun, I think."

------------------------------------------------------------------------

# 7. Progression

The ending sequence begins only after:

-   speaking with every major pirate
-   opening the captain's chest

------------------------------------------------------------------------

# 8. Walk the Plank

The captain appears and accuses Chuck of stealing his halfling leaf.

He orders Chuck to walk the plank.

A pirate objects:

> "But we've all grown fond of the smoking rat, Cap."

The captain refuses.

Moving Astral Sea blocks begin appearing over the ocean.

Moving Hell blocks appear alongside them.

Jeffries shouts:

> "It's back! The purple is back!"

Chuck is kicked from the plank and lands in a Hell block.

------------------------------------------------------------------------

# 9. Ending Cutscene

Reuse the Chult falling presentation and music.

Chuck falls into the Nine Hells.

Gameplay ends upon arrival.

Phase 8 begins there.

------------------------------------------------------------------------

# 10. Story Notes

Jeffries is one of the first NPCs partially aware of reality.

The rest of the crew rationalize the strange events instead.

Do not fully explain the collided worlds.

------------------------------------------------------------------------

# 11. Acceptance Criteria

-   [ ] Ship interior is fully explorable.
-   [x] Lower hold contains rats and reused pantry assets.
-   [x] Galley chef chases Chuck.
-   [x] Crew quarters contain the seated pirate.
-   [x] Captain's chest grants Premium Buhetian Halfling Leaf (+40
    cigarettes).
-   [x] Pirate animations are richer than previous NPCs.
-   [x] NPC dialogue changes after first conversations.
-   [x] Deck rocking and animated waves are implemented.
-   [ ] Sword-fighting pirates damage Chuck.
-   [ ] Deck animations synchronize with the soundtrack.
-   [x] Jeffries delivers collided-world dialogue.
-   [x] Other pirates dismiss Jeffries.
-   [ ] Captain sequence triggers correctly.
-   [ ] Moving Astral Sea and Hell blocks appear.
-   [ ] Chuck falls into a Hell block.
-   [ ] Phase ends with the Nine Hells transition.
