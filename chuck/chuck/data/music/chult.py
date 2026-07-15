"""Chult jungle exploration theme -- bass-forward, humid, and propulsive.

Original piece, ~86 seconds per cycle. D Dorian at 112 BPM gives the jungle a
confident minor groove while the raised sixth (B natural) keeps it alive rather
than grim. A two-bar syncopated bass hook remains the identity of every section;
pitched hand drums, woody offbeats, and hats layer around it without imitating
real-world field recordings or any existing game composition.

Structure (bars of 4/4):
    0-3    Groove intro   bass hook + hand percussion arrive immediately
    4-11   A              compact plucked jungle hook
    12-19  A'             hook lifts; flute answers; percussion opens up
    20-27  B              darker canopy turn, bass remains insistent
    28-31  Humid break    melody thins; sub pulse, toms, and bells breathe
    32-39  A''            full hook and layered groove return to the loop

Ten voices: lead, flute, deep bass, sub pulse, bells, kick, snare, hats,
pitched toms, and woodblock. Note tails wrap through the end for a clean loop.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 112
BEATS_PER_BAR = 4
TOTAL_BARS = 40
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR


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


_FIFTH = {
    "D2": "A2", "C2": "G2", "Bb1": "F2", "G1": "D2",
    "A1": "E2", "F2": "C3",
}
_OCTAVE = {
    "D2": "D3", "C2": "C3", "Bb1": "Bb2", "G1": "G2",
    "A1": "A2", "F2": "F3",
}
_A_ROOTS = ["D2", "D2", "C2", "G1", "D2", "D2", "Bb1", "C2"]
_B_ROOTS = ["Bb1", "C2", "D2", "A1", "Bb1", "G1", "A1", "A1"]


def _bass(start_bar: int, roots: list[str], full: bool = True) -> dict:
    """The song's two-bar identity: low roots with syncopated upper answers."""
    out = {}
    for index, root in enumerate(roots):
        fifth, octave = _FIFTH[root], _OCTAVE[root]
        if full:
            shape = [
                (0, 0.62, root, 1.0), (0.75, 0.25, root, 0.68),
                (1.5, 0.42, fifth, 0.82), (2, 0.5, octave, 0.9),
                (2.75, 0.25, root, 0.68), (3, 0.42, fifth, 0.8),
                (3.5, 0.45, octave if index % 2 == 0 else root, 0.82),
            ]
        else:
            shape = [(0, 1.1, root, 0.9), (1.75, 0.25, fifth, 0.65),
                     (2.5, 0.75, root, 0.8), (3.5, 0.4, octave, 0.7)]
        out[start_bar + index] = shape
    return out


def _lead_a(start_bar: int, lift: bool, velocity: float) -> dict:
    peak = "D5" if lift else "C5"
    return {
        start_bar + 0: [(0, 0.5, "D4", velocity), (0.75, 0.5, "F4", velocity),
                        (1.5, 0.5, "G4", velocity), (2.25, 1.25, "A4", velocity)],
        start_bar + 1: [(0, 0.5, "C5", velocity), (0.75, 0.5, "A4", velocity),
                        (1.5, 0.5, "G4", velocity), (2.5, 1.5, "F4", velocity)],
        start_bar + 2: [(0, 0.5, "D4", velocity), (0.75, 0.5, "F4", velocity),
                        (1.5, 0.5, "A4", velocity), (2.25, 0.5, "B4", velocity),
                        (3, 1, peak, velocity)],
        start_bar + 3: [(0, 0.75, "A4", velocity), (1, 0.5, "G4", velocity),
                        (1.75, 0.5, "F4", velocity), (2.5, 1.5, "D4", velocity)],
        start_bar + 4: [(0, 0.5, "D4", velocity), (0.75, 0.5, "G4", velocity),
                        (1.5, 0.5, "A4", velocity), (2.25, 1.25, "C5", velocity)],
        start_bar + 5: [(0, 0.5, "B4", velocity), (0.75, 0.5, "A4", velocity),
                        (1.5, 0.5, "G4", velocity), (2.5, 1.5, "E4", velocity)],
        start_bar + 6: [(0, 0.5, "F4", velocity), (0.75, 0.5, "G4", velocity),
                        (1.5, 0.5, "A4", velocity), (2.5, 1.5, "C5", velocity)],
        start_bar + 7: [(0, 0.75, "B4", velocity), (1, 0.5, "A4", velocity),
                        (1.75, 0.5, "F4", velocity), (2.5, 1.5, "D4", velocity)],
    }


