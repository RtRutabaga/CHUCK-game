# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `81f8930` (sewer prompts/highway edge fix)
- Current work: inserted the requested pre-fight Phlegethos traversal map
- Active scope: `docs/development/PHASE-11.md`
- Next implementation slice: playtest Fractured Way in sequence; Phase 12
  remains unopened until its scope document exists

## Completed This Pass

- Inserted `phlegethos_fractured_way` between Rubble Pass and the unchanged
  Fortress Approach fight. The 76x48 route winds around dense dark rubble and
  three small lava ponds before a cliff-backed, four-jump Astral course.
- Added one slow 128x128 Pit Fiend beyond notice range from the required path,
  plus three lava-bound flameskulls that provide setting motion without
  blocking progression.
- Added a procedural modern bus shelter and reused the umbrella businessman
  with exact city dialogue (`Ah! A rat!`). Five nearby Astral fragments leave
  a broad clear approach so Chuck can reach and interact with him.
- Added one Ashtray and shared-loader/development checkpoint `Phlegethos 5`.
  Fortress Approach now displays as `Phlegethos 6`; its IDs, arrival name,
  entry dialogue, battle boundary, and cutscene choreography are unchanged.
- Focused Fractured Way, Rubble Pass, Phase 8, and checkpoint/save suites all
  pass. All 111 repository suites pass in isolated processes; source, tools,
  and tests compile cleanly. The map loads and draws at native resolution
  headlessly, and the bus-stop, Astral-course, and Pit-Fiend compositions were
  visually inspected.

- Tightened the automatic modern-sewer choices to exact one-tile zones. The
  manhole marker now sits immediately at its lip, and the final sewer ladder
  asks only when Chuck reaches its foot; nearby arrival and approach tiles do
  not raise either prompt. Prompt text, YES/NO behavior, and destinations are
  unchanged.
- Closed City Night 5's misleading unauthored northern highway opening with a
  three-tile-deep shared Astral fall band across its roads, median, and
  pavement. The authored east/west transitions and highway challenge remain
  unchanged.
- Focused Night 5, Night 6, Sewer 4, and Day 1 tests pass, including explicit
  non-trigger proximity and full-boundary assertions. The three affected
  checkpoints load and render headlessly, and source/tools compile cleanly.

- Fixed close-contact scratch resolution without changing its presentation.
  If a living enemy has entered Chuck's own footprint, that enemy receives the
  committed swipe before normal forward targets are considered. Otherwise the
  original forward hitbox, target order, and one-target-per-swipe rule remain
  exact. Scenery and reactive flowers do not receive the overlap allowance.
- Added focused system coverage for trapped-enemy reach and target priority,
  plus a live Feywild thorn-mite regression with the mite fully inside Chuck
  and outside the forward paw rectangle. Combat and Feywild checks pass,
  modern-sewer/Twilight regressions pass, compilation is clean, and the
  headless title scene renders successfully.

- Added the 92x38 City Sewer 1 as a narrow three-leg route running north,
  east, then south. Its future continuation remains visibly severed by exact
  Astral fall tiles rather than pretending City Sewer 2 already exists.
- Added a dedicated procedural modern-sewer tileset: poured concrete, gray
  brick repairs, exposed metal pipes, animated utility lights, slab walkways,
  safe wet floor, warning stripes, animated runoff, and shared Astral art.
  Waterdeep's medieval dirt/mud sewer remains unchanged.
- Completed City Night 6's YES transition into the named sewer arrival and
  added an aligned walk-back route. The reusable choice schema now supports a
  validated optional arrival-facing direction; NO remains a silent close.
- Added the map's physical Ashtray/shared-loader checkpoint, three cigarettes,
  and five spaced rats using exact ship-hold pursuit. Rats respect walls and
  Astral terrain and reset normally after Sanity-zero return.
- Focused tests cover map topology/materials, exact transitions, choice data,
  shared checkpoint loading, aggressive pursuit/collision/reset, native
  rendering, and the absence of exterior rain inside the sewer. All 95 suites
  pass in isolated processes; compilation and headless title/City Sewer 1
  launches are clean.

- Opened City Night 5's western approach into the reciprocal 88x60 City Night
  6. Four intact 32x20 office masses frame a turning intersection, while all
  unauthored exterior routes remain exact shared Astral fall terrain.
- Added the map's physical Ashtray/shared-loader checkpoint, rain, four
  cigarettes, one avoidable raccoon, two stationary businesspeople, one
  vertical patrol, and two fixed-population traffic lanes. Death return resets
  the traffic and raccoon through the existing shared world-reset path.
- Added an 80x64 open concrete sewer entrance with a black worker-scale arch,
  descending stairs, handrails, and a shallow approach trigger. It presents
  exact `Enter the sewer?` / YES / NO text; both choices close silently until
  City Sewer 1 is authored in the next bounded slice.
- Focused tests cover topology, office scale, safe reachability, exact Map 5/6
  alignment, shared checkpoint loading, entrance art/scale/prompt behavior,
  native rendering, and Sanity-zero reset. All 94 suites pass in isolated
  processes; compilation and headless title/City Night 6 launches are clean.

- Opened City Night 4's western sidewalk into the reciprocal 112x48 City
  Night 5. Four full-scale office blocks frame the highway corridor, while
  the unauthored western continuation remains exact shared Astral fall terrain.
- Added two sixteen-tile carriageways carrying eight fixed-population,
  alternating vertical traffic lanes. Zebra markings, broad approaches, and
  a safe ten-tile median make the main Frogger challenge readable in stages.
- Added the map's own physical Ashtray/shared-loader checkpoint, rain, five
  cigarettes, one avoidable raccoon, two stationary businesspeople, and one
  horizontal-patrol businessperson. Death return resets the raccoon and all
  lane phases through the existing shared world-reset path.
- Focused tests cover topology, office bounds, highway staging, lane markers,
  safe reachability, exact Map 4/5 alignment, shared checkpoint loading,
  native rendering, and Sanity-zero reset. All 93 suites pass in isolated
  processes; compilation and headless title/City Night 5 launches are clean.

- Opened City Night 3's north sidewalk into the reciprocal 84x60 City Night 4.
  Four offset, full-size office blocks retain the city's scale and every
  unauthored edge remains exact shared Astral fall terrain.
- Added the map's own physical Ashtray/shared-loader checkpoint, rain, four
  cigarettes, two optional-arm raccoons, two stationary businesspeople, one
  horizontal-patrol businessperson, and two horizontal traffic lanes.
- Focused tests cover topology, building bounds, safe reachability, exact
  Map 3/4 entrance alignment, checkpoint/world initialization, traffic, native
  rendering, and Sanity-zero return with raccoon reset.
- All 92 suites pass in isolated processes; compilation is clean. The title
  loop and City Night 4 checkpoint launch headlessly, and the native arrival
  composition was visually inspected.

- Opened City Night 2's east sidewalk into the new reciprocal 80x56 City
  Night 3. Four large office blocks retain credible city scale; all other
  unauthored directions end visibly in the shared Astral fall hazard.
- Added the map's physical Ashtray/shared-loader checkpoint, rain, four loose
  cigarettes, two optional-arm raccoons, one stationary businessperson, one
  vertical-patrol businessperson, and two vertical traffic lanes.
- Added the region's one homeless man as a seated non-patrolling NPC beside
  two clusters of human-scale bottles. His exact sole line is
  `Hey there buddy!`; the businesspeople's existing line remains unchanged.
- Focused tests cover topology, large-building bounds, reachability, exact
  entrance alignment, checkpoint/dialogue registration, scene composition,
  traffic direction, rain, sprites, props, and native rendering.
- All 91 suites pass in isolated processes; compilation is clean. The title
  loop and City Night 3 checkpoint launch headlessly, and the native arrival
  composition was visually inspected.

- Connected City Night 1's north sidewalk to a new 76x56 City Night 2 and
  provided a reciprocal southern return. Four office masses remain at real
  city-block scale; all unauthored edges end in the established Astral fall
  tiles rather than narrow fake buildings.
- Added the map's own Ashtray/shared-loader checkpoint, continuous rain, four
  cigarettes, and a second two-lane crossing. Extracted the office painter so
  later city maps use the same three-quarter-view building language.
- Added two stationary businesspeople and one short-patrol businessperson with
  exact `Ah! A rat!` dialogue. Added one raccoon: direct pursuit, 15 Sanity
  contact damage, three scratches to defeat, full scratch/contact rendering,
  and normal death reset.
- Focused tests cover the map topology and large-building invariant, safe
  route reachability, reciprocal transitions, checkpoint registration, exact
  dialogue, rain, pedestrian patrol, raccoon stats/pursuit/defeat/reset, and
  the existing City Night 1/Phase 10 handoff.
- All 90 suites pass in isolated processes; compilation is clean. The title
  loop and City Night 2 checkpoint both launch headlessly, and the native
  checkpoint render was visually inspected.

- Added a reusable four-direction traffic-lane controller with fixed car
  populations, deterministic spacing/phases, clean boundary wrapping, and no
  entity accumulation. Four procedural top-down modern-car variants make each
  vehicle enormous beside one-foot Chuck.
