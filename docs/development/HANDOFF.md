# Agent Handoff

## Repository State

- Branch: main
- Base commit: `72fce5a` (`Add Waterdeep market woman`)
- Current work: post-sewer tavern entrance state
- Active phase: Phase 2 — Waterdeep Starting Area and Sewer Tutorial

## Completed This Pass

Returning through the sewer outflow now visibly opens the Waterdeep tavern
entrance. The initial exterior remains unchanged until that return.

## Implementation

- `WorldScene` records sewer completion only when Waterdeep loads through the
  named `sewer_outflow` arrival. The state persists across later map loads in
  the same scene.
- `TileMap.open_tavern_entrance()` changes the single `D` door tile to a
  walkable `v` threshold and swaps only its prop from `tavern_door` to
  `tavern_open`. It validates that exactly one authored tavern door exists.
- The new 48×34 procedural prop removes the wooden leaves, retains the familiar
  side lanterns and frame, and fills the opening with near-black interior space
  plus a stone sill.
- The threshold is a shallow exterior alcove. Adjacent and rear facade tiles
  remain solid; there is no interior scene, transition, or Phase 3 content.

## Verification

- Focused prop, tilemap, and outflow lifecycle suites pass.
- Coverage confirms the ordinary map begins with a solid closed `D`, while the
  sewer return produces one walkable `v` and one `tavern_open` prop.
- The outflow test loads and draws the returned Waterdeep scene headlessly.
- All 18 test suites pass, including existing headless launch/render coverage.

## Playtest Focus

- On a fresh start, confirm the original wooden tavern doors remain closed.
- Complete the sewer and return through the outflow. Confirm the doors are gone
  and the dark threshold reads clearly from the south pier approach.
- Walk onto the threshold. Chuck should enter the shallow opening but stop at
  the still-solid facade; no interior transition should occur.
- Confirm the guard, market woman, HEROD sign, windows, and exterior layout are
  otherwise unchanged.

## Next Bounded Task

Phase 2's documented feature checklist is complete. Conduct a full human
playtest and wait for Sean to advance `CURRENT-PHASE.md` before beginning the
tavern interior or any Phase 3 work.
