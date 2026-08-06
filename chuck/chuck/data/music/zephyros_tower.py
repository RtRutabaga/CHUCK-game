"""Cloud Staircase / Zephyros tower theme -- open, ancient wonder.

An original ~105-second C-Lydian loop at 82 BPM. Open fifths and the raised
fourth (F#) give the tower a sense of impossible height without making it
ominous. A patient eight-bar flute theme returns after a quieter high-altitude
middle passage; glassy mallets, sparse bells, reverse swells, and a broad
cloud-pad ensemble leave generous air around the melody.

Structure (36 bars of 4/4):
    0-3    Horizon       cloud pads, high bells, fragments of the motif
    4-11   A             the complete ascending flute theme
    12-19  A'            mallet lead with gentle reed answers
    20-27  High chamber  thinner, older, suspended above the clouds
    28-35  A return      flute theme returns and opens into the loop
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 82
BEATS_PER_BAR = 4
TOTAL_BARS = 36
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
# Sustained pads carry far more average energy than the transient-heavy
# Feywild mix. This ceiling keeps perceived loudness level while preserving
# the intended open air around the melody.
MASTER_HEADROOM = 0.60


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
    ((0, 1.5, "C5"), (1.5, .5, "E5"), (2, 1.5, "G5"), (3.5, .5, "F#5")),
    ((0, 2, "D5"), (2, 1, "G5"), (3, 1, "E5")),
    ((0, 1, "C5"), (1, .5, "D5"), (1.5, .5, "E5"), (2, 2, "G5")),
    ((0, 1.5, "F#5"), (1.5, .5, "E5"), (2, 2, "D5")),
    ((0, 1, "A4"), (1, 1, "C5"), (2, 1, "E5"), (3, 1, "D5")),
    ((0, 2, "G4"), (2, 1, "B4"), (3, 1, "D5")),
    ((0, .75, "F#5"), (.75, .75, "G5"), (1.5, 1, "B5"),
     (2.5, 1, "A5"), (3.5, .5, "F#5")),
    ((0, 3.5, "G5"),),
)

_CHAMBER = (
    ((0, 2.5, "E5"), (3, 1, "B4")),
    ((0, 1.5, "D5"), (2, 2, "A4")),
    ((0, 1, "C5"), (1.5, 1, "F#5"), (3, 1, "E5")),
    ((0, 3.5, "D5"),),
    ((0, 2, "A4"), (2.5, 1.5, "C5")),
    ((0, 1.5, "B4"), (2, 2, "D5")),
    ((0, 1, "F#5"), (1.5, 1, "E5"), (3, 1, "D5")),
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
    "C2", "G1", "D2", "C2", "A1", "G1", "D2", "G1",
    "C2", "G1", "D2", "C2", "A1", "G1", "D2", "G1",
    "E2", "D2", "C2", "D2", "A1", "G1", "D2", "G1",
    "C2", "G1", "D2", "C2", "A1", "G1", "D2", "G1",
    "C2", "D2", "G1", "G1",
)

_FIFTH = {
    "C2": "G2", "G1": "D2", "D2": "A2", "A1": "E2", "E2": "B2",
}
_PAD = {
    "C2": ("C3", "G3", "E4"),
    "G1": ("G2", "D3", "B3"),
    "D2": ("D3", "A3", "F#4"),
    "A1": ("A2", "E3", "C4"),
    "E2": ("E3", "B3", "G4"),
}


def build_tracks() -> list[Track]:
    flute = _merge(
        {0: [(0, 2, "C5", .40)], 2: [(2, 1.5, "G5", .38)]},
        _melody(4, _THEME, .88),
        _melody(28, _THEME, .82),
    )
    mallet = _merge(
        _melody(12, _THEME, .70),
        {
            1: [(1, .8, "E5", .35)], 3: [(2.5, .8, "F#5", .34)],
            20: [(0, 1.2, "E5", .40)], 22: [(1.5, 1.2, "F#5", .42)],
            24: [(0, 1.2, "A4", .38)], 26: [(2, 1.2, "D5", .40)],
        },
    )
    reed = _merge(
        {
            13: [(2.5, 1.2, "B4", .38)],
            15: [(2.5, 1.2, "A4", .36)],
            17: [(2.5, 1.2, "E5", .38)],
            19: [(2.5, 1.2, "D5", .36)],
        },
        _melody(20, _CHAMBER, .46),
    )

    arpeggio = {}
    for bar, root in enumerate(_ROOTS):
        chord = _PAD[root]
        events = []
        order = (0, 1, 2, 1)
        for beat, chord_index in enumerate(order):
            velocity = .38 if beat in {0, 2} else .28
            if 20 <= bar < 28:
                velocity *= .65
            events.append((beat, .72, chord[chord_index], velocity))
        arpeggio[bar] = events

    bass = {
        bar: [
            (0, 2.8, root, .58),
            (3, .8, _FIFTH[root], .33),
        ]
        for bar, root in enumerate(_ROOTS)
    }
    pads = {}
    for bar, root in enumerate(_ROOTS):
        # Two open voices per bar; the third belongs to the lighter arpeggio.
        pads[bar] = [
            (0, 4, _PAD[root][0], .68),
            (0, 4, _PAD[root][1], .48),
        ]

    bells = {
        0: [(0, 3.5, "C6", .42)], 3: [(3, 1, "G5", .34)],
        7: [(2.5, 1.5, "D6", .38)], 11: [(3, 1, "F#6", .36)],
        15: [(2, 2, "E6", .35)], 19: [(3, 1, "B5", .34)],
        23: [(2, 2, "F#5", .32)], 27: [(3, 1, "D6", .36)],
        31: [(2.5, 1.5, "E6", .38)], 35: [(2, 2, "G5", .36)],
    }
    swells = {
        bar: [(0, 3.75, pitch, velocity)]
        for bar, pitch, velocity in (
            (2, "G5", .35), (10, "D5", .32), (18, "F#5", .34),
            (20, "E5", .40), (24, "C5", .40), (26, "D5", .38),
            (34, "G5", .34),
        )
    }
    ceremonial = {
        bar: [(0, .08, "C5", .28), (2.5, .06, "G5", .20)]
        for bar in range(TOTAL_BARS)
        if not 20 <= bar < 28 or bar % 2 == 0
    }

    return [
        Track("flute", ins.flute, .88, _bars(flute)),
        Track("mallet", ins.enchanted_mallet, .58, _bars(mallet)),
        Track("reed", ins.breathy_reed, .48, _bars(reed)),
        Track("arpeggio", ins.bell, .44, _bars(arpeggio)),
        Track("cloud_pad", ins.cloud_pad, 1.05, _bars(pads)),
        Track("open_bass", ins.round_bass, .72, _bars(bass)),
        Track("high_bells", ins.bell, .52, _bars(bells)),
        Track("swells", ins.reverse_bell, .50, _bars(swells)),
        Track("ceremonial", ins.woodblock, .38, _bars(ceremonial)),
    ]
