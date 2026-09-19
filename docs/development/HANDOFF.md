# Agent Handoff

<!-- Read the Baton. Do not read the rest of this file to start a task.
     Deeper history is in HANDOFF-ARCHIVE.md. See TWO-AGENT-GIT-WORKFLOW.md. -->

## Baton

- **Mobile prototype, first phone build (Claude, 2026-09-19):** picked up
  Codex's touch-shell pass and shipped it. `tools/build_web.py` writes
  `build/web/mobile/index.html`, an iframe around the existing browser build
  with a landscape touch overlay (d-pad, JUMP/SCRATCH/INSPECT, pause, and a
  gear panel sizing the buttons). The existing Pages workflow uploads the
  whole `web` tree, so it publishes free at
  `https://rtrutabaga.github.io/CHUCK-game/mobile/`.
  Two things were fixed before it could work at all:
  - `#pad` and `#actions` are not `.touch`, so they were `position: static`
    and both stacked at the top-left with all three action buttons at one
    point. They now anchor to the bottom corners inside the safe-area insets.
  - The shell dispatched its synthetic `KeyboardEvent`s at the iframe's
    *window*. SDL registers `keydown`/`keyup` on the iframe's **document**
    (confirmed by reading `JSEvents.eventHandlers`), so nothing ever reached
    the game. It now dispatches on `contentDocument`, and each button carries
    an explicit `data-code`/`data-keycode` because SDL2 looks the scancode up
    from `code` -- `f` and `e` were sending `code:"f"`/`code:"e"` rather than
    `KeyF`/`KeyE`.
  Verified in-browser against the real buttons, not by hand-dispatching:
  arrows move the title cursor, INSPECT opens LOAD CODE, pause backs out.
  Same origin, so `contentDocument` stays reachable.
  **Known gap for the next pass:** LOAD CODE wants a typed twelve-character
  code and the shell offers no keyboard, so a phone can start a new game but
  cannot resume one. That is the first thing to solve -- either an on-screen
  code entry in the shell or touch-driven entry in `title_scene`.
  Sean is play-testing Waterdeep and the sewers on a phone; Codex owns the
  next mobile pass. Core game code is untouched by this commit.
- **Suite is red at 80c9749, and not from the mobile pass (Claude,
  2026-09-19):** 190 of 191 modules, four failures, all pre-existing with a
  clean tree. Three are counts left stale by the tea-table (`feywild_5`) cut:
  `test_feywild_arrival_alignment` still wants 26 reciprocal arrivals,
  `test_feywild_mushroom_dressing` still wants 10 mushroom maps, and
  `test_save_registry.test_every_entry_is_a_real_resume_point` trips on the
  retired `feywild_5` slot the cut deliberately kept -- so that test needs to
  learn about retired slots rather than the slot being removed. The fourth,
  `test_treasure_handoffs`, imports `pytest`, which is not installed in the
  local 3.14 environment and which the module runner does not support.
  Whoever picks this up owns deciding whether the suite gains pytest or that
  module drops it. Not fixed here: unrelated to the mobile shell, and the
  tea-table cut is Codex's to reconcile.

## Recent Passes

## Superseded Baton Entries

Passes that were left in the baton block rather than moved down when
they finished. Newest first.

- **NPC trailer revision (Codex, 2026-09-19):** added eight seconds of Chuck
  approaching the plaza blacksmith, interacting, reading "I don't shoe rats."
  and walking away. Dialogue stays visible 5.4 seconds. Trailer is now 46
  seconds; previous action footage and per-world audio preserved. Reviewed
  conversation frame and verified full export decode; same local MP4 path.
- **Action trailer revision (Codex, 2026-09-19):** recut to 38 seconds:
  grass destruction + cigarette pickup, sewer enemy scratch/defeat, Chult,
  urn shatter + carton collection, three spike-pit jumps, ship, Feywild, city.
  Actual game-state logs verify rewards, breakage and defeat; no gameplay
  rules changed. Local MP4 overwritten, per-area music retained, no added
  text, cabin or final encounter. Export verified by full decode.
