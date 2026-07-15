"""Unit tests for the synth engine and the rendered audio assets.

Run from the project root with:

    python -m tests.test_audio       (pure stdlib, no dependencies)
    pytest                           (if you have pytest)

Asset tests enforce the Soundtrack Bible's quality bar: correct format,
no clipping (headroom preserved), click-free edges, and an inaudible
ambience loop point.
"""

import struct
import wave

import pygame

from src.audio import instruments
from src.audio.synth import (
    SAMPLE_RATE, crossfade_loop, envelope, mix, noise, normalize, tone,
)
from src.core import config  # noqa: F401 (SFX paths)
from src.systems.audio import AudioSystem


def _read_wav(path):
    with wave.open(str(path), "rb") as f:
        assert f.getnchannels() == 1, "expected mono"
        assert f.getframerate() == SAMPLE_RATE, f.getframerate()
        raw = f.readframes(f.getnframes())
    return [s / 32767 for (s,) in struct.iter_unpack("<h", raw)]


def test_tone_length_and_range() -> None:
    t = tone(440, 0.5)
    assert len(t) == int(0.5 * SAMPLE_RATE)
    assert all(-1.0 <= s <= 1.0 for s in t)


def test_envelope_silences_edges() -> None:
    e = envelope([1.0] * 1000, attack=0.01, release=0.01)
    assert e[0] < 0.02 and e[-1] < 0.02
    assert max(e) > 0.9  # sustain untouched


def test_normalize_hits_headroom_exactly() -> None:
    n = normalize([0.1, -0.2, 0.05], headroom=0.85)
    assert abs(max(abs(s) for s in n) - 0.85) < 1e-9


def test_mix_pads_to_longest() -> None:
    assert len(mix([1.0] * 10, [1.0] * 25)) == 25


def test_crossfade_loop_seam_is_continuous() -> None:
    # Use a smooth (lowpassed) signal — the guarantee is that the wrap
    # point becomes two ADJACENT samples of the original signal, so
    # seams are only as smooth as the source. White noise would jump.
    from src.audio.synth import lowpass

    src = lowpass(noise(3.0, seed=5), 500)
    buf = crossfade_loop(src, fade=0.5)
    assert len(buf) == int(2.5 * SAMPLE_RATE)
    n = int(0.5 * SAMPLE_RATE)
    # buf[0] is (almost entirely) the original tail's first sample...
    assert abs(buf[0] - src[len(src) - n]) < 0.05
    # ...and the wrap buf[-1] -> buf[0] is adjacent-sample smooth.
    assert abs(buf[-1] - buf[0]) < 0.1


def test_chult_percussion_voices_are_short_audible_and_click_free() -> None:
    for voice, frequency in (
        (instruments.jungle_tom, 147.0),
        (instruments.woodblock, 784.0),
    ):
        samples = voice(frequency, 0.2, 1.0)
        duration = len(samples) / SAMPLE_RATE
        assert 0.04 <= duration <= 0.2
        assert max(abs(sample) for sample in samples) >= 0.1
        assert abs(samples[0]) < 0.05 and abs(samples[-1]) < 0.05


def test_all_rendered_sfx_exist_and_respect_headroom() -> None:
    names = ["pickup", "interact", "hurt", "jump", "scratch", "vanish", "respawn", "chime",
             "footstep_wood_1", "footstep_wood_2",
             "footstep_stone_1", "footstep_stone_2"]
    for name in names:
        samples = _read_wav(config.SFX_DIR / f"{name}.wav")
        assert samples, f"{name} is empty"
        peak = max(abs(s) for s in samples)
        assert peak <= 0.9, f"{name} too hot ({peak:.2f}) — no headroom"
        assert abs(samples[0]) < 0.05 and abs(samples[-1]) < 0.05, \
            f"{name} has clicky edges"


def test_scratch_sfx_is_brief_and_audible() -> None:
    samples = _read_wav(config.SFX_DIR / "scratch.wav")
    duration = len(samples) / SAMPLE_RATE
    assert 0.08 <= duration <= 0.2, duration
    assert max(abs(s) for s in samples) >= 0.3


def test_jump_sfx_is_brief_quiet_and_audible() -> None:
    samples = _read_wav(config.SFX_DIR / "jump.wav")
    duration = len(samples) / SAMPLE_RATE
    peak = max(abs(s) for s in samples)
    zero_crossings = sum((a < 0) != (b < 0)
                         for a, b in zip(samples, samples[1:]))
    assert 0.07 <= duration <= 0.15, duration
    assert 0.15 <= peak <= 0.3, peak
    assert 20 <= zero_crossings <= 80, zero_crossings


def test_same_music_request_continues_without_restarting() -> None:
    """Shared Waterdeep interiors keep the current stream position."""
    audio = object.__new__(AudioSystem)
    audio.enabled = True
    audio.music_volume = 0.6
    audio._current_music = None
    calls = []
    original_load = pygame.mixer.music.load
    original_volume = pygame.mixer.music.set_volume
    original_play = pygame.mixer.music.play
    original_stop = pygame.mixer.music.stop
    try:
        pygame.mixer.music.load = lambda path: calls.append(("load", path))
        pygame.mixer.music.set_volume = lambda volume: calls.append(
            ("volume", volume)
        )
        pygame.mixer.music.play = lambda loops: calls.append(("play", loops))
        pygame.mixer.music.stop = lambda: calls.append(("stop",))

        audio.play_music("waterdeep_docks.wav")
        audio.play_music("waterdeep_docks.wav")
        assert [name for name, *_rest in calls].count("load") == 1
        assert [name for name, *_rest in calls].count("play") == 1

        audio.play_music("sewer.wav")
        assert [name for name, *_rest in calls].count("load") == 2
        assert audio._current_music == ("sewer.wav", True)

        audio.stop_music()
        audio.play_music("sewer.wav")
        assert [name for name, *_rest in calls].count("load") == 3
    finally:
        pygame.mixer.music.load = original_load
        pygame.mixer.music.set_volume = original_volume
        pygame.mixer.music.play = original_play
        pygame.mixer.music.stop = original_stop



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
    print("All audio tests passed.")


if __name__ == "__main__":
    _run_all()
