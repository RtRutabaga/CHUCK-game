"""The final encounter -- the desert theme and the fall, at once.

The room Chuck walks into at the end of the traversal needed music that
belongs to two places. It is still the Collided Desert, and he has been
listening to that theme for eight maps; but it is also the climax of
the whole game, and the piece this game has used for that since the
very first crossing is the fall to Chult -- the driving D-minor thing
with the wrong note in it, which by now is as close to a main theme as
CHUCK has.

The mashup works because the two are already in the same key. The
desert is D Dorian; the fall is D minor. Same tonic, same tonic chord,
one note apart -- the desert's B natural against the fall's B flat. So
nothing had to be transposed, and the join is not a modulation but a
single flattened note. That flattening *is* the arrangement: the first
eight bars are the desert as the player knows it, and then the sixth
drops and the fall theme has arrived without anything else changing.

It reads as the fall because it brings the fall's own things: its
eighth-note pulse, its full kit, its bells, and its Eb -- the wrong
note that has meant "this is going badly" since the sewer. It stays
the desert's because the arpeggio underneath is the desert's arpeggio,
unchanged, and because the reed still answers in the gaps.

Cinematic, in the one way this synth can be: the fall's hook, which
has only ever been heard scurrying past in eighths, played on brass in
half time with timpani under it. Same notes, four times the length.
That is the entire trick of every heroic restatement ever written and
it works here for the same reason it works anywhere -- the player has
heard the tune a hundred times and never once heard it stand still.

A 74-second loop at 104 BPM: between the desert's 96 and the fall's
120, which is what lets both sets of material sit at their own weight
without either sounding rushed or dragged.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 104
BEATS_PER_BAR = 4
TOTAL_BARS = 32
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.72

# Where the fall arrives. Before it, the desert's own mode; from here
# on, the flattened sixth and everything that comes with it.
FALL_IN = 8
# ...and where the wrong note starts, which is the fall's other tell.
WRONG_NOTE_IN = 16

_ROOTS = (
    # The desert, as the player has had it for eight maps.
    "D2", "D2", "C2", "G2", "D2", "F2", "G2", "D2",
    # The sixth drops: the fall theme is here.
    "D2", "Bb1", "C2", "A1", "D2", "Bb1", "F2", "A1",
    # ...and the wrong note with it.
    "D2", "Eb2", "C2", "A1", "D2", "Eb2", "Bb1", "A1",
    # Both at once, and home.
    "D2", "Bb1", "C2", "D2", "G2", "Bb1", "A1", "D2",
)
_FIFTHS = {
    "D2": "A2", "C2": "G2", "F2": "C3", "G2": "D3", "A1": "E2",
    "Bb1": "F2", "Eb2": "Bb2",
}
# The tonic chord is the one both pieces already share, which is why
# there was never a key to argue about.
_TRIADS = {
    "D2": ("D4", "F4", "A4"),
    "C2": ("C4", "E4", "G4"),
    "F2": ("F4", "A4", "C5"),
    "A1": ("A3", "C4", "E4"),
    "Bb1": ("Bb3", "D4", "F4"),
    "Eb2": ("Eb4", "G4", "Bb4"),
}
# G is the note the two modes disagree about: major in the desert's
# Dorian, minor once the fall has landed. It is the only chord in the
# piece that changes quality, and it is doing all the work.
_G_DORIAN = ("G4", "B4", "D5")
_G_MINOR = ("G4", "Bb4", "D5")

# The fall's hook, as it is played there: five notes in a bar and a
# half, gone before you have it. Here it is the same five notes over
# four bars.
_HOOK = ("D5", "F5", "G5", "A5", "F5")


def _triad(bar: int, root: str) -> tuple[str, str, str]:
    if root == "G2":
        return _G_DORIAN if bar < FALL_IN else _G_MINOR
    return _TRIADS[root]


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
    pulse: dict[int, list[tuple]] = {}
    bass: dict[int, list[tuple]] = {}
    brass: dict[int, list[tuple]] = {}
    reed: dict[int, list[tuple]] = {}
    bells: dict[int, list[tuple]] = {}
    timp: dict[int, list[tuple]] = {}
    kicks: dict[int, list[tuple]] = {}
    snares: dict[int, list[tuple]] = {}
    hats: dict[int, list[tuple]] = {}

    for bar, root in enumerate(_ROOTS):
        triad = _triad(bar, root)
        fifth = _FIFTHS[root]

        # The desert's engine, unchanged and running the whole way
        # through. It is the thing that keeps this the same region's
        # music while everything on top of it becomes the fall.
        arp[bar] = [(index * .5, .45, triad[index % 3], .52)
                    for index in range(8)]

        # The fall's own pulse, on top of it, from the bar the fall
        # arrives. Eighths in the shapes it uses there, with the Eb
        # pressing in once the wrong note is allowed.
        if bar >= FALL_IN:
            shape = (triad[0], triad[1], triad[2], _FIFTHS[root])
            if bar >= WRONG_NOTE_IN and bar % 2 == 0:
                shape = (triad[0], "Eb4", triad[2], "A4")
            pulse[bar] = [
                (step * .5, .40, shape[step % 4], .70 if step % 2 else .88)
                for step in range(8)
            ]

        bass[bar] = [(0, .75, root, .96), (1, .5, fifth, .80),
                     (2, .75, root, .90), (3, .5, fifth, .78)]
        if bar >= FALL_IN:
            # The fall's bass does not walk, it drives: the extra
            # pickup on the and-of-four is its signature.
            bass[bar].append((3.5, .5, root, .74))

        # The kit arrives with the fall and never leaves. Before that
        # there is nothing under the desert but its own arpeggio, which
        # is what makes the entry land.
        if bar >= FALL_IN - 2:
            kicks[bar] = [(0, .12, "C2", 1.0), (1.5, .12, "C2", .70),
                          (2, .12, "C2", .92), (3.25, .12, "C2", .72)]
            snares[bar] = [(1, .12, "C3", .88), (3, .12, "C3", .98)]
            hats[bar] = [
                (step * .5, .08, "C5", .78 if step % 2 == 0 else .52)
                for step in range(8)
            ]
        if bar >= WRONG_NOTE_IN:
            hats.setdefault(bar, []).extend(
                (step + .25, .06, "C5", .42) for step in range(4))

        # Timpani on the downbeat of every other bar once it is big,
        # which is most of what "cinematic" costs on this synth.
        if bar >= FALL_IN and bar % 2 == 0:
            timp[bar] = [(0, .9, root, .58)]
        if bar >= 24:
            timp.setdefault(bar, []).append((2.5, .6, fifth, .40))

    # The hook, in half time, on brass. Four bars for five notes that
    # normally go past in a bar and a half.
    for entry in (8, 24):
        brass[entry] = [(0, 2.0, _HOOK[0], .82), (2, 1.0, _HOOK[1], .76),
                        (3, 1.0, _HOOK[2], .78)]
        brass[entry + 1] = [(0, 2.0, _HOOK[3], .86), (2, 2.0, _HOOK[4], .78)]
        brass[entry + 2] = [(0, 1.5, "D5", .80), (2, 2.0, "A4", .72)]
        brass[entry + 3] = [(0, 3.0, "F4", .70)]
    # ...and once in the middle with the wrong note in it, which is the
    # version that says the heroes are not winning yet.
    brass[16] = [(0, 2.0, "D5", .80), (2, 1.0, "Eb5", .84),
                 (3, 1.0, "D5", .76)]
    brass[17] = [(0, 2.0, "A4", .78), (2, 2.0, "F4", .70)]
    brass[20] = [(0, 1.5, "Bb4", .74), (2, 2.0, "A4", .78)]
    brass[21] = [(0, 3.0, "D5", .72)]

    # The desert's reed, still answering in the gaps. It is the one
    # voice that does not change when the fall arrives, and it is here
    # so the room does not stop being the desert.
    reed[4] = [(1.0, 1.5, "A4", .70), (3.0, 1.0, "G4", .62)]
    reed[5] = [(0.5, 2.0, "F4", .66)]
    reed[12] = [(1.0, 1.0, "Bb4", .66), (2.0, 2.0, "A4", .62)]
    reed[18] = [(1.0, .5, "Eb5", .68), (1.5, .5, "D5", .64),
                (2.0, 2.0, "A4", .60)]
    reed[22] = [(0.5, 1.5, "Bb4", .64), (2.5, 1.5, "C5", .60)]
    reed[28] = [(1.0, 1.0, "A4", .66), (2.0, 1.0, "G4", .60),
                (3.0, 1.0, "F4", .56)]

    # The fall's bells, on the bars that matter.
    for bar in (8, 12, 16, 20, 24, 28, 31):
        bells[bar] = [(0, 1.5, "D5" if bar % 8 == 0 else "A4", .48)]
    bells[31].append((2, 2.0, "D5", .52))

    return [
        Track("arp", ins.pulse_arp, .70, _bars(arp)),
        Track("pulse", ins.pluck_lead, .62, _bars(pulse)),
        Track("brass", ins.brass, .80, _bars(brass)),
        Track("reed", ins.breathy_reed, .70, _bars(reed)),
        Track("bass", ins.round_bass, 1.00, _bars(bass)),
        Track("bells", ins.bell, .58, _bars(bells)),
        Track("timp", ins.timpani, .70, _bars(timp)),
        Track("kick", ins.kick, .88, _bars(kicks)),
        Track("snare", ins.snare, .80, _bars(snares)),
        Track("hats", ins.hat, .74, _bars(hats)),
    ]
