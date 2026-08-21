"""Cabin theme -- an insistent bassline under cool nocturnal electronics.

An original ~103-second loop in D Dorian at 112 BPM. A syncopated, chord-tone
elastic bass figure remains the track's identity, while the former
Feywild-like mallets, reed, bells, and magical swells have been replaced by a
four-on-the-floor pulse, rounded arpeggios, and a warm neon synth melody.
Sparse tabla accents retain the Cabin phase's requested hand-drum color
without pulling the arrangement away from its driving electronic character.
Occasional jaw-harp twangs answer the bass on open offbeats.

The exterior and interior request this same cue, so ordinary door transitions
do not restart it.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 112
BEATS_PER_BAR = 4
TOTAL_BARS = 48
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.72


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for event in events:
            beat, duration, pitch = event[:3]
            velocity = event[3] if len(event) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, duration, pitch,
                              velocity))
    return notes


_ROOT_CYCLE = (
    "D2", "D2", "C2", "G2", "D2", "D2", "C2", "A1",
    "D2", "D2", "C2", "G2", "D2", "B1", "C2", "A1",
    "G2", "G2", "C2", "D2", "B1", "C2", "G2", "A1",
    "D2", "D2", "C2", "G2", "D2", "C2", "G2", "A1",
)
_ROOTS = _ROOT_CYCLE + _ROOT_CYCLE[:16]
_FIFTH = {
    "D2": "A2", "C2": "G2", "G2": "D3", "A1": "E2", "B1": "F#2",
}
_OCTAVE = {
    "D2": "D3", "C2": "C3", "G2": "G3", "A1": "A2", "B1": "B2",
}
_THIRD = {
    "D2": "F2", "C2": "E2", "G2": "B2", "A1": "C2", "B1": "D2",
}
_SEVENTH = {
    "D2": "C3", "C2": "B2", "G2": "F3", "A1": "G2", "B1": "A2",
}
_ARP = {
    "D2": ("D4", "A4", "C5", "E5"),
    "C2": ("C4", "G4", "B4", "D5"),
    "G2": ("G3", "D4", "A4", "B4"),
    "A1": ("A3", "E4", "G4", "C5"),
    "B1": ("B3", "F#4", "A4", "D5"),
}


_HOOK_A = (
    ((0, .34, "D5"), (.5, .34, "F5"), (1, .70, "A5"),
     (2, .34, "G5"), (2.5, .34, "F5"), (3, .72, "D5")),
    ((0, .34, "C5"), (.5, .34, "D5"), (1, .70, "F5"),
     (2, .34, "E5"), (2.5, .34, "D5"), (3, .72, "C5")),
    ((0, .34, "G4"), (.5, .34, "B4"), (1, .70, "D5"),
     (2, .34, "E5"), (2.5, .34, "G5"), (3, .72, "A5")),
    ((0, .48, "E5"), (.75, .48, "C5"), (1.5, .48, "A4"),
     (2.25, 1.34, "D5")),
    ((0, .34, "D5"), (.5, .34, "F5"), (1, .70, "A5"),
     (2, .34, "C6"), (2.5, .34, "A5"), (3, .72, "G5")),
    ((0, .34, "E5"), (.5, .34, "G5"), (1, .70, "B5"),
     (2, .34, "A5"), (2.5, .34, "G5"), (3, .72, "E5")),
    ((0, .34, "C5"), (.5, .34, "E5"), (1, .70, "G5"),
     (2, .34, "A5"), (2.5, .34, "C6"), (3, .72, "B5")),
    ((0, .48, "A5"), (.75, .48, "E5"), (1.5, .48, "C5"),
     (2.25, 1.34, "D5")),
)

_HOOK_B = (
    ((0, .34, "G5"), (.5, .34, "A5"), (1, .70, "B5"),
     (2, .34, "D6"), (2.5, .34, "B5"), (3, .72, "A5")),
    ((0, .34, "F5"), (.5, .34, "G5"), (1, .70, "A5"),
     (2, .34, "C6"), (2.5, .34, "A5"), (3, .72, "G5")),
    ((0, .34, "E5"), (.5, .34, "G5"), (1, .70, "B5"),
     (2, .34, "A5"), (2.5, .34, "G5"), (3, .72, "E5")),
    ((0, .48, "F5"), (.75, .48, "E5"), (1.5, .48, "C5"),
     (2.25, 1.34, "D5")),
    ((0, .34, "B5"), (.5, .34, "A5"), (1, .70, "G5"),
     (2, .34, "E5"), (2.5, .34, "G5"), (3, .72, "A5")),
    ((0, .34, "C6"), (.5, .34, "A5"), (1, .70, "G5"),
     (2, .34, "E5"), (2.5, .34, "D5"), (3, .72, "C5")),
    ((0, .34, "G5"), (.5, .34, "A5"), (1, .70, "B5"),
     (2, .34, "D6"), (2.5, .34, "C6"), (3, .72, "A5")),
    ((0, .48, "E5"), (.75, .48, "C5"), (1.5, .48, "A4"),
     (2.25, 1.34, "D5")),
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
    """A syncopated funk figure that walks through each chord's color tones."""
    level = .68 if quiet else 1.0
    return [
        (0, .42, root, .90 * level),
        (.625, .18, _OCTAVE[root], .52 * level),
        (1, .28, _FIFTH[root], .68 * level),
        (1.5, .30, _THIRD[root], .76 * level),
        (2.125, .22, root, .52 * level),
        (2.5, .36, _SEVENTH[root], .82 * level),
        (3.125, .22, _FIFTH[root], .60 * level),
        (3.5, .38, _OCTAVE[root], .86 * level),
    ]