- Authored two fast opposed lanes across City Night 1's horizontal road and a
  worn zebra crossing aligned with the southern sidewalk approach. This is a
  readable two-lane teaching beat, not the later highway challenge.
- Vehicle impact costs 50 Sanity and returns Chuck to his last safe non-road
  footing, preventing embedding and out-of-bounds pushing. Lethal impact uses
  the ordinary Ashtray return and restores both lanes to their authored phase.
- Focused coverage validates deterministic wrapping, fixed populations,
  marker/road alignment, impact, checkpoint return, reset, generated art, and
  map/cutscene regressions.
- All 89 isolated test suites pass, compilation is clean, and the live
  checkpoint crossing was inspected at native resolution with rain and moving
  traffic active.

- Rebuilt City Night 1 as a 72x54 road-and-sidewalk grid flanked by four
  genuinely large inaccessible office blocks. Every connected office mass is
  at least 21x18 tiles; the unequal setbacks form explorable sidewalk pockets
  without cutting buildings into narrow leftover strips.
- Added reusable three-quarter-view city architecture: broad rooftop planes,
  cornices, eight-tile-deep windowed facades, darker side columns, and quiet
  three-frame rain/window glints. The Phase 11 contract now makes these scale
  constraints authoritative for all later night and day city maps.
- Kept the map/checkpoint IDs, rain, cigarettes, Astral non-exits, and Phase 10
  handoff intact. The physical City Night 1 Ashtray position follows its new
  authored marker.
- All 88 test files pass in isolated processes, compilation is clean, and the
  regenerated full-map and playable checkpoint views were inspected at native
  resolution.

- Corrected one Phase 10 presentation regression found during playtest: the
  Zephyros-room cloud now renders only within the blue window opening, behind
  the intact dark reveal, instead of crossing the frame into the interior.
- Added a focused pixel-layer regression. All eight Zephyros introduction
  tests pass, compilation is clean, and the corrected frame was visually
  inspected at native resolution.

- Began Phase 11 by expanding the former 24x16 contained city endpoint into
  the 56x36 `City Night 1` map. The existing `modern_city_arrival`,
  `modern_city_1`, and `modern_city_anchor` IDs remain intact for save and
  cutscene compatibility; only their player-facing display names and authored
  Ashtray position changed.
- Established the rainy-city map language with a broad wet cross street, four
  human-scale building masses, readable window bands, two optional sidewalk
  pockets, four loose cigarettes, continuous rain, and exact shared animated
  Astral fall tiles visibly severing every not-yet-authored route.
- Added a deterministic map generator, extended the city tileset with the
  established Astral terrain, and added Phase 11 topology/checkpoint/art
  coverage. The Phase 10 arrival, save, Continue, death-return, and music
  handoff remain unchanged.
- All 88 test files pass in isolated processes, compilation is clean, and
  both the title and City Night 1 frames launch and draw headlessly.
- This slice intentionally adds no traffic, people, raccoons, or City Night 2.
  The dedicated night-city soundtrack also remains pending its audio pass.

- Added the complete Phase 11 contract without beginning implementation. It
  preserves the existing `modern_city_arrival` / `City 1` handoff and scopes
  sixteen maps: six rainy night streets, four modern sewer maps, and six rainy
  daytime streets.
- Formalized the supplied NPC dialogue, raccoon/rat/crocodile roles,
  Frogger-like traffic and highway, toxic sludge, harder sewer Astral jumps,
  Animal Control net capture, stationary and spinning police projectiles,
  final Chult/Astral collision tableau, cigarettes, regional music, one
  Ashtray per map, and the Douglas fir transition boundary.
- No game code, maps, art, audio, or runtime state changed in this
  documentation-only pass.
- Added six new freestanding mushrooms to every Feywild map from Giant Tea
  Table through Twilight Crossroads, plus six to the Cloud Staircase approach.
  Maps 1--4 already retain 3--4 each, so the density now increases from Map 5
  onward as requested.
- Centralized the new authored coordinates in one dressing module used by all
  available procedural map generators and by the map-update tool. Placements
  use broad ground pockets or already-solid hedge cells and do not occupy jump
  landings, flower mutations, entrances, checkpoints, or enemy markers.
- Added focused coordinate/generator coverage. All 87 standalone suites pass,
  including every affected Map 5--13 suite and the Phase 10 Cloud Staircase
  suite.
- Corrected the previous Tea Table cleanup after visual review: restored all
  four structural table legs beneath the tabletop and removed only the three
  unexplained freestanding chair-leg props in the eastern aisle. The three
  western chair legs and all traversal geometry remain unchanged.
- Added exact-coordinate coverage for both structural and freestanding legs.
  All 86 standalone suites pass; compilation and the headless title-frame
  launch check are clean.
- Added grounded landing validation to the shared committed jump. Its existing
  airborne collision exemptions still clear authored one-tile channels, but a
  hop that expires while overlapping solid terrain now restores Chuck to the
  last safe point reached during that hop.
- Verified that valid Feywild landings on both stepping stones and raised lily
  pads remain unchanged, while incomplete hops can no longer strand Chuck on
  channel water and let him walk through it.
- Added focused jump regressions; all 86 standalone suites pass. Compilation
  and the headless title-frame launch check are clean.
- The earlier pass misidentified the four under-table supports as the stray
  props. This is superseded by the correction above.
- Audited all reciprocal Feywild transitions through the shared registry and
  moved all 26 destination arrivals to the center tile immediately inside the
  corresponding visible opening. This also fixes the Pollen Orchard's
  off-center southern arrival. Updated every available procedural map source
  alongside its generated map.
- Added one region-wide invariant test that derives the reverse visual opening
  for every Feywild transition and requires the named arrival to be centered
  exactly one safe tile inward.
- All 86 standalone suites pass; compilation and the headless title-frame
  launch check are clean.
- Composed and rendered the final Phase 10 cue: an original 48-second D-minor
  launch/city one-shot at 120 BPM. Its opening quotes the established falling
  motif, then accumulates Astral pulse, wind, rain-like hats, urban metal, and
  subtle low synth before resolving into bells and tired flute after impact.
- Replaced the reused Chult cue at the existing 3.5-second launch boundary.
  Playback continues across the launch-to-city scene replacement without a
  restart; action breaks at sidewalk impact and the remaining wet-city texture
  fades for 750 ms with the final visual fade into the playable checkpoint.
- Added focused motif-continuity, layer-timing, impact-break, render, loudness,
  one-shot dispatch, scene-continuity, and final-fade regression coverage.
  All three Phase 10 musical identities and transition acceptance items are
  now complete; no Phase 11 gameplay was added.
- Composed and rendered the second Phase 10 cue: a 111-second warm Zephyros
  conversation theme in G major with a restrained Mixolydian turn at 78 BPM.
  Warm reed, soft mallets, round bass, plucks, cloud pads, sparse bells,
  reverse swells, and wooden ticks keep it gentle, wise, and lightly whimsical.
- Integrated the cue at the conversation boundary. The uninterrupted tower
  theme fades for 900 ms while Zephyros' hand settles, then the new loop begins
  with the first player-advanced dialogue panel. A two-step dispatch preserves
  the fade even if a single unusually long frame crosses both cue points.
- Added focused composition, motif-return, arrangement, render, loop-seam,
  loudness, and cutscene-transition regression checks. The launch/modern-city
  transition cue remains the next bounded Phase 10 task.
- Composed and rendered the first Phase 10 cue: a 105-second C-Lydian Cloud
  Staircase/Tower theme at 82 BPM. A recurring flute melody, glassy mallets,
  open-fifth bass, high bells, reverse swells, and a new slow cloud-pad voice
  create peaceful ancient wonder with strong melodic identity.
- Integrated `zephyros_tower.wav` across the Cloud Staircase, exterior, and
  Aerie. Their identical music request uses the existing no-restart behavior,
  so the cue flows continuously across normal map changes and the ascent.
- Added composition, rendered-file, mode, motif-return, arrangement-density,
  loop-seam, and perceptual-level regression gates. The mix is intentionally
  spacious but level-matched to the preceding Feywild theme.
- Reversed the Zephyros introduction staging: Chuck stays at the rope landing
  while the giant hand travels from offscreen to collect him. Extended the
  purple robe through the frame bottom so Zephyros reads as a body rather than
  a floating bust.
- Consolidated the unchanged speech into 19 modest panels and replaced the
  automatic timer with the standard interact-to-complete/interact-to-advance
  dialogue rhythm. The final completed panel alone dispatches the launch.
- Delayed the launch motif from 0.9 to 3.5 seconds and removed the unexplained
  black perspective-road rectangle from the rainy city canyon.
- Rescaled the playable exterior platform into a compact roughly 20x20-tile
  stone island and enlarged the embedded tower/arch facade from 192x128 to
  320x224 pixels. The facade now exceeds the native viewport and the doorway
  visibly dwarfs Chuck, while the Ashtray and reversible Aerie transition keep
  their established behavior.
- Continued the city-fragment collision directly into an input-free rainy-city
  descent. Chuck crosses a modern street canyon diagonally, loses horizontal
  momentum, and falls the remaining distance to the sidewalk.
