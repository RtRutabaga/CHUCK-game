# CHUCK — Project Status

Updated: session 86 (Chult Map 2 raptors and Ashtray). This file is required by
the project rules and updated every session.

## Working systems

- Game loop, native 320x180 surface integer-scaled 4x, scene stack
  with overlay support (dialogue draws over the frozen world)
- Startup now hands off from the one-frame BootScene to a native 320x180 title
  menu. NEW GAME clears the single save slot and loads the authored Waterdeep
  opening; CONTINUE is visibly disabled unless a valid current-version save can
  be restored. A config-gated DEV CHECKPOINTS option opens the temporary test
  selector and disappears entirely when `ENABLE_DEV_CHECKPOINT_SELECTOR` is
  false
- Input: keys -> named actions, normalized 8-way movement vector
- Text maps (assets/maps/): terrain legend + marker system (spawns and
  objects declare their under-terrain); loud errors on any bad data
- Swept, axis-separated tile collision (no tunneling at any dt)
- Smooth frame-rate-independent follow camera, clamped to map bounds
- Sprites from text grids (tools/): Chuck (idle/walk x4 facings), the
  cat, seven human NPCs, and the 75-glyph 5x9 pixel font
- Sanity with i-frames; cigarette pickups; HUD meter (a cigarette
  burning down); patrolling cat hazard; Astral Anchor checkpoints;
  quiet vanish -> starfield -> respawn (no game-over screen, ever); enemies
  rebuild from their map markers when Chuck returns
- Checkpoints and saving: one registry defines map, position/named arrival,
  facing, required progression flags, and visibility/save rules. NEW GAME,
  CONTINUE, and the development selector all call the same
  `CheckpointLoader.load_checkpoint(checkpoint_id)` path. Map-entry definitions
  retain the established local retry behavior; the four authored Ashtrays have
  stable IDs and save on first contact. A small version-1 JSON slot under the
  user's application-data folder stores only checkpoint ID, current Sanity, and
  durable progression flags. Invalid, missing, outdated, unknown, or forged
  development-only checkpoint saves disable CONTINUE without crashing. Durable
  flags are `sewer_completed`, which restores the tavern's open exterior, and
  `chult_reached`, which restores the playable Chult state
- Dialogue: JSON data files, typewriter box, seven NPCs; choice
  options can speak, navigate, or close silently
- Audio: pure-stdlib engine (src/audio: synth, instruments,
  sequencer), offline rendering (tools/generate_audio.py +
  tools/generate_music.py <name>), AudioSystem with graceful no-device
  fallback; four composed pieces (data/music/, 7-10 voices) —
  the 95s warm Waterdeep Docks theme and the 83s eerie/funky D-minor
  Sewer theme loop seamlessly, while the 36s one-shot fall-to-Chult cue drives
  the Phase 3 cutscene. Chult now has an original 86s D-Dorian exploration loop:
  a persistent syncopated deep-bass hook, pitched hand drums, woody offbeats,
  layered retro percussion, a compact plucked melody, flute answers, and a humid
  breakdown. It enters immediately on either cutscene arrival or Chult 1 load;
  SFX for pickup, interact, hurt, vanish, respawn, anchor
  chime, a quiet rounded jump bounce, scratch scrape, and per-surface footsteps.
  Re-requesting the same looping track is idempotent, so movement among the
  docks, tavern, and pantry preserves the Waterdeep theme's playback position;
  sewer, cutscene, Chult, and future differently scored regions still switch
  or stop normally
- Distribution: reproducible PyInstaller 6.21 single-file Windows build
  (`CHUCK.spec` + `requirements-build.txt`) bundles all runtime assets and data
  into `dist/CHUCK-demo.exe`. The windowed EXE needs no Python installation,
  excludes unused optional NumPy/OpenGL support, and writes crash diagnostics
  beside itself rather than into its temporary one-file extraction directory
- NPC interaction covers the whole visible person (probe + overlap)
- Depth: barrels/crates are standing props (solid tiles + tall
  sprites), y-sorted with all characters by feet position
- Ground: per-area drawn tilesets (tileset_layout.Tileset: a sheet +
  its terrain rows + char maps; tileset_for(map) picks one) with stable
  per-position variants, animated frames, view culling, and a flat-
  color fallback when a sheet is missing. docks.png, sewer.png, tavern.png,
  and pantry.png
