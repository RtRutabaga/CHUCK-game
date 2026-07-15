# Agent Handoff

## Repository State

- Branch: main
- Base commit: `447f2f2` (`Refine tavern and pantry presentation`)
- Current work: Phase 3 environment placement and sky variation polish
- Active phase: Phase 3 - Waterdeep Tavern, Pantry, and Fall to Chult

## Completed This Pass

The tavern hearth is flush with the east wall, pantry sky clouds no longer form
an obvious repeated tile stamp, the exterior HEROD sign clears the tavern door,
and all three north-district house doors now answer "it's closed".

## Implementation

- Moved the tavern hearth from column 25 to column 28, the last floor tile before
  the solid east wall. Its established sprite, collision, and prop behavior are
  unchanged.
- Increased pantry sky art from two to twelve stable variants. Each variant uses
  a seeded generator for cloud height, width, horizontal position, and one-pixel
  frame drift; map-coordinate hashing still keeps every selected variant stable.
- Moved the exterior HEROD sign one tile west, from `(43, 18)` to `(42, 18)`,
  while preserving the tavern threshold and named return marker.
- Added a shared `closed_door` dialogue ID to the existing `house_door` prop.
  All three north-district doors remain solid and now say exactly "it's closed".

## Verification

- All 20 test suites pass.
- Coverage verifies exact hearth/sign coordinates, all three shared house-door
  props and end-to-end interaction with each door, the closed-door line, twelve
  sky variants with at least ten distinct first frames, map drawability, and
  unchanged pantry fall behavior.
- Native-scale visual review confirms the sign clears the open doorway, the
  hearth reads flush to the east wall, and the sky field has varied cloud
  placement without losing its clear teal/cloud identity.

## Playtest Focus

- Inspect the tavern's east side and confirm the fireplace visually meets the
  wall rather than floating one or more floor tiles away.
- Return to the exterior after the sewer and confirm the HEROD sign no longer
  obscures any part of the open tavern threshold.
- Interact with each of the three doors in the north-district buildings; every
  one should show only "it's closed" while remaining physically shut.
- View the pantry sky field for several animation frames. Cloud blocks should
  feel scattered rather than stamped, while the cheese remains legible and sky
  contact still enters the falling scene.

## Next Bounded Task

Turn `FallingCutsceneScene` into the complete circa-1994 long-fall sequence:
author timed visual stages, changing cloud density/sky, a stylized audio arc,
and an approach toward Chult, then end at a clean non-playable Phase 4 handoff.
Do not create the playable Chult map or return control in Chult.
