# CHUCK — Project Status

Updated: session 31 (checkpoint marker is an ashtray now). This file is required by the
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
  tools/generate_music.py), AudioSystem with graceful no-device
  fallback; the composed 95s Waterdeep Docks theme (7 voices, seamless
  loop, composition data in data/music/); SFX for pickup, interact,
  hurt, vanish, respawn, anchor chime, and per-surface footsteps
- NPC interaction covers the whole visible person (probe + overlap)
- Depth: barrels/crates are standing props (solid tiles + tall
  sprites), y-sorted with all characters by feet position
- Ground: drawn tileset (planks/stone/water/floor/wall) with stable
  per-position variants, animated water, view culling, and a flat-
  color fallback when the tileset is missing
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

## Placeholder systems
- Tavern door is solid decoration; interiors are a later phase
- (Quiet music variation cut by creative direction — soundtrack is
  Phase-One-complete)

## Known issues / accepted quirks

- SPACE and RETURN are also bound to "interact". SPACE becomes jump in
  Phase 2 item 6 — unbind it from interact then (E and RETURN remain).

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

9 suites, all pure Python (no pygame needed):
collision, tilemap, camera, animation, sanity, hazard, dialogue, audio
(`python -m tests.test_<name>` from the project root, or `pytest`).

## Phase 2 progress (starting area + sewer tutorial)

1. [x] Waterdeep guard: armored NPC at the upper plaza's east edge,
       "Stick to the docks, rat." No gate/barrier — the map layout
       already blocks (sessions 32-33)
2. [x] Tutorial text ("Press E to interact"), area-scoped, shown only
       while an interactable is in reach (session 34)
3. [x] Sewer grate + Yes/No dialogue choice: choices are data
       (data/choices/*.json), DialogueScene renders options with a
       caret, up/down selects, E commits (session 35)
4. [ ] Sewer map + tileset (stone/dirt/mud/channel)
5. [ ] Sewer music (eerie, funky)
6. [ ] Astral Sea glitch blocks + jump mechanic & tutorial
7. [ ] Rats + scratch attack & tutorial
8. [ ] Sewer exit -> climb-out -> return to docks
9. [ ] Tavern doorway opens (Phase 3 setup)

## Next recommended session

Continue playtest & polish: this size pass was the first round of
playtest-driven changes. Sean keeps playing the full loop and
reporting; we tune (speeds, damage, cigarette economy, camera feel,
volumes) and fix whatever surfaces. Phase One closes when the slice
feels right in Sean's hands.

## After that (Phase Two territory)

- A market NPC under the awning (pure data)
- Tavern interior behind the door
- 12 test suites and counting
