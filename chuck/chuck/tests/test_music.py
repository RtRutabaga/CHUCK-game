"""Unit tests for the sequencer and the Waterdeep Docks theme.

Run from the project root with:

    python -m tests.test_music       (pure stdlib, no dependencies)
    pytest                           (if you have pytest)

The composition tests turn the Soundtrack Bible's minimum standard for
the Waterdeep theme into executable checks.
"""

import struct
import wave

from data.music import fall_to_chult as fall_song
from data.music import sewer as sewer_song
from data.music import waterdeep_docks as song
from src.audio.sequencer import Note, Track, note_to_freq, render_song
from src.audio.synth import SAMPLE_RATE
from src.core import config


def test_note_to_freq_landmarks() -> None:
    assert abs(note_to_freq("A4") - 440.0) < 1e-6
    assert abs(note_to_freq("A5") - 880.0) < 1e-6
    assert abs(note_to_freq("C4") - 261.626) < 0.01
    assert abs(note_to_freq("F#4") - note_to_freq("Gb4")) < 1e-9


def test_sequencer_places_notes_at_their_beat() -> None:
    marker = lambda hz, sec, vel: [1.0] * 10
    out = render_song(60, 4, [Track("t", marker, 1.0, [Note(2, 1, "A4")])],
                      headroom=1.0)
    start = 2 * SAMPLE_RATE
    assert out[start] == 1.0 and out[start - 1] == 0.0


def test_sequencer_wraps_tails_for_seamless_loops() -> None:
    tail = lambda hz, sec, vel: [0.5] * (SAMPLE_RATE // 2)
    out = render_song(60, 2, [Track("t", tail, 1.0,
                                    [Note(1.75, 0.25, "A4")])], headroom=1.0)
    assert out[0] != 0.0, "tail did not wrap to the start"


def test_sequencer_rejects_notes_past_the_end() -> None:
    try:
        render_song(60, 2, [Track("t", lambda *a: [0.0], 1.0,
                                  [Note(5, 1, "A4")])])
    except ValueError as exc:
        assert "past the song end" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_theme_meets_the_soundtrack_bible_bar() -> None:
    tracks = song.build_tracks()
    duration = song.TOTAL_BEATS * 60.0 / song.TEMPO_BPM
    assert duration >= 60.0, "theme must run 60+ seconds before repeating"
    voiced = [t for t in tracks if t.notes]
    assert len(voiced) >= 4, "theme needs at least four voices"
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)  # every pitch must parse
            assert 0 <= note.beat < song.TOTAL_BEATS, (track.name, note)
    # Two distinct sections: the flute leads in B while the pluck lead
    # carries A — both must actually contain material.
    lead = next(t for t in tracks if t.name == "lead")
    flute = next(t for t in tracks if t.name == "flute")
    b_start, b_end = 20 * 4, 28 * 4
    assert any(b_start <= n.beat < b_end for n in flute.notes)
    assert any(n.beat < b_start for n in lead.notes)


def test_rendered_theme_exists_and_respects_quality_gates() -> None:
    with wave.open(str(config.MUSIC_DIR / config.MUSIC_FILE)) as f:
        assert f.getframerate() == SAMPLE_RATE and f.getnchannels() == 1
        raw = f.readframes(f.getnframes())
    samples = [x / 32767 for (x,) in struct.iter_unpack("<h", raw)]
    assert len(samples) >= 60 * SAMPLE_RATE
    peak = max(abs(s) for s in samples)
    assert peak <= 0.9, f"clipping risk: peak {peak:.2f}"
    assert abs(samples[-1] - samples[0]) < 0.15, "audible loop seam"


def test_sewer_theme_is_eerie_funky_and_loops() -> None:
    tracks = sewer_song.build_tracks()
    duration = sewer_song.TOTAL_BEATS * 60.0 / sewer_song.TEMPO_BPM
    assert duration >= 60.0, "sewer theme must run 60+ seconds before repeating"
    voiced = [t for t in tracks if t.notes]
    assert len(voiced) >= 4, "sewer theme needs at least four voices"
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)  # every pitch must parse
            assert 0 <= note.beat < sewer_song.TOTAL_BEATS, (track.name, note)
    # Funk: the bass grooves busily through the A section (many
    # syncopated hits per bar, not just downbeats).
    bass = next(t for t in tracks if t.name == "bass")
    a_hits = [n for n in bass.notes if 4 * 4 <= n.beat < 12 * 4]
    assert len(a_hits) >= 8 * 4, len(a_hits)
    # Eerie: the B section (bars 20-27) leans on the Eb tritone color.
    lead = next(t for t in tracks if t.name == "lead")
    b_start, b_end = 20 * 4, 28 * 4
    assert any(b_start <= n.beat < b_end and n.pitch.startswith("Eb")
               for n in lead.notes), "B section is missing its tritone chill"


def test_rendered_sewer_theme_respects_quality_gates() -> None:
    with wave.open(str(config.MUSIC_DIR / "sewer.wav")) as f:
        assert f.getframerate() == SAMPLE_RATE and f.getnchannels() == 1
        raw = f.readframes(f.getnframes())
    samples = [x / 32767 for (x,) in struct.iter_unpack("<h", raw)]
    assert len(samples) >= 60 * SAMPLE_RATE
    peak = max(abs(s) for s in samples)
    assert peak <= 0.9, f"clipping risk: peak {peak:.2f}"
    assert abs(samples[-1] - samples[0]) < 0.15, "audible loop seam"


def test_fall_cue_is_dense_then_resolves_for_the_jungle_tableau() -> None:
    tracks = fall_song.build_tracks()
    duration = fall_song.TOTAL_BEATS * 60.0 / fall_song.TEMPO_BPM
    assert 35.0 <= duration <= 37.0
    assert len([track for track in tracks if track.notes]) >= 7
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)
            assert 0 <= note.beat < fall_song.TOTAL_BEATS

    pulse = next(track for track in tracks if track.name == "pulse")
    kick = next(track for track in tracks if track.name == "kick")
    assert len([note for note in pulse.notes if note.beat < 13 * 4]) >= 100
    assert any(note.beat == 0 for note in kick.notes), "cue must kick off hard"
    # Music begins four seconds into the scene, so beat 50 is the exact
    # 29-second jungle impact. The action kit must stop there.
    assert not any(note.beat >= 50 for note in kick.notes)
    flute = next(track for track in tracks if track.name == "flute")
    assert any(note.beat >= 13 * 4 for note in flute.notes)


def test_rendered_fall_cue_respects_one_shot_quality_gates() -> None:
    with wave.open(str(config.MUSIC_DIR / "fall_to_chult.wav")) as f:
        assert f.getframerate() == SAMPLE_RATE and f.getnchannels() == 1
        raw = f.readframes(f.getnframes())
    samples = [x / 32767 for (x,) in struct.iter_unpack("<h", raw)]
    assert 35 * SAMPLE_RATE <= len(samples) <= 37 * SAMPLE_RATE
    assert max(abs(sample) for sample in samples) <= 0.9


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
    print("All music tests passed.")


if __name__ == "__main__":
    _run_all()