def _lead_b(start_bar: int) -> dict:
    return {
        start_bar + 0: [(0, 1, "F4"), (1.5, 0.5, "G4"), (2.25, 1.75, "Bb4")],
        start_bar + 1: [(0, 0.5, "A4"), (0.75, 0.5, "G4"),
                        (1.5, 0.5, "F4"), (2.5, 1.5, "D4")],
        start_bar + 2: [(0, 1, "C5"), (1.5, 0.5, "A4"), (2.25, 1.75, "G4")],
        start_bar + 3: [(0, 0.5, "E4"), (0.75, 0.5, "F4"),
                        (1.5, 0.5, "G4"), (2.5, 1.5, "A4")],
        start_bar + 4: [(0, 0.75, "Bb4"), (1, 0.5, "A4"),
                        (1.75, 0.5, "G4"), (2.5, 1.5, "F4")],
        start_bar + 5: [(0, 1, "D5"), (1.5, 0.5, "C5"), (2.25, 1.75, "A4")],
        start_bar + 6: [(0, 0.5, "G4"), (0.75, 0.5, "F4"),
                        (1.5, 0.5, "E4"), (2.5, 1.5, "D4")],
        start_bar + 7: [(0, 3, "A4", 0.85)],
    }


def _flute_answers(start_bar: int) -> dict:
    pitches = [("A4", "B4"), ("G4", "A4"), ("F4", "G4"), ("E4", "D4")]
    out = {}
    for index in range(8):
        first, second = pitches[index % 4]
        out[start_bar + index] = [(0.5, 1.25, first, 0.55),
                                  (2.5, 1.25, second, 0.5)]
    return out


def _percussion(start_bar: int, bars: int, dense: bool
                ) -> tuple[dict, dict, dict, dict, dict]:
    kicks, snares, hats, toms, wood = {}, {}, {}, {}, {}
    for index in range(bars):
        bar = start_bar + index
        kicks[bar] = [(0, 0.12, "C2"), (1.75, 0.12, "C2", 0.72),
                      (2.5, 0.12, "C2", 0.9), (3.5, 0.12, "C2", 0.7)]
        snares[bar] = [(1, 0.12, "C3", 0.72), (3, 0.12, "C3", 0.82)]
        hat_beats = (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5) if dense else (
            0.5, 1.5, 2.5, 3.5
        )
        hats[bar] = [(beat, 0.07, "C5", 0.65 if beat % 1 else 0.82)
                     for beat in hat_beats]
        toms[bar] = [(0.75, 0.15, "G2", 0.8), (2.25, 0.15, "D3", 0.72),
                     (3.25, 0.15, "A2", 0.68 if index % 2 else 0.82)]
        wood[bar] = [(0.5, 0.06, "G5", 0.62), (1.5, 0.06, "D5", 0.52),
                     (2.75, 0.06, "A5", 0.62), (3.5, 0.06, "D5", 0.48)]
    return kicks, snares, hats, toms, wood


def build_tracks() -> list[Track]:
    lead = _merge(
        _lead_a(4, lift=False, velocity=0.92),
        _lead_a(12, lift=True, velocity=0.98),
        _lead_b(20),
        _lead_a(32, lift=True, velocity=0.88),
    )
    flute = _merge(
        _flute_answers(12),
        {28: [(0, 4, "A4", 0.42)], 29: [(0, 4, "G4", 0.4)],
         30: [(0, 4, "E4", 0.38)], 31: [(0, 4, "D4", 0.42)]},
        _flute_answers(32),
    )
    bass = _merge(
        _bass(0, _A_ROOTS[:4]), _bass(4, _A_ROOTS),
        _bass(12, _A_ROOTS), _bass(20, _B_ROOTS),
        _bass(28, ["D2", "C2", "Bb1", "A1"], full=False),
        _bass(32, _A_ROOTS),
    )
    sub = {
        bar: [(0, 3.75, root, 0.38)]
        for bar, root in enumerate(
            ["D2", "D2", "C2", "G1"] * 2,
            start=28,
        )
    }
    bells = {
        2: [(2, 2, "D5", 0.38)], 10: [(3, 1, "B4", 0.4)],
        18: [(3, 1, "D5", 0.42)], 24: [(0, 2, "Bb4", 0.38)],
        28: [(0, 3, "D5", 0.42)], 30: [(0, 3, "B4", 0.4)],
        31: [(2, 2, "A4", 0.38)], 39: [(3, 1, "D5", 0.38)],
    }

    sections = [
        _percussion(0, 4, dense=False),
        _percussion(4, 8, dense=False),
        _percussion(12, 8, dense=True),
        _percussion(20, 8, dense=True),
        _percussion(28, 4, dense=False),
        _percussion(32, 8, dense=True),
    ]
    percussion = [
        _merge(*(section[index] for section in sections))
        for index in range(5)
    ]
    kicks, snares, hats, toms, wood = percussion

    return [
        Track("lead", ins.pluck_lead, 0.78, _bars(lead)),
        Track("flute", ins.flute, 0.68, _bars(flute)),
        Track("bass", ins.round_bass, 1.2, _bars(bass)),
        Track("sub", ins.round_bass, 0.52, _bars(sub)),
        Track("bells", ins.bell, 0.55, _bars(bells)),
        Track("kick", ins.kick, 1.0, _bars(kicks)),
        Track("snare", ins.snare, 0.72, _bars(snares)),
        Track("hats", ins.hat, 0.8, _bars(hats)),
        Track("toms", ins.jungle_tom, 1.0, _bars(toms)),
        Track("wood", ins.woodblock, 0.85, _bars(wood)),
    ]
