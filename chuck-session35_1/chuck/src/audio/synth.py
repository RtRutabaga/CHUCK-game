"""Synthesis primitives (Soundtrack Bible: shared, never duplicated).

Pure standard-library DSP for offline rendering: oscillators, noise,
envelopes, a one-pole filter, mixing, loop crossfading, and WAV output.
Buffers are plain lists of floats in -1..1; nothing here imports pygame
or any third-party package, so it runs (and is tested) anywhere.

This module is used by tools/generate_audio.py today and by the music
sequencer/instrument layers in the Waterdeep-theme session. Rendering
happens at dev time; the game only plays the cached WAVs.
"""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 22050  # deliberate retro-practical rate (Soundtrack Bible)


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------
def silence(duration: float) -> list[float]:
    return [0.0] * int(duration * SAMPLE_RATE)


def tone(
    freq: float, duration: float, wave_shape: str = "sine", duty: float = 0.5
) -> list[float]:
    """An oscillator: sine, triangle, or square (with duty cycle)."""
    n = int(duration * SAMPLE_RATE)
    out = []
    for i in range(n):
        phase = (freq * i / SAMPLE_RATE) % 1.0
        if wave_shape == "sine":
            v = math.sin(2 * math.pi * phase)
        elif wave_shape == "triangle":
            v = 4.0 * abs(phase - 0.5) - 1.0
        elif wave_shape == "square":
            v = 1.0 if phase < duty else -1.0
        else:
            raise ValueError(f"Unknown wave shape {wave_shape!r}")
        out.append(v)
    return out


def noise(duration: float, seed: int | None = None) -> list[float]:
    """White noise. Seedable so renders are reproducible."""
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(int(duration * SAMPLE_RATE))]


# ---------------------------------------------------------------------------
# Shaping
# ---------------------------------------------------------------------------
def envelope(
    samples: list[float], attack: float, release: float, sustain: float = 1.0
) -> list[float]:
    """Linear attack, sustain level, linear release. Click-free edges."""
    n = len(samples)
    a = min(int(attack * SAMPLE_RATE), n)
    r = min(int(release * SAMPLE_RATE), n - a)
    out = list(samples)
    for i in range(a):
        out[i] *= sustain * (i / a if a else 1.0)
    for i in range(a, n - r):
        out[i] *= sustain
    for i in range(r):
        out[n - r + i] *= sustain * (1.0 - (i + 1) / r)
    return out


def lowpass(samples: list[float], cutoff: float) -> list[float]:
    """One-pole lowpass. Cheap, warm, and good enough for 16-bit vibes."""
    if cutoff >= SAMPLE_RATE / 2:
        return list(samples)
    alpha = 1.0 - math.exp(-2.0 * math.pi * cutoff / SAMPLE_RATE)
    out, y = [], 0.0
    for x in samples:
        y += alpha * (x - y)
        out.append(y)
    return out


def gain(samples: list[float], amount: float) -> list[float]:
    return [s * amount for s in samples]


def tremolo(samples: list[float], rate_hz: float, depth: float,
            phase: float = 0.0) -> list[float]:
    """Slow amplitude LFO — wave swells are tremolo on filtered noise."""
    out = []
    for i, s in enumerate(samples):
        lfo = 0.5 + 0.5 * math.sin(2 * math.pi * (rate_hz * i / SAMPLE_RATE + phase))
        out.append(s * (1.0 - depth + depth * lfo))
    return out


# ---------------------------------------------------------------------------
# Combining
# ---------------------------------------------------------------------------
def mix(*layers: list[float]) -> list[float]:
    """Sum layers (padded to the longest). Normalize afterwards."""
    n = max(len(l) for l in layers)
    out = [0.0] * n
    for layer in layers:
        for i, s in enumerate(layer):
            out[i] += s
    return out


def normalize(samples: list[float], headroom: float = 0.85) -> list[float]:
    """Scale peak to `headroom` (never clip; preserve some ceiling)."""
    peak = max((abs(s) for s in samples), default=0.0)
    if peak == 0.0:
        return list(samples)
    return gain(samples, headroom / peak)


def crossfade_loop(samples: list[float], fade: float) -> list[float]:
    """Make a buffer loop seamlessly: blend its tail into its head,
    then trim the tail. The returned buffer's end flows into its start."""
    n = int(fade * SAMPLE_RATE)
    if n <= 0 or n * 2 > len(samples):
        raise ValueError("fade too long for buffer")
    body = samples[: len(samples) - n]
    for i in range(n):
        t = (i + 1) / n
        body[i] = samples[len(samples) - n + i] * (1.0 - t) + body[i] * t
    return body


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def write_wav(path: str | Path, samples: list[float]) -> None:
    """16-bit mono WAV at SAMPLE_RATE. Values are clamped defensively."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for s in samples:
            frames += struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767))
        f.writeframes(bytes(frames))
