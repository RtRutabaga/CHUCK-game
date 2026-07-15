"""Fall to Chult cutscene cue -- fast action followed by a quiet landing.

The cue starts only after the cutscene has held on open sky for four seconds.
Once started it has no musical introduction: a sixteenth-note D-minor pulse,
driving bass, and full kit arrive together.  The pulse climbs and becomes more
chromatic as the canopy approaches, then breaks apart at impact.  Bells and a
small flute resolution carry Chuck's blip-back, look around, and cigarette drag.

At 120 BPM the 18 bars last 36 seconds.  Playback is one-shot, not looped.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 120
BEATS_PER_BAR = 4
TOTAL_BARS = 18
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR


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
    "D2", "Bb1", "C2", "A1",
    "D2", "F2", "C2", "A1",
    "D2", "Eb2", "C2", "A1", "D2",
)
_FIFTHS = {
    "D2": "A2", "Bb1": "F2", "C2": "G2", "A1": "E2",
    "F2": "C3", "Eb2": "Bb2",
}


def _action_pulse() -> dict:
    shapes = (
        ("D4", "F4", "A4", "C5"),
        ("D4", "F4", "Bb4", "A4"),
        ("E4", "G4", "C5", "G4"),
        ("E4", "A4", "C5", "A4"),
    )
    out = {}
    for bar in range(13):
        shape = shapes[bar % len(shapes)]
        if bar >= 8:
            # The wrong-note Eb presses into the established sewer harmony as
            # the jungle begins to intrude on the teal sky.
            shape = ("D4", "Eb4", "A4", "C5") if bar % 2 == 0 else (
                "F4", "A4", "D5", "Eb5"
            )
        events = []
        # Bar 12 stops halfway through: with the four-second playback delay,
        # beat 50 lands exactly on the cutscene's 29-second ground impact.
        steps = 4 if bar == 12 else 8
        for step in range(steps):
            events.append((step * 0.5, 0.42, shape[step % 4],
                           0.78 if step % 2 else 1.0))
        out[bar] = events
    return out


def _action_lead() -> dict:
    phrases = {
        0: [(0, 1, "D5"), (1, 0.5, "F5"), (1.5, 0.5, "G5"),
            (2, 1, "A5"), (3, 1, "F5")],
        2: [(0, 0.5, "A5"), (0.5, 0.5, "G5"), (1, 1, "F5"),
            (2, 0.5, "D5"), (2.5, 0.5, "F5"), (3, 1, "C6")],
        4: [(0, 1, "D5"), (1, 1, "A5"), (2, 0.5, "C6"),
            (2.5, 0.5, "A5"), (3, 1, "G5")],
        6: [(0, 0.5, "F5"), (0.5, 0.5, "G5"), (1, 1, "A5"),
            (2, 0.5, "C6"), (2.5, 0.5, "D6"), (3, 1, "A5")],
        8: [(0, 0.5, "D6"), (0.5, 0.5, "C6"), (1, 0.5, "A5"),
            (1.5, 0.5, "Eb6"), (2, 0.5, "D6"), (2.5, 0.5, "C6"),
            (3, 0.5, "A5"), (3.5, 0.5, "Eb5")],
        10: [(0, 0.5, "D6"), (0.5, 0.5, "Eb6"), (1, 0.5, "D6"),
             (1.5, 0.5, "A5"), (2, 0.5, "C6"), (2.5, 0.5, "Eb6"),
             (3, 0.5, "D6"), (3.5, 0.5, "A5")],
        11: [(0, 0.5, "F5"), (0.5, 0.5, "A5"), (1, 0.5, "C6"),
             (1.5, 0.5, "D6"), (2, 0.5, "Eb6"), (2.5, 0.5, "D6"),
             (3, 0.5, "C6"), (3.5, 0.5, "A5")],
        12: [(0, 0.5, "D6", 1.0), (0.5, 0.5, "Eb6", 1.0),
             (1, 0.5, "D6", 1.0), (1.5, 0.5, "C6", 1.0)],
    }
    return phrases


def _bass() -> dict:
    out = {}
    for bar, root in enumerate(_ROOTS):
        fifth = _FIFTHS[root]
        events = [
            (0, 0.75, root, 1.0), (1, 0.5, fifth, 0.85),
            (1.75, 0.25, root, 0.7), (2, 0.75, root, 0.95),
            (3, 0.5, fifth, 0.85), (3.5, 0.5, root, 0.8),
        ]
        out[bar] = [event for event in events if bar < 12 or event[0] < 2]
    return out


def _kit() -> tuple[dict, dict, dict]:
    kicks, snares, hats = {}, {}, {}
    for bar in range(13):
        kicks[bar] = [(0, 0.12, "C2"), (1.5, 0.12, "C2", 0.7),
                      (2, 0.12, "C2", 0.95), (3.25, 0.12, "C2", 0.75)]
        snares[bar] = [(1, 0.12, "C3", 0.9), (3, 0.12, "C3", 1.0)]
        hats[bar] = [
            (step * 0.5, 0.08, "C5", 0.82 if step % 2 == 0 else 0.55)
            for step in range(8)
        ]
        if bar >= 10:
            hats[bar].extend((step + 0.25, 0.06, "C5", 0.45)
                             for step in range(4))
        if bar == 12:
            kicks[bar] = [event for event in kicks[bar] if event[0] < 2]
            snares[bar] = [event for event in snares[bar] if event[0] < 2]
            hats[bar] = [event for event in hats[bar] if event[0] < 2]
    return kicks, snares, hats


def build_tracks() -> list[Track]:
    kicks, snares, hats = _kit()
    aftermath_lead = {
        13: [(2, 2, "A4", 0.35)],
        14: [(0, 2, "F4", 0.4), (2, 2, "E4", 0.35)],
        15: [(0, 4, "D4", 0.42)],
        16: [(0, 4, "A4", 0.3)],
        17: [(0, 4, "D4", 0.38)],
    }
    aftermath_bells = {
        12: [(2, 2, "D5", 0.65)],
        13: [(0, 2, "D5", 0.65), (2, 2, "A4", 0.45)],
        14: [(0, 3, "F5", 0.45)],
        15: [(1, 3, "E5", 0.35)],
        16: [(0, 4, "A4", 0.3)],
        17: [(0, 4, "D5", 0.5)],
    }
    bass_resolution = {
        14: [(0, 4, "D2", 0.35)],
        16: [(0, 4, "A1", 0.25)],
        17: [(0, 4, "D2", 0.32)],
    }
    action_bells = {
        bar: [(0, 1, "D5" if bar % 2 == 0 else "A4", 0.45)]
        for bar in (0, 4, 8, 10, 12)
    }

    return [
        Track("pulse", ins.pluck_lead, 0.72, _bars(_action_pulse())),
        Track("lead", ins.pluck_lead, 0.9, _bars(_action_lead())),
        Track("flute", ins.flute, 0.9, _bars(aftermath_lead)),
        Track("bass", ins.round_bass, 0.9,
              _bars(_merge(_bass(), bass_resolution))),
        Track("bells", ins.bell, 0.9,
              _bars(_merge(action_bells, aftermath_bells))),
        Track("kick", ins.kick, 0.9, _bars(kicks)),
        Track("snare", ins.snare, 0.85, _bars(snares)),
        Track("hats", ins.hat, 0.9, _bars(hats)),
    ]