- Reused the established impact, zero-Sanity vanish, Astral reformation,
  look-around, cigarette insertion, and drag language. The camera remains fixed
  throughout and control returns only after the final fade.
- Added a contained 24x16 playable endpoint with procedural modern-city art,
  persistent screen-space rain, exactly one physical Ashtray, and no exits,
  NPCs, enemies, interiors, or Phase 11 content.
- Added `City 1` to the development selector and the saveable
  `modern_city_anchor`. The cutscene activates and persists that real Ashtray,
  then enters it through the shared checkpoint loader; Continue restores the
  same map, world flag, full Sanity, and lit anchor.
- Added focused coverage for trajectory, cues, death/return phases, cigarette
  tableau, save/Continue restoration, dev loading, map containment, and rain.
- All 85 standalone test suites pass; compilation and the headless title-frame
  launch check are clean.
- Continued directly from Zephyros' final line into a dedicated input-free
  launch scene. A whole-tower side view makes Chuck a two-pixel dot while one
  small palm motion throws him effortlessly across the sky.
- Added a close horizontal-flight composition: Chuck enters west-to-east at a
  stable altitude, then gradually descends. Exact animated Astral hazard cells
  arrive first; office windows and jagged concrete fragments progressively
  join them in the same moving sky.
- Reused the established falling motif after a short music fade and ended on a
  clear collision with a large city fragment. The collision holds as the
  stable boundary for the rainy-city descent; no Phase 11 gameplay was added.
- Added focused coverage for truthful throw scale, trajectory, Astral-art
  reuse, city-fragment accumulation, one-shot music dispatch, input-free
  behavior, Sanity continuity, and the held collision. All 84 suites pass.
- Connected rope `YES` to a dedicated cinematic while preserving
  silent `NO` and Sanity. Chuck descends the giant rope, an impossibly large
  Zephyros enters, blinks and smiles, raises his palm, and receives Chuck.
- Added a warm blue-grey procedural portrait at native scale: raised brows,
  readable eyes and smile, gold earrings, purple-and-gold clothing, long white
  beard, and a separate giant hand. Chuck remains tiny and readable throughout.
- Added the complete supplied dialogue as data using the established dialogue
  panel. The current polished version groups it into 19 manually advanced
  panels, and the final line hands directly into the tower-launch scene.
- Added focused coverage for exact text, validated choice dispatch, Sanity
  preservation, distinct visual beats, manual line progression, and the launch
  handoff. All 83 suites passed that original slice.
- Connected the exterior's embedded arch to a 60x46 open-sided Aerie and added
  a reversible three-tile southern return. The platform now has a clearly
  rounded elliptical tower silhouette. Four seven-tile-wide nests surround a
  near-black interior shaft; its giant rope is visibly lashed to an iron cleat
  on the south stone lip instead of floating over the opening.
- Added one griffon emerging from the northwest nest. It uses the existing
  `MassiveDinosaur` behavior/configuration under regional art, begins outside
  notice range, is easy to outrun, resets normally, and does not gate travel.
- Added one physical `Zephyros 3 Ashtray`, the shared `Zephyros 3` development
  entry, and the exact walk-triggered `Climb down the rope?` prompt. `YES`
  starts the complete introduction scene and `NO` closes silently.
- Added procedural Aerie map, nest, rope, and griffon generation plus focused
  coverage for layout, connectivity, scale, choice, behavior, transitions,
  checkpoint saving, and direct development loading.
- Reworked the tower arrival into two truthful scales and extended it from
  roughly nine to 19.5 seconds. Close framing shows Chuck climbing against
  nothing but enormous masonry; a cloud-white scale cut then shows the whole
  tower and cloud stair without drawing an impossibly visible Chuck. The wide
  shot holds through a 6.5-second step-by-step upward retraction, then uses the
  existing fade/checkpoint handoff unchanged.
- Moved the Cloud Staircase choice marker directly below the stair prop and
  reduced its walk-trigger from five-by-three tiles to two-by-one. The player
  now sees the staircase at close range before the YES/NO prompt takes over;
  choice text, silent `NO`, cutscene dispatch, and route geometry are unchanged.
- Reworked the exterior arch into a broad curved section of Zephyros' pale
  tower wall. Its masonry continues north beyond the frame and fully surrounds
  the centered black threshold, so the boundary reads as the Aerie entrance
  rather than a freestanding doorway to open sky. Map geometry, checkpoint,
  and the connected Aerie boundary are unchanged.
- Added the peaceful Cloud Staircase map, exact approach-triggered YES/NO
  prompt, input-free side-view climbing/retraction cutscene, and playable
  circular tower exterior.
- All three Phase 10 gameplay maps have one physical Ashtray. `Zephyros 1`,
  `Zephyros 2`, and `Zephyros 3` are development-visible entries in the shared
  checkpoint loader.
- Choice JSON now supports a small validated `action` target. WorldScene owns
  the explicit scene dispatch; the choice menu contains no transition logic.
- Added procedural generators for the maps, airy tower tileset, immense cloud
  stair, giant arch, nests, rope, and griffon.
- Next: await the authoritative Phase 11 document before beginning modern-city
  gameplay. Preserve the completed three-cue Phase 10 soundtrack and contained
  city-arrival endpoint.

## Previous Pass (commit 23b76ed)

Feywild thorn mites gained the ship-hold rats' pursuit behavior while
preserving their existing scale, damage, scratch defeat, and reset lifecycle.

## Previous Pass (commit fd81259)

Completed Phase 9 with the 76x52 Twilight Crossroads, its flower route,
pollen route, Chuck-only root shortcut, restrained enemies, shared checkpoint,
Rapids travel, and inert pre-tower boundary. All 80 suites passed.

## Previous Pass (commit d728b28)

Added the Luminous Rapids traversal synthesis, reactive lily-pad groups,
stepping-stone jumps, pollen approaches, moth lanes, one optional orchid, its
shared checkpoint, and Mushroom Underways travel.

## Previous Pass (commit 4bc7e36)

Moved every implemented Feywild handoff from a single interior opening to a
contiguous three-cell trail mouth on the real outer map edge. All 70 suites
passed.

## Previous Pass (commit bcc1639)

Added the 68x46 Rootways, reusable Chuck-scale root passages, two redcaps, its
shared checkpoint/Ashtray, Pollen Orchard travel, procedural art, and focused
coverage. All 70 suites passed.

## Previous Pass (commit a6af3a9)

Made the original Feywild theme catchier and less harmonically strange by
moving to F Mixolydian, repeating its central call earlier, and restraining
reverse swells. All 69 suites passed.

## Previous Pass (commit a35781c)

Added the original 48-bar Feywild exploration theme, four reusable procedural
instruments, seamless regional integration, and composition/rendered-audio
quality regressions. All 69 suites passed.

## Previous Pass (commit 9284e56)

- Extended the existing deck state machine so the captain's arrival, crew
  announcement, accusation, plank order, objection, refusal, Chuck's walk,
  Jeffries' warning, outer-plank approach, kick, and Hell-fall handoff form one
  uninterrupted cinematic sequence.
- Chuck now walks automatically from the staged approach onto the first plank
  row. The existing reality field activates there and Jeffries delivers the
  unchanged `It's back! The purple is back!` line. When its dialogue overlay
  closes, Chuck automatically walks the remaining seven plank rows.
- Reaching the outer tile now invokes the existing captain approach/kick state
  directly. Reality-fragment timing, live-Hell-block targeting, fall motion,
  Sanity carry, dialogue, character placements, and the later Hell cutscene
  remain unchanged. Manual post-confrontation development/loading behavior is
  preserved for existing checkpoint states.
- Focused regressions run the whole path from captain arrival through every
  dialogue overlay and scripted walk into `HellFallingCutsceneScene`, asserting
  there is no idle WorldScene frame where player control resumes.
- All 67 standalone test suites pass, compilation is clean, and the headless
  title-loop launch smoke check passes.

## Next Logical Task

Run the complete Phase 9 human acceptance route from `Feywild 1` through
`Feywild 13`, then load each development checkpoint independently. Make only
narrow fixes evidenced by that playtest; do not begin the floating wizard
tower without its own phase document.

## Previous Pass (commit 474435d)

Clarified every implemented Feywild transition with vegetation-framed
wilderness openings and placed cigarette grass beside the first reactive
flower to teach scratching through natural overlap.

## Previous Pass (commit e10fe67)

Added Pollen Orchard, animated slowing pollen, the shared `Feywild 3`
checkpoint/Ashtray, an optional route-exchange flower, and complete focused
coverage. All 69 suites passed.

## Previous Pass (commit 4b0c5b2)

Added Blooming Path, its Ashtray and shared checkpoint, and the reusable
scratch-reactive flower system. All 68 suites passed.

## Previous Pass (commit 4e08336)

Authored Phase 9 as a thirteen-map Feywild region with reactive flowers,
slowing pollen, Chuck-sized passages, five enemy roles, pacing, checkpoints,
acceptance criteria, and a stable pre-wizard-tower endpoint.

## Previous Pass (commit 60e0394)

