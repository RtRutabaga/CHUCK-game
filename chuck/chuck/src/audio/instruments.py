"""Instrument voices (Soundtrack Bible: NES/SNES-inspired palette).

Each instrument is a function (freq_hz, duration_s, velocity) -> samples,
built from src/audio/synth primitives. Shared by every track; never
duplicated per composition.
"""

from __future__ import annotations

import math

from src.audio.synth import (
    SAMPLE_RATE, envelope, gain, lowpass, mix, noise, tone,
)


def _vibrato_sine(freq: float, dur: float, rate: float, depth: float
                  ) -> list[float]:
    """A sine with gentle pitch vibrato (phase-accumulated)."""
    out, phase = [], 0.0
    n = int(dur * SAMPLE_RATE)
    for i in range(n):
        f = freq * (1.0 + depth * math.sin(2 * math.pi * rate * i / SAMPLE_RATE))
        phase += f / SAMPLE_RATE
        out.append(math.sin(2 * math.pi * phase))
    return out


def _highpassed_noise(dur: float, cutoff: float, seed: int) -> list[float]:
    """Highpass by subtraction (all we need for hats/snare sizzle)."""
    n = noise(dur, seed=seed)
    low = lowpass(n, cutoff)
    return [a - b for a, b in zip(n, low)]


# ---------------------------------------------------------------------------
# Pitched voices
# ---------------------------------------------------------------------------
def pluck_lead(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Plucked lead: narrow pulse + sub octave, quick natural decay."""
    body = mix(
        tone(freq, dur, "square", duty=0.25),
        gain(tone(freq / 2, dur), 0.3),
    )
    return gain(envelope(lowpass(body, 2800), 0.003, dur * 0.65, sustain=0.9),
                vel * 0.5)


def flute(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Soft flute: vibrato sine + faint 2nd harmonic, gentle attack."""
    body = mix(
        _vibrato_sine(freq, dur, rate=5.5, depth=0.008),
        gain(tone(freq * 2, dur), 0.12),
    )
    return gain(envelope(lowpass(body, 3600), 0.05, min(0.25, dur * 0.4)),
                vel * 0.55)


def round_bass(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Round bass: triangle + sub sine, softened top."""
    body = mix(tone(freq, dur, "triangle"), gain(tone(freq / 2, dur), 0.4))
    return gain(envelope(lowpass(body, 700), 0.005, min(0.2, dur * 0.3)),
                vel * 0.75)


def bell(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Soft bell: detuned partials, long release."""
    body = mix(
        tone(freq, dur),
        gain(tone(freq * 2.01, dur), 0.4),
        gain(tone(freq * 2.99, dur), 0.15),
    )
    return gain(envelope(lowpass(body, 4200), 0.003, dur * 0.9), vel * 0.4)


# ---------------------------------------------------------------------------
# Percussion (freq is ignored or used loosely for tuning)
# ---------------------------------------------------------------------------
def kick(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    body = mix(
        envelope(tone(max(55.0, freq / 4), 0.10), 0.001, 0.09),
        envelope(gain(noise(0.015, seed=11), 0.4), 0.001, 0.012),
    )
    return gain(lowpass(body, 300), vel * 0.9)


def snare(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    body = mix(
        envelope(_highpassed_noise(0.10, 1200, seed=12), 0.001, 0.09),
        envelope(gain(tone(190.0, 0.06), 0.5), 0.001, 0.05),
    )
    return gain(body, vel * 0.5)


def hat(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    return gain(envelope(_highpassed_noise(0.035, 5200, seed=13),
                         0.001, 0.03), vel * 0.28)


def jungle_tom(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Warm hand-drum/tom voice for low, pitched percussion patterns."""
    body = mix(
        tone(max(70.0, freq / 2), 0.16, "triangle"),
        gain(tone(max(55.0, freq / 4), 0.18), 0.55),
        gain(noise(0.012, seed=21), 0.18),
    )
    return gain(envelope(lowpass(body, 900), 0.001, 0.15), vel * 0.62)


def woodblock(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Short woody click: pitched enough to groove, dry enough to stay retro."""
    body = mix(
        tone(max(280.0, freq), 0.045, "square", duty=0.2),
        gain(noise(0.018, seed=22), 0.25),
    )
    return gain(envelope(lowpass(body, 2400), 0.001, 0.04), vel * 0.32)
