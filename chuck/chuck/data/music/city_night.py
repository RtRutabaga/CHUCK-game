"""Night City theme -- jazzy synth, rain-lit, nocturnal.

An original ~96-second loop in D minor at 96 BPM. The harmony is jazz
rather than pop: ii-V motion, a flat-six turn, and sevenths and ninths
stacked on a tine electric piano. A syncopated square bass pushes ahead
of the beat, brushed electronic drums stay restrained, and a low wash of
filtered noise keeps wet air under everything.

The hook is deliberately short and singable -- five notes falling and
answering itself -- so it survives being heard across six connected
maps. It states plainly, comes back harmonised, drops out entirely for a
darker middle, and returns up an octave over the fullest arrangement.

Structure (32 bars of 4/4):
    0-3    Wet street    keys and rain, the hook implied but not played
    4-11   A             the hook stated, bass and brushes enter
    12-19  A'            the hook harmonised, counter-line underneath
    20-25  Underpass     keys drop to stabs; the melody stays away
    26-31  A return      the hook an octave up, fullest arrangement
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 96
BEATS_PER_BAR = 4
TOTAL_BARS = 32
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
# Stacked electric-piano chords plus a square bass carry a lot of average
# energy. This keeps the city level against the temple and Feywild cues.
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


# The harmony: Dm9 - G13 - Cmaj9 - A7#5, with a Bb detour before the
# turnaround. Four bars, repeated with variation.
_ROOTS = (
    "D3", "G2", "C3", "A2",
    "D3", "G2", "Bb2", "A2",
)
_VOICING = {
    "D3": ("F4", "A4", "C5", "E5"),      # Dm9
    "G2": ("F4", "B4", "D5", "E5"),      # G13
    "C3": ("E4", "G4", "B4", "D5"),      # Cmaj9
    "A2": ("C#4", "G4", "Bb4", "E5"),    # A7#5b9
    "Bb2": ("D4", "F4", "A4", "C5"),     # Bbmaj9
}

# Five notes down, then the answer. Short enough to whistle after one map.
_HOOK = (
    ((0, .75, "A4"), (.75, .75, "F4"), (1.5, .5, "E4"), (2, 1, "D4"),
     (3.25, .75, "F4")),
    ((0, 1.5, "E4"), (1.75, .75, "D4"), (2.5, 1, "C4"), (3.5, .5, "D4")),
    ((0, .75, "F4"), (.75, .75, "A4"), (1.5, .5, "C5"), (2, 1.5, "B4"),
     (3.5, .5, "A4")),
    ((0, 2.5, "G4"), (3, 1, "E4")),
    ((0, .75, "A4"), (.75, .75, "F4"), (1.5, .5, "E4"), (2, 1, "D4"),
     (3.25, .75, "A4")),
    ((0, 1.5, "C5"), (1.75, .75, "Bb4"), (2.5, 1, "A4"), (3.5, .5, "G4")),
    ((0, .75, "F4"), (.75, .75, "G4"), (1.5, 1, "A4"), (2.5, 1.5, "C#5")),
    ((0, 3.5, "D5"),),
)


def _hook_at(start_bar: int, octave_up: bool = False,
             velocity: float = 1.0) -> dict:
    def lift(pitch: str) -> str:
        if not octave_up:
            return pitch
        name, number = pitch[:-1], int(pitch[-1])
        return f"{name}{number + 1}"

    return {
        start_bar + index: [
            (beat, duration, lift(pitch), velocity)
            for beat, duration, pitch in bar
        ]
        for index, bar in enumerate(_HOOK)
    }


def build_tracks() -> list[Track]:
    lead = {}
    lead.update(_hook_at(4, velocity=.92))          # stated
    lead.update(_hook_at(12, velocity=.86))         # harmonised
    # Bars 20-25 are the underpass: the melody stays away entirely.
    # The return is the hook's first six bars, an octave up, landing on
    # the turnaround so the loop seam falls mid-phrase rather than on a
    # full stop.
    lead.update({
        bar: events
        for bar, events in _hook_at(26, octave_up=True, velocity=.96).items()
        if bar < TOTAL_BARS
    })

    # A quiet counter-line under the second statement: the same shape
    # a third lower, so the hook thickens without a new idea.
    counter = {
        12: [(2, 1, "F3", .40)], 13: [(0, 1.5, "A3", .42), (3, 1, "G3", .34)],
        14: [(1, 1, "C4", .40)], 15: [(0, 2, "E3", .38)],
        16: [(2, 1, "D4", .40)], 17: [(0, 1.5, "F3", .42), (3, 1, "E3", .34)],
        18: [(1, 1, "A3", .40)], 19: [(0, 2, "D3", .40)],
    }

    keys = {}
    for bar in range(TOTAL_BARS):
        root = _ROOTS[bar % len(_ROOTS)]
        chord = _VOICING[root]
        if 20 <= bar < 26:
            # The underpass: clipped stabs, no sustain, harmony only.
            keys[bar] = [
                (0.5, .35, chord[0], .48), (0.5, .35, chord[2], .40),
                (2.5, .35, chord[1], .44), (2.5, .35, chord[3], .34),
            ]
            continue
        opening = bar < 4
        spread = .58 if opening else .74
        keys[bar] = [
            (0, 2.4, chord[0], spread),
            (0, 2.4, chord[1], spread * .82),
            (1.5, 2.2, chord[2], spread * .74),
            (2.75, 1.1, chord[3], spread * .60),
        ]

    bass = {}
    for bar in range(TOTAL_BARS):
        root = _ROOTS[bar % len(_ROOTS)]
        if bar < 4:
            bass[bar] = [(0, 2.5, root, .40)]
            continue
        quiet = .70 if 20 <= bar < 26 else 1.0
        # Pushed off the beat: the "and" of two is the loudest note.
        bass[bar] = [
            (0, .7, root, .74 * quiet),
            (1.5, .5, root, .58 * quiet),
            (2.25, .4, root, .82 * quiet),
            (3, .5, _VOICING[root][0], .52 * quiet),
            (3.5, .4, root, .46 * quiet),
        ]

    kick = {}
    snare = {}
    hats = {}
    for bar in range(4, TOTAL_BARS):
        soft = 20 <= bar < 26
        kick[bar] = [(0, .2, "C2", .60 if soft else .82),
                     (2.5, .2, "C2", .44 if soft else .58)]
        snare[bar] = [(1, .2, "D2", .40 if soft else .54),
                      (3, .2, "D2", .42 if soft else .56)]
        if soft:
            hats[bar] = [(beat, .1, "F#2", .18) for beat in (0.5, 2.5)]
        else:
            hats[bar] = [
                (beat, .1, "F#2", .26 if beat % 1 else .16)
                for beat in (0, .5, 1, 1.5, 2, 2.5, 3, 3.5)
            ]

    # Wet air, all the way through, following the bass loosely.
    rain = {
        bar: [(0, 3.9, _ROOTS[bar % len(_ROOTS)], .40)]
        for bar in range(TOTAL_BARS)
    }
    # A far-off bell on the turnarounds: a clock, or a crossing signal.
    signal = {
        3: [(3, 1, "D5", .30)], 11: [(3.5, .5, "A5", .26)],
        19: [(3, 1, "F5", .28)], 25: [(3.5, .5, "C#5", .30)],
        31: [(2.5, 1.5, "D5", .32)],
    }

    return [
        Track("lead", ins.pluck_lead, .82, _bars(lead)),
        Track("counter", ins.breathy_reed, .44, _bars(counter)),
        Track("keys", ins.electric_key, .95, _bars(keys)),
        Track("bass", ins.synth_bass, .90, _bars(bass)),
        Track("kick", ins.kick, .70, _bars(kick)),
        Track("snare", ins.snare, .46, _bars(snare)),
        Track("hats", ins.hat, .34, _bars(hats)),
        Track("rain", ins.rain_wash, .70, _bars(rain)),
        Track("signal", ins.bell, .40, _bars(signal)),
    ]
