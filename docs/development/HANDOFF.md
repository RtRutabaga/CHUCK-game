# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `7fe8729` (`Add scratchable Waterdeep grass reward`)
- Current work: Waterdeep/sewer grass expansion and proximity guidance
- Active phase: Phase 4 — Chult Jungle (`PHASE-4.md`)

## Completed This Pass

The complete Phase 4 contract now lives at `docs/development/PHASE-4.md` and is
the active scope referenced by the docs guide. Phase 3's final jungle tableau
holds for two seconds after its authored completion, then loads a playable Chult
landing through the shared checkpoint loader.

`chult_jungle.txt` is now a contained 64x60 padded exploration area, slightly larger in
authored tile area than the sewer. Its dedicated procedural
tileset uses the cutscene's dark ground, canopy, trunk, vine, and leaf colors so
normal gameplay continues the same visual language. Dense vegetation is solid;
the landing and branching clearings support ordinary movement and camera
behavior. All walkable terrain remains connected.

Large vegetation masses establish a northbound route with opportunities to
circle them on either side. The first mass near Chult 1 creates an immediate
optional branch. Farther north, three `_` tiles pass through a dense wall under
a human-scale fallen trunk. Jungle ground draws below it and a new transparent
overhead tileset row draws the log above Chuck, making the scale relationship
visible without adding crouching or special-case movement.

The checkpoint registry now includes a hidden, non-saveable `chult_landing`
runtime entry and a saveable/development-visible `chult_anchor` displayed as
`Chult 1`. Both require `sewer_completed` and the new minimal durable flag
`chult_reached`. The cutscene, development selector, Ashtray activation,
CONTINUE, and Sanity-zero respawn therefore use the same existing loader and
save architecture.

Four undead markers now populate broad clearings: two zombies and two skeletons.
`UndeadEnemy` is one reusable entity with data-tuned variants. It uses the
existing collision mover for simple direct pursuit inside a 112-pixel notice
radius. Zombies move at 18 px/s, deal 20 Sanity, and require eight scratches;
skeletons move at 25 px/s, deal 15 Sanity, and require six. Both use the exact
human NPC sprite/hitbox scale, so they tower over Chuck. Scratch dispatch remains
one-target-per-swipe, contact uses existing Sanity i-frames, and the normal
enemy rebuild on Astral return restores defeated undead from map markers.

The pantry now joins the temporary tutorial-map set. While Chuck is within two
tiles of teal sky material, the existing hint renderer repeats the exact earlier
line `Press SPACE to jump`; it remains hidden elsewhere and during the fall.

The cutscene's final tableau still holds for two seconds after completion, then
fades to black over 0.75 seconds. `chult_landing` now authors a reusable
checkpoint `fade_in` flag, so the shared loader replaces the scene while black
and WorldScene fades in over 0.75 seconds with simulation/control locked. Chult
1 development loads and saved CONTINUE restoration do not request that fade.

Twenty-five `|` tiles form six small thorny-undergrowth patches scattered
through optional open clearings.
The Chult tileset renders three stable variants as bright angular stems over the
existing ground language. `systems/terrain_hazard.py` owns the reusable terrain
effect lookup and footprint contact scan. Thorns cost 10 Sanity on foot through
normal i-frames/hurt feedback; airborne Chuck is safe. No required route crosses
the patches. The backpack and boot were removed from the northern clearing at
Sean's request, including their map characters, sprites, generator functions,
dialogue data, and obsolete placement test. Phase 4 therefore needs a different
previous-traveler environmental scene before acceptance is complete.

The existing north route now resolves into a distinct three-tile-wide worn
track. It runs beneath a dense overhead canopy arch at the top edge and carries
one named `boundary:chult_deeper` marker. Boundary markers are authored map
metadata and intentionally spawn no runtime entity until a real destination is
available. This preserves the transition system's rule that actual exits must
target loadable maps, while giving the next Chult area a stable connection
point. No second map, narrative beat, progression flag, or placeholder teleport
was added.

Chult now has its dedicated exploration theme. `data/music/chult.py` defines an
original 40-bar D-Dorian loop at 112 BPM (85.7 seconds) through the existing
offline sequencer. Its two-bar syncopated bass ostinato persists across the
groove intro, A/A' hooks, darker B section, humid breakdown, and full return.
Ten reusable voices layer deep bass and sub pulse with pluck lead, flute, bells,
kick/snare/hats, and two new generic instrument voices: warm pitched jungle toms
and a short dry woodblock. `chult.wav` is cached at the established 22.05 kHz,
16-bit mono format and `AREA_MUSIC` starts it for all normal Chult entry paths.
No ambience subsystem or map/gameplay changes were added.

