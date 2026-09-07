"""The desert's music: one theme for the region, and one for the climax.

Two things are being asserted here and they pull in opposite
directions, which is why both are worth writing down.

The region has *one* piece of music and the arrival cutscene is part of
it. The cutscene used to open with a cue of its own and then hand to a
theme, which is two pieces of music with a join in them; now it starts
the theme and the map picks it up, and the join is gone because there
is nothing to join. That rests entirely on the audio system treating a
repeat request as a no-op, so the test is that the two requests are
identical -- not that they sound similar.

And the trio's map is the one place east of the hub where the music
changes at all. It is the region's theme and the fall to Chult played
together, which works because they were already in the same key: D
Dorian against D minor, one note apart. The tests here are mostly
about that being true rather than approximately true -- same tonic
chord, the fall's own hook, the fall's wrong note -- because "a mashup"
is easy to claim and easy to get almost right.
"""

import math
import os
import struct
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from data.music import desert, desert_arrival, desert_trio, fall_to_chult
from src.audio.sequencer import note_to_freq
from src.core import config
from src.world.transitions import AREA_MUSIC


REGION = "desert.wav"
CLIMAX = "desert_trio.wav"


def _samples(track: str):
    with wave.open(str(config.MUSIC_DIR / track)) as handle:
        assert handle.getnchannels() == 1
        frames = handle.getnframes()
        rate = handle.getframerate()
        data = struct.unpack(f"<{frames}h", handle.readframes(frames))
    return [value / 32767 for value in data], rate


def _measure(track: str) -> dict:
    values, rate = _samples(track)
    return {
        "seconds": len(values) / rate,
        "peak": max(abs(v) for v in values),
        "seam": abs(values[-1] - values[0]),
        "rms": math.sqrt(sum(v * v for v in values) / len(values)),
    }


def _pitches(module, track_name: str) -> set[str]:
    for track in module.build_tracks():
        if track.name == track_name:
            return {note.pitch for note in track.notes}
    raise AssertionError(f"{module.__name__} has no {track_name!r} track")


def test_the_cutscene_and_the_region_are_one_piece_of_music() -> None:
    """The same request, which is what makes it a no-op.

    The audio system skips a repeat of the track it is already playing,
    so the cutscene starting the region's theme means the map that
    follows does not restart it -- the tune simply carries on under the
    scene change. That only works if the two calls agree exactly, loop
    flag included, so this compares the calls rather than the sound.
    """
    from src.scenes import desert_arrival_cutscene_scene as arrival

    assert AREA_MUSIC["desert_central"] == REGION
    # The cutscene asks for exactly what the map will ask for: the same
    # file, and looping, which is the world scene's default.
    played: list[tuple] = []

    class _Audio:
        def play_music(self, filename, loop=True):
            played.append((filename, loop))

        def play_sfx(self, name):
            pass

        def stop_music(self, fade_ms=0):
            pass

    class _Game:
        audio = _Audio()

    scene = arrival.DesertArrivalCutsceneScene.__new__(
        arrival.DesertArrivalCutsceneScene)
    scene.game = _Game()
    scene._play_cues(arrival.MUSIC_START - 0.1, arrival.MUSIC_START + 0.1)
    assert (REGION, True) in played, played


def test_the_region_theme_grew_and_most_of_it_is_the_desert_mode() -> None:
    """Longer, and deserty for the bulk of it rather than in passing.

    Two minutes rather than seventy-five seconds, because it now has to
    open a scene as well as carry a walk. And two thirds of it sits in
    D Phrygian dominant -- the flat second with the major third over it
    -- which is the mode the sound is actually recognised by. A bar or
    two of it would be a flavour; the point of the ask was that it
    should be what the theme *is* for most of its length.
    """
    seconds = desert.TOTAL_BEATS * 60.0 / desert.TEMPO_BPM
    assert seconds > 110.0, seconds
    measured = _measure(REGION)
    assert measured["seconds"] >= 110.0, measured
    assert measured["peak"] <= 0.9, measured
    assert measured["seam"] < 0.15, measured
    assert 0.10 <= measured["rms"] <= 0.20, measured

    desert_bars = sum(1 for bar in range(desert.TOTAL_BARS)
                      if desert._in_desert(bar))
    assert desert_bars / desert.TOTAL_BARS > 0.6, desert_bars

    # The mode itself: the flat second and the major third against the
    # tonic, which is the whole sound.
    assert desert._DESERT_TRIADS["D2"] == ("D4", "F#4", "A4")
    assert "Eb2" in desert._DESERT_TRIADS
    arp = _pitches(desert, "arp")
    assert "F#4" in arp and "Eb4" in arp, sorted(arp)

    # ...and the frame it opens and closes in is still the mode the
    # rest of the region's music lives in.
    assert not desert._in_desert(0)
    assert not desert._in_desert(desert.TOTAL_BARS - 1)
    assert desert._TRIADS["D2"] == desert_arrival._TRIADS["D2"]
    assert desert._ROOTS[0] == desert_arrival._ROOTS[0] == "D2"