- **Trailer revision (Codex, 2026-09-19):** per Sean, removed all added
  titles/cards and video fades. Export is now 44 seconds of gameplay with
  each scene's actual requested music and synchronized SFX. No continuous
  replacement soundtrack. Same local MP4 path; cabin/finale still excluded.
- **Trailer (Codex, 2026-09-19):** created a 49-second 1080p/30 MP4 at
  artifacts/trailer/CHUCK-gameplay-trailer.mp4 (local ignored artifact).
  tools/capture_trailer.py captures actual game-rendered frames with scripted
  movement, mixes frame-timed game SFX with fall_to_chult music, and encodes
  using optional local imageio-ffmpeg. Includes docks, Chult Falls, earlier
  temple battle, ship, Feywild and city; excludes cabin and final encounter.
  Gameplay code untouched. Capture setup and intermediates are ignored.
- **Final encounter music (Codex, 2026-09-18):** the 74-second trio cue
  was looping back to its sparse intro before the dragon's 82+ second entry.
  First dialogue now hands to desert_trio_pressure.wav, a developed-section
  loop with continuous pulse/kit, added timpani, snare pickups and brass
  through the ending. The existing dragon trigger still starts its boss cue.
  Source score and rendered WAV included; 22 music/encounter checks pass.
- **Final encounter respawn (Codex, 2026-09-18):** death now preserves the
  running trio encounter, army/siege/dragon, dialogue clock, terrain and music.
  Chuck returns at (32, 26), on protected ground beyond the west Sea's maximum
  advance, with full sanity. Collected cigarettes remain with the ongoing
  room. Other maps retain their existing reset behavior. All 34 focused final
  encounter tests pass, including repeated deaths after arena collapse and
  continued dialogue afterward.
- **Latest cut (Codex, 2026-09-18):** removed the giant tea-table map.
  Rootways now connects directly to Needle Garden in both directions using
  their existing arrival markers. Retired feywild_5 save-code slots stay
  reserved and load neighboring maps; no save registry IDs were renumbered.
  Removed the map generator and retired-map tests/dressing registrations.
- **Latest fixes (Codex, 2026-09-18):** extended the plaza smithy's west
  wing to the edge and north wall, sealing the reverse route into the guarded
  docks street while keeping southern exits open. Escape-to-ship and four
  later story cutscenes now pass existing progress flags to checkpoint loads
  so premium cartons survive. Verified five real cutscene handoffs, all plaza
  tests, and existing escape/river tests (27 passing checks total).
  Already-erased treasure flags need a player save-code repair; do not award
  optional treasure automatically to all players.
- **Correction (Codex, 2026-09-18):** Sean clarified that only the street
  north of the tavern is guarded (rows 1–7, including the previously missed
  row 7). East exits beside/south of the tavern reach the fountain plaza.
  Supersedes the full-edge block below. Controller A now jumps/backs out;
  B inspects, talks, and confirms. Y still pauses; View/Menu stay unbound.
  Verified all east exit rows in both eras; 13 plaza checks and 29
  controller/tutorial/checkpoint checks pass.
- **Publication follow-up (Codex, 2026-09-18):** the previous full dock
  boundary fix had never been committed/pushed after approval hit a usage
  limit. Verified every east exit row in both Waterdeep eras, including
  repeated updates on the exit; 32 focused tests pass. Publishing the pending
  guard fix together with the previously requested controller changes.
- **Latest pass (Codex, 2026-09-18):** reserved Xbox Menu/Start and
  View/Change View for Edge browser controls. In-game controller pause now uses
  the otherwise-unused Y button, with prompts and browser Gamepad fallback
  updated accordingly. Focused controller/tutorial checks pass (32).
