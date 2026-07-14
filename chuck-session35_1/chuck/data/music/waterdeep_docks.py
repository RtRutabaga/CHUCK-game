"""The Waterdeep Docks daytime theme — composition data.

Original piece, ~95 seconds per cycle. D mixolydian at 96 BPM: warm and
coastal, with the mode's flat seventh (C natural) supplying the "faint
undercurrent of something strange" the Soundtrack Bible asks for.

Structure (bars of 4/4):
    0-3    Intro       bass + bells; the harbor waking up
    4-11   A           plucked-lead melody enters, light percussion
    12-19  A'          melody varied upward, flute countermelody, full kit
    20-27  B           relative-minor turn, flute takes the lead
    28-29  Transition  percussion drops; two bells
    30-37  A''         melody thinned, no snare, settling back to loop

Six voices: pluck lead, flute, round bass, bells, kick/snare, hats.
The sequencer wraps note tails past bar 38 to the start: seamless loop.

Editing: everything here is (beat-in-bar, duration, pitch[, velocity])
tuples grouped per bar. Changing the tune touches zero engine code.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track

TEMPO_BPM = 96
BEATS_PER_BAR = 4
TOTAL_BARS = 38
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    """{bar_index: [(beat, dur, pitch[, vel]), ...]} -> absolute Notes."""
    notes = []
    for bar, events in pattern.items():
        for ev in events:
            beat, dur, pitch = ev[0], ev[1], ev[2]
            vel = ev[3] if len(ev) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, dur, pitch, vel))
    return notes


# ---------------------------------------------------------------------------
# Melody phrases (reused with variation — Bible: repetition, varied)
# ---------------------------------------------------------------------------
def _melody_a(start_bar: int, lift: bool, vel: float) -> dict:
    """The main tune. `lift=True` is the A' variation that climbs to D5."""
    peak = "D5" if lift else "C5"
    return {
        start_bar + 0: [(0, 1, "D4", vel), (1, 1, "F#4", vel),
                        (2, 1.5, "A4", vel), (3.5, 0.5, "B4", vel)],
        start_bar + 1: [(0, 2, "A4", vel), (2, 1, "F#4", vel),
                        (3, 1, "E4", vel)],
        start_bar + 2: [(0, 1, "G4", vel), (1, 0.5, "F#4", vel),
                        (1.5, 0.5, "E4", vel), (2, 1, "D4", vel),
                        (3, 1, "E4", vel)],
        start_bar + 3: [(0, 3, "F#4", vel)],  # then a beat of space
        start_bar + 4: [(0, 1, "D4", vel), (1, 1, "F#4", vel),
                        (2, 1.5, "A4", vel), (3.5, 0.5, "B4", vel)],
        start_bar + 5: [(0, 1, "A4", vel), (1, 1, "B4", vel),
                        (2, 1.5, peak, vel), (3.5, 0.5, "A4", vel)],
        start_bar + 6: [(0, 1, "B4", vel), (1, 0.5, "A4", vel),
                        (1.5, 0.5, "G4", vel), (2, 1, "F#4", vel),
                        (3, 1, "E4", vel)],
        start_bar + 7: [(0, 4, "D4", vel)],
    }


def _melody_b(start_bar: int, vel: float) -> dict:
    """The B section tune (flute): the minor turn, looking out to sea."""
    return {
        start_bar + 0: [(0, 1.5, "B4", vel), (1.5, 0.5, "A4", vel),
                        (2, 2, "F#4", vel)],
        start_bar + 1: [(0, 1, "G4", vel), (1, 1, "A4", vel),
                        (2, 2, "B4", vel)],
        start_bar + 2: [(0, 1.5, "A4", vel), (1.5, 0.5, "G4", vel),
                        (2, 1, "F#4", vel), (3, 1, "E4", vel)],
        start_bar + 3: [(0, 4, "F#4", vel)],
        start_bar + 4: [(0, 1.5, "B4", vel), (1.5, 0.5, "C5", vel),
                        (2, 2, "D5", vel)],
        start_bar + 5: [(0, 1, "C5", vel), (1, 1, "B4", vel),
                        (2, 2, "A4", vel)],
        start_bar + 6: [(0, 1, "G4", vel), (1, 1, "F#4", vel),
                        (2, 1, "E4", vel), (3, 1, "C4", vel)],
        start_bar + 7: [(0, 3, "D4", vel)],
    }


def _counter_flute(start_bar: int) -> dict:
    """Long tones under A': a second pair of eyes on the harbor."""
    tones = ["A4", "G4", "B4", "A4", "F#4", "G4", "A4", "F#4"]
    return {start_bar + i: [(0.5, 3.0, t, 0.5)] for i, t in enumerate(tones)}


