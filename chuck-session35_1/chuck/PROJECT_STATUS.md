# CHUCK — Project Status

Updated: session 39 (Astral interruption + jump tutorial). This file is required by the
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
  cat, the dock worker, and the 75-glyph 5x9 pixel font
- Sanity with i-frames; cigarette pickups; HUD meter (a cigarette
  burning down); patrolling cat hazard; Astral Anchor checkpoints;
  quiet vanish -> starfield -> respawn (no game-over screen, ever)
- Dialogue: JSON data files, typewriter box, one NPC (dock worker)
- Audio: pure-stdlib engine (src/audio: synth, instruments,
  sequencer), offline rendering (tools/generate_audio.py +
  tools/generate_music.py <name>), AudioSystem with graceful no-device
  fallback; two composed themes (data/music/, 7 voices, seamless loop) —
  the 95s warm Waterdeep Docks theme and the 83s eerie/funky D-minor
  Sewer theme; SFX for pickup, interact, hurt, vanish, respawn, anchor
  chime, and per-surface footsteps
- NPC interaction covers the whole visible person (probe + overlap)
- Depth: barrels/crates are standing props (solid tiles + tall
  sprites), y-sorted with all characters by feet position
- Ground: per-area drawn tilesets (tileset_layout.Tileset: a sheet +
  its terrain rows + char maps; tileset_for(map) picks one) with stable
  per-position variants, animated frames, view culling, and a flat-
  color fallback when a sheet is missing. docks.png and sewer.png so far
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
  facade + lit windows, all new tileset terrains ('r','e','t','W','m');
  building footprint and collision unchanged
- District wall: battlements/brick/banners/flickering torches
  ('w','b','F','i') with portcullis gates drawn overhead ('g');
  northern boundary wall battlemented too; footprint/gates unchanged
- District houses: the three north blocks reskinned with the tavern
  grammar + decorative house doors ('h'); solid, never accessible
- Market stall (cutaway): checkered canopy over the back rows ending
  in scalloped edge ('u') + corner posts ('P'); goods '1'-'5' (produce
  crates/table/barrel) stand visible in the open front row
- Ruined foundation ('R' walls / 'f' rubble): the mid-map block is a
  crumbling ruin with collapsed gaps; solid, style only
- Shared mathutil.approach() (camera follow + any future smoothing)
- Crash logging: unhandled exceptions write crash_log.txt
- Map transitions: WorldScene.load_map(name) (re)builds a whole area;
  a dialogue choice can carry Chuck between maps. Where a choice goes is
  data — a choice option's `goto` names the destination map (no code
  table). Each area's looping music (or deliberate silence) is data too
  (transitions.AREA_MUSIC). The grate's YES drops Chuck straight into
  the sewer, wordlessly — no confirmation lines
- Sewer: assets/maps/sewer.txt is a narrow, long, mostly-linear descent
  (walkable corridor wrapped in thick rock so it fills the view) with
  its own tileset (assets/tilesets/sewer.png, built by
  tools/generate_sewer_tileset.py): brick walls '#', stone landing ',',
  dirt 'd', mud 'M', and a drainage channel '%' that flows over 3
  frames. Its own looping theme plays on entry (data/music/sewer.py ->
  sewer.wav). A hard-edged band of animated dark-blue/purple Astral
  wrong-map material interrupts the corridor; SPACE performs a short
  committed hop that crosses it but cannot bypass normal walls. The
  nearby jump hint clears after Chuck lands beyond it. Walled off at
  the bottom (no exit yet)

## Placeholder systems
- Tavern door is solid decoration; interiors are a later phase
- (Quiet music variation cut by creative direction — soundtrack is
  Phase-One-complete)

## Known issues / accepted quirks

- E and RETURN interact; SPACE jumps. The jump is intentionally short
  and only ignores Astral-gap collision while Chuck is airborne.

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

15 suites (most pure Python/headless): collision, tilemap,
camera, animation, sanity, hazard, dialogue, audio, props, tileset,
tutorial, choice, music, transitions, jump
(`python -m tests.test_<name>` from the project root, or `pytest`).
The map-transition flow (grate YES -> sewer) is also verified
end-to-end headlessly with dummy SDL drivers.

## Phase 2 progress (starting area + sewer tutorial)

1. [x] Waterdeep guard: armored NPC at the upper plaza's east edge,
       "Stick to the docks, rat." No gate/barrier — the map layout
       already blocks (sessions 32-33)
2. [x] Tutorial text ("Press E to interact"), area-scoped, shown only
       while an interactable is in reach (session 34)
3. [x] Sewer grate + Yes/No dialogue choice: choices are data
       (data/choices/*.json), DialogueScene renders options with a
       caret, up/down selects, E commits (session 35)
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
       dark-blue/purple wrong-map tiles form a one-tile interruption;
       SPACE makes a restrained forward hop, ordinary walls remain solid,
       and the proximity hint clears after landing beyond it (session 39)
7. [ ] Rats + scratch attack & tutorial
8. [ ] Sewer exit -> climb-out -> return to docks
9. [ ] Tavern doorway opens (Phase 3 setup)

## Next recommended session

Item 7 — ordinary sewer rats + scratch attack & tutorial. Place a small
group beyond the jump, visibly smaller than Chuck, gate forward progress
until they are defeated, bind and display the real scratch control, and
keep the attack animation minimal and readable. One scratch kills one rat.

## Also open (Phase 2 / later)

- Market NPC near the red awning (pure data; Phase 2 spec)
- Rats + scratch attack (item 7)
- Sewer outflow exit -> climb-out -> return to the docks (item 8)
- Tavern doorway reads as open for Phase 3 (item 9)