Made the Nine Hells impact reuse Chult's exact death/return timing, Astral blip
renderer, sounds, look, cigarette, fade, and handoff cadence. All 67 suites
passed.

## Previous Pass (commit 18b49c8)

Aligned the Rubble Pass east cleft and transition, animated its lava fall,
moved the wizard clear of the Pit Fiend, and removed the river-cutscene foam
artifact. All 67 suites passed.

## Previous Pass (commit de6519f)

Added the first playable Feywild riverbank, its procedural terrain/props,
map-local Ashtray, `Feywild 1` shared checkpoint, durable progression flag,
and final-black cutscene handoff. All 67 suites passed.

## Previous Pass (commit 6d16217)

Added the east-west Phlegethos rubble pass between the Lava Lake and Fortress,
with dark rubble, a lava fall and river, one lemure, one optional horned devil,
a map-local Ashtray, urns, and shared transitions. All 66 suites passed.

## Previous Pass (commit b09e109)

Extended the Feywild river cutscene to 35 seconds with a slow black reveal,
denser enchanted psychedelic banks, a longer visible river journey, and a
clear wash-prone-rise-stand shoreline sequence. All 65 suites passed.

## Previous Pass (commit 11adf87)

Made grounded or airborne river contact use Chuck's full fall animation before
the cutscene handoff, increased the early river fragments, replaced the forced
Astral choke with an unavoidable full-height late river surge, and preserved a
readable central route around the Astral corruption. All 65 suites passed.

## Previous Pass (commit dc4b250)

Added fourteen shared breakable temple urns and carton rewards across all four
Phlegethos maps. All 65 suites passed.

## Previous Pass (commit f898d04)

Enlarged the fortress Pit Fiend from 64x64 to 128x128 while preserving its
marker, feet anchor, choreography, and attacks. All 65 suites passed.

## Previous Pass (commit aab0e48)

Completed the input-free rushing-river cutscene from the fortress escape
through the waterfall and quiet Feywild-bank ending. All 65 suites passed.

## Previous Pass (commit fc0ae50)

Added the moving Feywild river fragments, final forced Astral choke, airborne
escape rule, death reset, and stable black cutscene boundary. All 64 suites
passed.

## Previous Pass (session 179, commit 4dfda43)

Removed the remaining rectangular head silhouette visible when ship pirates
turned upward:

- The earlier correction shaped the warm back-of-head area, but the deck
  generator still drew the rear tricorn as a full-width 13x4 near-black slab.
  Replaced it with a narrow brim, peaked crown, and broken silhouette across
  both performance and captain-walk frames.
- Audited the separate seated-pirate generator and applied the same rear-view
  rule, also replacing its dark hair block with a warm shaped head/scarf area.
- Regenerated all five deck/captain sheets plus the seated pirate sheet.
- Added pixel regressions for both ordinary up-facing performance frames and
  the captain's scripted up-walk frames, plus the seated pirate's two up
  frames. A 4x native montage was inspected; focused deck-cast and crew-quarter
  suites pass. All 63 standalone suites pass, compilation is clean, and the
  title-loop launch smoke check passes.

## Previous Pass (session 178, commit 8813701)

Improved the crew and captain sleeping spaces without changing map dimensions,
routes, checkpoints, or gameplay progression:

- Enlarged the procedurally generated hammock art from 20x34 to 30x44 native
  pixels. All eight crew-quarter bunks now read at human scale while retaining
  their single authored anchor and scurry-under overhang language.
- Added a 72x44 brass-trimmed double bed to the captain's cabin with a broad
  two-row solid footprint, keeping Chuck from walking through the mattress.
- Added an 80x48 woven central rug beneath the cabin's existing furniture.
  Formalized a small reusable floor-prop flag so rugs render immediately above
  terrain and below pickups, Chuck, NPCs, and standing props.
- Added focused coverage for furniture counts, native sprite sizes, bed
  collision authorship, and rug draw-layer behavior. Native 4x room and
  furniture renders were inspected. All 63 standalone suites pass,
  compilation is clean, and the title-loop launch smoke check passes.

## Previous Pass (session 177, commit 896b08d)

Fixed the ladder-to-exterior-deck crash introduced by the development-only
`Captain Arrival` checkpoint:

- The development checkpoint had accidentally been marked as a normal runtime
  map-entry definition, giving `ship_exterior_deck/from_crew_quarters` two
  competing checkpoint IDs and making the shared loader reject ladder travel.
- `Captain Arrival` remains development-visible and still uses the shared
  loader with the real captain prerequisites, but is no longer considered for
  ordinary named-arrival resolution.
- Added regression coverage proving the crew ladder resolves uniquely to
  `ship_exterior_deck`, while direct development loading still starts the real
  captain arrival sequence.
- Focused exterior-deck and captain-confrontation suites pass. All 63
  standalone suites pass, compilation is clean, and the title-loop launch
  smoke check passes.

## Previous Pass (session 176, commit 5f9ba7c)

Polished the completed Phase 7 ship and ending in the five requested areas:

- Added a development-visible `Captain Arrival` definition to the shared
  checkpoint registry. It loads the exterior deck with the real seven captain
  prerequisites and no confronted flag, so the ordinary production gate,
  spawn, camera, walk, announcement, and dialogue all run unchanged.
- Kept the galley, crew quarters, and captain cabin at their exact 40/42/36
  tile east-west widths while compressing their north-south spans to 22/24/21
  tiles. Every prop, actor, doorway, ladder, arrival, Ashtray, and reversible
  transition remains; the three anchor respawn positions follow their moved
  markers.
- Found the remaining NPC black block in the procedural deck-pirate up frame:
  one solid 7x5 near-black patch covered the head. Replaced it with shaped warm
  head shadow, scarf, and narrow hair/edge pixels, then regenerated all five
  deck/captain sheets from source.
- Removed all overhead Hell fragments from the street-view fall. Chuck now
  descends through heated open air and sparks with one large distant volcano
  behind him.
- Rebuilt the arrival ground as over 90% basalt with only a thin branching
  molten fissure, then reused the Chult tableau's left/right/down look,
  cigarette insertion, lit ember, drag, and rising smoke before the input-free
  Phase 8 hold.
- Targeted galley, crew, cabin, captain gate, checkpoint selector, deck-pirate
  pixel, and plank/fall suites pass. All 63 standalone suites pass, compilation
  is clean, and the title-loop launch smoke check passes. Native renders of all
  three compressed rooms, every regenerated up-facing pirate, and
  fall/impact/smoke frames were inspected.

## Previous Pass (session 175, commit ebdb3d8)

Completed the bounded Phase 7 ending without beginning playable Phase 8:

- Reaching the outermost staged plank tile now locks control and routes the
  captain horizontally to the plank centerline, then straight down behind
  Chuck using his existing scripted walk cycle.
- The captain waits in place until a currently rendered Hell fragment crosses
  beneath Chuck. A native-pixel boot extension, `hurt` impact, and restrained
  camera shake launch Chuck down and into that exact still-moving fragment;
  the established shrinking fall animation carries the contact.
- Added a dedicated input-free Nine Hells descent scene. It reuses the
  fall-to-Chult music and its four-second cue / 29-second impact structure,
  while overhead volcanic fragments, rising sparks, a warming void, and an
  approaching basalt/lava plane replace the Chult clouds and canopy.
- Chuck lands at the stable Phase 8 boundary and the tableau holds without
  player control. Sanity and the global cigarette run remain available to a
  future Phase 8 handoff, but no map, checkpoint, mechanic, or narrative
  content was invented without Phase 8 documentation.
- Targeted regressions cover the outer-tile gate, captain approach, live Hell
  target selection, kick/fall frames, scene handoff, reused music timing,
  impact, preserved Sanity, input-free arrival hold, and rendering. The
  eleven-test plank suite plus captain, deck-cast, and original Chult-fall
  regressions pass; all 63 standalone suites pass, compilation is clean, and
  the title-loop launch smoke check passes. Native 4x renders of both the kick
  and fall/arrival frames were inspected.

## Previous Pass (session 174, commit 13d5ecd)

Removed the repeated grid from adjacent overhead Hell fragments without
changing their established appearance or movement:

- Replaced the shared fixed 12x12 basalt lattice with deterministic
  per-fragment bands whose heights, horizontal origins, slab widths, vertical
  insets, gap widths, and missing lava-pool plates vary by seed.
- Neighboring Hell chunks now place their lava channels and exposed pools at
  different coordinates instead of visually continuing one uniform grid.
- Terrain remains stable between animation frames; only the existing lava
  highlights drift, avoiding procedural shimmer.
- Astral art, Hell palette/material identity, stream lanes, westward motion,
  recycling, layering, collision, and plank behavior are unchanged.
- Added a focused regression that renders separate seeds and requires
  substantially distinct lava masks. The focused nine-test plank suite and all
  63 standalone suites pass, compilation is clean, the title-loop launch smoke
  check passes, and a side-by-side 4x nearest-neighbor native preview was
  inspected.

## Previous Pass (session 173, commit 0557fcc)

Reworked only the moving Hell-fragment art to read as terrain viewed from
above, preserving the established plank stream and its unfinished fall boundary:

