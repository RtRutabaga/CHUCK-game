"""Day City theme -- the night hook, taken to a lunchtime jazz trio.

An original ~87-second loop in D minor at 88 BPM. The phase document
allows the daytime theme to share a motif with the night one, so this
does not merely resemble it: the melody is *derived* from
`city_night._HOOK` in code -- the same pitches in the same order, with
every duration stretched and the phrase spread across twice the bars.
The tune Chuck whistled in the neon is the same tune at noon.

What changed is everything holding it up. The electronic kit is gone,
but nothing replaced it with silence: there is a walking bass under the
whole loop, a ride riding swung eighths over it, brushes on two and
four, and an electric piano that comps in syncopated stabs rather than
holding chords. The harmony moves -- sixteen bars of ii-V motion
through Gm9, Cmaj9 and Fmaj9 with a raised-ninth dominant leaning back
to the tonic each time -- where the night theme mostly sat still.

Halfway through, a tenor answers the hook with a line of its own,
built from the same D dorian the hook lives in but phrased freely
against the bar. That is the section that used to be held harmony.

The unease survives it: the tonic is Dm(maj9), so the daylight is
bright but the major seventh in the middle of it never quite settles.

Structure (32 bars of 4/4):
    0-3    Count in     bass and ride alone, the trio starting up
    4-15   Head         the night hook augmented across twelve bars
    16-27  Answer       tenor solo over the turnaround
    28-31  Trading      the hook's first phrase again, into the loop
"""

from data.music.city_night import _HOOK as _NIGHT_HOOK
from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 88
BEATS_PER_BAR = 4
TOTAL_BARS = 32
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
# A full trio with a ride on top: busier than the night cue, so the
# ceiling comes down again to keep the two level with one another.
MASTER_HEADROOM = 0.80

# Swing: the second eighth of each beat lands late, which is most of
# what separates this from the night theme's straight sixteenths.
_SWING = 0.66

_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def _midi(pitch: str) -> int:
    step = _SEMITONE[pitch[0]]
    body = pitch[1:]
    if body[0] in "#b":
        step += 1 if body[0] == "#" else -1
        body = body[1:]
    return (int(body) + 1) * 12 + step


def _name(midi: int) -> str:
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return f"{names[midi % 12]}{midi // 12 - 1}"


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for event in events:
            beat, duration, pitch = event[:3]
            velocity = event[3] if len(event) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, duration, pitch,
                              velocity))
    return notes


# Sixteen bars that actually go somewhere: two ii-V-i turnarounds and a
# lift up to the relative major in the middle. The night theme's four
# roots are all still in here, which is why it still sounds like the
# same city.
_ROOTS = (
    "D3", "G2", "E3", "A2",
    "D3", "Bb2", "E3", "A2",
    "D3", "G2", "C3", "F2",
    "Bb2", "E3", "A2", "D3",
)
_VOICING = {
    "D3": ("F4", "A4", "C#5", "E5"),     # Dm(maj9): the note that is wrong
    "G2": ("Bb3", "D4", "F4", "A4"),     # Gm9
    "E3": ("G4", "Bb4", "D5", "F5"),     # Em7b5, the ii of the turnaround
    "A2": ("C#4", "G4", "Bb4", "E5"),    # A7b9: the pull back to the tonic
    "Bb2": ("D4", "F4", "A4", "C5"),     # Bbmaj9
    "C3": ("E4", "G4", "B4", "D5"),      # Cmaj9: the one bar of pure daylight
    "F2": ("A3", "C4", "E4", "G4"),      # Fmaj9
}

# The comping figures, one bar each, cycled: anticipations and rests, so
# no two consecutive bars land the chord in the same place.
_COMP = (
    ((0.0, 0.9), (2.5, 1.1)),
    ((1.0, 0.7), (2.5, 0.6), (3.5, 0.9)),
    ((0.0, 0.6), (1.5, 0.8), (3.0, 0.7)),
    ((2.0, 1.2),),
    ((0.5, 0.9), (2.5, 1.3)),
    ((0.0, 0.7), (1.66, 0.6), (3.0, 1.0)),
)


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
            (beat, min(duration * 1.5, BEATS_PER_BAR - beat), pitch, .74)
        )
    return stretched


def _walking_bass() -> dict:
    """Four to the bar, chord tones, chromatic into the next root.

    A walking line is the single loudest signal that this is a trio and
    not a pad, and building it from the roots rather than writing it out
    means it cannot drift out of step with the harmony above it.
    """
    line: dict[int, list[tuple]] = {}
    for bar in range(TOTAL_BARS):
        root = _ROOTS[bar % len(_ROOTS)]
        following = _ROOTS[(bar + 1) % len(_ROOTS)]
        base = _midi(root)
        target = _midi(following)
        while target - base > 7:
            target -= 12
        while base - target > 7:
            target += 12
        chord = [base, base + 7, base + 10 if bar % 3 else base + 12]
        # ...and the last beat is a half step into wherever we are going.
        approach = target + (1 if target < base + 5 else -1)
        steps = [base, chord[1], chord[2], approach]
        for index, midi in enumerate(steps):
            velocity = .60 if index == 0 else .48 + .06 * (index % 2)
            line.setdefault(bar, []).append(
                (index, .92, _name(midi), velocity if bar >= 2 else .40)
            )
    return line