- Bobert asleep in his barrel at spawn (solid scenery, tile 'B');
  cigarette is a drawn sprite; the Astral Anchor presents as an
  ashtray (cold ash dormant / live ember + smoke when attuned), with
  rect fallbacks for headless runs
- 56x35 map: north warehouse district, tavern front (door 'D', HEROD
  sign 'H'), southeast market with awning 'a' — the overhead layer
  draws canvas over Chuck; flood-fill connectivity is a permanent test
- Prop dialogue: Bobert snores ("... Zzzzz."), the sign reads "Herod
  Cover Band - Tonight Only", and all three northern house doors answer
  "it's closed"; other props are mute; NPCs answer first
- Playtest sizing: human-scale tavern door (now 48x34 with hanging
  lanterns), enlarged west pier (4 rows to col 1), south pier with
  T-head, and a 48-tile market awning
- Tavern exterior: slate roof + chimney props + eave trim + tan brick
  facade + lit windows, all new tileset terrains ('r','e','t','W','m'). It
  begins with solid double doors; returning through the sewer outflow swaps
  them for a 48x34 black open threshold with lit side lanterns. Only the
  threshold tile becomes walkable; the surrounding facade remains solid. The
  freestanding HEROD sign now sits one tile farther west so neither its post nor
  face competes with the open doorway
- District wall: battlements/brick/banners/flickering torches
  ('w','b','F','i') with portcullis gates drawn overhead ('g');
  both northern portcullises now occupy the upper opening row with clear
  walkable stone beneath, so they read as raised/open without changing the
  passage footprint; northern boundary wall battlemented too
- District houses: the three north blocks reskinned with the tavern
  grammar + decorative house doors ('h'); the doors remain solid but are now
  interactable and all return the shared line "it's closed"
- Market stall (cutaway): checkered canopy over the back rows ending
  in scalloped edge ('u') + corner posts ('P'); goods '1'-'5' (produce
  crates/table/barrel) stand visible in the open front row. A human-scale
  market woman stands just left of the goods in a muted headscarf and apron;
  she directs Chuck toward sewer scraps without a quest or marker
- Ruined foundation ('R' walls / 'f' rubble): the mid-map block is a
  crumbling ruin with collapsed gaps; solid, style only
- Breakable grass: three walkable 16x16 tufts frame the ruined foundation and
  four more are scattered through the sewer on ordinary dirt. The shared
  scratch dispatch shreds each into eight radial leaf fragments over 0.42
  seconds and reveals one cigarette at its center. The former exposed
  cigarette south of the ruin was relocated into the first authored reward.
  Grass resets when the map reloads and uses one reusable entity with separate
  stone, dirt, and jungle-ground markers. Eight more tufts are distributed
  across Chult's jungle ground without replacing thorns, enemies, routes, or
  checkpoints. Within two tiles, Waterdeep and sewer reuse the exact
  `Press F to scratch` tutorial line;
  Chult remains prompt-free. Future exterior Chult maps should continue this
  restrained grass scatter through the same shared implementation
- Shared mathutil.approach() (camera follow + any future smoothing)
- Crash logging: unhandled exceptions write crash_log.txt
- Map transitions: WorldScene.load_map(name) (re)builds a whole area;
  a dialogue choice can carry Chuck between maps. Where a choice goes is
  data — a choice option's `goto` names the destination map (no code
  table). Each area's looping music (or deliberate silence) is data too
  (transitions.AREA_MUSIC). Navigation choices can also carry a named arrival
  marker and restrained arrival choreography without hardcoded coordinates.
  The entrance grate's YES drops Chuck straight into the sewer, wordlessly —
  no confirmation lines
