"""The ship theme — a jaunty sea-shanty Irish reel (session 144).

Built from the Waterdeep-docks rhythm — same warm D-mixolydian, the same
flat-seventh (C natural) coastal color and D/G/A groove — but cranked
from a slow harbor sway into a fast fiddle reel at 126 BPM. A driving
root-fifth bass and a bodhran backbeat carry a plucked-fiddle reel tune;
an accordion (reedy brass) chops the offbeats and swells the turns; a
tin whistle ornaments above; and in the second half the crew joins in
with shouted "hey!" vocals. Plays over the escape onto the ship and into
the next phase.

Structure (bars of 4/4, 40 bars, ~76s):
    0-7    A     the reel tune: fiddle, bass, bodhran
    8-15   B     the turn, up high; whistle + accordion swell in
    16-23  A'    the tune returns, the crew shouting along
    24-31  B'    the turn, full band
    32-39  A''   a last pass that loops back on itself

Eleven voices: fiddle, whistle, accordion, bass, crew (choir), kick,
snare, woodblock, hats, toms, bells. Note tails wrap the loop seam.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track

TEMPO_BPM = 126
BEATS_PER_BAR = 4
TOTAL_BARS = 40
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.9   # a loud, lively pub-band mix


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for ev in events:
            beat, dur, pitch = ev[0], ev[1], ev[2]
            vel = ev[3] if len(ev) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, dur, pitch, vel))
    return notes


def _merge(*patterns: dict) -> dict:
    out: dict = {}
    for p in patterns:
        for bar, events in p.items():
            out.setdefault(bar, []).extend(events)
    return out


# --- The reel tune, as bars of eight driving eighth notes -----------------
_A_PHRASES = (
    ("D4", "F#4", "A4", "F#4", "D5", "A4", "F#4", "A4"),
    ("G4", "B4", "D5", "B4", "G4", "A4", "B4", "G4"),
    ("F#4", "A4", "D5", "A4", "F#4", "E4", "D4", "E4"),
    ("A4", "G4", "F#4", "E4", "D4", "F#4", "A4", "B4"),
    ("D5", "A4", "F#4", "A4", "D5", "A4", "F#4", "A4"),
    ("G4", "B4", "D5", "B4", "G4", "A4", "B4", "G4"),
    ("A4", "B4", "C5", "B4", "A4", "G4", "F#4", "E4"),   # C natural
    ("D4", "F#4", "A4", "F#4", "E4", "D4", "E4", "F#4"),
)
_B_PHRASES = (
    ("A4", "D5", "F#5", "D5", "A4", "D5", "F#5", "A5"),
    ("G5", "F#5", "E5", "D5", "B4", "D5", "G4", "B4"),
    ("A4", "D5", "F#5", "A5", "G5", "F#5", "E5", "D5"),
    ("B4", "A4", "G4", "F#4", "E4", "F#4", "A4", "B4"),
    ("A4", "D5", "F#5", "D5", "A4", "D5", "F#5", "A5"),
    ("G5", "F#5", "E5", "D5", "B4", "D5", "G4", "B4"),
    ("C5", "B4", "A4", "G4", "F#4", "E4", "D4", "C4"),   # C natural
    ("D4", "F#4", "A4", "D5", "A4", "F#4", "A4", "F#4"),
)


def _reel(start_bar: int, phrases, vel: float) -> dict:
    out = {}
    for i, phrase in enumerate(phrases):
        events = []
        for j, pitch in enumerate(phrase):
            accent = 1.0 if j == 0 else (0.9 if j % 2 == 0 else 0.72)
            events.append((j * 0.5, 0.5, pitch, accent * vel))
        out[start_bar + i] = events
    return out


# --- Accompaniment --------------------------------------------------------
_A_ROOTS = ("D2", "G2", "D2", "A2", "D2", "G2", "A2", "D2")
_B_ROOTS = ("D2", "G2", "B1", "A2", "D2", "G2", "A2", "D2")
_FIFTH = {"D2": "A2", "G2": "D3", "A2": "E3", "B1": "F#2"}
_FIFTH_UP = {"D2": "A3", "G2": "D4", "A2": "E4", "B1": "F#3"}


def _bass(start_bar: int, roots) -> dict:
    """A driving root-fifth reel bass, a bounce on every beat."""
    out = {}
    for i, root in enumerate(roots):
        fifth = _FIFTH[root]
        out[start_bar + i] = [
            (0, 0.9, root, 1.0), (1, 0.9, fifth, 0.82),
            (2, 0.9, root, 0.95), (3, 0.6, fifth, 0.82),
            (3.5, 0.4, root, 0.66),
        ]
    return out


def _accordion(start_bar: int, roots, swell: bool) -> dict:
    """Reedy offbeat chops (the reel 'chuck'); sustained in the turns."""
    out = {}
    for i, root in enumerate(roots):
        fifth = _FIFTH_UP[root]
        if swell:
            out[start_bar + i] = [(0, 2, fifth, 0.5), (2, 2, root[0] + "3",
                                                       0.46)]
        else:
            out[start_bar + i] = [(1, 0.4, fifth, 0.5), (3, 0.4, fifth, 0.55)]
    return out


def _crew(start_bar: int) -> dict:
    """The crew shouting along: a 'hey!' on the phrase downbeats."""
    return {start_bar + 0: [(0, 0.5, "D4", 0.7), (0.5, 0.4, "D4", 0.5)],
            start_bar + 4: [(0, 0.5, "D4", 0.7), (0.5, 0.4, "A4", 0.5)],
            start_bar + 7: [(3, 0.6, "A4", 0.7)]}


def _whistle(start_bar: int, phrases) -> dict:
    """A tin-whistle ornament: the tune's high notes, sustained a touch."""
    out = {}
    for i, phrase in enumerate(phrases):
        out[start_bar + i] = [(0, 1.0, phrase[0], 0.42),
                              (2, 1.5, phrase[4], 0.4)]
    return out


