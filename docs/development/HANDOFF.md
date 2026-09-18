# Agent Handoff

<!-- Read the Baton. Do not read the rest of this file to start a task.
     Deeper history is in HANDOFF-ARCHIVE.md. See TWO-AGENT-GIT-WORKFLOW.md. -->

## Baton

- **Latest pass (Codex):** Sean reports glitchy audio while walking in web;
  unsure whether music or footsteps. Base `5f74abe`. Increased browser mixer
  buffer to 2048 (~93 ms at 22050 Hz); desktop remains 512 (~23 ms).
  This mitigates suspected callback starvation, not an audibly confirmed fix.
  Six browser-runtime and ten audio checks pass, plus mocked startup checks
  confirming each platform's buffer. Web preview rebuilt successfully.
  Next: Sean's listening test; if glitches persist, measure movement/frame
  stalls before expanding the change. Slightly increased SFX latency possible.

- **Branch / base commit:** `save-codes`, this browser-fix pass starts at
  `ac3199d`; previous build foundation is `c54100a`.
- **Completed:** fixed Sean's narrow/stretching browser canvas and opening
  cutscene freeze. Browser framebuffer is fixed at 1280x720, CSS fits 16:9
  with letterboxing. Desktop fullscreen UI omitted on web; web F11 never
  recreates SDL's surface. Desktop display behavior remains unchanged.
- **Freeze:** title music begins a 400 ms fade; opening music loads at 200 ms.
  Loading a replacement while that fade was pending hung the wasm renderer.
  On web only, explicitly stopping before loading resolves it. Actual browser
  ran the complete opening, arrived on docks, and accepted movement/jump/pause.
- **Verified:** 71 focused checks across browser runtime, audio, opening,
  title, pause, save menu, transitions and controller pass. Previous full
  baseline: 1,291 checks. Web geometry: framebuffer 1280x720; displayed at
  1280x720 in wide view and 800x450 in an 800x900 viewport. Override reset.
- **Build:** local files rebuilt under `chuck/chuck/build/browser-app/build/web`.
  Open `http://127.0.0.1:8000/`; close an older frozen tab and open afresh.
  Build command and limitations are in `chuck/chuck/WEB-README.md`.
- **Expensive findings:** do not use `localhost` with this runtime: Pygbag
  treated it as a runtime-development host, fetching a nonexistent local
  `/cdn/` pygame wheel. `127.0.0.1` fetched the public runtime successfully.
  Normal reload sometimes leaves the old wasm game; use a fresh tab.
- **Dirty work:** none after this pass is committed. No deployment or content
  changes. Browser audio uses the same cues and original desktop WAV masters.
- **Known limitations:** audible quality, cold-load time/FPS, full traversal,
  browser save-code round trip and other browsers are not yet verified.
  Browser file saves/settings remain temporary; use portable codes.
  Stale Feywild generators remain unrelated (see DECISIONS.md).
- **Next bounded task:** continue WEB-BUILD browser traversal/measurement,
  then persistent saves. No Pages deployment until remaining checks pass.

---

## Recent Passes

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
