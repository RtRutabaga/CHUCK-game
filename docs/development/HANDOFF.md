# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `826fe7e` (the battle tableau)
- Current work: the battle in motion (session 132)
- Active phase: Phase 6 — The Jungle Temple (`PHASE-6.md`)

## Completed This Pass

The sanctum battle fights on fixed cadences Chuck cannot influence:

- src/entities/battle_hazards.py (new): BattleProjectile (eye ray /
  arrow / bolt; dies on masonry, rays also dissipate at
  BATTLE_RAY_RANGE so the arrival aisle stays survivable) and
  BattleChoreographer (staggered timers; rays cycle the three
  adventurers' lanes in a fixed learnable order east from the beholder;
  arrows and bolts fly west at it; the fighter's slash pulses a 14x12
  zone west of him on BATTLE_SLASH_INTERVAL).
- Every attack costs Sanity through the ordinary i-frame damage path
  (config BATTLE_* constants: ray 20, bolt 15, slash 12, arrow 10) and
  the shot is spent on impact. Projectiles are y-sorted drawables.
- Three skeletons (plain Ψ markers at (13,20), (13,26), (15,18)) press
  the fighter's line between him and the beholder — the room's only
  conventional enemies, the fight he is "occupied" by.
- Actors animate in place: BattleActor.update(dt) drives a breathing
  beholder hover and offset-phase sways; the choreographer sets
  attack_flash on fire, drawn as a one-beat lunge toward the target.
- The battle rebuilds inside _reset_enemies(): death clears the air and
  restarts every cadence with the re-pressed skeletons.

## Files Changed

- New: src/entities/battle_hazards.py,
  tests/test_phase6_sanctum_battle.py (7 tests).
- src/core/config.py (BATTLE_* block), src/entities/battle_actor.py
  (update/center props/flash/animated draw), src/scenes/world_scene.py
  (choreographer + projectile update, damage, reset, draw wiring),
  assets/maps/temple_sanctum.txt (three Ψ).
- tests/test_phase6_temple_sanctum.py: the enemy-free contract became
  "exactly 3 skeletons, nothing else".

## Verification Performed

- All 50 suites pass.
- Headless screenshot mid-fight: rays streaking east past the braziers,
  the wizard's teal bolt in flight, the beholder hovering over its
  shadow, a skeleton pressing toward the dais.

## Known Issues

- None known from this pass.

## Scope Notes

- No future-phase work. The survival timer / scripted Fireball (which
  reduces Chuck to ~half Sanity and throws him to the rubble map), the
  rubble map itself, the escape cutscene, and the final-chamber battle
  music remain unbuilt.

## Recommended Next Bounded Task

- The scripted Fireball: after a survival period in the sanctum, the
  wizard's Fireball fills the room, cuts Chuck to roughly half Sanity,
  and throws him into a new rubble map (author its first structural
  slice with the crawlspace exit as a follow-up if it doesn't fit).
