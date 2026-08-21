"""Phase 12 Cabin theme composition, render, and doorway continuity."""

import math
import os
import struct
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from data.music import cabin
from src.audio import instruments as ins
from src.audio.sequencer import note_to_freq
from src.core import config
from src.world.transitions import AREA_MUSIC


TRACK = "cabin.wav"
CABIN_MAPS = ("tahuya_cabin_exterior", "tahuya_cabin_interior")


def _samples():
    with wave.open(str(config.MUSIC_DIR / TRACK)) as handle:
        assert handle.getnchannels() == 1
        frames = handle.getnframes()
        rate = handle.getframerate()
        data = struct.unpack(f"<{frames}h", handle.readframes(frames))
    return data, rate


def test_cabin_theme_is_cool_driving_and_jazz_funk_bass_driven() -> None:
    tracks = cabin.build_tracks()
    named = {track.name: track for track in tracks}
    duration = cabin.TOTAL_BEATS * 60.0 / cabin.TEMPO_BPM
    assert duration >= 90.0
    assert len([track for track in tracks if track.notes]) >= 10
    for track in tracks:
        for note in track.notes:
            note_to_freq(note.pitch)
            assert 0 <= note.beat < cabin.TOTAL_BEATS

    bass = named["driving_bass"]
    hook = named["synth_hook"]
    assert bass.level > hook.level
    assert len(bass.notes) == cabin.TOTAL_BARS * 8
    assert [note.beat for note in bass.notes[:8]] == [
        0, .625, 1, 1.5, 2.125, 2.5, 3.125, 3.5
    ]
    assert {note.pitch for note in bass.notes[:8]} == {
        "D2", "F2", "A2", "C3", "D3",
    }
    assert hook.instrument is ins.neon_synth_lead
    assert named["pulse_arp"].instrument is ins.pulse_arp
    assert named["low_pulse"].instrument is ins.pulse_arp
    assert not ({"mallet_hook", "reed_answers", "colored_lights",
                 "strange_swells"} & named.keys())

    first = [
        (note.beat - 4 * 4, note.dur, note.pitch)
        for note in hook.notes if 4 * 4 <= note.beat < 12 * 4
    ]
    returned = [
        (note.beat - 32 * 4, note.dur, note.pitch)
        for note in hook.notes if 32 * 4 <= note.beat < 40 * 4
    ]
    assert first == returned and len(first) >= 40
    assert any(note.pitch == "D6" for note in hook.notes)

    assert named["dayan"].instrument is ins.tabla_dayan
    assert named["bayan"].instrument is ins.tabla_bayan
    assert named["jaw_harp"].instrument is ins.jaw_harp
    assert len(named["dayan"].notes) == cabin.TOTAL_BARS * 2
    assert len(named["bayan"].notes) == cabin.TOTAL_BARS
    assert 20 <= len(named["jaw_harp"].notes) <= 48
    assert all(note.beat % 4 in {1.75, 3.75}
               for note in named["jaw_harp"].notes)

    # The night break removes the lead but never drops the techno heartbeat.
    break_start, break_end = 28 * 4, 32 * 4
    assert not any(break_start <= n.beat < break_end for n in hook.notes)
    assert all(len([n for n in named["kick"].notes
                    if bar * 4 <= n.beat < (bar + 1) * 4]) == 4
               for bar in range(cabin.TOTAL_BARS))
    assert len(named["snare"].notes) == cabin.TOTAL_BARS * 2


def test_rendered_cabin_theme_meets_loop_and_mix_gates() -> None:
    data, rate = _samples()
    duration = len(data) / rate
    peak = max(abs(sample) for sample in data) / 32768
    rms = math.sqrt(sum(sample * sample for sample in data) / len(data)) / 32768
    assert rate == 22050
    assert duration >= 90.0
    assert peak <= .94
    assert .10 <= rms <= .22
    assert abs(data[-1] - data[0]) / 32768 < .15


def test_cabin_doors_share_one_uninterrupted_cue() -> None:
    assert (config.MUSIC_DIR / TRACK).is_file()
    assert {AREA_MUSIC[name] for name in CABIN_MAPS} == {TRACK}


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
    print("All Cabin music tests passed.")


if __name__ == "__main__":
    _run_all()