def _ride() -> dict:
    """Swung eighths: ding, ding-da, ding, ding-da."""
    pattern: dict[int, list[tuple]] = {}
    for bar in range(TOTAL_BARS):
        events = []
        for beat in range(BEATS_PER_BAR):
            events.append((beat, .34, "F#5", .40 if beat % 2 else .50))
            if beat % 2 == 1:
                events.append((beat + _SWING, .22, "F#5", .30))
        pattern[bar] = events
    return pattern


# The tenor's answer: D dorian, phrased across the bar lines rather than
# inside them, and deliberately not a second hook -- it wanders, lands
# on the ninth, and hands the tune back.
_ANSWER = {
    16: [(1.0, .9, "A4", .62), (2.0, .5, "C5", .58), (2.66, 1.2, "D5", .66)],
    17: [(1.5, .7, "E5", .60), (2.5, 1.3, "C5", .56)],
    18: [(0.66, .5, "Bb4", .58), (1.5, .5, "A4", .60),
         (2.5, 1.4, "G4", .62)],
    19: [(1.0, 2.4, "A4", .58)],
    20: [(0.5, .5, "D5", .64), (1.5, .5, "F5", .62),
         (2.5, 1.3, "E5", .60)],
    21: [(1.0, .6, "C5", .56), (2.0, .6, "A4", .58), (3.0, .9, "F4", .54)],
    22: [(0.66, .5, "G4", .58), (1.66, .5, "Bb4", .60),
         (2.66, 1.2, "A4", .64)],
    23: [(1.5, 2.0, "D5", .60)],
    24: [(0.5, .5, "F5", .62), (1.0, .5, "E5", .58),
         (2.0, .5, "D5", .60), (3.0, .9, "C5", .54)],
    25: [(0.66, .6, "Bb4", .58), (2.0, 1.6, "A4", .62)],
    26: [(1.0, .5, "G4", .56), (2.0, .5, "A4", .58),
         (2.66, 1.1, "E5", .64)],
    27: [(1.0, 2.6, "D5", .58)],
}


def build_tracks() -> list[Track]:
    lead = {bar: events for bar, events in _augmented_hook(4).items()
            if bar < 16}
    # The loop ends mid-phrase: the first four bars of the hook again,
    # stopping before its answer, so the join never feels like an ending.
    for bar, events in _augmented_hook(28).items():
        if bar < TOTAL_BARS:
            lead[bar] = [(beat, duration, pitch, .66)
                         for beat, duration, pitch, _v in events]

    keys = {}
    pads = {}
    for bar in range(TOTAL_BARS):
        root = _ROOTS[bar % len(_ROOTS)]
        chord = _VOICING[root]
        opening = bar < 4
        figure = _COMP[bar % len(_COMP)]
        # Comping, not holding: short voicings placed off the beat, with
        # the top note left out of some of them so the piano breathes.
        keys[bar] = []
        for index, (beat, duration) in enumerate(figure):
            level = (.34 if opening else .54) * (1.0 if index == 0 else .88)
            voices = chord if index % 2 == 0 else chord[:3]
            for voice_index, pitch in enumerate(voices):
                keys[bar].append(
                    (beat, duration, pitch, level * (1.0 - voice_index * .12))
                )
        # The pad is still there, but well underneath and out of the way.
        pads[bar] = [(0, 4, chord[1], .34 if not opening else .26)]

    # Brushes: two and four, and a pickup into the next bar now and then.
    brush = {}
    for bar in range(2, TOTAL_BARS):
        events = [(1, .3, "D2", .30), (3, .3, "D2", .34)]
        if bar % 4 == 3:
            events.append((3 + _SWING, .2, "D2", .22))
        brush[bar] = events

    # Rain, louder than at night: in daylight you can see it falling.
    rain = {
        bar: [(0, 3.95, _ROOTS[bar % len(_ROOTS)], .62)]
        for bar in range(TOTAL_BARS)
    }
    # Water off an awning, irregular, never on a beat.
    drips = {
        bar: [(1.35, .16, "A4", .26), (3.15, .16, "D5", .22)]
        for bar in range(TOTAL_BARS) if bar % 3 == 1
    }

    return [
        Track("lead", ins.bell, .86, _bars(lead)),
        Track("answer", ins.breathy_reed, .78, _bars(_ANSWER)),
        Track("keys", ins.electric_key, .60, _bars(keys)),
        Track("pad", ins.cloud_pad, .48, _bars(pads)),
        Track("bass", ins.round_bass, .82, _bars(_walking_bass())),
        Track("ride", ins.hat, .26, _bars(_ride())),
        Track("brush", ins.snare, .26, _bars(brush)),
        Track("rain", ins.rain_wash, .80, _bars(rain)),
        Track("drips", ins.sewer_drip, .40, _bars(drips)),
    ]
