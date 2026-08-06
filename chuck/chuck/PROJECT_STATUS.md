# CHUCK — Project Status

Updated: Phase 9's thirteenth and final map, the Twilight Crossroads, brings
the complete Feywild route to a stable boundary before the later wizard tower.
This file is required by the project rules and updated every session.

## Current state

- Phase 8 is complete. Five connected playable Phlegethos maps lead through the fortress
  approach: Arrival, Lava Road, Lava Lake, Rubble Pass, and Fortress Approach.
- The new 64x34 Rubble Pass sits between the Lava Lake and Fortress and turns
  the route west-to-east. A broad paved lane winds through 127 pieces of dark
  basalt-and-ember rubble, crosses a narrow two-tile lava river on an intact
  slab, and passes a 48x96 cliff-fed lava fall. One slow lemure starts beyond
  notice range at the west end; one slow horned devil remains optional beyond
  notice range from the required route. The map has its own Ashtray,
  development checkpoint `Phlegethos 4`, three breakable carton urns, and
  uninterrupted Phlegethos music. The fortress is now displayed as
  `Phlegethos 5`; its stable persisted checkpoint IDs are unchanged.
- The Rubble Pass's east exit no longer borrows a misaligned temple arch. A
  three-tile-tall infernal wall cleft is centered on the paved approach, and
  every visible dark doorway cell is the actual transition trigger. The
  cliff-fed lava fall now cycles through four procedural ribbon, highlight,
  and impact frames. In the fortress tableau, the wizard stands clear to the
  east of the enlarged Pit Fiend rather than being hidden behind its 128px
  sprite.
- The complete Phase 8 enemy set is present: lemures, fire snakes, spined
  devils, flameskulls, and horned devils, all built as variants or extensions
  of established enemy/hazard systems.
- Seventeen temple-style breakable urns are distributed across all five
  Phlegethos maps: three each in Arrival and Lava Road, four on the Lava
  Lake's two safe shores, three in the Rubble Pass, and four around the
  Fortress yard. They reuse the
  exact temple scratch/shatter/reset lifecycle and each drops the established
  20-cigarette carton. Placements stay off required routes, stepping stones,
  checkpoints, and the fortress battle aisle.
- The fortress yard now shows the returning fighter, wizard, and ranger
  actively battling a massive 128x128 Pit Fiend, now more than four times a
  human enemy's sprite height. A Phlegethos-specific choreographer
  reuses the shared battle projectile path: the ranger aims at the fiend, the
  wizard fires bolt fans, the fighter holds lesser devils, and the fiend
  returns fire. Automatic entry dialogue establishes that the trio is trying
  to repair the spreading fractures.
- Road and Lake Ashtray marker IDs now match the checkpoint registry. Their
  previous mismatch crashed on activation; regression coverage now validates
  every authored Phase 8 Ashtray against a saveable same-map definition.
- Entering the upper fortress yard now triggers escalating Astral corruption:
  a continuous two-row band cuts off retreat, then three timed jagged waves
  advance from the arena's sides. They use the exact animated Astral fall
  tiles, never materialize under Chuck, preserve a broad central route through
  the complete climax, and restore completely on death/reset.
- Ten hard-edged Feywild river fragments begin flowing west through staggered
  arena lanes after the third Astral wave. Six seconds later, eighteen more
  blocks align into a continuous arena-height surge and sweep west, making
  river contact inevitable while Astral tiles remain easy to route around.
  Walking or jumping into any river block now starts Chuck's shared
  shrink-and-sink fall animation; after the animation completes, Sanity is
  preserved and the dedicated input-free river cutscene begins.
- The Phase 8 ending is complete. It opens fully black and slowly reveals a
  35-second river journey suspended between collided worlds. Basalt banks give
  way to dense enchanted growth, luminous spiral plants, glowing flowers,
  mushrooms, saturated violet/cyan accents, oversized roots, and vibrant
  vegetation. Chuck remains clearly visible in the current through the longer
  rush and waterfall, enters calmer water, then visibly washes out prone onto
  the bank. He lies still, slowly pushes himself upright, and stands before the
  final black fade. The scene reuses the established fall soundtrack and
  carries Sanity across the fortress handoff.
- The detached horizontal foam stroke that appeared beside Chuck as he washed
  onto the Feywild bank has been removed; the river and shoreline animation
  otherwise remain unchanged.
- By direct instruction, the final black now resolves into the first playable
  Feywild area: a 52x36 enemy-free riverbank. Chuck wakes beside the broad
  animated teal river, reaches the nearby `Feywild Ashtray`, and follows a
  winding, branching path through dense enchanted growth toward an inert
  deeper-Feywild boundary. A dedicated procedural tileset and reusable tree,
  luminous spiral-plant, and mushroom props carry the cutscene's cyan,
  emerald, violet, and pink visual language into normal top-down play.
- `Feywild 1` uses the shared checkpoint loader and development selector;
  `feywild_reached` is the only new durable progression flag. Loading directly
  or arriving from the cutscene preserves the normal checkpoint/Sanity
  architecture, and the map-local Ashtray is the sole save/respawn point.
  Phase 9 is now specified in `docs/development/PHASE-9.md` as a thirteen-map
  Feywild region: the existing riverbank plus twelve new maps built around
  reactive flower switches, slowing pollen, Chuck-sized passages, and a
  Feywild-specific enemy scale.
- `Feywild 2` (Blooming Path) is now a connected 60x42, enemy-free enchanted
  clearing with one Ashtray, two cigarette-grass tufts, dense
  oversized vegetation, and valid paths both back to the Riverbank and toward
  the inert Map 3 boundary. Its shared development checkpoint and map-local
  save checkpoint both use the existing checkpoint loader.
- The first reusable reactive-flower group is live. Chuck scratches the
  central flower with the normal attack; it pulses before three authored
  vegetation cells retract and three others close, swapping a winding upper
  route for a direct lower route. The change is reversible, waits if Chuck
  occupies a target cell, cannot strand him in either authored state, and
  resets on death, map reload, or Continue rather than expanding the save
  format. One grass tuft now grows immediately beside this first flower; a
  casual scratch aimed between them prioritizes the flower, providing a
  natural accidental demonstration while leaving the grass reward intact.
- `Feywild 3` (Pollen Orchard) is a connected 62x46 enemy-free map with five
  shallow pollen beds, winding orchard lanes, one Ashtray, an optional
  cigarette-grass pocket, and an inert Rootways boundary. Its reversible
  flower exchanges a long eastern detour for a direct middle lane while both
  configurations preserve all required routes.
- Slowing pollen is implemented as a reusable immediate terrain effect rather
  than a status system. Animated low flowers and drifting gold, pink, and cyan
  motes visibly mark the walkable terrain. Grounded contact applies one
  consistent 0.48 movement multiplier; leaving restores full speed, jumping
  remains unaffected, and pollen never damages Sanity or behaves as a fall
  hazard. `Feywild 3` and its Ashtray use the shared checkpoint loader.
- Every current Feywild transition threshold now uses Chult's actual boundary
  structure: a contiguous three-tile wilderness mouth cut through the outer
  map edge, reached by a visible trail. Cardinal enchanted leaves, vines, and
  saturated accents render overhead while all three cells use the established
  walk-transition terrain. No between-map exit remains as a single opening
  embedded inside the vegetation field.
- The Feywild now has its own 99-second regional soundtrack at 116 BPM. Its
  recurring syncopated mallet hook, elastic scooped bass, hand percussion,
  woody reed answers, restrained reverse-bell swells, and F Mixolydian harmony
  make it catchy and funky while retaining mysterious enchanted color.
  Later peaks use only isolated echo accents, reserve reed answers for
  contrasting sections, and avoid added bass/percussion fills so the hook
  remains clear rather than becoming cluttered or disharmonious.
  All thirteen Feywild maps request the same seamless loop, so the
  existing audio deduplication keeps it playing through map transitions,
  checkpoint respawns, and reloads without layering or restarting.
- `Feywild 4` (Rootways) is a connected 68x46 east-west forest floor divided
  by giant knotted root masses. Two restrained, gnome-sized redcaps pursue
  Chuck across the broad exposed route, deal 18 Sanity contact damage, and
  take six scratches to defeat, making escape the practical response without
  turning either encounter into a combat gate.
- Reusable low root gaps are ordinary walkable overhead terrain for one-foot
  Chuck but extra-solid terrain for larger pursuers. Redcaps visibly stop at
  the mouth instead of disappearing or teleporting; one gap opens a protected
  refuge and the other is the sole entrance to an optional cigarette-grass
  cache. Rootways has exactly one physical Ashtray, a shared `Feywild 4`
  development checkpoint, reversible travel to Pollen Orchard and Giant Tea
  Table, and the uninterrupted regional soundtrack.
- `Feywild 5` (Giant Tea Table) is a 72x52 enemy-free north-to-south
  exploration respite. A colossal solid tabletop, room-sized plates and cups,
  spilled tea, crumbs, napkins, six chair-leg columns, and four immense table
  legs make Chuck's one-foot scale architectural rather than decorative.
- The required route cannot simply walk around the furniture: dense growth
  closes both side aisles, sending Chuck beneath the table's heavy apron and
  across its cool shadow before the southern clearing. Under-table and apron
  terrain extend the shared large-actor passage rule, while an optional root
  pocket hides one of four cigarette-grass rewards. Two reachable place
  settings offer only the restrained lines `Still warm.` and `Set for one.`
  The map has one physical Ashtray, shared `Feywild 5` development entry,
  Chult-style three-cell edge openings, reversible Rootways and Needle Garden
  travel, and uninterrupted Feywild music.