- Replaced the old flat brown field, diagonal stripes, central seam, and
  top-edge flame row, which implied a side-facing block.
- Hell fragments now expose an animated orange-red lava ground plane beneath
  irregular clipped basalt shelves. Branching molten gaps, angular rock
  fissures, larger exposed pools, and pinprick hot vents keep the small chunks
  legible at native 320x180 scale.
- Astral art, east-to-west screen crossing, stagger timing, recycling,
  ship/plank layering, activation, collision, Jeffries' warning, and bounded
  plank endpoint are unchanged.
- Added a focused visual-material regression requiring a basalt-majority
  overhead surface, substantial lava exposure, bright heat points, and mixed
  terrain at the upper edge instead of the former flame strip. The focused
  plank suite and all 63 standalone suites pass, compilation is clean, the
  title-loop launch smoke check passes, and a 4x nearest-neighbor native render
  was inspected.

## Previous Pass (session 172, commit bf5f141)

Reworked the plank reality breakup to match established Astral art and the
ship's direction of travel without beginning the kick/fall:

- Removed the old plank-centered sine drift and custom Astral approximation.
- Astral fragments now load and tile the exact six animated `astral_void`
  cells used by the sewer, pantry, Chult, and temple fall hazards.
- Astral and ember-cracked Hell blocks occupy staggered screen-space sea lanes.
  Each begins entering at the native screen's east edge, moves directly west
  until fully off-screen, then recycles as a replacement at the east edge.
- The streams remain fixed to the sea frame and draw below the rocking
  hull/plank, so the ship appears to travel through them without changing
  physics, collision, Jeffries' warning, or the bounded plank endpoint.
- Focused tests verify exact Astral cell reuse, pure westward movement, full
  screen crossing, east-edge recycling, both materials, and all existing plank
  gates. All 63 standalone suites pass, compilation is clean, the title-loop
  launch smoke check passes, and a native 320×180 plank render was inspected.

## Previous Pass (session 171, commit 057b189)

Corrected the apparent black boxes over animated deck NPC faces when dialogue
made them turn left or right:

- Confirmed the sprite surfaces retain alpha; the fault was visual rather than
  a transparency or runtime-flip bug. The old side-view tricorn used one
  full-width 13×4 dark rectangle that read as covering the face at 4× scale.
- Reworked the shared procedural side-view hat into a stepped crown and narrow,
  rear-weighted brim while preserving the established front/back silhouettes.
- Regenerated all four animated deck performers and the captain from the same
  source, so both left- and mirrored right-facing dialogue poses keep the eye,
  nose, cheek, and red hat band readable.
- Added a focused native-pixel regression that caps the dark side-hat mass and
  requires visible face pixels in every side-facing performer frame.
- Focused deck-cast and captain-confrontation tests pass; all 63 standalone
  suites pass, compilation is clean, the title-loop launch smoke check passes,
  and a native 320×180 render was visually inspected from the reported angle.

## Previous Pass (session 170, commit 4203c0a)

Reworked the beginning and timing of the existing captain confrontation
without changing its prerequisite gate, outcome, or plank handoff:

- The captain now emerges at the authored midship ladder instead of appearing
  instantly at the helm. Player control locks and the camera follows him north
  of the deck Ashtray, west across the clear lower deck, and into his authored
  stern-helm position.
- Expanded only the captain sprite sheet with a dedicated four-frame,
  directional walk cycle. His established pointing performance resumes once
  the walk ends.
- The nearby concertina crewman turns toward the arriving captain and delivers
  the exact new line `Captain on deck!`.
- Added one `...` beat after the announcement and one before the captain's
  final `No.` so the entrance and objection have deliberate cinematic pauses.
- The captain gate remains unset until both dialogue sequences close. Saved
  `captain_confronted` state still reconstructs the completed plank tableau
  without replaying the entrance.
- Focused captain, deck-cast, and plank regressions pass. All 63 standalone
  test scripts pass, compilation is clean, and the launch smoke check passes.

## Previous Pass (session 169, commit 502c7aa)

Gave only the lower-hold rats the temple snakes' readable attack-chase
behavior without changing the sewer tutorial encounters:

- Added a reusable opt-in rat chase mode with the snakes' 96-pixel notice
  radius and 32 px/s pursuit speed.
- Pursuit uses the shared swept tile collision and treats fall hazards as
  solid, so rats chase through valid cargo lanes without crossing walls or
  unsupported hazards.
- All sixteen lower-hold rat markers enable the chase mode when the room is
  built or reset. Their existing contact Sanity damage and one-scratch defeat
  behavior are unchanged.
- Sewer and other ordinary rats retain their established short horizontal
  patrol configuration.
- Focused combat, lower-hold reset, sewer reset, and temple-snake regression
  checks pass. All 63 standalone test scripts pass, compilation is clean, and
  the game reaches and cleanly exits its running title loop.

## Previous Pass (session 168, commit 2d3f934)

Implemented the reality-breakup reveal around the staged plank without
beginning the captain's kick, fall, or Phase 8:

- Added a modular deterministic reality-block field anchored to the authored
  plank origin. Four Astral and four Hell fragments phase in sequentially and
  drift in broad ocean lanes on both sides without crossing the plank.
- Astral chunks use hard-edged purple/blue starfield pixels; Hell chunks use
  foreign basalt, orange magma seams, embers, and square flickering flames.
  They render with the fixed sea rather than inheriting the ship's rocking
  offset.
