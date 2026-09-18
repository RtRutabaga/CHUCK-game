"""Stage a browser-only copy, then package it with Pygbag.

Run from any directory: python tools/build_web.py
Add --serve to build and serve locally at http://127.0.0.1:8000.
Desktop WAV masters and save files are never included or modified.
"""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "build" / "browser-app"


def finalize_web_artifact(web: Path) -> None:
    """Apply CHUCK's host-specific additions to Pygbag's static output."""
    page = web / "index.html"
    # Override the stock template's independent width/height scaling. SDL
    # retains a fixed framebuffer; CSS fits it into the browser viewport.
    style = """<style>
html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #000 !important; }
#canvas { width: min(100vw, 177.777778vh) !important;
          height: min(100vh, 56.25vw) !important;
          position: fixed !important; inset: 0 !important;
          margin: auto !important; border: 0 !important;
          image-rendering: pixelated; }
</style>"""
    page.write_text(page.read_text(encoding="utf-8") + style, encoding="utf-8")
    # Pages otherwise runs Jekyll, which can omit Pygbag runtime files whose
    # names begin with an underscore.
    (web / ".nojekyll").touch()


def stage() -> Path:
    import soundfile as sf

    if not STAGE.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError(f"Staging directory escapes the project: {STAGE}")
    STAGE.mkdir(parents=True, exist_ok=True)
    for name in ("src", "data", "assets"):
        target = STAGE / name
        if target.exists():
            if target.resolve().parent != STAGE.resolve():
                raise ValueError(f"Unsafe staging path: {target}")
            shutil.rmtree(target)
        shutil.copytree(ROOT / name, target,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.wav"))
    shutil.copy2(ROOT / "main.py", STAGE / "main.py")
    total_source = total_web = 0
    for source in sorted((ROOT / "assets" / "audio").rglob("*.wav")):
        target = (STAGE / source.relative_to(ROOT)).with_suffix(".ogg")
        # Bounded writes avoid libsndfile's Windows Vorbis stack overflow
        # on a whole music track, and keep conversion memory constant.
        with sf.SoundFile(source) as original:
            with sf.SoundFile(target, "w", samplerate=original.samplerate,
                              channels=original.channels, format="OGG",
                              subtype="VORBIS") as encoded:
                for samples in original.blocks(blocksize=8192):
                    encoded.write(samples)
        total_source += source.stat().st_size
        total_web += target.stat().st_size
    print(f"Audio: {total_source / 1e6:.1f} MB WAV -> {total_web / 1e6:.1f} MB OGG", flush=True)
    return STAGE


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    directory = stage()
    command = [sys.executable, "-m", "pygbag", "--no_opt", "--title", "CHUCK"]
    command.append("--build")
    subprocess.run([*command, str(directory)], check=True)
    web = directory / "build" / "web"
    finalize_web_artifact(web)
    print(f"Browser files: {web}", flush=True)
    if args.serve:
        subprocess.run([sys.executable, "-m", "http.server", "8000",
                        "--bind", "127.0.0.1", "--directory", str(web)], check=True)


if __name__ == "__main__":
    main()
