# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `69d8118` (`Add Phase 4 Chult landing, undead, and thorn hazard`)
- Current work: Phase 4 through the route-deeper boundary
- Active phase: Phase 4 — Chult Jungle (`PHASE-4.md`)

## Completed This Pass

The complete Phase 4 contract now lives at `docs/development/PHASE-4.md` and is
the active scope referenced by the docs guide. Phase 3's final jungle tableau
holds for two seconds after its authored completion, then loads a playable Chult
landing through the shared checkpoint loader.

`chult_jungle.txt` is now a contained 60x60 exploration area, slightly larger in
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
save architecture. Chult is deliberately silent pending its dedicated music
slice; no placeholder Waterdeep track leaks into the jungle.

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

Ten `|` tiles form one thorny-undergrowth cluster in an optional open clearing.
The Chult tileset renders three stable variants as bright angular stems over the
existing ground language. `systems/terrain_hazard.py` owns the reusable terrain
effect lookup and footprint contact scan. Thorns cost 10 Sanity on foot through
normal i-frames/hurt feedback; airborne Chuck is safe. No required route crosses
the cluster.

An optional northern clearing now holds two oversized human expedition props:
a 30x32 packed backpack and a 26x16 discarded boot. They are solid standing
props backed against vegetation and approachable from three directions. The
backpack is more than twice Chuck's height and returns the sole line `Someone
left quickly.`; the boot is mute. This is deliberately generic environmental
history, not an overt Tomb campaign reference.

The existing north route now resolves into a distinct three-tile-wide worn
track. It runs beneath a dense overhead canopy arch at the top edge and carries
one named `boundary:chult_deeper` marker. Boundary markers are authored map
metadata and intentionally spawn no runtime entity until a real destination is
available. This preserves the transition system's rule that actual exits must
target loadable maps, while giving the next Chult area a stable connection
point. No second map, narrative beat, progression flag, or placeholder teleport
was added.

## Verification

- All 27 test modules pass through their standalone runners (pytest is not
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
  WorldScene damage/i-frames, authored cluster size, and a thorn-free route from
  the landing to the north end. Native render review confirms clear silhouettes.
- A 26th traveler-scene suite verifies exact authored placement, open approach,
  sprite scale relative to Chuck/humans, prop dialogue mapping, and the single
  restrained line. The normal tileset and dialogue suites also cover the new data.
- A 27th Chult-exit suite verifies the single named boundary, its exact stable
  location, the continuous three-wide approach, solid authored edge, and
  dedicated ground/overhead tileset rows. Native 320x180 review confirms the
  darker track and canopy opening read clearly from the northern clearing.

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
13. Find the thorn cluster in the mid-jungle side clearing. Walk into it twice
    quickly and confirm only one 10-Sanity hit lands during i-frames; jump across
    it without damage, then confirm the main route can bypass it entirely.
14. Find the backpack and boot in the northern clearing. Confirm their human
    scale makes Chuck look appropriately tiny, neither blocks the route, the
    backpack says `Someone left quickly.`, and the boot remains mute.
15. Continue north onto the darker worn trail. Confirm it reads as the route
    deeper, the canopy closes over Chuck at the threshold, and the stable edge
    stops him cleanly without a broken transition or missing-map error.

## Next Bounded Task

Create the dedicated bass-forward Chult exploration soundtrack as one bounded
audio slice. Keep it original, groove-led, jungle-oriented, and consistent with
the established procedural retro soundtrack; do not add a new map in that pass.
