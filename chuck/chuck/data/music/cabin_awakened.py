"""Cabin theme, awakened -- the same tune with the roof off.

When the table map turns planar and the aurora projector comes on, the
cabin cue does not change to a different piece. It changes gear. Every
identifying part of `cabin` is imported rather than rewritten: the same
thirty-two-bar root cycle, the same syncopated elastic-bass figure, the
same two neon hooks. Played back it is unmistakably the room Chuck was
just standing in.

What arrives on top of it is the Beholder fight's language, because
that is the reference for "more intense" in this game and the two share
a modal world. D Dorian and D Phrygian differ by one note, so the boss
theme's flat-second grind can be laid over the cabin's harmony without
retuning either: a choral ostinato chanting the semitone, brass stabs
answering the hook, timpani under the downbeats and toms filling the
turnarounds.

It also runs faster -- 132 against 112 -- and gives up the cabin's
headroom for the boss's. Nothing else about the arrangement is new.
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


def build_tracks() -> list[Track]:
    # The hook, unchanged in pitch and rhythm, played harder.
    synth_hook = {}
    for start, phrase, velocity in (
        (4, cabin._HOOK_A, 1.0), (12, cabin._HOOK_A, 1.0),
        (20, cabin._HOOK_B, 1.0), (32, cabin._HOOK_A, 1.0),
        (40, cabin._HOOK_B, 1.0),
    ):
        synth_hook.update(cabin._melody(start, phrase, velocity))

    # The bass figure is the cabin's own, with the mid-track break taken
    # out: the awakened room does not drop back.
    bass = {bar: _bass_bar(root) for bar, root in enumerate(_ROOTS)}

    arp, low_pulse = {}, {}
    chant, horn, kick, snare, hats, timp, toms, sub = {}, {}, {}, {}, {}, {}, {}, {}
    for bar, root in enumerate(_ROOTS):
        chord = _ARP[root]
        held, flat = _CHANT[root]

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

    return [
        Track("synth_hook", ins.neon_synth_lead, 1.0, _bars(synth_hook)),
        Track("chant", ins.choir, .82, _bars(chant)),
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