Dense Chult collision masses no longer read as repeated green masonry. The
`dense_jungle` tileset row now builds interlocking elliptical broad-leaf clusters
over dark woody seams and vines. A new solid `/` terrain tile preserves `#`
underneath while adding a y-sorted `jungle_tree` prop. The map authors 165 of
these only where dense vegetation was already solid. Three deterministic 34x46
tree variants layer broad tropical crowns, visible trunks, and hanging vines;
they tower over Chuck and human NPCs and overlap into path edges without moving
the collision boundary. No open tile, enemy, checkpoint, or route changed.

The same dense masses now also carry 170 y-sorted `jungle_shrub` props on solid
`\\` tiles, distributed among the remaining `#` cells with extra coverage along
vegetation edges. Three deterministic 28x24 variants use six overlapping
pointed leaves, readable central veins, dark understory bases, and brighter
tropical midtones. Each shrub is wider than two Chucks and taller than Chuck,
filling the visual gap below the tall tree crowns without changing collision.

Waterdeep now authors three reusable `breakable_grass` markers on ordinary
stone, framing the ruined foundation at its northeast, southwest, and southeast
corners. The southeast tuft replaces the exposed cigarette that previously sat
just south of the ruin. Four more dirt-based instances are spaced through the
sewer from its early descent into the late Astral maze. Each walkable 16x16 tuft
joins the existing scratch target dispatch ahead of enemies; one swipe plays the
normal scratch sound, shakes the tuft, sends eight deterministic leaf chips
outward over 0.42 seconds, and creates exactly one ordinary cigarette beneath
it. While Chuck is within two tiles of intact grass, Waterdeep and sewer reuse
the exact `Press F to scratch` hint already established by the sewer rats. The
check is explicitly map-scoped and never appears in tavern, pantry, Chult, or
future areas. Grass and rewards reset with an ordinary map reload; no durable
flag or inventory state was added. `tools/generate_breakable_sprites.py`
reproduces the native-scale procedural art for later map reuse.

## Verification

- All 28 test modules pass through their standalone runners (pytest is not
  installed in the bundled runtime).
- New Chult coverage verifies map dimensions/spawns, shared-loader cutscene
  handoff, required progression, Ashtray save data, and relaunch/CONTINUE.
- Existing tileset coverage now requires every used Chult terrain to have art.
- Chult coverage now also flood-fills every walkable tile and verifies the
  three-tile log tunnel is horizontally traversable and enclosed above/below.
- The generated `assets/tilesets/chult.png` is 64x48 and source-reproducible via
  `tools/generate_chult_tileset.py`.
- `tools/generate_undead_sprites.py` reproduces the 48x30 zombie and skeleton
  sheets. Targeted tests cover human scale, six/eight-hit durability, pursuit,
  wall collision, avoidable placement, contact damage, defeat, and respawn reset.
- `AudioSystem.play_music()` now treats an identical filename/loop request as a
  no-op. Docks, tavern, and pantry all configure the same Waterdeep theme, so
  crossing those boundaries keeps its playback position. Different tracks
  still load normally, and `stop_music()` clears the remembered request. The
  audio suite directly verifies all three cases.
- Pantry coverage verifies the jump reminder is proximity-scoped. Chult tests
  verify partial cutscene fade, black handoff, control-locked WorldScene fade,
  and completion back to ordinary simulation.
- A 25th terrain-hazard suite verifies contact classification, airborne safety,
  WorldScene damage/i-frames, authored patch count, and a thorn-free route from
  the landing to the north end. Native render review confirms clear silhouettes.
- A 26th Chult-exit suite verifies the single named boundary, its exact stable
  location, the continuous three-wide approach, solid authored edge, and
  dedicated ground/overhead tileset rows. Native 320x180 review confirms the
  darker track and canopy opening read clearly from the northern clearing.
- Music coverage now verifies Chult's 80+ second duration, ten active layers,
  bass-forward relative mix, seven-hit syncopated bass bars, Dorian melodic
  color, three tom and four woodblock hits per bar, valid pitches, rendered
  format, peak headroom, and loop seam. The 85.7-second render peaks at 0.75;
  a diagnostic 220 Hz low-pass retained about 88% of total RMS, confirming the
  mix is materially low-end-led. Transition coverage verifies the file exists.
