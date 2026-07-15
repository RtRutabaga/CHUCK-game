# Agent Handoff

## Repository State

- Branch: main
- Base commit: `983bcd3` (`Score the fall-to-Chult cutscene`)
- Current work: shareable single-file Windows demo build
- Active phase: Phase 3 - Waterdeep Tavern, Pantry, and Fall to Chult

## Completed This Pass

The current Phase 3 demo now builds as a portable `CHUCK-demo.exe` containing
the game, Pygame runtime, maps, art, dialogue, music, and sound. Recipients do
not need Python or the repository.

## Implementation

- Added `CHUCK.spec`, a reproducible PyInstaller 6.21 one-file/windowed build
  that mirrors `assets/` and `data/` at the paths expected by `config.py`.
- Added `requirements-build.txt` and Windows build instructions to the README.
- The spec excludes optional NumPy and OpenGL helpers that CHUCK never uses,
  reducing the tested EXE from 36.3 MB to 25.1 MB.
- Frozen builds now place `crash_log.txt` beside the executable. Source runs
  retain the existing project-root crash location.
- `build/` and `dist/` are ignored generated output; the current shareable file
  remains locally available at `dist/CHUCK-demo.exe`.

## Verification

- All 21 test suites pass.
- New packaging tests cover source and frozen crash-log paths plus the bundle's
  resource-root contract.
- PyInstaller completed cleanly on Windows 11 with Python 3.12 and Pygame CE
  2.5.7. The actual optimized EXE was launched with dummy video/audio drivers,
  held its game loop for six seconds, and produced no crash log.
- Built artifact: `dist/CHUCK-demo.exe`, 25,132,589 bytes.

## Playtest Focus

- Double-click `dist/CHUCK-demo.exe` from outside the source tree and verify the
  real window, controller/keyboard input, music, and SFX on a normal device.
- Copy only the EXE to another Windows machine or folder and complete the demo
  path through the held jungle tableau.
- Expect an unsigned-build SmartScreen warning. If an actual crash occurs,
  collect the `crash_log.txt` created beside the EXE.

## Next Bounded Task

Run the complete Phase 3 path from a clean save and tune only demonstrated
timing/readability defects. Once accepted, begin Phase 4 from the held jungle
tableau under the Phase 4 scope; do not retrofit playable Chult into this scene.
