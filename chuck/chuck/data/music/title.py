"""Title screen theme -- the Astral Sea, very quietly.

An original ~128-second loop at 60 BPM in D Lydian. It sits under a rat
leaning on his own name having a smoke, so it does almost nothing: slow
pad chords that take seconds to bloom and seconds to fade, a low drone
so the room has a floor, and every so often a single high bell, placed
the way stars are placed -- irregularly, and never two at once. A few
reverse swells breathe in underneath. No percussion, no melody anybody
could hum, nothing that asks to be listened to.

The raised fourth (G#) is the one strange colour, the same trick the
tower theme uses for height: here it is for distance.

Structure (32 bars of 4/4, two-bar chords throughout):
    0-15    Drift     Dmaj9, Bm11, Gmaj7#11, Asus2 -- twice
    16-23   Further   the same four chords voiced higher and thinner
    24-31   Drift     home again, and into the loop
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


TEMPO_BPM = 60
BEATS_PER_BAR = 4
TOTAL_BARS = 32
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
# Almost all sustained pad energy: a low ceiling keeps it from ever
# arriving as a wall of sound, and the stream trim keeps it under the menu.
MASTER_HEADROOM = 0.48

_CHORDS = (
    ("D3", "A3", "E4", "F#4"),      # Dmaj9
    ("B2", "F#3", "A3", "E4"),      # Bm11
    ("G2", "D3", "F#3", "C#4"),     # Gmaj7 with the raised fourth below
    ("A2", "E3", "B3", "E4"),       # Asus2
)
_HIGH_CHORDS = (
    ("A3", "E4", "F#4", "G#4"),
    ("F#3", "A3", "D4", "E4"),
    ("D3", "F#3", "C#4", "G#4"),
    ("E3", "B3", "D4", "E4"),
)
_DRONES = ("D1", "B0", "G1", "A1")

# Where the stars are: (bar, beat, pitch, velocity). Irregular on
# purpose -- a bell every other bar on the downbeat is a clock.
_STARS = (
    (1, 2.5, "F#6", .42), (3, 0.5, "A6", .34), (4, 3.0, "E6", .38),
    (7, 1.5, "C#7", .30), (9, 2.0, "B6", .36), (10, 3.5, "F#6", .32),
    (13, 0.0, "G#6", .34), (14, 2.5, "E6", .40), (17, 1.0, "A6", .30),
    (18, 3.0, "D7", .26), (20, 1.5, "G#6", .32), (22, 0.5, "F#6", .30),
    (25, 2.0, "E6", .38), (26, 3.5, "A6", .32), (28, 1.0, "B6", .36),
    (30, 2.5, "F#6", .34),
)
_SWELLS = ((5, 0, "D5"), (11, 2, "A4"), (19, 0, "E5"), (27, 2, "F#5"))


def build_tracks() -> list[Track]:
    pad: list[Note] = []
    shimmer: list[Note] = []
    drone: list[Note] = []
    for bar in range(0, TOTAL_BARS, 2):
        index = (bar // 2) % len(_CHORDS)
        higher = 16 <= bar < 24
        chord = _HIGH_CHORDS[index] if higher else _CHORDS[index]
        start = bar * BEATS_PER_BAR
        # Eight beats of chord, held a little long so each one is still
        # fading as the next one blooms: there is never a gap.
        for voice, pitch in enumerate(chord):
            pad.append(Note(start + voice * 0.35, 9.0, pitch,
                            .52 if voice == 0 else .40))
        if not higher:
            drone.append(Note(start, 8.5, _DRONES[index], .55))
        # A faint octave above the top voice on every other chord, for
        # air rather than for harmony.
        if (bar // 2) % 2 == 1:
            shimmer.append(Note(start + 2.0, 6.0,
                                chord[-1][:-1] + str(int(chord[-1][-1]) + 1),
                                .22))

    stars = [Note(bar * BEATS_PER_BAR + beat, 3.0, pitch, vel)
             for bar, beat, pitch, vel in _STARS]
    swells = [Note(bar * BEATS_PER_BAR + beat, 4.0, pitch, .30)
              for bar, beat, pitch in _SWELLS]

    return [
        Track("pad", ins.cloud_pad, 0.62, pad),
        Track("shimmer", ins.cloud_pad, 0.30, shimmer),
        Track("drone", ins.cloud_pad, 0.50, drone),
        Track("stars", ins.bell, 0.34, stars),
        Track("swells", ins.reverse_bell, 0.26, swells),
    ]