- `Feywild 6` (Needle Garden) is a 72x50 timing-focused flower maze. Four
  rooted spitting orchids face authored cardinal lanes, remain stationary,
  swell and flash through three readable native-scale frames, then launch hard
  seeds that stop against solid terrain and cost 14 Sanity on contact.
- The opening orchid fires across a broad, safe observation chamber. Later
  orchids occupy narrower flowerbed corridors on evenly staggered cadences;
  the final horizontal/vertical crossing has a lower bypass that replaces
  projectile pressure with the already-established slowing pollen. The
  Ashtray approach never intersects a firing lane. The map has two optional
  cigarette-grass rewards, one physical Ashtray, shared `Feywild 6`
  development entry, reversible Giant Tea Table travel, and uninterrupted
  Feywild music. Its east edge now carries on into the Moonmoth Fen.
- `Feywild 7` (Moonmoth Fen) is a 62x40 wetland of small safe islands strung
  across impassable deep water. Every gap is exactly one tile of the jumpable
  `≈` channel — given new `fey_channel` art here — so each crossing is a single
  committed hop and the fen cannot be walked; two branch islands hang off the
  main chain.
- Lantern moths are the flameskull hazard as living Feywild wildlife: the same
  weaving, unscratchable, 14-Sanity contact behaviour behind a new luminous
  moth sprite with a pale blue wing trail. They haunt fixed horizontal and
  vertical lines out over the deep water, so a crossing means timing the moth
  and the hop together. No landing tile moves. The map has an optional northern
  side island with a cigarette-grass cache, one physical Ashtray, shared
  `Feywild 7` development entry, reversible Needle Garden travel, and
  uninterrupted Feywild music. Its east edge continues into the Warrens.
- `Feywild 8` (Redcap Warrens) is a 76x50 camp map, the region's strongest
  ordinary-enemy area. Four redcaps hold a clearing of gnome-sized gear ---
  kicked-off boots, a cooking cauldron, planted sickles Chuck walks under,
  and crude hide shelters --- standing on trampled camp-dirt terrain so it
  reads as lived-in ground rather than a room. Their notice zones sit more
  than two notice ranges apart, so pursuit never becomes a mob.
- A northern game trail crosses the full width of the map outside every
  notice zone: the warrens are passable without a single fight, while the
  camp centre stays genuinely contested. Solid toadstool thicket walls the
  trail off from the camp, and two Chuck-only openings --- one root arch and
  a pair of toadstool caps --- join them and guard the two cigarette caches.
  No redcap can follow through either.
- Thorn mites are the rat role as fey wildlife: tiny, patrolling, cleared by
  one committed scratch, behind a new burr-shaped sprite. The map has one
  physical Ashtray, shared `Feywild 8` development entry, reversible Moonmoth
  Fen travel, and uninterrupted Feywild music. Its east edge continues into
  the Shifting Hedge.
- `Feywild 9` (Shifting Hedge) is a 68x44 ring corridor around a great hedge,
  gated at its four corners. Two gates start open and two start shut. Four
  reactive-flower groups each open one doorway and close another, and every
  group is its own reciprocal, so a second scratch always undoes the first.
  The hedge is fixed and inspectable, never randomised.
- Its two guarantees are proved by walking the entire state space --- every
  tile in all sixteen group combinations. Neither the exit nor the optional
  pocket can be reached without the flowers, and from every state Chuck can
  reach, the exit is still reachable, so no order of scratches can strand
  him. Changes still refuse to land under Chuck, and Sanity-zero restores the
  authored opening state. The map has two cigarette caches in the pocket,
  four thorn mites and no larger enemies, one physical Ashtray, shared
  `Feywild 9` development entry, reversible Redcap Warrens travel, and
  uninterrupted Feywild music. Its east edge continues into the meadow.
- `Feywild 10` (Displacer Meadow) is a 74x48 massive-creature encounter. The
  displacer beast reuses the Chult colossus wholesale behind a new sprite: a
  six-legged blue-black panther with barbed tentacles over its shoulders and
  a faint after-image offset from its real body. It holds the middle of a
  meandering, wholly exposed route thick with slowing pollen, starting far
  enough from the arrival to be seen before it is met.
- The answer is never to fight it. Three walled pockets and four loose root
  arches are built to Chuck's scale: he walks under them and the beast stops
  at the mouth. The Ashtray sits in a pocket a large-actor flood proves the
  beast can never enter, more than a notice range from its haunt, so
  respawning never drops Chuck inside it. The map has two cigarette caches,
  three thorn mites, no redcaps, shared `Feywild 10` development entry,
  reversible Shifting Hedge travel, and uninterrupted Feywild music. Its
  east edge continues into the Underways.
- `Feywild 11` (Mushroom Underways) is a 70x46 recovery map with two new
  terrains: canopy shade, ordinary walkable ground drawn dark and drifting
  with spores, and luminous pools, which are solid so they shape a clearing
  without standing in the way. One rhythm repeats four times --- a long dim
  run under a giant cap, then an open clearing with a pool --- so the walk
  feels like weather rather than a corridor.
- Nothing here pursues Chuck, and that is enforced: no hostile spawn of any
  kind, every enemy list empty at runtime, and a full minute standing still
  costs no Sanity. Between a third and two thirds of everything reachable is
  under a cap, so neither shade nor open ground takes over. The map has three
  quiet side chambers, six fungal tufts holding cigarettes, one physical
  Ashtray under the third canopy, shared `Feywild 11` development entry,
  reversible Displacer Meadow travel, and uninterrupted Feywild music. Its
  east edge continues into the rapids.
- `Feywild 12` (Luminous Rapids) is a 78x44 traversal synthesis with four new
  terrains: fast bright water no one crosses, static wet stepping stones, and
  giant lily pads in risen and furled states. Three crossings run in teaching
  order --- static stones and one-tile jumps first, then two twin pad chains
  where a flower raises one and sinks the other. Each chain fits on one
  screen, so no required landing is offscreen.
- The reactive-flower controller gained a small companion table,
  `GROUP_TERRAIN`, so a group can declare what its change writes. These
  flowers raise and sink pads instead of paving a river with path tiles; the
  default vegetation behaviour is unchanged everywhere else.
- The lower flower is the crossing: a state-space walk with the jump rule
  built in proves the exit cannot be walked to, cannot be jumped to either,
  and that from every reachable state the exit is still reachable. The upper
  flower gates only the north ledge's cache. Pollen thickens approaches and
  never touches a landing tile or a gap; three lantern moths patrol the
  water; one spitting orchid sits on the optional ledge. The map has two
  cigarette caches, one physical Ashtray on the middle isle, shared
  `Feywild 12` development entry, reversible Mushroom Underways travel, a
  connected Map 13 edge, and uninterrupted Feywild music.
- `Feywild 13` (Twilight Crossroads) completes the Phase 9 region with a 76x52
  twilight clearing and several ordinary-looking trails whose connections are
  geographically wrong: leaving the Rapids eastward arrives from the south.
  One reversible flower closes a harmless northern decoy while opening the
  western route, a pollen-heavy direct line offers a slower shortcut, and a
  two-mouth low-root shortcut protects an optional cigarette cache from the
  restrained lone redcap. Five thorn mites provide light wildlife pressure
  without making the route a combat gate.
- The map has one physical Ashtray, shared `Feywild 13` development entry,
  save/Continue and Sanity-zero reset through the existing checkpoint loader,
  and reversible travel to the Luminous Rapids. Its three-cell western
  wilderness opening is deliberately inert: it is the stable boundary for a
  later floating-wizard-tower phase, with no cutscene, tower map, boss, or new
  region transition implemented here. Phase 9's authored content is complete;
  the next pass is the full thirteen-map human acceptance playtest and any
  narrowly evidenced polish it reveals.

## Working systems

- Game loop, native 320x180 surface integer-scaled 4x, scene stack
  with overlay support (dialogue draws over the frozen world)
- Startup now hands off from the one-frame BootScene to a native 320x180 title
  menu. NEW GAME clears the single save slot and loads the authored Waterdeep
  opening; CONTINUE is visibly disabled unless a valid current-version save can
  be restored. A config-gated DEV CHECKPOINTS option opens the temporary test
  selector and disappears entirely when `ENABLE_DEV_CHECKPOINT_SELECTOR` is
  false. The selector pages in twelve-slot screenfuls (session 125): the
  page follows the up/down caret, left/right leap a whole page with
  wraparound, side arrows mark further pages, and a PAGE X OF Y label
  shows the position
- Input: keys -> named actions, normalized 8-way movement vector
- Text maps (assets/maps/): terrain legend + marker system (spawns and
  objects declare their under-terrain); loud errors on any bad data
- Swept, axis-separated tile collision (no tunneling at any dt)
- Smooth frame-rate-independent follow camera, clamped to map bounds
- Sprites from text grids (tools/): Chuck (idle/walk x4 facings), the
  cat, eight human NPCs, and the 75-glyph 5x9 pixel font
- Sanity with i-frames; cigarette pickups; HUD meter (a cigarette
  burning down); patrolling cat hazard; Astral Anchor checkpoints;
  quiet vanish -> starfield -> respawn (no game-over screen, ever); enemies
  rebuild from their map markers when Chuck returns
- Checkpoints and saving: one registry defines map, position/named arrival,
  facing, required progression flags, and visibility/save rules. NEW GAME,
  CONTINUE, and the development selector all call the same
  `CheckpointLoader.load_checkpoint(checkpoint_id)` path. Map-entry definitions
  retain the established local retry behavior; the 29 authored Ashtrays have
  stable IDs and save on first contact. A small version-1 JSON slot under the
  user's application-data folder stores only checkpoint ID, current Sanity, and
  durable progression flags. Invalid, missing, outdated, unknown, or forged
  development-only checkpoint saves disable CONTINUE without crashing. Durable
  flags are `sewer_completed`, which restores the tavern's open exterior,
  `chult_reached`, which restores the playable Chult state,
  `feywild_reached`, which restores the first Feywild riverbank, and
  `crew_pirate_met`, which preserves the first/repeat pirate conversation;
  `captain_chest_opened` preserves the captain chest's opened art and later
  confrontation gate, while `captain_chest_carton_collected` prevents its
  physical golden 40-cigarette carton from duplicating after collection
