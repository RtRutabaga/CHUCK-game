"""The ship theme — a dark, swashbuckling pirate reel (session 145).

Built from the Waterdeep-docks rhythm (its fast D-centred groove), but
turned pirate: D MINOR now, driving a galloping root-fifth bass under a
plucked-fiddle tune that hammers the classic minor pirate loop
(i - bVI - bVII: Dm-Bb-C) and, in the turns, the descending Andalusian
cadence (Dm-C-Bb-A) with the raised-seventh C# that gives swashbuckler
music its menace. Bold accordion (brass) horns, a bodhran gallop, a tin
whistle above, and a gruff crew chanting along. Plays over the escape
onto the ship and into the next phase.

Structure (bars of 4/4, 40 bars, ~76s):
    0-7    A     the pirate loop: fiddle, galloping bass, bodhran
    8-15   B     the Andalusian turn; whistle + accordion swell in
    16-23  A'    the loop returns, the crew shouting along
    24-31  B'    the turn, full band, brass horns
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


# --- The pirate tune, as bars of eight driving eighth notes ---------------
# D minor: the i-bVI-bVII loop (Dm-Bb-C) in A, the descending Andalusian
# cadence (Dm-C-Bb-A) with a raised-seventh C# over the A in B.
_A_PHRASES = (
    ("D4", "D4", "A4", "D5", "A4", "F4", "D4", "F4"),    # i  (Dm)
    ("Bb4", "Bb4", "F4", "Bb4", "D5", "Bb4", "F4", "D4"),  # bVI (Bb)
    ("C5", "C5", "G4", "C5", "E5", "C5", "G4", "E4"),    # bVII (C)
    ("D5", "A4", "F4", "D4", "A3", "D4", "F4", "A4"),    # i
    ("D4", "D4", "A4", "D5", "A4", "F4", "D4", "F4"),
    ("Bb4", "Bb4", "F4", "Bb4", "D5", "Bb4", "F4", "D4"),
    ("C5", "G4", "Bb4", "A4", "G4", "F4", "E4", "D4"),   # descending
    ("D4", "E4", "F4", "G4", "A4", "F4", "A4", "F4"),    # cadence
)
_B_PHRASES = (
    ("A4", "D5", "F5", "D5", "A4", "F5", "D5", "A4"),    # Dm
    ("G4", "C5", "E5", "C5", "G4", "E5", "C5", "G4"),    # C
    ("F4", "Bb4", "D5", "Bb4", "F4", "D5", "Bb4", "F4"),  # Bb
    ("E4", "A4", "C#5", "A4", "E4", "C#5", "A4", "E4"),  # A (raised 7th C#)
    ("A4", "D5", "F5", "D5", "A4", "F5", "D5", "A4"),
    ("G4", "C5", "E5", "C5", "G4", "E5", "C5", "G4"),
    ("Bb4", "A4", "G4", "F4", "E4", "F4", "G4", "A4"),   # Bb descending
    ("A4", "C#5", "E5", "C#5", "A4", "E4", "D4", "A3"),  # A -> D cadence
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
_A_ROOTS = ("D2", "Bb1", "C2", "D2", "D2", "Bb1", "C2", "D2")
_B_ROOTS = ("D2", "C2", "Bb1", "A1", "D2", "C2", "Bb1", "A1")
_FIFTH = {"D2": "A2", "Bb1": "F2", "C2": "G2", "A1": "E2"}
# The "chord colour" the accordion holds — the fifth, but the raised-7th
# C# over the A chord for the swashbuckler cadence.
_COLOUR = {"D2": "A3", "Bb1": "F3", "C2": "G3", "A1": "C#4"}


def _bass(start_bar: int, roots) -> dict:
    """A galloping root-fifth bass — relentless eighths, pirate-chase drive."""
    out = {}
    for i, root in enumerate(roots):
        fifth = _FIFTH[root]
        out[start_bar + i] = [
            (0, 0.45, root, 1.0), (0.5, 0.45, root, 0.72),
            (1, 0.45, fifth, 0.88), (1.5, 0.45, root, 0.7),
            (2, 0.45, root, 0.95), (2.5, 0.45, root, 0.72),
            (3, 0.45, fifth, 0.88), (3.5, 0.45, root, 0.7),
        ]
    return out


def _accordion(start_bar: int, roots, swell: bool) -> dict:
    """Reedy offbeat chops (the 'chuck'); bold sustained horns in the turns."""
    out = {}
    for i, root in enumerate(roots):
        colour = _COLOUR[root]
        if swell:
            out[start_bar + i] = [(0, 2, colour, 0.62),
                                  (2, 2, root[:-1] + "3", 0.56)]
        else:
            out[start_bar + i] = [(1, 0.4, colour, 0.55),
                                  (3, 0.4, colour, 0.6)]
    return out


def _crew(start_bar: int) -> dict:
    """The crew chanting along, low and gruff — 'hey! ho!' through the bars."""
    return {
        start_bar + 0: [(0, 0.5, "D3", 0.85), (0.5, 0.45, "D3", 0.6)],
        start_bar + 2: [(0, 0.5, "F3", 0.7), (2, 0.5, "F3", 0.55)],
        start_bar + 4: [(0, 0.5, "D3", 0.85), (0.5, 0.45, "A3", 0.6)],
        start_bar + 6: [(0, 0.5, "C4", 0.7)],
        start_bar + 7: [(2, 0.5, "A3", 0.7), (3, 0.7, "D3", 0.85)],
    }


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
    # Sparse low bell tolls, like a ship's bell — no bright chimes.
    bells = {7: [(3, 1, "D5", 0.42)], 15: [(3, 1, "A4", 0.42)],
             23: [(3, 1, "D5", 0.44)], 31: [(3, 1, "A4", 0.44)],
             39: [(2, 2, "D5", 0.46)]}

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
        Track("accordion", ins.brass, 0.92, _bars(accordion)),
        Track("bass", ins.round_bass, 1.1, _bars(bass)),
        Track("crew", ins.choir, 0.7, _bars(crew)),
        Track("bells", ins.bell, 0.5, _bars(bells)),
        Track("kick", ins.kick, 1.05, _bars(kick)),
        Track("snare", ins.snare, 0.85, _bars(snare)),
        Track("woodblock", ins.woodblock, 0.7, _bars(wood)),
        Track("hats", ins.hat, 0.72, _bars(hats)),
        Track("toms", ins.jungle_tom, 0.95, _bars(toms)),
    ]