- **Latest polish (Codex, 2026-09-18):** confirmed controller-aware text is
  shared by the title, Controls page, load/save footers, and tutorial hints,
  including browser Gamepad fallback input. The title's controller footer now
  explicitly reads ``D-PAD / STICK`` plus the controller-specific confirm
  button. Focused controller/title checks pass (18).
- **Latest pass (Codex, 2026-09-18):** browser SAVE GAME → COPY now uses
  ``navigator.clipboard.writeText`` instead of unavailable Pygame/SDL scrap.
  It reports ``Copied.`` on success and an honest permission fallback when a
  browser or device blocks clipboard access. Desktop copying is unchanged.
  The browser package builds and 54 focused save/code/browser tests pass.
- **Latest fix (Codex, 2026-09-18):** completed the Waterdeep guard boundary
  as specified. Every east-edge exit tile, including the lower opening, now
  gives ``Stick to the docks, rat.`` and holds Chuck on the docks after the
  dialogue closes, in both opening and finale states. The plaza remains
  available by checkpoint/code but not by walking from the docks. Focused
  Waterdeep checks pass (23).
- **Latest pass (Codex, 2026-09-18):** added a browser Gamepad API fallback
  for Xbox Edge, which can expose the controller to JavaScript while sending
  no SDL/Pygame events. Standard Xbox buttons, d-pad, and left stick now feed
  the same named actions as desktop controllers; Menu/View pause globally.
  The browser package builds successfully and the focused fallback/browser/
  checkpoint checks pass (25).
- **Latest pass (Claude Code, 2026-09-18):** finished Codex's dock pass.
  The tree is clean; `main` is pushed and Pages redeploys on push.
- **Branch / base:** `main`, base `9fc2c87`.
- **The bug in it was a decorator, not a design.** Codex's new
  `_dock_guard_boundary_hit` property was inserted directly above
  `_waterdeep_midday` and took its `@property` with it. `_waterdeep_midday`
  became a bound method, which is always truthy, so the docks were
  permanently in their returned-from-the-sewer state: `dock_worker`
  became `bobert_neighbour`, the lamps went out, the pier retinted. Four
  of the five failures were that one line.
- **The fifth was a real disagreement, resolved in Codex's favour.** The
  open tavern doorway art is 48px — three tiles — but only the centre
  tile was walkable, so Chuck caught solid facade inside the visible
  arch. `test_tilemap` asserted the sides stay solid "because Phase 2
  does not build an interior"; that reason is stale now the tavern
  interior exists, so the test was updated rather than the code.
- **Verified by behaviour, not just by tests:** walking the guarded
  upper-east edge gives "Stick to the docks, rat." and does not
  transition; the tavern threshold is three walkable tiles with solid
  facade either side and behind.
- **Suite:** 191 of 191.
- **Xbox, still open and the most useful next thing.** `?diagnostics=1`
  now logs the pad: `button N down | reached: <actions>`. Get that
  reading off the Xbox before any further controller fix. The title
  accepts `jump` as a confirm; if that is what Xbox sends, dialogue,
  the pause menu, the code field and talking in the world all need the
  same treatment — and the pause menu cannot copy it verbatim, because
  the east button is bound to both `jump` and `back` there.
- **Live:** `https://rtrutabaga.github.io/CHUCK-game/`.

---


## Latest Pass — Codex's Dock Pass, Finished (2026-09-18)

- Restored `@property` to `_waterdeep_midday`, which Codex's new
  boundary property had taken. That single line was four of the five
  failures: the docks had been stuck in their midday state.
- Kept the three-tile tavern threshold and updated the test that
  contradicted it, since the art is 48px and the stated reason for the
  old assertion no longer holds.
- Checked both behaviours in a running scene rather than trusting the
  suite: the guarded edge warns and holds, the doorway is walkable
  across its visible width and solid either side.

## Latest Pass — Xbox Confirm, and a Way to Stop Guessing (2026-09-18)