- Dialogue: JSON data files, typewriter box, eight NPCs; choice
  options can speak, navigate, or close silently
- Audio: pure-stdlib engine (src/audio: synth, instruments,
  sequencer), offline rendering (tools/generate_audio.py +
  tools/generate_music.py <name>), AudioSystem with graceful no-device
  fallback; five composed pieces (data/music/, 7-10 voices) —
  the 95s warm Waterdeep Docks theme and the 83s eerie/funky D-minor
  Sewer theme loop seamlessly, while the 36s one-shot fall-to-Chult cue drives
  the Phase 3 cutscene. Chult now has an original 86s D-Dorian exploration loop:
  a persistent syncopated deep-bass hook, pitched hand drums, woody offbeats,
  layered retro percussion, a compact plucked melody, flute answers, and a humid
  breakdown. It enters immediately on either cutscene arrival or Chult 1 load.
  The Phase 6 entrance hall switches to an original 80s temple loop built from
  low drones, uneven hand drums, dry wood clicks, sparse bells, and restrained
  Phrygian-colored flute phrases. Its sustained voices are mastered to match
  the Chult theme's perceived in-game strength. After direct playtest found the
  matched-RMS mix still too restrained, the temple render alone now uses 0.98
  peak headroom instead of the soundtrack default 0.75 (raised again in
  session 124);
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
  pantry.png, chult.png, temple.png, and feywild.png
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
- Vine-exit readability (playtest, session 109): every hanging-vine jungle
  exit now shows Map 1's worn-trail approach so it reads as "head this way" —
  a short beaten-trail strip before the Chult 2 north exit (one clear row;
  the thorn maze sits directly beneath), the Chult 3 log-crawl approach
  corridor, and the Chult 4 north exit (whose canopy also widened from one
  vine tile to the full five-tile gap). Trail terrain is walkable like the
  ground it replaced, so no route, thorn, grass, or enemy data changed. New
  exits should include a trail approach from the start
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
- Phase 5 raptor territory: exactly two large 44x30 Chultan raptors occupy the
  broad central Map 2 clearing, well north of the cog. Their two-frame run,
  30x15 footprint, 68 px/s pursuit, 152-pixel notice radius, and 25-Sanity
  contact make them substantially larger, faster, and more dangerous than the
  prior undead. They are over three Chuck-widths across and more than twice his
  sprite height; Chuck's 80 px/s movement and the clearing's wide side routes
  still leave a narrow, reliable escape advantage. Ten scratches can defeat
  one, but no route or progression state requires either kill. They use shared collision,
  scratch, Sanity/i-frame, painter-order, and enemy-respawn behavior
- Phase 5 massive dinosaur: one 72x60 tyrannosaur-like creature stands alone
  in Map 2's broad northern clearing, separated from the two fast raptors. Its
  reference-informed silhouette uses a huge blunt green head, yellow eyes,
  olive dorsal plates and belly, tiny forearms, heavy legs, and pale square
  claws. A 48x24 footprint reinforces its scale while its 14 px/s pursuit is
  slower than a zombie. Contact costs 40 Sanity and twenty scratches can defeat
  it, but the wide clearing preserves a route around its body and no progression
  state requires combat. It reuses collision, scratch, i-frames, painter order,
  and enemy reset after Chuck's return
- Chult Map 2 now has one physical Ashtray south of the cog. Its hidden
  `chult_2_anchor` save definition is distinct from the development-visible
  `Chult 2` map entry but uses the same registry and loader. Contact saves,
  CONTINUE restores the Ashtray position, and Sanity-zero return rebuilds both
  raptors there. The durable decision log now records one physical checkpoint
  for each newly authored gameplay map
- Phase 5 thorn maze and Chult Map 3 handoff: Map 2's former open northern tip
  is now a compact maze built entirely from established dense-jungle collision
  and 136 existing thorn-hazard tiles. A single southern entrance commits Chuck
  to a substantially longer winding route with multiple safe loops, many branching
  choices, and dangerous thorn-cut shortcuts. A fully thorn-free solution
  remains available without a minimap or unavoidable damage. The
  canopy-framed north threshold transitions to `chult_run` through the ordinary
  walk-exit and named-arrival architecture
- Chult Map 3 undead run: the 48x36 exterior starts quietly at its southern
  Ashtray, then releases three finite groups of 6, 8, and 10 existing zombies
  and skeletons as Chuck advances north. All 24 enemies originate beneath
  flanking canopy arches rather than appearing in open ground, open directly
  onto ordinary notice range of the lane, and funnel into three broad evasion
  spaces. Groups
  release only once, no kill gate exists, and Astral return rebuilds the quiet
  pre-run state. Six reusable grass tufts continue the exterior-Chult convention.
  `Chult 3` remains development-visible through the shared loader; its separate
  physical Ashtray still saves, restores through CONTINUE, and becomes the
  Sanity-zero return point
- Chult Map 3 now ends in a six-tile low passage that Chuck can traverse but
  human-sized undead treat as solid. It leads through the ordinary named walk
  transition into the 64x56 `chult_respite` map without deleting pursuers or
  requiring combat
- Phase 5 Chult Map 4 jungle respite: a mostly calm, lower-pressure exterior
  with dense vegetation masses, 295 authored tree/shrub decorations, a fully
  authored winding route, sixteen shared cigarette-grass tufts, and one
  physical Ashtray. `Chult 4`
  uses the shared development/save loader; the northern Map 5 temple boundary
  is authored but deliberately inert until the next session
- Chult Map 4 stream crossing: a continuous 68-tile animated water ribbon
  winds from the west map edge to the east edge and splits the route into two
  banks. Ordinary movement stops at the water; Chuck's established committed
  jump clears the one-tile crossing. It adds no swimming, drowning, new input,
  tutorial, enemy, or alternate endpoint bypass
- Chult Map 4 northern clearing now contains exactly one reused massive slow
  dinosaur at the open end of the route. Its existing scale, 14 px/s pursuit,
  twenty-scratch durability, 40-Sanity contact, and checkpoint reset remain
  unchanged; the clearing and alternate approach preserve a route around it
- Phase 5 Chult Map 5 temple exterior: a 64x48 enemy-free approach centers a
  huge five-tier stepped pyramid, 42 tiles wide at its base, with 468 solid
  weathered masonry tiles, a six-tile-wide walkable stair, moss/vine variation,
  and a dark readable entrance. Eight grass tufts continue the Chult exterior
  convention. Map 4 now enters its named southern arrival; `Chult 5` and its
  one physical Ashtray use the shared loader/save/respawn path. The entrance
  now hands off into the first Phase 6 interior through a safe named arrival
- Temple approach dressing: four matched pairs of reusable 12x30 skull stakes
  line the path immediately before the pyramid staircase. Their solid native
  footprints preserve an eight-tile central corridor and normal painter order;
  they are mute environmental storytelling rather than enemies or interactables
- Phase 6 Temple Map 1: the former exterior boundary now enters a dedicated
  48x37 monumental entrance hall and can be crossed back without transition
  bounce. Weathered floor slabs, mossy/glyph-marked solid masonry, sparse
  structural piers, and dark thresholds establish a distinct interior visual
  language at native scale. Five matched pairs of animated wall torches now
  establish the recurring temple lighting language. The room is deliberately
  enemy- and trap-free; its
  north doorway is the stable inert boundary for the next dungeon slice.
  `Temple 1` is development-visible, while the room's single physical Ashtray
  saves, restores through CONTINUE, and receives Sanity-zero returns through
  the existing shared checkpoint architecture
- Phase 6 Temple Map 2: the entrance hall's former inert north threshold now
  enters a reversible 48x44 stone corridor without transition bounce or music
  restart. Five full-width rows of large pale spikes divide the route into six
  safe landings. Five durable skeletons occupy alternating landings while
  fourteen animated wall torches reinforce the long, narrow connector shape.
  Spike terrain is solid during ordinary movement and ignored
  only by Chuck's existing committed jump, so each band requires SPACE without
  adding new input, damage, fall, or tutorial systems. The map uses only five
  existing durable skeletons,
  contains exactly one physical Ashtray, exposes `Temple 2` through the shared
  development/checkpoint loader, and connects north to Temple Map 3
- Phase 6 Temple Map 3: a reversible 56x44 chamber continues the temple without
  restarting its music. Twelve existing human-scale skeletons occupy spaced side
  lanes around monumental masonry piers; a connected route still reaches the
  west boundary while reserving a three-by-three avoidance envelope around
  every enemy, so combat is possible but never a progression gate. Twelve
  animated wall torches frame the room, and the former north exit now turns
  west to break the dungeon's straight-line rhythm. The map
  contains exactly one physical Ashtray, exposes `Temple 3` through the shared
  development/checkpoint loader, rebuilds all twelve enemies on Sanity-zero
  return, and turns west into Temple Map 4
- Phase 6 Temple Map 4: a reversible 72x24 west-running connector alternates
  the open skeleton chamber with a long, narrow trap passage. Eight reusable
  wall launchers fire staggered vertical darts through visible timing lanes;
  darts travel faster than Chuck, deal 15 Sanity through normal i-frames, and
  disappear against masonry or after a hit. Eleven animated torches and eight
  dark wall apertures remain visible together at native 320x180. The room is
  enemy-free, contains exactly one physical Ashtray, exposes `Temple 4` through
  the shared loader, resets all active darts on Sanity-zero return, preserves
  uninterrupted temple music, and enters the next open room through its west
  threshold
