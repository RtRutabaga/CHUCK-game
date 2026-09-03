"""Desert arrival cue -- eighteen seconds, written like an NES opening.

This is not an area theme and does not loop. It starts under the
whiteout, so the desert fades up onto music already playing, and it
ends exactly as the scene fades out: at 120 BPM the nine bars run 18.0
seconds, against the cutscene's 3.6-second music start and 21.6-second
end.

The arrangement is a deliberate four-channel imitation: a narrow-duty
pulse carries the tune, a rounder pulse answers it a third below, a
third pulse runs broken triads underneath at eighth notes -- the
arpeggio being the trick that made two square waves sound like a whole
chord -- and a soft bass walks root and fifth under all of it, with the
noise channel keeping time on an offbeat hat and a snare on two.

D Dorian, not Phrygian dominant. The augmented second in that mode is
what makes a desert sound haunted, and this is the wrong kind of
desert: Chuck has just arrived somewhere, at the start of a thing
rather than the end of one, and the music should be pleased about it.

The shape still follows the scene. The tune enters as he walks out of
the portal, turns over as the portal folds up, and thins to a quiet
restatement while he stands there lighting a cigarette, ending on a
held tonic under the white fade.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 120
BEATS_PER_BAR = 4
TOTAL_BARS = 9
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.70

# The scene's clock, in beats of this cue. Music starts 3.6 seconds in
# and a beat is half a second, so beat = (scene_time - 3.6) * 2.
DESERT_IN_BEAT = 2.8        # scene 5.0  -- the desert has arrived
WALK_BEAT = 4.4             # scene 5.8  -- he steps out of the mouth
COLLAPSE_BEAT = 11.2        # scene 9.2  -- the portal folds up
CIGARETTE_BEAT = 22.8       # scene 15.0 -- it catches

# The tune's harmony, one chord to the bar. G major rather than G minor:
# Dorian's natural sixth is the whole reason this sounds like an open
# road instead of a haunted one.
_ROOTS = ("D2", "D2", "C2", "F2", "G2", "D2", "F2", "G2", "D2")
_FIFTHS = {"D2": "A2", "C2": "G2", "F2": "C3", "G2": "D3"}
_TRIADS = {
    "D2": ("D4", "F4", "A4"),
    "C2": ("C4", "E4", "G4"),
    "F2": ("F4", "A4", "C5"),
    "G2": ("G4", "B4", "D5"),
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
    lead: dict[int, list[tuple]] = {}
    harmony: dict[int, list[tuple]] = {}
    arp: dict[int, list[tuple]] = {}
    bass: dict[int, list[tuple]] = {}
    hat: dict[int, list[tuple]] = {}
    snare: dict[int, list[tuple]] = {}

    # Bar zero is under the whiteout: bass and arpeggio only, so the
    # desert fades up onto something already running rather than onto
    # the downbeat of a tune.
    #
    # The tune itself climbs to the fifth and comes back down twice --
    # deliberately plain, because it has eighteen seconds and one job.
    lead[1] = [(0, 1, "A4", .92), (1, 1, "G4", .84), (2, 2, "F4", .88)]
    lead[2] = [(0, 1, "G4", .86), (1, 1, "A4", .90), (2, 2, "D5", .96)]
    lead[3] = [(0, 1, "C5", .90), (1, 1, "D5", .94),
               (2, 1, "C5", .86), (3, 1, "A4", .82)]
    lead[4] = [(0, 2, "G4", .88), (2, 2, "F4", .84)]
    lead[5] = [(0, 1, "G4", .84), (1, 1, "A4", .88), (2, 2, "G4", .80)]
    # He has stopped walking; so does the tune, into a quieter version
    # of its own opening.
    lead[6] = [(0, 2, "F4", .62), (2, 2, "E4", .58)]
    lead[7] = [(0, 1, "D4", .60), (1, 1, "F4", .58), (2, 2, "A4", .64)]
    # Softer than the phrase before it: the fade to white should
    # feel like the tune letting go, not like a button.
    lead[8] = [(0, 4, "D4", .42)]

    # The second pulse, a third or a sixth under the tune, and only on
    # its long notes: two channels playing every note together is what
    # makes a chiptune sound like an organ instead of a band.
    harmony[1] = [(2, 2, "D4", .50)]
    harmony[2] = [(2, 2, "A4", .54)]
    harmony[3] = [(0, 2, "A4", .48)]
    harmony[4] = [(0, 2, "D4", .46), (2, 2, "C4", .44)]
    harmony[5] = [(2, 2, "D4", .44)]
    harmony[7] = [(2, 2, "D4", .34)]
    harmony[8] = [(0, 4, "A3", .24)]

    for bar, root in enumerate(_ROOTS):
        fifth = _FIFTHS[root]
        # Root and fifth on the quarters: the NES bass part, which is
        # almost always exactly this and almost always enough.
        if bar < 8:
            bass[bar] = [(beat, .5, root if beat % 2 == 0 else fifth,
                          .90 if bar < 6 else .70)
                         for beat in (0, 1, 2, 3)]
        else:
            bass[bar] = [(0, 2.0, root, .52), (2, 2.0, fifth, .42)]

        # The arpeggio: eighth-note broken triads, running from the
        # first bar to the last of the walking section and then out.
        if bar <= 5:
            triad = _TRIADS[root]
            level = .70 if bar else .52
            arp[bar] = [(index * .5, .45, triad[index % 3], level)
                        for index in range(8)]
        elif bar < 8:
            triad = _TRIADS[root]
            arp[bar] = [(index * 1.0, .9, triad[index % 3], .34)
                        for index in range(4)]

        # Noise channel: offbeat hat through the walk, a snare on two.
        if 1 <= bar <= 5:
            hat[bar] = [(beat + .5, .12, "D6", .30) for beat in range(4)]
            snare[bar] = [(2, .16, "D3", .52)]
        elif bar == 6:
            hat[bar] = [(beat + .5, .12, "D6", .18) for beat in (0, 2)]

    return [
        Track("lead", ins.pluck_lead, .92, _bars(lead)),
        Track("harmony", ins.neon_synth_lead, .60, _bars(harmony)),
        Track("arp", ins.pulse_arp, .74, _bars(arp)),
        Track("bass", ins.round_bass, 1.00, _bars(bass)),
        Track("hat", ins.hat, .30, _bars(hat)),
        Track("snare", ins.snare, .40, _bars(snare)),
    ]