- Committed Codex's title fix: the title accepts `jump` as well as
  `interact`, so Edge on Xbox can confirm an option after moving with
  the d-pad.
- Added a gamepad reader to `?diagnostics=1`. It names the pad once and
  then reports every press as `button N down | reached: <actions>`,
  polled rather than hooked so it changes nothing about input handling.
  Four focused checks, including the Xbox case: a press that reaches
  nothing at all.
- Set aside an unfinished pass of Codex's that fails five tests, so the
  Xbox fix could ship on its own. It is back in the working tree.

## Latest Pass — Requested Gameplay Polish (2026-09-18)

- Added the opening Waterdeep pause-hint fallback and fixed numpad code input.
- Closed both old routes out of final Waterdeep, updated the sign and dock
  dialogue, and preserved the opening-era tavern/sewer behavior.
- Added the daytime arrival manhole through its generator, muted cabin seating
  examinations, and shortened the collided-desert banner examination.
- Focused regression modules and map regeneration checks pass.

## Latest Pass — The Code Is The Only Save (2026-09-18)

- Removed CONTINUE from the title and the local save file from the game.
  `SaveSystem`, `save2.json` and `default_save_path` are gone; `save.py`
  keeps `SaveRecord` alone. `write_save` became `save_here`, which banks
  the point and returns the record rather than writing anything.
- `settings.json` was deriving its path from the save file's and would
  have vanished with it. It has its own `default_settings_path()` now,
  pointing at the same place, so existing settings are kept.
- The test suite's save/relaunch round trips go through a code. Sanity
  assertions after a resume became `SANITY_START`: a code has no room
  for sanity, so the old assertions described the impossible.

## Latest Pass — Codes Become The Only Save (2026-09-18)

- Sean decided to drop CONTINUE and the local save file entirely, leaving
  the twelve-character code as the whole save system. Recorded in
  `DECISIONS.md`, with `SAVE_CODES.md` §7 and `WEB-BUILD.md` §4.1 marked.
- QUIT TO TITLE now shows the code before asking, since with no CONTINUE
  it is the only thing that survives leaving. Read-only. The no-code case
  (mid-cutscene) says so plainly. Both layouts checked by rendering them.
- The removal itself was deliberately not started: ~37 test files touch
  the file-save path, past the session-size line in the workflow doc.

## Latest Pass — Pages Blockers Answered (2026-09-18)

- Committed Codex's browser timing reporter, which its session had written
  and described in the handoff but not committed. Verified first: 3
  diagnostics checks, 6 browser-runtime checks, full suite 190 of 190.
- Served the existing local build and inspected the running context. Pygbag
  0.9.3 needs no cross-origin isolation for this game, so GitHub Pages can
  host it; `index.html` carries no absolute asset paths, so the
  `/CHUCK-game/` subpath is fine.
- Recorded that the runtime comes from a third-party CDN at play time, and
  that Claude's browser pane is unusable for timing or play-testing.
- No game code changed in this pass beyond committing Codex's.

## Latest Pass — Browser Traversal Diagnostics (2026-09-18)

- Added opt-in `?diagnostics=1` console timing samples with FPS, p95 frame
  time, and worst frame time. Hidden-tab time and scene/map changes reset the
  sample so reports do not hide stalls.
- Verified title, opening cutscene, and `waterdeep_docks` in the browser at
  approximately 60 FPS; observed p95 frame times of 17.3–17.6 ms and maxima
  below 21.5 ms in the measured samples.
- Added focused tests for timing behavior and rebuilt the browser preview.

## Latest Pass — Browser Audio Buffer (2026-09-18)

- Added browser-only buffering headroom for reported walking audio glitches.
- Desktop audio, cues and playback rules unchanged. 16 focused checks and
  both platform startup assertions pass; web build succeeds.
- Audible result awaits Sean's test in a fresh preview tab.

