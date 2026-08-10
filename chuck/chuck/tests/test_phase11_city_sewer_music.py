"""Phase 11 Urban Sewer theme: composition, render, and originality.

The phase document points at the memorable groove of classic
underground music as a broad reference and then draws a hard line: do
not copy its melodies, bass lines, harmony or arrangement. So the tests
here check both that the cue works -- the same gates the other area
themes meet -- and that what was taken is the *idea* of a short
low-register motif under a long walk, not the reference itself.
"""

import math
import os
from pathlib import Path
import struct
import tempfile
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from data.music import city_night, city_sewer
from src.audio import instruments as ins
from src.core.game import Game
from src.core import config
from src.world.transitions import AREA_MUSIC


TRACK = "city_sewer.wav"
SEWER_MAPS = (
    "modern_city_sewer_1", "modern_city_sewer_2",
    "modern_city_sewer_3", "modern_city_sewer_4",
)
SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _midi(pitch: str) -> int:
    name = pitch[0]
    index = 1
    value = SEMITONES[name]
    while index < len(pitch) and pitch[index] in "#b":
        value += 1 if pitch[index] == "#" else -1
        index += 1
    return value + 12 * (int(pitch[index:]) + 1)


def _samples():
    handle = wave.open(str(config.MUSIC_DIR / TRACK))
    frames = handle.getnframes()
    rate = handle.getframerate()
    data = struct.unpack(f"<{frames}h", handle.readframes(frames))
    handle.close()
    return data, rate


def test_the_sewer_theme_meets_the_area_theme_gates() -> None:
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


def test_the_riff_is_its_own_and_not_the_reference() -> None:
    """What was borrowed is the idea, not the tune."""
    riff = city_sewer._RIFF
    pitches = [_midi(pitch) for _b, _d, pitch, _v in riff]

    # Straight sixteenths, not a triplet feel: every onset sits on a
    # quarter of a beat. The reference's swing is the thing most worth
    # not reproducing.
    for beat, _duration, _pitch, _velocity in riff:
        assert abs(beat * 4 - round(beat * 4)) < 1e-9, beat

    # It rises to a blue note and falls back; it is not a chromatic
    # descent, which is the reference's whole contour.
    assert pitches[0] < max(pitches), "the riff never rises"
    assert pitches[-1] < max(pitches), "the riff never comes back down"
    descending_semitones = sum(
        1 for a, b in zip(pitches, pitches[1:]) if b - a == -1
    )
    assert descending_semitones <= 1, descending_semitones

    # The blue flat five is the hook, and the motif is short enough to
    # carry a long winding map.
    assert max(pitches) - min(pitches) == 6, "no flat five in the riff"
    assert len(riff) <= 8, len(riff)


def test_the_tunnel_sounds_like_a_tunnel_not_a_street() -> None:
    tracks = {track.name: track for track in city_sewer.build_tracks()}
    # The palette the document asked for: funk bass, clipped percussion,
    # hollow pipe timbres, and water.
    assert tracks["bass"].instrument is ins.elastic_bass
    assert tracks["pipes"].instrument is ins.hollow_pipe
    assert tracks["blocks"].instrument is ins.woodblock
    assert tracks["drips"].instrument is ins.sewer_drip

    # No lead melody at all: the sewer maps are long, and a tune would
    # wear out before they did.
    assert "lead" not in tracks

    # It lives low. Every bass note is below the night theme's melody.
    night = {track.name: track for track in city_night.build_tracks()}
    lowest_lead = min(_midi(note.pitch) for note in night["lead"].notes)
    assert all(_midi(note.pitch) < lowest_lead
               for note in tracks["bass"].notes)

    # ...and it keeps moving: something plays on well over half the
    # sixteenths of a groove bar, or a winding map would feel static.
    groove = [note for track in tracks.values() for note in track.notes
              if 24 <= note.beat < 28]
    assert len({round(note.beat * 4) for note in groove}) >= 10


def test_the_tunnel_plays_as_loud_as_the_street() -> None:
    """Measured level is not played level when the material is this low.

    The mastering gates put every area theme in the same RMS window, and
    by that meter the sewer cue was already level with the night one.
    It still played noticeably quieter, because nearly all of it sits
    below 300Hz and low material measures loud. The fix is in two
    places: the mix leans harder on the pipes, blocks and hats that
    carry perceived loudness, and the cue carries an authored trim on
    top of the stream volume.
    """
    tracks = {track.name: track for track in city_sewer.build_tracks()}
    # The mid and high voices are no longer buried under the bass.
    assert tracks["pipes"].level >= tracks["bass"].level * 0.9
    for name in ("blocks", "hats", "snare"):
        assert tracks[name].level >= 0.44, (name, tracks[name].level)

    assert config.MUSIC_TRIM[TRACK] > 1.0
    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        street = game.audio.volume_for("city_night.wav")
        tunnel = game.audio.volume_for(TRACK)
        assert street == config.AUDIO_MUSIC_VOLUME
        assert tunnel > street, (tunnel, street)
        # ...but never past the mixer's own ceiling.
        assert tunnel <= 1.0
    finally:
        game._shutdown()
        directory.cleanup()


def test_the_cue_runs_unbroken_through_the_sewer_only() -> None:
    assert (config.MUSIC_DIR / TRACK).is_file()
    for name in SEWER_MAPS:
        assert AREA_MUSIC[name] == TRACK, name

    # It changes at the region boundary and nowhere else: the night city
    # keeps its own cue, and the day city is still to be composed.
    assert AREA_MUSIC["modern_city_night_6"] == "city_night.wav"
    for name, cue in AREA_MUSIC.items():
        if name.startswith("modern_city_day"):
            assert cue != TRACK, name
    # The medieval Waterdeep sewer is a different place entirely.
    assert AREA_MUSIC["sewer"] != TRACK


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
    print("All Urban Sewer music tests passed.")


if __name__ == "__main__":
    _run_all()
