"""Zephyros conversation theme -- kindly impossible wisdom.

An original ~111-second G-major loop at 78 BPM. A warm reed carries a patient,
memorable theme over soft mallets and a gently walking round bass. Occasional
Mixolydian F-natural turns keep Zephyros whimsical rather than saintly, while
low cloud pads, restrained plucks, tiny bells, and dry wooden ticks make the
conversation feel intimate despite the speaker filling almost the whole frame.

Structure (36 bars of 4/4):
    0-3    Greeting       mallet fragments, bass, and a warm held room
    4-11   A              Zephyros' full reed theme
    12-19  A'             mallet restatement with short reed answers
    20-27  B              a gentle minor question, never an ominous turn
    28-35  A return       the reed theme settles back into the greeting
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 78
BEATS_PER_BAR = 4
TOTAL_BARS = 36
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.62


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


_THEME = (
    ((0, 1.5, "G4"), (1.5, .5, "B4"), (2, 1, "D5"), (3, 1, "B4")),
    ((0, 1, "A4"), (1, .5, "B4"), (1.5, .5, "C5"), (2, 2, "B4")),
    ((0, 1, "E4"), (1, 1, "G4"), (2, .75, "B4"),
     (2.75, .75, "A4"), (3.5, .5, "G4")),
    ((0, 3.25, "D4"),),
    ((0, .75, "G4"), (.75, .75, "A4"), (1.5, 1, "B4"),
     (2.5, 1, "D5"), (3.5, .5, "C5")),
    ((0, 1.5, "B4"), (1.5, .5, "A4"), (2, 2, "G4")),
    ((0, 1, "F4"), (1, .5, "G4"), (1.5, .5, "A4"),
     (2, 1, "C5"), (3, 1, "B4")),
    ((0, 3.5, "G4"),),
)

_QUESTION = (
    ((0, 2, "E4"), (2.5, 1.5, "G4")),
    ((0, 1, "A4"), (1.5, 1, "B4"), (3, 1, "C5")),
    ((0, 2, "B4"), (2.5, 1.5, "G4")),
    ((0, 3.5, "E4"),),
    ((0, 1.5, "C5"), (1.5, .5, "B4"), (2, 2, "A4")),
    ((0, 1, "F4"), (1.5, 1, "A4"), (3, 1, "C5")),
    ((0, 1.5, "B4"), (2, 1, "A4"), (3, 1, "F4")),
    ((0, 3.5, "G4"),),
)


def _melody(start_bar: int, phrase, velocity: float) -> dict:
    return {
        start_bar + index: [
            (beat, duration, pitch, velocity)
            for beat, duration, pitch in events
        ]
        for index, events in enumerate(phrase)
    }


_ROOTS = (
    "G2", "C2", "E2", "D2",
    "G2", "C2", "E2", "D2", "G2", "C2", "A1", "D2",
    "G2", "C2", "E2", "D2", "G2", "C2", "A1", "D2",
    "E2", "C2", "G2", "E2", "C2", "A1", "D2", "D2",
    "G2", "C2", "E2", "D2", "G2", "C2", "A1", "D2",
)

_FIFTH = {
    "G2": "D3", "C2": "G2", "E2": "B2", "D2": "A2", "A1": "E2",
}
_CHORD = {
    "G2": ("G3", "B3", "D4"),
    "C2": ("C3", "E3", "G3"),
    "E2": ("E3", "G3", "B3"),
    "D2": ("D3", "F#3", "A3"),
    "A1": ("A2", "C3", "E3"),
}


def build_tracks() -> list[Track]:
    reed = _merge(
        {0: [(0, 2, "G4", .34)], 2: [(2, 1.5, "D5", .30)]},
        _melody(4, _THEME, .80),
        {
            13: [(2.5, 1, "D5", .34)], 15: [(2.5, 1, "B4", .32)],
            17: [(2.5, 1, "C5", .34)], 19: [(2.5, 1, "A4", .32)],
        },
        _melody(20, _QUESTION, .62),
        _melody(28, _THEME, .76),
    )
    mallet = _merge(
        {
            0: [(0, 1, "G4", .46), (2, 1, "D5", .34)],
            1: [(1, 1, "E5", .38)],
            2: [(0, 1, "B4", .42)],
            3: [(2, 1.5, "A4", .36)],
        },
        _melody(12, _THEME, .56),
    )

    bass = {}
    pad = {}
    plucks = {}
    for bar, root in enumerate(_ROOTS):
        bass[bar] = [
            (0, 1.7, root, .58),
            (2.25, .65, _FIFTH[root], .35),
            (3.25, .6, root, .40),
        ]
        chord = _CHORD[root]
        pad[bar] = [
            (0, 4, chord[0], .54),
            (0, 4, chord[2], .34),
        ]
        # A relaxed 3+3+2 sway makes the giant lightly whimsical.
        plucks[bar] = [
            (0, .42, chord[0], .32),
            (1.5, .42, chord[1], .25),
            (3, .42, chord[2], .28),
        ]

    bells = {
        3: [(3, 1, "G5", .28)], 7: [(2.5, 1.5, "D6", .30)],
        11: [(3, 1, "B5", .28)], 15: [(2, 2, "E6", .28)],
        19: [(3, 1, "C6", .28)], 23: [(2, 2, "G5", .26)],
        27: [(3, 1, "A5", .28)], 31: [(2.5, 1.5, "D6", .30)],
        35: [(2, 2, "G5", .28)],
    }
    swells = {
        bar: [(0, 3.75, pitch, velocity)]
        for bar, pitch, velocity in (
            (10, "G4", .24), (18, "C5", .24),
            (22, "E5", .28), (26, "D5", .26), (34, "G4", .24),
        )
    }
    wood = {
        bar: [(.75, .06, "G5", .20), (3.25, .06, "D5", .17)]
        for bar in range(TOTAL_BARS) if bar % 2 == 0
    }

    return [
        Track("warm_reed", ins.breathy_reed, .84, _bars(reed)),
        Track("mallet", ins.enchanted_mallet, .54, _bars(mallet)),
        Track("round_bass", ins.round_bass, .72, _bars(bass)),
        Track("room_pad", ins.cloud_pad, .82, _bars(pad)),
        Track("gentle_plucks", ins.pluck_lead, .34, _bars(plucks)),
        Track("small_bells", ins.bell, .40, _bars(bells)),
        Track("soft_swells", ins.reverse_bell, .36, _bars(swells)),
        Track("wood_ticks", ins.woodblock, .30, _bars(wood)),
    ]
