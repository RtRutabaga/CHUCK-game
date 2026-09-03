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
    jump        a tiny rounded bounce tone — movement, not a large impact
    scratch     a short filtered scrape — quick motion, no sword clang
    vanish      three soft falling tones ending unresolved
    respawn     two quiet rising bells — a restrained return
    chime       a single soft bell — the anchor attunes. Singular.
    portal_hum      a held airy chord shimmering — a mouth standing open
    portal_collapse an inward rising rush closing on a soft knock
    lighter         two dry scrapes and a small flame catching
    footsteps   tiny filtered taps; wood is deeper, stone is drier;
                two variants each so steps don't machine-gun
"""

import math
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


def sfx_jump() -> list[float]:
    """A quiet rounded upward bounce with no scratchy noise layer."""
    duration = 0.12
    sample_count = int(duration * SAMPLE_RATE)
    phase = 0.0
    bounce = []
    for i in range(sample_count):
        progress = i / max(1, sample_count - 1)
        eased = progress * progress * (3.0 - 2.0 * progress)
        frequency = 155.0 + 105.0 * eased
        phase += 2.0 * math.pi * frequency / SAMPLE_RATE
        bounce.append(math.sin(phase) + 0.08 * math.sin(phase * 2.0))
    return normalize(envelope(bounce, 0.004, 0.105), headroom=0.24)


def sfx_scratch() -> list[float]:
    """A dry two-part scrape: filtered noise with a tiny tonal edge."""
    first = envelope(lowpass(noise(0.11, seed=47), 4600), 0.001, 0.09)
    second = _pad(
        envelope(lowpass(noise(0.09, seed=48), 3200), 0.001, 0.075),
        0.025,
    )
    edge = envelope(gain(tone(1150, 0.09, "triangle"), 0.16),
                    0.001, 0.075)
    return normalize(mix(first, gain(second, 0.7), edge), headroom=0.45)


def sfx_vanish() -> list[float]:
    """Three falling tones; the last interval refuses to resolve."""
    notes = []
    for i, freq in enumerate((440.0, 349.2, 246.9)):  # A4, F4, B3
        pair = mix(tone(freq, 0.4, "triangle"),
                   gain(tone(freq * 1.006, 0.4, "triangle"), 0.5))
        notes.append(_pad(envelope(lowpass(pair, 2600), 0.01, 0.3), i * 0.22))
    return normalize(mix(*notes), headroom=0.45)


def sfx_beholder_blast() -> list[float]:
    """A deep detonation: a sub-bass drop, a filtered slam, a low growl.

    The beholder's cone of force landing — felt more than heard, meant
    to pair with the screen shake as the wall of energy hits."""
    dur = 0.7
    n = int(dur * SAMPLE_RATE)
    drop = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 120.0 - 80.0 * (t / dur)  # 120 Hz sinking to 40 Hz
        drop.append(math.sin(2.0 * math.pi * freq * t))
    drop = envelope(gain(drop, 0.9), 0.005, 0.6)
    slam = envelope(lowpass(noise(dur, seed=61), 900), 0.001, 0.5)
    growl = envelope(lowpass(tone(70.0, dur, "square"), 520), 0.01, 0.6)
    return normalize(mix(drop, gain(slam, 0.7), gain(growl, 0.5)),
                     headroom=0.5)


def sfx_fireball() -> list[float]:
    """The scripted Fireball: a rising whoosh into a roaring detonation.

    Bigger and brighter than the beholder's cone blast — the climactic
    explosion that ends the fight and throws Chuck into the rubble."""
    dur = 1.0
    n = int(dur * SAMPLE_RATE)
    # A swelling roar: broadband noise opening up over the first beat.
    roar = []
    for i in range(n):
        t = i / SAMPLE_RATE
        cutoff = 400.0 + 4200.0 * min(1.0, t / 0.35)  # filter sweeps open
        roar.append(cutoff)
    body = lowpass(noise(dur, seed=71), 5000)
    body = envelope(body, 0.18, 0.7)  # slow attack (the whoosh), long tail
    # A sub-bass thump at the moment of detonation.
    thump = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 90.0 - 55.0 * min(1.0, t / dur)
        thump.append(math.sin(2.0 * math.pi * freq * t))
    thump = _pad(envelope(gain(thump, 0.95), 0.001, 0.55), 0.22)
    crackle = envelope(gain(noise(dur, seed=72), 0.5), 0.2, 0.7)
    return normalize(mix(body, thump, gain(crackle, 0.4)), headroom=0.5)


def sfx_portal_hum() -> list[float]:
    """A planar mouth standing open: airy, tuned, and barely there.

    A held fifth with an octave over it, shimmering rather than beating.
    Written first as two tones a hair apart it throbbed slowly against
    itself, which sounded haunted -- wrong for a scene whose music is a
    cheerful little tune in D Dorian. Fast and shallow it reads as light
    instead. Nothing percussive either way: it is a hole in the air, and
    a hole does not have an attack.
    """
    dur = 2.2
    chord = mix(
        tone(293.7, dur, "triangle"),
        gain(tone(440.0, dur, "triangle"), 0.55),
        gain(tone(587.3, dur, "triangle"), 0.34),
        gain(tone(880.0, dur, "triangle"), 0.16),
    )
    breath = gain(lowpass(noise(dur, seed=91), 2000), 0.16)
    body = envelope(lowpass(mix(chord, breath), 3200), attack=0.4, release=1.5)
    return normalize(tremolo(body, 7.5, 0.18), headroom=0.28)


def sfx_portal_collapse() -> list[float]:
    """The mouth folding into itself: everything runs inward, then stops.

    A rising tone rather than a falling one, because the thing is being
    drawn to a point and not dropped. It ends on a soft closed knock
    with no tail -- nothing is destroyed here, something is shut.
    """
    dur = 1.1
    n = int(dur * SAMPLE_RATE)
    inward = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # 180 Hz climbing away as the opening narrows, then gone.
        freq = 180.0 + 900.0 * (t / dur) ** 2.2
        inward.append(math.sin(2.0 * math.pi * freq * t))
    inward = envelope(gain(inward, 0.55), 0.02, 0.35)
    rush = envelope(lowpass(noise(dur, seed=92), 3000), 0.6, 0.3)
    shut = _pad(
        envelope(lowpass(tone(88.0, 0.16, "triangle"), 700), 0.001, 0.14),
        0.94,
    )
    return normalize(mix(inward, gain(rush, 0.4), gain(shut, 0.8)),
                     headroom=0.42)


def sfx_lighter() -> list[float]:
    """A thumb on a wheel, then a small flame catching.

    Two dry scrapes and a soft breath of flame. It has to be quiet: it
    is the smallest event in a scene where a portal has just closed.
    """
    scrapes = [
        _pad(envelope(gain(lowpass(noise(0.05, seed=93 + i), 5200), 0.7),
                      0.001, 0.04), i * 0.16)
        for i in range(2)
    ]
    catch = _pad(
        envelope(lowpass(noise(0.5, seed=95), 1800), 0.02, 0.42), 0.3)
    return normalize(mix(*scrapes, gain(catch, 0.55)), headroom=0.28)


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
        "jump.wav": sfx_jump,
        "scratch.wav": sfx_scratch,
        "vanish.wav": sfx_vanish,
        "respawn.wav": sfx_respawn,
        "chime.wav": sfx_chime,
        "beholder_blast.wav": sfx_beholder_blast,
        "fireball.wav": sfx_fireball,
        "portal_hum.wav": sfx_portal_hum,
        "portal_collapse.wav": sfx_portal_collapse,
        "lighter.wav": sfx_lighter,
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