- Phase 6 Temple Map 5: a reversible 60x44 broad chamber turns the dungeon
  south after the west-running connector. Twenty compact temple snakes occupy
  open looping lanes around monumental masonry piers. They pursue only within
  a finite 96-pixel range, deal 10 Sanity through normal contact/i-frames, and
  intentionally disappear after one scratch. Eighteen animated wall torches
  carry the recurring visual language around the chamber. Combat is not a gate;
  the south threshold remains reachable through connected open space. The map
  contains exactly one physical Ashtray, exposes `Temple 5` through the shared
  loader, rebuilds all snakes on Sanity-zero return, preserves uninterrupted
  temple music, and enters the next narrow map through its south threshold
- Processional path (session 117): the entrance hall's central aisle is a
  four-wide paved walkway ('≡', a new walkable two-variant temple terrain —
  smoother slabs a shade lighter than the floor, with rare worn gold
  flecks) running unbroken from the exterior door to the deeper gate. The
  aisle's three markers (arrivals + Ashtray) declare it as their
  under-terrain, and a test asserts the path spans every aisle row.
  Session 119 extended the language: a short centered stub of the same
  path sits before every other temple doorway (3-wide by up to 3 deep,
  shaped to each door's approach — single-row lanes at the side doors of
  the corridor maps, 2 deep at the snake chamber's south door where a
  snake spawn bounds it). Where a door's approach is a narrow lane (the
  skeleton chamber's west door, the dart corridor's west door), the path
  fills the whole lane and blooms into a full three-tall landing at its
  mouth into the open room; the dart corridor's fully-open east door
  carries a complete 3x3 stub (session 120). Door arrivals/anchors inside
  a stub declare the path as their under-terrain (Ι φ Λ Ρ Η Μ Ζ Σ Ξ), and
  a test locks the per-map path counts (18/23/21/15/18). One Astral scatter cell moved one
  leg south, out of the wind map's east-door stub, preserving the
  36-cell scatter contract and the walk-and-hop course invariant
- Guardian monuments (sessions 115-117, reference-directed): twenty-seven large
  ziggurat statues (48x64 props, two alternating weathering variants each —
  stepped tiers, thin green painted bands, gold diamond plaques, a tiny base
  stair) stand in dense aligned rows through every map with open space: ten
  lining the entrance hall's aisle, five on the spike corridor's landings
  (opposite each landing's skeleton), six in the skeleton chamber's side
  lanes, two between the dart corridor's timing lanes (placed strictly in
  the dart-free columns so no lane gains cover), and four in the snake
  chamber. Only the Astral wind connector stays undressed — its five-wide
  winding passage has no open space to fill. Two faces share the frame: the pale carved skull ('Ϙ'
  anchors) and a coiled serpent with gold-glint eyes and forked tongue ('Ϟ'
  anchors); rows alternate skull/serpent, and the snake chamber's guardians
  are all serpents — its statues match its inhabitants. Each stands on a
  3x2 solid footprint of temple wall cells with the anchor at bottom-center
  carrying the y-sorted prop. Placement was assertion-validated (plain-floor
  footprints, clearance rings free of spawns/thresholds/hazards, full
  connectivity and the entrance's walkable minimum re-verified per statue)
  and a dedicated test locks the per-kind counts, footprints, and row
  formations
- Deeper-door facade (session 114, reference-directed): Temple Map 1's north
  threshold is now a monumental composition — an 80x48 temple_gate prop
  (stepped corbelled crown, tall dark opening, flanking pillars, moss, gold
  diamond glyphs) spanning the walkable doorway, two 28x36 carved-stone
  temple_skull reliefs flanking it on the wall (replacing that wall's two
  idols), and two freestanding pedestal braziers ('ø': a new animated
  two-frame tileset terrain like the wall torch, solid on the floor)
  burning before it. The gate tile ('£', under '∇') transitions exactly as
  the arch char it replaced. The broad chambers carry the language onward:
  skull pairs + braziers on the skeleton chamber's north wall, braziers
  beside the snake chamber's serpent idols
- Temple thresholds: all twelve entrances/exits across Temple Maps 1-6 now use
  narrowed three-tile openings centered beneath reusable procedural stone arch
  props. North/south arches are 48x38 and east/west arches are 38x48, both
  taller than a human NPC and enormous beside Chuck. Continuous dark doorway
  ground replaces the old repeated vertical-frame pattern while the existing
  transition terrain and safe named arrivals remain authoritative. East/west
  arch chars anchor on the BOTTOM row of their three-row openings (props draw
  upward from their tile's bottom edge, so a 48px side arch spans its opening
  exactly from there; a middle-row anchor sits one tile too high — playtest
  caught exactly that misalignment in session 108)
- Phase 6 Temple Map 6: a reversible 48x60 connector winds through four major
  direction changes in a five-tile-wide passage. Eight full-width, one-tile
  Astral Sea cuts require Chuck's established committed jump; stepping onto
  them reuses the quiet Astral fall and checkpoint-return behavior. Session
  118 scattered 36 additional single Astral blocks through the legs — a
  broken-reality fracture that doubles as a harder jump slalom. No scatter
  cell touches a mandatory cut cardinally (nothing widens past the
  ~2.3-tile committed jump), and a permanent test walks the whole course
  with single-tile hops only, proving every safe cell reachable and the
  east boundary attainable. Twenty-seven
  animated wall torches trace the winding route. The enemy-free map contains
  exactly one physical Ashtray, exposes `Temple 6` through the shared loader,
  preserves uninterrupted temple music, returns safely to Map 5, and holds an
  inert east boundary for the next broad room
- Temple interior dressing: all six temple maps carry the game's established
  style-add-on language (the docks' three-quarter buildings, walls/gates, and
  market stall; the jungle's cog, trees, and shrubs) translated into ancient
  temple pieces — coiled serpent idols (26x44, gold-eyed, taller than a human
  NPC), rounded glyph stelae (20x34), terracotta urns (14x18: whole, cracked,
  toppled), and low fallen column drums (24x16). All are mute, y-sorted
  procedural props from tools/generate_temple_props.py with stable positional
  variants. Wall pieces ('†','‡','¦') keep the wall's solidity against its
  face, so no route, torch count, spike band, or dart lane changed; floor
  pieces ('¢','¬') occupy single tiles in the broad rooms only, and a
  dedicated suite locks the per-map placement counts and re-verifies every
  arrival-to-boundary route
- Pantry jar shelves are scratch-breakables (session 112): the two Waterdeep
  pantry shelves build as PantryJarShelf entities. The furniture stands
  forever — solid, human-scale — but one scratch rattles its JARS down into
  glazed ceramic shards and spills a cigarette carton (the same 20-count
  CigaretteCarton the temple urns use). The emptied shelf keeps drawing with
  a dedicated bare sprite (pantry_shelf_empty.png). The scene picks each
  carton's drop tile because only the map knows which neighboring board is
  safe: the left shelf stands directly above an Astral fall tile, so its
  carton lands one tile aside. Shelves restock on reload. The pantry's four
  round floor jars (the 'z' vessels, session 113) are breakables too:
  PantryJar subclasses the temple urn's lifecycle with crockery-toned
  shards — one scratch shatters the jar, clears its tile to open board,
  and spills a carton where it stood
- Temple urns are scratch-breakables (session 110): all 26 dressed urns build
  as living BreakableUrn entities (same positions/variants; idols, stelae,
  and columns stay static). One scratch shatters one urn into terracotta
  shards and spills a full cigarette carton — a new pickup worth exactly
  CARTON_CIGARETTE_COUNT (20) cigarettes (config comment marks the number
  as the contract for the future cigarette counter; sanity simply clamps at
  full today). Wall-base urns spill onto the floor tile beneath them; a
  broken urn's tile clears to its under-terrain through the new
  TileMap.clear_tile, so floor urns open for walking while wall tiles stay
  wall. Urns and tiles rebuild on checkpoint reload like every enemy

- Phase 6 Temple Map 8 (session 122): `temple_gauntlet`, a reversible 40x52
  L-shaped connector where the temple's defenses concentrate — a narrow
  vertical climb crossed by three full-width spike bands with skeletons on
  the landings and a skull/serpent monument pair, turning west into a
  five-tall dart corridor (two down + two up launchers in the dart-free
  pattern) seeded with three single Astral cells. A permanent test proves
  the whole run completable with walking plus single-tile hops. Full kit:
  arches on both doors, paved stubs, braziers at the west boundary (inert
  until Map 9), nine torches, two carton urns, stelae, a fallen column, and
  one shared-loader Ashtray (`Temple 8`). Map 7's north boundary is live
  both ways
- Cigarette counter (session 128): Chuck's coin counter. A CigaretteLedger
  on Game accumulates every cigarette ever collected — loose pickups bank
  one, cartons bank exactly CARTON_CIGARETTE_COUNT (20), settling the
  contract carried since session 110. The total survives map walks and
  Astral respawns (coins surviving a lost life), persists in the save slot
  as a tolerant new field (pre-counter saves stay valid and resume with
  zero; forged/negative totals invalidate the save), restores on CONTINUE,
  and resets only with NEW GAME. Session 129 fixed the fall-to-Chult
  handoff zeroing the count (load_checkpoint now carries the running total
  forward; only NEW GAME and CONTINUE set it explicitly) and added death
  rewind: entering a map or attuning an Ashtray commits the total, and the
  quiet Astral respawn rolls back to the committed value — cigarettes
  gathered past the checkpoint are lost with Chuck. The HUD shows the
  count quietly top-right: a tiny cigarette pictogram beside xN in the
  pixel font, opposite the sanity cigarette. No spending exists yet — the
  ledger only accumulates
- Enemies respect fall hazards (session 127): a shared
  collision.FALL_HAZARD_TERRAIN set ('V', '♠', 's') is extra-solid for
  every pursuing enemy — undead, snakes, raptors, the massive dinosaur,
  and the cat all treat spike pits, Astral cells, and the pantry sky as
  walls, since only Chuck has fall choreography. Skeletons stop flush at
  a band's edge instead of strolling across (verified in the gauntlet:
  20 seconds of pursuit never crosses the row-42 band). Rats keep their
  spawn-validated fixed patrols
- Fall centering (session 126): a fall begins the moment Chuck's
  footprint center crosses a hazard tile, which used to leave his sprite
  mostly over the safe neighbor when entering from the north or a side —
  the sink read as dropping into ordinary ground. The choreography now
  glides him onto the triggering tile's center over the fall's first 40%
  (control is already locked), so he always visibly drops INTO the hole
  from every approach direction, for Astral, spikes, and the pantry sky
  alike. A test enters a cut from the side and asserts the mid-fall
  centering
- Spike pits are fall hazards (session 124): '♠' is walkable now and
  classifies as the exact Astral fall — lethal underfoot with the same
  quiet vanish and checkpoint return, safe only under the committed jump.
  The spike corridor's and gauntlet's bands, and every future pit, share
  one hazard family with the wrong-map material. Tests updated to the new
  contract: walking onto a band is possible-but-death (fall kind
  asserted), safe on-foot floods treat spikes as blocked, and the jump
  suite verifies the hop still clears a band onto safe floor
- Astral wind spike trial (session 124): eighteen spike cells joined Map
  6's course — a mixed spike/Astral trench across the entry chamber (the
  hop lands beside the Ashtray), a full-width band between the final cut
  and the east leg, and nine singles threaded through the leg slaloms.
  The walk-and-hop invariant now spans both hazard kinds: every safe cell
  reachable, the east boundary attainable, single hops only
