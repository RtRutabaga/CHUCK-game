"""Cabin theme, awakened -- the same tune with the roof off.

When the table map turns planar and the aurora projector comes on, the
cabin cue does not change to a different piece. It changes gear. Every
identifying part of `cabin` is imported rather than rewritten: the same
thirty-two-bar root cycle, the same syncopated elastic-bass figure, the
same two neon hooks. Played back it is unmistakably the room Chuck was
just standing in.

What is gone is the neon synth lead. The tune is carried instead by a
jaw harp and a pair of Tuvan throat voices: a kargyraa growl holding
the root an octave under where it is sung, and a sygyt overtone
whistling the hook's own contour two octaves below where the synth used
to play it. Same notes, same order, no longer up in the air.

Under that sits the Beholder fight's language, because that is the
reference for "more intense" in this game and the two share a modal
world. D Dorian and D Phrygian differ by one note, so the boss theme's
flat-second grind can be laid over the cabin's harmony without retuning
either: a choral ostinato chanting the semitone, brass answering on the
offbeats, timpani under the downbeats and toms filling the turnarounds.

It also runs faster -- 132 against 112 -- and gives up the cabin's
headroom for the boss's.
"""

from data.music import cabin
from data.music.cabin import _ARP, _FIFTH, _OCTAVE, _ROOTS, _bass_bar
from src.audio import instruments as ins
from src.audio.sequencer import Note, Track


# Faster than the cabin, slower than the Beholder fight: the room has
# woken up, it has not turned into a boss.
TEMPO_BPM = 132
BEATS_PER_BAR = 4
TOTAL_BARS = cabin.TOTAL_BARS
TOTAL_BEATS = TOTAL_BARS * BEATS_PER_BAR
# The cabin cue sits well back at 0.72. This one takes the boss theme's
# ceiling, which is most of why it lands as a lift rather than a remix.
MASTER_HEADROOM = 0.94

