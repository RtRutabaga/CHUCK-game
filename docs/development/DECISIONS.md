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
- Each newly authored gameplay map receives one physical Ashtray/checkpoint,
  registered through the shared save/checkpoint loader rather than a separate
  map-specific or development teleport path.
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
