# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `56c17c6` (enemy hazard blocking)
- Current work: the overall-game cigarette counter (session 128)
- Active phase: Phase 6 — The Jungle Temple (`PHASE-6.md`)

## Completed This Pass

The long-deferred cigarette counter, Mario-coin style — settling the
20-per-carton contract carried in config since session 110:

- `src/systems/cigarettes.py` (new): CigaretteLedger — a monotonically
  accumulating total with add()/replace(), owned by Game so it survives
  map walks and Astral respawns.
- Banking: Cigarette.on_collect banks 1; CigaretteCarton.on_collect
  banks its exact cigarette_count (20); the scene's pickup loop passes
  the ledger. Grass-revealed cigarettes bank automatically (ordinary
  pickups).
- Persistence: SaveRecord gains a `cigarettes` field WITHOUT a version
  bump — pre-counter saves stay valid and resume with zero banked,
  while forged/negative totals invalidate the save like any bad field.
  Ashtray saves include the current total; CONTINUE restores it;
  NEW GAME (and any bare load_checkpoint) resets to zero.
- HUD: the total sits quietly top-right — a tiny cigarette pictogram
  beside "xN" in the pixel font — opposite the diegetic sanity
  cigarette, keeping the Bible's calm screen.
- No spending exists yet; the ledger only accumulates.

## Files Changed

- src/systems/cigarettes.py (new), src/systems/save.py,
  src/systems/checkpoints.py, src/core/game.py,
  src/entities/pickup.py, src/scenes/world_scene.py, src/ui/hud.py.
- tests/test_cigarette_counter.py (new, 6 tests): ledger math, 1-vs-20
  banking, real-scene collection surviving respawn and a map walk, the
  anchor-save/CONTINUE/NEW GAME round trip, pre-counter save
  compatibility + forged-total rejection, and the HUD render.
- tests/test_checkpoints.py: the exact save-JSON dict and the CONTINUE
  kwargs now include the cigarettes field.
- Contract comments in config/pickup settled (the "later session" is
  this one).

## Verification Performed

- All 47 suites pass.
- Screenshot confirms the top-right counter (pictogram + x47) balanced
  against the sanity cigarette at native scale.

## Session 129 Addendum: continuous count + death rewind

Playtest found the Chult arrival zeroing the counter: the cutscene
hands off through load_checkpoint, whose default reset the ledger. The
count is now continuous for the whole run — load_checkpoint carries the
running total forward (committing it as the new respawn value); only
NEW GAME passes an explicit zero and CONTINUE the saved total.

Second direction: death rewinds the count to the active respawn point.
The ledger gained commit/rollback semantics — set_runtime_checkpoint
(every map entry and Ashtray attunement) commits, and the Astral
respawn completion rolls back beside the sanity refill, so cigarettes
gathered past the checkpoint are lost with Chuck. Tests: a regression
for the handoff carry, and a full death-rewind walk (map-entry rewind,
Ashtray commit, post-Ashtray loss, cross-map carry+recommit). All 47
suites pass.

## Known Issues

- None known. Balance note: with the counter live, the carton economy
  (temple urns, pantry shelves/jars) now visibly banks large totals —
  ready for whatever spending/economy design comes later.

## Scope Notes

- No future-phase work; no documented creative rules changed. No
  inventory system was introduced — the ledger is a single number,
  deliberately short of the Bible's deferred-inventory line.

## Recommended Next Bounded Task

- Temple Map 9: the final chamber's antechamber or the chamber itself
  (adventurers/beholder battle, scripted Fireball) — the next Phase 6
  beat, sliced to taste.
