"""Phase 11 Day City theme, and the region's three-cue music plan.

The phase document allows the daytime theme to share a motif with the
night one while its arrangement differs. This composition takes that
literally -- the melody is derived from the night hook in code -- so
the first test here proves the shared motif is the same tune rather
than a similar one, and the rest prove the arrangement around it
genuinely changed: the same tune handed to a lunchtime jazz trio.

The last test covers the whole region: three cues, each unbroken across
its own maps, changing only at the two boundaries.
"""

import math
import os
import struct
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from data.music import city_day, city_night
from src.audio import instruments as ins
from src.core import config
from src.world.transitions import AREA_MUSIC


TRACK = "city_day.wav"
DAY_MAPS = ("modern_city_day_1", "modern_city_day_2")
NIGHT_MAPS = (
    "modern_city_arrival", "modern_city_night_2", "modern_city_night_3",
    "modern_city_night_4", "modern_city_night_5", "modern_city_night_6",
)
SEWER_MAPS = (
    "modern_city_sewer_1", "modern_city_sewer_2",
    "modern_city_sewer_3", "modern_city_sewer_4",
)


def _samples():
    handle = wave.open(str(config.MUSIC_DIR / TRACK))
    frames = handle.getnframes()
    rate = handle.getframerate()
    data = struct.unpack(f"<{frames}h", handle.readframes(frames))
    handle.close()
    return data, rate


def test_the_day_theme_meets_the_area_theme_gates() -> None:
    data, rate = _samples()
    duration = len(data) / rate
    peak = max(abs(sample) for sample in data) / 32768
    rms = math.sqrt(sum(sample * sample for sample in data) / len(data)) / 32768

    assert duration >= 60.0, duration
    assert peak <= 0.95, peak
    assert 0.10 <= rms <= 0.20, rms

    window = rate // 2
    head = sum(abs(s) for s in data[:window]) / window
    tail = sum(abs(s) for s in data[-window:]) / window
    assert abs(tail - head) / 32768 < 0.15, (head, tail)


def test_the_day_melody_is_the_night_hook_slowed_down() -> None:
    """Not a resemblance -- the same tune, walking instead of running."""
    day = {track.name: track for track in city_day.build_tracks()}
    lead = sorted(day["lead"].notes, key=lambda note: note.beat)

    night_pitches = [pitch for bar in city_night._HOOK
                     for _beat, _duration, pitch in bar]
    statement = [note.pitch for note in lead if note.beat < 16 * 4]
    assert statement == night_pitches, (statement[:6], night_pitches[:6])

    # Every note is longer than it was, and the phrase covers more bars.
    night_total = sum(duration for bar in city_night._HOOK
                      for _beat, duration, _pitch in bar)
    day_total = sum(note.dur for note in lead if note.beat < 16 * 4)
    assert day_total > night_total

    # ...and it is slower still in real time, not just in beats.
    assert city_day.TEMPO_BPM < city_night.TEMPO_BPM


def test_daylight_handed_the_tune_to_a_trio() -> None:
    day = {track.name: track for track in city_day.build_tracks()}
    night = {track.name: track for track in city_night.build_tracks()}

    # The electronic kit is gone, but it was replaced rather than
    # removed: a ride and brushes, not a four-on-the-floor.
    assert "kick" in night and "hats" in night
    assert "kick" not in day and "hats" not in day
    assert day["ride"].notes and day["brush"].notes

    # The bass walks: four to the bar, every bar, all different notes.
    bass = sorted(day["bass"].notes, key=lambda note: note.beat)
    assert len(bass) == city_day.TOTAL_BARS * 4
    for bar in range(4, city_day.TOTAL_BARS):
        in_bar = [note for note in bass
                  if bar * 4 <= note.beat < (bar + 1) * 4]
        assert [note.beat % 4 for note in in_bar] == [0, 1, 2, 3], bar
        assert len({note.pitch for note in in_bar}) >= 3, bar

    # The piano comps instead of holding: more, shorter chord events
    # than the night theme, placed off the beat as often as on it.
    assert len(day["keys"].notes) > len(night["keys"].notes)
    assert (sum(note.dur for note in day["keys"].notes)
            / len(day["keys"].notes)) < 1.5
    offbeat = [note for note in day["keys"].notes
               if abs(note.beat - round(note.beat)) > 1e-6]
    assert len(offbeat) > len(day["keys"].notes) / 4

    # A tenor answers the hook where the arrangement used to just hold.
    assert day["answer"].instrument is ins.breathy_reed
    answer_bars = {int(note.beat // 4) for note in day["answer"].notes}
    assert min(answer_bars) >= 16 and max(answer_bars) < 28

    # The harmony moves: sixteen bars with ii-V motion, not four roots.
    assert len(city_day._ROOTS) >= 16
    assert len(set(city_day._ROOTS)) >= 6

    # A pad still underneath, and rain still louder than it was at night.
    assert day["pad"].instrument is ins.cloud_pad
    assert day["rain"].level > night["rain"].level

    # The unease survives the daylight: a major seventh over the tonic.
    assert "C#5" in city_day._VOICING["D3"], city_day._VOICING["D3"]


def test_the_city_runs_on_three_cues_and_two_boundaries() -> None:
    assert (config.MUSIC_DIR / TRACK).is_file()
    for name in DAY_MAPS:
        assert AREA_MUSIC[name] == TRACK, name

    # Each region is unbroken within itself...
    assert {AREA_MUSIC[name] for name in NIGHT_MAPS} == {"city_night.wav"}
    assert {AREA_MUSIC[name] for name in SEWER_MAPS} == {"city_sewer.wav"}
    assert {AREA_MUSIC[name] for name in DAY_MAPS} == {TRACK}

    # ...and the three are distinct, so the music changes exactly twice
    # across the phase: at the sewer entrance and at the ladder.
    cues = {AREA_MUSIC[name] for name in NIGHT_MAPS + SEWER_MAPS + DAY_MAPS}
    assert len(cues) == 3, cues
    assert all((config.MUSIC_DIR / cue).is_file() for cue in cues)


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
    print("All Day City music tests passed.")


if __name__ == "__main__":
    _run_all()
