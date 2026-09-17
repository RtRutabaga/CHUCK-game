"""Phlegethos, turned lethal --- the pit fiend's fortress approach.

The same theme as the rest of the realm, played as a fight. When the
Astral seal slams shut behind Chuck on the approach, the area theme
hands over to this: same E Phrygian dominant, same four-bar infernal
cycle (i - bII - i - bVII), and both of the realm's own lead phrases,
imported from `phlegethos` rather than copied so the fight cannot drift
into being a different tune. What changes is everything around them.

    * 152 BPM against the realm's 132 -- the same tune, hurrying.
    * The bass drives in eighths from the first bar and never lets up,
      and the low pulse is busy throughout. The theme's own opening bed
      is gone: there is no establishing shot in a fight.
    * A brass section the wandering theme does not have, stabbing the
      cycle on the off-beats and doubling the lead an octave down when
      the tune comes back at full height.
    * Timpani under the phrase ends, and the tribal toms churning
      rather than rolling.

Structure (bars of 4/4, 40 bars, ~63s):
    0-7    A   the realm's first lead phrase, already at full drive
    8-15   B   the climbing phrase; brass stabs answer it
    16-23  C   the churn -- choir, timpani, toms at their busiest
    24-31  B'  the climbing phrase at maximum, brass doubling the lead
    32-39  D   a turnaround that hands straight back into bar 0

Thirteen voices: lead, brass, choir, eerie flute, low pulse, bass, metal
hits, bells, timpani, kick, snare, toms, woodblock, hats. Note tails
wrap the loop seam, so the fight never hears the join.
"""

from data.music.phlegethos import FIFTH, LEAD_A, LEAD_B, OCTAVE, ROOTS
from src.audio import instruments as ins
from src.audio.sequencer import Note, Track

TEMPO_BPM = 152
BEATS_PER_BAR = 4
TOTAL_BARS = 40
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.95   # a fight mix, like the sanctum boss


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


def _pulse(start_bar: int, bars: int) -> dict:
    """The ground breathing under everything -- busy the whole way."""
    return {
        start_bar + i: [(0, 1.9, ROOTS[i % 4], 0.95),
                        (2, 1.4, ROOTS[i % 4], 0.85),
                        (3.5, 0.5, FIFTH[ROOTS[i % 4]], 0.75)]
        for i in range(bars)
    }


def _bass(start_bar: int, bars: int) -> dict:
    """Relentless eighths. The theme's walking version never appears."""
    out = {}
    for i in range(bars):
        root = ROOTS[i % 4]
        fifth, octave = FIFTH[root], OCTAVE[root]
        out[start_bar + i] = [
            (0, 0.45, octave, 1.0), (0.5, 0.45, octave, 0.78),
            (1, 0.45, fifth, 0.9), (1.5, 0.45, octave, 0.76),
            (2, 0.45, octave, 1.0), (2.5, 0.45, fifth, 0.8),
            (3, 0.45, octave, 0.92), (3.5, 0.45, fifth, 0.78),
        ]
    return out


def _lead(start_bar: int, phrases, vel: float, octave_down: bool = False):
    """One of the realm's lead phrases, optionally as a brass double."""
    def shift(pitch: str) -> str:
        if not octave_down:
            return pitch
        return f"{pitch[:-1]}{int(pitch[-1]) - 1}"

    return {start_bar + i: [(b, d, shift(p), vel) for b, d, p in phrase]
            for i, phrase in enumerate(phrases)}


def _stabs(start_bar: int, bars: int) -> dict:
    """Brass on the off-beats: the section the theme does not have.

    It answers the lead rather than covering it -- root and fifth of
    whatever bar of the cycle is underneath, hit short and hard.
    """
    out = {}
    for i in range(bars):
        root = ROOTS[i % 4]
        chord = f"{root[:-1]}3", f"{FIFTH[root][:-1]}3"
        out[start_bar + i] = [
            (1.5, 0.4, chord[0], 0.85), (1.5, 0.4, chord[1], 0.7),
            (3.5, 0.4, chord[0], 0.9), (3.5, 0.4, chord[1], 0.72),
        ]
    return out


