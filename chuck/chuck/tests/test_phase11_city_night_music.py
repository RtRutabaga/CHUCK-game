"""Phase 11 Night City theme: composition, render, and continuity.

The phase document asks for an original jazzy synth city theme that is
nocturnal, rain-lit and catchy, and insists the music run uninterrupted
between maps sharing a regional cue -- changing only at the region
boundaries. These tests check the render against the same quality gates
the earlier area themes are held to, and check the wiring against that
continuity rule.
"""

import math
import os
import struct
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from data.music import city_night
from src.audio import instruments as ins
from src.core import config
from src.world.transitions import AREA_MUSIC


TRACK = "city_night.wav"
NIGHT_MAPS = (
    "modern_city_arrival", "modern_city_night_2", "modern_city_night_3",
    "modern_city_night_4", "modern_city_night_5", "modern_city_night_6",
)


def _samples():
    path = config.MUSIC_DIR / TRACK
    handle = wave.open(str(path))
    frames = handle.getnframes()
    rate = handle.getframerate()
    data = struct.unpack(f"<{frames}h", handle.readframes(frames))
    handle.close()
    return data, rate


def test_the_night_theme_meets_the_area_theme_gates() -> None:
    data, rate = _samples()
    duration = len(data) / rate
    peak = max(abs(sample) for sample in data) / 32768
    rms = math.sqrt(sum(sample * sample for sample in data) / len(data)) / 32768

    assert duration >= 60.0, duration          # long enough not to nag
    assert peak <= 0.95, peak                  # headroom, never clipped
    assert 0.10 <= rms <= 0.20, rms            # level with the other cues

    # The loop seam: the end must sit at the same energy as the start, or
    # the join is audible every eighty seconds.
    window = rate // 2
    head = sum(abs(s) for s in data[:window]) / window
    tail = sum(abs(s) for s in data[-window:]) / window
    assert abs(tail - head) / 32768 < 0.15, (head, tail)


def test_the_composition_is_jazz_rather_than_pop() -> None:
    """The harmony the phase document asked for, held to in the data."""
    # Sevenths and ninths stacked, not triads: every voicing is four notes.
    assert all(len(chord) == 4 for chord in city_night._VOICING.values())
    # ii-V-I motion is present, and the flat-six detour with it.
    assert ("D3", "G2", "C3") == city_night._ROOTS[:3]
    assert "Bb2" in city_night._ROOTS

    tracks = city_night.build_tracks()
    voices = {track.name: track for track in tracks}
    # The palette the document asked for: electric-key harmony, a
    # syncopated synth bass, restrained drums, and wet air.
    assert voices["keys"].instrument is ins.electric_key
    assert voices["bass"].instrument is ins.synth_bass
    assert voices["rain"].instrument is ins.rain_wash
    assert {"kick", "snare", "hats"} <= set(voices)

    # The bass pushes off the beat rather than landing on it: its loudest
    # note in a bar is not the downbeat.
    bar_four = [note for note in voices["bass"].notes
                if 16 <= note.beat < 20]
    loudest = max(bar_four, key=lambda note: note.vel)
    assert loudest.beat % 4 != 0, loudest.beat


def test_the_hook_states_rests_and_returns() -> None:
    tracks = {track.name: track for track in city_night.build_tracks()}
    lead = tracks["lead"].notes
    assert lead, "the theme has no melody"

    def bars_with_melody(first, last):
        return {int(note.beat // 4) for note in lead
                if first <= note.beat // 4 <= last}

    assert bars_with_melody(4, 11), "the hook is never stated"
    assert bars_with_melody(12, 19), "the hook never returns harmonised"
    # The underpass is the point: the melody stops so its return lands.
    assert not bars_with_melody(20, 25), "the middle is not a rest"
    assert bars_with_melody(26, 31), "the hook never comes back"

    # The return is the same shape an octave up, not a new idea.
    opening = [note.pitch for note in lead if 16 <= note.beat < 20]
    returning = [note.pitch for note in lead if 104 <= note.beat < 108]
    assert len(opening) == len(returning)
    for low, high in zip(opening, returning):
        assert low[:-1] == high[:-1], (low, high)
        assert int(high[-1]) == int(low[-1]) + 1


def test_the_cue_runs_unbroken_across_the_night_region() -> None:
    """It changes only at a region boundary, never between night maps."""
    assert (config.MUSIC_DIR / TRACK).is_file()
    for name in NIGHT_MAPS:
        assert AREA_MUSIC[name] == TRACK, name

    # The sewer and the day city are their own regions; their themes are
    # still to be composed, and they must not borrow this one.
    for name, cue in AREA_MUSIC.items():
        if name.startswith(("modern_city_sewer", "modern_city_day")):
            assert cue != TRACK, name


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
    print("All Night City music tests passed.")


if __name__ == "__main__":
    _run_all()
