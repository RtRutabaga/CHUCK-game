"""Small platform differences shared by asset loaders."""

from pathlib import Path
import sys


def audio_path(path: Path) -> Path:
    """Web builds ship OGG copies; authored cue names keep their WAV keys."""
    return path.with_suffix(".ogg") if sys.platform == "emscripten" else path
