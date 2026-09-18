# Agent Handoff

<!-- Read the Baton. Do not read the rest of this file to start a task.
     Deeper history is in HANDOFF-ARCHIVE.md. See TWO-AGENT-GIT-WORKFLOW.md. -->

## Baton

- **Branch / base commit:** `save-codes`, `8c3193f`.
- **In progress (Codex):** reconciling and verifying the existing browser
  prototype per `WEB-BUILD.md` step 0. Runtime/build changes are this agent's
  earlier unfinished work, now explicitly resumed by Sean.
- **Verified so far:** Pygbag 0.9.3 packages the game; real browser reaches
  title (CPython 3.12.12, pygame-ce 2.5.7 / SDL 2.28.4). Audio converts from
  87.5 MB WAV to 10.4 MB OGG; browser tar.gz is approximately 11.1 MB.
  Async-loop (3), save-menu (17), save-code (16), code-entry (24), audio (10)
  checks pass. Full desktop verification underway.
- **Unresolved:** Enter at NEW GAME produced a runtime error; its traceback
  was not captured before the browser connection became unavailable on
  session resume. Do not call this playable or publish it yet. Docks/sewer
  playtest, FPS, audio listening and browser save-code round trip remain.
- **Expensive findings:** pygbag only discovered pygame after adding a direct
  import in main.py; whole-track SoundFile Vorbis writes stack-overflow on
  Windows, so encoding now streams 8192-frame blocks. Desktop WAVs untouched.
- **Known issues:** stale Feywild generators (see DECISIONS.md). Browser
  persistence/fullscreen remain later work in WEB-BUILD.md.
- **Next bounded task:** finish step 0 verification/commit, then diagnose NEW
  GAME with a connected browser and perform step 1. No publishing in this pass.

---

## Recent Passes

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
