"""The dragon's theme -- what the final encounter turns into.

The trio's map opens on `desert_trio`, which is the desert theme and
the fall to Chult played at once: two pieces a note apart, joined by
flattening one of them. That is the heroic version, and it is the right
music for three people who are going to win.

Then the wizard finds it, the worlds start arriving, and a red dragon
comes across the arena. This is what plays from there.

It is the same trick a third time and one step further down. The desert
is D Dorian; the mashup dropped the sixth and became D minor; this
drops the *second* and becomes D Phrygian -- D, Eb, F, G, A, Bb, C. So
the Eb, which has meant "this is going badly" since the sewer and
arrived in the mashup as a wrong note pressing in, is now simply the
second degree of the scale. The wrong note has become the key. There is
no better way to say that the situation has stopped being recoverable
and started being the situation.

Everything else is what a boss theme is made of on this synth:

    the desert's arpeggio, still running, at twice the speed
    a square bass hammering eighths instead of walking
    the fall's own hook in quarter notes, where the mashup stated it
        in half time -- same five notes, four times faster
    an Ab that does not belong to the mode at all, under the bars the
        dragon is on, which is the tritone and is the oldest monster
        chord there is
    the full kit from bar one, because this piece does not build to
        anything: what it is is the thing that has already happened

132 BPM, above both of its parents, and 36 bars of it -- 65 seconds,
which is about twice as long as the encounter has left to run when it
starts. It does not need to loop cleanly for the player's sake so much
as for the room's: if the heroes take longer than usual it turns over
rather than stopping.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 132
BEATS_PER_BAR = 4
TOTAL_BARS = 36
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
# The loudest thing in the phase, and meant to be. The walk is at 0.62
# and the mashup at 0.72.
MASTER_HEADROOM = 0.80

# Where the hook lands, and where the dragon's own bars are.
HOOK_AT = (8, 24)
DRAGON_FROM = 16
DRAGON_TO = 24

_ROOTS = (
    # The engine, and the flat second stating itself immediately.
    "D2", "D2", "Eb2", "D2", "D2", "Bb1", "A1", "A1",
    # The hook.
    "D2", "Eb2", "D2", "Bb1", "D2", "Eb2", "A1", "D2",
    # The dragon: the tritone, which is in no key at all.
    "D2", "Ab1", "D2", "Ab1", "Eb2", "Eb2", "A1", "A1",
    # The hook again, harder, and home.
    "D2", "Eb2", "F2", "Eb2", "D2", "Bb1", "A1", "D2",
    "Eb2", "D2", "A1", "D2",
)
# Fifths, except where the mode does not have one. A's is flat, which
# is what makes it the dark chord of a Phrygian key rather than the
# bright one it is in a major.
_FIFTHS = {
    "D2": "A2", "Eb2": "Bb2", "F2": "C3", "G2": "D3",
    "A1": "Eb2", "Bb1": "F2", "C2": "G2", "Ab1": "Eb2",
}
# D Phrygian. The v is diminished and the bII is major, which between
# them are the whole sound of the mode.
_TRIADS = {
    "D2": ("D4", "F4", "A4"),
    "Eb2": ("Eb4", "G4", "Bb4"),
    "F2": ("F4", "A4", "C5"),
    "G2": ("G4", "Bb4", "D5"),
    "A1": ("A3", "C4", "Eb4"),
    "Bb1": ("Bb3", "D4", "F4"),
    "C2": ("C4", "Eb4", "G4"),
    # Not in the mode, and that is the point of it.
    "Ab1": ("Ab3", "C4", "Eb4"),
}

# The fall's hook, note for note, as the mashup states it -- and as the
# fall itself states it. Here it goes past in quarters.
_HOOK = ("D5", "F5", "G5", "A5", "F5")


def _bars(pattern: dict[int, list[tuple]]) -> list[Note]:
    notes = []
    for bar, events in pattern.items():
        for event in events:
            beat, duration, pitch = event[:3]
            velocity = event[3] if len(event) > 3 else 1.0
            notes.append(Note(bar * BEATS_PER_BAR + beat, duration, pitch,
                              velocity))
    return notes


def _on_the_dragon(bar: int) -> bool:
    return DRAGON_FROM <= bar < DRAGON_TO


def build_tracks() -> list[Track]:
    arp: dict[int, list[tuple]] = {}
    bass: dict[int, list[tuple]] = {}
    brass: dict[int, list[tuple]] = {}
    stab: dict[int, list[tuple]] = {}
    reed: dict[int, list[tuple]] = {}
    growl: dict[int, list[tuple]] = {}
    timp: dict[int, list[tuple]] = {}
    kicks: dict[int, list[tuple]] = {}
    snares: dict[int, list[tuple]] = {}
    hats: dict[int, list[tuple]] = {}

    for bar, root in enumerate(_ROOTS):
        triad = _TRIADS[root]
        fifth = _FIFTHS[root]

        # The desert's own arpeggio, unchanged in shape and running at
        # sixteenths instead of eighths. It is the thread back through
        # the mashup to the walk, and doubling it is the cheapest
        # possible way to say the same place is now moving twice as
        # fast.
        arp[bar] = [(index * .25, .22, triad[index % 3], .46)
                    for index in range(16)]

        # Hammered eighths rather than a walk. A bass that goes
        # somewhere is a bass with time to spare.
        bass[bar] = [(index * .5, .42, root if index % 4 else root, .92)
                     for index in range(8)]
        bass[bar][2] = (1.0, .42, fifth, .82)
        bass[bar][6] = (3.0, .42, fifth, .78)

        # The kit, from bar one and at full size. This piece does not
        # build to anything: it *is* the thing that has already
        # happened.
        kicks[bar] = [(0, .12, "C2", 1.0), (0.75, .12, "C2", .74),
                      (1.5, .12, "C2", .92), (2, .12, "C2", .96),
                      (3.25, .12, "C2", .78)]
        snares[bar] = [(1, .12, "C3", .94), (3, .12, "C3", 1.0)]
        hats[bar] = [(index * .25, .06, "C5",
                      .74 if index % 4 == 0 else .40)
                     for index in range(16)]
        if bar % 4 == 3:
            snares[bar].extend([(3.5, .1, "C3", .70), (3.75, .1, "C3", .86)])

        if _on_the_dragon(bar):
            # Under the tritone bars: a low sustained growl and a
            # timpani on every downbeat. Nothing clever -- this is the
            # part of the piece that is a large animal.
            growl[bar] = [(0, 3.6, root, .54)]
            timp[bar] = [(0, .9, root, .70)]
            if bar % 2:
                timp[bar].append((2.5, .6, fifth, .48))
        elif bar % 4 == 0:
            timp[bar] = [(0, .8, root, .52)]

        # Off-beat stabs on the chord, which is most of what makes a
        # theme feel like it is chasing you.
        if not _on_the_dragon(bar):
            stab[bar] = [(1.5, .2, triad[1], .60), (3.5, .2, triad[2], .56)]
        else:
            stab[bar] = [(0.5, .2, triad[0], .66), (1.5, .2, triad[1], .62),
                         (2.5, .2, triad[2], .60), (3.5, .2, triad[1], .58)]

    # The hook, in quarters. The mashup plays these five notes over four
    # bars on brass with timpani under them, which is a restatement of
    # something the player has heard a hundred times and never heard
    # stand still. Here they go past in a bar and a half, which is how
    # the fall itself has always played them -- except that this time
    # they are being played *at* somebody.
    for entry in HOOK_AT:
        brass[entry] = [(0, .9, _HOOK[0], .92), (1, .9, _HOOK[1], .88),
                        (2, .9, _HOOK[2], .90), (3, .9, _HOOK[3], .94)]
        brass[entry + 1] = [(0, 1.8, _HOOK[4], .88), (2, 1.8, "D5", .84)]
        brass[entry + 2] = [(0, .9, "Eb5", .90), (1, .9, "D5", .86),
                            (2, 1.8, "A4", .82)]
        brass[entry + 3] = [(0, 1.4, "F4", .80), (2, 1.8, "D4", .76)]
    # ...and once inside the dragon's own bars, bent onto the tritone:
    # the same shape with the ground taken out from under it.
    brass[20] = [(0, .9, "Eb5", .90), (1, .9, "C5", .86),
                 (2, 1.8, "Ab4", .88)]
    brass[21] = [(0, 1.4, "Eb5", .84), (2, 1.4, "C5", .78)]

    # The desert's reed, still answering, and with almost no room left
    # to do it in. It is the last thing in the piece that belongs to the
    # place rather than to the emergency.
    reed[6] = [(1.0, .5, "Bb4", .62), (1.5, .5, "A4", .60),
               (2.0, 1.2, "F4", .58)]
    reed[14] = [(0.5, .5, "Eb5", .64), (1.0, .5, "D5", .60),
                (1.5, 1.4, "A4", .56)]
    reed[30] = [(1.0, .5, "F5", .62), (1.5, .5, "Eb5", .60),
                (2.0, 1.4, "D5", .58)]
    reed[34] = [(0.5, 1.0, "Eb5", .58), (2.0, 1.6, "D5", .54)]

    return [
        Track("arp", ins.pulse_arp, .58, _bars(arp)),
        Track("bass", ins.synth_bass, 1.00, _bars(bass)),
        Track("growl", ins.low_pulse, .70, _bars(growl)),
        Track("brass", ins.brass, .86, _bars(brass)),
        Track("stab", ins.metal_hit, .40, _bars(stab)),
        Track("reed", ins.breathy_reed, .62, _bars(reed)),
        Track("timp", ins.timpani, .74, _bars(timp)),
        Track("kick", ins.kick, .92, _bars(kicks)),
        Track("snare", ins.snare, .84, _bars(snares)),
        Track("hats", ins.hat, .70, _bars(hats)),
    ]
