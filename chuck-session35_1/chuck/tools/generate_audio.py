"""Render the Phase One SFX set to WAV.
(Music lives in tools/generate_music.py; the old synthesized harbor
ambience was cut — it read as static on real speakers.)

Run from the project root (pure stdlib — no extra dependencies):

    python tools/generate_audio.py

Writes assets/audio/sfx/*.wav.
Rendering happens here at dev time (Soundtrack Bible); the game only
plays these cached files.

Sound design intent (Bible: understated, dry, never cartoonish):
    pickup      two quick warm plucks — small satisfaction
    interact    one very soft blip — a page turning
    hurt        a dry low thud — inconvenience, not tragedy
    vanish      three soft falling tones ending unresolved
    respawn     two quiet rising bells — a restrained return
    chime       a single soft bell — the anchor attunes. Singular.
    footsteps   tiny filtered taps; wood is deeper, stone is drier;
                two variants each so steps don't machine-gun
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.audio.synth import (
    SAMPLE_RATE, crossfade_loop, envelope, gain, lowpass, mix, noise,
    normalize, silence, tone, tremolo, write_wav,
)

SFX_DIR = ROOT / "assets" / "audio" / "sfx"
MUSIC_DIR = ROOT / "assets" / "audio" / "music"


def _pluck(freq: float, dur: float, cutoff: float = 3200) -> list[float]:
    """A warm plucked note: sine + quiet octave, fast decay."""
    body = mix(tone(freq, dur), gain(tone(freq * 2, dur), 0.35))
    return envelope(lowpass(body, cutoff), attack=0.004, release=dur * 0.8)


def _bell(freq: float, dur: float) -> list[float]:
    """A soft bell: fundamental + detuned upper partials, long release."""
    body = mix(
        tone(freq, dur),
        gain(tone(freq * 2.01, dur), 0.4),
        gain(tone(freq * 2.99, dur), 0.15),
    )
    return envelope(lowpass(body, 4200), attack=0.003, release=dur * 0.9)


def _pad(samples: list[float], start: float) -> list[float]:
    return silence(start) + samples


def sfx_pickup() -> list[float]:
    return normalize(
        mix(_pad(_pluck(659.3, 0.16), 0.0), _pad(_pluck(880.0, 0.22), 0.07)),
        headroom=0.5,
    )


def sfx_interact() -> list[float]:
    blip = envelope(lowpass(tone(523.3, 0.05, "square", duty=0.3), 1800),
                    attack=0.004, release=0.04)
    return normalize(blip, headroom=0.3)


def sfx_hurt() -> list[float]:
    thud = mix(
        envelope(lowpass(noise(0.14, seed=7), 420), 0.002, 0.12),
        envelope(gain(tone(82.0, 0.16), 0.9), 0.002, 0.14),
    )
    return normalize(thud, headroom=0.6)


def sfx_vanish() -> list[float]:
    """Three falling tones; the last interval refuses to resolve."""
    notes = []
    for i, freq in enumerate((440.0, 349.2, 246.9)):  # A4, F4, B3
        pair = mix(tone(freq, 0.4, "triangle"),
                   gain(tone(freq * 1.006, 0.4, "triangle"), 0.5))
        notes.append(_pad(envelope(lowpass(pair, 2600), 0.01, 0.3), i * 0.22))
    return normalize(mix(*notes), headroom=0.45)


def sfx_respawn() -> list[float]:
    return normalize(
        mix(_pad(_bell(392.0, 0.5), 0.0), _pad(_bell(587.3, 0.6), 0.18)),
        headroom=0.4,
    )


def sfx_chime() -> list[float]:
    return normalize(_bell(784.0, 0.8), headroom=0.35)


def _footstep(thump_hz: float, cutoff: float, dur: float, seed: int) -> list[float]:
    tap = mix(
        envelope(lowpass(noise(dur, seed=seed), cutoff), 0.001, dur * 0.85),
        envelope(gain(tone(thump_hz, dur * 0.7), 0.5), 0.001, dur * 0.6),
    )
    return normalize(tap, headroom=0.30)



def main() -> None:
    sounds = {
        "pickup.wav": sfx_pickup,
        "interact.wav": sfx_interact,
        "hurt.wav": sfx_hurt,
        "vanish.wav": sfx_vanish,
        "respawn.wav": sfx_respawn,
        "chime.wav": sfx_chime,
    }
    for i, (hz, cut, dur) in enumerate(((150, 800, 0.07), (135, 750, 0.075))):
        sounds[f"footstep_wood_{i + 1}.wav"] = (
            lambda hz=hz, cut=cut, dur=dur, i=i: _footstep(hz, cut, dur, 20 + i)
        )
    for i, (hz, cut, dur) in enumerate(((230, 1900, 0.05), (210, 1750, 0.055))):
        sounds[f"footstep_stone_{i + 1}.wav"] = (
            lambda hz=hz, cut=cut, dur=dur, i=i: _footstep(hz, cut, dur, 30 + i)
        )
    for name, build in sounds.items():
        write_wav(SFX_DIR / name, build())
        print(f"Wrote sfx/{name}")


if __name__ == "__main__":
    main()
