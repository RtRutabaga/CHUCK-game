# Decision Log

Record durable decisions another agent might otherwise reverse. Do not use this for ordinary progress notes.

## Established Project Decisions

- CHUCK is a top-down action-adventure RPG inspired by 16-bit adventure games.
- Chuck is approximately one foot tall.
- The D&D source stat block's “Giant Rat” creature name does not define his visual scale in the game.
- The Game Bible is the core creative authority.
- Topic-specific supplements are authoritative within their defined topics.
- Campaign notes are historical source material and reference pools, not automatic implementation requirements.
- Development is incremental: one coherent feature or vertical slice at a time.
- The game should remain runnable after each completed pass.
- Claude Code and Codex use the same Git repository.
- Only one coding agent edits at a time.
- Each completed pass should be tested, handed off, and committed before switching agents.
- ~~Each newly authored gameplay map receives one physical Ashtray/checkpoint,
  registered through the shared save/checkpoint loader rather than a separate
  map-specific or development teleport path.~~ **Superseded** — see the save
  and browser decisions at the end of this file. Do not add Ashtrays.
- Phase 5 and Phase 6 are complete. Phase 6's implemented scope remains
  documented in `PHASE-6.md`.
- Phase 6 begins at the jungle-temple interior and ends when Chuck reaches the
  ship; ship gameplay remains Phase 7 content.
- The first Phase 6 room is a dedicated, reversible temple entrance hall with
  one physical Ashtray and a development-visible `Temple 1` entry through the
  shared checkpoint loader.
- Phase 6 temple maps use recurring animated wall torches. Broad/open rooms
  alternate with long, narrow connector maps, and successive routes vary among
  cardinal directions instead of forming a single straight northward chain.
- Temple gameplay-map thresholds use reusable human-NPC-scale stone arch props
  over narrowed three-tile walkable openings. Transition terrain and named
  arrivals remain authoritative beneath the presentation.
- Phase 5 map order after the undead ambush is Chult Map 4 as a vegetation-dense,
  low-pressure jungle respite with exactly one massive slow dinosaur, followed
  by the temple exterior on Chult Map 5. Do not merge the respite and temple
  maps or add other Map 4 enemies.
- Exterior Chult maps should include a restrained scatter of reusable
  scratchable grass tufts. They use the shared breakable/reward behavior, but
  the `Press F to scratch` proximity tutorial remains limited to Waterdeep and
  the sewer.
- Phase 9 is governed by `PHASE-9.md` and contains thirteen playable Feywild
  maps total: the existing riverbank plus twelve new maps. Its recurring
  gameplay language is reactive flower switches, slowing pollen, and
  Chuck-sized root/table/mushroom passages that exclude larger enemies.
- Phase 9 ends at a stable Feywild boundary. The floating wizard's tower, its
  cutscene, and the transition beyond it are reserved for a later phase.
- Phase 10 is governed by `PHASE-10.md`. It begins at the Cloud Staircase,
  introduces Zephyros, and ends at a contained modern-city arrival. Playable
  modern-city content is reserved for Phase 11.
- Phase 11 is complete. Phase 12 is governed by `PHASE-12.md` and contains
  exactly two peaceful Tahuya-cabin maps: the cabin grounds with both playable
  porches, and the cabin interior. The Sean-authored layout and photographs in
  `docs/design/references/tahuya-cabin/` are authoritative references for this
  real-place adaptation; agents must not redesign it as a generic cabin.
- Phase 12's counter map awakens only after all four light entities have been
  spoken to and Chuck subsequently crosses the back door. Its desert-arrival
  cutscene is the end boundary; playable desert content belongs to Phase 13.

## Save, Respawn, and the Browser (2026-09-17)

- The Ashtray is gone from the game entirely: object, interaction and writing.
  Do not reintroduce it, and do not add one to a new map. The only surviving
  ashtray is Zephyros's cigarette metaphor in `data/dialogue/zephyros.json`,
  which is about the cigarette the game is named after and not about saving.
- A map's **door** — the runtime entry Chuck walked in by — is both the save
  point and the respawn point. One per visit, set on arrival, unmoved while he
  is in the map. Measured cost against the old Ashtrays: a median of 1.7 tiles
  of extra walking.
- A save is written from the pause menu, not by touching anything in the world.
- The portable save is a **twelve-character code** (`src/systems/save_code.py`).
  Its two registries in `src/systems/save_registry.py` are append-only: reorder
  one and every code in the wild silently means something else.
