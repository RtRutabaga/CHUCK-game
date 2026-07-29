"""Unit tests for the sequencer and the Waterdeep Docks theme.

Run from the project root with:

    python -m tests.test_music       (pure stdlib, no dependencies)
    pytest                           (if you have pytest)

The composition tests turn the Soundtrack Bible's minimum standard for
the Waterdeep theme into executable checks.
"""

import struct
import wave

from data.music import boss_battle as boss_song
from data.music import phlegethos as phlegethos_song
from data.music import ship_shanty as shanty_song
from data.music import fall_to_chult as fall_song
from data.music import chult as chult_song
from data.music import temple as temple_song
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


def test_chult_theme_is_bass_forward_syncopated_and_layered() -> None:
    tracks = chult_song.build_tracks()
    duration = chult_song.TOTAL_BEATS * 60.0 / chult_song.TEMPO_BPM
    assert duration >= 80.0
    assert len([track for track in tracks if track.notes]) >= 9
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)
            assert 0 <= note.beat < chult_song.TOTAL_BEATS

    bass = next(track for track in tracks if track.name == "bass")
    assert bass.level > next(track for track in tracks if track.name == "lead").level
    a_hits = [note for note in bass.notes if 4 * 4 <= note.beat < 12 * 4]
    assert len(a_hits) >= 8 * 7
    assert any(note.beat % 1 not in {0.0, 0.5} for note in a_hits)

    toms = next(track for track in tracks if track.name == "toms")
    wood = next(track for track in tracks if track.name == "wood")
    assert len(toms.notes) >= chult_song.TOTAL_BARS * 3
    assert len(wood.notes) >= chult_song.TOTAL_BARS * 4
    assert any(note.pitch == "B4" for note in tracks[0].notes), (
        "Dorian raised-sixth color is missing from the lead"
    )


def test_rendered_chult_theme_respects_loop_quality_gates() -> None:
    with wave.open(str(config.MUSIC_DIR / "chult.wav")) as f:
        assert f.getframerate() == SAMPLE_RATE and f.getnchannels() == 1
        raw = f.readframes(f.getnframes())
    samples = [x / 32767 for (x,) in struct.iter_unpack("<h", raw)]
    assert len(samples) >= 80 * SAMPLE_RATE
    peak = max(abs(sample) for sample in samples)
    assert peak <= 0.9, f"clipping risk: peak {peak:.2f}"
    assert abs(samples[-1] - samples[0]) < 0.15, "audible loop seam"


def test_temple_theme_is_ancient_shamanic_and_exploratory() -> None:
    tracks = temple_song.build_tracks()
    duration = temple_song.TOTAL_BEATS * 60.0 / temple_song.TEMPO_BPM
    assert duration >= 75.0
    assert len([track for track in tracks if track.notes]) >= 7
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)
            assert 0 <= note.beat < temple_song.TOTAL_BEATS
    toms = next(track for track in tracks if track.name == "ritual_toms")
    flute = next(track for track in tracks if track.name == "flute")
    assert len(toms.notes) >= temple_song.TOTAL_BARS * 4
    assert len(flute.notes) < temple_song.TOTAL_BARS * 2
    assert any(note.pitch.startswith("Eb") for note in flute.notes)


def test_rendered_temple_theme_respects_loop_quality_gates() -> None:
    with wave.open(str(config.MUSIC_DIR / "temple.wav")) as f:
        assert f.getframerate() == SAMPLE_RATE and f.getnchannels() == 1
        raw = f.readframes(f.getnframes())
    samples = [x / 32767 for (x,) in struct.iter_unpack("<h", raw)]
    assert len(samples) >= 75 * SAMPLE_RATE
    # Session 124: playtest asked for the temple louder again; its render
    # alone uses 0.98 peak headroom (still never clipping).
    assert max(abs(sample) for sample in samples) <= 0.99
    assert abs(samples[-1] - samples[0]) < 0.15

    with wave.open(str(config.MUSIC_DIR / "chult.wav")) as f:
        chult_raw = f.readframes(f.getnframes())
    chult_samples = [x / 32767
                     for (x,) in struct.iter_unpack("<h", chult_raw)]
    temple_rms = (sum(sample * sample for sample in samples)
                  / len(samples)) ** 0.5
    chult_rms = (sum(sample * sample for sample in chult_samples)
                 / len(chult_samples)) ** 0.5
    # The sparse arrangement needs a deliberate lift above the dense jungle
    # mix to read equally strongly during actual gameplay.
    assert 1.25 <= temple_rms / chult_rms <= 1.45, (
        temple_rms, chult_rms
    )


