"""Urban Sewer theme -- dark funk in a concrete tunnel.

An original ~65-second loop in G minor at 104 BPM. The phase document
points at the memorable groove of classic underground music as a broad
reference, so what is borrowed is the *idea*: a short low-register motif
you remember, repeating under a long walk. Nothing else is. This riff is
straight-feel sixteenth funk built on G-B flat-C-D flat -- a blue flat
five -- where the reference is a triplet-feel chromatic descent. Melody,
bass line, harmony and arrangement are all original.

The register is deliberately low and the palette narrow: rubbery funk
bass, clipped woodblock and hats, struck utility pipes answering the
riff from somewhere further down the tunnel, and water falling into
standing water. There is no lead melody above it at all, because the
sewer maps are long and winding and a tune would wear out first.

Structure (28 bars of 4/4):
    0-3    Down the pipe   bass riff alone, drips, one distant pipe
    4-11   Groove          full kit, pipes answering every second bar
    12-17  Deeper          the riff drops a fourth; pipes go sparse
    18-23  Pressure        tightest sixteenths, the throb underneath
    24-27  Return          the opening riff, pipes overhead, into the loop
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 104
BEATS_PER_BAR = 4
TOTAL_BARS = 28
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
# Almost everything here lives below 300Hz, which reads far louder than a
# spread arrangement. The ceiling keeps the tunnel level with the street.
MASTER_HEADROOM = 0.78


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for event in events:
            beat, duration, pitch = event[:3]
            velocity = event[3] if len(event) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, duration, pitch,
                              velocity))
    return notes


# The motif: seven notes, all off the beat except the first. G minor with
# a flat five leaning on the fourth -- the blue note is the hook.
_RIFF = (
    (0, .35, "G2", .92), (.75, .25, "G2", .58), (1.25, .35, "Bb2", .78),
    (1.75, .25, "C3", .62), (2.25, .35, "Db3", .86), (2.75, .25, "C3", .60),
    (3.25, .55, "Bb2", .72),
)
# The same shape a fourth down for the middle section: same rhythm, so it
# is heard as the riff moving rather than as a different idea.
_RIFF_LOW = tuple(
    (beat, duration, {"G2": "D2", "Bb2": "F2", "C3": "G2", "Db3": "Ab2"}[pitch],
     velocity)
    for beat, duration, pitch, velocity in _RIFF
)
# The answer, up in the pipework: three notes, always late.
_ANSWER = ((2.5, .5, "G4", .48), (3.0, .4, "Bb4", .40), (3.5, .5, "D5", .44))


def build_tracks() -> list[Track]:
    bass = {}
    for bar in range(TOTAL_BARS):
        deep = 12 <= bar < 18
        riff = _RIFF_LOW if deep else _RIFF
        quiet = .62 if bar < 4 else 1.0
        events = [(beat, duration, pitch, velocity * quiet)
                  for beat, duration, pitch, velocity in riff]
        if 18 <= bar < 24:
            # Pressure: an extra sixteenth pickup into the next bar.
            events.append((3.75, .2, "F2", .54))
        bass[bar] = events

    # Struck pipes answer the riff from further along the tunnel. They
    # thin out in the deep section so the low end has the room.
    pipes = {}
    for bar in range(TOTAL_BARS):
        if bar == 2:
            pipes[bar] = [(3.5, .5, "G4", .34)]
        elif 4 <= bar < 12 and bar % 2 == 1:
            pipes[bar] = list(_ANSWER)
        elif 12 <= bar < 18 and bar % 3 == 0:
            pipes[bar] = [(3.0, .6, "F4", .34)]
        elif 24 <= bar and bar % 2 == 0:
            pipes[bar] = [(beat, duration, pitch, velocity * 1.1)
                          for beat, duration, pitch, velocity in _ANSWER]

    # A slow throb under the pressure section: the ground moving.
    throb = {
        bar: [(0, 3.9, "G1" if bar % 2 == 0 else "F1", .46)]
        for bar in range(18, 24)
    }

    kick = {}
    snare = {}
    hats = {}
    blocks = {}
    for bar in range(TOTAL_BARS):
        if bar < 4:
            hats[bar] = [(beat, .08, "F#2", .16) for beat in (1, 3)]
            continue
        tight = 18 <= bar < 24
        kick[bar] = [(0, .18, "C2", .86), (1.75, .18, "C2", .52),
                     (2.5, .18, "C2", .64)]
        snare[bar] = [(1, .18, "D2", .58), (3, .18, "D2", .60)]
        if tight:
            hats[bar] = [(beat / 4, .06, "F#2", .24 if beat % 2 else .14)
                         for beat in range(16)]
        else:
            hats[bar] = [(beat / 2, .07, "F#2", .22 if beat % 2 else .13)
                         for beat in range(8)]
        # Clipped wood on the offbeat: the clatter of a long tunnel.
        blocks[bar] = [(1.5, .06, "A3", .30), (3.25, .06, "A3", .24)]
        if tight:
            blocks[bar].append((2.75, .06, "C4", .26))

    # Water, all the way through, never on the beat.
    drips = {}
    for bar in range(TOTAL_BARS):
        offsets = ((0.65, "D5"), (2.15, "A4")) if bar % 2 == 0 else \
                  ((1.4, "F5"), (3.6, "C5"),)
        drips[bar] = [(beat, .16, pitch, .40) for beat, pitch in offsets]

    return [
        Track("bass", ins.elastic_bass, 1.05, _bars(bass)),
        Track("pipes", ins.hollow_pipe, .78, _bars(pipes)),
        Track("throb", ins.low_pulse, .58, _bars(throb)),
        Track("kick", ins.kick, .78, _bars(kick)),
        Track("snare", ins.snare, .44, _bars(snare)),
        Track("hats", ins.hat, .30, _bars(hats)),
        Track("blocks", ins.woodblock, .40, _bars(blocks)),
        Track("drips", ins.sewer_drip, .62, _bars(drips)),
    ]
