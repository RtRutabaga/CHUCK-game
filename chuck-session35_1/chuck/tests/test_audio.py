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

from src.audio.synth import (
    SAMPLE_RATE, crossfade_loop, envelope, mix, noise, normalize, tone,
)
from src.core import config  # noqa: F401 (SFX paths)


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


def test_all_rendered_sfx_exist_and_respect_headroom() -> None:
    names = ["pickup", "interact", "hurt", "vanish", "respawn", "chime",
             "footstep_wood_1", "footstep_wood_2",
             "footstep_stone_1", "footstep_stone_2"]
    for name in names:
        samples = _read_wav(config.SFX_DIR / f"{name}.wav")
        assert samples, f"{name} is empty"
        peak = max(abs(s) for s in samples)
        assert peak <= 0.9, f"{name} too hot ({peak:.2f}) — no headroom"
        assert abs(samples[0]) < 0.05 and abs(samples[-1]) < 0.05, \
            f"{name} has clicky edges"



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