def test_boss_theme_is_choral_climactic_and_looping() -> None:
    tracks = boss_song.build_tracks()
    duration = boss_song.TOTAL_BEATS * 60.0 / boss_song.TEMPO_BPM
    assert duration >= 60.0, "boss theme must run 60+ seconds before repeating"
    voiced = [t for t in tracks if t.notes]
    assert len(voiced) >= 8, "a climactic boss theme wants a full ensemble"
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)  # every pitch must parse
            assert 0 <= note.beat < boss_song.TOTAL_BEATS, (track.name, note)
    # The chant is a relentless choral ostinato: eighth notes hammering
    # through every drive bar, not an occasional phrase.
    chant = next(t for t in tracks if t.name == "chant")
    assert len(chant.notes) >= 44 * 8 * 0.8, len(chant.notes)
    # Duel-of-the-Fates menace: the chant grinds the Phrygian flat-second
    # (Eb over a D tonic) hard.
    assert sum(1 for n in chant.notes if n.pitch.startswith("Eb")) >= 24
    # The horns carry the theatrical melody up top in the B section...
    horn = next(t for t in tracks if t.name == "horn")
    b_start, b_end = 16 * 4, 24 * 4
    assert any(b_start <= n.beat < b_end and n.pitch[-1] in "45"
               for n in horn.notes), "the horn melody is missing from B"
    # ...over sustained choir 'aahs'.
    pad = next(t for t in tracks if t.name == "choir_pad")
    assert any(b_start <= n.beat < b_end for n in pad.notes)
    # Orchestral weight: timpani drive the low end throughout.
    timp = next(t for t in tracks if t.name == "timpani")
    assert len(timp.notes) >= boss_song.TOTAL_BARS


def test_rendered_boss_theme_respects_loop_quality_gates() -> None:
    with wave.open(str(config.MUSIC_DIR / "boss_battle.wav")) as f:
        assert f.getframerate() == SAMPLE_RATE and f.getnchannels() == 1
        raw = f.readframes(f.getnframes())
    samples = [x / 32767 for (x,) in struct.iter_unpack("<h", raw)]
    assert len(samples) >= 60 * SAMPLE_RATE
    # The boss render, like the temple, earns a loud ceiling for its
    # climactic mix (still safely short of clipping).
    peak = max(abs(s) for s in samples)
    assert peak <= 0.97, f"clipping risk: peak {peak:.2f}"
    assert abs(samples[-1] - samples[0]) < 0.15, "audible loop seam"
    # It must read at least as strongly as the loud temple/jungle themes.
    with wave.open(str(config.MUSIC_DIR / "temple.wav")) as f:
        traw = f.readframes(f.getnframes())
    tsamp = [x / 32767 for (x,) in struct.iter_unpack("<h", traw)]
    boss_rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    temple_rms = (sum(s * s for s in tsamp) / len(tsamp)) ** 0.5
    assert boss_rms >= temple_rms * 0.9, (boss_rms, temple_rms)


def test_ship_shanty_is_a_fast_dark_pirate_reel() -> None:
    tracks = shanty_song.build_tracks()
    duration = shanty_song.TOTAL_BEATS * 60.0 / shanty_song.TEMPO_BPM
    assert duration >= 60.0
    assert shanty_song.TEMPO_BPM >= 120  # a reel, not a harbor sway
    voiced = [t for t in tracks if t.notes]
    assert len(voiced) >= 8, "a pirate crew needs a full band"
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)
            assert 0 <= note.beat < shanty_song.TOTAL_BEATS, (track.name, note)
    # The fiddle drives a near-continuous stream of eighth notes (a reel).
    fiddle = next(t for t in tracks if t.name == "fiddle")
    assert len(fiddle.notes) >= shanty_song.TOTAL_BARS * 8 * 0.9
    assert all(abs(n.dur - 0.5) < 1e-6 for n in fiddle.notes)  # eighths
    fp = [n.pitch for n in fiddle.notes]
    # It's DARK now: D minor, not the old major reel. The minor third
    # (F natural) is everywhere and the major third (F#) is gone...
    assert any(p.startswith("F") and not p.startswith("F#") for p in fp)
    assert not any(p.startswith("F#") for p in fp)
    # ...while the raised-seventh C# supplies the swashbuckler cadence.
    assert any(p.startswith("C#") for p in fp)
    # The crew chants in the second half (the pirate sing-along).
    crew = next(t for t in tracks if t.name == "crew")
    assert crew.notes and all(n.beat >= 16 * 4 for n in crew.notes)
    # Accordion horns and the whistle round out the band.
    assert next(t for t in tracks if t.name == "accordion").notes
    assert next(t for t in tracks if t.name == "whistle").notes