## Latest Pass — Browser Cutscene and Canvas Fix (2026-09-18)

- Explicitly stop the previous browser music stream before replacement,
  avoiding the hang at the opening cutscene's early music cue.
- Fixed SDL framebuffer and CSS 16:9 letterboxing; browser fullscreen stays
  with browser chrome. Build/serve both apply the presentation override.
- Live title -> full opening -> docks verified, plus movement/jump/pause
  and tall-window proportions. 71 relevant regression checks pass.
- Preview rebuilt; desktop behavior and authored content retained.

## Latest Pass — Local Browser Build Foundation (2026-09-17)

- Reconciled Codex's interrupted prototype per Claude's WEB-BUILD contract;
  committed runtime/build foundation as `c54100a`.
- Browser title launch verified; gameplay verification stopped when browser
  tooling became unavailable. Added console traceback reporting for resumption.
- Desktop checks: 1,291 across 189 modules; isolated save-path rerun required
  for one module. Build archive is 11.1 MB, plus separately fetched runtime.
- No content, controls, save format, desktop audio masters or publishing changes.

## Latest Pass — Broken Daytime Street Ends (2026-09-17)

- Branch: `save-codes`; base commit: `9edf766`.
- Replaced thin unbuilt wall caps at daytime street ends with Astral Sea:
  Day 1's north side street, Day 2's north/east streets (including Sean's
  screenshot), and Day 3's capped street/sidewalk/alley edges. Genuine
  authored building masses and the sidewalk exits remain intact.
- `finish_day_buildings` finds shallow boundary caps using the generators'
  original unbuilt-wall vocabulary, runs the existing terrace pass, then
  removes only those caps. This preserves surrounding building art seeds
  and never treats an authored building as an unfinished street end.
- Removed Day 4's isolated southern road, crossings and lower protrusion.
  A shorter paved footway with concrete edging still joins the west/east
  routes; its puddle and street furniture remain on surviving pavement.
  Updated its material validator to require the absence of stray roadway.
- All six day generators validate. All 49 checks across 11 focused modules
  pass: street ends, furnishing/parity, street furniture, sidewalk travel,
  park/Examine, and each daytime map. Native views of the road ends and the
  former southern stub were inspected. Days 5/6's shipped maps are unchanged.

## Latest Pass — Daytime Shops and Municipal Plaza (2026-09-17)

- Branch: `save-codes`; base commit: `634ede6`.
- Added twelve signless storefronts to suitable building fronts in Days
  1, 2, 3, 4 and 6 (3/2/3/3/1). Day 5 remains a building-free overpass.
  They reuse the night shops' dimensions and window vocabulary with an
  overcast daytime palette and unlettered canvas valances. Doors answer
  exactly `it's closed`; existing night signs/assets are unchanged.
- Day 1's open plaza beside the avenue now has one animated low concrete
  fountain, four park benches, four planted tubs, and a newspaper box.
  The fountain's five-by-two-tile collision follows the bowl; a clear
  pedestrian ring surrounds it. The plaza/side-street connection, pickups,
  puddles, patrol routes, and onward sidewalk exit remain accessible.
- New props have restrained Examine lines in `data/dialogue/examine.json`.
  Sprites come from `generate_city_furnishing.py`; placement is generated
  by `dress_day_storefronts` and `dress_day_park` in the shared city helpers.
  Map glyphs U+E180–U+E187 identify these props and the fountain's solid base.
- All 101 checks across 14 relevant modules pass, including actual Examine
  actions at every new object, storefront wall footprints, fountain
  collision/walkability, sidewalk exits, generator parity, the six day-map
  suites, and existing night storefronts. Native park and shop views were
  rendered and inspected. No save, progression, or transition changes.

## Latest Pass — Day-City Sidewalk Connections (2026-09-17)

- Branch: `save-codes`; base commit: `dcabdfe`.
- Removed Day 1's one-column building seam between the plaza and the north
  side street (column 53, rows 14–28), replacing it with continuous sidewalk.