- Temple loudness (session 124): playtest asked for the temple louder
  again — its render now uses 0.98 peak headroom (RMS ratio vs Chult
  ~1.33; the music suite's band moved to 1.25-1.45 and the temple's peak
  gate to 0.99)
- Shrine hall winding rework (session 123): 150 interior wall cells grow
  two spines out of the shrine hall's monument columns, transforming the
  open room into a wound route — the west entry is forced south through
  the west chamber past its six skeletons, a south gap opens directly at
  the Ashtray, and the central aisle (walled both sides, guardian statues
  embedded in the spines) runs back north to the exit. The east chamber
  becomes an optional pocket entered through a north gap. The envelope
  invariant still holds: entry -> Ashtray -> boundary remains walkable
  with 3x3 avoidance envelopes around every skeleton blocked
- The Astral breach (session 133): once Chuck walks west of
  BREACH_TRIGGER_COL (28) — into sight of the battle — the Astral Sea
  breaks through the sanctum floor behind him (AstralBreach in
  src/entities/battle_hazards.py): a two-tile-thick north-south band of
  'V' terrain at BREACH_COLS (32, 33), landing instantly across the
  rows nearest Chuck so it cannot be outrun, then cascading to the
  walls with a per-tile flash and the vanish sfx. The band is lethal to
  walk into, unjumpable at two tiles, and uncrossable by enemies —
  there is no returning to the east door; the player is sealed in line
  of sight of the fight. A tile never breaks through under Chuck (it
  waits for him to step off). Built on the new TileMap.set_terrain
  runtime mutator; _reset_enemies() restores every mutated tile and
  re-arms the trigger, so death (including falling into the seal)
  heals the floor with the rest of the room. Twenty-four more skeletons
  (Ψ) line the sealed chamber's north and south fringes in two
  staggered rows each (rows 5/7 and 40/42, west of the seal), sparing
  the central sight-line to the beholder and trio: at 7-tile notice
  range they lie dormant until Chuck flees a wall to escape the eye
  rays, then rouse and herd him back to center — 27 skeletons in all
- The beholder boss-battle soundtrack (session 136): the sanctum now
  gets its own climactic theme (AREA_MUSIC["temple_sanctum"] =
  boss_battle.wav) instead of the ambient temple loop. data/music/
  boss_battle.py: an original 80s loop in D Phrygian at 144 BPM, 48 bars,
  11 voices. A relentless choral ostinato (the new ins.choir voice)
  grinds the Phrygian flat-second Eb against a pounding octave bass and
  orchestral timpani (new ins.timpani), while a horn section (new
  ins.brass) soars the theatrical melody over the B section and the coda
  — SNES boss-battle drive with a Duel-of-the-Fates processional menace,
  built from the temple's own D/Eb/C modal world. Dynamic arc: drive →
  soaring B → a dark timpani-roll build → full return → climactic
  turnaround, seamless (loop seam 0.000), rendered at 0.95 headroom to
  match the loud temple/jungle mixes. Three reusable instrument voices
  added to src/audio/instruments.py; tests in test_music.py
- Ship compartment with portholes (sessions 147-148): the playable ship_deck
  (26x13) is an internal wooden hull compartment with brass portholes onto
  the sunlit wavy sea — matching the escape
  cutscene. A dedicated ship tileset (tools/generate_ship_tileset.py ->
  ship.png; tileset_layout.SHIP; MAP_TILESET["ship_deck"]="ship") draws
  plank floor, timber hull wall, and an animated 4-frame porthole tile
  ('Ø', solid) whose sky/sea/crest colours are the cutscene's exact
  palette and whose frames roll the wave crests. Session 148 confined the
  windows to the north hull, added human-scale doors to the side walls, and
  moved Chuck's safe cutscene arrival to tile 13,9 above the new lower-hold
  ladder. This replaced the original plain docks-tileset room/open water band
- Phase 7 opening + lower hold (session 148): the arrival compartment now
  keeps its four animated sea portholes exclusively on the north hull. Its
  west/east walls carry three-cell-tall dark open doorway recesses and the
  south wall carries a 3x2 opening, reserving future interior routes without
  implying that Chuck can operate full-sized doors. A southern floor ladder
  connects
  reversibly to the new 40x30 ship_lower_hold. The hold reuses pantry shelf
  and jar silhouettes alongside crates and barrels; session 150 routed all
  eight shelves and floor jars through the pantry's existing scratch-break,
  debris, tile-clearing, reload-restock, and 20-cigarette-carton lifecycle.
  It houses sixteen ordinary scratchable rats, continues ship_shanty.wav without a
  restart, and owns one physical shared-loader Ashtray plus development-
  visible `Ship Hold`. The user-supplied `docs/design/pirate ship.png` is
  reserved as the composition reference for the later exterior deck map
- Clean cutscene porthole waves (session 150): the Phase 6 escape tableau keeps
  its animated undulating crest/shadow lines but no longer adds four isolated
  white sun-glitter dots inside each porthole
- Walk-in crevice prompt (session 146): the rubble "Enter crevice?"
  YES/NO no longer needs the interact key — walking into the crevice
  zone pops it. ChoiceTrigger gains a walk_triggered flag (a _WALK_TRIGGERS
  set; "crevice"); WorldScene checks walk-triggered zones each frame
  after movement and pushes the choice on entry, with a _walk_choice_armed
  flag that only re-arms once Chuck leaves the zone (so a "NO" isn't
  re-asked while he stands there). Walk-triggered choices are excluded
  from the interact-range check, so the crevice is purely walk-driven
  while the sewer grate keeps its interact prompt
