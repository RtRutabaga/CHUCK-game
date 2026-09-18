# Web Build — CHUCK in a browser, hosted on GitHub Pages

Status: **local build foundation and opening browser fixes verified; broader
traversal and release checks remain.** Read the Baton in `HANDOFF.md` for current results. The build
instructions are in `../../chuck/chuck/WEB-README.md`. Section 2 below records
the original incoming state, not a claim that those files remain uncommitted.

This is a technical contract for running the existing game in a browser
and publishing it from this repository. It is written to be executed by
an agent (Codex or Claude Code) one slice at a time.

## What this is not

This is **not** Phase 15 and it does not open Phase 15.
`docs/development/CURRENT-PHASE.md` gates new phases on Sean adding an
authoritative contract, and that still holds. Nothing here changes game
content, a creative decision, a control, the scale, or a rule. If a step
appears to require one of those, stop and report — that is a stop
condition under `AGENTS.md`, not a small technical choice.

The desktop game is the reference build. Every step must leave
`python main.py` on Windows behaving exactly as it does today.

## Authority

`AGENTS.md` first, then this file for the web work only. Where this file
and a design document disagree about the game itself, the design
document wins and the web work bends around it.

---

## 1. Target

- **Toolchain:** [pygbag](https://pypi.org/project/pygbag/) — pygame-ce
  packaged as CPython compiled to WebAssembly, emitting a static site. It
  is the only maintained path for pygame-ce in a browser.
- **Host:** GitHub Pages on this repository, built by GitHub Actions.
- **URL shape:** `https://<owner>.github.io/CHUCK-game/`. The repository
  moved from `SeanKerr9876` to `RtRutabaga` on 2026-09-18, so the owner
  half is `rtrutabaga` unless it moves again. Confirm against the live
  remote before writing it into a workflow or a README.
- **Added dependencies:** build-time only, in `requirements-web.txt`,
  never imported by the game and never in `requirements.txt`.

---

## 2. Original incoming state — the unfinished prototype

When this contract was written, the working tree carried a web pass that was
**not in any commit**. Before starting, run `git status` and reconcile.
Do not duplicate this work, and do not commit it as part of something
else without reading it.

| File | State |
| --- | --- |
| `src/core/game.py` | `run_async()` added beside `run()`: same frame body, `await asyncio.sleep(0)` per frame, `_shutdown()` in a `finally`. |
| `main.py` | Branches on `sys.platform == "emscripten"`; browser path sets `imageRendering = "pixelated"` on the canvas. |
| `src/core/runtime.py` | New. `audio_path()` swaps `.wav` for `.ogg` under emscripten. |
| `src/systems/audio.py`, `src/core/assets.py` | Route audio through `audio_path()`. |
| `tools/build_web.py` | Stages a browser-only copy and runs pygbag. Has a `--serve` mode. |
| `requirements-web.txt` | `pygbag==0.9.3`, `soundfile==0.14.0`. |
| `tests/test_browser_runtime.py` | New. |

**Not started at all:** everything in §4 and §5 — browser save
persistence, the display/fullscreen difference, audio's first-gesture
problem, and the entire publishing half. There is no `.github/`
directory in this repository.

Per `AGENTS.md`, only one coding agent changes things at a time. If that
uncommitted work is someone else's in-flight pass, leave it alone and say
so rather than building on top of it.

---

## 3. What the codebase already had going for it

Verified against the tree, not assumed:

| Thing | Why it matters |
| --- | --- |
| Save codes (`src/systems/save_code.py`) | Twelve characters carry a whole save. This is the browser's real save story — a lost browser profile does not lose the game. |
| Clipboard wrapper (`src/systems/clipboard.py`) | `pygame.scrap` is absent in wasm. `copy()` returns `False`, `paste()` returns `None`, and the menu already falls back to "write it down". |
| Controller guard (`src/core/input.py:128`) | `from pygame._sdl2 import controller` is already inside `try/except (ImportError, pygame.error)`. |
| No threads, no `subprocess`, no `input()`, no `time.sleep` | All fatal or blocking under wasm. The game uses none of them. |
| Language level | All of `src/` and `main.py` parse as 3.11 grammar (`ast.parse(..., feature_version=(3, 11))`). pygbag ships an older CPython than the 3.14 used locally. |
| Lazy asset loading (`src/core/assets.py`) | Images and sounds load on first use, not all at boot. |

**Dependency:** the save-code work lives on the `save-codes` branch and
is not merged to `main`. The browser build is not worth publishing
without it — a browser game whose only save is a file in a wasm
filesystem is a browser game with no save.

---

## 4. What still has to be solved

### 4.1 The save file has nowhere to go — **cancelled, 2026-09-18**

Not being done. Sean's decision: the save code is the only save, and
CONTINUE and the local file are being removed, so there is nothing to
persist in a browser. See `DECISIONS.md`. The original plan follows for
the record.

#### Original plan (not being built)

`src/systems/save.py:default_save_path()` resolves `LOCALAPPDATA` or
`XDG_DATA_HOME`. Neither exists in wasm, and the emscripten filesystem is
in memory: it dies with the tab. There is no `emscripten` branch in
`save.py` today.

**Fix, in order of preference:**

1. Keep `SaveSystem` as it is and, on web, point it at a path under an
   IndexedDB-backed mount so `CONTINUE` survives a reload. Needs an
   explicit sync after each write — an unsynced IDBFS write is lost.
2. If that proves unreliable across browsers, put the record in
   `localStorage` through `platform.window`, behind the same
   `SaveSystem` interface.

Either way the **save code is the guarantee** and IndexedDB is only the
convenience. If the local save cannot be written, say so in the UI: the
player should learn to keep their code, not find out the hard way.

### 4.2 Audio cannot start before a user gesture (not started)

Browsers refuse audio until the player interacts. `AudioSystem.__init__`
calls `pygame.mixer.init()` at boot; `play_music()` streams per area.

`AudioSystem` already degrades — `self.enabled` goes `False` and
everything becomes a no-op when the mixer will not start — so this should
not crash. But the title theme will be silent and may stay silent.
**Fix:** on web, defer the first `play_music` until the first input
event, then let the normal area cue take over. Silence until the first
key press is acceptable; silence for the whole session is not.

### 4.3 The window is opened and reopened (not started)

`src/core/game.py:_open_window` asks for `RESIZABLE`, `vsync=1`, and
`(0, 0) + FULLSCREEN`, and `set_fullscreen` **recreates** the window.
Under wasm the display is set once; recreating it is unreliable.

**Fix:** on emscripten open one fixed-size window and make
`set_fullscreen` a no-op, or route F11 to the browser's own fullscreen
through `platform.window`. The pause menu's FULLSCREEN row should be
absent on web rather than offering something that does nothing.

### 4.4 Audio weight — verify the encode

Measured on the desktop assets:

- 24 tracks, 32.9 minutes total, **87.1 MB** of WAV
- all 22050 Hz, mono, 16-bit
- 43 audio files are tracked in git; `.git` is 155 MB largely because of them
- sfx are fine: 17 files, 416 KB

The WAVs are *derived* — `tools/generate_music.py` renders them from
`data/music/*.py`, one source per track — so the web build may encode its
own copies without touching the desktop assets. `tools/build_web.py`
already does this via `soundfile`.

What has **not** been done is checking the result. Bitrate arithmetic for
32.9 minutes:

| bitrate | total |
| --- | --- |
| 48 kbps mono | ~11.8 MB |
| 64 kbps mono | ~15.8 MB |
| 96 kbps mono | ~23.7 MB |

That is arithmetic, not encoder output. This is synth material at 22 kHz,
where Vorbis may do considerably better or noticeably worse. Encode, weigh
the real total, **listen**, and record the choice in
`docs/development/DECISIONS.md`. The soundtrack has its own authority
(`design/CHUCK-SOUNDTRACK-BIBLE.md`): if a bitrate audibly damages the
music, that is no longer a technical choice. Raise it.

**Do not** shorten or re-render loops to save bytes. That changes the
music.

---

## 5. Publishing — workflow prepared, activation pending

`.github/workflows/pages.yml` builds the browser artifact on `main`, uploads it,
and deploys it to the `github-pages` environment. The generated artifact now
includes `.nojekyll`.

- Repository Settings → Pages → Source = **GitHub Actions** (not a
  branch). Must be set by hand once; a workflow cannot enable it.
- Workflow: build with pygbag, then `actions/upload-pages-artifact`
  followed by `actions/deploy-pages`. Needs
  `permissions: {pages: write, id-token: write}`.
- ~~Add **`.nojekyll`** to the published artifact.~~ **Done 2026-09-18.**
  Without it Pages runs
  Jekyll and silently drops files and directories beginning with `_`,
  which pygbag emits. `tools/build_web.py` creates it after each build.
- The site is served from a subpath (`/CHUCK-game/`), so every asset
  reference must be relative. Check pygbag's generated HTML for absolute
  `/` paths.
- **Cross-origin isolation is not required** (checked 2026-09-18 against
  the local build: `crossOriginIsolated === false`, `SharedArrayBuffer`
  undefined, game running). Pages needs no COOP/COEP headers, which it
  could not set anyway.
- **Relative paths are already correct** for a `/CHUCK-game/` subpath:
  `index.html` references `favicon.png` and `browser-app.apk` relatively
  and carries no leading-slash asset paths. Re-check after any pygbag
  upgrade.
- **The runtime is fetched from a third-party CDN** at play time —
  `https://pygame-web.github.io/cdn/0.9.3/…` for `pythons.js`,
  `browserfs.min.js` and CPython 3.12. Pages hosts our game; it does not
  host the interpreter. If that CDN is down or gone, the published game
  does not start. Sean should know this before it is announced anywhere.
- Pages limits: 1 GB published site (soft), 100 MB per file (hard), 100
  GB/month bandwidth (soft). §4.4 is what keeps us clear.

---

## 6. Order of the remaining work

Each step is a commit that leaves the desktop game running and the suite
green. Do not start the next until the previous is verified.

0. **Reconcile** the uncommitted pass in §2 — finish it, commit it, or
   set it aside. Record which in `HANDOFF.md`.
1. **Local build and a real play test.** Build, open it, play from the
   title through the docks, the sewer, and one map transition. Record the
   load time and frame rate in `HANDOFF.md`. If it will not hold 60 fps
   at 320×180, stop and report before optimising — the fix may be a
   design question.
2. **Audio** — §4.2, and weigh and listen to the encode per §4.4.
3. **Display** — §4.3.
4. **Saves** — §4.1.
5. **Publish** — §5.
6. **Document** — `docs/README.md`, `HANDOFF.md`, `DECISIONS.md`, and a
   "Play in a browser" line in the root `README.md`.

---

## 6b. Where verification can happen

Claude Code's in-app browser pane **cannot** be used to judge this build.
It runs the wasm game at roughly 1.4 fps with multi-second frames, so
both the timing reporter's numbers and any interactive play are
meaningless there. It is fine for one-shot checks that do not depend on
the loop running at speed — does it load, what does `index.html`
reference, is the context cross-origin isolated.

Frame rate, traversal, transitions and the save-code round trip need a
real foreground browser. That is Sean's machine, or an agent with one.
Do not report a performance figure measured in the pane.

---

## 7. Risks, ranked by how likely they are to sink the effort

1. ~~**Cross-origin isolation.**~~ **Answered 2026-09-18: not required.**
   The local build ran with `crossOriginIsolated === false` and
   `SharedArrayBuffer` undefined. Pages is viable.
2. **pygame-ce feature gap** in pygbag's bundled build. Find out early:
   record pygbag's CPython and pygame-ce versions in `HANDOFF.md` on the
   first successful build.
3. **Performance.** 320×180 scaled up, y-sorted draws, up to ~4000 astral
   tiles on the largest maps. Unknown under wasm until step 1.
4. **Audio quality** at whatever bitrate survives §4.4.
5. **IndexedDB persistence** being flaky across browsers. Mitigated by
   the save codes already existing.

---

## 8. Definition of done

- Playable at the Pages URL from a cold browser profile.
- Title → NEW GAME → the docks → the sewer → a map transition, at a
  steady frame rate.
- SAVE GAME produces a code; LOAD CODE on the title accepts one; a
  reload plus CONTINUE resumes.
- First load is well under the Pages per-file limit; the total is
  recorded in `HANDOFF.md`.
- `python main.py` on Windows is unchanged.
- The full suite is green. Run it the way the repo already does; do not
  add a second test runner for the web build.
- No game content, control, scale or rule has changed.

---

## 9. Stop conditions specific to this work

Stop and report instead of continuing when:

- The desktop build cannot be kept working alongside the web build.
- Running in a browser would require changing controls, the native
  resolution, the soundtrack, or any game rule.
- Cross-origin isolation turns out to be required.
- The audio budget can only be met by shortening or re-arranging music.
- pygbag's bundled pygame-ce lacks something the game relies on.
- Another agent's uncommitted work is in the tree (§2).

None of these are for an agent to decide alone.
