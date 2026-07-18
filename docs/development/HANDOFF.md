# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `ccc1173` (deeper-door facade)
- Current work: guardian monument rows in the temple's open halls
  (session 115)
- Active phase: Phase 6 — The Jungle Temple (`PHASE-6.md`)

## Completed This Pass

Playtest direction: less open space in the temple interiors, filled with
large statues in rows (reference: a stepped skull ziggurat with green
painted bands, gold diamond plaques, and a small base stair).

Twelve `temple_monument` statues now stand in aligned guardian rows:

- Temple Map 1 entrance hall: two vertical rows of three flanking the
  central aisle (west anchors col 11 / east col 36).
- Temple Map 3 skeleton chamber: two per side in the side lanes.
- Temple Map 5 snake chamber: a southern row of two.

Each monument is a 48x64 procedural prop (two alternating variants via
the standard positional hash) on a 3x2 solid footprint: five temple-wall
cells plus the new 'Ϙ' anchor (solid, under '█') at bottom-center
carrying the y-sorted sprite, which rises two tiles above its footprint.
Chuck walks in front of and behind them correctly; the narrow connector
maps (2/4/6) were deliberately left alone — they have no open space, and
statues there would break spike bands, dart lanes, or the Astral wind.

Placement was applied by an assertion-checked script: every footprint
cell had to be plain open floor; a surrounding clearance ring could
contain only floor, wall, mute dressing, and torches (never thresholds,
hazards, spawns, or another monument); connectivity plus every
spawn/arrival/boundary's reachability was re-verified after each
statue; and the entrance hall kept a margin above its >=850-walkable
test floor. The validator caught and forced two placement corrections
(a pier collision and a snake-spawn adjacency) before anything was
written.

## Files Changed

- tools/generate_temple_props.py: temple_monument(variant) + green band
  palette; regenerated temple_monument_1/2.png.
- src/world/tilemap.py: 'Ϙ' anchor tile def + legend.
- src/entities/prop.py: temple_monument variant tuple.
- assets/maps/temple_entrance.txt, temple_skeletons.txt,
  temple_snakes.txt: the twelve 3x2 footprints.
- tests/test_phase6_temple_dressing.py: a new test locking monument
  counts (6/4/2), solid footprints, row formations, and the anchor
  tile's shape.

## Verification Performed

- All 44 suites pass — including the skeleton chamber's 3x3-envelope
  route test, the snake chamber's threshold route, and the entrance
  hall's walkable minimum.
- Screenshots confirm the statues render in rows at native scale with
  correct y-sorting and the intended silhouette.

## Known Issues

- None known from this pass.

## Scope Notes

- No future-phase work; no documented creative rules changed.

## Recommended Next Bounded Task

- Build Temple Map 7 as the next broad/open room east of the Astral wind
  connector, continuing arches (E/W anchored on the bottom opening row),
  torches, dressing — urns, skulls/braziers, and now guardian monument
  rows — one physical Ashtray, and shared-loader entry.
