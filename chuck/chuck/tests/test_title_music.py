"""The title screen's music: space ambience, and very quiet.

What makes it ambient rather than just slow is tested as a set of
properties of the score, because "subtle" is the whole brief and every
one of these is a way it could stop being subtle: a beat, a melody, too
many notes, two bells at once, or a stream loud enough to compete with
the menu.
"""

import math
import os
from pathlib import Path
import struct
import tempfile
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from data.music import title as song
from src.audio import instruments as ins
from src.core import config
from src.core.game import Game
from src.scenes.title_scene import TITLE_MUSIC, TitleScene


TRACK = config.MUSIC_DIR / "title.wav"


def _samples() -> tuple[list[int], int]:
    with wave.open(str(TRACK), "rb") as handle:
        rate = handle.getframerate()
        frames = handle.readframes(handle.getnframes())
    return list(struct.unpack(f"<{len(frames) // 2}h", frames)), rate


def test_the_score_is_slow_sparse_and_has_no_beat() -> None:
    tracks = song.build_tracks()
    duration = song.TOTAL_BEATS * 60.0 / song.TEMPO_BPM
    assert song.TEMPO_BPM <= 66
    assert duration >= 90.0
    percussion = {ins.kick, ins.snare, ins.hat, ins.timpani, ins.jungle_tom,
                  ins.woodblock, ins.tabla_dayan, ins.tabla_bayan,
                  ins.metal_hit}
    assert not any(track.instrument in percussion for track in tracks)
    # Sparse. The chords move no more often than every eight seconds
    # (their voices bloom in a fraction of a beat apart, which is one
    # chord, not four notes), and everything that is not a chord or the
    # drone adds up to fewer than one sound every four seconds.
    named = {track.name: track for track in tracks}
    seconds_per_beat = 60.0 / song.TEMPO_BPM
    chord_starts = []
    for beat in sorted(note.beat for note in named["pad"].notes):
        if not chord_starts or beat - chord_starts[-1] > 2.0:
            chord_starts.append(beat)
    changes = [(b - a) * seconds_per_beat
               for a, b in zip(chord_starts, chord_starts[1:])]
    assert min(changes) >= 8.0, min(changes)
    extras = sum(len(track.notes) for name, track in named.items()
                 if name not in ("pad", "drone"))
    assert extras / duration < 0.25, extras / duration


def test_it_is_carried_by_long_pads() -> None:
    """Most of the sound is chords that take seconds to arrive."""
    named = {track.name: track for track in song.build_tracks()}
    pad = named["pad"]
    assert pad.instrument is ins.cloud_pad
    assert all(note.dur >= 6.0 for note in pad.notes)
    # Every chord is still sounding when the next one starts: no gaps.
    starts = sorted({note.beat for note in pad.notes if note.vel > 0.5})
    for first, second in zip(starts, starts[1:]):
        longest = max(n.dur for n in pad.notes if n.beat == first)
        assert first + longest > second, (first, second)


def test_the_stars_never_twinkle_together() -> None:
    """One bell at a time, irregularly: a bell every bar is a clock."""
    stars = sorted(song.build_tracks(), key=lambda t: t.name != "stars")[0]
    assert stars.name == "stars"
    beats = sorted(note.beat for note in stars.notes)
    gaps = [b - a for a, b in zip(beats, beats[1:])]
    assert min(gaps) >= 4.0, min(gaps)
    assert len(set(round(gap, 2) for gap in gaps)) > len(gaps) // 2


def test_rendered_loop_meets_the_gates() -> None:
    data, rate = _samples()
    duration = len(data) / rate
    peak = max(abs(sample) for sample in data) / 32768
    rms = math.sqrt(sum(s * s for s in data) / len(data)) / 32768
    assert duration >= 60.0
    assert peak <= 0.9
    assert abs(data[-1] - data[0]) / 32768 < 0.15
    # Quiet in the file as well as in the mix.
    assert rms < 0.15, rms


def test_it_plays_quietly_on_the_title() -> None:
    assert config.MUSIC_TRIM.get(TITLE_MUSIC, 1.0) <= 0.6
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        played = []
        game.audio.play_music = lambda name, loop=True: played.append(
            (name, loop))
        game.scenes.replace(TitleScene(game))
        assert played == [(TITLE_MUSIC, True)]
        assert game.audio.volume_for(TITLE_MUSIC) < config.AUDIO_MUSIC_VOLUME
        assert TRACK.is_file()
    finally:
        game._shutdown()
        directory.cleanup()


def _run_all() -> None:
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"  PASS  {name}")
            except AssertionError as exc:
                failures += 1
                print(f"  FAIL  {name}: {exc}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All title music tests passed.")


if __name__ == "__main__":
    _run_all()
