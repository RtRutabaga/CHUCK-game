# Agent Handoff

## Repository State

- Branch: main
- Latest commit reviewed: `6cedb0b` (`feat: build the sewer — entrance, tileset, and theme`)
- Current work: uncommitted Phase 2 jump-obstacle pass; stop for Sean's playtest
- Active phase: Phase 2 — Waterdeep Starting Area and Sewer Tutorial

## Review This Pass

Commit `6cedb0b` was reviewed in detail, including its transition flow,
choice data, map rebuild, per-area tilesets, generated sewer art, music
wiring, and tests. It is coherent with the established architecture,
Game Bible, and Phase 2 scope. No corrective fix was needed.

## Completed This Pass

Phase 2 item 6: an Astral wrong-map interruption, a short top-down jump,
and the temporary jump tutorial prompt.

## Files and Systems Changed

- Input/config/player/collision: SPACE is now `jump`; E and RETURN remain
  `interact`. A short committed hop travels in Chuck's facing direction,
  lifts his sprite six native pixels, and ignores only terrain `V` while
  airborne. Normal walls remain solid.
- Sewer map/tileset/generator: `V` is a solid, animated, hard-edged
  blue-purple Astral terrain, deliberately not a portal. A one-tile-thick
  band interrupts the full corridor at row 19. `sewer.png` was regenerated
  with a sixth terrain row.
- WorldScene/tutorial: approaching the gap shows "Press SPACE to jump";
  reaching the far side clears the prompt for the rest of that sewer visit.
- Tests: new jump suite plus map, tileset, and input/hint coverage.

`move_and_collide` gained an optional ignored-terrain set. Its default is
empty, so every existing caller retains the prior behavior; Player passes
only `{V}` during a jump.

## Verification

- All 15 test suites pass.
- Headless launch/render check reached `WorldScene`, loaded the sewer,
  updated and drew it at 320x180, then shut down cleanly.

## Known Issues / Playtest Focus

- Sewer remains a forward dead-end; the exit is Phase 2 item 8.
- Check jump timing, the six-pixel arc, prompt distance, and whether the
  Astral band reads as misplaced map material at native scale.
- Existing note from the prior pass: entering an area rebuilds SanitySystem,
  so sanity resets on descent. Harmless while the sewer has no hazards.

## Next Bounded Task

Phase 2 item 7: ordinary rats and the scratch attack/tutorial beyond the
jump. Rats must be visibly smaller than Chuck; one scratch kills one rat.
