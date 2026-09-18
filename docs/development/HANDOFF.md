# Agent Handoff

<!-- Read the Baton. Do not read the rest of this file to start a task.
     Deeper history is in HANDOFF-ARCHIVE.md. See TWO-AGENT-GIT-WORKFLOW.md. -->

## Baton

- **Latest pass (Codex):** GitHub Pages release infrastructure on top of
  `aeb1db4`. The Pygbag build now creates `.nojekyll`; the Pages workflow
  builds and deploys `main`; root and browser READMEs name the future public
  URL and the one-time Pages setting. The live repository and owner were
  confirmed, and this checkout's `origin` now uses `RtRutabaga/CHUCK-game`.
- **Browser verification:** rebuilt artifact opens at 16:9 and a title-screen
  load of `KMW9-J6ZP-2T5D` reaches the expected temple checkpoint. Generated
  archive: 11,401,293 bytes; static output: 22,562,567 bytes including the
  archive and loose template files. Full opening-to-sewer traversal remains
  the release playtest boundary.
- **Suite:** 1,300 passed in one combined pytest process after correcting the
  cafe/hatch interaction overlap and an older test that deleted Chult's `$`
  transition marker from shared state. Browser runtime checks are 7/7.
- **CONTINUE and the save file are gone.** The twelve-character code is
  the whole save system, on desktop and in a browser alike. Sean's
  decision; reasoning in `DECISIONS.md`. Do not reintroduce either, and
  **do not build browser save persistence** — `WEB-BUILD.md` §4.1 is
  cancelled.
- **Branch / base:** `save-codes`, base `a000690`.
- **What changed:** `SaveSystem`, `save2.json` and `default_save_path`
  are removed; `src/systems/save.py` keeps only `SaveRecord`, which the
  codec is written from. `checkpoints.write_save` is now `save_here` —
  it banks the save point and hands back the record to make a code of,
  and writes nothing. `settings.json` has its own path in
  `settings.default_settings_path()`, the same location as before, so a
  player's existing volume and fullscreen survive.
- **`spoken` is session memory now.** People Chuck has met introduce
  themselves again after a resume. It needed a positional key and never
  fit in twelve characters. Cosmetic, and accepted.
- **Sanity likewise:** a resumed game starts at `SANITY_START`. Codes
  stay twelve characters; do not widen the format to carry it.
- **Tests:** the file round trips became code round trips. Where a test
  asserted an exact sanity after resuming it now asserts
  `config.SANITY_START`, because the old assertion described something
  the game can no longer do.
- **Next bounded task:** remove release-only developer checkpoints, merge this
  branch to `main`, select **Settings → Pages → Source → GitHub Actions**, and
  run the workflow. Then cold-load the public URL and play title → docks →
  sewer → one transition before announcing it.
- **Preview:** `python -m http.server 8000 --bind 127.0.0.1 --directory
  chuck/chuck/build/browser-app/build/web`, then `http://127.0.0.1:8000/`
  in a fresh tab. Never `localhost`. Check for a server already running
  before starting or killing one — Sean may be playing.

---

## Recent Passes

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
