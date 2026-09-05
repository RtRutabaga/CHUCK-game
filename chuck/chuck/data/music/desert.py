"""Chult desert theme -- Phase 13's opening region.

A ~74-second loop in D Dorian at 96 BPM. It is the walking-around
version of the arrival cutscene's little NES tune: same mode, same
tonic, the same broken-triad arpeggio running under it, so that
stepping out of the cutscene and into the playable desert sounds like
staying in one place rather than changing channel.

What it is not is that tune again. A cue eighteen seconds long can lead
with its melody; a theme the player will hear for the length of five
maps of unmarked exploration cannot, or it becomes the only thing they
can think about. So the roles are swapped. The arpeggio and the walking
bass carry the whole thing, a reed states a phrase roughly every eight
bars and then leaves a long gap, and the tune's own shape only arrives
whole twice in the loop.

The kit is deliberately thin -- a woodblock on the beat and a single
tabla answering it -- because this is heat rather than adventure, and
because a full drum part under a search for an unmarked exit gets
tiring long before the player finds it.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 96
BEATS_PER_BAR = 4
TOTAL_BARS = 30
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.68

# One chord to the bar, thirty bars, resolving home at the seam. The
# progression turns over every ten bars rather than every four so that
# the loop does not announce its own length.
_ROOTS = (
    "D2", "D2", "C2", "C2", "F2", "F2", "G2", "D2", "A2", "D2",
    "D2", "F2", "C2", "C2", "G2", "G2", "D2", "A2", "F2", "D2",
    "D2", "C2", "F2", "G2", "D2", "D2", "C2", "G2", "A2", "D2",
)
_FIFTHS = {"D2": "A2", "C2": "G2", "F2": "C3", "G2": "D3", "A2": "E3"}
_TRIADS = {
    "D2": ("D4", "F4", "A4"),
    "C2": ("C4", "E4", "G4"),
    "F2": ("F4", "A4", "C5"),
    "G2": ("G4", "B4", "D5"),
    "A2": ("A3", "C4", "E4"),
}


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

    for bar, root in enumerate(_ROOTS):
        triad = _TRIADS[root]
        fifth = _FIFTHS[root]

        # The engine of the whole theme: eighth-note broken triads, the
        # same trick the cutscene used, running the entire loop.
        arp[bar] = [(index * .5, .45, triad[index % 3], .60)
                    for index in range(8)]
        # ...with the shape inverted in the second third, so eighty
        # seconds of the same rising figure does not become a drill.
        if 10 <= bar < 20:
            arp[bar] = [(index * .5, .45, triad[(2 - index) % 3], .58)
                        for index in range(8)]

        bass[bar] = [(0, .9, root, .88), (2, .9, fifth, .74)]
        # Every fourth bar the bass picks up a passing eighth, which is
        # most of what stops it sounding mechanical.
        if bar % 4 == 3:
            bass[bar].append((3.5, .4, fifth, .50))

        # A woodblock on two and four and nothing else. The tabla
        # answers it only in the busier third of the loop.
        block[bar] = [(1, .1, "D5", .26), (3, .1, "D5", .22)]
        if 18 <= bar < 28:
            drum[bar] = [(2.5, .12, "A3", .34), (3.75, .1, "D4", .26)]

    # The reed states the phrase and then shuts up for a long time. Four
    # entries in thirty bars: this is a theme for a place, and the place
    # is mostly empty.
    reed[2] = [(1.0, 1.5, "A4", .74), (3.0, 1.0, "G4", .66)]
    reed[3] = [(0.5, 2.0, "F4", .70)]
    reed[12] = [(1.0, 1.0, "C5", .72), (2.0, 2.0, "A4", .68)]
    reed[13] = [(1.0, 2.5, "G4", .64)]
    reed[22] = [(0.5, 1.5, "F4", .66), (2.5, 1.5, "G4", .70)]
    reed[26] = [(1.0, 1.0, "A4", .68), (2.0, 1.0, "G4", .62),
                (3.0, 1.0, "F4", .58)]

    # Twice in the loop the pulse lead comes in and plays the tune
    # properly -- once in the middle, once on the way home -- so that a
    # player who has been out here a while gets something back.
    lead[7] = [(0, 1, "A4", .70), (1, 1, "G4", .64), (2, 2, "F4", .68)]
    lead[8] = [(0, 1, "G4", .66), (1, 1, "A4", .70), (2, 2, "D5", .74)]
    lead[9] = [(0, 2, "A4", .64), (2, 2, "G4", .58)]
    lead[17] = [(0, 1, "D5", .68), (1, 1, "C5", .62), (2, 2, "A4", .66)]
    lead[18] = [(0, 2, "G4", .62), (2, 2, "F4", .58)]
    lead[19] = [(0, 3, "D4", .56)]

    # One hollow answer from somewhere off the map, in the gaps the reed
    # leaves. Never underneath it -- two voices in an empty place should
    # be calling to each other, not harmonising.
    pipe[5] = [(1.0, 2.0, "D4", .40)]
    pipe[15] = [(2.0, 2.0, "A3", .38)]
    pipe[24] = [(1.0, 2.5, "F4", .36)]
    pipe[29] = [(0.5, 3.0, "D4", .34)]

    return [
        Track("arp", ins.pulse_arp, .80, _bars(arp)),
        Track("bass", ins.round_bass, 1.00, _bars(bass)),
        Track("reed", ins.breathy_reed, .78, _bars(reed)),
        Track("lead", ins.pluck_lead, .66, _bars(lead)),
        Track("pipe", ins.hollow_pipe, .54, _bars(pipe)),
        Track("block", ins.woodblock, .34, _bars(block)),
        Track("drum", ins.tabla_dayan, .42, _bars(drum)),
    ]
