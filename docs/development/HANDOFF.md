# Agent Handoff

## Repository State

- Branch: main
- Base commit: `8a62fb3` (`Package the demo for Windows`)
- Current work: title menu, persistent saves, and shared checkpoint loading
- Active phase: Phase 3 - Waterdeep Tavern, Pantry, and Fall to Chult

## Completed This Pass

CHUCK now opens on a restrained 320x180 title screen with NEW GAME and a
save-aware CONTINUE. A temporary visible DEV CHECKPOINTS option exposes the
currently authored test entries. All three entry paths call the same checkpoint
loader; there is no separate debug teleport implementation.

## Architecture

- `systems/checkpoints.py` owns immutable checkpoint definitions, the single
  known progress flag (`sewer_completed`), current progress state, save
  validation, and `CheckpointLoader.load_checkpoint(checkpoint_id)`.
- `systems/save.py` owns one atomic, versioned JSON slot. Version 1 contains:
  `version`, `checkpoint_id`, `sanity`, and sorted `progress_flags`. Runtime
  scenes, entities, enemies, animation, camera, and map data are rebuilt.
- The default Windows path is `%LOCALAPPDATA%\CHUCK\save.json`; tests inject
  temporary paths. Missing, malformed, outdated, semantically unknown, and
  development-only checkpoint records are treated as no valid save.
- NEW GAME deletes the old slot, resets progress, and loads
  `waterdeep_start`. CONTINUE reads a valid Anchor save and calls the same
  loader with its saved Sanity and flags.
- Map entry and named-arrival definitions formalize existing local respawn
  behavior without writing saves. The `A` and `Y` map markers now carry stable
  `waterdeep_anchor` and `sewer_anchor` IDs; touching either updates active
  runtime state and writes the save.
- Sanity persists across ordinary map transitions. Sanity-zero still uses the
  same quiet vanish/starfield/return choreography and returns to the current
  local map-entry or activated Ashtray checkpoint with full Sanity.
- `TitleScene` and `CheckpointSelectScene` use the existing bitmap font, input,
  SFX, SceneManager, and native render surface. Set
  `config.ENABLE_DEV_CHECKPOINT_SELECTOR = False` to remove the temporary menu.

## Development Checkpoints

The visible selector entries are:

1. Waterdeep 1 (`waterdeep_start`)
2. Waterdeep Ashtray (`waterdeep_anchor`)
3. Sewer 1 (`sewer_entrance`)
4. Sewer 2 (`sewer_anchor`)
5. Waterdeep 2 (`waterdeep_return`, with `sewer_completed`)
6. Tavern 1 (`tavern_entry`, with `sewer_completed`)
7. Pantry 1 (`pantry_entry`, with `sewer_completed`)

No Chult entry exists because Phase 3 contains no playable Chult map. Two
additional hidden registry entries preserve the tavern/docks and pantry/tavern
return-arrival retry positions, plus hidden default spawns used by direct scene
construction in tests.

## Verification

- All 22 test suites pass.
- Targeted coverage verifies no-save startup; disabled CONTINUE; NEW GAME
  deletion/reset; readable atomic version-1 JSON; graceful invalid/outdated
  handling; Anchor save; close/relaunch/CONTINUE restoration; restored tavern
  exterior; saved Sanity; Sanity-zero Anchor respawn; rejection of forged
  development saves; all seven visible development loads; required late-game
  progression; and shared-loader dispatch from both real and development menus.
- Native 2x visual review confirms both menus are crisp, readable, and fit the
  established 1994-style presentation.

## Playtest Focus

1. Remove/rename any existing save, launch, and confirm CONTINUE is dimmed and
   skipped by the caret.
2. Select NEW GAME and confirm Chuck starts beside Bobert at Waterdeep Docks.
3. Touch the Waterdeep Ashtray, quit, relaunch, and confirm CONTINUE restores
   that Ashtray and the saved Sanity value.
4. Progress through the sewer, touch its late Ashtray, quit, and confirm
   CONTINUE restores the Sewer 2 checkpoint and normal enemy layout.
5. Reach Waterdeep after the sewer, then touch the Waterdeep Ashtray again;
   relaunch and confirm the tavern exterior is still open.
6. Deplete Sanity after each Anchor and confirm the existing quiet return lands
   at the active local checkpoint with enemies reset and full Sanity.
7. From the title screen choose DEV CHECKPOINTS. Load every visible entry and
   verify Waterdeep 2, Tavern 1, and Pantry 1 all have the post-sewer open-door
   progression required to function.
8. Complete the normal Phase 3 route from NEW GAME through the held jungle
   tableau to ensure the title/save infrastructure caused no transition drift.

## Next Bounded Task

Human-playtest the title, save slot, both Ashtray saves, and every development
entry. Fix only demonstrated restoration or presentation defects; do not begin
playable Chult until Phase 4 scope is active.