- Sewer: assets/maps/sewer.txt is a 48x72, mostly-linear descent
  (walkable corridor wrapped in thick rock so it fills the view) with
  its own tileset (assets/tilesets/sewer.png, built by
  tools/generate_sewer_tileset.py): brick walls '#', stone landing ',',
  dirt 'd', mud 'M', and a drainage channel '%' that flows over 3
  frames. Its own looping theme plays on entry (data/music/sewer.py ->
  sewer.wav). The east-side approach now runs for roughly 28 rows before the
  required jump, with sparse avoidable Astral substitutions foreshadowing the
  wrong map. A hard-edged band of animated dark-blue/purple Astral material
  then interrupts the corridor; SPACE performs a short
  committed hop with a subtle rounded bounce tone that crosses it but cannot
  bypass normal walls. On foot,
  the Astral blocks are a lethal fall zone: control locks, Chuck quietly
  shrinks and sinks for 0.65s, then the existing Astral Anchor respawn
  flow returns him to the sewer entrance. Airborne Chuck crosses safely.
  The nearby jump hint clears after Chuck lands beyond it. Beyond the gap,
  three ordinary rats occupy
  a one-tile choke: their 10x8 sprites are smaller than Chuck, contact
  costs 10 Sanity, and their bodies block progress. F performs a brief
  forward scratch with a moving fan of translucent claw afterimages and
  a brief filtered scrape SFX; one swipe defeats one rat, and the nearby
  tutorial hint disappears when all three are gone. Past the encounter the
  map opens broadly west and continues for another three screens, with Astral
  blocks becoming denser and more chaotically arranged around a continuous
  narrow safe route. Four additional ordinary rats are spaced through this
  late corrupted run; they use the established one-hit behavior without
  extending the original scratch tutorial prompt. Those four make restrained
  six-pixel horizontal patrols at 12 px/s; the three choke rats and any rat
  beside walls, props, another rat spawn, or Astral fall tiles stay stationary.
  Defeated rats reset when Chuck dies and returns. A cold ashtray midway through
  the late maze lights on contact, becomes the active respawn checkpoint, and
  introduces itself on proximity with "Ashtrays save your progress." The safe
  route ends at a three-tile iron drainage outflow drawn overhead from the sewer
  tileset. E opens "Leave the sewer?" with YES/NO choices. NO closes silently;
  YES returns Chuck to the Waterdeep south pier, where he appears one tile out
  in the harbor and rises onto the planks over a restrained 0.65-second
  control-locked climb, with no further dialogue or explanation

- Phase 3 tavern shell: once the sewer return has opened the exterior doorway,
  stepping onto it loads a compact 30x20 tavern common room. A named interior
  arrival places Chuck safely above the threshold facing inward; the matching
  walk-out exit returns him below the Waterdeep doorway facing away, preventing
  immediate transition bounce. The room uses a dedicated procedural tileset;
  its floor now calls the pantry generator's exact worn-board renderer while
  retaining the tavern's distinct interior walls. A bar counter, three
  human-scale tables, chairs, hearth, barrels, and crates remain solid. The
  hearth now occupies the floor tile directly beside the east wall, with no
  intervening plank gap. A small
  raised stage against the north wall uses dedicated top-board and solid front-
  fascia terrain. All remaining floor and the stage's side access form one
  connected traversal area, the camera remains on the normal WorldScene path,
  and the existing Waterdeep theme currently carries across the doorway
- Tavern hook: three non-solid human NPCs use the established dock-worker scale
  and facing/dialogue behavior. The bartender recognizes Chuck and directs him
  to unwanted cheese in the kitchen; a patron supplies one restrained ambient
  line. A third human-height but deliberately thin/lanky musician stands on the
  stage in green clothes and hat with an orange beard and lute, promising 37
  renditions of "Fortune Favors the Kobold." The former common-room cheese trail
  is gone. The north doorway remains plainly open into the pantry without
  requiring an inventory item or flag
- Phase 3 pantry: a compact 26x18 storage room connected bidirectionally to the
  tavern with safe named arrivals. Worn boards, human shelves with jars, sacks,
  barrels, and crates establish the ordinary room before its central broken
  floor. Thirty scattered purple/dark-blue `V` blocks now fracture the ordinary
  boards around the room while reusing the sewer's exact animated Astral art and
  existing fall -> local respawn behavior; small singles and pairs make reality
  feel substituted without breaking the connected safe route. A separate hard-
  edged teal sky with blocky clouds is immediately distinct at native scale.
  Its animation now uses twelve seeded, stable cloud layouts instead of two
  repeated stamps, varying cloud height, width, horizontal placement, and drift
  without rearranging the floor between frames or runs.
  The game's sole cheese sits on a one-board island inside that broad sky field:
  every cardinal approach is four tiles from ordinary floor, beyond Chuck's
  fixed 2.3-tile jump. It is a readable temptation toward the successful fall,
  not a collectible or reachable reward. Approaching within two tiles of the
  teal sky repeats the established `Press SPACE to jump` tutorial line; it is
  absent elsewhere in the pantry and uses the existing temporary hint system