- First stepping onto the staged plank activates the field and triggers
  Jeffries' exact one-time shout: `It's back! The purple is back!`
- The fragments are presentation-only in this slice. They do not collide,
  damage, or pull Chuck off the plank, and the existing solid ocean endpoint
  remains intact.
- Focused tests cover delayed reveal, both materials, motion, plank separation,
  activation gating, exact dialogue, one-time behavior, and the deliberate
  absence of any fall/transition. A native 320x180 render was visually checked.
- All 63 standalone test scripts pass, compilation is clean, and the game
  reaches its running title loop in the headless launch smoke check.

## Previous Pass (session 167, commit 0210eaa)

Rebuilt the actual ladder geometry and art at human crew scale without
changing any route or confirmation behavior:

- Replaced the old complete 16x16 ladder icon (doubled side by side in two
  rooms) with aligned top/bottom terrain pieces that form one continuous
  16x32 ladder, matching the established 16x30 human NPC frame.
- Updated the arrival compartment, lower hold, crew quarters, and exterior
  deck so each contains exactly one two-cell ladder. Nearby arrivals remain on
  safe floor rather than inside the enlarged footprint.
- Both halves are walkable and carry the same direction-correct YES/NO
  confirmation, destination, named arrival, and facing.
- Regenerated the procedural ship tileset and added regression coverage for
  the human-height pairing and shared top/bottom transition records.
- All 63 standalone test scripts pass, compilation is clean, and the game
  reaches its running title loop in the headless launch smoke check.

## Previous Pass (session 166, commit 02b84f4)

Added rubble-style YES/NO approach confirmation to every live ship ladder
without creating a parallel route system:

- Extended the existing `AreaExit` records with an optional confirmation
  prompt. Only the four ship ladder directions opt in.
- Arrival compartment to lower hold and exterior deck to crew quarters ask
  `Climb down ladder?`; lower hold to arrival compartment and crew quarters
  to exterior deck ask `Climb up ladder?`.
- YES reuses the same destination, named arrival, and facing already authored
  for the ladder. NO closes silently, does not traverse, and does not reopen
  while Chuck remains on the tile; leaving and approaching again rearms it.
- Focused checks cover both prompt texts, NO/rearm behavior, YES traversal,
  named arrivals, facing, and the exterior ladder pair.
- All 63 standalone test scripts pass, and the game reaches its running title
  loop in the headless launch smoke check.

## Previous Pass (session 165, commit 0b48103)

Corrected the arrival compartment and captain chest without changing the
completed ship routes or confrontation architecture:

- Restored the arrival compartment's unused south-wall doorway recess to
  ordinary solid hull. The live west/east passages and lower-hold floor ladder
  remain unchanged.
- Interacting with or scratching the captain's chest now starts the same
  four-frame lid-opening animation. It opens directly in the world and never
  pushes the old Buhetian Halfling Leaf or empty dialogue.
- When the lid finishes, the chest drops a dedicated golden carton on the
  floor in front. Physical collection grants exactly 40 cigarettes and banks
  the one-time reward against death.
- Separate durable opened and collected flags let CONTINUE reconstruct an
  opened-but-uncollected carton while preventing duplication after collection.
  The existing captain-confrontation gate still requires only opening the
  chest.
- All 63 standalone test scripts pass, including focused interaction, scratch,
  animation timing, one-time reward, save/Continue, arrival collision, and
  confrontation regressions.

## Previous Pass (session 164, commit 04a68e4)

Implemented the physical plank and ordered approach without beginning the
reality breakup or fall:

- Authored one hidden plank origin in the south/starboard rail. Once the
  confrontation completes, it replaces that rail cell and seven ocean cells
  with a dedicated narrow, walkable plank terrain rendered transparently over
  the existing animated sea.
- Solid ocean tiles remain on both sides and beyond the endpoint, so Chuck can
  walk the full plank but cannot step off it or trigger an unfinished fall.
- The captain and objecting cheering pirate move to opposite sides of the
  approach. Chuck cuts to a clear four-tile lane and takes a short input-locked
  walk to the rail using his normal shuffle animation and wooden footsteps;
  control returns one tile before the plank.
- `captain_confronted` derives the complete staged tableau on map load and
  CONTINUE without replaying the procession or adding another save flag.
- Focused tests cover hidden/staged terrain, collision containment, tableau
  positions, procession completion, and control return. A native render
  verified the opened rail and plank over the sea.
- Astral/Hell blocks, Jeffries' warning, the kick, fall, and Phase 8 transition
  remain untouched.

## Previous Pass (session 163, commit 72138e5)

Implemented the captain's gated arrival and accusation without beginning the
physical plank sequence or reality breakup:

- Added one modular seven-flag gate requiring the galley chef encounter,
  seated pirate, all four deck conversations, and opened captain's chest.
  The previously runtime-only chef notice now sets a durable save flag.
- A hidden authored captain marker beside the stern helm materializes only
  when the gate is ready. The camera cuts to him and the dialogue delivers the
  theft accusation, plank order, exact authored crew objection, and the
  captain's clipped refusal.
- Added a twelve-cell captain sheet with four shanty-timed pointing frames per
  facing. After the exchange he remains as a normal first/repeat-aware deck
  pirate and the camera returns to Chuck.
- `captain_confronted` persists through the deck Ashtray and CONTINUE. A
  restored captain never replays the automatic sequence.
- Focused tests cover every prerequisite, hidden/spawned states, authored
  dialogue, animation, chef tracking, and save restoration. A native render
  verified the captain's placement beside the helm.

## Previous Pass (session 162, commit 729aeca)

Corrected the exterior helm's position and perspective without changing routes
or progression:

- Moved the helm two rows north so its anchor now shares the exact row-22
  stern-to-bow centerline with both mast bases, remaining four tiles sternward
  of the western/main mast.
- Rebuilt its wheel from a flush circular face into a narrow, layered
  transverse rim with offset depth, compressed spokes, handles, angled
  pedestal, and brass hub. It now reads from the authored three-quarter
  viewpoint off the starboard side.
- The focused exterior-deck test locks the shared centerline. The helm remains
  a 56x54 human-scale solid prop and shares the ship's visual rocking.

## Previous Pass (session 161, commit ba4a404)

Polished two requested exterior-deck composition details without changing its
routes or progression:

- Jeffries keeps his safe marker and dialogue approach tile directly below the
  western/main mast, but his rendered 30-pixel struggling figure is lifted 24
  pixels. His complete body now visibly overlaps the exposed pole instead of
  appearing to stand at its base.
- Added one 56x54 procedural ship's helm on a solid plank anchor four tiles
  west (sternward) and two tiles south of the main mast. Its large timber rim,
  eight handles, brass hub, and pedestal remain readable at native 320x180
  scale and reinforce Chuck's one-foot scale.
- Focused exterior/deck-cast tests lock the helm position and size plus
  Jeffries' visual lift. A native headless render verified their composition.

## Previous Pass (session 160, commit cf0e49a)

Completed the exterior deck's lively cast without beginning the ending:

- Added exactly two `SwordFighter` hazards in the central deck lanes. They bind
  to one shared midpoint, wander it in a slow broad loop, and lunge/retreat
  across it while always facing one another.
- Each fighter has twelve procedural 24x30 cells. Their guard, lunge, high
  parry, and low recovery run on opposing half-beats at the shanty's 126 BPM;
  one wears blue and one red so the exchange remains readable.
- Movement uses ordinary swept tile collision, so the pair cannot pass through
  masts or rails. Routes above and below remain open, making this an avoidable
  hazard rather than a combat gate. They are intentionally not scratch targets.
- Contact costs 15 Sanity and restores Chuck's previous position. The ordinary
  enemy-reset lifecycle rebuilds and rebinds both fighters after death.
- A focused test suite covers exact map composition, open bypass lanes, paired
  movement, beat timing, collision-safe positions, contact damage, and reset.

## Previous Pass (session 159, commit f3cb6c6)

Populated the exterior deck without beginning its combat or ending sequence:

- Added four `DeckPirateNPC` performers: concertina player, cheering tankard
  pirate, dancing pirate, and Jeffries struggling directly beneath the western
  mast. Each has twelve procedural cells: four down/up/side action frames plus
  mirrored right-facing frames at runtime.
- Their distinct bellows, tankard, jig, and rope-strain loops all advance twice
  per beat against the established 126-BPM shanty. Small phase offsets keep the
  whole deck rhythmic without making every gesture mechanically simultaneous.
- Added first/repeat dialogue and durable progress flags for all four. Jeffries
  uses the documented collided-world warnings; the cheering pirate uses the
  documented dismissal. Saving at the existing deck Ashtray and CONTINUE
  preserve every conversation state.
- Added a data-driven `deck_pirate:` map marker/spawn path and a dedicated test
  suite covering cast composition, Jeffries' mast placement, exact key lines,
  four-frame beat timing, first/repeat switching, and save restoration.
- Sword-fighting pirates, their Sanity hazard, the captain, and the plank
  sequence remain untouched for later bounded sessions.

## Previous Pass (session 158, commit 9be609a)

Corrected the bowsprit scale and attachment point after visual playtesting:

- Rebuilt `ship_bowsprit` from a 120x32 canvas with roughly four tiles of thin
  visible spar into a 400x96 canvas with over twelve tiles of broad, tapered
  timber projection and a substantially reinforced heel.
- Moved its anchor from the final interior deck tile to the eastern perimeter
  rail itself. The rail remains its solid under-tile, so the spar now begins at
  the literal bow edge before extending over animated open water.
- The bowsprit remains a presentation-only y-sorted prop sharing ship rocking;
  no route, checkpoint, collision boundary, or mast placement changed.
- Focused tests lock its bow-edge coordinate and new dimensions.

## Previous Pass (session 157, commit 87e8c9f)

Completed another tightly scoped exterior silhouette pass:

- Enlarged each centerline mast/sail from 176x160 to 224x192. The two bases
  retain their exact row-22 east-west alignment, while each complete broad sail
  now spans approximately the narrowed hull's full north-south beam.
- Added one dedicated 120x32 `ship_bowsprit` prop at the eastern bow. Its heel
  is planted on the final deck tile inside the rail and most of the tapered,
  highlighted timber spar projects east over animated open water.
- The bowsprit uses the same y-sorted procedural prop architecture and shares
  the deck's presentation-only rocking offset. It changes no route, transition,
  checkpoint, or hazard behavior.
- Focused tests lock both larger sail dimensions and the sole bowsprit's
  authored bow position and dimensions.

## Previous Pass (session 156, commit 82e92be)

Refined the exterior silhouette after a second visual playtest:

- Reduced the hull's north-south beam from 30 tile rows to 22 while preserving
  its full east-west length. The surrounding ocean now reads more strongly and
  the deck no longer feels excessively broad.
- Moved the existing hatch, named arrival, and sole Ashtray two rows inward so
  the narrower rail never crowds the save/transition space; the Ashtray's
  shared checkpoint position moved with its authored marker.
- Enlarged both centerline mast-and-sail sprites from 144x136 to 176x160. Their
  east-west alignment and anchor columns are unchanged.
- Focused tests lock the new beam bounds, mast positions and sprite size.

## Previous Pass (session 155, commit 28cc329)

Corrected the exterior deck's mast composition after visual playtesting:

- Both mast anchors now share the deck's exact center row, spaced east-to-west
  at columns 21 and 42. The previous diagonal placement is gone.
- Rebuilt the procedural mast/sail from 58x90 to 144x136: the broad complete
  sail is nearly half the native screen wide, the mast remains visibly planted
  in the boards, and the silhouette now reads at human-ship scale beside Chuck.
- No deck route, checkpoint, collision rule, ocean animation, or rocking logic
  changed. Targeted exterior-deck tests now lock the alignment and asset size.

## Previous Pass (session 154, commit 2656bb9)

Built the exterior-deck foundation without beginning its pirate encounters:

- The crew quarters' existing ladder now enters a reversible 64x44 exterior
  map through safe named arrivals. Its broad tapered hull, two large complete
  mast-and-sail silhouettes, and rail geometry translate the authored
  `docs/design/pirate ship.png` composition into native procedural pixel art.
- Open sea surrounds the hull using a dedicated four-frame line-wave tile;
  there are no Waterdeep-style moving dots. Sea rendering remains fixed while
  the deck, Chuck, props, and future occupants share a presentation-only
  one-pixel rock over an eight-beat 126-BPM shanty cycle. Collision and map
  coordinates remain stable.
- Added one physical `Ship Exterior Ashtray`, development-visible `Ship
  Exterior Deck`, and a shared-loader save/respawn checkpoint. The existing
  shanty continues uninterrupted from the crew room.
- Added focused coverage for map composition, ocean art selection, exactly one
  checkpoint, shared loading, reversible ladder routing, and bounded periodic
  ship motion. The previous crew/cabin suites remain green.

## Previous Pass (session 153, commit 62b4cca)

Completed the final currently specified ship-interior room:

- The crew quarters' existing black east doorway is now a live three-tile
  passage into a reversible 36x26 captain's cabin with a one-time 40-cigarette
  Premium Buhetian Halfling Leaf chest and durable save state.

## Previous Pass (session 152, commit fba743f)

Built the second Phase 7 interior branch:

- The arrival compartment's east three-tile black doorway now enters a
  reversible 42x30 crew-quarters map. Its west doorway returns through a safe
  named marker; all three threshold cells use the ordinary transition table.
- Added eight tall hanging hammocks and one 34x25 round mess table as dedicated
  procedural ship props. Their one-tile solid anchors and broad overhangs keep
  the human furniture architectural at Chuck's scale. Cargo fills the corners
  without obstructing the room's main routes.
- Added one physical `Ship Crew Ashtray` and development-visible `Ship Crew
  Quarters` entry through the shared checkpoint loader. The same ship shanty
  continues uninterrupted.
- Added a reusable animated `PirateNPC`: two frames per facing, rhythmic
  update, authored first/repeat dialogue IDs, and a supplied durable progress
  flag. The seated pirate raises his mug and sways, comments on Chuck's coat on
  first interaction, and uses a shorter line thereafter. `crew_pirate_met`
  survives Ashtray saving and CONTINUE.
- The crew room visibly includes a deck hatch and black/open captain-cabin
  doorway. Both are named inert boundaries until their maps are implemented;
  no closed door was introduced and the exterior deck remains untouched.
- Targeted tests cover room content, one-checkpoint policy, reversible route,
  inert future boundaries, sprite animation, first/repeat dialogue, and save
  restoration of the conversation state.

## Previous Pass (session 151, commit d59344d)

Built the first non-combat-focused Phase 7 interior branch:

- The arrival compartment's west three-tile black doorway is now a live,
  reversible passage to `ship_galley`; a safe named return marker preserves
  the same open threshold and ordinary transition architecture.
- Added a 40x26 working galley with pantry shelving, hearth, counters, tables,
  cargo, broad escape lanes, one physical `Ship Galley Ashtray`, and a
  development-visible `Ship Galley` checkpoint. The shanty remains
  uninterrupted between both rooms.
- Added a human-scale pirate chef. At 96 pixels he turns toward Chuck and gives
  the exact authored warning; only after the dialogue closes does he pursue at
  58 px/s with ordinary swept collision. Contact costs 20 Sanity. He cannot be
  scratched, so the encounter encourages escape, and normal enemy reset
  rebuilds/re-arms him after death.
- Added a reproducible six-frame procedural sprite: two directional frames per
  facing give the cook a heavy stride and alternating cleaver swing, noticeably
  richer than the established stationary human NPCs while retaining their
  16x30 scale.
- Added targeted tests for map/checkpoint/audio content, reversible passage
  wiring, exact dialogue ordering, delayed pursuit, damage, and reset. Updated
  selector pagination regression coverage for the new third page.

## Previous Pass (session 150, commit 39ff813)

Polished the escape portholes and restored the pantry breakable behavior in
the lower hold:

- Removed the four isolated pure-white sun-glitter pixels from each cutscene
  porthole. The animated undulating crest lines and their darker shadow lines
  remain, so the sea still moves without mixing line and dot languages.
- Lower-hold shelf/jar map tiles now declare the actual `pantry_shelf` and
  `grain_sack` prop kinds over ship planks. WorldScene's existing pantry
  breakable construction therefore supplies the same scratch, debris, empty
  shelf, tile-clearing, carton-drop, and reload-restock lifecycle.
- Generalized shelf carton placement from pantry board only to safe pantry
  board or ship plank. Every one of the hold's eight shelves and floor jars
  now yields the established 20-cigarette carton; no duplicate ship-specific
  breakable implementation was added.

## Previous Pass (session 149, commit bfa8ee6)

Replaced the arrival compartment's closed doors with open doorway recesses:

- All west/east/south doorway cells now draw as uninterrupted black interior
  space within highlighted timber jambs, with no panel, latch, or closed-door
  silhouette. Their terrain is walkable so Chuck can enter each threshold;
  ordinary out-of-bounds collision contains the two unfinished future routes.
- The north portholes, southern lower-hold ladder, map geometry, transition
  wiring, checkpoint positions, and uninterrupted ship music are unchanged.

## Previous Pass (session 148, commit 7eca61a)

Started Phase 7 with the corrected arrival compartment and lower hold:

- The arrival compartment keeps exactly four animated portholes, all on the
  north hull. Human-scale doorways now occupy the other three walls for
  future interior branches. A southern floor ladder is a
  live reversible walk exit; the cutscene arrival moved one safe tile north.
- Expanded the procedural ship tileset with six side-door sections and a deck
  hatch/ladder while preserving its 4-frame rolling-wave porthole animation.
- Added `ship_lower_hold` (40x30): a cargo-filled rat nest using static aliases
  of the pantry shelf/sack silhouettes plus ordinary crates and barrels.
  Sixteen ordinary rats use the established scratch, patrol, damage, and reset
  systems. The same shanty continues through the ladder transition.
- Added shared-loader `Ship Hold`, one physical `Ship Hold Ashtray`, reversible
  named arrivals, and targeted Phase 7 tests for content, transition, loader,
  and enemy reset behavior.
- Added the user-authored Phase 7 contract and `docs/design/pirate ship.png`;
  that image is reserved as the composition reference for the later exterior
  deck map, which this pass deliberately did not begin.

## Previous Pass (session 147, commit f73c726)

Rebuilt the playable ship_deck to match the escape cutscene:

- New dedicated ship tileset (tools/generate_ship_tileset.py -> ship.png):
  plank floor, timber hull wall, and an animated 4-frame porthole tile.
  The porthole's sky/sea/wave-crest colours are the cutscene's exact
  palette (escape_cutscene_scene.py), and its frames roll the crests, so
  the compartment and the cutscene read as the same place. Added SHIP to
  tileset_layout (+ TILESETS + MAP_TILESET["ship_deck"]="ship") and the
  'Ø' porthole tile to TILE_DEFS (solid hull).
- assets/maps/ship_deck.txt rewritten (26x13): a wooden compartment
  ringed with portholes (a band across the top hull + side-wall
  portholes) over plank floor with cargo crates/barrels; arrival at the
  bottom (from_crawlspace, now tile 13,10), the ashtray at (8,7) — the
  checkpoint position (116,117) is unchanged.
- Tests updated: the wooden-room test now checks the compartment
  dims/portholes and that 'Ø' is solid; the art test asserts ship.png
  with an animated porthole row; the crawl test's arrival tile is 13,10.

## Previous Pass (session 146, commit 9ef67d4)

Made the rubble crevice prompt pop by walking in, not by interact:

- ChoiceTrigger gains `walk_triggered` (from a `_WALK_TRIGGERS = {"crevice"}`
  set). WorldScene now checks walk-triggered choice zones every frame
  after movement: on overlap it pushes the "Enter crevice?" DialogueScene
  and returns. A `_walk_choice_armed` flag (reset in load_map) fires the
  prompt once on entry and only re-arms after Chuck has left the zone —
  so declining "NO" while still standing on it does not re-ask.
- Walk-triggered choices are filtered out of `_interactable_in_range`, so
  the crevice is purely walk-driven; the sewer grate (not walk-triggered)
  keeps its interact prompt.
- The ship-deck escape test now drives it by walking into the zone
  (no interact press).

## Previous Pass (session 145, commit 185e890)

Reworked the ship theme from a major reel into a dark pirate one:

- data/music/ship_shanty.py went from D mixolydian to D MINOR. The
  fiddle tune now hammers the classic minor pirate loop (i-bVI-bVII:
  Dm-Bb-C), and the turns run the descending Andalusian cadence
  (Dm-C-Bb-A) with a raised-seventh C# — the swashbuckler-movie sound.
  The bass became a relentless galloping eighth-note ostinato; the
  accordion (brass) is bolder (horns, louder, holding the C# colour over
  the A); the crew chants lower and gruffer; the bright bells dropped to
  low ship-bell tolls. Same 126 BPM, 40 bars, 11 voices.
- Re-rendered ship_shanty.wav (peak 0.900, seam 0.000, RMS 0.175). No
  new wiring needed — the cutscene and deck already play ship_shanty.wav.
- The music test was renamed/strengthened to assert the minor tonality
  (F natural present, no F#, and the C# raised-seventh cadence).

## Previous Pass (session 144, commit cff3007)

Gave the ship (cutscene + deck) its own sea-shanty reel:

- data/music/ship_shanty.py — built from the Waterdeep-docks rhythm (same
  D mixolydian, flat-7 C-natural color, D/G/A groove) cranked to a fast
  fiddle reel at 126 BPM, 40 bars (~76s), 11 voices: fiddle reel tune
  (pluck_lead, near-continuous eighths), tin whistle ornaments (flute),
  accordion offbeat chops + turn-swells (brass), driving root-fifth bass,
  crew "hey!" shouts (choir) in the 2nd half, and a bodhran/backbeat kit.
  Reuses the existing instrument palette; no new instruments.
- Rendered to assets/audio/music/ship_shanty.wav (0.9 headroom; seam
  0.000; RMS 0.174, between docks and temple). Per-section RMS confirms
  the build (lighter A → fuller B turns → crew).
- Wiring: AREA_MUSIC["ship_deck"] and EscapeCutsceneScene's SEA_MUSIC
  both play ship_shanty.wav (idempotent, so the cutscene→deck handoff is
  seamless).
- Tests: test_music.py (reel character + rendered gates); the ship-deck
  music test updated to ship_shanty.wav.

## Previous Pass (session 143, commit 7a64aec)

Made the rubble look like a genuine roof collapse, not rows of blocks:

- temple_rubble_block is now 12 variants. rubble_block(variant) seeds a
  per-variant RNG and drops one or two broken chunks (_stone_chunk,
  lit from above) at a random offset and tumble-rotation (±24°) inside a
  44x36 canvas. Because props anchor bottom-center per tile, the
  off-centre chunks break the grid, and the per-tile variant index
  (col*31+row*17)%12 scatters the angles — so no orderly rows.
- generate_temple_rubble.py places debris in irregular collapse-piles:
  density is a 0.18 base scatter plus up to +0.68 near ~14 collapse
  centres, so blocks heap thickly where the roof dropped and thin out
  between. ~270 blocks + ~45 drums, 214 Astral, the paved lane still
  clear (connectivity re-asserted).
- 8 new block PNGs + 4 updated; no churn elsewhere. All 55 suites pass.

## Previous Pass (session 142, commit 4667e3f)

Rebuilt the rubble map's debris as big broken blocks:

- New prop temple_rubble_block — four chunky 3/4-view broken-masonry
  sprites (tools/generate_temple_props.py rubble_block(); 30x24; lit top
  face, shadowed side, cracks, a broken-off corner, moss). Registered in
  prop.py _SPRITES and as tile 'ß' (solid, under '·').
- tools/generate_temple_rubble.py now fills the chamber with a dense
  field of these big blocks (~360) plus a scatter of smaller column
  drums (~45) for scale. Torches, cracked stelae ('‡'), and flat
  wall-tile boulders ('█') were all removed, so it reads as one
  consistent field of collapsed masonry with the clean paved '≡' lane
  threading through. temple_column is unchanged → temple dressing maps
  untouched.
- Only the four new PNGs were written (no churn on the other prop art).
- test_phase6_temple_rubble.py now asserts the blocks dominate and there
  are no torches.

## Previous Pass (session 141, commit 42c7208)

Reworked the rubble exit and the escape cutscene per playtest notes:

- The rubble exit is now an "Enter crevice?" YES/NO interaction, not a
  walk-over exit. data/choices/temple_rubble.json ("crevice": YES →
  goto ship_deck, NO closes); ChoiceTrigger "crevice" (2x2); a marker
  Ҏ on the paved lane one tile above the ∇ crawl mouth. The ∇ walk-exit
  was removed from AREA_WALK_EXITS; YES's goto ship_deck is intercepted
  in WorldScene's _pending_map handler to replace the world with the
  escape cutscene (so the interception moved from the walk-exit block to
  the pending-map load).
- The escape cutscene is now wordless — the three narration captions and
  the caption drawing were removed, shortening the timeline (HOLD_END
  11.4, FADE_END 12.2).
- Its emergence tableau was rebuilt: the open hull breach became a
  wooden hull WALL set with three round brass-rimmed portholes, each
  showing a sunlit, lighter-blue sea over a horizon — plainly a ship's
  interior, the sea framed in circles. (_draw_hold / new _draw_porthole;
  lighter sea palette.)
- Tests: test_phase6_escape_cutscene.py now asserts wordlessness and the
  shorter timeline; the rubble test asserts the crevice choice trigger
  (no walk-exit); the ship-deck test drives YES → cutscene → deck.

## Previous Pass (session 140, commit ce4c4f2)

The escape cutscene, which ends Phase 6:

- src/scenes/escape_cutscene_scene.py (new): EscapeCutsceneScene, a
  contained input-free Scene modelled on FallingCutsceneScene. Chuck
  crawls a tight stone tunnel toward a growing blade of daylight
  (receding stone rings for forward motion, a corner vignette for
  tightness, scrape sfx), the light whites out the screen, and he
  emerges into the wooden hold with the open sea beyond the hull breach
  (colours matched to the ship_deck map). The sea theme
  (waterdeep_docks.wav) swells in at the emergence. Three timed
  narration captions land the beat, then it fades to black and hands off
  to the playable deck via load_checkpoint("ship_deck", sanity=...),
  carrying Chuck's Sanity across.
- src/scenes/world_scene.py: the rubble crawlspace walk-exit now
  replaces the world with the cutscene instead of loading ship_deck
  directly (mirrors the sky-fall → FallingCutsceneScene trigger).
- PHASE-6.md: "The cutscene ends aboard a ship at sea" is now checked.
- Tests: test_phase6_escape_cutscene.py (3, new — captions, draws every
  phase input-free, hands off preserving Sanity); the ship-deck crawl
  test now asserts it routes through the cutscene.

## Previous Pass (session 139, commit b1a2b1d)

temple_rubble was rebuilt to look like the temple's ceiling has caved in:

- The chamber is now choked with ~460 pieces of fallen-stone debris —
  toppled columns ('¬') and cracked leaning stelae ('‡') scattered as
  separate props at ~58% density off the route (so it reads as rubble
  on the floor, not a wall), plus a few lone '█' boulders ringed by
  floor. Split by 15 distinct blocks of Astral Sea (~213 'V'). Off the
  route it is almost impassable.
- One intact paved lane ('≡', the temple's own processional tile) winds
  torch-lit from the from_fireball arrival, past the rubble ashtray, to
  the crawlspace mouth. Against the debris the clean lane is unmistakably
  the way out. The Ѣ/Ѥ marker unders changed to '≡' so they sit
  seamlessly on it.
- tools/generate_temple_rubble.py was rewritten (curated Astral blocks,
  a lane-polyline clear + pave, a deterministic debris scatter, lone
  boulders, flanking torches) and still asserts arrival → anchor →
  crawlspace connectivity on foot before writing.

## Previous Pass (session 138, commit 2968d01)

The rubble got its one way out, leading to the ship — the Phase 6 → 7
boundary:

- The crawlspace exit: a narrow mouth ('∇', the established threshold
  tile) is carved into temple_rubble's south wall at the foot of a
  cleared right-side lane. tools/generate_temple_rubble.py now protects
  that lane (col 34, rows 20-27) and asserts the mouth is reachable on
  foot before writing. Walking onto it transitions to the ship
  (AREA_WALK_EXITS["temple_rubble","∇"] → ship_deck / from_crawlspace).
- ship_deck (assets/maps/ship_deck.txt, 30x18): a cramped wooden hold
  on the docks tileset — plank floor, lashed barrels and crates — with
  a jagged breach in the hull (top) opening onto the open sea (water).
  Chuck arrives at the crawl mouth in the deck floor and walks up toward
  the sea reveal. No onward exit (Phase 7 is unbuilt).
- Wiring: new markers Ҋ (arrival:from_crawlspace) / Ҍ
  (anchor:ship_deck_anchor); MAP_TILESET["ship_deck"] = "docks";
  AREA_MUSIC["ship_deck"] = "waterdeep_docks.wav" (the sea theme
  returns); checkpoints "Ship 1" (runtime, dev-visible, fade_in) +
  "Ship Ashtray".

## Files Changed

- tools/generate_temple_rubble.py (full rewrite: curated Astral blocks,
  lane pave, debris scatter, boulders, torches),
  assets/maps/temple_rubble.txt (regenerated), src/world/tilemap.py
  (Ѣ/Ѥ marker unders → '≡'), tests/test_phase6_temple_rubble.py (the
  broken-chamber test now locks in the debris count, the paved lane, and
  the raised Astral count).

## Verification Performed

- All 55 standalone test suites pass; targeted ship arrival, lower-hold, and
  checkpoint suites pass independently.
- Headless launch/render succeeded at native 320x180 for both ship maps.
- The arrival ladder enters the hold at its safe named arrival; the return
  ladder restores the arrival compartment, and enemy reset restores all
  sixteen rats.
- Native screenshots were inspected for north-only portholes, side-door scale,
  ladder readability, cargo silhouettes, and rat readability.
- Session 150 targeted suites pass for the escape cutscene, lower hold, pantry
  breakables, and ship arrival. Native screenshots confirm line-only cutscene
  waves and the unchanged lower-hold cargo presentation.

## Known Issues

- None known from this pass.

## Scope Notes

- Phase 6 is complete end to end. Per the user's direction, the escape
  cutscene intentionally starts `ship_shanty.wav`; do not split it into a
  separate cue.
- Phase 7 is complete. The Nine Hells arrival is deliberately an input-free
  held tableau because no Phase 8 implementation document exists in the
  repository yet.

## Recommended Next Bounded Task

- Do not begin Phase 8 gameplay until its authoritative phase document is
  added. The held Nine Hells arrival tableau is the intended handoff point.
