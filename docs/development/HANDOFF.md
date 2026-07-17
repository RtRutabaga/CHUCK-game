# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `40533f3` (`Add worn-trail approaches before the Chult vine exits`)
- Current work: breakable temple urns spilling cigarette cartons (session 110)
- Active phase: Phase 6 — The Jungle Temple (`PHASE-6.md`)

## Completed This Pass

All 26 dressed temple urns (map chars '¦' wall-base and '¢' floor, across
Temple Maps 1-6) are now scratch-breakables instead of static props. One
scratch shatters one urn into terracotta shards — the breakable-grass
lifecycle with a clay palette — and spills a full cigarette carton.

The carton is a new pickup (`CigaretteCarton`, 12x8 cream box with a red
band and visible filter tips) worth exactly `CARTON_CIGARETTE_COUNT` (20)
cigarettes: `restore_amount = 20 * CIGARETTE_SANITY_RESTORE`, clamped at
full sanity today. THE NUMBER IS THE CONTRACT — a later session adds a
cigarette counter, and a carton must bank exactly 20 into it; the config
comment and the pickup's `cigarette_count` attribute carry that intent.

Wall-base urns spill their carton onto the guaranteed floor tile beneath
them; floor urns spill in place. Breaking clears the urn's tile to its
declared under-terrain via the new `TileMap.clear_tile`: floor urns open
for walking, wall-base tiles remain the solid wall they always were. Urns,
tiles, and cartons all rebuild on checkpoint reload, matching the enemy
lifecycle. Idols, stelae, and fallen columns remain static mute dressing.

## Files Changed

- src/entities/breakable_urn.py (new): the BreakableUrn entity — same
  positional-variant formula as the old prop so each urn looks unchanged,
  scratch-once behavior, terracotta debris, on_break tile-clear callback.
- src/entities/pickup.py: CigaretteCarton.
- src/entities/breakable_grass.py: create_pickup() (grass yields its
  cigarette); the scene drop loop is now polymorphic over breakables.
- src/world/tilemap.py: clear_tile(col, row) — swaps a prop tile's grid
  char for its declared under-terrain, loud error if it has none.
- src/scenes/world_scene.py: temple_urn prop tiles build as BreakableUrn
  breakables (excluded from static props); drop loop delegates to each
  breakable's create_pickup.
- src/core/config.py: CARTON_CIGARETTE_COUNT = 20 with the counter note.
- tools/generate_breakable_sprites.py + assets/.../cigarette_carton.png:
  the carton sprite.
- tests/test_temple_urns.py (new, 7 tests): carton counts/clamping,
  break-once + debris lifecycle, wall-vs-floor spill positions, tile
  clearing both ways, an end-to-end scratch through a real scene, per-map
  breakable counts (7/2/9/2/3/3), and full checkpoint-reload reset.
- tests/test_phase6_temple_dressing.py: docstring updated (urns are
  breakables now; still no dialogue).

## Systems Added or Changed

- TileMap.clear_tile is the only schema-level addition: the first runtime
  tile mutation, deliberately restricted to prop tiles with an authored
  under-terrain, resetting naturally on map reload.

## Verification Performed

- All 43 test suites pass (42 prior + the new urn suite).
- Headless end-to-end: standing beneath a wall urn and scratching breaks
  it, spills the carton onto Chuck's tile, and collects it the same frame
  (sanity 10 -> 100); floor urn tiles open; checkpoint reload restores
  all urns and tiles.
- Screenshot confirmed the shatter debris and the carton read clearly at
  native scale.

## Known Issues

- Balance flag for playtest: 26 cartons across the temple is a generous
  sanity economy while the counter doesn't exist yet (each carton is
  effectively a full heal). The count/placement is data if tuning wants
  fewer urns to hold cartons later.

## Scope Notes

- No future-phase work was intentionally implemented; the cigarette
  counter itself is explicitly deferred, with the 20-per-carton contract
  recorded in config and on the pickup.
- No documented creative rules were intentionally changed.

## Recommended Next Bounded Task

- Build Temple Map 7 as the next broad/open room east of the narrow Astral
  wind connector, continuing the recurring arches (east/west arches
  anchored on the bottom opening row), torches, dressing language —
  including breakable urns — one physical Ashtray, and shared-loader
  entry. Keep the slice distinct from the final chamber, Fireball, rubble
  escape, and Phase 7 ship.
