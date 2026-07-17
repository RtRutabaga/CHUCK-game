# Agent Handoff

## Repository State

- Branch: main
- Base commit before this pass: `696cab4` (`Dress temple interiors with idols, stelae, urns, and columns`)
- Current work: east/west temple arch alignment fix (session 108)
- Active phase: Phase 6 — The Jungle Temple (`PHASE-6.md`)

## Completed This Pass

Playtest found every east/west temple doorway's arch sitting one tile above
its walkable opening: the dark void read above the path instead of around it.

Root cause: props draw upward from their anchor tile's bottom edge. The
38x48 east/west arch is exactly three tiles tall, and each side threshold is
a three-row opening — but the arch chars ('«'/'»') were authored on the
opening's MIDDLE row, so the sprite spanned the middle row and the two rows
above it, one tile too high. (North/south arches were unaffected: their
48-wide sprite centers horizontally over a middle-column anchor.)

Fix: moved all five east/west arch chars down one row, onto the bottom row of
their openings — temple_darts west and east, temple_skeletons west,
temple_snakes east, and temple_astral_wind east. The vacated middle cell
became its plain threshold terrain ('∇'/'Δ'), so the doorway footprint,
collision, and exits are unchanged. In temple_astral_wind the cell below was
ordinary floor; the arch char's own `under="∇"` repaints that single cell as
walkable dark threshold, which reads as the doorway's shadow.

## Files Changed

- assets/maps/temple_darts.txt, temple_skeletons.txt, temple_snakes.txt,
  temple_astral_wind.txt: the one-row arch moves (applied by an
  assertion-checked script; no other cells touched).
- PROJECT_STATUS.md: session note plus a durable statement of the anchoring
  rule — east/west arches anchor on the BOTTOM row of their three-row
  openings — so future temple maps don't reintroduce the misalignment.

## Systems Added or Changed

- None. Map data only.

## Verification Performed

- All 42 test suites pass.
- Screenshots at all five east/west doorways confirm the dark opening now
  centers on the walkable path row (including the exact skeleton-chamber
  west door from the playtest report).
- Headless walk-through: stepping onto each MOVED arch tile still fires its
  transition — darts west -> snakes, darts east -> skeletons, skeletons
  west -> darts, snakes east -> darts.

## Known Issues

- None known from this pass.

## Scope Notes

- No future-phase work was intentionally implemented.
- No documented creative rules were intentionally changed.

## Recommended Next Bounded Task

- Build Temple Map 7 as the next broad/open room east of the narrow Astral
  wind connector, continuing the recurring arches (east/west arches anchored
  on the bottom opening row), torches, dressing language, one physical
  Ashtray, and shared-loader entry. Keep the slice distinct from the final
  chamber, Fireball, rubble escape, and Phase 7 ship.
