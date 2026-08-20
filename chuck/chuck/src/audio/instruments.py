"""Instrument voices (Soundtrack Bible: NES/SNES-inspired palette).

Each instrument is a function (freq_hz, duration_s, velocity) -> samples,
built from src/audio/synth primitives. Shared by every track; never
duplicated per composition.
"""

from __future__ import annotations

import math

from src.audio.synth import (
    SAMPLE_RATE, envelope, gain, lowpass, mix, noise, tone, tremolo,
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


def choir(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Massed voices on a vowel: the boss theme's ominous chant.

    A wavering fundamental with an octave shimmer and a fifth for the
    'ah' body, warmed by a formant-ish lowpass. The swelled attack lets
    even a short chant syllable bloom, so a driving ostinato of these
    reads as a choir hammering the room."""
    body = mix(
        _vibrato_sine(freq, dur, rate=5.2, depth=0.007),
        gain(tone(freq * 2.0, dur), 0.30),   # octave shimmer
        gain(tone(freq * 1.5, dur), 0.16),   # fifth -> vowel color
        gain(tone(freq * 3.0, dur), 0.07),   # a breath of upper air
    )
    body = lowpass(body, 2300)
    return gain(envelope(body, min(0.05, dur * 0.35),
                         min(dur * 0.55, dur), sustain=0.95), vel * 0.5)


def brass(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Cutting horn section: a bright pulse over a triangle body and a
    sub for weight. Carries the theatrical melody and the stabs."""
    body = mix(
        tone(freq, dur, "square", duty=0.4),
        gain(tone(freq, dur, "triangle"), 0.75),
        gain(tone(freq / 2, dur, "triangle"), 0.28),
    )
    body = lowpass(body, 2700)
    return gain(envelope(body, min(0.025, dur * 0.2),
                         min(0.3, dur * 0.5), sustain=0.95), vel * 0.46)


def enchanted_mallet(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Warm wooden mallet with a glassy, deliberately imperfect overtone."""
    body = mix(
        tone(freq, dur, "triangle"),
        gain(tone(freq * 2.01, dur), 0.32),
        gain(tone(freq * 3.98, dur), 0.10),
    )
    strike = envelope(noise(min(0.018, dur), seed=61), 0.001,
                      min(0.016, dur))
    body = mix(lowpass(body, 3300), gain(strike, 0.18))
    return gain(envelope(body, 0.002, max(0.03, dur * 0.82)),
                vel * 0.52)


def breathy_reed(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Woody enchanted reed: warm vibrato body with restrained breath."""
    body = mix(
        _vibrato_sine(freq, dur, rate=4.7, depth=0.011),
        gain(tone(freq, dur, "triangle"), 0.36),
        gain(tone(freq * 2, dur), 0.10),
        gain(_highpassed_noise(dur, 2600, seed=62), 0.055),
    )
    return gain(
        envelope(lowpass(body, 3100), min(0.09, dur * 0.25),
                 min(0.35, dur * 0.35), sustain=0.92),
        vel * 0.47,
    )


def reverse_bell(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """A backwards-feeling magical swell that still ends click-free."""
    body = mix(
        tone(freq, dur),
        gain(tone(freq * 2.02, dur), 0.34),
        gain(tone(freq * 3.01, dur), 0.13),
    )
    body = lowpass(body, 3900)
    n = len(body)
    out = []
    for index, sample in enumerate(body):
        progress = index / max(1, n - 1)
        rise = progress ** 1.8
        # Preserve the reverse gesture, then close the final 6% cleanly.
        release = min(1.0, (1.0 - progress) / 0.06)
        out.append(sample * rise * max(0.0, release))
    return gain(out, vel * 0.43)


def cloud_pad(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Wide, slow-blooming 16-bit pad for open sky and immense spaces."""
    body = mix(
        _vibrato_sine(freq, dur, rate=3.1, depth=0.004),
        gain(_vibrato_sine(freq * 1.005, dur, rate=2.7, depth=0.003), 0.52),
        gain(tone(freq / 2, dur, "triangle"), 0.24),
        gain(tone(freq * 2, dur), 0.08),
    )
    body = lowpass(body, 2400)
    return gain(
        envelope(body, min(0.42, dur * 0.22), min(0.7, dur * 0.3),
                 sustain=0.94),
        vel * 0.38,
    )


def elastic_bass(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Rubbery funk bass with a quick upward pitch scoop on each note."""
    n = int(dur * SAMPLE_RATE)
    phase = 0.0
    body = []
    for index in range(n):
        seconds = index / SAMPLE_RATE
        scoop = 0.90 + 0.10 * (1.0 - math.exp(-seconds / 0.045))
        phase = (phase + freq * scoop / SAMPLE_RATE) % 1.0
        body.append(4.0 * abs(phase - 0.5) - 1.0)
    body = mix(body, gain(tone(freq / 2, dur), 0.32))
    return gain(
        envelope(lowpass(body, 820), 0.003, min(0.16, dur * 0.35)),
        vel * 0.72,
    )


def neon_synth_lead(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Bright, confident retro lead with a tight electronic edge."""
    body = mix(
        tone(freq, dur, "square"),
        gain(tone(freq * 1.006, dur, "square"), 0.38),
        gain(tone(freq / 2, dur, "triangle"), 0.28),
    )
    body = lowpass(body, 3100)
    return gain(
        envelope(body, 0.004, min(0.13, dur * 0.34), sustain=0.82),
        vel * 0.43,
    )


def pulse_arp(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Short filtered pulse for a clean 16-bit techno arpeggio."""
    body = mix(
        tone(freq, dur, "square"),
        gain(tone(freq * 2, dur, "triangle"), 0.18),
    )
    return gain(
        envelope(lowpass(body, 2200), 0.002, min(0.08, dur * 0.7)),
        vel * 0.32,
    )


def electric_key(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """A tine electric piano: the modern city's jazz harmony voice.

    A struck metal tine over a soft body -- the bell partial rings a
    little sharp and dies quickly, leaving a rounded sine to sustain, so
    a stacked chord reads as an electric piano rather than a chime.
    """
    tine = gain(envelope(tone(freq * 4.02, dur), 0.001, min(0.09, dur)), 0.30)
    body = mix(
        tone(freq, dur),
        gain(tone(freq * 2.0, dur), 0.22),
        gain(tone(freq / 2, dur), 0.18),
    )
    voiced = envelope(lowpass(body, 2600), 0.004, dur * 0.75)
    return gain(mix(voiced, tine), vel * 0.42)


def synth_bass(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """A clipped, syncopated square bass with a fast filter thump.

    Rounder than the temple's low pulse and drier than the elastic funk
    bass: it wants to sit under a jazz chord and get out of the way.
    """
    body = mix(
        tone(freq, dur, "square"),
        gain(tone(freq / 2, dur), 0.42),
    )
    thump = envelope(lowpass(body, 480), 0.002, min(0.05, dur * 0.4))
    voiced = envelope(lowpass(body, 900), 0.004, min(0.22, dur * 0.55))
    return gain(mix(voiced, gain(thump, 0.5)), vel * 0.66)


def rain_wash(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Wet reflected air: filtered noise swelling and falling away.

    Pitched loosely by freq so it can follow the harmony without ever
    being heard as a note.
    """
    body = lowpass(noise(dur), max(400.0, min(2400.0, freq * 3.0)))
    return gain(tremolo(envelope(body, dur * 0.35, dur * 0.6), 0.6, 0.25),
                vel * 0.14)


def hollow_pipe(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """A struck utility pipe: odd harmonics only, ringing in a tube.

    Suppressing the even partials is what makes it read as hollow rather
    than as a bell, and the short noise chiff at the front is the sound
    of something small hitting metal in a concrete tunnel.
    """
    body = mix(
        tone(freq, dur),
        gain(tone(freq * 3.0, dur), 0.34),     # odd partials only: a tube
        gain(tone(freq * 5.0, dur), 0.16),
        gain(tone(freq * 7.0, dur), 0.07),
    )
    ring = envelope(lowpass(body, 3400), 0.002, dur * 0.72)
    chiff = envelope(_highpassed_noise(0.02, 2200, seed=57), 0.001, 0.02)
    return gain(mix(ring, gain(chiff, 0.35)), vel * 0.34)


def sewer_drip(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """One drip landing in standing water: a fast downward blip.

    Pitched by freq only loosely -- it falls away too quickly to be
    heard as a note, which is the point.
    """
    n = int(min(dur, 0.16) * SAMPLE_RATE)
    phase = 0.0
    body = []
    for index in range(n):
        seconds = index / SAMPLE_RATE
        # A sharp downward sweep: the classic drip contour.
        sweep = max(0.25, 1.0 - seconds * 7.0)
        phase = (phase + freq * sweep / SAMPLE_RATE) % 1.0
        body.append(math.sin(phase * 2.0 * math.pi))
    return gain(envelope(lowpass(body, 3000), 0.001, 0.09), vel * 0.22)


# ---------------------------------------------------------------------------
# Percussion (freq is ignored or used loosely for tuning)
# ---------------------------------------------------------------------------
def metal_hit(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """A struck-metal clang: inharmonic partials over a bright noise
    transient, ringing out. Phlegethos's forge-and-chain percussion."""
    f = max(90.0, freq)
    body = mix(
        tone(f, dur),
        gain(tone(f * 2.76, dur), 0.55),   # deliberately inharmonic, so it
        gain(tone(f * 5.40, dur), 0.30),   # reads as metal, not as a pitch
        gain(tone(f * 8.93, dur), 0.16),
    )
    ring = envelope(lowpass(body, 6200), 0.001, dur * 0.9)
    strike = envelope(_highpassed_noise(0.03, 3000, seed=41), 0.001, 0.028)
    return gain(mix(ring, gain(strike, 0.5)), vel * 0.34)


def low_pulse(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """A pulsing low synth: a narrow filtered square throbbing under the
    groove, so the ground itself feels alive and moving."""
    body = mix(
        tone(freq, dur, "square", duty=0.34),
        gain(tone(freq / 2, dur, "triangle"), 0.5),
    )
    body = lowpass(body, 480)
    # The throb: a fast tremolo keeps it in motion rather than droning.
    body = tremolo(body, rate_hz=6.4, depth=0.55)
    return gain(envelope(body, 0.02, min(0.25, dur * 0.35), sustain=0.95),
                vel * 0.6)


def timpani(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """A tuned orchestral boom: low sine body with a soft mallet thud
    and a longer decay than the hand-tom. Big dramatic accents."""
    f = max(48.0, freq)
    body = mix(
        envelope(tone(f, 0.45, "sine"), 0.002, 0.42),
        gain(tone(f * 1.5, 0.2), 0.18),      # a faint tuned overtone
        gain(envelope(noise(0.04, seed=31), 0.001, 0.038), 0.28),
    )
    return gain(lowpass(body, 420), vel * 0.85)
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


def tabla_dayan(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Dry, tuned hand-drum stroke inspired by a tabla's higher drum.

    This is an original synthetic color rather than a sampled or reproduced
    traditional performance: a short pitched ring, a woody partial, and a
    fingertip transient keep it readable in the game's compact retro mix.
    """
    f = max(150.0, freq)
    body = mix(
        tone(f, 0.14),
        gain(tone(f * 1.48, 0.10, "triangle"), 0.30),
        gain(noise(0.009, seed=71), 0.16),
    )
    return gain(envelope(lowpass(body, 2400), 0.001, 0.12), vel * 0.48)


def tabla_bayan(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Rounded low hand-drum stroke with a quick downward pitch bend."""
    f = max(62.0, freq / 2)
    length = min(0.24, max(0.10, dur))
    phase = 0.0
    body = []
    for index in range(int(length * SAMPLE_RATE)):
        seconds = index / SAMPLE_RATE
        bend = 1.22 - 0.22 * min(1.0, seconds / 0.08)
        phase += f * bend / SAMPLE_RATE
        body.append(math.sin(2.0 * math.pi * phase))
    strike = envelope(noise(0.012, seed=72), 0.001, 0.01)
    return gain(
        envelope(lowpass(mix(body, gain(strike, 0.12)), 650), 0.001,
                 length * 0.88),
        vel * 0.70,
    )


def jaw_harp(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """A short metallic jaw-harp twang with a decaying mouth resonance.

    A bent pulse provides the vibrating tongue while a quick moving formant
    makes the hit read as a jaw harp rather than another bass pluck. The voice
    is deliberately compact so occasional offbeat accents stay clear of the
    Cabin's elastic bass figure.
    """
    length = min(0.34, max(0.12, dur))
    f = max(82.0, freq)
    count = int(length * SAMPLE_RATE)
    phase = 0.0
    body = []
    for index in range(count):
        seconds = index / SAMPLE_RATE
        bend = 1.16 - 0.16 * min(1.0, seconds / 0.055)
        wobble = 1.0 + 0.012 * math.sin(2 * math.pi * 13.0 * seconds)
        phase = (phase + f * bend * wobble / SAMPLE_RATE) % 1.0
        tongue = 1.0 if phase < 0.18 else -0.42
        mouth = math.sin(2 * math.pi * f * 3.02 * seconds)
        pulse = 0.72 + 0.28 * math.sin(2 * math.pi * 7.0 * seconds)
        body.append((tongue * 0.72 + mouth * 0.28) * pulse)
    click = envelope(_highpassed_noise(0.012, 2100, seed=79), 0.001, 0.010)
    voiced = envelope(lowpass(body, 2600), 0.001, length * 0.88)
    return gain(mix(voiced, gain(click, 0.28)), vel * 0.38)


def woodblock(freq: float, dur: float, vel: float = 1.0) -> list[float]:
    """Short woody click: pitched enough to groove, dry enough to stay retro."""
    body = mix(
        tone(max(280.0, freq), 0.045, "square", duty=0.2),
        gain(noise(0.018, seed=22), 0.25),
    )
    return gain(envelope(lowpass(body, 2400), 0.001, 0.04), vel * 0.32)
