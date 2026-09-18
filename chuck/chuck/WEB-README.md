# Local browser prototype

The desktop launch remains `python main.py`. Development checkpoints are still
enabled and must be removed before announcing a release.

The GitHub Pages workflow publishes `main` to
https://rtrutabaga.github.io/CHUCK-game/. The repository owner must select
**GitHub Actions** once under **Settings → Pages → Source** before the first
deployment. The workflow can also be run manually from the Actions tab.

Use Python 3.12 from this directory:

```powershell
py -3.12 -m venv .venv-web
.venv-web\Scripts\python -m pip install -r requirements-web.txt
.venv-web\Scripts\python tools/build_web.py --serve
```

Open http://127.0.0.1:8000 and click the game canvas to start. Pygbag waits
for that gesture before launching the game so the browser can unlock audio.
The initial load needs internet access to fetch Pygbag's Python/pygame runtime.

For a build without a running server:

```powershell
.venv-web\Scripts\python tools/build_web.py
.venv-web\Scripts\python -m http.server 8000 --bind 127.0.0.1 --directory build/browser-app/build/web
```

The build stages only `main.py`, `src`, `data` and `assets` in
`build/browser-app`. WAV audio is replaced with OGG copies in that staging
directory. Original assets, local saves, tools, tests and the build environment
are not shipped. Generated output and `.venv-web` are ignored by Git.

## Current verification boundary

- Title, complete opening cutscene, automatic arrival on the playable docks,
  movement, jump and pause verified in the Chromium-based in-app browser.
  Runtime: Pygbag 0.9.3, CPython 3.12.12, pygame-ce 2.5.7 / SDL 2.28.4.
- The browser canvas preserves 16:9 at wide and tall viewport sizes. The
  in-game desktop fullscreen toggle is omitted; use browser fullscreen.
- Browser music replacement explicitly stops the previous stream before
  loading a new one. This fixes the opening hang while the title cue was
  still fading at the cutscene's 0.2-second music handoff.
- Browser mixer buffer is 2048 samples (~93 ms), giving audio more headroom
  during rendering than the desktop's 512 samples (~23 ms). This targets
  reported walking dropouts; listening confirmation is pending and sound
  effects may have slightly more latency.
- Use **127.0.0.1**, not `localhost`: Pygbag 0.9.3 treats the latter as a
  runtime-development host and tried to fetch pygame from a missing local
  `/cdn/` path in testing.
- After a rebuild, close the previous game tab and open the link again if
  normal reload does not replace the running game. A frozen old tab cannot
  repair itself when the files on disk change.
- The twelve-character save code is the complete save system. Keep it outside
  the browser if you want to resume later.
- A title-screen load of the known code `KMW9-J6ZP-2T5D` reaches its expected
  temple checkpoint in the browser. Broader traversal, measured frame rate,
  listening verification and other browsers remain to be checked. Pages
  deployment is defined in `.github/workflows/pages.yml`.

## Build measurements

41 WAV files (24 music, 17 effects): 87.5 MB before conversion, 10.4 MB of
Vorbis output. The compressed game archive is approximately 11.1 MB, excluding
the separately downloaded Python/pygame runtime. Conversion preserves each
file's frame count, sample rate and channel count; listening approval is still
pending. Encoding is streamed in 8192-frame blocks to avoid a Windows
libsndfile stack overflow on whole-track writes.