# ---------------------------------------------------------------------------
# Accompaniment
# ---------------------------------------------------------------------------
_A_ROOTS = ["D2", "C2", "G2", "D2", "D2", "C2", "G2", "D2"]
_A_FIFTHS = ["A2", "G2", "D3", "A2", "A2", "G2", "D3", "A2"]
_B_ROOTS = ["B1", "G2", "D2", "A2", "B1", "G2", "D2", "A2"]
_B_FIFTHS = ["F#2", "D3", "A2", "E3", "F#2", "D3", "A2", "E3"]


def _bass_bars(start_bar: int, roots, fifths, busy: bool) -> dict:
    out = {}
    for i, (root, fifth) in enumerate(zip(roots, fifths)):
        if busy:
            out[start_bar + i] = [(0, 1.5, root), (1.5, 0.5, root, 0.7),
                                  (2, 1, fifth, 0.85), (3, 1, root, 0.9)]
        else:
            out[start_bar + i] = [(0, 2, root), (2, 2, fifth, 0.8)]
    return out


def _kit(start_bar: int, bars: int, with_snare: bool
         ) -> tuple[dict, dict, dict]:
    """Returns (kicks, snares, hats) bar patterns for a section."""
    kicks, snares, hats = {}, {}, {}
    for i in range(bars):
        b = start_bar + i
        kicks[b] = [(0, 0.2, "C2"), (2.5, 0.2, "C2", 0.8)]
        if with_snare:
            snares[b] = [(2, 0.2, "C3", 0.9)]
        hats[b] = [(bt, 0.1, "C5", 0.6 if bt % 1 else 0.9)
                   for bt in (0.5, 1, 1.5, 3, 3.5)]
    return kicks, snares, hats


def _merge(*patterns: dict) -> dict:
    out: dict = {}
    for p in patterns:
        for bar, events in p.items():
            out.setdefault(bar, []).extend(events)
    return out


# ---------------------------------------------------------------------------
# The song
# ---------------------------------------------------------------------------
def build_tracks() -> list[Track]:
    lead = _merge(
        _melody_a(4, lift=False, vel=1.0),
        _melody_a(12, lift=True, vel=1.0),
        # B section: pluck steps back to a gentle arpeggio figure.
        {20 + i: [(0, 0.5, r, 0.45), (1, 0.5, f, 0.4), (2, 0.5, r, 0.45),
                  (3, 0.5, f, 0.4)]
         for i, (r, f) in enumerate(zip(
             ["B3", "G3", "D4", "A3"] * 2, ["F#4", "D4", "F#4", "E4"] * 2))},
        _melody_a(30, lift=False, vel=0.8),
    )
    flute_part = _merge(
        _counter_flute(12),
        _melody_b(20, vel=1.0),
        # Transition: one long farewell tone.
        {28: [(0, 4, "A4", 0.6)], 29: [(0, 3, "F#4", 0.5)]},
    )
    bass = _merge(
        _bass_bars(0, _A_ROOTS[:4], _A_FIFTHS[:4], busy=False),   # intro
        _bass_bars(4, _A_ROOTS, _A_FIFTHS, busy=False),
        _bass_bars(12, _A_ROOTS, _A_FIFTHS, busy=True),
        _bass_bars(20, _B_ROOTS, _B_FIFTHS, busy=True),
        _bass_bars(28, ["G2", "A2"], ["D3", "E3"], busy=False),
        _bass_bars(30, _A_ROOTS, _A_FIFTHS, busy=False),
    )
    bells = _merge(
        {0: [(0, 4, "D5", 0.8)], 1: [(0, 4, "A4", 0.7)],
         2: [(0, 4, "B4", 0.7)], 3: [(0, 4, "F#4", 0.8)]},
        {12: [(0, 2, "D5", 0.6)], 20: [(0, 2, "B4", 0.6)],
         28: [(0, 2, "G5", 0.7)], 29: [(2, 2, "F#5", 0.6)],
         30: [(0, 2, "D5", 0.5)]},
    )
    kicks_a, snares_a, hats_a = _kit(8, 4, with_snare=False)   # eases in
    kicks_b, snares_b, hats_b = _kit(12, 8, with_snare=True)   # full kit
    kicks_c, snares_c, hats_c = _kit(20, 8, with_snare=True)
    kicks_d, snares_d, hats_d = _kit(30, 8, with_snare=False)  # settling

    return [
        Track("lead", ins.pluck_lead, 1.0, _bars(lead)),
        Track("flute", ins.flute, 1.0, _bars(flute_part)),
        Track("bass", ins.round_bass, 1.0, _bars(bass)),
        Track("bells", ins.bell, 1.0, _bars(bells)),
        Track("kick", ins.kick, 1.0,
              _bars(_merge(kicks_a, kicks_b, kicks_c, kicks_d))),
        Track("snare", ins.snare, 1.0,
              _bars(_merge(snares_b, snares_c))),
        Track("hats", ins.hat, 1.0,
              _bars(_merge(hats_a, hats_b, hats_c, hats_d))),
    ]

