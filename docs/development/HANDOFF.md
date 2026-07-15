# Agent Handoff

## Repository State

- Branch: main
- Base commit: `2d13370` (`Build Waterdeep pantry floor`)
- Current work: Phase 3 successful sky fall and dedicated cutscene handoff
- Active phase: Phase 3 - Waterdeep Tavern, Pantry, and Fall to Chult

## Completed This Pass

Teal pantry sky blocks now trigger the familiar initial fall without killing
Chuck, then reliably replace gameplay with a dedicated, input-free falling
scene. The scene establishes the visual cut and descent language but remains an
open-ended first shot; the full long fall and Phase 4 endpoint are not built.

## Implementation

- Added a material-classifying fall query. `V` reports `astral`, `s` reports
  `sky`, and both remain safe while Chuck is airborne. The existing Astral
  compatibility helper and every Phase 2 behavior remain intact.
- Made teal sky tiles walkable. Entering one locks control and runs the same
  0.65-second shrink/sink used for Astral material.
- At completion, Astral still depletes Sanity and respawns locally. Sky instead
  preserves Sanity and replaces WorldScene with `FallingCutsceneScene`, so Chuck
  cannot duplicate across scenes or accidentally continue pantry simulation.
- The dedicated scene has no player-controlled entity and ignores movement
  state. It fades the warm Waterdeep music, draws a native-pixel teal vertical
  grade, moves two restrained layers of blocky clouds upward, and reframes the
  idle Chuck sprite from the tiny end of the gameplay fall to readable cutscene
  scale. Letterbox bars make the authored presentation boundary explicit.
- The scene currently loops this first shot indefinitely. It does not yet vary
  the descent over time, introduce a falling audio cue, suggest Chult below, or
  reach the clean Phase 4 endpoint.

## Verification

- All 20 test suites pass.
- Pantry coverage verifies Astral and sky identify separately; Astral still
  performs local death/retry; sky preserves Sanity, completes the familiar
  initial fall, replaces the world exactly once, and reaches the dedicated
  scene. Held movement does not create a controllable entity there.
- Cutscene clouds advance over time and the scene renders through the native
  320x180 pipeline. Native-scale visual review confirms Chuck remains
  recognizable and the sky palette connects directly to the pantry blocks.

## Playtest Focus

- Enter a teal sky block on foot. Chuck should perform the same quiet initial
  shrink/sink as an Astral fall, then cut to the dedicated sky shot.
- Confirm there is no vanish/respawn sequence, Sanity loss, or return to the
  pantry after the sky fall.
- Hold movement, jump, scratch, and interact during the cutscene. None should
  restore normal player control or affect the shot.
- Watch the cloud layers: they should move upward at different restrained speeds
  while Chuck remains recognizable and calm at center frame.
- Compare an Astral fall afterward from a fresh run to confirm it still returns
  Chuck locally and never enters the cutscene.
- The cutscene intentionally continues indefinitely in its opening shot; that
  is the next session's implementation boundary, not the final Phase 3 ending.

## Next Bounded Task

Turn `FallingCutsceneScene` into the complete circa-1994 long-fall sequence:
author timed visual stages, changing cloud density/sky, a stylized audio arc,
and an approach toward Chult, then end at a clean non-playable Phase 4 handoff.
Do not create the playable Chult map or return control in Chult.
