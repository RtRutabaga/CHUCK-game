"""Jungle-temple theme -- ancient, shamanic, and quietly watchful.

An original 80-second D-minor loop. Low drones and an uneven hand-drum pulse
make the room feel old and physical; sparse flute and bell phrases leave room
for exploration rather than turning the entrance into a combat cue.
"""

from src.audio import instruments as ins
from src.audio.sequencer import Note, Track

TEMPO_BPM = 96
BEATS_PER_BAR = 4
TOTAL_BARS = 32
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR


def _notes(events) -> list[Note]:
    return [Note(bar * 4 + beat, duration, pitch, velocity)
            for bar, beat, duration, pitch, velocity in events]


def build_tracks() -> list[Track]:
    drone = []
    pulse = []
    toms = []
    wood = []
    hats = []
    for bar in range(TOTAL_BARS):
        root = ("D2", "D2", "Eb2", "C2")[bar % 4]
        drone.append((bar, 0, 4, root, 0.72))
        pulse.extend([
            (bar, 0, .7, root, .72),
            (bar, 2.5, .45, "A2" if root == "D2" else root, .55),
        ])
        toms.extend([
            (bar, 0, .14, "D3", .82),
            (bar, 1.5, .14, "A2", .62),
            (bar, 2.25, .14, "F3", .72),
            (bar, 3.5, .14, "C3", .58),
        ])
        wood.extend([
            (bar, .75, .06, "D5", .46),
            (bar, 2.75, .06, "A4", .42),
        ])
        if bar >= 8:
            hats.extend((bar, beat, .05, "C5", .28)
                        for beat in (1.25, 3.25))

    flute = [
        (4, 0, 2.5, "D4", .62), (5, 0, 1.5, "F4", .58),
        (5, 2, 2, "Eb4", .55), (6, 2, 2, "C4", .52),
        (12, 0, 1.5, "A4", .58), (12, 2, 1.5, "G4", .54),
        (13, 0, 3, "F4", .58), (14, 2, 2, "D4", .62),
        (20, 0, 2, "Eb4", .56), (20, 2.5, 1.5, "D4", .6),
        (21, 1, 3, "A3", .5), (22, 2, 2, "C4", .54),
        (28, 0, 1.5, "F4", .58), (28, 2, 1.5, "G4", .52),
        (29, 0, 2, "Eb4", .56), (30, 0, 3.75, "D4", .64),
    ]
    bells = [
        (2, 3, 1, "A5", .38), (7, 1, 2, "Eb5", .35),
        (10, 3.5, .5, "D5", .38), (15, 0, 2, "A4", .36),
        (18, 2, 2, "C5", .34), (23, 3, 1, "Eb5", .37),
        (26, 1, 2, "A5", .34), (31, 3, 1, "D5", .38),
    ]

    return [
        Track("drone", ins.round_bass, .62, _notes(drone)),
        Track("pulse", ins.round_bass, .72, _notes(pulse)),
        Track("flute", ins.flute, .66, _notes(flute)),
        Track("bells", ins.bell, .52, _notes(bells)),
        Track("ritual_toms", ins.jungle_tom, .92, _notes(toms)),
        Track("wood", ins.woodblock, .72, _notes(wood)),
        Track("dust", ins.hat, .45, _notes(hats)),
    ]
