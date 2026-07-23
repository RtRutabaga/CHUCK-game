# PHASE 7 --- THE PIRATE SHIP

## Status

The ship transition, opening interior room, and soundtrack were
completed in Phase 6.

Phase 7 begins inside the ship and focuses on exploration, dialogue, and
character animation rather than combat.

Implemented so far:

- The opening compartment now confines its animated sea portholes to the
  north hull. Human-scale dark open doorways occupy the west/east walls and
  connect its two side routes, while the floor ladder begins the playable
  phase. The unused south-wall opening has been restored to solid hull.
- The ladder leads to a reversible cargo-filled lower hold with reused pantry
  shelves and jars that scratch-break into cigarette cartons, sixteen ordinary
  rats that notice and chase Chuck like the temple snakes, uninterrupted ship
  music, one physical Ashtray, and shared-loader `Ship Hold` development
  entry. Approaching any live ship ladder opens a direction-correct `Climb up
  ladder?` or `Climb down ladder?` YES/NO prompt; NO closes silently and YES
  follows the existing named transition. Each ladder is a continuous 16×32
  structure matching the human crew's 16×30 sprite scale rather than a
  repeated Chuck-height tile.
- The west open passage leads to a reversible working galley with one physical
  Ashtray. The pirate chef gives the authored warning, then begins a
  collision-aware, animated cleaver pursuit; Chuck cannot clear him by
  scratching, so the encounter remains an escape through galley lanes.
- The east open passage leads to reversible crew quarters with hanging bunks,
  an oversized round mess table, one physical Ashtray, and a seated pirate who
  sways with his mug. His first greeting and shorter repeat line are selected
  by a durable conversation flag. The deck hatch remains visible but inert;
  the open captain-cabin passage is now connected to its finished room.
- The crew quarters' east opening now enters the captain's cabin. Interacting
  with or scratching its oversized chest plays a lid-opening animation and
  drops a physical golden 40-cigarette carton in front, with no dialogue box.
  The open and collected states persist through the cabin's Ashtray and
  CONTINUE without duplicating the reward.
- The exterior deck now uses `docs/design/pirate ship.png` as its composition
  reference and includes the authored crew performances, fencing hazard,
  rocking sea presentation, Jeffries, helm, and physical Ashtray. Animated
  crew tricorns use shaped side-view crowns and narrow brims so turning toward
  Chuck during dialogue never obscures their faces with a dark rectangle.
- After the chef encounter, seated-pirate conversation, four deck
  conversations, and captain's chest are all complete, the camera finds the
  captain emerging at the midship ladder and follows his animated walk across
  the deck to the stern helm. A nearby crewman announces `Captain on deck!`;
  restrained `...` dialogue beats pace the accusation, plank order, crew
  objection, and refusal. A narrow physical plank then opens through the
  starboard rail; the captain and objecting pirate flank its approach while
  Chuck is marched to the rail and control returns. The outer endpoint remains
  safely bounded. Stepping onto the plank now starts staggered streams of
  Astral Sea and overhead volcanic Hell blocks while Jeffries shouts `It's back!
  The purple is back!`. Astral chunks tile the exact animated fall-hazard art
  shared by the sewer, pantry, Chult, and temple. Hell chunks show a bird's-eye
  plane of cracked basalt plates, branching lava channels, and molten vents
  below the ship rather than a side-facing flame strip. Each fragment uses a
  different deterministic arrangement of staggered plates and lava pools so
  neighboring chunks do not join into a uniform grid. Both materials enter at
  the east screen edge, travel completely off the west edge, and continuously
  recycle behind the ship. They remain non-colliding and the kick/fall is
  reserved for the next slice.

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

The crew stages a narrow plank through the starboard rail. Chuck is marched to
its approach, then the player regains control and can walk to its currently
bounded outer end.

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

-   [x] Ship interior is fully explorable.
-   [x] Lower hold contains rats and reused pantry assets.
-   [x] Galley chef chases Chuck.
-   [x] Crew quarters contain the seated pirate.
-   [x] Captain's chest grants Premium Buhetian Halfling Leaf (+40
    cigarettes).
-   [x] Pirate animations are richer than previous NPCs.
-   [x] NPC dialogue changes after first conversations.
-   [x] Deck rocking and animated waves are implemented.
-   [x] Sword-fighting pirates damage Chuck.
-   [x] Deck animations synchronize with the soundtrack.
-   [x] Jeffries delivers collided-world dialogue.
-   [x] Other pirates dismiss Jeffries.
-   [x] Captain sequence triggers correctly.
-   [x] Moving Astral Sea and Hell blocks appear.
-   [ ] Chuck falls into a Hell block.
-   [ ] Phase ends with the Nine Hells transition.