def build_tracks() -> list[Track]:
    synth_hook = {}
    for start, phrase, velocity in (
        (4, _HOOK_A, .88), (12, _HOOK_A, .92), (20, _HOOK_B, .92),
        (32, _HOOK_A, .98), (40, _HOOK_B, 1.0),
    ):
        synth_hook.update(_melody(start, phrase, velocity))

    bass = {
        bar: _bass_bar(root, 28 <= bar < 32)
        for bar, root in enumerate(_ROOTS)
    }
    arp = {}
    low_pulse = {}
    kick, snare, hats, dayan, bayan, jaw_harp = {}, {}, {}, {}, {}, {}
    for bar, root in enumerate(_ROOTS):
        break_bar = 28 <= bar < 32
        full_drive = 8 <= bar < 28 or bar >= 32
        chord = _ARP[root]
        arp[bar] = [
            (step * .5 + .25, .18, chord[step % 4],
             .54 if full_drive else .38)
            for step in range(8)
        ]
        low_pulse[bar] = [
            (.5, .20, chord[0], .34), (1.5, .20, chord[1], .30),
            (2.5, .20, chord[2], .34), (3.5, .20, chord[1], .30),
        ]
        kick[bar] = [
            (beat, .10, "C2", .78 if not break_bar else .58)
            for beat in (0, 1, 2, 3)
        ]
        snare[bar] = [(1, .08, "D3", .56), (3, .08, "D3", .60)]
        hats[bar] = [
            (beat, .04, "C6", .18 if beat % 1 else .10)
            for beat in (0, .5, 1, 1.5, 2, 2.5, 3, 3.5)
        ]
        # Sparse hand-drum color woven between the mechanical backbeat.
        dayan[bar] = [(.75, .10, "D4", .38), (2.75, .10, "A3", .34)]
        bayan[bar] = [(3.5, .16, "D2", .36 if not break_bar else .28)]
        # One compact twang every other active bar adds rustic character while
        # leaving the bass and neon hook in control of the groove.
        if bar >= 4 and not break_bar and bar % 2 == 0:
            jaw_harp[bar] = [
                (1.75, .30, _OCTAVE[root], .60),
                (3.75, .24, _FIFTH[root], .44),
            ]

    return [
        Track("synth_hook", ins.neon_synth_lead, .90, _bars(synth_hook)),
        Track("driving_bass", ins.elastic_bass, 1.10, _bars(bass)),
        Track("pulse_arp", ins.pulse_arp, .62, _bars(arp)),
        Track("low_pulse", ins.pulse_arp, .42, _bars(low_pulse)),
        Track("kick", ins.kick, .72, _bars(kick)),
        Track("snare", ins.snare, .44, _bars(snare)),
        Track("hats", ins.hat, .28, _bars(hats)),
        Track("dayan", ins.tabla_dayan, .48, _bars(dayan)),
        Track("bayan", ins.tabla_bayan, .50, _bars(bayan)),
        Track("jaw_harp", ins.jaw_harp, .56, _bars(jaw_harp)),
    ]