- Fall materials now classify independently before choreography. Astral retains
  its exact fall -> Sanity depletion -> local retry behavior. Teal sky is a
  walkable successful-fall trigger: it begins with the same restrained 0.65s
  shrink/sink animation, preserves Sanity, and replaces gameplay with a
  dedicated `FallingCutsceneScene`. The cutscene has no player-controlled entity
  and fades out the Waterdeep music. After four seconds of exposed freefall, a
  dedicated 36-second one-shot cue launches directly into an urgent D-minor
  pulse, fast bass, melodic runs, and full synthesized kit. It grows chromatic
  and denser as the canopy arrives, fractures at impact, then leaves sparse
  flute, bells, and bass under Chuck's return and cigarette drag. Its complete
  39-second authored visual timeline
  intentionally holds open sky for almost 24 seconds while irregular cloud
  layers scroll upward and the teal grade slowly darkens. Branches, vines, and
  trunks then accelerate through frame as a dense eerie jungle and its ground
  rush upward. Chuck impacts at 29 seconds, quietly blips out through the
  familiar Astral language, blips back, looks left/right/down, places a
  cigarette in his mouth, and takes a restrained smoking drag. Existing scrape,
  thud, vanish, and respawn cues punctuate the collision and return. At 39
  seconds the scene holds on the smoking jungle tableau for two more seconds,
  fades fully to black over 0.75 seconds, then enters playable Chult through the
  shared checkpoint loader. The authored `chult_landing` entry keeps the screen
  black across scene replacement and fades gameplay in over another 0.75
  seconds with control and simulation locked. Direct Chult 1/CONTINUE loads do
  not replay this one-time arrival presentation

- Phase 4 jungle layout: `chult_jungle.txt` is a 64x60 padded playable jungle space
  with a dedicated procedural `chult.png` sheet derived from the cutscene's
  ground, canopy, trunk, vine, and leaf palette. Dense vegetation forms stable
  collision boundaries around the landing and large growth masses create a
  main northbound route with connected side clearings. A central vegetation
  mass near the landing creates an immediate optional left/right exploration
  choice. A three-tile overhead fallen log cuts through a dense wall as the
  first explicit Chuck-sized shortcut: ordinary movement carries Chuck beneath
  the human-scale trunk, which occludes him without adding a crouch control.
  The hidden `chult_landing` runtime
  checkpoint receives the cutscene handoff; the nearby Ashtray is the saveable,
  development-visible `chult_anchor`, displayed as `Chult 1`. Activation saves,
  CONTINUE restores it, and Sanity-zero return uses it. The area is deliberately
  silent until its dedicated Phase 4 soundtrack pass

- Phase 4 undead: two zombies and two skeletons occupy broad Chult clearings,
  never mandatory chokes. Both use the established 16x30 human-NPC scale and
  simple three-facing procedural sprites. A reusable `UndeadEnemy` performs
  direct collision-aware pursuit only within 112 pixels. Zombies shamble at
  18 px/s, inflict 20 Sanity, and take eight scratches; skeletons move at
  25 px/s, inflict 15 Sanity, and take six. Scratch still hits at most one
  target per swipe. Contact blocks Chuck and respects existing damage i-frames.
  Defeated undead rebuild from map markers during the established Astral return,
  alongside cats and rats, while the wide encounter spaces remain escapable

- Phase 4 terrain hazard: 25 thorn tiles occupy six small patches scattered
  through optional clearings, rendered as bright angular stems over ordinary
  jungle ground. A
  reusable terrain-hazard lookup checks Chuck's full footprint rather than a
  Chult-specific scene branch. Contact on foot costs 10 Sanity through the
  established i-frame/hurt feedback; a committed jump passes safely above it.
  Flood-fill coverage verifies the northbound main route remains reachable
  without touching any thorn tile. The former backpack and boot have been
  removed from the northern clearing, along with their unused art and dialogue

- Phase 4 route deeper: a three-tile-wide worn track now leads out of the
  existing northern clearing and terminates beneath a dense canopy arch. The
  walkable threshold carries the named `boundary:chult_deeper` marker. Phase 5
  now binds that existing threshold to `chult_cog`, entering at its safe named
  southern arrival through the ordinary walk-exit/checkpoint path
- Phase 5 Chult Map 2 foundation: `chult_cog.txt` is an 80x80 authored exterior,
  substantially larger than the 64x60 first jungle. One connected exploration
  network joins a broad southern future-cog clearing, central future-raptor
  territory, and northern future-thorn-maze reserve. It reuses the established
  Chult terrain, dense trees/shrubs, theme, camera, collision, and breakable
  grass language. The shared registry exposes its runtime entry as `Chult 2`;
  no separate debug teleport or new progression flag was added