- The 27th vegetation suite verifies 150-180 trees and 160-180 shrubs, solid
  terrain preservation, all six generated variants, tree scale above humans,
  shrub scale above and wider than Chuck, and deterministic sprite selection.
  Existing Chult flood-fill and tileset coverage verify route/collision stability.
- The 28th breakable-grass suite verifies exact southeast-ruin placement,
  all three ruin placements, four safe dirt-based sewer placements, removal of
  the former exposed pickup, one-shot reward creation through WorldScene scratch
  dispatch, debris lifetime, native 16x16 scale, proximity behavior, and the
  Waterdeep/sewer-only hint boundary.

## Playtest Focus

1. Finish the pantry fall and confirm the completed cigarette tableau holds for
   about two seconds before player control returns in Chult.
2. Confirm the playable ground feels like the same jungle shown in the cutscene,
   with crisp native-scale terrain and stable collision/camera bounds.
3. Walk north to the nearby Ashtray. Quit and use CONTINUE; verify Chuck returns
   at Chult 1 with saved Sanity.
4. Deplete Sanity after activating it and confirm Chuck's established quiet
   return lands at Chult 1.
5. From the title choose DEV CHECKPOINTS → Chult 1 and confirm it loads directly
   with the Ashtray lit and no replay of prior regions.
6. Explore north around both sides of the first vegetation mass; confirm one
   direction reads as optional wandering without becoming a trapped pocket.
7. Find the low fallen-log passage farther north. Confirm Chuck visibly passes
   beneath the trunk and emerges on the other side without a crouch input.
8. Approach each undead type and confirm it begins a slow readable pursuit.
   Verify skeletons are modestly faster, both can be escaped, and neither blocks
   the route merely by existing.
9. Scratch a zombie eight times and a skeleton six times. Confirm contact costs
   Sanity without rapid repeated drain, then die and verify all four return.
10. Move docks → tavern → pantry → tavern → docks and confirm the Waterdeep
    music never returns to its opening. Enter the sewer and confirm its distinct
    theme still starts normally.
11. Approach the teal sky in the pantry and confirm `Press SPACE to jump`
    appears, then walk away and confirm it clears.
12. Finish the cutscene and confirm the jungle tableau fades fully out, followed
    by a smooth fade into controllable Chult with no bright frame between scenes.
13. Find the thorn patches scattered through the jungle clearings. Walk into one twice
    quickly and confirm only one 10-Sanity hit lands during i-frames; jump across
    it without damage, then confirm the main route can bypass it entirely.
14. Revisit the northern clearing and confirm the backpack and boot are gone,
    with no invisible collision or leftover interaction prompt where they stood.
15. Continue north onto the darker worn trail. Confirm it reads as the route
    deeper, the canopy closes over Chuck at the threshold, and the stable edge
    stops him cleanly without a broken transition or missing-map error.
16. Listen through the Chult theme from Chult 1. Confirm the bass hook is
    immediately memorable, percussion feels jungle-oriented and syncopated,
    the middle breakdown stays propulsive, and the full loop has no audible
    seam. Die and CONTINUE in Chult; confirm music remains stable and restarts
    appropriately on a fresh launch.
17. Walk the entire Chult route at native scale. Confirm the former green blocks
    now read as dense tropical tree masses, trunks and crowns layer naturally,
    Chuck remains visible on paths, and no tree appears to open or close a route.
18. Check the vegetation edges and interiors for broad-leaf shrubs. Confirm they
    read as distinct low understory beneath the trees, vary naturally, and do not
    imply any collision difference from the surrounding dense growth.
19. In Waterdeep, find the grass at the ruined foundation's southeast corner.
    Scratch it once and confirm the tuft bursts into quick outward leaf chips,
    reveals one cigarette, and leaves no invisible collision. Leave and re-enter
    Waterdeep to confirm the grass resets normally.
20. Check all three ruin tufts and the four sewer tufts. Confirm `Press F to
    scratch` appears only within roughly two tiles of intact grass, clears after
    shredding it, still appears for the rat tutorial, and never follows Chuck
    into the tavern, pantry, or Chult.

## Next Bounded Task

Choose a replacement previous-traveler environmental scene that does not restore
the removed backpack or boot, then finish the complete Phase 4 acceptance run.
Do not begin Phase 5 without an active Phase 5 contract or explicit direction.