def test_rendered_ship_shanty_respects_loop_quality_gates() -> None:
    with wave.open(str(config.MUSIC_DIR / "ship_shanty.wav")) as f:
        assert f.getframerate() == SAMPLE_RATE and f.getnchannels() == 1
        raw = f.readframes(f.getnframes())
    samples = [x / 32767 for (x,) in struct.iter_unpack("<h", raw)]
    assert len(samples) >= 60 * SAMPLE_RATE
    peak = max(abs(s) for s in samples)
    assert peak <= 0.92, f"clipping risk: peak {peak:.2f}"
    assert abs(samples[-1] - samples[0]) < 0.15, "audible loop seam"


def test_phlegethos_theme_is_driving_infernal_and_never_ambient() -> None:
    """The brief: dangerous, adventurous, mysterious, infernal, energetic,
    rhythmically driven -- and explicitly NOT slow, ambient-only, or
    hopeless. Hell is an active, hostile place."""
    tracks = phlegethos_song.build_tracks()
    duration = phlegethos_song.TOTAL_BEATS * 60.0 / phlegethos_song.TEMPO_BPM
    assert duration >= 60.0
    assert phlegethos_song.TEMPO_BPM >= 120  # energetic, never slow
    voiced = [t for t in tracks if t.notes]
    assert len(voiced) >= 10, "the brief asks for a big percussive ensemble"
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)
            assert 0 <= note.beat < phlegethos_song.TOTAL_BEATS, (
                track.name, note)

    named = {track.name: track for track in tracks}
    # Heavy percussion / tribal tom rhythms carry every single bar: this
    # is a groove, not an atmosphere.
    toms = named["toms"]
    assert len(toms.notes) >= phlegethos_song.TOTAL_BARS * 6
    kick = named["kick"]
    assert len(kick.notes) >= phlegethos_song.TOTAL_BARS * 4
    tom_bars = {int(n.beat // 4) for n in toms.notes}
    assert len(tom_bars) == phlegethos_song.TOTAL_BARS, "a bar without toms"
    # Driving bass, pulsing low synth, and metallic hits are all present.
    assert len(named["bass"].notes) >= phlegethos_song.TOTAL_BARS * 4
    assert named["pulse"].notes and named["metal"].notes
    # An eerie melodic lead and an occasional choir texture sit on top.
    assert named["lead"].notes and named["eerie"].notes
    assert named["choir"].notes
    # Phrygian-dominant heat: the flat second (F) against a raised third
    # (G#) over an E tonic is what makes it infernal rather than merely sad.
    lead_pitches = {n.pitch for n in named["lead"].notes}
    assert any(p.startswith("F") and not p.startswith("F#")
               for p in lead_pitches)
    assert any(p.startswith("G#") for p in lead_pitches)


def test_rendered_phlegethos_theme_respects_loop_quality_gates() -> None:
    with wave.open(str(config.MUSIC_DIR / "phlegethos.wav")) as f:
        assert f.getframerate() == SAMPLE_RATE and f.getnchannels() == 1
        raw = f.readframes(f.getnframes())
    samples = [x / 32767 for (x,) in struct.iter_unpack("<h", raw)]
    assert len(samples) >= 60 * SAMPLE_RATE
    peak = max(abs(s) for s in samples)
    assert peak <= 0.95, f"clipping risk: peak {peak:.2f}"
    assert abs(samples[-1] - samples[0]) < 0.15, "audible loop seam"
    # It must read as strongly as the other late-game themes in play.
    with wave.open(str(config.MUSIC_DIR / "temple.wav")) as f:
        traw = f.readframes(f.getnframes())
    tsamp = [x / 32767 for (x,) in struct.iter_unpack("<h", traw)]
    rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    temple_rms = (sum(s * s for s in tsamp) / len(tsamp)) ** 0.5
    assert rms >= temple_rms * 0.9, (rms, temple_rms)


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