- Day 1's east connection now occupies the northern sidewalk's full width.
  Day 2's south connection moves to the eastern sidewalk. Day 3's northern
  entrance has a three-column footway beside a slightly narrower building;
  its southern exit moves to the western sidewalk. Day 5's two connections
  move from traffic lanes to widened ends of the western footway.
- Day 4's already-paved north/east connections now cover their whole footway
  widths; Day 6's northern pavement entrance is five tiles wide. The roads
  beside relocated exits in Days 1–3 visibly end in Astral terrain.
- Shared furnishing helpers accept protected approach cells, used only by
  these six day-map generators, so lamps, bins, benches and signs cannot
  obstruct the exit mouths. All six shipped maps were regenerated and
  validated; named arrivals and stable checkpoint IDs are preserved.
- Corrected Day 4 → 5 arrival facing to south and Day 5 → 4 to west, matching
  the destination footways (including the Day 4 return checkpoint).
- New regression coverage checks clear pavement behind every threshold
  cell, actual travel through every cell, safe pavement arrivals, facing,
  no immediate bounce, and removal of the Day 1 seam. Also ran all six day
  map suites, city furnishing/edge checks, transitions, checkpoints and
  save registry checks. Native views of all ten connection mouths and the
  repaired plaza were rendered and inspected.

## Latest Pass — Sewer Jump Mercy (2026-09-17)

- Branch: `save-codes`; base commit: `98ab2fe`.
- Sean requested a nearby retry for the difficult Astral jump course shown
  in his screenshot. That course is `modern_city_sewer_2` in the repository
  (not the crocodile hall named `modern_city_sewer_3`).
- Deaths within course columns 10–24, rows 45–54 now return Chuck to the
  center of dry tile (12, 42), below the green sludge and before the first
  jump. The normal fall, quiet fade, enemy reset, Sanity refill, cigarette
  rollback, and death count continue unchanged.
- Mercy destinations are authored in `src/systems/respawn.py`. WorldScene
  selects a destination per death; it never moves the entrance checkpoint
  or changes a save record, registry, code, or progression flag. Deaths
  elsewhere still return to the entrance, even after a local retry.
- Regression coverage drives actual falls at every gap in the course,
  repeated retries, safe footing, unchanged entrance identity, and a later
  non-course death. The neighboring sewer, checkpoint, menu/save, hazard,
  and death-count checks were also run. The actual retry frame was rendered
  and visually inspected at native resolution.

## Latest Pass — City Storefronts (2026-09-17)

- Branch: `save-codes`; base commit: `ac5fa4d`.
- Sean requested ground-level shop graphics matching the existing city neon,
  with every door closed and answering exactly `it's closed` on Examine.
- All twelve signed locations across the six night-city maps now have a
  three-tile-wide frontage: a bottle-window bar, a cafe under OPEN, or a
  stocked convenience store under 24H. Each has inset glazing, a closed
  human-scale door, a latch, and a flush pavement threshold. Only the neon
  animates; the frontage stays still.
- Uses the existing neon prop anchors and animation registry. The generator
  now renders complete fronts into those assets, and the props reuse the
  existing `closed_door` dialogue. No map regeneration, collision, route,
  progression, save-system, or daytime-city changes.
- Validation: 98 checks across 12 focused modules passed (storefronts,
  furnishing, Examine, props, dialogue, tilemap, and all six night-city maps).
  The storefront checks exercise the actual Examine action at all twelve
  doors and verify the sprite footprint remains within solid building tiles.
  All twelve locations were rendered and visually inspected at 320x180.
- Work boundary remains scenery polish within existing maps. Phase 15 has
  no contract. Older notes below predate Claude's save-code work; consult
  `chuck/chuck/PROJECT_STATUS.md` and `SAVE_CODES.md` for the current save
  system. Ashtrays no longer exist.
