"""Desert arrival cue -- eighteen seconds of dry air and one small event.

This is not an area theme and does not loop. It starts under the
whiteout, so the desert fades up onto music already playing, and it
ends exactly as the scene fades out: at 80 BPM the six bars run 18.0
seconds, against the cutscene's 3.6-second music start and 21.6-second
end.

D Phrygian dominant -- D, Eb, F#, G, A, Bb, C. The raised third against
the flat second is the interval that says heat and distance without any
of the instrumentation having to imitate anything in particular.

The shape follows the scene rather than a song form. A throat drone
holds the whole way through, because the horizon does. Over it: a reed
phrase while Chuck walks out of the portal, a struck low bell where the
portal folds up, then almost nothing at all while he stands there and
lights a cigarette, which is the quietest thing that happens in it.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 80
BEATS_PER_BAR = 4
TOTAL_BARS = 6
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
MASTER_HEADROOM = 0.66

# The scene's clock, in beats of this cue. Music starts 3.6 seconds in
# and a beat is 0.75 seconds, so beat = (scene_time - 3.6) / 0.75.
DESERT_IN_BEAT = 1.87       # scene 5.0  -- the desert has arrived
COLLAPSE_BEAT = 7.47        # scene 9.2  -- the portal folds up
CIGARETTE_BEAT = 15.2       # scene 15.0 -- it catches


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
    drone: dict[int, list[tuple]] = {}
    overtone: dict[int, list[tuple]] = {}
    reed: dict[int, list[tuple]] = {}
    pipe: dict[int, list[tuple]] = {}
    bass: dict[int, list[tuple]] = {}
    bells: dict[int, list[tuple]] = {}
    block: dict[int, list[tuple]] = {}

    # The horizon: a held D under everything, swelling once in the
    # middle and thinning out at the end rather than stopping. Struck
    # every two beats and overlapping, because the drone voice decays
    # over about a second whatever duration it is given -- written one
    # note to the bar it left a hole in the middle of every bar, and the
    # hole in bar one landed exactly where Chuck steps out.
    for bar, velocity in enumerate((.46, .60, .68, .64, .54, .42)):
        drone[bar] = [(beat, 2.6, "D2", velocity) for beat in (0, 2)]
    # An overtone above it from the moment the desert is visible, so the
    # arrival has something opening out rather than only something held.
    # Bar zero's second half needs something in it: the drone voice is
    # a struck sound and it has died away by then, and that gap sits
    # right where the whiteout clears.
    overtone[0] = [(2.0, 2.2, "D3", .34)]
    overtone[1] = [(0, 3.2, "A3", .30)]
    overtone[2] = [(0, 3.6, "D4", .38)]
    overtone[3] = [(1.0, 2.4, "A3", .30)]
    overtone[5] = [(0.0, 3.0, "D3", .26)]

    # The reed carries the walk out of the portal: a phrase that climbs
    # to the raised third and sits there, which is where the mode's heat
    # actually lives.
    reed[1] = [(0.5, 1.0, "D4", .62), (2.0, 0.75, "Eb4", .54),
               (3.0, 1.0, "F#4", .66)]
    reed[2] = [(0.5, 1.5, "G4", .60), (2.5, 1.25, "F#4", .52)]
    # ...then stops, because he has stopped.
    reed[4] = [(1.0, 2.0, "D4", .40)]
    reed[5] = [(0.5, 2.6, "A3", .42)]

    # A hollow answer from a long way off, never in the same bar as the
    # reed: two things calling across an empty place, not a duet.
    pipe[3] = [(0.0, 1.5, "Bb3", .40), (2.0, 1.75, "A3", .36)]
    pipe[5] = [(0.5, 2.0, "D4", .26)]

    # Sparse low movement. Four notes in the whole cue.
    bass[0] = [(0.0, 2.0, "D1", .70)]
    bass[2] = [(0.0, 2.0, "Bb1", .58)]
    bass[3] = [(2.0, 2.0, "C2", .52)]
    bass[4] = [(0.0, 3.0, "D1", .60)]

    # One struck bell on the collapse, and one high one where the
    # lighter catches. Two events, two sounds; nothing else is marked.
    bells[1] = [(3.47, 2.0, "D5", .58)]
    bells[3] = [(3.2, 2.4, "A5", .30)]

    # A dry tap under the walk only, like something ticking in the heat.
    block[1] = [(0.0, .08, "D5", .22), (2.0, .08, "D5", .18)]
    block[2] = [(0.0, .08, "D5", .20), (2.5, .08, "D5", .15)]

    return [
        Track("drone", ins.throat_drone, .78, _bars(drone)),
        Track("overtone", ins.throat_overtone, .50, _bars(overtone)),
        Track("reed", ins.breathy_reed, .86, _bars(reed)),
        Track("pipe", ins.hollow_pipe, .62, _bars(pipe)),
        Track("bass", ins.round_bass, .92, _bars(bass)),
        Track("bells", ins.bell, .56, _bars(bells)),
        Track("block", ins.woodblock, .34, _bars(block)),
    ]
