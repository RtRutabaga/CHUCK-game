"""The cabin cue when the lightshow starts.

Waking the table map does not change the piece, it changes the gear.
Every identifying part of the cabin theme is imported rather than
rewritten -- the same root cycle, the same elastic-bass figure, the
same two hooks -- and the Beholder fight's language is laid over the
top of it: a choral ostinato grinding the flat second, brass answering
on the offbeats, timpani and toms under a double-time kit.

The neon synth lead is gone. The tune is carried by a jaw harp and two
Tuvan throat voices instead, so the hook now has to be checked where it
actually is: the same notes in the same order, two octaves down, sung
rather than played.

So the tests here are about identity and lift. It has to still be the
cabin's tune, it has to be measurably harder than the calm cue, and it
has to belong to the room the aurora is in rather than to the phase.
"""

import math
import os
from pathlib import Path
import struct
import tempfile
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from data.music import boss_battle, cabin, cabin_awakened
from src.audio import instruments as ins
from src.core import config
from src.core.game import Game
from src.systems.cabin_progress import (
    AWAKENED_MUSIC, CABIN_ENTITY_FLAGS, COUNTER_MAP_AWAKENED_FLAG,
)
from src.world.transitions import AREA_MUSIC


TRACK = "cabin_awakened.wav"
AWAKE = set(CABIN_ENTITY_FLAGS) | {COUNTER_MAP_AWAKENED_FLAG}


def _measure(name):
    handle = wave.open(str(config.MUSIC_DIR / name))
    frames = handle.getnframes()
    rate = handle.getframerate()
    data = struct.unpack(f"<{frames}h", handle.readframes(frames))
    handle.close()
    peak = max(abs(sample) for sample in data) / 32768
    rms = math.sqrt(sum(s * s for s in data) / len(data)) / 32768
    return len(data) / rate, peak, rms, data


_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _midi(pitch):
    step = _SEMITONE[pitch[0]]
    body = pitch[1:]
    if body[0] in "#b":
        step += 1 if body[0] == "#" else -1
        body = body[1:]
    return (int(body) + 1) * 12 + step


def test_the_awakened_cue_is_the_cabin_tune_not_a_new_one() -> None:
    calm = {track.name: track for track in cabin.build_tracks()}
    loud = {track.name: track for track in cabin_awakened.build_tracks()}

    # The neon lead is gone -- no voice in here plays it, and nothing is
    # left up in the register it occupied.
    assert "synth_hook" not in loud
    assert all(track.instrument is not ins.neon_synth_lead for track in
               cabin_awakened.build_tracks())

    # The hook survives it: same notes in the same order at the same
    # beats, dropped two octaves onto the overtone voice.
    sung = loud["throat_overtone"].notes
    played = calm["synth_hook"].notes
    assert [note.beat for note in sung] == [note.beat for note in played]
    assert all(_midi(a.pitch) == _midi(b.pitch) - 24
               for a, b in zip(sung, played))

    # The melody is jaw harp and throat singing, and the harp is the
    # loudest thing that is not the bass or the kit.
    assert loud["throat_overtone"].instrument is ins.throat_overtone
    assert loud["throat_drone"].instrument is ins.throat_drone
    assert loud["jaw_harp"].instrument is ins.jaw_harp
    # ...and there is a great deal more of it than the calm cue has.
    assert len(loud["jaw_harp"].notes) > len(calm["jaw_harp"].notes) * 5

    # The drone never rests: it is the floor the other two are drawn on.
    assert len(loud["throat_drone"].notes) == cabin.TOTAL_BARS

    # The bass is the cabin's own figure, on the cabin's own roots.
    assert loud["driving_bass"].instrument is ins.elastic_bass
    assert len(loud["driving_bass"].notes) == cabin.TOTAL_BARS * 8
    assert [note.pitch for note in loud["driving_bass"].notes[:8]] == [
        note.pitch for note in calm["driving_bass"].notes[:8]
    ]
    assert cabin_awakened.TOTAL_BARS == cabin.TOTAL_BARS


def test_it_borrows_the_beholder_fight_rather_than_imitating_it() -> None:
    loud = {track.name: track for track in cabin_awakened.build_tracks()}
    boss = {track.name: track for track in boss_battle.build_tracks()}

    # The boss theme's voices, on the cabin's harmony.
    assert loud["chant"].instrument is boss["chant"].instrument is ins.choir
    assert loud["horn"].instrument is boss["horn"].instrument is ins.brass
    assert loud["timpani"].instrument is ins.timpani
    assert loud["toms"].instrument is ins.jungle_tom

    # The ostinato grinds a flat second, which is the whole trick: the
    # cabin is D Dorian and the boss is D Phrygian, one note apart.
    semitones = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

    def midi(pitch):
        step = semitones[pitch[0]]
        body = pitch[1:]
        if body[0] in "#b":
            step += 1 if body[0] == "#" else -1
            body = body[1:]
        return (int(body) + 1) * 12 + step

    first_bar = [note for note in loud["chant"].notes if note.beat < 4]
    intervals = {abs(midi(a.pitch) - midi(b.pitch))
                 for a, b in zip(first_bar, first_bar[1:])}
    assert intervals == {1}, intervals

    # ...and it is not simply the boss cue: it keeps the cabin's tempo
    # family and its own melody instead.
    assert cabin.TEMPO_BPM < cabin_awakened.TEMPO_BPM < boss_battle.TEMPO_BPM
    assert "chant" not in {track.name for track in cabin.build_tracks()}


def test_the_awakened_cue_is_harder_and_still_meets_the_gates() -> None:
    duration, peak, rms, data = _measure(TRACK)
    assert duration >= 60.0, duration
    assert peak <= 0.95, peak
    assert 0.10 <= rms <= 0.22, rms
    assert abs(data[-1] - data[0]) / 32768 < 0.15

    # Measurably harder than the room was a moment ago, and no louder
    # than the fight it borrows from.
    _calm_duration, _calm_peak, calm_rms, _calm = _measure("cabin.wav")
    _boss_duration, _boss_peak, boss_rms, _boss = _measure("boss_battle.wav")
    assert rms > calm_rms * 1.15, (rms, calm_rms)
    assert rms <= boss_rms, (rms, boss_rms)
    assert cabin_awakened.MASTER_HEADROOM > cabin.MASTER_HEADROOM


def test_the_lift_belongs_to_the_room_the_aurora_is_in() -> None:
    # The authored cue is unchanged: both cabin maps still share it, so
    # ordinary door crossings before the awakening restart nothing.
    assert AREA_MUSIC["tahuya_cabin_exterior"] == "cabin.wav"
    assert AREA_MUSIC["tahuya_cabin_interior"] == "cabin.wav"
    assert (config.MUSIC_DIR / AWAKENED_MUSIC).is_file()

    directory = tempfile.TemporaryDirectory()
    game = Game(save_path=Path(directory.name) / "save.json")
    try:
        game.checkpoints.load_checkpoint("tahuya_interior")
        assert game.audio._current_music == ("cabin.wav", True)

        world = game.checkpoints.load_checkpoint(
            "tahuya_interior", progress_flags=AWAKE
        )
        assert game.audio._current_music == (AWAKENED_MUSIC, True)
        # The lightshow and the lift arrive together.
        assert world.aurora is not None

        game.checkpoints.load_checkpoint(
            "tahuya_exterior", progress_flags=AWAKE
        )
        assert game.audio._current_music == ("cabin.wav", True)
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
    print("All awakened cabin music tests passed.")


if __name__ == "__main__":
    _run_all()