def test_the_region_keeps_its_drone_and_its_thin_kit() -> None:
    """More desert, not more drums.

    The instruction was that the middle should feel like a desert, and
    the cheap way to do that is to pile on percussion. What the piece
    does instead is stop the harmony moving -- a held drone under the
    whole middle -- and let the reed ornament over it, which is the
    difference between a tune played in a mode and one that belongs to
    it.
    """
    named = {track.name: track for track in desert.build_tracks()}
    assert "drone" in named and named["drone"].notes
    for note in named["drone"].notes:
        bar = int(note.beat // desert.BEATS_PER_BAR)
        assert desert._in_desert(bar), bar

    # The kit is still two voices and neither of them is a drum kit.
    assert set(named) >= {"block", "drum"}
    assert "kick" not in named and "snare" not in named
    for track in desert.build_tracks():
        for note in track.notes:
            note_to_freq(note.pitch)
            assert 0 <= note.beat < desert.TOTAL_BEATS


def test_the_climax_is_both_themes_and_they_were_already_in_the_same_key() -> None:
    """A mashup that is actually one, checked against both parents.

    Same tonic chord in all three pieces -- which is why nothing had to
    be transposed and why the join is a single flattened note rather
    than a modulation. Then the two halves of the claim: the fall's own
    hook and its wrong note are in here, and so is the desert's
    arpeggio.
    """
    assert desert_trio._TRIADS["D2"] == desert._TRIADS["D2"]
    assert desert_trio._ROOTS[0] == "D2" == fall_to_chult._ROOTS[0]

    # The note the two modes disagree about, and the only chord in the
    # piece that changes quality because of it.
    assert desert_trio._G_DORIAN[1] == "B4"
    assert desert_trio._G_MINOR[1] == "Bb4"
    assert "Bb1" in desert_trio._ROOTS, desert_trio._ROOTS

    # The fall's hook, note for note, and its wrong note.
    fall_lead = _pitches(fall_to_chult, "lead")
    assert set(desert_trio._HOOK) <= fall_lead, desert_trio._HOOK
    brass = _pitches(desert_trio, "brass")
    assert set(desert_trio._HOOK) <= brass, sorted(brass)
    assert "Eb5" in brass, sorted(brass)
    assert "Eb4" in _pitches(desert_trio, "pulse")

    # ...and the desert's engine, still running underneath it.
    named = {track.name: track for track in desert_trio.build_tracks()}
    desert_named = {track.name: track for track in desert.build_tracks()}
    assert named["arp"].instrument is desert_named["arp"].instrument
    assert named["reed"].instrument is desert_named["reed"].instrument
    fall_named = {track.name: track for track in fall_to_chult.build_tracks()}
    for voice in ("kick", "snare", "bass"):
        assert named[voice].instrument is fall_named[voice].instrument, voice


def test_the_climax_arrives_rather_than_starting() -> None:
    """The desert first, and then the fall lands on top of it.

    Eight bars of what the player has been walking to, and then the
    sixth drops, the kit comes in and the hook is stated in half time.
    Starting at full size would be a different piece of music playing
    in the same room rather than the room's own music becoming this.
    """
    named = {track.name: track for track in desert_trio.build_tracks()}
    per_bar = desert_trio.BEATS_PER_BAR

    def first_bar(voice: str) -> int:
        return min(int(note.beat // per_bar) for note in named[voice].notes)

    assert first_bar("arp") == 0
    assert first_bar("bass") == 0
    assert first_bar("pulse") == desert_trio.FALL_IN
    assert first_bar("brass") == desert_trio.FALL_IN
    assert first_bar("kick") < desert_trio.FALL_IN, "no run-up into it"
    assert first_bar("timp") >= desert_trio.FALL_IN

    # The wrong note waits for its own bar rather than arriving with
    # everything else: two entrances, not one.
    assert desert_trio.WRONG_NOTE_IN > desert_trio.FALL_IN


def test_the_climax_loops_and_is_the_biggest_thing_in_the_phase() -> None:
    """It has to be a theme, and it has to be louder than the walk."""
    seconds = desert_trio.TOTAL_BEATS * 60.0 / desert_trio.TEMPO_BPM
    assert seconds >= 60.0, seconds
    measured = _measure(CLIMAX)
    assert measured["seconds"] >= 60.0, measured
    assert measured["peak"] <= 0.9, measured
    assert measured["seam"] < 0.15, measured
    assert measured["rms"] > _measure(REGION)["rms"], measured

    # Tempo between its two parents, so neither set of material is
    # rushed or dragged into the other's.
    assert desert.TEMPO_BPM < desert_trio.TEMPO_BPM < fall_to_chult.TEMPO_BPM

    for track in desert_trio.build_tracks():
        for note in track.notes:
            note_to_freq(note.pitch)
            assert 0 <= note.beat < desert_trio.TOTAL_BEATS


def test_it_is_the_only_map_east_where_the_music_changes() -> None:
    """One region, one theme, and one exception at the end of it."""
    eastern = [f"desert_east_{index}" for index in range(1, 9)]
    for name in ["desert_central", "desert_orc_camp", "desert_oasis",
                 "desert_undead_ruins"] + eastern:
        assert AREA_MUSIC[name] == REGION, name
    assert AREA_MUSIC["desert_trio"] == CLIMAX


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
    print("All Phase 13 music tests passed.")


if __name__ == "__main__":
    _run_all()