- Phase 5 sailing cog discovery: a single 224x152 procedural landmark dominates
  the southern clearing. Its shallow diagonal projection sits between the
  game's bird's-eye view and a side elevation: a broad visible deck, sparse
  wooden posts, deep near hull, and sharply tapered southwest bow establish the
  three-quarter perspective. The reference-directed upper silhouette uses one
  wide rectangular cream sail on a plain exposed central mast. The deck remains
  open, with no northwest box, ladder, rigging, or rope details. The mast is
  layered for perspective: the complete sail renders over the rear deck so its
  shape remains uninterrupted and occludes part of the boat, while the lower
  post and broad foot render over both layers, visibly anchoring it aboard.
  Its shaped fourteen-tile-wide solid footprint matches the visible base while
  leaving safe routes around both sides. Twenty-four scattered `V` substitutions arc
  around the hull in small broken clusters, reusing the established animated
  Astral art and ordinary fall/return behavior. They are avoidable on the main
  route, so the ship discovery does not become a mandatory jump gate
- Phase 5 cog sailor: one ordinary human-scale sailor stands visibly on the
  cog's deck in a faded navy coat, weathered trousers, and pale cap. A contained
  elevated-NPC marker preserves the ship's solid hull while painter-ordering
  him over the deck; only his normal interaction zone extends down to the safe
  ground tile beside the hull. From there, the existing dialogue scene delivers
  the three exact sequential boxes: `Oi!`, `Look at that rat.`, and
  `Walkin' on the sea...`. No ship-specific dialogue or teleport path was added
- Phase 5 raptor territory: exactly two large 36x24 Chultan raptors occupy the
  broad central Map 2 clearing, well north of the cog. Their two-frame run,
  24x12 footprint, 54 px/s pursuit, 152-pixel notice radius, and 25-Sanity
  contact make them substantially larger, faster, and more dangerous than the
  prior undead while leaving Chuck's 80 px/s movement and the clearing's wide
  side routes as reliable escape options. Ten scratches can defeat one, but no
  route or progression state requires either kill. They use shared collision,
  scratch, Sanity/i-frame, painter-order, and enemy-respawn behavior
- Chult Map 2 now has one physical Ashtray south of the cog. Its hidden
  `chult_2_anchor` save definition is distinct from the development-visible
  `Chult 2` map entry but uses the same registry and loader. Contact saves,
  CONTINUE restores the Ashtray position, and Sanity-zero return rebuilds both
  raptors there. The durable decision log now records one physical checkpoint
  for each newly authored gameplay map

- Phase 4 dense vegetation art: the former blocky green collision texture is
  now an interlocked organic canopy of broad leaves, woody seams, and hanging
  vines. Across the same solid vegetation cells, 165 deterministic y-sorted
  tree props use three 34x46 silhouettes with layered tropical crowns, trunks,
  and trailing vines. A second solid vegetation decoration adds 170 broad-leaf
  shrubs across the same masses using three 28x24 variants: overlapping pointed
  leaves, central veins, and brighter tropical midtones. Trees rise above human
  NPC height while shrubs are wider than two Chucks, making each collision mass
  read as dense forest and understory without changing a walkable tile or route

## Placeholder systems
- Phase 4 previous-traveler evidence needs a replacement environmental scene
  after the requested backpack/boot removal; all other authored feature slices
  remain pending full-route human playtest and acceptance
- (Quiet music variation cut by creative direction — soundtrack is
  Phase-One-complete)

## Known issues / accepted quirks

- E and RETURN interact; SPACE jumps. The jump is intentionally short;
  Astral material is safe only while Chuck is airborne.

- Scroll shimmer fix (session 29): native pipeline audited whole-pixel
  (int camera offset used by every draw; exact 4x nearest-neighbor
  scale). Cause was at presentation: Windows DPI scaling stretching
  the DPI-unaware window non-integrally (+ possible tearing). Fixed
  via SDL_WINDOWS_DPI_AWARENESS=permonitorv2 and vsync=1 (best-effort).
- Stop-shake fix (session 30): vsync + clock.tick double-pacing made
  dt oscillate, which showed as +/-1px lurches during the camera's
  asymptotic settle tail. Fixed by clamping dt (MAX_DT = 1/30) and
  snapping the camera to target within 0.5px so the settle ends
  crisply instead of hovering at a rounding boundary.

