# Local browser prototype

This is a development build, not a published release. The desktop launch
remains `python main.py`. Development checkpoints are still enabled.

Use Python 3.12 from this directory:

```powershell
py -3.12 -m venv .venv-web
.venv-web\Scripts\python -m pip install -r requirements-web.txt
.venv-web\Scripts\python tools/build_web.py --serve
```

Open http://localhost:8000 and click the game canvas to start. Pygbag waits
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

- Real browser title launch verified with Pygbag 0.9.3, CPython 3.12.12,
  pygame-ce 2.5.7 and SDL 2.28.4.
- NEW GAME produced a runtime error during the initial browser test. The
  browser connection was lost before its traceback could be inspected.
  Browser errors now also go to the JavaScript console for the next test.
- Opening-map play, transitions, FPS, audible sound and save-code entry in
  the browser still need verification. See the Baton in
  `../../docs/development/HANDOFF.md` for the latest state.
- Browser local saves/settings are currently temporary. Keep the displayed
  save code; do not rely on CONTINUE surviving a page reload.
- Browser fullscreen, persistent storage and GitHub Pages deployment remain
  separate work under `../../docs/development/WEB-BUILD.md`.

## Build measurements

41 WAV files (24 music, 17 effects): 87.5 MB before conversion, 10.4 MB of
Vorbis output. The compressed game archive is approximately 11.1 MB, excluding
the separately downloaded Python/pygame runtime. Conversion preserves each
file's frame count, sample rate and channel count; listening approval is still
pending. Encoding is streamed in 8192-frame blocks to avoid a Windows
libsndfile stack overflow on whole-track writes.
