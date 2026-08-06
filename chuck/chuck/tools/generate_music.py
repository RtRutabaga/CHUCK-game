"""Render an area theme to WAV.

Run from the project root (pure stdlib):

    python tools/generate_music.py                 # the docks theme
    python tools/generate_music.py sewer           # the sewer theme
    python tools/generate_music.py fall_to_chult   # the cutscene cue
    python tools/generate_music.py chult            # the Chult jungle theme
    python tools/generate_music.py temple           # the temple interior theme
    python tools/generate_music.py zephyros_tower   # Phase 10 airy tower cue
    python tools/generate_music.py zephyros_conversation  # warm giant cue

Reads the composition from data/music/<name>.py, renders it through
src/audio (sequencer + instruments + synth), and writes
assets/audio/music/<name>.wav. Note tails wrap around the song end, so
the loop point is seamless.
"""

import importlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.audio.sequencer import render_song
from src.audio.synth import SAMPLE_RATE, write_wav


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "waterdeep_docks"
    song = importlib.import_module(f"data.music.{name}")
    t0 = time.time()
    tracks = song.build_tracks()
    print(f"Rendering {name}: {song.TOTAL_BARS} bars at {song.TEMPO_BPM} "
          f"BPM, {len(tracks)} voices, "
          f"{sum(len(t.notes) for t in tracks)} notes...")
    headroom = getattr(song, "MASTER_HEADROOM", 0.75)
    master = render_song(
        song.TEMPO_BPM, song.TOTAL_BEATS, tracks, headroom=headroom
    )
    out = ROOT / "assets" / "audio" / "music" / f"{name}.wav"
    write_wav(out, master)
    print(f"Wrote {out} ({len(master) / SAMPLE_RATE:.1f}s "
          f"in {time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
