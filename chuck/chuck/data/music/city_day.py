"""Day City theme -- the night hook under cold overcast daylight.

An original ~82-second loop in D minor at 76 BPM. The phase document
allows the daytime theme to share a motif with the night one, so this
does not merely resemble it: the melody is *derived* from
`city_night._HOOK` in code -- the same pitches in the same order, with
every duration stretched and the phrase spread across twice the bars.
Slowed to two-thirds tempo and moved to a glassy bell, the tune Chuck
whistled in the neon reads as the same city seen flat and grey.

Everything around it changes. The electronic kit is gone; there is no
backbeat at all, only a soft brush on the second half of every other
bar. The electric piano stops comping and holds. A pad sits underneath
throughout, and the rain is louder than it was at night, because in
daylight you can see it coming down.

The unease is one note: the harmony leans on a major seventh that never
resolves, so the daylight stays wrong.

Structure (26 bars of 4/4):
    0-3    Grey light   pad and rain, the motif not yet stated
    4-15   A            the night hook augmented across twelve bars
    16-21  Overcast     harmony only, held; the melody waits
    22-25  Fragment     the hook's first phrase, unfinished, into the loop
"""

from data.music.city_night import _HOOK as _NIGHT_HOOK
from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 76
BEATS_PER_BAR = 4
TOTAL_BARS = 26
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
# Sustained pads and held keys, with no kit to cut through them: this
# needs more ceiling than the night cue to land at the same loudness.
MASTER_HEADROOM = 0.68


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for event in events:
            beat, duration, pitch = event[:3]
            velocity = event[3] if len(event) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, duration, pitch,
                              velocity))
    return notes


# Daylight harmony: the night theme's roots, but voiced with a major
# seventh left hanging. Dm(maj9) is the unease -- one semitone of it.
_ROOTS = ("D3", "Bb2", "F2", "A2", "D3", "Bb2", "G2", "A2")
_VOICING = {
    "D3": ("F4", "A4", "C#5", "E5"),     # Dm(maj9): the note that is wrong
    "Bb2": ("D4", "F4", "A4", "C5"),     # Bbmaj9
    "F2": ("A3", "C4", "E4", "G4"),      # Fmaj9
    "A2": ("C#4", "E4", "G4", "B4"),     # A9
    "G2": ("Bb3", "D4", "F4", "A4"),     # Gm9
}


def _augmented_hook(start_bar: int) -> dict:
    """Stretch the night hook to half speed across twice the bars.

    The pitches and their order are untouched -- this is the same tune,
    walking instead of running.
    """
    events = [
        (bar_index * BEATS_PER_BAR + beat, duration, pitch)
        for bar_index, bar in enumerate(_NIGHT_HOOK)
        for beat, duration, pitch in bar
    ]
    stretched: dict[int, list[tuple]] = {}
    for position, duration, pitch in events:
        slow = position * 1.5          # 8 night bars become 12 day bars
        bar = start_bar + int(slow // BEATS_PER_BAR)
        beat = slow % BEATS_PER_BAR
        stretched.setdefault(bar, []).append(
            (beat, min(duration * 1.5, BEATS_PER_BAR - beat), pitch, .70)
        )
    return stretched


def build_tracks() -> list[Track]:
    lead = {bar: events for bar, events in _augmented_hook(4).items()
            if bar < 16}
    # The loop ends mid-phrase: the first four bars of the hook again,
    # stopping before its answer, so the join never feels like an ending.
    for bar, events in _augmented_hook(22).items():
        if bar < TOTAL_BARS:
            lead[bar] = [(beat, duration, pitch, .62)
                         for beat, duration, pitch, _v in events]

    keys = {}
    pads = {}
    for bar in range(TOTAL_BARS):
        root = _ROOTS[bar % len(_ROOTS)]
        chord = _VOICING[root]
        opening = bar < 4
        held = .46 if opening else .58
        # No comping: the piano holds a chord for the whole bar and lets
        # it decay. Daylight is not rhythmic.
        keys[bar] = [
            (0, 3.8, chord[0], held),
            (0, 3.8, chord[2], held * .78),
            (2, 1.9, chord[3], held * .58),
        ]
        pads[bar] = [
            (0, 4, chord[1], .62 if not opening else .48),
            (0, 4, root, .40),
        ]

    bass = {
        bar: [(0, 3.2, _ROOTS[bar % len(_ROOTS)], .52 if bar >= 4 else .34)]
        for bar in range(TOTAL_BARS)
    }

    # No kit. One brush, late, every other bar -- the only pulse there is.
    brush = {
        bar: [(2.5, .3, "D2", .26)]
        for bar in range(4, TOTAL_BARS) if bar % 2 == 0
    }
    # Rain, louder than at night: in daylight you can see it falling.
    rain = {
        bar: [(0, 3.95, _ROOTS[bar % len(_ROOTS)], .70)]
        for bar in range(TOTAL_BARS)
    }
    # Water off an awning, irregular, never on a beat.
    drips = {
        bar: [(1.35, .16, "A4", .30), (3.15, .16, "D5", .26)]
        for bar in range(TOTAL_BARS) if bar % 3 == 1
    }

    return [
        Track("lead", ins.bell, .90, _bars(lead)),
        Track("keys", ins.electric_key, .82, _bars(keys)),
        Track("pad", ins.cloud_pad, .74, _bars(pads)),
        Track("bass", ins.synth_bass, .62, _bars(bass)),
        Track("brush", ins.snare, .30, _bars(brush)),
        Track("rain", ins.rain_wash, .95, _bars(rain)),
        Track("drips", ins.sewer_drip, .48, _bars(drips)),
    ]
