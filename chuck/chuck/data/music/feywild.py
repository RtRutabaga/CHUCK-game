"""Feywild exploration theme -- catchy, funky, and enchanted.

An original ~99-second loop in F Mixolydian at 116 BPM. The major third keeps
the region warm and inviting, while Eb's flat seventh gives the groove a
playful storybook turn without pushing the harmony too far off balance. A
two-bar elastic-bass figure and a compact four-bar mallet hook are the tune's
durable identity; the hook repeats within each main section so it lands early.

Structure (48 bars of 4/4):
    0-3    Firefly intro   bass hook, mallet fragment, hand percussion
    4-11   A               full memorable mallet theme
    12-19  A'              sparse echo accents, clearer rhythm section
    20-27  B               the hedge turns; B/Eb mystery comes forward
    28-31  Moonlit break   reverse swells, bass and sparse wooden pulse
    32-39  A''             fullest, funkiest return of the main hook
    40-47  C / turnaround  wandering variation folds cleanly into the loop

Twelve voices: enchanted mallet, plucked echo, breathy reed, elastic bass,
sub pulse, bells, reversed bell swells, kick, snare, hand toms, woodblock,
and hats. The arrangement remains rhythmically alive without becoming a
combat cue, and all tails wrap through the loop seam.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 116
BEATS_PER_BAR = 4
TOTAL_BARS = 48
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.92


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for event in events:
            beat, duration, pitch = event[:3]
            velocity = event[3] if len(event) > 3 else 1.0
            notes.append(Note(
                bar * BEATS_PER_BAR + beat, duration, pitch, velocity
            ))
    return notes


def _merge(*patterns: dict) -> dict:
    merged: dict = {}
    for pattern in patterns:
        for bar, events in pattern.items():
            merged.setdefault(bar, []).extend(events)
    return merged


_COMP = {
    "F2": ("C3", "F3"), "Eb2": ("Bb2", "Eb3"),
    "G2": ("D3", "G3"), "C2": ("G2", "C3"),
    "Bb1": ("F2", "Bb2"),
    "D2": ("A2", "D3"),
}
_A_ROOTS = ("F2", "F2", "Eb2", "C2", "F2", "G2", "Eb2", "C2")
_B_ROOTS = ("Bb1", "C2", "D2", "Eb2", "Bb1", "C2", "G2", "C2")
_C_ROOTS = ("G2", "Eb2", "Bb1", "C2", "D2", "Eb2", "C2", "C2")


def _bass(start_bar: int, roots, intensity: str = "groove") -> dict:
    """The elastic two-bar identity: roots bounce into fifths and octaves."""
    out = {}
    for index, root in enumerate(roots):
        fifth, octave = _COMP[root]
        if intensity == "break":
            shape = [
                (0, 0.9, root, 0.82), (1.5, 0.35, fifth, 0.60),
                (2.5, 0.65, octave, 0.72), (3.5, 0.35, fifth, 0.56),
            ]
        else:
            shape = [
                (0, 0.55, root, 1.0),
                (0.75, 0.22, octave, 0.64),
                (1.25, 0.34, fifth, 0.78),
                (1.875, 0.22, root, 0.58),
                (2.25, 0.48, octave, 0.91),
                (3.0, 0.30, fifth, 0.72),
                (3.5, 0.38, octave if index % 2 == 0 else root, 0.82),
            ]
            if intensity == "full":
                shape.append((2.75, 0.18, root, 0.52))
        out[start_bar + index] = shape
    return out


_HOOK_A = (
    ((0, .45, "F4"), (.75, .4, "A4"), (1.5, .4, "Bb4"),
     (2.25, .7, "C5"), (3.25, .45, "A4")),
    ((0, .45, "G4"), (.75, .4, "F4"), (1.5, .4, "Eb4"),
     (2.25, .7, "C4"), (3.25, .45, "F4")),
    ((0, .4, "A4"), (.5, .4, "C5"), (1.25, .4, "D5"),
     (2, .4, "C5"), (2.75, .4, "Bb4"), (3.5, .4, "G4")),
    ((0, 1.15, "F4"), (1.5, .4, "A4"), (2.25, .4, "G4"),
     (3, .85, "F4")),
    ((0, .45, "F4"), (.75, .4, "A4"), (1.5, .4, "Bb4"),
     (2.25, .7, "C5"), (3.25, .45, "A4")),
    ((0, .45, "G4"), (.75, .4, "F4"), (1.5, .4, "Eb4"),
     (2.25, .7, "C4"), (3.25, .45, "F4")),
    ((0, .4, "A4"), (.5, .4, "C5"), (1.25, .4, "D5"),
     (2, .4, "C5"), (2.75, .4, "Bb4"), (3.5, .4, "G4")),
    ((0, .7, "F4"), (1, .4, "A4"), (1.75, .4, "G4"),
     (2.5, 1.25, "F4")),
)

_HOOK_B = (
    ((0, .5, "Bb4"), (.75, .5, "C5"), (1.5, .5, "Eb5"),
     (2.5, 1.2, "D5")),
    ((0, .5, "C5"), (.75, .5, "Bb4"), (1.5, .5, "G4"),
     (2.5, 1.2, "F4")),
    ((0, .4, "D5"), (.5, .4, "Eb5"), (1.25, .4, "D5"),
     (2, .65, "Bb4"), (3, .75, "A4")),
    ((0, 1.2, "G4"), (1.5, .45, "Bb4"), (2.25, 1.5, "Eb5")),
    ((0, .5, "Bb4"), (.75, .5, "C5"), (1.5, .5, "D5"),
     (2.5, 1.2, "F5")),
    ((0, .5, "Eb5"), (.75, .5, "D5"), (1.5, .5, "Bb4"),
     (2.5, 1.2, "G4")),
    ((0, .4, "Bb4"), (.5, .4, "C5"), (1.25, .4, "D5"),
     (2, .65, "Eb5"), (3, .75, "C5")),
    ((0, 1.0, "G4"), (1.5, .5, "Eb4"), (2.5, 1.25, "F4")),
)

_HOOK_C = (
    ((0, .45, "G4"), (.75, .4, "Bb4"), (1.5, .4, "D5"),
     (2.25, .7, "Eb5"), (3.25, .45, "Bb4")),
    ((0, .45, "F4"), (.75, .4, "G4"), (1.5, .4, "Bb4"),
     (2.25, .7, "C5"), (3.25, .45, "G4")),
    ((0, .4, "D5"), (.5, .4, "C5"), (1.25, .4, "Bb4"),
     (2, .4, "G4"), (2.75, .4, "F4"), (3.5, .4, "G4")),
    ((0, 1.15, "Eb4"), (1.5, .4, "G4"), (2.25, .4, "Bb4"),
     (3, .85, "C5")),
    _HOOK_A[4], _HOOK_A[5], _HOOK_A[6], _HOOK_A[7],
)


def _melody(start_bar: int, phrase, velocity: float) -> dict:
    return {
        start_bar + index: [
            (beat, duration, pitch, velocity)
            for beat, duration, pitch in events
        ]
        for index, events in enumerate(phrase)
    }


def _reed_answers(start_bar: int, bright: bool) -> dict:
    """One consonant answer per bar, never a second continuous melody."""
    if bright:
        colors = ("D5", "Bb4", "F4", "G4", "A4", "Bb4", "G4", "C5")
    else:
        colors = ("F4", "G4", "A4", "Bb4", "F4", "G4", "D5", "G4")
    return {
        start_bar + index: [
            (1.0 if index % 2 == 0 else 2.5, .72, pitch, .40)
        ]
        for index, pitch in enumerate(colors)
    }


def _kit(start_bar: int, bars: int, mode: str) -> tuple:
    kick, snare, toms, wood, hats = {}, {}, {}, {}, {}
    for index in range(bars):
        bar = start_bar + index
        kick[bar] = [
            (0, .11, "C2", .92), (1.75, .11, "C2", .64),
            (2.5, .11, "C2", .84),
        ]
        if mode != "break":
            snare[bar] = [
                (1, .10, "C3", .70), (3, .10, "C3", .82)
            ]
        toms[bar] = [
            (.5, .12, "F3", .66), (1.5, .12, "C3", .58),
            (3.25, .12, "G3", .62 + .10 * (index % 2)),
        ]
        wood[bar] = [
            (.25, .05, "C6", .52), (1.25, .05, "G5", .44),
            (2.25, .05, "Bb5", .54), (3.5, .05, "F5", .46),
        ]
        beats = (
            (.5, 1.5, 2.5, 3.5) if mode == "break" else
            (0, .5, 1, 1.5, 2, 2.5, 3, 3.5)
        )
        hats[bar] = [
            (beat, .045, "C5", .34 if beat % 1 else .54)
            for beat in beats
        ]
    return kick, snare, toms, wood, hats


def build_tracks() -> list[Track]:
    mallet = _merge(
        _melody(0, _HOOK_A[:4], .68),
        _melody(4, _HOOK_A, .96),
        _melody(12, _HOOK_A, 1.0),
        _melody(20, _HOOK_B, .90),
        _melody(32, _HOOK_A, 1.0),
        _melody(40, _HOOK_C, .92),
    )
    echo = {}
    # A few delayed first notes widen the hook without duplicating every
    # mallet event into a competing second melody.
    for start, phrase in ((12, _HOOK_A), (32, _HOOK_A)):
        for index, events in enumerate(phrase):
            if index % 2 != 0:
                continue
            beat, duration, pitch = events[0]
            echo[start + index] = [
                (beat + .375, min(.24, duration), pitch, .26)
            ]
    reed = _merge(
        _reed_answers(20, bright=False),
        {
            28: [(0, 3.5, "Bb4", .42)],
            29: [(0, 3.5, "Eb5", .40)],
            30: [(0, 3.5, "D5", .42)],
            31: [(0, 3.5, "C5", .40)],
        },
        _reed_answers(40, bright=True),
    )
    bass = _merge(
        _bass(0, _A_ROOTS[:4]),
        _bass(4, _A_ROOTS),
        _bass(12, _A_ROOTS),
        _bass(20, _B_ROOTS),
        _bass(28, ("F2", "Bb1", "Eb2", "C2"), "break"),
        _bass(32, _A_ROOTS),
        _bass(40, _C_ROOTS),
    )
    sub_roots = (
        _A_ROOTS[:4] + _A_ROOTS + _A_ROOTS + _B_ROOTS
        + ("F2", "Bb1", "Eb2", "C2") + _A_ROOTS + _C_ROOTS
    )
    sub = {
        bar: [(0, 3.8, root, .30)]
        for bar, root in enumerate(sub_roots)
    }
    bells = {
        3: [(3, 1, "Bb5", .32)], 7: [(2.5, 1.5, "F6", .34)],
        11: [(3, 1, "C6", .34)], 15: [(3, 1, "Bb5", .36)],
        19: [(2, 2, "D6", .36)], 23: [(3, 1, "Eb6", .34)],
        27: [(2, 2, "Bb5", .38)], 31: [(2.5, 1.5, "F6", .34)],
        35: [(3, 1, "C6", .36)], 39: [(2, 2, "Bb5", .38)],
        43: [(3, 1, "D6", .34)], 47: [(2.5, 1.5, "F5", .36)],
    }
    swells = {
        bar: [(0, 3.75, pitch, velocity)]
        for bar, pitch, velocity in (
            (10, "F5", .26), (18, "C5", .28),
            (22, "Eb5", .30), (26, "Bb4", .28),
            (28, "F5", .36), (30, "Eb5", .34),
            (38, "Bb4", .28), (46, "Eb5", .28),
        )
    }

    sections = (
        _kit(0, 4, "break"),
        _kit(4, 8, "groove"),
        _kit(12, 8, "groove"),
        _kit(20, 8, "groove"),
        _kit(28, 4, "break"),
        _kit(32, 8, "groove"),
        _kit(40, 8, "groove"),
    )
    kick, snare, toms, wood, hats = (
        _merge(*(section[index] for section in sections))
        for index in range(5)
    )

    return [
        Track("mallet", ins.enchanted_mallet, .88, _bars(mallet)),
        Track("echo", ins.pluck_lead, .26, _bars(echo)),
        Track("reed", ins.breathy_reed, .50, _bars(reed)),
        Track("bass", ins.elastic_bass, 1.16, _bars(bass)),
        Track("sub", ins.round_bass, .42, _bars(sub)),
        Track("bells", ins.bell, .38, _bars(bells)),
        Track("swells", ins.reverse_bell, .40, _bars(swells)),
        Track("kick", ins.kick, .92, _bars(kick)),
        Track("snare", ins.snare, .66, _bars(snare)),
        Track("toms", ins.jungle_tom, .74, _bars(toms)),
        Track("wood", ins.woodblock, .76, _bars(wood)),
        Track("hats", ins.hat, .50, _bars(hats)),
    ]
