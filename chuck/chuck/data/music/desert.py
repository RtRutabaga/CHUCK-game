"""Chult desert theme -- Phase 13's region, and its arrival.

A two-minute loop in D at 96 BPM. It is the only piece of music the
region has: the arrival cutscene starts it and the desert map carries
it on, uninterrupted, because the audio system treats a repeat request
for the same track as a no-op. Stepping out of the cutscene and into
the playable desert is now not a change of channel but the same tune
still going.

That is why it grew. At seventy-five seconds it was a map theme with a
separate cue in front of it; at two minutes it is one piece that can
open a scene, carry a walk, and turn over without ever announcing its
own length.

The middle of it leans into the mode everybody hears as desert. The
frame -- the first eight bars and the last eight -- stays in D Dorian,
which is where the rest of the region's music lives and what the
arrival cue was written in. Everything between them is D Phrygian
dominant over a drone: the flat second and the major third against it,
the interval this kind of music is recognised by. Two thirds of the
loop is in it, which is what "the bulk" has to mean for the change to
register at all.

The two halves share D and A, so the joins are not modulations so much
as the same room being lit differently. Nothing was transposed to make
this work, which is the whole reason it does.

The kit is still deliberately thin -- a woodblock on the beat, a tabla
answering it -- because this is heat rather than adventure. What the
desert section adds is not more drums but a held drone underneath and a
reed that ornaments instead of stating, which is the difference between
a tune played in a mode and a tune that belongs to one.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 96
BEATS_PER_BAR = 4
TOTAL_BARS = 48
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.62

# Where the Dorian frame ends and the desert begins, and where it comes
# home. Two thirds of the loop is between them.
DESERT_IN = 8
DESERT_OUT = 40

# One chord to the bar. The frame's progression turns over every ten
# bars rather than every four so that the loop does not announce its
# own length; the desert section barely moves at all, because a drone
# is most of what that sound is.
_ROOTS = (
    # The Dorian frame, opening.
    "D2", "D2", "C2", "C2", "F2", "F2", "G2", "D2",
    # ...and the desert, which sits on D and leans off it.
    "D2", "D2", "Eb2", "D2", "D2", "G2", "A2", "D2",
    "D2", "Eb2", "D2", "D2", "G2", "G2", "A2", "A2",
    "D2", "D2", "Eb2", "Eb2", "D2", "G2", "A2", "D2",
    "D2", "Eb2", "D2", "A2", "D2", "D2", "G2", "A2",
    # ...and home, in the mode it started in.
    "D2", "C2", "F2", "G2", "A2", "F2", "C2", "D2",
)
_FIFTHS = {"D2": "A2", "C2": "G2", "F2": "C3", "G2": "D3", "A2": "E3",
           "Eb2": "Bb2"}
# The Dorian triads, unchanged: the arrival cue is written on these and
# a test compares the two, so the region and its opening keep one
# harmony between them.
_TRIADS = {
    "D2": ("D4", "F4", "A4"),
    "C2": ("C4", "E4", "G4"),
    "F2": ("F4", "A4", "C5"),
    "G2": ("G4", "B4", "D5"),
    "A2": ("A3", "C4", "E4"),
}
# ...and the same chords in D Phrygian dominant -- D, Eb, F#, G, A, Bb,
# C. The flat second sitting a semitone off the tonic and the major
# third above it is the entire effect; everything else here is just
# staying out of its way.
_DESERT_TRIADS = {
    "D2": ("D4", "F#4", "A4"),
    "Eb2": ("Eb4", "G4", "Bb4"),
    "G2": ("G4", "Bb4", "D5"),
    "A2": ("A3", "C#4", "E4"),
    "C2": ("C4", "Eb4", "G4"),
    "F2": ("F4", "A4", "C5"),
}


def _in_desert(bar: int) -> bool:
    return DESERT_IN <= bar < DESERT_OUT


def _triad(bar: int, root: str) -> tuple[str, str, str]:
    table = _DESERT_TRIADS if _in_desert(bar) else _TRIADS
    return table[root]


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for event in events:
            beat, duration, pitch = event[:3]
            velocity = event[3] if len(event) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, duration, pitch,
                              velocity))
    return notes


def build_tracks() -> list[Track]:
    arp: dict[int, list[tuple]] = {}
    bass: dict[int, list[tuple]] = {}
    reed: dict[int, list[tuple]] = {}
    lead: dict[int, list[tuple]] = {}
    pipe: dict[int, list[tuple]] = {}
    block: dict[int, list[tuple]] = {}
    drum: dict[int, list[tuple]] = {}
    drone: dict[int, list[tuple]] = {}

    for bar, root in enumerate(_ROOTS):
        triad = _triad(bar, root)
        fifth = _FIFTHS[root]

        # The engine of the whole theme: eighth-note broken triads,
        # running the entire loop. The notes it is broken out of are
        # what changes when the desert arrives -- the figure does not.
        arp[bar] = [(index * .5, .45, triad[index % 3], .60)
                    for index in range(8)]
        # ...with the shape inverted for a long stretch of the middle,
        # so two minutes of the same rising figure does not become a
        # drill.
        if 16 <= bar < 32:
            arp[bar] = [(index * .5, .45, triad[(2 - index) % 3], .58)
                        for index in range(8)]

        if _in_desert(bar):
            # A drone under the whole desert section, and a bass that
            # stops walking. This is the other half of why the middle
            # sounds like somewhere else: the harmony stops moving and
            # the melody has to carry it.
            drone[bar] = [(0, 4.0, "D2", .30), (0, 4.0, "A2", .22)]
            bass[bar] = [(0, 1.6, root, .84)]
            if bar % 4 == 3:
                bass[bar].append((2.5, 1.0, fifth, .52))
        else:
            bass[bar] = [(0, .9, root, .88), (2, .9, fifth, .74)]
            # Every fourth bar the bass picks up a passing eighth, which
            # is most of what stops it sounding mechanical.
            if bar % 4 == 3:
                bass[bar].append((3.5, .4, fifth, .50))

        # A woodblock on two and four and nothing else. The tabla
        # answers it through the desert stretch and then stops.
        block[bar] = [(1, .1, "D5", .26), (3, .1, "D5", .22)]
        if 12 <= bar < 36:
            drum[bar] = [(2.5, .12, "A3", .34), (3.75, .1, "D4", .26)]
        if 20 <= bar < 32:
            drum[bar].append((1.25, .1, "D4", .22))

    # The reed states the phrase and then shuts up for a long time --
    # this is a theme for a place, and the place is mostly empty. In the
    # frame it states; in the desert it ornaments, which is the
    # difference between a tune played in a mode and one that belongs
    # to it.
    reed[2] = [(1.0, 1.5, "A4", .74), (3.0, 1.0, "G4", .66)]
    reed[3] = [(0.5, 2.0, "F4", .70)]

    reed[10] = [(0.5, .5, "D5", .70), (1.0, .5, "Eb5", .72),
                (1.5, 1.5, "D5", .68), (3.0, 1.0, "A4", .60)]
    reed[11] = [(0.5, .5, "Bb4", .58), (1.0, .5, "A4", .62),
                (1.5, 2.0, "F#4", .66)]
    reed[18] = [(0.5, .5, "F#4", .62), (1.0, .5, "G4", .64),
                (1.5, .5, "A4", .68), (2.0, 2.0, "Bb4", .70)]
    reed[19] = [(0.5, .5, "A4", .62), (1.0, .5, "G4", .58),
                (1.5, 2.5, "D4", .60)]
    reed[26] = [(1.0, .5, "Eb5", .70), (1.5, .5, "D5", .66),
                (2.0, .5, "C#5", .64), (2.5, 1.5, "D5", .72)]
    reed[27] = [(0.5, 3.0, "A4", .58)]
    reed[34] = [(0.5, .5, "D5", .66), (1.0, .5, "Eb5", .68),
                (1.5, .5, "F#5", .70), (2.0, 2.0, "E5", .64)]
    reed[35] = [(0.5, 2.5, "D5", .60)]

    reed[44] = [(0.5, 1.5, "F4", .66), (2.5, 1.5, "G4", .70)]
    reed[46] = [(1.0, 1.0, "A4", .68), (2.0, 1.0, "G4", .62),
                (3.0, 1.0, "F4", .58)]

    # Twice in the loop the pulse lead comes in and plays the tune
    # properly -- once on the way into the desert, once on the way out
    # of it -- so a player who has been out here a while gets something
    # back.
    lead[6] = [(0, 1, "A4", .70), (1, 1, "G4", .64), (2, 2, "F4", .68)]
    lead[7] = [(0, 1, "G4", .66), (1, 1, "A4", .70), (2, 2, "D5", .74)]
    lead[30] = [(0, 1, "D5", .68), (1, 1, "Eb5", .62), (2, 2, "A4", .66)]
    lead[31] = [(0, 2, "F#4", .62), (2, 2, "D4", .58)]
    lead[41] = [(0, 1, "D5", .68), (1, 1, "C5", .62), (2, 2, "A4", .66)]
    lead[42] = [(0, 2, "G4", .62), (2, 2, "F4", .58)]
    lead[43] = [(0, 3, "D4", .56)]

    # One hollow answer from somewhere off the map, in the gaps the reed
    # leaves. Never underneath it -- two voices in an empty place should
    # be calling to each other, not harmonising.
    pipe[5] = [(1.0, 2.0, "D4", .40)]
    pipe[15] = [(2.0, 2.0, "A3", .38)]
    pipe[23] = [(1.0, 2.5, "Bb3", .34)]
    pipe[33] = [(2.0, 2.0, "Eb4", .32)]
    pipe[39] = [(1.0, 2.5, "A3", .36)]
    pipe[47] = [(0.5, 3.0, "D4", .34)]

    return [
        Track("arp", ins.pulse_arp, .80, _bars(arp)),
        Track("bass", ins.round_bass, 1.00, _bars(bass)),
        Track("drone", ins.throat_drone, .46, _bars(drone)),
        Track("reed", ins.breathy_reed, .78, _bars(reed)),
        Track("lead", ins.pluck_lead, .66, _bars(lead)),
        Track("pipe", ins.hollow_pipe, .54, _bars(pipe)),
        Track("block", ins.woodblock, .34, _bars(block)),
        Track("drum", ins.tabla_dayan, .42, _bars(drum)),
    ]
