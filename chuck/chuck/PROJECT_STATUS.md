# CHUCK — Project Status

Updated: session 54 (Phase 3 tavern shell). This file is required by the
project rules and updated every session.

## Working systems

- Game loop, native 320x180 surface integer-scaled 4x, scene stack
  with overlay support (dialogue draws over the frozen world)
- Input: keys -> named actions, normalized 8-way movement vector
- Text maps (assets/maps/): terrain legend + marker system (spawns and
  objects declare their under-terrain); loud errors on any bad data
- Swept, axis-separated tile collision (no tunneling at any dt)
- Smooth frame-rate-independent follow camera, clamped to map bounds
- Sprites from text grids (tools/): Chuck (idle/walk x4 facings), the
  cat, three human NPCs, and the 75-glyph 5x9 pixel font
- Sanity with i-frames; cigarette pickups; HUD meter (a cigarette
  burning down); patrolling cat hazard; Astral Anchor checkpoints;
  quiet vanish -> starfield -> respawn (no game-over screen, ever); enemies
  rebuild from their map markers when Chuck returns
- Dialogue: JSON data files, typewriter box, three NPCs; choice
  options can speak, navigate, or close silently
- Audio: pure-stdlib engine (src/audio: synth, instruments,
  sequencer), offline rendering (tools/generate_audio.py +
  tools/generate_music.py <name>), AudioSystem with graceful no-device
  fallback; two composed themes (data/music/, 7 voices, seamless loop) —
  the 95s warm Waterdeep Docks theme and the 83s eerie/funky D-minor
  Sewer theme; SFX for pickup, interact, hurt, vanish, respawn, anchor
  chime, a quiet rounded jump bounce, scratch scrape, and per-surface footsteps
- NPC interaction covers the whole visible person (probe + overlap)
- Depth: barrels/crates are standing props (solid tiles + tall
  sprites), y-sorted with all characters by feet position
- Ground: per-area drawn tilesets (tileset_layout.Tileset: a sheet +
  its terrain rows + char maps; tileset_for(map) picks one) with stable
  per-position variants, animated frames, view culling, and a flat-
  color fallback when a sheet is missing. docks.png, sewer.png, and tavern.png
- Bobert asleep in his barrel at spawn (solid scenery, tile 'B');
  cigarette is a drawn sprite; the Astral Anchor presents as an
  ashtray (cold ash dormant / live ember + smoke when attuned), with
  rect fallbacks for headless runs
- 56x35 map: north warehouse district, tavern front (door 'D', HEROD
  sign 'H'), southeast market with awning 'a' — the overhead layer
  draws canvas over Chuck; flood-fill connectivity is a permanent test
- Prop dialogue: Bobert snores ("... Zzzzz."), the sign reads "Herod
  Cover Band - Tonight Only"; other props are mute; NPCs answer first
- Playtest sizing: human-scale tavern door (now 48x34 with hanging
  lanterns), enlarged west pier (4 rows to col 1), south pier with
  T-head, and a 48-tile market awning
- Tavern exterior: slate roof + chimney props + eave trim + tan brick
  facade + lit windows, all new tileset terrains ('r','e','t','W','m'). It
  begins with solid double doors; returning through the sewer outflow swaps
  them for a 48x34 black open threshold with lit side lanterns. Only the
  threshold tile becomes walkable; the surrounding facade remains solid
- District wall: battlements/brick/banners/flickering torches
  ('w','b','F','i') with portcullis gates drawn overhead ('g');
  both northern portcullises now occupy the upper opening row with clear
  walkable stone beneath, so they read as raised/open without changing the
  passage footprint; northern boundary wall battlemented too
- District houses: the three north blocks reskinned with the tavern
  grammar + decorative house doors ('h'); solid, never accessible
- Market stall (cutaway): checkered canopy over the back rows ending
  in scalloped edge ('u') + corner posts ('P'); goods '1'-'5' (produce
  crates/table/barrel) stand visible in the open front row. A human-scale
  market woman stands just left of the goods in a muted headscarf and apron;
  she directs Chuck toward sewer scraps without a quest or marker
- Ruined foundation ('R' walls / 'f' rubble): the mid-map block is a
  crumbling ruin with collapsed gaps; solid, style only
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
  immediate transition bounce. The room uses a dedicated warm plank-and-wall
  procedural tileset with a bar counter, three human-scale tables, chairs,
  hearth, barrels, and crates. Furniture is solid, all remaining floor is one
  connected traversal area, the camera remains on the normal WorldScene path,
  and the existing Waterdeep theme currently carries across the doorway

## Placeholder systems
- Tavern occupants, the environmental cheese hook, rear pantry route, pantry
  hazards, sky fall, and falling cutscene remain intentionally absent pending
  their bounded Phase 3 passes
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

19 suites (most pure Python/headless): collision, tilemap,
camera, animation, sanity, hazard, dialogue, audio, props, tileset,
tutorial, choice, music, transitions, jump, combat, outflow, enemy_reset,
tavern
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

## Next recommended session

Add the tavern's minimal occupants and a plainly readable environmental cheese
trail that leads toward a rear pantry entrance. Keep the cheese non-inventory
and leave pantry hazards and the Chult fall for later bounded passes.

## Also open

- Full Phase 2 human playtest and acceptance
- Dedicated tavern music or ambience (the shell currently reuses Waterdeep)
- Pantry room and three-way floor language
- Sky fall branch and falling-to-Chult cutscene

## Phase 3 progress (tavern, pantry, and fall to Chult)

1. [x] Tavern doorway transition + common-room shell: bidirectional safe named
       arrivals, stable collision, readable sparse furniture, dedicated warm
       procedural tileset, and normal camera/audio behavior (session 54)
2. [ ] Minimal tavern occupants + environmental cheese hook toward the pantry
3. [ ] Pantry room + normal/Astral/teal-sky floor navigation
4. [ ] Reused Astral fall death + distinct successful sky-fall branch
5. [ ] Dedicated circa-1994 falling-to-Chult cutscene and Phase 4 handoff point
