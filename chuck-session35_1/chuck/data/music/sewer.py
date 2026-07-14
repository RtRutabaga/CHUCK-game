"""The Waterdeep Sewer theme — composition data.

Original piece, ~83 seconds per cycle. D natural minor at 104 BPM: the
daylit docks' warm D mixolydian dragged underground and into shadow —
same tonic, darker mode. Eerie and a little funky (Phase 2 spec): a
syncopated round-bass groove does the funk; a sparse minor lead and
dissonant bell drips (an Eb/Ab tritone against the D) do the unease —
"something is wrong down here" without a single realistic drip sample.

Structure (bars of 4/4):
    0-3    Intro       bass groove alone, a couple of bell drips
    4-11   A           minor lead enters over an off-beat funk kit
    12-19  A'          lead varied, flute long tones, busier hats
    20-27  B           the tritone turn — Eb/Ab dissonance, lead tense
    28-29  Transition  drums drop; a lonely flute + one bell
    30-35  A''         thinned, drums easing out, settling back to loop

Seven voices: pluck lead, flute, round bass, bell, kick/snare, hats.
The sequencer wraps note tails past the end back to the start: seamless.

Editing: everything here is (beat-in-bar, duration, pitch[, velocity])
tuples grouped per bar. Changing the tune touches zero engine code.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track

TEMPO_BPM = 104
BEATS_PER_BAR = 4
TOTAL_BARS = 36
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    """{bar_index: [(beat, dur, pitch[, vel]), ...]} -> absolute Notes."""
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


# ---------------------------------------------------------------------------
# Bass — the funk. A syncopated sixteenth-inflected groove per bar; each
# root carries its fifth and octave for the pops.
# ---------------------------------------------------------------------------
_COMP = {  # root -> (fifth, octave-up)
    "D2": ("A2", "D3"), "C2": ("G2", "C3"), "Bb1": ("F2", "Bb2"),
    "A1": ("E2", "A2"), "F2": ("C3", "F3"), "G2": ("D3", "G3"),
}
_A_ROOTS = ["D2", "D2", "Bb1", "C2", "D2", "D2", "F2", "C2"]
_B_ROOTS = ["A1", "A1", "F2", "F2", "Bb1", "Bb1", "A1", "A1"]


def _bass(start_bar: int, roots: list[str], busy: bool) -> dict:
    out = {}
    for i, r in enumerate(roots):
        fifth, octv = _COMP[r]
        b = start_bar + i
        if busy:
            out[b] = [(0, 0.5, r), (0.75, 0.25, r, 0.55),
                      (1.5, 0.5, octv, 0.8), (2, 0.5, fifth, 0.85),
                      (2.75, 0.25, r, 0.6), (3, 0.5, r, 0.8),
                      (3.5, 0.5, octv, 0.65)]
        else:
            out[b] = [(0, 1, r), (1.5, 0.5, fifth, 0.7),
                      (2, 1, r, 0.8), (3, 1, octv, 0.7)]
    return out


# ---------------------------------------------------------------------------
# Lead — sparse D-minor motif (pluck). The B variant leans on Eb (the
# Phrygian flat-2) for the tritone chill.
# ---------------------------------------------------------------------------
def _lead_a(start_bar: int, vel: float) -> dict:
    return {
        start_bar + 0: [(0, 1, "D4", vel), (1, 1, "F4", vel),
                        (2, 2, "A4", vel)],
        start_bar + 1: [(0, 1, "G4", vel), (1, 1, "F4", vel),
                        (2, 1, "E4", vel), (3, 1, "D4", vel)],
        start_bar + 2: [(0, 1.5, "F4", vel), (1.5, 0.5, "E4", vel),
                        (2, 2, "D4", vel)],
        start_bar + 3: [(0, 3, "A4", vel)],  # a held, hollow tone
        start_bar + 4: [(0, 1, "D4", vel), (1, 1, "F4", vel),
                        (2, 1, "A4", vel), (3, 1, "C5", vel)],
        start_bar + 5: [(0, 2, "Bb4", vel), (2, 1, "A4", vel),
                        (3, 1, "G4", vel)],
        start_bar + 6: [(0, 1, "F4", vel), (1, 1, "E4", vel),
                        (2, 1, "D4", vel), (3, 1, "E4", vel)],
        start_bar + 7: [(0, 4, "D4", vel)],
    }


def _lead_b(start_bar: int, vel: float) -> dict:
    return {
        start_bar + 0: [(0, 2, "A4", vel), (2, 2, "Eb5", vel * 0.9)],
        start_bar + 1: [(0, 1.5, "D5", vel), (1.5, 0.5, "C5", vel),
                        (2, 2, "Bb4", vel)],
        start_bar + 2: [(0, 2, "A4", vel), (2, 2, "F4", vel)],
        start_bar + 3: [(0, 4, "E4", vel)],
        start_bar + 4: [(0, 2, "A4", vel), (2, 1, "Bb4", vel),
                        (3, 1, "A4", vel)],
        start_bar + 5: [(0, 2, "Eb5", vel * 0.85), (2, 2, "D5", vel)],
        start_bar + 6: [(0, 1, "F4", vel), (1, 1, "E4", vel),
                        (2, 1, "D4", vel), (3, 1, "C4", vel)],
        start_bar + 7: [(0, 3, "D4", vel)],
    }


def _lead_outro(start_bar: int, vel: float) -> dict:
    """Six bars, thinned right down as it settles back to the loop."""
    return {
        start_bar + 0: [(0, 1, "D4", vel), (1, 1, "F4", vel),
                        (2, 2, "A4", vel)],
        start_bar + 1: [(0, 2, "G4", vel), (2, 2, "F4", vel)],
        start_bar + 2: [(0, 2, "F4", vel), (2, 2, "D4", vel)],
        start_bar + 3: [(0, 4, "A4", vel * 0.9)],
        start_bar + 4: [(0, 2, "F4", vel), (2, 1, "E4", vel),
                        (3, 1, "D4", vel)],
        start_bar + 5: [(0, 4, "D4", vel * 0.85)],
    }


def _flute_counter(start_bar: int) -> dict:
    """Long tones under A': a cold draft moving through the tunnel."""
    tones = ["A4", "F4", "G4", "A4", "D4", "F4", "E4", "D4"]
    return {start_bar + i: [(0.5, 3.0, t, 0.5)] for i, t in enumerate(tones)}


