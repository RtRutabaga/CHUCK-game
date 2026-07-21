"""Beholder boss-battle theme -- climactic, choral, and theatrical.

The sanctum's final fight. An original ~80-second loop in D Phrygian at
144 BPM: a relentless choral ostinato grinds the ominous flat-second
(Eb) against a pounding octave bass and orchestral timpani, while a horn
section soars over the top -- SNES boss-battle drive wearing the dark,
processional grandeur of a chanting film score. Nothing here quotes any
existing piece; the chant is built from the temple's own D/Eb/C modal
world so the boss feels like the temple turned lethal.

Structure (bars of 4/4, 48 bars):
    0-7    A     chant + pounding bass arrive; kit fills in, timpani hits
    8-15   A'    full drive, horn stabs punctuating the chant
    16-23  B     the horn melody soars; choir 'aahs' swell above
    24-31  C     dark build -- texture thins to chant + a timpani roll
    32-39  A''   the full drive returns at maximum energy
    40-47  Coda  a climactic horn phrase turns the loop back on itself

Eleven voices: chant, choir pad, horn, bass, sub, kick, snare, timpani,
toms, hats, and bells. Note tails wrap the loop end for a seamless cycle.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track

TEMPO_BPM = 144
BEATS_PER_BAR = 4
TOTAL_BARS = 48
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.95  # a loud, climactic mix -- the boss earns the ceiling


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for event in events:
            beat, duration, pitch = event[:3]
            velocity = event[3] if len(event) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, duration, pitch,
                              velocity))
    return notes


def _merge(*patterns: dict) -> dict:
    merged: dict = {}
    for pattern in patterns:
        for bar, events in pattern.items():
            merged.setdefault(bar, []).extend(events)
    return merged


# --- The chant: a driving eighth-note ostinato, D Phrygian -----------------
# Four one-bar cells (i, i, bII, bVII) hammered as a choir, grinding the
# flat-second Eb against the D tonic for menace.
_CHANT_CELL = (
    ("D3", "D3", "A3", "D3", "F3", "D3", "Eb3", "D3"),
    ("D3", "D3", "A3", "D3", "F3", "D3", "Eb3", "F3"),
    ("Eb3", "Eb3", "Bb3", "Eb3", "G3", "Eb3", "D3", "Eb3"),
    ("C3", "C3", "G3", "C3", "Eb3", "C3", "D3", "C3"),
)


def _chant(start_bar: int, bars: int, vel: float = 1.0) -> dict:
    out = {}
    for i in range(bars):
        cell = _CHANT_CELL[i % 4]
        events = []
        for j, pitch in enumerate(cell):
            accent = 1.0 if j == 0 else (0.86 if j % 2 == 0 else 0.66)
            events.append((j * 0.5, 0.5, pitch, accent * vel))
        out[start_bar + i] = events
    return out


# --- The bass: pounding octave eighths under the chant ---------------------
_ROOT4 = ("D", "D", "Eb", "C")
_FIFTH = {"D": "A2", "Eb": "Bb2", "C": "G2"}


def _bass(start_bar: int, bars: int, full: bool = True) -> dict:
    out = {}
    for i in range(bars):
        r = _ROOT4[i % 4]
        low, high, fifth = r + "2", r + "3", _FIFTH[r]
        if full:
            out[start_bar + i] = [
                (0, 0.45, low, 1.0), (0.5, 0.45, low, 0.72),
                (1, 0.45, fifth, 0.86), (1.5, 0.45, low, 0.72),
                (2, 0.45, high, 0.92), (2.5, 0.45, low, 0.72),
                (3, 0.45, fifth, 0.86), (3.5, 0.45, low, 0.74),
            ]
        else:
            out[start_bar + i] = [(0, 1.4, low, 0.92), (2, 1.4, high, 0.8)]
    return out


def _sub(start_bar: int, bars: int) -> dict:
    return {start_bar + i: [(0, 3.9, _ROOT4[i % 4] + "1", 0.42)]
            for i in range(bars)}


# --- Horns: stabs in the drive, a soaring melody in the B and coda ---------
def _horn_stabs(start_bar: int, bars: int) -> dict:
    out = {}
    for i in range(bars):
        r = _ROOT4[i % 4]
        chord_top = {"D": "A4", "Eb": "Bb4", "C": "G4"}[r]
        out[start_bar + i] = [
            (2.5, 0.4, r + "4", 0.8), (3.5, 0.45, chord_top, 0.85),
        ]
    return out


_HORN_B = {
    16: [(0, 2, "D4", 0.9), (2, 1, "F4", 0.85), (3, 1, "A4", 0.9)],
    17: [(0, 2, "Bb4", 0.95), (2, 2, "A4", 0.88)],
    18: [(0, 1, "G4", 0.82), (1, 1, "A4", 0.85), (2, 2, "Bb4", 0.9)],
    19: [(0, 3, "A4", 0.9)],
    20: [(0, 2, "D5", 1.0), (2, 1, "C5", 0.9), (3, 1, "Bb4", 0.88)],
    21: [(0, 2, "A4", 0.9), (2, 1, "Bb4", 0.85), (3, 1, "A4", 0.85)],
    22: [(0, 1, "G4", 0.85), (1, 1, "F4", 0.82), (2, 2, "Eb4", 0.92)],
    23: [(0, 3.5, "D4", 0.95)],
}
_HORN_CODA = {
    40: [(0, 1, "A4", 0.9), (1, 1, "Bb4", 0.9), (2, 1, "A4", 0.88),
         (3, 1, "D5", 0.95)],
    41: [(0, 2, "F5", 1.0), (2, 2, "D5", 0.92)],
    42: [(0, 2, "Eb5", 0.98), (2, 2, "D5", 0.92)],
    43: [(0, 3.5, "A4", 0.9)],
    44: [(0, 1, "Bb4", 0.9), (1, 1, "C5", 0.9), (2, 2, "D5", 0.98)],
    45: [(0, 2, "F5", 1.0), (2, 2, "Eb5", 0.95)],
    46: [(0, 2, "D5", 0.95), (2, 1, "A4", 0.88), (3, 1, "F4", 0.85)],
    47: [(0, 3.25, "D4", 0.9)],  # tapers before the loop point
}


# --- Choir pad: high sustained 'aahs' over the B and the dark build --------
_PAD_B = {
    16: [(0, 4, "A4", 0.46)], 17: [(0, 4, "D5", 0.46)],
    18: [(0, 4, "Bb4", 0.44)], 19: [(0, 4, "A4", 0.46)],
    20: [(0, 4, "D5", 0.48)], 21: [(0, 4, "F5", 0.42)],
    22: [(0, 4, "Eb5", 0.42)], 23: [(0, 4, "D5", 0.5)],
}
_PAD_C = {
    24: [(0, 4, "D4", 0.4)], 25: [(0, 4, "D4", 0.42)],
    26: [(0, 4, "Eb4", 0.44)], 27: [(0, 4, "Eb4", 0.46)],
    28: [(0, 4, "F4", 0.48)], 29: [(0, 4, "A4", 0.5)],
    30: [(0, 4, "Bb4", 0.54)], 31: [(0, 2, "A4", 0.56), (2, 2, "C5", 0.6)],
}


# --- Percussion ------------------------------------------------------------
def _kit(start_bar: int, bars: int, mode: str) -> tuple:
    """mode: 'drive' (full), 'lead-in' (sparse), or 'build' (crescendo)."""
    kick, snare, hats, toms, timp = {}, {}, {}, {}, {}
    for i in range(bars):
        bar = start_bar + i
        if mode == "drive":
            kick[bar] = [(0, 0.12, "C2", 1.0), (1, 0.12, "C2", 0.82),
                         (2, 0.12, "C2", 0.95), (3, 0.12, "C2", 0.82),
                         (2.5, 0.1, "C2", 0.6)]
            snare[bar] = [(1, 0.12, "C3", 0.85), (3, 0.12, "C3", 0.95)]
            hats[bar] = [(b * 0.5, 0.05, "C5", 0.55 if b % 2 else 0.72)
                         for b in range(8)]
            timp[bar] = [(0, 0.4, "D2", 0.9)] if i % 2 == 0 else []
        elif mode == "lead-in":
            kick[bar] = [(0, 0.12, "C2", 0.95), (2, 0.12, "C2", 0.85)]
            snare[bar] = [(3, 0.12, "C3", 0.7)] if i % 2 else []
            hats[bar] = [(b, 0.05, "C5", 0.5) for b in (1, 2, 3)]
            timp[bar] = [(0, 0.45, "D2", 0.95)]
        else:  # build -- a timpani roll and snare crescendo into bar 32
            step = 0.5 if i < 2 else 0.25
            beats = [round(k * step, 3) for k in range(int(4 / step))]
            base = 0.4 + 0.5 * (i / max(1, bars - 1))
            timp[bar] = [(b, step * 0.9, "D2", min(1.0, base)) for b in beats]
            snare[bar] = [(b, 0.1, "C3", min(0.95, base * 0.8))
                          for b in (beats if i >= 4 else beats[::2])]
            kick[bar] = [(0, 0.12, "C2", 0.9)]
            hats[bar] = []
        # A tom fill closes each eight-bar phrase.
        if i == bars - 1:
            toms[bar] = [(2, 0.15, "A3", 0.8), (2.5, 0.15, "F3", 0.85),
                         (3, 0.15, "D3", 0.9), (3.5, 0.15, "A2", 0.95)]
    return kick, snare, hats, toms, timp


def build_tracks() -> list[Track]:
    chant = _merge(
        _chant(0, 8, 0.86), _chant(8, 8), _chant(16, 8, 0.8),
        _chant(24, 4, 0.66), _chant(32, 8), _chant(40, 8),
    )
    # bars 28-31 leave the chant out so the dark build can breathe.

    bass = _merge(
        _bass(0, 8), _bass(8, 8), _bass(16, 8),
        _bass(24, 4), _bass(28, 4, full=False),
        _bass(32, 8), _bass(40, 8),
    )
    sub = _merge(_sub(0, 24), _sub(28, 20))

    horn = _merge(
        _horn_stabs(8, 8), _HORN_B, _horn_stabs(32, 8), _HORN_CODA,
    )
    pad = _merge(_PAD_B, _PAD_C, {
        44: [(0, 4, "A5", 0.4)], 45: [(0, 4, "F5", 0.4)],
        46: [(0, 4, "D5", 0.42)], 47: [(0, 3.5, "A4", 0.44)],
    })
    bells = {
        7: [(3, 1, "D6", 0.4)], 15: [(3, 1, "A5", 0.42)],
        20: [(0, 1, "D6", 0.44)], 23: [(2, 2, "A5", 0.4)],
        31: [(2, 2, "D6", 0.46)], 39: [(3, 1, "A5", 0.42)],
        45: [(0, 1, "F6", 0.44)], 47: [(0, 2, "D6", 0.42)],
    }

    sections = [
        _kit(0, 8, "lead-in"),
        _kit(8, 8, "drive"),
        _kit(16, 8, "drive"),
        _kit(24, 8, "build"),
        _kit(32, 8, "drive"),
        _kit(40, 8, "drive"),
    ]
    kick, snare, hats, toms, timp = (
        _merge(*(s[i] for s in sections)) for i in range(5)
    )

    return [
        Track("chant", ins.choir, 0.92, _bars(chant)),
        Track("choir_pad", ins.choir, 0.5, _bars(pad)),
        Track("horn", ins.brass, 0.9, _bars(horn)),
        Track("bass", ins.round_bass, 1.15, _bars(bass)),
        Track("sub", ins.round_bass, 0.5, _bars(sub)),
        Track("bells", ins.bell, 0.5, _bars(bells)),
        Track("kick", ins.kick, 1.05, _bars(kick)),
        Track("snare", ins.snare, 0.82, _bars(snare)),
        Track("timpani", ins.timpani, 1.0, _bars(timp)),
        Track("toms", ins.jungle_tom, 0.95, _bars(toms)),
        Track("hats", ins.hat, 0.72, _bars(hats)),
    ]
