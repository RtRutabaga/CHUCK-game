"""Render the Waterdeep Docks theme to WAV.

Run from the project root (pure stdlib):

    python tools/generate_music.py

Reads the composition from data/music/waterdeep_docks.py, renders it
through src/audio (sequencer + instruments + synth), and writes
assets/audio/music/waterdeep_docks.wav. Note tails wrap around the
song end, so the loop point is seamless.
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from data.music import waterdeep_docks as song
from src.audio.sequencer import render_song
from src.audio.synth import SAMPLE_RATE, write_wav


def main() -> None:
    t0 = time.time()
    tracks = song.build_tracks()
    print(f"Rendering {song.TOTAL_BARS} bars at {song.TEMPO_BPM} BPM, "
          f"{len(tracks)} voices, "
          f"{sum(len(t.notes) for t in tracks)} notes...")
    master = render_song(song.TEMPO_BPM, song.TOTAL_BEATS, tracks)
    out = ROOT / "assets" / "audio" / "music" / "waterdeep_docks.wav"
    write_wav(out, master)
    print(f"Wrote {out} ({len(master) / SAMPLE_RATE:.1f}s "
          f"in {time.time() - t0:.1f}s)")


if __name__ == "__main__":
    main()