- NPCs are intentionally not solid (Chuck walks between boots)
- The world freezes entirely under dialogue (deliberate)
- Docks map bottom rows are open water with no southern content

## Tests

30 suites (most pure Python/headless): collision, tilemap,
camera, animation, sanity, hazard, dialogue, audio, props, tileset,
tutorial, choice, music, transitions, jump, combat, outflow, enemy_reset,
tavern, pantry, packaging, checkpoints, Chult landing, Chult undead,
Chult terrain hazard, Chult route-deeper boundary,
Chult dense vegetation, breakable grass, Phase 5 Chult Map 2 foundation,
Phase 5 raptors
(`python -m tests.test_<name>` from the project root, or `pytest`).
The map-transition flow (grate YES -> sewer) is also verified
end-to-end headlessly with dummy SDL drivers.

## Phase 2 progress (starting area + sewer tutorial)

1. [x] Waterdeep guard: armored NPC at the upper plaza's east edge,
       "Stick to the docks, rat." No gate/barrier — the map layout
       already blocks (sessions 32-33)
   - [x] Market woman: human-scale NPC beside the open market goods,
         "No handouts here. If you're hungry, you should check the sewer for
         scraps" with no quest, marker, or waypoint (session 51)
2. [x] Tutorial text ("Press E to interact"), area-scoped, shown only
       while an interactable is in reach (session 34)
