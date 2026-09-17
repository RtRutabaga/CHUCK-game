"""Phlegethos theme --- dangerous, driving, and alive (Phase 8).

Hell here is an active, hostile PLACE, never quiet despair: a relentless
tribal tom groove over a throbbing low synth, struck metal ringing across
it like distant forges, and an eerie lead picking its way overhead. The
mode is E Phrygian dominant (E F G# A B C D) -- the raised third against
the flat second gives the exotic, menacing heat this realm needs, and
keeps it clearly distinct from the temple's D minor and the boss theme's
D Phrygian.

Nothing here imitates any existing soundtrack; it aims only at the same
emotional register -- driving rhythm, volcanic mystery, forward motion.

Structure (bars of 4/4, 48 bars, ~87s):
    0-7    A    toms, low pulse and metal establish the place
    8-15   A'   the eerie lead picks its way in
    16-23  B    the bass takes over and drives; the lead climbs
    24-31  C    "the environment is alive": choir swell, churning toms
    32-39  A''  full return at maximum drive
    40-47  D    a climbing turnaround that folds back into the loop

Twelve voices: lead, eerie flute, choir, low pulse, bass, metal hits,
bells, kick, snare, toms, woodblock, hats. Tails wrap the loop seam.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track

TEMPO_BPM = 132
BEATS_PER_BAR = 4
TOTAL_BARS = 48
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.93   # loud and physical, like the temple/boss renders


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for ev in events:
            beat, dur, pitch = ev[0], ev[1], ev[2]
            vel = ev[3] if len(ev) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, dur, pitch, vel))
    return notes


def _merge(*patterns: dict) -> dict:
    out: dict = {}
    for p in patterns:
        for bar, events in p.items():
            out.setdefault(bar, []).extend(events)
    return out


# --- Harmony: a four-bar infernal cycle, i - bII - i - bVII ---------------
_ROOTS = ("E1", "F1", "E1", "D1")
_FIFTH = {"E1": "B1", "F1": "C2", "D1": "A1"}
_OCTAVE = {"E1": "E2", "F1": "F2", "D1": "D2"}


def _pulse(start_bar: int, bars: int, busy: bool) -> dict:
    """The throbbing low synth: the ground breathing under everything."""
    out = {}
    for i in range(bars):
        root = _ROOTS[i % 4]
        if busy:
            out[start_bar + i] = [(0, 2, root, 0.9), (2, 1.5, root, 0.8),
                                  (3.5, 0.5, _FIFTH[root], 0.7)]
        else:
            out[start_bar + i] = [(0, 3.9, root, 0.85)]
    return out


def _bass(start_bar: int, bars: int, driving: bool) -> dict:
    """Root-fifth drive; `driving` doubles it into relentless eighths."""
    out = {}
    for i in range(bars):
        root = _ROOTS[i % 4]
        fifth, octave = _FIFTH[root], _OCTAVE[root]
        if driving:
            out[start_bar + i] = [
                (0, 0.45, octave, 1.0), (0.5, 0.45, octave, 0.72),
                (1, 0.45, fifth, 0.86), (1.5, 0.45, octave, 0.7),
                (2, 0.45, octave, 0.95), (2.5, 0.45, fifth, 0.74),
                (3, 0.45, octave, 0.88), (3.5, 0.45, fifth, 0.7),
            ]
        else:
            out[start_bar + i] = [
                (0, 0.7, octave, 0.95), (1.5, 0.4, fifth, 0.72),
                (2.5, 0.7, octave, 0.85), (3.5, 0.4, fifth, 0.7),
            ]
    return out


# --- The eerie lead: sparse, exotic, always moving somewhere ---------------
_LEAD_A = (
    ((0, 1, "E4"), (1, 0.5, "F4"), (1.5, 0.5, "G#4"), (2, 1.5, "B4"),
     (3.5, 0.5, "A4")),
    ((0, 1.5, "G#4"), (1.5, 0.5, "F4"), (2, 2, "E4")),
    ((0, 0.5, "B4"), (0.5, 0.5, "C5"), (1, 1, "B4"), (2, 1, "G#4"),
     (3, 1, "A4")),
    ((0, 3, "F4"),),
    ((0, 1, "E4"), (1, 0.5, "G#4"), (1.5, 0.5, "B4"), (2, 1.5, "E5"),
     (3.5, 0.5, "D5")),
    ((0, 1.5, "C5"), (1.5, 0.5, "B4"), (2, 2, "A4")),
    ((0, 0.5, "G#4"), (0.5, 0.5, "A4"), (1, 0.5, "B4"), (1.5, 0.5, "C5"),
     (2, 2, "B4")),
    ((0, 3.5, "E4"),),
)
_LEAD_B = (
    ((0, 0.5, "E5"), (0.5, 0.5, "D5"), (1, 0.5, "C5"), (1.5, 0.5, "B4"),
     (2, 1, "C5"), (3, 1, "D5")),
    ((0, 2, "E5"), (2, 1, "B4"), (3, 1, "C5")),
    ((0, 0.5, "D5"), (0.5, 0.5, "C5"), (1, 0.5, "B4"), (1.5, 0.5, "A4"),
     (2, 2, "G#4")),
    ((0, 1, "A4"), (1, 1, "B4"), (2, 2, "E4")),
    ((0, 0.5, "E5"), (0.5, 0.5, "F5"), (1, 1, "E5"), (2, 1, "C5"),
     (3, 1, "B4")),
    ((0, 2, "A4"), (2, 1, "B4"), (3, 1, "C5")),
    ((0, 0.5, "B4"), (0.5, 0.5, "C5"), (1, 0.5, "D5"), (1.5, 0.5, "E5"),
     (2, 2, "F5")),
    ((0, 3.5, "E5"),),
)


def _lead(start_bar: int, phrases, vel: float) -> dict:
    return {start_bar + i: [(b, d, p, vel) for b, d, p in phrase]
            for i, phrase in enumerate(phrases)}


# --- Percussion: the tribal engine ---------------------------------------
def _kit(start_bar: int, bars: int, mode: str) -> tuple:
    """mode: 'bed' (establishing), 'drive' (full), 'churn' (busiest)."""
    kick, snare, toms, wood, hats, metal = {}, {}, {}, {}, {}, {}
    for i in range(bars):
        bar = start_bar + i
        kick[bar] = [(0, 0.13, "C2", 1.0), (1.5, 0.12, "C2", 0.7),
                     (2, 0.13, "C2", 0.92), (3.25, 0.12, "C2", 0.66)]
        # Uneven tribal toms: a rolling 3+3+2 feel that never sits still.
        toms[bar] = [(0, 0.14, "E3", 0.95), (0.75, 0.14, "B2", 0.7),
                     (1.5, 0.14, "E3", 0.82), (2.25, 0.14, "A2", 0.72),
                     (3, 0.14, "E3", 0.86), (3.5, 0.14, "B2", 0.66)]
        if mode in {"drive", "churn"}:
            snare[bar] = [(1, 0.12, "C3", 0.8), (3, 0.12, "C3", 0.95)]
            wood[bar] = [(b * 0.5, 0.05, "B5", 0.5 if b % 2 else 0.62)
                         for b in range(8)]
        if mode == "churn":
            toms[bar].extend([(0.375, 0.1, "A2", 0.5),
                              (2.625, 0.1, "B2", 0.55)])
        hats[bar] = [(b, 0.05, "C5", 0.5 if b % 1 else 0.7)
                     for b in ((0.5, 1.5, 2.5, 3.5) if mode == "bed"
                               else (0.25, 0.75, 1.25, 1.75,
                                     2.25, 2.75, 3.25, 3.75))]
        # Struck metal rings across the groove -- distant infernal forges.
        if i % 2 == 0:
            metal[bar] = [(2, 1.6, "E3", 0.7)]
        if mode == "churn" and i % 4 == 3:
            metal.setdefault(bar, []).append((3.5, 1.2, "B3", 0.6))
    return kick, snare, toms, wood, hats, metal


def build_tracks() -> list[Track]:
    lead = _merge(
        _lead(8, _LEAD_A, 0.95),
        _lead(16, _LEAD_B, 1.0),
        _lead(32, _LEAD_A, 1.0),
        _lead(40, _LEAD_B, 0.95),
    )
    # The eerie upper voice: long exotic tones, sparse and watchful.
    flute = _merge(
        {2: [(2, 2, "B4", 0.4)], 5: [(0, 3, "F4", 0.38)],
         13: [(2, 2, "C5", 0.4)]},
        {24 + i: [(0, 4, p, 0.42)]
         for i, p in enumerate(("E4", "F4", "G#4", "A4",
                                "B4", "C5", "B4", "G#4"))},
        {45: [(0, 3, "E5", 0.4)], 47: [(0, 3.5, "B4", 0.38)]},
    )
    # A choir texture only where the place should feel alive and watching.
    choir = _merge(
        {24 + i: [(0, 4, p, 0.5)]
         for i, p in enumerate(("E3", "E3", "F3", "F3",
                                "E3", "D3", "E3", "E3"))},
        {46: [(0, 4, "E3", 0.42)], 47: [(0, 3.5, "B3", 0.4)]},
    )
    pulse = _merge(
        _pulse(0, 8, busy=False), _pulse(8, 8, busy=False),
        _pulse(16, 8, busy=True), _pulse(24, 8, busy=False),
        _pulse(32, 8, busy=True), _pulse(40, 8, busy=True),
    )
    bass = _merge(
        _bass(0, 8, driving=False), _bass(8, 8, driving=False),
        _bass(16, 8, driving=True), _bass(24, 8, driving=False),
        _bass(32, 8, driving=True), _bass(40, 8, driving=True),
    )
    bells = {7: [(3, 1, "E5", 0.34)], 15: [(3, 1, "B5", 0.34)],
             23: [(3, 1, "E5", 0.36)], 31: [(2, 2, "C6", 0.38)],
             39: [(3, 1, "B5", 0.34)], 47: [(2, 2, "E5", 0.36)]}

    sections = [
        _kit(0, 8, "bed"), _kit(8, 8, "drive"), _kit(16, 8, "drive"),
        _kit(24, 8, "churn"), _kit(32, 8, "drive"), _kit(40, 8, "churn"),
    ]
    kick, snare, toms, wood, hats, metal = (
        _merge(*(s[i] for s in sections)) for i in range(6))

    return [
        Track("lead", ins.pluck_lead, 0.9, _bars(lead)),
        Track("eerie", ins.flute, 0.62, _bars(flute)),
        Track("choir", ins.choir, 0.5, _bars(choir)),
        Track("pulse", ins.low_pulse, 0.95, _bars(pulse)),
        Track("bass", ins.round_bass, 1.15, _bars(bass)),
        Track("metal", ins.metal_hit, 0.85, _bars(metal)),
        Track("bells", ins.bell, 0.4, _bars(bells)),
        Track("kick", ins.kick, 1.05, _bars(kick)),
        Track("snare", ins.snare, 0.8, _bars(snare)),
        Track("toms", ins.jungle_tom, 1.1, _bars(toms)),
        Track("wood", ins.woodblock, 0.66, _bars(wood)),
        Track("hats", ins.hat, 0.7, _bars(hats)),
    ]


# --- What the fortress-approach battle arrangement is built from ----------
# The pit fiend's fight uses this theme's own mode, its four-bar cycle and
# both of its lead phrases, played hot. Exported rather than copied, so
# the fight cannot drift into being a different tune.
ROOTS, FIFTH, OCTAVE = _ROOTS, _FIFTH, _OCTAVE
LEAD_A, LEAD_B = _LEAD_A, _LEAD_B