def _kit(start_bar: int, bars: int, full: bool) -> tuple:
    kick, snare, wood, hats, toms = {}, {}, {}, {}, {}
    for i in range(bars):
        b = start_bar + i
        kick[b] = [(0, 0.14, "C2", 1.0), (2, 0.14, "C2", 0.92),
                   (2.75, 0.12, "C2", 0.6)]
        snare[b] = [(1, 0.13, "C3", 0.85), (3, 0.13, "C3", 1.0)]
        hats[b] = [(bt, 0.06, "C5", 0.55 if bt % 1 else 0.75)
                   for bt in (0.5, 1.5, 2.5, 3.5)]
        if full:
            wood[b] = [(bt * 0.5, 0.05, "G5", 0.5 if bt % 2 else 0.62)
                       for bt in range(8)]
        # A bodhran tom fill closes each eight-bar phrase.
        if i == bars - 1:
            toms[b] = [(2, 0.13, "D3", 0.8), (2.5, 0.13, "A2", 0.85),
                       (3, 0.13, "D3", 0.9), (3.5, 0.13, "F3", 0.95)]
    return kick, snare, wood, hats, toms


def build_tracks() -> list[Track]:
    fiddle = _merge(
        _reel(0, _A_PHRASES, 1.0), _reel(8, _B_PHRASES, 1.0),
        _reel(16, _A_PHRASES, 1.0), _reel(24, _B_PHRASES, 1.0),
        _reel(32, _A_PHRASES, 0.95),
    )
    whistle = _merge(
        _whistle(8, _B_PHRASES), _whistle(16, _A_PHRASES),
        _whistle(24, _B_PHRASES), _whistle(32, _A_PHRASES),
    )
    accordion = _merge(
        _accordion(0, _A_ROOTS, swell=False),
        _accordion(8, _B_ROOTS, swell=True),
        _accordion(16, _A_ROOTS, swell=False),
        _accordion(24, _B_ROOTS, swell=True),
        _accordion(32, _A_ROOTS, swell=False),
    )
    bass = _merge(
        _bass(0, _A_ROOTS), _bass(8, _B_ROOTS), _bass(16, _A_ROOTS),
        _bass(24, _B_ROOTS), _bass(32, _A_ROOTS),
    )
    crew = _merge(_crew(16), _crew(24), _crew(32))
    bells = {7: [(3, 1, "D6", 0.4)], 15: [(3, 1, "A5", 0.4)],
             23: [(3, 1, "D6", 0.42)], 31: [(3, 1, "F#6", 0.42)],
             39: [(2, 2, "D6", 0.44)]}

    sections = [
        _kit(0, 8, full=False), _kit(8, 8, full=True),
        _kit(16, 8, full=True), _kit(24, 8, full=True),
        _kit(32, 8, full=True),
    ]
    kick, snare, wood, hats, toms = (
        _merge(*(s[i] for s in sections)) for i in range(5))

    return [
        Track("fiddle", ins.pluck_lead, 1.0, _bars(fiddle)),
        Track("whistle", ins.flute, 0.85, _bars(whistle)),
        Track("accordion", ins.brass, 0.7, _bars(accordion)),
        Track("bass", ins.round_bass, 1.1, _bars(bass)),
        Track("crew", ins.choir, 0.7, _bars(crew)),
        Track("bells", ins.bell, 0.5, _bars(bells)),
        Track("kick", ins.kick, 1.05, _bars(kick)),
        Track("snare", ins.snare, 0.85, _bars(snare)),
        Track("woodblock", ins.woodblock, 0.7, _bars(wood)),
        Track("hats", ins.hat, 0.72, _bars(hats)),
        Track("toms", ins.jungle_tom, 0.95, _bars(toms)),
    ]