3. [x] Sewer grate + Yes/No dialogue choice: choices are data
       (data/choices/*.json), DialogueScene renders options with a
       caret, up/down selects, E commits; YES enters the sewer and NO
       immediately closes with no follow-up text (sessions 35/48)
4. [x] Sewer map + tileset: the grate's YES loads a narrow, linear
       sewer map (assets/maps/sewer.txt) via a reusable
       WorldScene.load_map + data-driven `goto` (sessions 36-37). Now
       with its own art (assets/tilesets/sewer.png): brick walls, stone
       landing, dirt/mud, and a flowing drainage channel. Per-area
       tilesets (tileset_layout.Tileset + tileset_for). YES is wordless
5. [x] Sewer music: an eerie/funky 83s D-minor loop (data/music/sewer.py,
       rendered to sewer.wav), wired via AREA_MUSIC and playing on entry
       (session 38)
6. [x] Astral Sea glitch blocks + jump mechanic & tutorial: animated
       dark-blue/purple wrong-map tiles form a one-tile fall-death zone;
       SPACE makes a restrained forward hop, a failed crossing plays a
       shrink-and-sink fall before normal respawn, ordinary walls remain
       solid, and the hint clears after landing beyond it (sessions 39/41)
7. [x] Rats + scratch attack & tutorial: three smaller ordinary rats
       physically block a narrow post-gap choke; F makes a brief forward
       motion-blurred swipe with a dry scrape SFX, one hit removes one rat,
       contact costs light Sanity, and the proximity hint clears with the
       group (sessions 40/42)
   - [x] Sewer route expansion: longer pre-gap walk with sparse Astral
         foreshadowing, then a broad westward post-rat continuation with
         escalating corruption and a preserved safe path (session 43)
8. [x] Sewer exit -> climb-out -> return to docks: a rat-scale iron outflow
       uses a data-driven YES/NO interaction and named south-pier arrival;
       NO closes silently, while YES has Chuck rise one tile from harbor water
       onto the planks in a brief, silent, control-locked animation. The late
       maze now also contains an ashtray checkpoint with proximity guidance
       (sessions 47/50)
9. [x] Tavern doorway opens (Phase 3 setup): the initial solid doors remain
       until Chuck returns through the sewer outflow, then become a dark,
       walkable exterior threshold. No interior or Phase 3 transition is
       present (session 52)
10. [x] Added reusable scratchable grass: three tufts around the ruined
        foundation and four through the sewer. Their brief leaf-debris animation
        reveals cigarettes, while a two-tile Waterdeep/sewer-only proximity hint
        repeats `Press F to scratch` (sessions 76-77).

## Next recommended session

Author the compact northern thorn maze and its readable route toward Chult Map
3 using the existing thorn system. When Map 3 is created, include its one
physical Ashtray and shared development checkpoint; do not begin its undead run
in the same pass.

## Also open

- Full Phase 2 human playtest and acceptance
- Dedicated tavern music or ambience (the shell currently reuses Waterdeep)
- Full clean-start Phase 3 human playtest and timing acceptance

## Phase 4 progress (Chult jungle)

1. [x] Phase 4 contract added and made the active development scope.
2. [x] Phase 3 tableau now hands control to a first playable Chult landing map
       through `load_checkpoint("chult_landing")` (session 64).
3. [x] First procedural Chult terrain sheet matches the cutscene palette and
       supports stable jungle-ground and dense-vegetation collision language.
4. [x] `Chult 1` Ashtray is wired to save, CONTINUE, development selection, and
       Sanity-zero respawn through the existing shared architecture.
5. [x] Expanded 64x60 padded connected exploration layout with a main route, optional
       branch, and overhead fallen-log passage sized for Chuck (session 65).
6. [x] Added two human-scale durable zombies and two skeletons with simple
       collision-aware pursuit, avoidable placement, existing scratch/contact
       damage, and Astral-return reset behavior (session 66).
7. [x] Expanded the reusable thorn terrain to 25 tiles across six optional
       patches: 10 Sanity on-foot contact, existing i-frames, jump-safe
       traversal, and a safe main route around every patch (sessions 69/75).
8. [ ] Add replacement previous-traveler evidence after the requested removal
       of the backpack and boot (session 75).
9. [x] Added a clear worn north trail and canopy-framed, named
       `chult_deeper` boundary without inventing the next full map (session 71).
10. [x] Added an original 86-second bass-forward Chult exploration loop with
        syncopated percussion, layered groove, melodic identity, clean looping,
        and normal area/checkpoint audio integration (session 72).
11. [x] Replaced block-like dense-jungle art with organic canopy texture and
        165 oversized tree silhouettes while preserving collision and routes
        (session 73).
12. [x] Added 170 deterministic broad-leaf shrub props across remaining solid
        vegetation cells, with three procedural variants and no route changes
        (session 74).
13. [x] Scattered eight reusable breakable-grass tufts across ordinary jungle
        ground and established them as an exterior-Chult map convention without
        extending the Waterdeep/sewer scratch tutorial (session 78).

## Phase 5 progress (deeper into Chult)

1. [x] Added the Phase 5 contract and made it the active development scope.
2. [x] Added the 80x80 connected Chult Map 2 foundation, linked the established
       Phase 4 north threshold to its named southern arrival, reused the Chult
       tileset/theme, scattered ten shared grass tufts, and registered `Chult 2`
       through the shared checkpoint loader (session 79).
3. [x] Added the oversized three-quarter-view sailing cog landmark, shaped
       solid hull footprint, and 24 avoidable animated Astral Sea substitutions
       around its base while preserving safe routes on both sides (sessions 80-84).
4. [x] Added a human-scale sailor visibly on the solid cog deck, reachable from
       safe ground and using the exact three sequential dialogue boxes through
       the existing dialogue system (session 85).
5. [x] Added exactly two large, fast, scratchable raptors in the broad central
       encounter space, with avoidable finite pursuit and normal respawn reset.
       Added Map 2's single physical shared-loader Ashtray (session 86).
6. [ ] Author the thorn-maze route into Chult Map 3.
7. [ ] Build the undead run, Chuck-sized escape, and Chult Map 4 temple exterior.

## Phase 3 progress (tavern, pantry, and fall to Chult)

1. [x] Tavern doorway transition + common-room shell: bidirectional safe named
       arrivals, stable collision, readable sparse furniture, small wall stage,
       dedicated warm procedural tileset, and normal camera/audio behavior
       (sessions 54/58)
2. [x] Restrained tavern occupants, including the lanky green stage musician,
       plus barkeep cheese hook toward the pantry door, with the sole cheese on
       an impossible sky island and no inventory or progression state
       (sessions 55/58)
3. [x] Compact pantry room + normal/Astral/teal-sky floor language, connected
       safe route, storage dressing, and local Astral retry (session 56)
4. [x] Reused Astral fall death + distinct successful sky fall preserving
       Sanity and handing off to an input-free cutscene scene (session 57)
5. [x] Dedicated circa-1994 falling-to-Chult cutscene: deliberately long cloud
       descent, canopy collision, jungle impact, Astral return, cigarette drag,
       held non-playable Phase 4 handoff point, and a delayed high-intensity
       procedural action cue that resolves after impact (sessions 60-61)
