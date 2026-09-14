"""The end credits theme: the Fall to Chult cue, as upbeat ska."""

import os
import struct
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from data.music import credits_ska as song
from data.music import fall_to_chult as fall_song
from src.audio.sequencer import note_to_freq
from src.audio.synth import SAMPLE_RATE
from src.core import config
from src.scenes import credits_scene


def _track(name: str):
    return next(t for t in song.build_tracks() if t.name == name)


def _bar_notes(track, bar: int):
    start = bar * song.BEATS_PER_BAR
    return sorted((n for n in track.notes
                   if start <= n.beat < start + song.BEATS_PER_BAR),
                  key=lambda n: (n.beat, n.pitch))


def test_it_is_fast_full_and_every_note_is_in_the_song() -> None:
    assert song.TEMPO_BPM >= 150  # ska, not a sway
    duration = song.TOTAL_BEATS * 60.0 / song.TEMPO_BPM
    assert 90 <= duration <= 130
    tracks = song.build_tracks()
    assert len([t for t in tracks if t.notes]) >= 9
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)
            assert 0 <= note.beat < song.TOTAL_BEATS, (track.name, note)


def test_the_skank_is_on_the_offbeat() -> None:
    for name in ("organ", "guitar"):
        track = _track(name)
        assert len(track.notes) > 400
        for note in track.notes:
            within = note.beat % 1.0
            assert 0.45 <= within <= 0.55, (name, note)
    # Hats chop the offbeats loudest; snare on two and four.
    snare = _track("snare")
    for bar in song.A:
        backbeats = {n.beat % 4 for n in _bar_notes(snare, bar)
                     if n.beat % 1 == 0}
        assert backbeats == {1.0, 3.0}, bar


def test_the_horns_play_the_fall_cues_own_lead() -> None:
    fall_lead = next(t for t in fall_song.build_tracks() if t.name == "lead")
    fall_bars = {}
    for note in fall_lead.notes:
        fall_bars.setdefault(int(note.beat // 4), []).append(note)
    horns = _track("horns")
    for index, fall_bar in enumerate((0, 2, 4, 6)):
        ska_bar = song.A.start + index * 2
        expected = [
            (round(n.beat % 4, 3), note_to_freq(n.pitch) / 2)
            for n in sorted(fall_bars[fall_bar], key=lambda n: n.beat)]
        played = [(round(n.beat % 4, 3), note_to_freq(n.pitch))
                  for n in _bar_notes(horns, ska_bar)]
        assert len(played) == len(expected)
        for (beat, freq), (want_beat, want_freq) in zip(played, expected):
            assert beat == want_beat
            assert abs(freq - want_freq) < 0.5


def test_same_key_and_chords_as_the_fall_with_a_major_lift() -> None:
    # The fall's opening progression, Dm-Bb-C-Am then Dm-F-C-Am.
    fall_roots = [r.rstrip("0123456789") for r in fall_song._ROOTS[:8]]
    ska_roots = [c.rstrip("m") for c in song.CHORDS[4:12]]
    assert ska_roots == fall_roots
    # Its chromatic Eb turns up in the breakdown...
    assert "Eb" in song.CHORDS[song.BREAK.start:song.BREAK.stop]
    # ...and the middle lifts into the relative major.
    assert song.CHORDS[song.B.start] == "F"


def test_rendered_theme_loops_cleanly_and_does_not_clip() -> None:
    with wave.open(str(config.MUSIC_DIR / "credits_ska.wav")) as f:
        assert f.getframerate() == SAMPLE_RATE and f.getnchannels() == 1
        raw = f.readframes(f.getnframes())
    samples = [x / 32767 for (x,) in struct.iter_unpack("<h", raw)]
    assert len(samples) >= 90 * SAMPLE_RATE
    peak = max(abs(s) for s in samples)
    assert peak <= 0.92, f"clipping risk: peak {peak:.2f}"
    assert abs(samples[-1] - samples[0]) < 0.15, "audible loop seam"
    rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    assert rms > 0.1, "an upbeat band, not an ambience"


def test_the_credits_play_it() -> None:
    assert credits_scene.CREDITS_MUSIC == "credits_ska.wav"
    assert (config.MUSIC_DIR / credits_scene.CREDITS_MUSIC).is_file()
