# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `ef4d522` (the battle in motion)
- Current work: the Astral breach (session 133)
- Active phase: Phase 6 — The Jungle Temple (`PHASE-6.md`)

## Completed This Pass

The sanctum seals shut behind Chuck so the battle cannot be walked
away from:

- src/entities/battle_hazards.py: AstralBreach. When Chuck walks west
  of BREACH_TRIGGER_COL (28) — into sight of the fight — the Astral
  Sea breaks through the floor at BREACH_COLS (32, 33): a
  two-tile-thick north-south band of 'V' terrain, landing instantly
  across the rows nearest Chuck (BREACH_INSTANT_RADIUS) so it cannot
  be outrun, then cascading outward on BREACH_STEP with a bright
  per-tile flash (drawn over the world) and one vanish sfx.
- The band is the established astral language: lethal to walk into,
  unjumpable at two tiles thick, uncrossable by enemies
  (FALL_HAZARD_TERRAIN). The east door and Ashtray are cut off; every
  battle actor stays west of the seal, in line of sight.
- A tile never breaks through under Chuck — an occupied cell waits
  until he steps off.
- src/world/tilemap.py: set_terrain(col, row, char) runtime mutator
  (returns the old char; unknown chars fail loudly). clear_tile's
  natural-reset note applies here too.
- _reset_enemies() restores every mutated tile in reverse order and
  re-arms the trigger: death — including falling into the seal —
  heals the floor with the rest of the room, and the respawn point
  (arrival or Ashtray) is always east of where the seal re-forms.
- 24 more skeletons (Ψ) line the sealed chamber's north and south
  fringes (two staggered rows each, rows 5/7 and 40/42, all west of
  the seal), sparing the center sight-line (rows 14-30). At 7-tile
  notice range they stay dormant until Chuck flees a wall to dodge the
  rays, then herd him back toward the fight — 27 skeletons total.
- The entrance establishing shot: the heroes' three lines fire at the
  far-east door, ~40 tiles from the fight, so the camera now cuts to
  the battle for them (Camera.focus_on holds a fixed point while the
  dialogue freezes the world) and hard-cuts back to Chuck afterward
  (WorldScene._battle_establishing_focus + _restore_camera_to_player;
  SANCTUM_ESTABLISH_LIFT lifts the group clear of the dialogue panel).
  The trio was reclustered into a tight arc — ranger (18,20), fighter
  (16,22), wizard (19,25), beholder (10,23) — so all four fit one
  frame; the aisle path (138 tiles) is untouched.

## Files Changed

- src/entities/battle_hazards.py (AstralBreach), src/core/config.py
  (BREACH_* block), src/world/tilemap.py (set_terrain),
  src/scenes/world_scene.py (trigger + update + draw + reset-restore).
- tests/test_phase6_sanctum_battle.py: six new tests (seal +
  two-thickness + unreachable east door, no-break-under-Chuck,
  death-heals-and-rearms, no-trigger-out-of-sight, wall-skeletons-
  line-the-fringes, entrance-camera-cuts-to-the-battle-and-back) — 13
  total. test_phase6_temple_sanctum.py's skeleton contract went 3 -> 27.

## Verification Performed

- All 50 suites pass.
- Flood-fill proof in-suite: with fall hazards lethal, the arrival
  tile is unreachable from Chuck once the seal lands, and every
  barrier tile's partner column is astral or solid (no jumpable gap).
- Screenshot mid-cascade: the flash wall landing behind Chuck,
  threading between the guardian monuments.

## Known Issues

- None known from this pass.

## Scope Notes

- No future-phase work. The survival timer / scripted Fireball (which
  reduces Chuck to ~half Sanity and throws him to the rubble map), the
  rubble map itself, the escape cutscene, and the final-chamber battle
  music remain unbuilt.

## Recommended Next Bounded Task

- The scripted Fireball: after a survival period in the sealed
  sanctum, the wizard's Fireball fills the room, cuts Chuck to roughly
  half Sanity, and throws him into a new rubble map (author its first
  structural slice with the crawlspace exit as a follow-up if it
  doesn't fit).