- The code's check is one Reed-Solomon symbol, not a hash. It always catches a
  single wrong character and a single transposition; beyond that it is a
  one-in-32 coin, and a made-up code is a real save about one time in fifty-six.
  That is deliberate, measured, and the price of twelve characters.
- Past their ceilings the cigarette and death counters read "a lot" rather than
  a number (`src/systems/tally.py`). The code's field widths are sized to those
  ceilings, not the other way round.

## Map Generators Are Stale (2026-09-17)

- The generators in `tools/` no longer reproduce every shipped map. Several
  Feywild maps have been dressed by hand since generation and differ from their
  generator by 500 cells and more — `feywild_pollen_orchard` by 663.
- **Re-running a generator for one of those maps destroys authored work.**
  Treat the shipped `assets/maps/*.txt` as the artifact and edit it directly,
  unless a test holds that map to its generator.
- Some maps *are* held to their generators by tests — the modern-city set in
  `test_city_furnishing.py`, the desert pair in `test_desert_ribcage_and_camp.py`.
  For those the generator is authoritative and the map follows it.
- This was established by running every generator and diffing; it cost a
  session to find. Do not rediscover it.

## Browser Build Constraints (2026-09-18)

- Pygbag does **not** need cross-origin isolation for this game. Verified
  against the local build: `crossOriginIsolated === false`,
  `SharedArrayBuffer` undefined, game running. GitHub Pages is therefore a
  viable host and needs no COOP/COEP headers — which it cannot set.
- The published game fetches its Python/pygame runtime from
  `https://pygame-web.github.io/cdn/` at play time. Pages hosts the game;
  a third party hosts the interpreter. If that CDN is unavailable the
  published game does not start. This is a property of pygbag, not of our
  build, and it should be understood before the game is announced anywhere.
- Use `127.0.0.1`, never `localhost`, for the local preview. Pygbag 0.9.3
  treats `localhost` as a runtime-development host and tries to fetch a
  pygame wheel from a local `/cdn/` that does not exist. (Codex, 2026-09-17.)
- Claude Code's in-app browser pane runs the wasm build at roughly 1.4 fps.
  It cannot be used to measure frame rate or to play-test. One-shot checks
  that do not depend on the loop running at speed are fine. Frame rate,
  traversal and the save-code round trip need a real foreground browser.

## Codes Are The Only Save (Sean, 2026-09-18)

- **CONTINUE and the local save file are being removed.** The save code is
  the whole save system. This reverses `SAVE_CODES.md` §7, which had local
  saves staying primary.
- **Why it costs almost nothing:** there is no autosave. `write_save` is
  called only by the pause menu's SAVE GAME and one cutscene handoff, so
  CONTINUE was already never better than the player's last deliberate save.
  Removing it costs typing twelve characters, exact sanity, and `spoken`
  (who has already introduced themselves). That is the entire difference.
- **Why it is worth doing:** it deletes a whole second persistence system
  and the browser half of it — `WEB-BUILD.md` §4.1, IndexedDB mounts and
  syncs, the localStorage fallback, cross-browser flakiness — which was the
  least certain remaining item in the web plan. It also removes the failure
  where a file and a code disagree about which is newer.
- **Sanity stays out of the code.** Sean: low stakes, and a hackable code is
  fine. Codes stay at twelve characters and a resumed game starts at
  `SANITY_START`. Do not widen the format to carry sanity.
- **Quitting hands the code over.** With no CONTINUE, leaving without a code
  loses the session, so QUIT TO TITLE shows the code rather than warning in
  the abstract. It writes nothing; it is read-only. Done 2026-09-18.
- **Done, 2026-09-18.** CONTINUE is off the title; `SaveSystem`, `save2.json`
  and `default_save_path` are gone; `settings.json` has its own path (the same
  place it always was, so existing settings survive); and the tests round-trip
  through a code instead of a file. `src/systems/save.py` keeps only
  `SaveRecord`, which the codec is written from.
- `checkpoints.write_save` is now `save_here`: it banks the save point and
  returns the record to make a code of. It writes nothing.
- **`spoken` is session memory now.** It needed a positional key and never fit
  in twelve characters, so people Chuck has met introduce themselves again
  after a resume. Cosmetic, and accepted.

