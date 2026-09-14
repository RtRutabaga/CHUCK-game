"""End credits theme -- the Fall to Chult cue, as an upbeat ska tune.

The fall cue is a sixteenth-note D-minor chase over Dm-Bb-C-Am. Played
upbeat and twice as happy, that progression and that tune are already
most of a ska number. So: the same key, the same chords, the fall's lead
phrases handed to a horn section, and everything around them turned
upside down onto the offbeat. Organ and guitar skank on every "and", a
walking bass, kick and snare on the beat, hats chopping between. The
chromatic Eb bars that pressed in as the canopy came up become a one-drop
breakdown; the fall's ascending pulse becomes the fanfare that opens it.
In the middle it lifts into F major, where a new tune in the fall's
rhythm gets the horns to themselves.

No intro: it opens on a bar of drums alone -- two hits and a snare roll
-- that kicks the melody off, and the same bar brings it round again at
the end of every loop.

Structure (bars of 4/4, 68 bars at 168 BPM, ~97s, looping):
    0      pickup     drums only: two hits and a snare roll into the tune
    1-16   A          the fall's lead on horns, skank, walking bass
    17-32  B          the lift into F major: a new tune in the same rhythm
    33-40  C          one-drop breakdown on the fall's chromatic Eb bars
    41-56  A'         the lead again, flute on top, four on the floor
    57-64  solo       flute over Dm-Bb-C-A
    65-67  turnaround horn hits on A major, into the pickup

Voices: horns, horn harmony, flute, organ skank, guitar skank, bass,
bells, kick, snare, hats. Note tails wrap the loop seam.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track

TEMPO_BPM = 168
BEATS_PER_BAR = 4
TOTAL_BARS = 68
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.85


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


# --- Pitch arithmetic ------------------------------------------------------
_NAMES = ("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")
_INDEX = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4,
          "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9,
          "A#": 10, "Bb": 10, "B": 11}


def _midi(name: str) -> int:
    pitch, octave = name[:-1], int(name[-1])
    return (octave + 1) * 12 + _INDEX[pitch]


def _name(midi: int) -> str:
    return f"{_NAMES[midi % 12]}{midi // 12 - 1}"


def _shift(name: str, semitones: int) -> str:
    return _name(_midi(name) + semitones)


# D natural minor, for the horn harmony a diatonic third below the tune.
_D_MINOR = (2, 4, 5, 7, 9, 10, 0)


def _third_below(name: str) -> str:
    midi = _midi(name)
    pc = midi % 12
    if pc not in _D_MINOR:
        return _name(midi - 3)
    step = _D_MINOR.index(pc)
    below = _D_MINOR[(step - 2) % 7]
    return _name(midi - ((pc - below) % 12))


# --- Harmony ---------------------------------------------------------------
_CHORDS = {
    "Dm": ("D", "F", "A"), "Bb": ("Bb", "D", "F"), "C": ("C", "E", "G"),
    "Am": ("A", "C", "E"), "F": ("F", "A", "C"), "Eb": ("Eb", "G", "Bb"),
    "A": ("A", "C#", "E"),
}


def _voicing(chord: str) -> list[str]:
    """A close triad in the skank register, around middle C to A4."""
    notes = []
    previous = None
    for index, pitch in enumerate(_CHORDS[chord]):
        octave = 3 if index == 0 and _INDEX[pitch] >= 7 else 4
        midi = _midi(f"{pitch}{octave}")
        while previous is not None and midi <= previous:
            midi += 12
        notes.append(_name(midi))
        previous = midi
    return notes


def _bass_root(chord: str) -> str:
    root = _CHORDS[chord][0]
    return f"{root}{1 if _INDEX[root] >= 9 else 2}"


# One chord per bar, for all 68.
_A_CHORDS = ("Dm", "Bb", "C", "Am", "Dm", "F", "C", "Am")
_B_CHORDS = ("F", "C", "Bb", "C", "F", "C", "Bb", "A")
_C_CHORDS = ("Dm", "Eb", "C", "Am", "Dm", "Eb", "C", "A")
_SOLO_CHORDS = ("Dm", "Bb", "C", "A")
CHORDS = (
    ("A",)
    + _A_CHORDS * 2
    + _B_CHORDS * 2
    + _C_CHORDS
    + _A_CHORDS * 2
    + _SOLO_CHORDS * 2
    + ("Dm", "Bb", "C")
)
assert len(CHORDS) == TOTAL_BARS

PICKUP = range(0, 1)
A = range(1, 17)
B = range(17, 33)
BREAK = range(33, 41)
A2 = range(41, 57)
SOLO = range(57, 65)
TURN = range(65, 68)


# --- The tune --------------------------------------------------------------
# The fall cue's own lead phrases (its bars 0, 2, 4, 6, 8, 10, 11), an
# octave down so the horns sit where horns sit.
_FALL_PHRASES = (
    [(0, 1, "D5"), (1, 0.5, "F5"), (1.5, 0.5, "G5"), (2, 1, "A5"),
     (3, 1, "F5")],
    [(0, 0.5, "A5"), (0.5, 0.5, "G5"), (1, 1, "F5"), (2, 0.5, "D5"),
     (2.5, 0.5, "F5"), (3, 1, "C6")],
    [(0, 1, "D5"), (1, 1, "A5"), (2, 0.5, "C6"), (2.5, 0.5, "A5"),
     (3, 1, "G5")],
    [(0, 0.5, "F5"), (0.5, 0.5, "G5"), (1, 1, "A5"), (2, 0.5, "C6"),
     (2.5, 0.5, "D6"), (3, 1, "A5")],
)
_FALL_CHROMATIC = (
    [(0, 0.5, "D6"), (0.5, 0.5, "C6"), (1, 0.5, "A5"), (1.5, 0.5, "Eb6"),
     (2, 0.5, "D6"), (2.5, 0.5, "C6"), (3, 0.5, "A5"), (3.5, 0.5, "Eb5")],
    [(0, 0.5, "D6"), (0.5, 0.5, "Eb6"), (1, 0.5, "D6"), (1.5, 0.5, "A5"),
     (2, 0.5, "C6"), (2.5, 0.5, "Eb6"), (3, 0.5, "D6"), (3.5, 0.5, "A5")],
    [(0, 0.5, "F5"), (0.5, 0.5, "A5"), (1, 0.5, "C6"), (1.5, 0.5, "D6"),
     (2, 0.5, "Eb6"), (2.5, 0.5, "D6"), (3, 0.5, "C6"), (3.5, 0.5, "A5")],
)
# The lift: a new tune in the fall's rhythm, over F-C-Bb-C / F-C-Bb-A.
_LIFT = (
    [(0, 0.5, "C5"), (0.5, 0.5, "F5"), (1, 0.5, "A5"), (1.5, 0.5, "C6"),
     (2, 1, "A5"), (3, 0.5, "G5"), (3.5, 0.5, "F5")],
    [(0, 1, "G5"), (1, 0.5, "E5"), (1.5, 0.5, "G5"), (2, 1.5, "C6"),
     (3.5, 0.5, "Bb5")],
    [(0, 0.5, "A5"), (0.5, 0.5, "Bb5"), (1, 1, "D6"), (2, 0.5, "C6"),
     (2.5, 0.5, "Bb5"), (3, 1, "A5")],
    [(0, 0.5, "G5"), (0.5, 0.5, "A5"), (1, 0.5, "Bb5"), (1.5, 0.5, "C6"),
     (2, 2, "E5")],
    [(0, 0.5, "C5"), (0.5, 0.5, "F5"), (1, 0.5, "A5"), (1.5, 0.5, "C6"),
     (2, 1, "A5"), (3, 0.5, "G5"), (3.5, 0.5, "F5")],
    [(0, 1, "G5"), (1, 0.5, "E5"), (1.5, 0.5, "G5"), (2, 1, "C6"),
     (3, 1, "D6")],
    [(0, 0.5, "D6"), (0.5, 0.5, "C6"), (1, 0.5, "Bb5"), (1.5, 0.5, "A5"),
     (2, 1, "F5"), (3, 1, "D5")],
    [(0, 1, "C#5"), (1, 1, "E5"), (2, 1, "A5"), (3, 0.5, "G5"),
     (3.5, 0.5, "E5")],
)


def _horn(phrase, octave: int = -12, velocity: float = 0.95) -> list:
    """Horns play short: every note clipped, so the offbeats breathe."""
    return [(beat, duration * 0.8, _shift(pitch, octave), velocity)
            for beat, duration, pitch in phrase]


def _answer(chord: str) -> list:
    """The horns' reply bar: two stabs on the offbeat and a pickup."""
    low, mid, top = _voicing(chord)
    return [(0.5, 0.25, _shift(top, 12), 0.8),
            (1.5, 0.25, _shift(top, 12), 0.85),
            (2.5, 0.4, _shift(mid, 12), 0.8),
            (3.5, 0.4, _shift(low, 12), 0.75)]