def _kit(start_bar: int, bars: int, churn: bool) -> tuple:
    """The tribal engine, at fight tempo. Never the theme's quiet bed."""
    kick, snare, toms, wood, hats, metal, timp = {}, {}, {}, {}, {}, {}, {}
    for i in range(bars):
        bar = start_bar + i
        kick[bar] = [(0, 0.13, "C2", 1.0), (0.75, 0.12, "C2", 0.7),
                     (1.5, 0.12, "C2", 0.78), (2, 0.13, "C2", 0.95),
                     (3.25, 0.12, "C2", 0.72)]
        snare[bar] = [(1, 0.12, "C3", 0.9), (3, 0.12, "C3", 1.0)]
        if churn:
            snare[bar].append((3.75, 0.1, "C3", 0.6))
        toms[bar] = [(0, 0.14, "E3", 1.0), (0.75, 0.14, "B2", 0.78),
                     (1.5, 0.14, "E3", 0.88), (2.25, 0.14, "A2", 0.8),
                     (3, 0.14, "E3", 0.92), (3.5, 0.14, "B2", 0.74)]
        if churn:
            toms[bar].extend([(0.375, 0.1, "A2", 0.58),
                              (2.625, 0.1, "B2", 0.62),
                              (3.75, 0.1, "E3", 0.55)])
        wood[bar] = [(b * 0.5, 0.05, "B5", 0.55 if b % 2 else 0.68)
                     for b in range(8)]
        hats[bar] = [(b, 0.05, "C5", 0.55 if b % 1 else 0.75)
                     for b in (0.25, 0.75, 1.25, 1.75,
                               2.25, 2.75, 3.25, 3.75)]
        if i % 2 == 0:
            metal[bar] = [(2, 1.6, "E3", 0.78)]
        if i % 4 == 3:
            metal.setdefault(bar, []).append((3.5, 1.2, "B3", 0.68))
            # Timpani under the end of every phrase, where the realm's
            # own theme leaves a bell.
            timp[bar] = [(2, 1.2, "E2", 0.85), (3, 1, "B2", 0.7)]
    return kick, snare, toms, wood, hats, metal, timp


def build_tracks() -> list[Track]:
    lead = _merge(
        _lead(0, LEAD_A, 1.0),
        _lead(8, LEAD_B, 1.0),
        _lead(16, LEAD_A, 0.95),
        _lead(24, LEAD_B, 1.0),
    )
    # The turnaround: the head of the climbing phrase, thrown back at
    # the top of the loop.
    lead = _merge(lead, _lead(32, LEAD_B[:8], 1.0))

    # Brass: stabs under the first three sections, then it takes the
    # tune itself an octave down for the last full statement.
    brass = _merge(
        _stabs(0, 8), _stabs(8, 8), _stabs(16, 8),
        _lead(24, LEAD_B, 0.8, octave_down=True),
        _stabs(32, 8),
    )
    # The place is alive and it is watching the fight, all the way
    # through rather than in one swell.
    choir = _merge(
        {16 + i: [(0, 4, p, 0.55)]
         for i, p in enumerate(("E3", "E3", "F3", "F3",
                                "E3", "D3", "E3", "E3"))},
        {32 + i: [(0, 4, p, 0.5)]
         for i, p in enumerate(("E3", "F3", "E3", "D3",
                                "E3", "F3", "B3", "E3"))},
    )
    # What is left of the wandering theme's eerie upper voice: a few long
    # tones over the churn, and one across the loop seam.
    flute = _merge(
        {18: [(2, 2, "C5", 0.4)], 21: [(0, 3, "F4", 0.38)]},
        {39: [(0, 3.5, "E5", 0.4)]},
    )
    pulse = _merge(*(_pulse(bar, 8) for bar in range(0, 40, 8)))
    bass = _merge(*(_bass(bar, 8) for bar in range(0, 40, 8)))
    bells = {7: [(3, 1, "E5", 0.36)], 15: [(3, 1, "B5", 0.36)],
             23: [(2, 2, "C6", 0.4)], 31: [(3, 1, "B5", 0.36)],
             39: [(2, 2, "E5", 0.38)]}

    sections = [_kit(0, 8, churn=False), _kit(8, 8, churn=False),
                _kit(16, 8, churn=True), _kit(24, 8, churn=True),
                _kit(32, 8, churn=True)]
    kick, snare, toms, wood, hats, metal, timp = (
        _merge(*(s[i] for s in sections)) for i in range(7))

    return [
        Track("lead", ins.pluck_lead, 0.95, _bars(lead)),
        Track("brass", ins.brass, 0.8, _bars(brass)),
        Track("choir", ins.choir, 0.5, _bars(choir)),
        Track("eerie", ins.flute, 0.55, _bars(flute)),
        Track("pulse", ins.low_pulse, 0.95, _bars(pulse)),
        Track("bass", ins.round_bass, 1.2, _bars(bass)),
        Track("metal", ins.metal_hit, 0.9, _bars(metal)),
        Track("bells", ins.bell, 0.4, _bars(bells)),
        Track("timpani", ins.timpani, 0.9, _bars(timp)),
        Track("kick", ins.kick, 1.1, _bars(kick)),
        Track("snare", ins.snare, 0.9, _bars(snare)),
        Track("toms", ins.jungle_tom, 1.15, _bars(toms)),
        Track("wood", ins.woodblock, 0.66, _bars(wood)),
        Track("hats", ins.hat, 0.7, _bars(hats)),
    ]