- The ship's pirate theme (sessions 144-145): the escape cutscene and
  the ship deck (the Phase 7 doorstep) share ship_shanty.wav
  (data/music/ship_shanty.py) instead of the borrowed docks loop. Built
  from the docks' fast D-centred groove but turned dark and piratical:
  D MINOR at 126 BPM, 40 bars (~76s), 11 voices. A plucked-fiddle tune
  hammers the classic minor pirate loop (i-bVI-bVII: Dm-Bb-C) and, in
  the turns, the descending Andalusian cadence (Dm-C-Bb-A) with a
  raised-seventh C# for swashbuckler menace; a galloping root-fifth
  bass and bodhran drive it; bold accordion horns (brass), a tin
  whistle, and a gruff crew (choir) chant along in the second half.
  Renders at 0.9 headroom, seamless (seam 0.000), RMS 0.175.
  AREA_MUSIC["ship_deck"] and the cutscene's SEA_MUSIC both play it.
  Tests lock in the minor tonality (F natural, no F#, C# cadence)
- Chaotic collapsed rubble (session 143): the big-block debris was made
  to look like the roof caved in, not tile in rows. temple_rubble_block
  is now 12 variants — each draws one or two chunks at a random offset
  and tumble-rotation (±24°) within a 44x36 canvas (rubble_block seeds a
  per-variant RNG; _stone_chunk lit from above so tilts still read).
  Since props anchor bottom-center per tile, the off-centre chunks break
  the grid alignment, and the per-tile variant index scatters the
  angles. The generator now places debris in irregular collapse-piles
  (a base scatter plus a bonus near ~14 collapse centres) so it heaps up
  in patches and thins between, rather than an even field
- Rubble map rebuilt from big broken blocks (session 142): a new
  temple_rubble_block prop (four chunky 3/4-view broken-masonry sprites,
  tools/generate_temple_props.py rubble_block(); tile 'ß', solid, under
  '·') is now the rubble map's dominant debris. The generator fills the
  chamber with a dense field of these big blocks (~360) plus a scatter
  of smaller column drums (~45) for scale, and the torches, cracked
  stelae, and flat wall-tile boulders were all removed — so it reads as
  one consistent field of collapsed masonry with the clean paved lane
  threading through. temple_column is unchanged, so the temple dressing
  maps are untouched. Rubble test locks in blocks-dominate and no-torches
- Crevice prompt + wordless porthole cutscene (session 141): the rubble
  exit is now an "Enter crevice?" YES/NO interaction (data/choices/
  temple_rubble.json; ChoiceTrigger "crevice"; marker Ҏ on the lane just
  above the ∇ mouth) rather than a walk-over exit — YES routes the goto
  ship_deck through the escape cutscene (intercepted in WorldScene's
  _pending_map handler), NO closes. The escape cutscene lost its
  narration captions (it plays wordlessly), and its emergence tableau
  was rebuilt: a sunlit, lighter-blue sea seen through three round
  brass-rimmed portholes set in the ship's wooden hull wall — plainly a
  ship interior, the sea framed in circles rather than an open breach.
  Suite: test_phase6_escape_cutscene.py (wordless), plus the crevice/
  crawl tests updated to the choice flow
- The escape cutscene (session 140): the Phase 6 -> 7 boundary. Stepping
  onto the rubble crawlspace now replaces the world with
  EscapeCutsceneScene (src/scenes/escape_cutscene_scene.py, a contained
  input-free Scene like FallingCutsceneScene): Chuck crawls a tight stone
  tunnel toward a growing blade of daylight (receding stone rings +
  vignette + scrape sfx), a whiteout, then he emerges into the wooden
  hold with the open sea beyond the hull breach as the sea theme
  (waterdeep_docks.wav) swells in. Three narration captions land the
  moment ("Daylight, at last." / "Salt air..." / "Chuck has reached a
  ship. He does not yet know it."), then it fades and hands off to the
  playable ship deck via load_checkpoint, carrying his Sanity across.
  Suite: test_phase6_escape_cutscene.py; the ship-deck crawl test now
  goes through the cutscene. Phase 6 is content-complete but for its
  distinct boss/cutscene-music polish and Phase 7 gameplay
- The rubble collapse (session 139): temple_rubble was rebuilt to look
  like the temple's ceiling has caved in. The chamber is now choked with
  ~460 pieces of fallen-stone debris (toppled columns '¬' and cracked
  stelae '‡' props scattered at ~58% density off the route, plus lone
  '█' boulders) and split by 15 distinct blocks of Astral Sea (~213 'V'
  cells), making it almost impassable off the path. One intact paved
  lane ('≡', the temple's processional tile — arrival/ashtray unders
  changed to '≡') winds torch-lit from the from_fireball arrival, past
  the ashtray, to the crawlspace mouth: against the debris it reads
  unmistakably as the way out. Generator (tools/generate_temple_rubble.py)
  still asserts the lane connects arrival → anchor → crawlspace on foot
- The rubble crawlspace + the ship deck (session 138): the rubble now
  has its one way out. A narrow crawlspace mouth ('∇') is carved into
  temple_rubble's south wall at the foot of a clear right-side lane
  (tools/generate_temple_rubble.py now protects the lane and proves the
  mouth reachable on foot). Walking onto it (AREA_WALK_EXITS
  ["temple_rubble","∇"]) leads to the new ship_deck map: a 30x18 wooden
  hold (docks tileset — planks, cargo crates/barrels) with a breach in
  the hull opening onto the open sea (water), the Phase 6 → 7 boundary.
  Chuck arrives at the crawl mouth in the deck floor (from_crawlspace)
  and can walk up to the sea reveal. New markers Ҋ/Ҍ; checkpoints
  "Ship 1" (runtime) + "Ship Ashtray"; sea theme (waterdeep_docks.wav).
  No onward exit yet — the escape cutscene (crawl choreography, light,
  the reveal beat) is the follow-up. Suites: test_phase6_ship_deck.py
- The Fireball argument (session 137): the cast is now preceded by a
  dialogue beat. When the survival clock runs out, the camera cuts to the
  battle (reusing the entrance establishing focus) and the adventurers
  argue over the ordinary dialogue box — "you can't cast that here!" /
  "we're too close to an astral rip" / "I have to try" / "......" /
  "FIREBALL!!" (data/dialogue/temple_sanctum.json "fireball_cast").
  Only when the line closes does _begin_fireball fire the blast
  (WorldScene._fireball_dialogue_shown / _fireball_after_dialogue, reset
  with the room). Tested in test_phase6_fireball.py
- The scripted Fireball + the rubble map (session 135): the sanctum
  fight now ends. Once Chuck is sealed in (the breach triggered) and has
  survived BATTLE_FIREBALL_DELAY (24s), the wizard casts Fireball — a
  scripted phase (WorldScene._begin_fireball/_update_fireball/
  _draw_fireball) that freezes the world, blooms an orange-white
  explosion from the wizard into a white-out, shakes the screen
  (FIREBALL_SHAKE) and booms a new deep fireball sfx
  (tools/generate_audio.py sfx_fireball), cuts Chuck to at most half his
  Sanity (FIREBALL_SANITY_FRACTION, never healing), and throws him into
  the new temple_rubble map (fade-in, via the _pending_map path with a
  new _pending_fade_in flag). The survival clock resets with the room, so
  dying before it lands simply restarts the wait. temple_rubble
  (tools/generate_temple_rubble.py, 48x30): a collapsed chamber of 154
  Astral Sea blocks around a clear central spine from the from_fireball
  arrival to the rubble ashtray; temple art/music; new markers Ѣ/Ѥ;
  checkpoints "Rubble 1" (runtime, dev-visible) + "Rubble Ashtray". No
  onward exit yet — the crawlspace and escape cutscene are later slices.
  Suites: test_phase6_fireball.py (6), test_phase6_temple_rubble.py (5)
- Battle chaos (session 134): the sanctum fight was made genuinely
  overwhelming. BattleProjectile now carries a free velocity vector, and
  the ranger whirls (BattleActor.spin, drawn as a rotating sprite;
  BATTLE_RANGER_SPIN_SPEED) loosing a rotating fan of arrows whose aim
  advances BATTLE_ARROW_SPIN_STEP each fast beat — arrows spray every
  compass direction, filling the room. The wizard hurls a westward
  BATTLE_BOLT_FAN of bolts far more often. Rays fire faster. New
  BeholderCone: the beholder occasionally charges a telegraphed wedge of
  force east across the hall (BATTLE_CONE_* — 0.9s pulsing telegraph,
  0.4s lethal window, 216px range leaving an eastern refuge), and on
  detonation the camera shakes (Camera.shake / .offset jitter, decaying
  at CAMERA_SHAKE_DECAY) and a new deep beholder_blast sfx booms
  (tools/generate_audio.py sfx_beholder_blast). BattleChoreographer.update
  now returns a BattleTick(projectiles, cones); the scene tracks
  battle_cones (damage via cone.contains, drawn as a translucent wedge),
  and both reset with the room. Suite: 8 new/expanded tests in
  test_phase6_sanctum_battle.py (19 total)
- The entrance establishing shot (session 133): entering the sanctum
  from the gauntlet queues the heroes' three lines at the far-east door,
  ~40 tiles from the battle. The camera now cuts to the fight for those
  lines (Camera.focus_on holds a fixed point while the dialogue freezes
  the world) so they land on the trio, not the empty aisle, then hard-
  cuts back to Chuck when the conversation closes
  (WorldScene._battle_establishing_focus centers on the actors' span and
  lifts their feet clear of the dialogue panel; SANCTUM_ESTABLISH_LIFT).
  The trio was reclustered into a tight arc around the beholder — ranger
  (18,20), fighter (16,22), wizard (19,25), beholder (10,23) — so all
  four frame in one shot; the ranger and wizard were the old vertical
  outliers (rows 15 and 26). The aisle path (138 ≡) is untouched
- The battle in motion (session 132): the sanctum tableau now fights on
  fixed cadences Chuck cannot influence (src/entities/battle_hazards.py).
  The beholder's eye rays cycle the three adventurers' lanes in a
  learnable order and dissipate at BATTLE_RAY_RANGE (320px), keeping the
  arrival aisle survivable; the ranger's arrows and the wizard's bolts
  streak west at the beholder and die on the west wall; the fighter's
  slash pulses west of him where three new skeletons (ordinary Ψ
  markers, the room's only conventional enemies) press his line. Every
  attack is a BattleProjectile or slash zone that costs Sanity through
  the ordinary i-frame path; the shot is spent on impact. The
  BattleChoreographer rebuilds with _reset_enemies(), so death restarts
  the cadences and re-presses the skeletons. Actors animate in place:
  the beholder's hover breathes on a sine, adventurers sway on offset
  phases, and each actor lunges toward its target for a beat
  (attack_flash) when its attack fires. Suite:
  tests/test_phase6_sanctum_battle.py (7 tests)
- Battle tableau, first slice (session 131): four procedural actors hold
  the sanctum's western arena as static y-sorted presences — the armored
  fighter (16x30, sword and shield), the blue-robed wizard (gem staff),
  the clearly female ranger (long auburn ponytail, longbow), and the
  beholder (40x40, five eye stalks, one vast glaring eye, floating on a
  hover offset over a ground shadow). Entering from the gauntlet plays
  three heroic non-interactive entrance lines (data/dialogue/
  temple_sanctum.json) through the ordinary dialogue box before control
  returns. The actors answer nothing: E gets no response, scratches pass
  through them, their identities are never explained (phase contract).
  Combat behavior, attacks, and the Fireball are the next slices
- Phase 6 Temple Map 9 (session 130): `temple_sanctum`, the final chamber
  structurally — the temple's widest hall (64x48, 2032 walkable tiles). A
  138-cell paved processional runs from the east door (the room's ONLY
  threshold; per the phase contract the scripted Fireball, a later slice,
  is the only way onward) between eight alternating guardian colonnade
  monuments to the western dais, where carved wall skulls and six braziers
  stage the coming battle. Fourteen torches, three carton urns, four
  stelae, two fallen columns, one Ashtray (`Temple 9`), reversible
  east-door transitions with the gauntlet (whose west boundary is now
  live), and deliberately no enemies and no onward exit — the
  adventurers/beholder battle and Fireball are their own next slices
- Phase 6 Temple Map 7 (session 121): a reversible 56x44 shrine hall east
  of the Astral wind connector, entered through a west-wall arch onto a
  full-width paved landing. Twelve avoidable skeletons occupy the side
  lanes (a permanent test proves every tile reachable even with 3x3
  avoidance envelopes around all of them); four skull and four serpent
  guardian monuments flank the aisle to the north door, which carries the
  full threshold kit — arch, path stub, flanking braziers and carved
  skulls — and stays inert until Map 8. Breakable urns, stelae, a fallen
  column, twelve torches, one physical Ashtray (`Temple 7` via the shared
  loader), uninterrupted temple music, and both-ways transitions with
  Map 6 (whose formerly inert east boundary is now live)
- Phase 4 dense vegetation art: the former blocky green collision texture is
  now an interlocked organic canopy of broad leaves, woody seams, and hanging
  vines. Across the same solid vegetation cells, deterministic y-sorted
  tree props use three 34x46 silhouettes with layered tropical crowns, trunks,
  and trailing vines. A second solid vegetation decoration adds broad-leaf
  shrubs across the same masses using three 28x24 variants: overlapping pointed
  leaves, central veins, and brighter tropical midtones. Trees rise above human
  NPC height while shrubs are wider than two Chucks, making each collision mass
  read as dense forest and understory without changing a walkable tile or route
- Jungle densification (session 111): all five Chult exteriors gained new
  organic vegetation blobs (~8-10% of each map's plain open ground — 576 new
  cells total: 172/211/29/69/65) so the jungle presses closer around the
  routes. New masses use the same canopy terrain studded with trees and shrubs
  at the established session-73 density. Placement was generated under strict
  guards: 2-tile buffers around every spawn/marker/special terrain, full
  walkable connectivity (the stream treated as jump-crossable) re-verified
  after every blob, the undead run's central lane excluded, the respite's
  bank-size minimums held, and the cog's raptor-notice-radius bypass route
  preserved. The Chult 1 tree/shrub test band widened (150-240/160-240) to
  cover the larger mass area

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

80 standalone suites (most pure Python/headless) cover the shared engine and
content from Waterdeep through the complete thirteen-map Feywild region. The
Phase 9 coverage includes every map transition and development checkpoint,
reactive-flower state and reset guarantees, pollen, Chuck-only passage
blocking, enemy roles and reset, save/Continue/respawn, uninterrupted music,
and the inert final boundary. All 80 pass, compilation is clean, and the dummy
SDL launch reaches `TitleScene` after the boot frame.

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

Run the Phase 9 full regional acceptance playtest from `Feywild 1` through
`Feywild 13`, then load each development checkpoint individually. Keep any
follow-up strictly to issues observed during that playtest; do not begin the
floating wizard tower without its own phase document.

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
       Added Map 2's single physical shared-loader Ashtray (session 86), then
       enlarged the raptors and increased pursuit speed (session 87).
   - [x] Added one reference-informed massive but slower dinosaur in the broad
         northern clearing, with optional combat and normal reset (session 88).
6. [x] Added a compact branching thorn maze with a safe solution, transitioned
       it into a connected Chult Map 3 staging foundation, and added Map 3's
       shared development entry and one physical Ashtray (session 89). Increased
       the maze to 136 thorns, one entrance, a longer route, and more difficult
       loops and wrong turns after playtesting (session 90).
7. [x] Added three increasing, finite undead releases from readable jungle
       openings, preserving a run-through route, ordinary combat, and complete
       encounter reset at the Chult 3 checkpoint (session 91), then expanded
       the authored groups to 6/8/10 undead after playtesting (session 92).
8. [x] Added a six-tile Chuck-sized escape that blocks human-sized undead, then
       transitioned into a lower-pressure 64x56 Chult Map 4 with dense
       vegetation, a deliberately meandering route, sixteen grass tufts, no
       enemies, one physical Ashtray, and shared `Chult 4` development loading
       (session 93).
   - [x] Added a map-spanning animated jungle stream with one required jump
         crossing, using the existing jump/collision behavior (session 94).
   - [x] Added one existing massive slow dinosaur to the broad northern
         clearing while preserving an optional route around it (session 95).
9. [x] Added the 64x48 Chult Map 5 exterior with a dominant five-tier stepped
       pyramid, broad walkable stair, dark inert dungeon boundary, eight grass
       tufts, no enemies, shared `Chult 5` development loading, and one physical
       Ashtray. Connected Map 4 through its existing named boundary without
       beginning the dungeon (session 96).
   - [x] Lined the pre-stair approach with eight reusable, human-scale skull
         stakes while preserving the broad central route (session 97).

## Phase 6 progress (jungle temple)

1. [x] Added the Phase 6 contract and made it the active development scope.
2. [x] Connected the Map 5 pyramid entrance to a reversible 48x37 Temple Map 1
       entrance hall with dedicated procedural interior art, one physical
       shared-loader Ashtray, development-visible `Temple 1`, and an original
       80-second ancient/shamanic exploration loop (session 98).
3. [x] Added a reversible 48x44 Temple Map 2 with five mandatory one-tile
       spike-pit jumps, five skeletons on alternating landings, fourteen wall
       torches, dedicated temple art, uninterrupted temple music, one
       physical shared-loader Ashtray, development-visible `Temple 2`, and a
       north boundary leading into the next room (session 101).
4. [x] Added a reversible 56x44 Temple Map 3 with twelve durable skeletons in
       avoidable side lanes, broad looping routes, twelve wall torches,
       uninterrupted temple music, one shared-loader Ashtray,
       development-visible `Temple 3`, and a west boundary entering the next
       narrow connector (sessions 102-103).
5. [x] Added a reversible 72x24 Temple Map 4 west-running connector with eight
       staggered reusable dart launchers, eleven wall torches, one physical
       shared-loader Ashtray, development-visible `Temple 4`, uninterrupted
       temple music, and a west boundary now connected to the next open room
       (session 104).
6. [x] Added a reversible 60x44 broad Temple Map 5 with twenty one-hit snakes,
       looping lanes, eighteen recurring wall torches, one physical shared-
       loader Ashtray, development-visible `Temple 5`, uninterrupted temple
       music, and an inert south boundary for the next connector (session 105).
7. [x] Reworked all Temple Map 1-6 thresholds into human-scale procedural stone
       arches over narrowed three-tile openings, then added a reversible 48x60
       Temple Map 6 winding connector with eight mandatory Astral Sea jumps,
       twenty-seven wall torches, one shared-loader Ashtray, development-visible
       `Temple 6`, and an inert east boundary (session 106).
8. [x] Dressed all six temple interiors with the established style-add-on
       language: serpent idols, glyph stelae, terracotta urns, and fallen
       column drums — 54 mute y-sorted procedural props that change no route,
       count, or hazard, locked by a dedicated test suite (session 107).
9. [x] Added the reversible 40x52 Temple Map 8 gauntlet: spike climb,
       dart corridor, Astral seeds, monument pair, full kit, one
       shared-loader Ashtray, and an inert west boundary for Map 9
       (session 122).
10. [x] Completed the multi-map dungeon, final battle, Fireball transition,
        rubble crawlspace, wordless escape cutscene, and ship arrival across
        bounded slices (sessions 130-147).

## Phase 7 progress (pirate ship)

1. [x] Added the Phase 7 contract and made it the active development scope.
2. [x] Corrected the existing arrival compartment to use four north-wall-only
       animated portholes, human-scale dark open doorway recesses on the other
       walls, and a southern floor ladder while keeping the established Phase
       7 ship theme continuous (sessions 148-149).
3. [x] Added the reversible 40x30 lower hold with pantry-derived breakable
       shelves/jars that spill 20-cigarette cartons, crates, barrels, sixteen
       ordinary rats, one physical Ashtray, and
       development-visible `Ship Hold` through the shared checkpoint loader
       (sessions 148/150). The hold rats now use the temple snakes' 96-pixel
       notice-and-chase pattern at 32 px/s, with swept wall/fall-hazard
       collision and the existing one-scratch defeat/contact-Sanity behavior.
       Sewer rats retain their established short patrols, and death/reset
       restores all sixteen hold pursuers (session 169).
4. [x] Added a reversible 40x26 working galley through the arrival room's west
       open passage, with counters and storage forming escape lanes, one
       physical Ashtray, development-visible `Ship Galley`, and uninterrupted
       shanty playback. The human-scale chef delivers the exact authored line,
       then starts a collision-aware 58 px/s cleaver chase; his two-frame
       directional run/swing animation is richer than ordinary NPCs, contact
       costs 20 Sanity, and death rebuilds and re-arms the encounter. He is
       intentionally not scratchable, keeping this an escape slice (session
       151).
5. [x] Added reversible 42x30 crew quarters through the arrival room's east
       open passage: eight hanging human bunks, an oversized round mess table,
       cargo, one physical Ashtray, development-visible `Ship Crew Quarters`,
       and uninterrupted shanty playback. The seated pirate has a restrained
       two-frame mug/sway animation and distinct first/repeat dialogue; meeting
       him sets the durable `crew_pirate_met` flag, which survives checkpoint
       save and CONTINUE. Its open captain-cabin route and deck ladder now lead
       to their completed destination maps (sessions 152-154).
6. [x] Added a reversible 36x26 captain's cabin through the crew room's open
       east doorway, with north-wall portholes, oversized human furniture, one
       physical Ashtray, development-visible `Ship Captain Cabin`, and the
       uninterrupted shanty. Its two-frame brass-bound chest grants Premium
       Buhetian Halfling Leaf (+40 cigarettes) once, switches permanently to
       an open/empty interaction, banks the paired reward against death, and
       persists both flag and count through save/CONTINUE (session 153).
7. [x] Added the reversible 64x44 exterior deck through the crew ladder, using
       the authored pirate-ship image as its composition reference: a broad
       tapered hull, two large mast-and-sail silhouettes, animated line-wave
       ocean, one physical shared-loader Ashtray, development-visible `Ship
       Exterior Deck`, and uninterrupted shanty playback. The ocean remains
       visually fixed while the complete ship/occupant layer rocks by one
       pixel over an eight-beat 126-BPM cycle; collision stays stable. The
       deck cast and ending sequence remain deliberately unbuilt (session 154).
   - [x] Enlarged both mast-and-sail props to a ship-scale 144x136 silhouette
         and aligned their anchors east-to-west along the deck's exact center
         row, replacing the small diagonal arrangement (session 155).
   - [x] Narrowed the hull's north-south beam from 30 tile rows to 22 without
         shortening it, moved the hatch/Ashtray safely inward, and enlarged
         both centerline mast-and-sail silhouettes again to 176x160 (session
         156).
   - [x] Enlarged both centerline mast-and-sail silhouettes to a deck-spanning
         224x192 and added a dedicated 120x32 east-facing bowsprit that plants
         inside the bow rail and projects over open water (session 157).
   - [x] Rebuilt the bowsprit as a massive 400x96 structural spar with over
         twelve tiles of visible projection, and moved its reinforced heel
         onto the actual eastern bow-edge rail tile (session 158).
8. [x] Populated the deck with its four non-combat performers: a concertina
       player with expanding bellows, a cheering tankard pirate, a four-step
       dancing pirate, and Jeffries visibly struggling in rope against the
       main-mast pole. Each uses four directional frames advancing on
       half-beats at the shanty's 126 BPM, distinct first/repeat dialogue, and
       a durable save flag. Jeffries delivers the authored collided-world
       warnings while the cheering pirate dismisses him. The fencing hazard
       and ending sequence remain deliberately unbuilt (session 159).
   - [x] Replaced the animated crew's full-width side-view tricorn rectangles
         with stepped crowns and narrow brims. Left/right dialogue facings now
         preserve readable eyes, noses, cheeks, and hat bands at native scale;
         the shared procedural fix covers the four performers and captain
         without changing their front/back art or interactions (session 171).
   - [x] Lifted Jeffries' rendered struggle fully onto the mast pole while
         preserving his accessible interaction tile, and added a human-scale
         procedural helm immediately sternward of the main mast (session 161).
   - [x] Corrected the helm to the masts' east-west centerline and redrew its
         wheel in a strongly foreshortened transverse plane for the ship's
         starboard three-quarter viewpoint (session 162).
9. [x] Added two human-scale sword-fighting pirates to the central deck lanes.
       Their paired controller wanders a shared midpoint while the fighters
       guard, lunge, high-parry, and recover on opposing shanty half-beats;
       swept tile collision keeps them off masts and rails. Contact costs 15
       Sanity, broad routes remain open above and below them, and ordinary
       death reset restores the complete pair. They are an avoidable hazard,
       not a combat gate or scratch target (session 160).
10. [x] Added a durable seven-condition captain gate covering the galley chef,
        seated pirate, four deck performers, and one-time chest reward. Once
        complete, the captain emerges at the midship ladder with a dedicated
        four-frame walk cycle. The camera follows his clear route north of the
        Ashtray and west to the stern helm, where the nearby concertina crewman
        turns toward him and announces `Captain on deck!`. Two restrained
        `...` dialogue beats pace his accusation, plank order, the crew's exact
        authored objection, and refusal. Completion saves at the deck Ashtray
        and CONTINUE restores the captain without replaying the exchange
        (sessions 163/170).
11. [x] Added a staged eight-tile starboard plank that replaces one rail
        section and projects as a narrow walkable strip over animated ocean.
        After the confrontation, the captain and objecting pirate flank the
        approach while Chuck begins an input-locked, normally animated
        wooden-footstep walk. The sequence no longer returns control at the
        rail: Chuck steps onto the plank, pauses for Jeffries' warning, then
        automatically walks to its outer tile and flows directly into the
        captain's approach, kick, and Hell fall. Saved confronted state still
        restores the complete tableau without replaying the procession.
   - [x] Restored the arrival compartment's unused south doorway to ordinary
         solid hull, leaving only its three real routes. Replaced the captain
         chest's direct dialogue reward with a four-frame opening action
         triggered by interact or scratch; it now drops a physical golden
         40-cigarette carton in front, banks the reward on collection, and
         restores opened/uncollected/collected states without duplication
         (session 165).
   - [x] Added reusable approach confirmations to all four live ship ladder
         directions. The hold descent and exterior-deck return ask
         `Climb down ladder?`; the hold return and crew-to-deck route ask
         `Climb up ladder?`. YES uses the existing AreaExit destination,
         named arrival, and facing; NO closes silently and stays dismissed
         until Chuck leaves and reapproaches the ladder (session 166).
   - [x] Rebuilt every ship ladder from a repeated 16x16 icon into one
         continuous 16x32 top/bottom structure, matching the established
         16x30 human NPC sprite scale. Both walkable halves share the same
         YES/NO transition, and nearby named arrivals were kept safely off
         the enlarged footprint (session 167).
12. [x] Added a deterministic moving reality field that activates when Chuck
        automatically steps onto the staged plank. Eight staggered Astral and
        volcanic Hell fragments enter from the native screen's east edge,
        travel fully clear of its west edge, and recycle continuously to sell
        the ship's forward motion. Astral chunks tile the exact animated
        `astral_void` fall-hazard cells shared by the sewer, pantry, Chult, and
        temple rather than using a separate approximation. Hell chunks now
        read as a bird's-eye plane below the ship: dark irregular basalt
        shelves cover flowing orange lava channels, angular fissures, exposed
        pools, and pinprick molten vents, with no side-facing flame edge. Their
        layouts use seed-varied row heights, staggered origins, slab sizes, and
        gaps so neighboring fragments do not align into a uniform lava grid;
        the deterministic terrain remains stable while only heat highlights
        animate. The streams render behind the hull/plank, remain non-colliding,
        and the endpoint still prevents the unbuilt kick/fall from beginning
        early. Jeffries retains his one-time `It's back! The purple is back!`
        warning (sessions 168/172/173/174).
13. [x] Completed the Phase 7 endpoint. Reaching the outer plank tile locks
        control and sends the captain along the authored plank centerline
        behind Chuck. He waits for an actual streamed Hell fragment to cross
        beneath the endpoint, extends a readable boot with impact feedback,
        and knocks Chuck into that same moving fragment while Chuck shrinks
        through the established fall animation. A dedicated input-free Nine
        Hells descent reuses the fall-to-Chult cue and its four-second music /
        29-second impact timing language, replaces clouds and jungle with
        rising volcanic fragments, sparks, and an approaching overhead
        basalt/lava plane, then holds on Chuck's arrival without granting
        gameplay control. This is the stable Phase 8 boundary; no Phase 8 map,
        mechanics, checkpoint, or narrative content was invented (session
        175).
   - [x] Added the development-only `Captain Arrival` checkpoint through the
         shared checkpoint registry/loader. It enters the exterior deck with
         all seven production prerequisites and without `captain_confronted`,
         so the ordinary gate starts the captain walk on the next update
         (session 176).
   - [x] Fixed the crew-quarters ladder crash by keeping `Captain Arrival`
         development-selectable but excluding it from ordinary named-arrival
         resolution. The ladder now resolves uniquely to the normal exterior
         deck entry, while direct development loading still starts the captain
         sequence through the same checkpoint loader (session 177).
   - [x] Enlarged all ship hammocks from 20x34 to 30x44 native pixels, then
         added a 72x44 solid captain's bed and an 80x48 central woven rug to
         the captain's cabin. The rug uses a reusable flat-prop layer so Chuck,
         furniture, and pickups always draw above it (session 178).
   - [x] Compressed only the north-south spans of the galley (40x26 -> 40x22),
         crew quarters (42x30 -> 42x24), and captain cabin (36x26 -> 36x21).
         East-west lengths, props, enemies/NPCs, ladders, open passages,
         arrivals, Ashtrays, chest behavior, and reversible routes remain
         authored; moved Ashtray checkpoint coordinates match their new rows
         (session 176).
   - [x] Removed the remaining solid near-black up-facing deck-pirate head
         patch at its procedural source and regenerated all five affected
         sheets with warm shaped head/scarf silhouettes (session 176).
   - [x] Replaced the remaining full-width rear tricorn rectangles in both
         captain/deck and seated-pirate generators with narrow peaked
         silhouettes. Up-facing performance and captain-walk frames now retain
         readable warm head/scarf pixels at 4x scale (session 179).
   - [x] Widened the staged starboard gangplank from one tile to two (16px to
         32px), including its rail opening and collision. Either lane starts
         the reality warning and endpoint sequence; the cinematic recenters
         Chuck and the captain on the broad plank before the kick. Its
         procedural tile now fills both halves without a water seam (session
         180).
   - [x] Revised the Nine Hells fall so no overhead Hell tiles appear behind
         Chuck in the street-view descent. A large distant volcano now anchors
         the open heated sky. The landing plane is over 90% basalt with sparse
         molten fissures. On impact Chuck now follows the Chult landing's exact
         quiet death timing: a `hurt` beat, vanish at 29.15 seconds through the
         same contracting Astral-star blip, respawn at 31.1 seconds through the
         same return flicker, then the established left/right/down look,
         cigarette insertion, ember, drag, and smoke before the playable
         Phlegethos handoff.

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
