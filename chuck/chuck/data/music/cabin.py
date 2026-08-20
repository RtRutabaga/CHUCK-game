"""Cabin theme -- warm wood, colored lights, and a crooked familiar groove.

An original ~92-second loop in D Dorian at 104 BPM. A two-bar elastic bass
figure is the track's identity: steady enough to feel welcoming, syncopated
enough to keep the strange clearing alive. Wooden mallets state a compact
eight-bar tune while a breathy reed answers only in the middle sections.
Tuned high and low hand drums add an Indian-inspired organic/electronic color
without quoting a traditional rhythm or composition.

Structure (40 bars of 4/4):
    0-3    Porch lights   bass hook, soft mallet fragment, hand drums
    4-11   A              full memorable cabin theme
    12-19  A'             theme variation with sparse reed answers
    20-27  B              subtly uncanny Dorian turn, still consonant
    28-31  Firelight      arrangement thins to bass, pad, and hand drums
    32-39  A return       clear full hook, folding back into the opening

The exterior and interior both request this same cue, so ordinary door
transitions do not restart it.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 104
BEATS_PER_BAR = 4
TOTAL_BARS = 40
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.76


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


_ROOTS = (
    "D2", "D2", "C2", "G2", "D2", "D2", "C2", "A1",
    "D2", "D2", "C2", "G2", "D2", "B1", "C2", "A1",
    "G2", "G2", "C2", "D2", "B1", "C2", "G2", "A1",
    "D2", "D2", "C2", "G2",
    "D2", "C2", "G2", "A1",
    "D2", "D2", "C2", "G2", "D2", "D2", "C2", "A1",
)

_FIFTH = {
    "D2": "A2", "C2": "G2", "G2": "D3", "A1": "E2", "B1": "F#2",
}
_OCTAVE = {
    "D2": "D3", "C2": "C3", "G2": "G3", "A1": "A2", "B1": "B2",
}
_PAD = {
    "D2": ("D3", "A3"), "C2": ("C3", "G3"),
    "G2": ("G3", "D4"), "A1": ("A2", "E3"),
    "B1": ("B2", "F#3"),
}


_HOOK_A = (
    ((0, .48, "D4"), (.75, .34, "F4"), (1.5, .48, "G4"),
     (2.25, .72, "A4"), (3.25, .42, "F4")),
    ((0, .70, "E4"), (1, .42, "D4"), (1.75, .42, "C4"),
     (2.5, 1.15, "D4")),
    ((0, .42, "F4"), (.5, .42, "G4"), (1.25, .55, "B4"),
     (2.25, .50, "A4"), (3, .70, "G4")),
    ((0, 1.35, "E4"), (1.75, .48, "G4"), (2.5, 1.10, "D4")),
    ((0, .48, "D4"), (.75, .34, "F4"), (1.5, .48, "G4"),
     (2.25, .72, "A4"), (3.25, .42, "F4")),
    ((0, .70, "E4"), (1, .42, "D4"), (1.75, .42, "C4"),
     (2.5, 1.15, "D4")),
    ((0, .45, "A4"), (.75, .45, "B4"), (1.5, .55, "G4"),
     (2.5, .45, "E4"), (3.25, .55, "C4")),
    ((0, .72, "E4"), (1, .45, "C4"), (1.75, 1.95, "D4")),
)

_HOOK_B = (
    ((0, .65, "G4"), (1, .40, "B4"), (1.75, .75, "D5"),
     (3, .55, "B4")),
    ((0, .70, "A4"), (1, .45, "G4"), (2, 1.35, "E4")),
    ((0, .45, "C5"), (.75, .45, "B4"), (1.5, .70, "G4"),
     (2.75, .75, "F4")),
    ((0, 1.25, "E4"), (1.75, .45, "G4"), (2.5, 1.20, "A4")),
    ((0, .65, "B4"), (1, .40, "A4"), (1.75, .75, "G4"),
     (3, .55, "E4")),
    ((0, .70, "F4"), (1, .45, "E4"), (2, 1.35, "D4")),
    ((0, .45, "G4"), (.75, .45, "A4"), (1.5, .70, "B4"),
     (2.75, .75, "C5")),
    ((0, .75, "A4"), (1, .45, "E4"), (2, 1.75, "D4")),
)


def _melody(start_bar: int, phrase, velocity: float) -> dict:
    return {
        start_bar + index: [
            (beat, duration, pitch, velocity)
            for beat, duration, pitch in events
        ]
        for index, events in enumerate(phrase)
    }


def _bass_bar(root: str, quiet: bool = False) -> list[tuple]:
    level = .68 if quiet else 1.0
    return [
        (0, .55, root, .92 * level),
        (.75, .24, _OCTAVE[root], .62 * level),
        (1.375, .36, _FIFTH[root], .78 * level),
        (2.125, .24, root, .56 * level),
        (2.625, .48, _OCTAVE[root], .88 * level),
        (3.5, .34, _FIFTH[root], .70 * level),
    ]


def build_tracks() -> list[Track]:
    mallet = _merge(
        _melody(0, _HOOK_A[:4], .48),
        _melody(4, _HOOK_A, .92),
        _melody(12, _HOOK_A, .82),
        _melody(20, _HOOK_B, .82),
        _melody(32, _HOOK_A, .96),
    )
    # Reed answers occur only between statements. It never competes with the
    # final peak, preserving the bass and mallet hook as the clear foreground.
    reed = {
        13: [(2.5, 1.1, "A4", .42)], 15: [(2.5, 1.1, "E4", .38)],
        17: [(2.5, 1.1, "B4", .42)], 19: [(2.5, 1.1, "G4", .38)],
        21: [(2.75, .9, "D5", .40)], 23: [(2.5, 1.1, "A4", .38)],
        25: [(2.75, .9, "G4", .40)], 27: [(2.5, 1.1, "E4", .38)],
    }

    bass = {
        bar: _bass_bar(root, 28 <= bar < 32)
        for bar, root in enumerate(_ROOTS)
    }
    pad = {
        bar: [(0, 3.85, _PAD[root][0], .34),
              (0, 3.85, _PAD[root][1], .22)]
        for bar, root in enumerate(_ROOTS)
    }
    colored_lights = {
        bar: [(2.5, 1.35, pitch, .25)]
        for bar, pitch in (
            (3, "A5"), (7, "D6"), (11, "B5"), (15, "G5"),
            (19, "E6"), (23, "C6"), (27, "B5"), (31, "A5"),
            (35, "D6"), (39, "A5"),
        )
    }
    swells = {
        bar: [(0, 3.75, pitch, .24)]
        for bar, pitch in (
            (10, "D5"), (18, "G4"), (22, "B4"), (26, "C5"),
            (29, "A4"), (30, "G4"), (38, "D5"),
        )
    }

    kick, hats, dayan, bayan, wood = {}, {}, {}, {}, {}
    for bar in range(TOTAL_BARS):
        hush = 28 <= bar < 32
        if not hush:
            kick[bar] = [(0, .10, "C2", .66), (2.5, .10, "C2", .48)]
            hats[bar] = [
                (beat, .04, "C6", .22 if beat % 1 else .30)
                for beat in (0, .5, 1, 1.5, 2, 2.5, 3, 3.5)
            ]
        else:
            hats[bar] = [(.5, .04, "C6", .16), (2.5, .04, "C6", .18)]
        # Original 3+3+2-derived hand-drum conversation. The voices alternate
        # rather than stacking every stroke, keeping the groove nimble.
        dayan[bar] = [
            (.375, .12, "D4", .62), (1.125, .12, "A3", .50),
            (2.0, .12, "F4", .58), (3.25, .12, "A3", .54),
        ]
        bayan[bar] = [
            (0, .20, "D2", .72 if not hush else .52),
            (1.75, .18, "C2", .48), (3.0, .20, "D2", .62),
        ]
        wood[bar] = [(1.5, .05, "D6", .30), (3.75, .05, "A5", .26)]

    return [
        Track("mallet_hook", ins.enchanted_mallet, .84, _bars(mallet)),
        Track("reed_answers", ins.breathy_reed, .46, _bars(reed)),
        Track("driving_bass", ins.elastic_bass, 1.10, _bars(bass)),
        Track("warm_room", ins.cloud_pad, .52, _bars(pad)),
        Track("colored_lights", ins.bell, .34, _bars(colored_lights)),
        Track("strange_swells", ins.reverse_bell, .30, _bars(swells)),
        Track("kick", ins.kick, .62, _bars(kick)),
        Track("dayan", ins.tabla_dayan, .76, _bars(dayan)),
        Track("bayan", ins.tabla_bayan, .78, _bars(bayan)),
        Track("wood", ins.woodblock, .48, _bars(wood)),
        Track("hats", ins.hat, .34, _bars(hats)),
    ]