# ---------------------------------------------------------------------------
# Percussion — an off-beat funk kit (backbeat snare, syncopated kick,
# sixteenth hats). Sparse in A, busy in A'/B, easing out in A''.
# ---------------------------------------------------------------------------
def _kit(start_bar: int, bars: int, with_snare: bool, busy_hats: bool
         ) -> tuple[dict, dict, dict]:
    kicks, snares, hats = {}, {}, {}
    for i in range(bars):
        b = start_bar + i
        kicks[b] = [(0, 0.15, "C2"), (2.5, 0.15, "C2", 0.85),
                    (3.5, 0.15, "C2", 0.55)]
        if with_snare:
            snares[b] = [(1, 0.15, "C3", 0.9), (3, 0.15, "C3", 0.9)]
        if busy_hats:
            hats[b] = [(bt, 0.08, "C5", 0.85 if bt == int(bt) else 0.55)
                       for bt in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5)]
        else:
            hats[b] = [(bt, 0.08, "C5", 0.7) for bt in (0.5, 1.5, 2.5, 3.5)]
    return kicks, snares, hats


# ---------------------------------------------------------------------------
# The song
# ---------------------------------------------------------------------------
def build_tracks() -> list[Track]:
    lead = _merge(
        _lead_a(4, vel=0.95),
        _lead_a(12, vel=1.0),
        _lead_b(20, vel=0.9),
        _lead_outro(30, vel=0.8),
    )
    flute_part = _merge(
        _flute_counter(12),
        # Transition: a lonely descending pair, then silence before A''.
        {28: [(0, 4, "A4", 0.5)], 29: [(0, 3, "F4", 0.45)]},
    )
    bass = _merge(
        _bass(0, ["D2", "D2", "Bb1", "C2"], busy=False),   # intro
        _bass(4, _A_ROOTS, busy=True),                     # A
        _bass(12, _A_ROOTS, busy=True),                    # A'
        _bass(20, _B_ROOTS, busy=True),                    # B
        _bass(28, ["G2", "A1"], busy=False),               # transition
        _bass(30, ["D2", "D2", "Bb1", "C2", "D2", "C2"], busy=False),  # A''
    )
    bells = _merge(
        {0: [(0, 3, "D5", 0.5)], 2: [(2, 2, "A4", 0.45)]},  # intro drips
        {20: [(0, 2, "Eb5", 0.5)], 24: [(2, 2, "Ab4", 0.45)],
         27: [(3, 1, "A4", 0.5)]},                          # B tritone chill
        {28: [(2, 2, "Bb4", 0.5)]},                         # transition
    )
    kicks_a, snares_a, hats_a = _kit(4, 8, with_snare=True, busy_hats=False)
    kicks_b, snares_b, hats_b = _kit(12, 8, with_snare=True, busy_hats=True)
    kicks_c, snares_c, hats_c = _kit(20, 8, with_snare=True, busy_hats=True)
    kicks_d, snares_d, hats_d = _kit(30, 6, with_snare=False, busy_hats=False)

    return [
        Track("lead", ins.pluck_lead, 1.0, _bars(lead)),
        Track("flute", ins.flute, 1.0, _bars(flute_part)),
        Track("bass", ins.round_bass, 1.0, _bars(bass)),
        Track("bells", ins.bell, 1.0, _bars(bells)),
        Track("kick", ins.kick, 1.0,
              _bars(_merge(kicks_a, kicks_b, kicks_c, kicks_d))),
        Track("snare", ins.snare, 1.0,
              _bars(_merge(snares_a, snares_b, snares_c))),
        Track("hats", ins.hat, 1.0,
              _bars(_merge(hats_a, hats_b, hats_c, hats_d))),
    ]