# The chant grinds the flat second against the root, exactly as the
# Beholder's does. D Dorian and D Phrygian differ by this one note, so
# it can sit over the cabin's own harmony without either being retuned.
_CHANT = {
    "D2": ("D3", "Eb3"),
    "C2": ("C3", "Db3"),
    "G2": ("G3", "Ab3"),
    "A1": ("A2", "Bb2"),
    "B1": ("B2", "C3"),
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


_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def _midi(pitch: str) -> int:
    step = _SEMITONE[pitch[0]]
    body = pitch[1:]
    if body[0] in "#b":
        step += 1 if body[0] == "#" else -1
        body = body[1:]
    return (int(body) + 1) * 12 + step


def _down(pitch: str, octaves: int) -> str:
    value = _midi(pitch) - 12 * octaves
    return f"{_NAMES[value % 12]}{value // 12 - 1}"


def build_tracks() -> list[Track]:
    # The hook, note for note, dropped two octaves and sung rather than
    # played. The neon lead it used to be is gone entirely.
    hook = {}
    for start, phrase, velocity in (
        (4, cabin._HOOK_A, .92), (12, cabin._HOOK_A, .96),
        (20, cabin._HOOK_B, .96), (32, cabin._HOOK_A, 1.0),
        (40, cabin._HOOK_B, 1.0),
    ):
        hook.update(cabin._melody(start, phrase, velocity))
    overtone = {
        bar: [(beat, duration, _down(pitch, 2), velocity)
              for beat, duration, pitch, velocity in events]
        for bar, events in hook.items()
    }
    # The jaw harp answers it in the gaps rather than doubling it, an
    # octave lower again, which is about where a jaw harp actually sits.
    jaw_hook = {
        bar: [(beat + duration, min(.30, duration), _down(pitch, 3),
               .80 if index % 2 else .62)
              for index, (beat, duration, pitch, _v) in enumerate(events)
              if beat + duration < BEATS_PER_BAR]
        for bar, events in hook.items()
    }

    # The bass figure is the cabin's own, with the mid-track break taken
    # out: the awakened room does not drop back.
    bass = {bar: _bass_bar(root) for bar, root in enumerate(_ROOTS)}

    arp, low_pulse = {}, {}
    chant, horn, kick, snare, hats, timp, toms, sub = {}, {}, {}, {}, {}, {}, {}, {}
    drone, jaw = {}, {}
    for bar, root in enumerate(_ROOTS):
        chord = _ARP[root]
        held, flat = _CHANT[root]

        # Kargyraa holds the root right through the bar. It is the floor
        # the whistle and the harp are drawn over, so it never rests.
        drone[bar] = [(0, 4.0, _down(root, 1), .86)]
        # ...and the jaw harp keeps the pulse under all of it, twanging
        # the root and its fifth on a syncopated figure of its own.
        jaw[bar] = [
            (0, .30, _OCTAVE[root], .90),
            (.75, .24, root, .62),
            (1.5, .28, _FIFTH[root], .76),
            (2.25, .24, _OCTAVE[root], .66),
            (2.75, .30, root, .84),
            (3.5, .26, _FIFTH[root], .70),
        ]

        arp[bar] = [
            (step * .25 + .125, .11, chord[step % 4], .50)
            for step in range(16)
        ]
        low_pulse[bar] = [
            (.5, .20, chord[0], .40), (1.5, .20, chord[1], .36),
            (2.5, .20, chord[2], .40), (3.5, .20, chord[1], .36),
        ]

        # The ostinato: root, flat second, root, on every beat. It is the
        # boss theme's engine and it is what makes this read as a lift
        # rather than as the cabin cue played louder.
        chant[bar] = [
            (0, .46, held, .84), (1, .46, flat, .78),
            (2, .46, held, .82), (3, .46, flat, .74),
        ]
        # Brass answers the hook on the offbeats rather than doubling it.
        if bar % 4 == 3:
            horn[bar] = [(2.5, .70, _OCTAVE[root], .88),
                         (3.5, .46, _FIFTH[root], .80)]
        elif bar % 8 == 5:
            horn[bar] = [(1.5, .90, _FIFTH[root], .82)]

        # Double-time kit under the same four-on-the-floor pulse.
        kick[bar] = [(beat, .10, "C2", .92 if beat % 1 == 0 else .58)
                     for beat in (0, .75, 1, 2, 2.75, 3)]
        snare[bar] = [(1, .08, "D3", .82), (3, .08, "D3", .88),
                      (3.75, .06, "D3", .46)]
        hats[bar] = [(step * .25, .03, "C6", .26 if step % 2 else .16)
                     for step in range(16)]
        timp[bar] = [(0, .40, root, .86)]
        if bar % 8 == 7:
            toms[bar] = [(2, .14, "A2", .78), (2.5, .14, "G2", .72),
                         (3, .14, "F2", .80), (3.5, .14, "D2", .86)]
        sub[bar] = [(0, 1.9, root, .52), (2, 1.9, root, .48)]

    for bar, events in jaw_hook.items():
        jaw[bar] = sorted(jaw[bar] + events)

    return [
        Track("throat_overtone", ins.throat_overtone, .94, _bars(overtone)),
        Track("throat_drone", ins.throat_drone, .88, _bars(drone)),
        Track("jaw_harp", ins.jaw_harp, .92, _bars(jaw)),
        Track("chant", ins.choir, .58, _bars(chant)),
        Track("horn", ins.brass, .86, _bars(horn)),
        Track("driving_bass", ins.elastic_bass, 1.10, _bars(bass)),
        Track("sub", ins.round_bass, .52, _bars(sub)),
        Track("pulse_arp", ins.pulse_arp, .58, _bars(arp)),
        Track("low_pulse", ins.pulse_arp, .40, _bars(low_pulse)),
        Track("kick", ins.kick, .95, _bars(kick)),
        Track("snare", ins.snare, .70, _bars(snare)),
        Track("hats", ins.hat, .40, _bars(hats)),
        Track("timpani", ins.timpani, .88, _bars(timp)),
        Track("toms", ins.jungle_tom, .82, _bars(toms)),
    ]
