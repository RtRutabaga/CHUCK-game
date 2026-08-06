"""Zephyros launch and modern-city transition -- one evolving cue.

An original 48-second D-minor one-shot at 120 BPM.  It opens with the same
five-note contour as Chuck's established falling music, then progressively
adds Astral pulse, rushing wind, rain-like hats, struck-city metal, and a
restrained low synth.  The action breaks at sidewalk impact; rain, distant
urban resonance, bells, and a tired flute carry Chuck's quiet return.

Structure (24 bars of 4/4):
    0-1    Throw          familiar falling motif in open air
    2-4    Astral flight  pulse and bass gather beneath the wind
    5-11   City stitch    rain, urban metal, and subtle synth accumulate
    12-17  Rainy descent  full forward motion, breaking at impact
    18-23  Return         wet-city afterglow, reformation, cigarette
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 120
BEATS_PER_BAR = 4
TOTAL_BARS = 24
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
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


def _merge(*patterns: dict) -> dict:
    merged: dict = {}
    for pattern in patterns:
        for bar, events in pattern.items():
            merged.setdefault(bar, []).extend(events)
    return merged


# The opening phrase deliberately matches fall_to_chult's first lead phrase.
_FALL_MOTIF = (
    (0, 1, "D5"), (1, .5, "F5"), (1.5, .5, "G5"),
    (2, 1, "A5"), (3, 1, "F5"),
)

_LEAD_PHRASES = {
    0: [(*event, .72) for event in _FALL_MOTIF],
    2: [(0, .5, "A5", .74), (.5, .5, "G5", .70),
        (1, 1, "F5", .76), (2, .5, "D5", .68),
        (2.5, .5, "F5", .72), (3, 1, "C6", .76)],
    4: [(0, 1, "D5", .80), (1, 1, "A5", .76),
        (2, .5, "C6", .82), (2.5, .5, "A5", .74),
        (3, 1, "G5", .78)],
    6: [(0, .5, "F5", .75), (.5, .5, "G5", .72),
        (1, 1, "A5", .82), (2, .5, "C6", .78),
        (2.5, .5, "D6", .84), (3, 1, "A5", .76)],
    8: [(0, .5, "D6", .86), (.5, .5, "C6", .80),
        (1, .5, "A5", .76), (1.5, .5, "Eb6", .82),
        (2, .5, "D6", .86), (2.5, .5, "C6", .78),
        (3, .5, "A5", .74), (3.5, .5, "Eb5", .72)],
    10: [(0, .5, "D6", .86), (.5, .5, "Eb6", .82),
         (1, .5, "D6", .86), (1.5, .5, "A5", .76),
         (2, .5, "C6", .80), (2.5, .5, "Eb6", .84),
         (3, .5, "D6", .88), (3.5, .5, "A5", .76)],
    12: [(0, .5, "F5", .76), (.5, .5, "A5", .80),
         (1, .5, "C6", .82), (1.5, .5, "D6", .88),
         (2, .5, "Eb6", .84), (2.5, .5, "D6", .86),
         (3, .5, "C6", .80), (3.5, .5, "A5", .76)],
    14: [(0, .5, "D6", .88), (.5, .5, "Eb6", .84),
         (1, .5, "F6", .86), (1.5, .5, "Eb6", .80),
         (2, .5, "D6", .88), (2.5, .5, "C6", .80),
         (3, .5, "A5", .76), (3.5, .5, "Eb6", .82)],
    16: [(0, .5, "D6", .90), (.5, .5, "Eb6", .86),
         (1, .5, "D6", .88), (1.5, .5, "C6", .82),
         (2, .5, "A5", .78), (2.5, .5, "Eb6", .84),
         (3, .5, "D6", .90), (3.5, .5, "C6", .82)],
    # Bar 17 ends at beat 1.5, aligned with the sidewalk impact.
    17: [(0, .5, "D6", .92), (.5, .5, "Eb6", .88),
         (1, .5, "D6", .92)],
}

_ROOTS = (
    "D2", "Bb1", "D2", "C2", "A1", "D2", "F2", "C2", "A1",
    "D2", "Eb2", "C2", "D2", "F2", "C2", "A1", "D2", "D2",
)
_FIFTHS = {
    "D2": "A2", "Bb1": "F2", "C2": "G2", "A1": "E2",
    "F2": "C3", "Eb2": "Bb2",
}


def _pulse() -> dict:
    shapes = (
        ("D4", "F4", "A4", "C5"),
        ("D4", "F4", "Bb4", "A4"),
        ("E4", "G4", "C5", "G4"),
        ("D4", "Eb4", "A4", "C5"),
    )
    out = {}
    for bar in range(2, 18):
        shape = shapes[(bar - 2) % len(shapes)]
        steps = 3 if bar == 2 else (8 if bar < 17 else 3)
        out[bar] = [
            (step * .5, .40, shape[step % 4],
             .48 + (.14 if step % 2 == 0 else 0))
            for step in range(steps)
        ]
    return out


def _bass() -> dict:
    out = {}
    for bar, root in enumerate(_ROOTS):
        if bar < 2:
            out[bar] = [(0, 3.5, root, .30)]
            continue
        events = [
            (0, 1.5, root, .68), (2, .7, _FIFTHS[root], .46),
            (3, .75, root, .54),
        ]
        if bar == 17:
            events = [(0, 1.5, root, .72)]
        out[bar] = events
    return out


def _rhythm() -> tuple[dict, dict, dict]:
    kicks, snares, rain = {}, {}, {}
    for bar in range(5, 18):
        if bar >= 6:
            kicks[bar] = [(0, .1, "C2", .72), (2, .1, "C2", .64)]
            snares[bar] = [(1, .1, "C3", .58), (3, .1, "C3", .64)]
        rain[bar] = [
            (step * .5, .06, "C6", .28 + (step % 3) * .05)
            for step in range(8)
        ]
    kicks[17] = [(0, .1, "C2", .82)]
    snares[17] = [(1, .1, "C3", .76)]
    rain[17] = [event for event in rain[17] if event[0] < 1.5]
    # Rain survives the impact and becomes the principal city texture.
    for bar in range(18, TOTAL_BARS):
        rain[bar] = [
            (beat, .055, "C6", velocity)
            for beat, velocity in ((.25, .22), (1.0, .28), (1.75, .20),
                                   (2.5, .26), (3.25, .21))
        ]
    return kicks, snares, rain


def build_tracks() -> list[Track]:
    kicks, snares, rain = _rhythm()
    wind_pad = {
        bar: [(0, 4, pitch, .30 if bar < 12 else .38)]
        for bar, pitch in enumerate(
            ("D3", "A2", "D3", "F3", "C3", "D3", "A2", "F3",
             "C3", "D3", "Eb3", "C3", "D3", "F3", "C3", "A2",
             "D3", "D3", "D3", "Bb2", "F3", "C3", "A2", "D3")
        )
    }
    wind_swells = {
        bar: [(0, 3.7, pitch, velocity)]
        for bar, pitch, velocity in (
            (1, "A4", .24), (3, "D5", .28), (6, "F5", .30),
            (9, "C5", .34), (12, "Eb5", .36), (15, "D5", .38),
            (19, "F4", .20), (22, "D4", .18),
        )
    }
    urban_metal = {
        5: [(3, .7, "A3", .32)], 7: [(1.5, .8, "D4", .38)],
        9: [(3, .7, "C4", .42)], 11: [(1, 1, "Eb4", .44)],
        13: [(2.5, .8, "A3", .46)], 15: [(1.5, 1, "D4", .50)],
        17: [(0, 1.4, "D3", .62)], 20: [(2, 1.2, "A3", .18)],
        23: [(0, 1.5, "D3", .16)],
    }
    city_synth = {
        bar: [(0, 1.75, root, .24), (2, 1.75, _FIFTHS[root], .18)]
        for bar, root in enumerate(_ROOTS[5:17], start=5)
    }
    city_synth[17] = [(0, 1.4, "D2", .30)]
    aftermath = {
        18: [(2, 2, "A4", .28)],
        19: [(0, 2, "F4", .32), (2, 2, "E4", .28)],
        20: [(0, 4, "D4", .34)],
        21: [(0, 2, "A4", .24), (2, 2, "F4", .26)],
        22: [(0, 4, "E4", .25)],
        23: [(0, 4, "D4", .30)],
    }
    return_bells = {
        17: [(1.5, 2.5, "D5", .40)],
        18: [(0, 2, "D5", .38), (2, 2, "A4", .28)],
        19: [(0, 3, "F5", .30)], 20: [(1, 3, "E5", .25)],
        21: [(0, 4, "A4", .22)], 23: [(0, 4, "D5", .28)],
    }

    return [
        Track("falling_lead", ins.pluck_lead, .90, _bars(_LEAD_PHRASES)),
        Track("astral_pulse", ins.pluck_lead, .58, _bars(_pulse())),
        Track("bass", ins.round_bass, .82, _bars(_bass())),
        Track("wind_pad", ins.cloud_pad, .72, _bars(wind_pad)),
        Track("wind_swells", ins.reverse_bell, .48, _bars(wind_swells)),
        Track("city_synth", ins.low_pulse, .34, _bars(city_synth)),
        Track("urban_metal", ins.metal_hit, .44, _bars(urban_metal)),
        Track("kick", ins.kick, .72, _bars(kicks)),
        Track("snare", ins.snare, .60, _bars(snares)),
        Track("rain", ins.hat, .72, _bars(rain)),
        Track("return_flute", ins.flute, .68, _bars(aftermath)),
        Track("return_bells", ins.bell, .60, _bars(return_bells)),
    ]