def _tune() -> dict:
    out: dict = {}
    # A and A': the fall's phrases, each answered.
    for section in (A, A2):
        for index, bar in enumerate(section):
            if index % 2 == 0:
                out[bar] = _horn(_FALL_PHRASES[(index // 2) % 4])
            else:
                out[bar] = _answer(CHORDS[bar])
    # B: the lift.
    for index, bar in enumerate(B):
        out[bar] = _horn(_LIFT[index % 8])
    # The breakdown: the chromatic bars, on their own.
    for index, bar in enumerate(BREAK):
        if index == 7:
            out[bar] = [(0, 0.3, "E5", 1.0), (1, 0.3, "E5", 1.0),
                        (2, 0.3, "C#5", 1.0), (3, 0.3, "A4", 1.0)]
        elif index % 2 == 0:
            out[bar] = _horn(_FALL_CHROMATIC[(index // 2) % 3])
        else:
            out[bar] = [(0, 0.3, _shift(_voicing(CHORDS[bar])[2], 12), 0.9)]
    # The solo is the flute's; the horns punch the downbeats.
    for bar in SOLO:
        out[bar] = [(0, 0.3, _shift(_voicing(CHORDS[bar])[2], 12), 0.7)]
    # Turnaround: hits, and into the drums' pickup.
    for bar in TURN:
        top = _shift(_voicing(CHORDS[bar])[2], 12)
        out[bar] = [(0, 0.3, top, 1.0), (1.5, 0.3, top, 0.9),
                    (2.5, 1.2, _shift(top, 2), 0.85)]
    return out


def _harmony(tune: dict) -> dict:
    """A third below the tune, in A' and the lift's second half."""
    bars = set(A2) | set(B[8:])
    return {bar: [(beat, dur, _third_below(pitch), vel * 0.8)
                  for beat, dur, pitch, vel in events]
            for bar, events in tune.items() if bar in bars}


def _flute() -> dict:
    out: dict = {}
    # In A', the fall's phrases an octave up over the horns.
    for index, bar in enumerate(A2):
        if index % 2 == 0:
            out[bar] = [(beat, dur, pitch, 0.55)
                        for beat, dur, pitch in _FALL_PHRASES[(index // 2) % 4]]
    # The solo: running eighths round the chord, a different turn each bar.
    shapes = ((0, 1, 2, 3, 2, 1, 0, 1), (2, 3, 4, 3, 2, 0, 1, 2),
              (4, 3, 2, 1, 2, 3, 4, 5), (0, 2, 1, 3, 2, 4, 3, 1))
    for index, bar in enumerate(SOLO):
        low, mid, top = (_shift(p, 12) for p in _voicing(CHORDS[bar]))
        tones = (low, mid, top, _shift(low, 12), _shift(mid, 12),
                 _shift(top, 12))
        shape = shapes[index % 4]
        out[bar] = [(step * 0.5, 0.42, tones[shape[step]],
                     0.8 if step % 2 == 0 else 0.62) for step in range(8)]
    return out


def _skank() -> tuple[dict, dict]:
    """Organ and guitar on the offbeats; the breakdown only on one."""
    organ, guitar = {}, {}
    for bar, chord in enumerate(CHORDS):
        voicing = _voicing(chord)
        if bar in PICKUP or bar in TURN:
            continue
        if bar in BREAK:
            offbeats = (2.5,)
        else:
            offbeats = (0.5, 1.5, 2.5, 3.5)
        organ[bar] = [(beat, 0.22, pitch, 0.8)
                      for beat in offbeats for pitch in voicing]
        guitar[bar] = [(beat + 0.02, 0.12, _shift(pitch, 12), 0.7)
                       for beat in offbeats for pitch in voicing[1:]]
    return organ, guitar


def _bass() -> dict:
    out: dict = {}
    for bar, chord in enumerate(CHORDS):
        root = _bass_root(chord)
        third = _shift(root, 3 if chord.endswith("m") else 4)
        fifth = _shift(root, 7)
        following = CHORDS[(bar + 1) % TOTAL_BARS]
        target = _midi(_bass_root(following))
        approach = _name(target - 1 if target - 1 > _midi(root) else target + 1)
        if bar in PICKUP:
            continue  # the drums' bar
        if bar in TURN:
            out[bar] = [(0, 0.3, root, 1.0), (1.5, 0.3, root, 0.9),
                        (2.5, 1.2, root, 0.85)]
        elif bar in BREAK:
            # One drop: the bass leaves a hole on one and lands on three.
            out[bar] = [(0.5, 0.4, root, 0.85), (2, 0.9, root, 1.0),
                        (3, 0.4, fifth, 0.8), (3.5, 0.4, third, 0.75)]
        else:
            out[bar] = [(0, 0.85, root, 1.0), (1, 0.85, third, 0.85),
                        (2, 0.85, fifth, 0.9), (3, 0.85, approach, 0.8)]
    return out


def _bells() -> dict:
    return {bar: [(0, 1.5, _shift(_voicing(CHORDS[bar])[2], 12), 0.4)]
            for bar in (A.start, A.start + 8, B.start, B.start + 8,
                        A2.start, A2.start + 8)}


def _kit() -> tuple[dict, dict, dict]:
    kicks, snares, hats = {}, {}, {}
    for bar in range(TOTAL_BARS):
        if bar in PICKUP or bar in TURN:
            # The pickup: two hits and a snare roll into the tune.
            hits = (0, 1) if bar in PICKUP else (0, 1.5, 2.5)
            kicks[bar] = [(beat, 0.12, "C2", 1.0) for beat in hits]
            snares[bar] = [(beat, 0.12, "C3", 0.9) for beat in hits]
            if bar in PICKUP:
                snares[bar] += [(2 + step * 0.25, 0.08, "C3",
                                 0.45 + step * 0.07) for step in range(8)]
            hats[bar] = []
            continue
        if bar in BREAK:
            kicks[bar] = [(2, 0.12, "C2", 1.0)]
            snares[bar] = [(2, 0.12, "C3", 0.85)]
            hats[bar] = [(step * 0.5, 0.06, "C5", 0.5 if step % 2 else 0.35)
                         for step in range(8)]
            continue
        four = bar in A2 or bar in B[8:]
        kicks[bar] = [(beat, 0.12, "C2", 0.95 if beat in (0, 2) else 0.75)
                      for beat in ((0, 1, 2, 3) if four else (0, 2))]
        snares[bar] = [(1, 0.12, "C3", 0.85), (3, 0.12, "C3", 0.95)]
        hats[bar] = [(beat + 0.5, 0.08, "C5", 0.8) for beat in range(4)]
        hats[bar] += [(float(beat), 0.05, "C5", 0.3) for beat in range(4)]
        # A pickup fill into each new section.
        if (bar + 1) in (B.start, BREAK.start, A2.start, SOLO.start,
                         TURN.start):
            snares[bar] += [(3 + step * 0.25, 0.08, "C3", 0.5 + step * 0.1)
                            for step in range(4)]
    return kicks, snares, hats


def build_tracks() -> list[Track]:
    tune = _tune()
    organ, guitar = _skank()
    kicks, snares, hats = _kit()
    return [
        Track("horns", ins.brass, 0.78, _bars(tune)),
        Track("horn_harmony", ins.brass, 0.5, _bars(_harmony(tune))),
        Track("flute", ins.flute, 0.8, _bars(_flute())),
        Track("organ", ins.electric_key, 0.5, _bars(organ)),
        Track("guitar", ins.pluck_lead, 0.3, _bars(guitar)),
        Track("bass", ins.round_bass, 1.2, _bars(_bass())),
        Track("bells", ins.bell, 0.6, _bars(_bells())),
        Track("kick", ins.kick, 0.9, _bars(kicks)),
        Track("snare", ins.snare, 0.8, _bars(snares)),
        Track("hats", ins.hat, 0.6, _bars(hats)),
    ]
