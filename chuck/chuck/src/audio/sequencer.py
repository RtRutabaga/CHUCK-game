"""Sequencer: turns note-event data into rendered audio.

Responsibilities (Soundtrack Bible: reusable, never duplicated):
    * note_to_freq: pitch names ("F#4", "Bb2") to Hz.
    * render_song: place every note of every track into one buffer at
      its beat position, WRAPPING tails past the end back to the start
      so the loop point is mathematically seamless.

Pure standard library; unit-testable anywhere.
"""

from __future__ import annotations

from typing import Callable, NamedTuple

from src.audio.synth import SAMPLE_RATE, gain, normalize

_NOTE_INDEX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note_to_freq(name: str) -> float:
    """'A4' -> 440.0; supports '#' and 'b' (e.g. 'F#3', 'Bb2')."""
    letter, rest = name[0].upper(), name[1:]
    if letter not in _NOTE_INDEX:
        raise ValueError(f"Bad note name {name!r}")
    semitone = _NOTE_INDEX[letter]
    while rest and rest[0] in "#b":
        semitone += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    octave = int(rest)
    midi = (octave + 1) * 12 + semitone
    return 440.0 * 2 ** ((midi - 69) / 12)


class Note(NamedTuple):
    beat: float      # position in beats from song start
    dur: float       # length in beats
    pitch: str       # note name; percussion may ignore it
    vel: float = 1.0


class Track(NamedTuple):
    name: str
    instrument: Callable[[float, float, float], list[float]]  # (hz, sec, vel)
    level: float
    notes: list[Note]


def render_song(
    tempo_bpm: float, total_beats: float, tracks: list[Track],
    headroom: float = 0.75,
) -> list[float]:
    """Render all tracks into one seamless-looping master buffer."""
    spb = 60.0 / tempo_bpm  # seconds per beat
    length = int(total_beats * spb * SAMPLE_RATE)
    master = [0.0] * length
    for track in tracks:
        for note in track.notes:
            if note.beat >= total_beats:
                raise ValueError(
                    f"{track.name}: note at beat {note.beat} is past the "
                    f"song end ({total_beats} beats)"
                )
            samples = track.instrument(
                note_to_freq(note.pitch), note.dur * spb, note.vel
            )
            start = int(note.beat * spb * SAMPLE_RATE)
            for i, s in enumerate(samples):
                master[(start + i) % length] += s * track.level  # wrap tails
    return normalize(master, headroom)
