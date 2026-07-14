# Agent Handoff

## Repository State

- Branch: main
- Base commit: `8934806` (`Close sewer grate dialogue silently on no`)
- Current work: enemy reset and short sewer-rat patrols
- Active phase: Phase 2 — Waterdeep Starting Area and Sewer Tutorial

## Completed This Pass

Enemies now reset from their map markers when Chuck dies and returns. Eligible
ordinary sewer rats also make short horizontal patrols around their spawn.

## Implementation

- `WorldScene` stores enemy marker data and centralizes cat/rat construction in
  `_reset_enemies()`. It runs on map load and when the respawn hold returns
  Chuck to the active Anchor.
- Defeated rats are reconstructed alive; the docks cat also returns to its
  original marker. Pickups, Anchor state, and other non-enemy state are not
  reset.
- `SewerRat.configure_patrol()` enables movement only when both neighboring
  horizontal tiles are walkable, non-Astral, and free of another rat spawn.
  Solid walls and props are rejected through normal tile solidity.
- Eligible rats travel at 12 px/s within six pixels of their home position and
  reverse at each endpoint. The three tutorial-choke rats remain stationary;
  the four late-maze rats patrol.

## Verification

- Focused combat checks cover patrol range/reversal and stationary behavior
  beside walls, props, Astral fall zones, and other rat spawns.
- Headless lifecycle checks defeat all seven rats, advance the full respawn,
  and confirm seven fresh living rats return with the same 3/4 stationary-to-
  patrolling split. A separate check confirms the docks cat resets to spawn.
- All 18 test suites pass, including existing headless launch/render coverage.

## Playtest Focus

- Watch the original three-rat choke: all three should remain fixed in place.
- In the late Astral section, confirm each of the four rats makes a subtle short
  side-to-side patrol without stepping onto Astral blocks.
- Defeat several rats, deliberately die to contact or a fall tile, and confirm
  every rat is restored after Chuck returns to the sewer entrance.
- On the docks, let the cat move, die, and confirm it restarts from its marker.

## Next Bounded Task

Add the missing market woman beside the red awning at established human scale
with her documented sewer-scraps line. Do not add a quest, marker, waypoint,
or tavern interior.
